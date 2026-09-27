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

ETH_RPCS = [
    "https://eth.llamarpc.com",
    "https://ethereum-rpc.publicnode.com",
]
BASE_RPCS = [
    "https://base.llamarpc.com",
    "https://base-rpc.publicnode.com",
]

ETH_SPOKE = "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5"
BASE_SPOKE = "0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64"
AERO_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"
AERO_FACTORY_DEPLOY = 3_200_559

BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913".lower()
BASE_WETH = "0x4200000000000000000000000000000000000006".lower()
BASE_AERO = "0x940181a94A35A4569E4529A3CDfB74e38FD98631".lower()
SUPPORTED_BASE_INPUTS = {BASE_USDC, BASE_WETH, BASE_AERO}

OUT = Path("v5_public_raw")
V4_PUBLIC_CSV = Path("evidence/v4/ethereum_23544921_23557920_exact_gas_real_prices.csv")
S = requests.Session()
S.headers.update({"User-Agent":"SYNERGY-V5-public-event-collector/1.0"})
BASE_BLOCKSCOUT = "https://base.blockscout.com/api"
ETH_BLOCKSCOUT = "https://eth.blockscout.com/api"

def blockscout(params, attempts=6, endpoint=BASE_BLOCKSCOUT):
    last=None
    for i in range(attempts):
        try:
            r=S.get(endpoint,params=params,timeout=60)
            r.raise_for_status()
            j=r.json()
            # Blockscout uses status=0 both for errors and for an empty log result.
            if str(j.get("status"))=="0" and j.get("message") not in ("No logs found","No transactions found"):
                raise RuntimeError(j)
            return j
        except Exception as e:
            last=e
            time.sleep(min(2**i,10))
    raise RuntimeError(f"Blockscout failed: {params}: {last!r}")

def base_block_by_time(ts, closest):
    j=blockscout({"module":"block","action":"getblocknobytime","timestamp":str(ts),"closest":closest})
    r=j["result"]
    return int(r["blockNumber"] if isinstance(r,dict) else r)

def base_logs(address, from_block, to_block, topic0=None, topic1=None, topic2=None):
    params={"module":"logs","action":"getLogs","fromBlock":str(from_block),"toBlock":str(to_block),"address":address}
    if topic0: params["topic0"]=topic0
    if topic1: params["topic1"]=topic1
    if topic2: params["topic2"]=topic2
    j=blockscout(params)
    return j.get("result",[]) if isinstance(j.get("result"),list) else []

def eth_logs(address, from_block, to_block, topic0=None):
    params={"module":"logs","action":"getLogs","fromBlock":str(from_block),"toBlock":str(to_block),"address":address}
    if topic0: params["topic0"]=topic0
    j=blockscout(params, endpoint=ETH_BLOCKSCOUT)
    return j.get("result",[]) if isinstance(j.get("result"),list) else []

def eth_block_timestamp(block_number):
    r=S.get(f"https://eth.blockscout.com/api/v2/blocks/{block_number}",timeout=45)
    r.raise_for_status()
    j=r.json()
    ts=j.get("timestamp")
    if isinstance(ts,str) and not ts.isdigit():
        from datetime import datetime
        return int(datetime.fromisoformat(ts.replace("Z","+00:00")).timestamp())
    return int(ts)

def topic_address(addr):
    return "0x" + "0"*24 + addr.lower().replace("0x","")

def parse_intish(v):
    if isinstance(v, int):
        return v
    s=str(v)
    return int(s,16) if s.startswith("0x") else int(s)

def decode_blockscout_log(x):
    # Normalize legacy Blockscout/Etherscan-compatible log object to eth_getLogs shape.
    return {
        "address": x.get("address","").lower(),
        "topics": x.get("topics",[]),
        "data": x.get("data","0x"),
        "blockNumber": x.get("blockNumber") or x.get("block_number"),
        "transactionHash": x.get("transactionHash") or x.get("transaction_hash"),
        "logIndex": x.get("logIndex") or x.get("log_index") or "0x0",
        "timeStamp": x.get("timeStamp") or x.get("timestamp") or x.get("time_stamp"),
    }

def load_v4_timestamp_map():
    if not V4_PUBLIC_CSV.is_file():
        raise RuntimeError(f"missing public V4 evidence CSV: {V4_PUBLIC_CSV}")
    out={}
    with V4_PUBLIC_CSV.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[int(r["block_number"])]=int(r["timestamp"])
    if len(out)!=13000:
        raise RuntimeError(f"bad V4 public timestamp map size: {len(out)}")
    return out

