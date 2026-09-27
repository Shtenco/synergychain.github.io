from __future__ import annotations

import csv, json, time
from collections import defaultdict
from pathlib import Path
import requests
from eth_abi import decode
from eth_utils import keccak, to_checksum_address

START_TS = 1760070203
END_TS = 1760227199
ETH_START = 23544921
ETH_END = 23557920

ETH_RPC = "https://ethereum-rpc.publicnode.com"
BASE_RPC = "https://base-rpc.publicnode.com"

ETH_SPOKE = "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5"
BASE_SPOKE = "0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64"
AERO_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"
AERO_FACTORY_DEPLOY = 3_200_559

BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913".lower()
BASE_WETH = "0x4200000000000000000000000000000000000006".lower()
BASE_AERO = "0x940181a94A35A4569E4529A3CDfB74e38FD98631".lower()
SUPPORTED_BASE_INPUTS = {BASE_USDC, BASE_WETH, BASE_AERO}

OUT = Path("v5_public_raw")
S = requests.Session()
S.headers.update({"User-Agent":"SYNERGY-V5-public-event-collector/1.0"})

OLD_DEPOSIT_SIG = "V3FundsDeposited(address,address,uint256,uint256,uint256,uint32,uint32,uint32,uint32,address,address,address,bytes)"
NEW_DEPOSIT_SIG = "FundsDeposited(bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,uint32,bytes32,bytes32,bytes32,bytes)"
POOL_CREATED_SIG = "PoolCreated(address,address,bool,address,uint256)"
SWAP_SIG = "Swap(address,address,uint256,uint256,uint256,uint256)"

TOPIC_OLD_DEPOSIT = "0x" + keccak(text=OLD_DEPOSIT_SIG).hex()
TOPIC_NEW_DEPOSIT = "0x" + keccak(text=NEW_DEPOSIT_SIG).hex()
TOPIC_POOL_CREATED = "0x" + keccak(text=POOL_CREATED_SIG).hex()
TOPIC_SWAP = "0x" + keccak(text=SWAP_SIG).hex()

def rpc(url, method, params, attempts=6):
    last=None
    for i in range(attempts):
        try:
            r=S.post(url,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
            r.raise_for_status()
            j=r.json()
            if "error" in j:
                raise RuntimeError(j["error"])
            return j["result"]
        except Exception as e:
            last=e
            time.sleep(min(2**i, 12))
    raise RuntimeError(f"{method} failed: {last!r}")

def block_ts(url, n):
    b=rpc(url,"eth_getBlockByNumber",[hex(n),False])
    if b is None:
        raise RuntimeError(f"missing block {n}")
    return int(b["timestamp"],16)

def latest_block(url):
    return int(rpc(url,"eth_blockNumber",[]),16)

def first_block_at_or_after(url, target_ts):
    lo,hi=0,latest_block(url)
    while lo<hi:
        mid=(lo+hi)//2
        if block_ts(url,mid) < target_ts:
            lo=mid+1
        else:
            hi=mid
    return lo

def last_block_at_or_before(url, target_ts):
    b=first_block_at_or_after(url,target_ts)
    if block_ts(url,b)>target_ts:
        b-=1
    return b

def get_logs_adaptive(url, address, topics, start, end, initial_chunk=20000):
    out=[]; cur=start; chunk=initial_chunk
    while cur<=end:
        hi=min(end,cur+chunk-1)
        try:
            flt={"fromBlock":hex(cur),"toBlock":hex(hi),"topics":topics}
            if address is not None:
                flt["address"]=address
            rows=rpc(url,"eth_getLogs",[flt],attempts=3)
            out.extend(rows)
            cur=hi+1
            if chunk<100000: chunk=min(100000,chunk*2)
        except Exception:
            if chunk<=250:
                raise
            chunk=max(250,chunk//2)
    return out

def topic_addr(topic):
    return "0x"+topic[-40:].lower()

def bytes32_addr(v: bytes):
    if len(v)==32 and v[:12]==b"\x00"*12:
        return "0x"+v[-20:].hex()
    return "0x"+v.hex()

def decode_deposit(log, chain_id):
    t0=log["topics"][0].lower()
    destination=int(log["topics"][1],16)
    deposit_id=int(log["topics"][2],16)
    tx=log["transactionHash"]
    block=int(log["blockNumber"],16)
    if t0==TOPIC_OLD_DEPOSIT.lower():
        vals=decode(
            ["address","address","uint256","uint256","uint32","uint32","uint32","address","address","bytes"],
            bytes.fromhex(log["data"][2:])
        )
        return {
            "event":"V3FundsDeposited","origin_chain_id":chain_id,"destination_chain_id":destination,
            "deposit_id":deposit_id,"block_number":block,"tx_hash":tx,
            "input_token":vals[0].lower(),"output_token":vals[1].lower(),
            "input_amount":str(vals[2]),"output_amount":str(vals[3]),
            "quote_timestamp":vals[4],"fill_deadline":vals[5],"exclusivity_deadline":vals[6],
            "raw_topic0":log["topics"][0],"raw_data":log["data"]
        }
    if t0==TOPIC_NEW_DEPOSIT.lower():
        vals=decode(
            ["bytes32","bytes32","uint256","uint256","uint32","uint32","uint32","bytes32","bytes32","bytes"],
            bytes.fromhex(log["data"][2:])
        )
        return {
            "event":"FundsDeposited","origin_chain_id":chain_id,"destination_chain_id":destination,
            "deposit_id":deposit_id,"block_number":block,"tx_hash":tx,
            "input_token":bytes32_addr(vals[0]).lower(),"output_token":bytes32_addr(vals[1]).lower(),
            "input_amount":str(vals[2]),"output_amount":str(vals[3]),
            "quote_timestamp":vals[4],"fill_deadline":vals[5],"exclusivity_deadline":vals[6],
            "raw_topic0":log["topics"][0],"raw_data":log["data"]
        }
    raise RuntimeError("unknown deposit topic")

def add_timestamps(url, rows):
    by_block=defaultdict(list)
    for r in rows: by_block[int(r["block_number"])].append(r)
    for n,rs in by_block.items():
        ts=block_ts(url,n)
        for r in rs: r["timestamp"]=ts

def collect_across(url, chain_id, spoke, start, end):
    logs=get_logs_adaptive(url,to_checksum_address(spoke),[[TOPIC_OLD_DEPOSIT,TOPIC_NEW_DEPOSIT]],start,end,5000)
    rows=[decode_deposit(x,chain_id) for x in logs]
    add_timestamps(url,rows)
    return rows

def discover_aero_pools(base_end):
    logs=get_logs_adaptive(BASE_RPC,to_checksum_address(AERO_FACTORY),[TOPIC_POOL_CREATED],AERO_FACTORY_DEPLOY,base_end,50000)
    pools=[]
    for l in logs:
        token0=topic_addr(l["topics"][1]); token1=topic_addr(l["topics"][2])
        stable=bool(int(l["topics"][3],16))
        pool,idx=decode(["address","uint256"],bytes.fromhex(l["data"][2:]))
        pools.append({
            "pool":pool.lower(),"token0":token0,"token1":token1,"stable":stable,
            "factory_index":int(idx),"created_block":int(l["blockNumber"],16),
            "selected_for_pricing": token0 in SUPPORTED_BASE_INPUTS or token1 in SUPPORTED_BASE_INPUTS
        })
    return pools

def collect_swaps(pools, base_start, base_end):
    selected=[p for p in pools if p["selected_for_pricing"] and p["created_block"]<=base_end]
    meta={p["pool"]:p for p in selected}
    rows=[]
    addresses=list(meta)
    for k in range(0,len(addresses),25):
        batch=addresses[k:k+25]
        logs=get_logs_adaptive(BASE_RPC,[to_checksum_address(x) for x in batch],[TOPIC_SWAP],base_start,base_end,5000)
        for l in logs:
            p=meta[l["address"].lower()]
            vals=decode(["uint256","uint256","uint256","uint256"],bytes.fromhex(l["data"][2:]))
            rows.append({
                "protocol":"AerodromeV2","chain_id":8453,"block_number":int(l["blockNumber"],16),
                "tx_hash":l["transactionHash"],"log_index":int(l["logIndex"],16),
                "pool":l["address"].lower(),"token0":p["token0"],"token1":p["token1"],
                "stable":p["stable"],"amount0_in":str(vals[0]),"amount1_in":str(vals[1]),
                "amount0_out":str(vals[2]),"amount1_out":str(vals[3])
            })
    add_timestamps(BASE_RPC,rows)
    rows.sort(key=lambda r:(r["block_number"],r["log_index"]))
    return rows,selected

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    base_start=first_block_at_or_after(BASE_RPC,START_TS)
    base_end=last_block_at_or_before(BASE_RPC,END_TS)

    eth_across=collect_across(ETH_RPC,1,ETH_SPOKE,ETH_START,ETH_END)
    base_across=collect_across(BASE_RPC,8453,BASE_SPOKE,base_start,base_end)
    across=sorted(eth_across+base_across,key=lambda r:(r["timestamp"],r["origin_chain_id"],r["block_number"]))
    # Keep only the Ethereum<->Base corridor for the observed bridge lower bound.
    for r in across:
        r["selected_eth_base_corridor"] = (
            (r["origin_chain_id"]==1 and r["destination_chain_id"]==8453) or
            (r["origin_chain_id"]==8453 and r["destination_chain_id"]==1)
        )

    pools=discover_aero_pools(base_end)
    swaps,selected_pools=collect_swaps(pools,base_start,base_end)

    across_fields=[
        "event","origin_chain_id","destination_chain_id","deposit_id","block_number","timestamp","tx_hash",
        "input_token","output_token","input_amount","output_amount","quote_timestamp","fill_deadline",
        "exclusivity_deadline","selected_eth_base_corridor","raw_topic0","raw_data"
    ]
    swap_fields=[
        "protocol","chain_id","block_number","timestamp","tx_hash","log_index","pool","token0","token1",
        "stable","amount0_in","amount1_in","amount0_out","amount1_out"
    ]
    write_csv(OUT/"across_events.csv",across,across_fields)
    write_csv(OUT/"aerodrome_swaps.csv",swaps,swap_fields)
    write_csv(OUT/"aerodrome_pools.csv",pools,["pool","token0","token1","stable","factory_index","created_block","selected_for_pricing"])

    manifest={
        "classification":"PUBLIC_RAW_ONCHAIN_EVENTS_ONLY_NO_USD_INFERENCE",
        "window":{"timestamp_start":START_TS,"timestamp_end":END_TS,"ethereum_blocks":[ETH_START,ETH_END],"base_blocks":[base_start,base_end]},
        "rpc":{"ethereum":ETH_RPC,"base":BASE_RPC},
        "across":{
            "ethereum_spokepool":ETH_SPOKE,"base_spokepool":BASE_SPOKE,
            "event_signatures":[OLD_DEPOSIT_SIG,NEW_DEPOSIT_SIG],
            "deposit_rows_total":len(across),
            "eth_base_corridor_deposits":sum(bool(x["selected_eth_base_corridor"]) for x in across),
            "ethereum_rows":len(eth_across),"base_rows":len(base_across)
        },
        "aerodrome":{
            "factory":AERO_FACTORY,"factory_deploy_block":AERO_FACTORY_DEPLOY,
            "pool_created_signature":POOL_CREATED_SIG,"swap_signature":SWAP_SIG,
            "all_pools_discovered":len(pools),"selected_pricable_pools":len(selected_pools),"swap_rows":len(swaps),
            "selection":"pool token0 or token1 is Base USDC/WETH/AERO; raw input side kept exactly"
        },
        "provenance":{
            "across_contracts":"official across-protocol/contracts deployed-addresses",
            "aerodrome_factory":"official aerodrome-finance/contracts deployment",
            "no_synthetic_prices":True
        }
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    if len(across)==0: raise RuntimeError("zero Across deposits")
    if len(pools)==0: raise RuntimeError("zero Aerodrome pools")
    if len(swaps)==0: raise RuntimeError("zero Aerodrome swaps")
    print(json.dumps(manifest,indent=2))
    print("V5 RAW ONCHAIN EVIDENCE: PASS")

if __name__=="__main__":
    main()