def log_timestamp(raw, fallback=None):
    v=raw.get("timeStamp") or raw.get("timestamp") or raw.get("time_stamp")
    if v not in (None,""):
        return parse_intish(v)
    if fallback is not None:
        return fallback()
    raise RuntimeError("Blockscout log has no timestamp and no fallback")


OLD_DEPOSIT_SIG = "V3FundsDeposited(address,address,uint256,uint256,uint256,uint32,uint32,uint32,uint32,address,address,address,bytes)"
NEW_DEPOSIT_SIG = "FundsDeposited(bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,uint32,bytes32,bytes32,bytes32,bytes)"
POOL_CREATED_SIG = "PoolCreated(address,address,bool,address,uint256)"
SWAP_SIG = "Swap(address,address,uint256,uint256,uint256,uint256)"

TOPIC_OLD_DEPOSIT = "0x" + keccak(text=OLD_DEPOSIT_SIG).hex()
TOPIC_NEW_DEPOSIT = "0x" + keccak(text=NEW_DEPOSIT_SIG).hex()
TOPIC_POOL_CREATED = "0x" + keccak(text=POOL_CREATED_SIG).hex()
TOPIC_SWAP = "0x" + keccak(text=SWAP_SIG).hex()

RPC_USED = {}

def rpc(urls, method, params, attempts=4):
    if isinstance(urls, str):
        urls = [urls]
    errors=[]
    preferred = RPC_USED.get(tuple(urls))
    ordered = ([preferred] if preferred else []) + [u for u in urls if u != preferred]
    for url in ordered:
        last=None
        for i in range(attempts):
            try:
                r=S.post(url,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
                r.raise_for_status()
                j=r.json()
                if "error" in j:
                    raise RuntimeError(j["error"])
                RPC_USED[tuple(urls)] = url
                return j["result"]
            except Exception as e:
                last=e
                time.sleep(min(2**i, 8))
        errors.append(f"{url}: {last!r}")
    raise RuntimeError(f"{method} failed on all RPCs: {' | '.join(errors)}")

def block_ts(urls, n):
    b=rpc(urls,"eth_getBlockByNumber",[hex(n),False])
    if b is None:
        raise RuntimeError(f"missing block {n}")
    return int(b["timestamp"],16)

def latest_block(urls):
    return int(rpc(urls,"eth_blockNumber",[]),16)

def first_block_at_or_after(urls, target_ts):
    lo,hi=0,latest_block(urls)
    while lo<hi:
        mid=(lo+hi)//2
        if block_ts(urls,mid) < target_ts:
            lo=mid+1
        else:
            hi=mid
    return lo

def last_block_at_or_before(urls, target_ts):
    b=first_block_at_or_after(urls,target_ts)
    if block_ts(urls,b)>target_ts:
        b-=1
    return b

def get_logs_adaptive(urls, address, topics, start, end, initial_chunk=20000):
    out=[]; cur=start; chunk=initial_chunk
    while cur<=end:
        hi=min(end,cur+chunk-1)
        try:
            flt={"fromBlock":hex(cur),"toBlock":hex(hi),"topics":topics}
            if address is not None:
                flt["address"]=address
            rows=rpc(urls,"eth_getLogs",[flt],attempts=3)
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
    block=parse_intish(log["blockNumber"])
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

def add_timestamps(urls, rows):
    by_block=defaultdict(list)
    for r in rows: by_block[int(r["block_number"])].append(r)
    for n,rs in by_block.items():
        ts=block_ts(urls,n)
        for r in rs: r["timestamp"]=ts

def base_block_timestamp(block_number):
    r=S.get(f"https://base.blockscout.com/api/v2/blocks/{block_number}",timeout=45)
    r.raise_for_status()
    j=r.json()
    ts=j.get("timestamp")
    if isinstance(ts,str) and not ts.isdigit():
        from datetime import datetime
        return int(datetime.fromisoformat(ts.replace("Z","+00:00")).timestamp())
    return int(ts)

def collect_across(urls, chain_id, spoke, start, end):
    logs=get_logs_adaptive(urls,to_checksum_address(spoke),[[TOPIC_OLD_DEPOSIT,TOPIC_NEW_DEPOSIT]],start,end,5000)
    rows=[decode_deposit(x,chain_id) for x in logs]
    add_timestamps(urls,rows)
    return rows

def discover_aero_pools(base_end):
    pools_by_addr={}
    # Discover only pools where token0 or token1 is a proven-price token.
    for token in sorted(SUPPORTED_BASE_INPUTS):
        t=topic_address(token)
        for pos in ("topic1","topic2"):
            params={"module":"logs","action":"getLogs","fromBlock":str(AERO_FACTORY_DEPLOY),"toBlock":str(base_end),
                    "address":AERO_FACTORY,"topic0":TOPIC_POOL_CREATED,pos:t}
            rows=blockscout(params).get("result",[])
            if not isinstance(rows,list):
                continue
            for raw in rows:
                l=decode_blockscout_log(raw)
                token0=topic_addr(l["topics"][1]); token1=topic_addr(l["topics"][2])
                stable=bool(int(l["topics"][3],16))
                pool,idx=decode(["address","uint256"],bytes.fromhex(l["data"][2:]))
                pools_by_addr[pool.lower()]={
                    "pool":pool.lower(),"token0":token0,"token1":token1,"stable":stable,
                    "factory_index":int(idx),"created_block":parse_intish(l["blockNumber"]),
                    "selected_for_pricing":True
                }
    return sorted(pools_by_addr.values(),key=lambda x:x["pool"])


def collect_swaps(pools, base_start, base_end):
    selected=[p for p in pools if p["created_block"]<=base_end]
    meta={p["pool"]:p for p in selected}
    rows=[]
    ts_cache={}
    for p in selected:
        logs=base_logs(p["pool"],base_start,base_end,topic0=TOPIC_SWAP)
        for raw in logs:
            l=decode_blockscout_log(raw)
            vals=decode(["uint256","uint256","uint256","uint256"],bytes.fromhex(l["data"][2:]))
            bn=parse_intish(l["blockNumber"])
            def fallback(n=bn):
                if n not in ts_cache:
                    for attempt in range(6):
                        try:
                            ts_cache[n]=base_block_timestamp(n)
                            break
                        except requests.HTTPError as e:
                            if getattr(e.response,"status_code",None)!=429 or attempt==5:
                                raise
                            time.sleep(2**attempt)
                return ts_cache[n]
            ts=log_timestamp(l,fallback)
            li=parse_intish(l["logIndex"])
            rows.append({
                "protocol":"AerodromeV2","chain_id":8453,"block_number":bn,"timestamp":ts,
                "tx_hash":l["transactionHash"],"log_index":li,
                "pool":l["address"].lower(),"token0":p["token0"],"token1":p["token1"],
                "stable":p["stable"],"amount0_in":str(vals[0]),"amount1_in":str(vals[1]),
                "amount0_out":str(vals[2]),"amount1_out":str(vals[3])
            })
    rows.sort(key=lambda r:(r["block_number"],r["log_index"]))
    return rows,selected


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    base_start=base_block_by_time(START_TS,"after")
    base_end=base_block_by_time(END_TS,"before")

    v4_ts_map=load_v4_timestamp_map()

    eth_logs_raw=[]
    for topic in (TOPIC_OLD_DEPOSIT,TOPIC_NEW_DEPOSIT):
        eth_logs_raw.extend(eth_logs(ETH_SPOKE,ETH_START,ETH_END,topic0=topic))
    eth_across=[]
    for raw in eth_logs_raw:
        norm=decode_blockscout_log(raw)
        row=decode_deposit(norm,1)
        n=int(row["block_number"])
        if n not in v4_ts_map:
            raise RuntimeError(f"Ethereum Across event outside V4 block map: {n}")
        row["timestamp"]=v4_ts_map[n]
        eth_across.append(row)

    base_logs_raw=[]
    for topic in (TOPIC_OLD_DEPOSIT,TOPIC_NEW_DEPOSIT):
        base_logs_raw.extend(base_logs(BASE_SPOKE,base_start,base_end,topic0=topic))
    base_across=[]
    base_ts_cache={}
    for raw in base_logs_raw:
        norm=decode_blockscout_log(raw)
        row=decode_deposit(norm,8453)
        n=int(row["block_number"])
        def fallback(n=n):
            if n not in base_ts_cache:
                # Small fallback only when the log itself omitted timeStamp.
                for attempt in range(6):
                    try:
                        base_ts_cache[n]=base_block_timestamp(n)
                        break
                    except requests.HTTPError as e:
                        if getattr(e.response,"status_code",None)!=429 or attempt==5:
                            raise
                        time.sleep(2**attempt)
            return base_ts_cache[n]
        row["timestamp"]=log_timestamp(norm,fallback)
        base_across.append(row)

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
        "history_indexers":{"ethereum":"https://eth.blockscout.com/api + /api/v2/blocks/{block}","base":"https://base.blockscout.com/api + /api/v2/blocks/{block}"},
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
