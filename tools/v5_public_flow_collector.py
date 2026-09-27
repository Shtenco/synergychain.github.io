from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import requests
from eth_utils import event_abi_to_log_topic
from web3 import Web3
from web3._utils.events import get_event_data

T0 = 1760070203
T1 = 1760227199
OUT = Path("v5_public_flow")
OUT.mkdir(exist_ok=True)

BLOCKSCOUT = "https://base.blockscout.com/api"
BASE_RPC = "https://base-rpc.publicnode.com"
AERO_FACTORY = Web3.to_checksum_address("0x420DD381b31aEf6683db6B902084cB0FFECe40Da")

CORE_TOKENS = {
    Web3.to_checksum_address("0x4200000000000000000000000000000000000006"): {"symbol": "WETH", "decimals": 18},
    Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"): {"symbol": "USDC", "decimals": 6},
    Web3.to_checksum_address("0x940181a94A35A4569E4529A3CDfB74e38FD98631"): {"symbol": "AERO", "decimals": 18},
}

ACROSS = {
    "legacy": {
        "address": Web3.to_checksum_address("0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64"),
        "abi_url": "https://raw.githubusercontent.com/across-protocol/contracts/master/deployments/base/Base_SpokePool.json",
    },
    "current": {
        "address": Web3.to_checksum_address("0x6C99671B249af73B2847D92123d823Cb3875E399"),
        "abi_url": "https://raw.githubusercontent.com/across-protocol/contracts/master/deployments/base/Base_SpokePool.json",
    },
}

S = requests.Session()
S.headers.update({"User-Agent": "SYNERGY-V5-Blockscout-collector/1.0"})
W3 = Web3()


def get_json(url, *, params=None, attempts=6, timeout=60):
    last = None
    for i in range(attempts):
        try:
            r = S.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(min(2**i, 10))
    raise RuntimeError(f"GET failed: {url}: {last!r}")


def rpc(method, params, attempts=6):
    last = None
    for i in range(attempts):
        try:
            r = S.post(BASE_RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=60)
            r.raise_for_status()
            j = r.json()
            if "error" in j:
                raise RuntimeError(j["error"])
            return j["result"]
        except Exception as e:
            last = e
            time.sleep(min(2**i, 10))
    raise RuntimeError(f"{method} failed: {last!r}")


def rpc_batch(calls, attempts=5):
    payload = [{"jsonrpc":"2.0","id":i,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    last = None
    for k in range(attempts):
        try:
            r = S.post(BASE_RPC, json=payload, timeout=90)
            r.raise_for_status()
            js = r.json()
            by = {x["id"]: x for x in js}
            out = []
            for i in range(len(calls)):
                x = by[i]
                if "error" in x:
                    raise RuntimeError(x["error"])
                out.append(x["result"])
            return out
        except Exception as e:
            last = e
            time.sleep(min(2**k, 10))
    raise RuntimeError(f"batch failed: {last!r}")


def block_by_time(ts, closest):
    j = get_json(BLOCKSCOUT, params={"module":"block","action":"getblocknobytime","timestamp":str(ts),"closest":closest})
    if str(j.get("status")) != "1":
        raise RuntimeError(f"Blockscout getblocknobytime failed: {j}")
    result = j["result"]
    if isinstance(result, dict):
        result = result["blockNumber"]
    return int(result)


def blockscout_logs(address, start, end, topic0=None):
    rows = []
    seen = set()
    # Blockscout's legacy logs endpoint may ignore page/offset on some versions.
    # Query in small block chunks so every response remains bounded.
    for a in range(start, end + 1, 1500):
        b = min(end, a + 1499)
        params = {
            "module":"logs",
            "action":"getLogs",
            "fromBlock":str(a),
            "toBlock":str(b),
            "address":address,
        }
        if topic0:
            params["topic0"] = topic0
        j = get_json(BLOCKSCOUT, params=params, timeout=90)
        status = str(j.get("status"))
        if status == "0":
            msg = str(j.get("message","")) + " " + str(j.get("result",""))
            if "No logs" in msg or "No records" in msg:
                continue
            raise RuntimeError(f"Blockscout logs failed {address} {a}-{b}: {j}")
        for x in j.get("result", []):
            key = (x.get("transactionHash"), x.get("logIndex"))
            if key not in seen:
                seen.add(key)
                rows.append(x)
    return rows


def normalize_log(x):
    topics = [Web3.to_bytes(hexstr=t) for t in x.get("topics",[]) if t]
    return {
        "address": Web3.to_checksum_address(x["address"]),
        "topics": topics,
        "data": Web3.to_bytes(hexstr=x.get("data","0x")),
        "blockNumber": int(x["blockNumber"],16),
        "transactionHash": Web3.to_bytes(hexstr=x["transactionHash"]),
        "transactionIndex": int(x.get("transactionIndex","0x0"),16),
        "blockHash": b"\x00"*32,
        "logIndex": int(x["logIndex"],16),
        "removed": False,
    }


def load_across_event_abis():
    abi = get_json(ACROSS["legacy"]["abi_url"])["abi"]
    wanted = {}
    for item in abi:
        if item.get("type") == "event" and item.get("name") in {
            "FundsDeposited","V3FundsDeposited","FilledRelay","FilledV3Relay"
        }:
            wanted[item["name"]] = item
    if not wanted:
        raise RuntimeError("Across event ABIs not found")
    return wanted


def collect_across(start, end):
    event_abis = load_across_event_abis()
    rows = []
    seen = set()
    for role, info in ACROSS.items():
        addr = info["address"]
        for name, abi in event_abis.items():
            topic = "0x" + event_abi_to_log_topic(abi).hex()
            raw = blockscout_logs(addr, start, end, topic)
            for x in raw:
                key = (x["transactionHash"], x["logIndex"])
                if key in seen:
                    continue
                seen.add(key)
                try:
                    decoded = get_event_data(W3.codec, abi, normalize_log(x))
                    args = dict(decoded["args"])
                except Exception as e:
                    print("ACROSS_DECODE_SKIP", role, name, key, repr(e), flush=True)
                    continue
                ts = int(x["timeStamp"],16)
                rows.append({
                    "protocol":"Across",
                    "chain":"base",
                    "contract_role":role,
                    "contract":addr,
                    "event":name,
                    "block_number":int(x["blockNumber"],16),
                    "timestamp":ts,
                    "tx_hash":x["transactionHash"],
                    "log_index":int(x["logIndex"],16),
                    "input_token":str(args.get("inputToken","")),
                    "output_token":str(args.get("outputToken","")),
                    "input_amount":str(args.get("inputAmount","")),
                    "output_amount":str(args.get("outputAmount","")),
                    "origin_chain_id":str(args.get("originChainId","")),
                    "destination_chain_id":str(args.get("destinationChainId","")),
                    "deposit_id":str(args.get("depositId","")),
                })
    keys = ["protocol","chain","contract_role","contract","event","block_number","timestamp","tx_hash","log_index",
            "input_token","output_token","input_amount","output_amount","origin_chain_id","destination_chain_id","deposit_id"]
    with (OUT/"across_events.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(sorted(rows,key=lambda r:(r["block_number"],r["log_index"])))
    return rows


def decode_addr_word(x):
    h=x[2:] if x.startswith("0x") else x
    return Web3.to_checksum_address("0x"+h[-40:])


def call_data(signature, args=()):
    from eth_abi import encode
    selector = Web3.keccak(text=signature)[:4]
    if not args:
        return "0x"+selector.hex()
    types = signature[signature.find("(")+1:signature.rfind(")")].split(",")
    return "0x"+(selector+encode(types,list(args))).hex()


def current_aero_pools():
    length_raw = rpc("eth_call",[{"to":AERO_FACTORY,"data":call_data("allPoolsLength()")},"latest"])
    n = int(length_raw,16)
    pools=[]
    for i in range(0,n,100):
        calls=[]
        for j in range(i,min(i+100,n)):
            calls.append(("eth_call",[{"to":AERO_FACTORY,"data":call_data("allPools(uint256)",(j,))},"latest"]))
        vals=rpc_batch(calls)
        pools.extend(decode_addr_word(v) for v in vals)
    return pools


def current_pool_metadata(pools):
    meta={}
    for i in range(0,len(pools),100):
        batch=pools[i:i+100]
        calls=[("eth_call",[{"to":p,"data":call_data("metadata()")},"latest"]) for p in batch]
        vals=rpc_batch(calls)
        from eth_abi import decode
        for pool,raw in zip(batch,vals):
            try:
                dec0,dec1,_,_,stable,t0,t1=decode(
                    ["uint256","uint256","uint256","uint256","bool","address","address"],
                    Web3.to_bytes(hexstr=raw)
                )
                meta[pool]={"dec0":int(dec0),"dec1":int(dec1),"stable":bool(stable),
                            "token0":Web3.to_checksum_address(t0),"token1":Web3.to_checksum_address(t1)}
            except Exception:
                pass
    return meta


def collect_aerodrome(start,end):
    pools=current_aero_pools()
    meta=current_pool_metadata(pools)
    # Honest priced lower bound: only pools touching tokens whose USD price is
    # provable from the V4 dataset or the USDC unit reference.
    selected=[
        p for p,m in meta.items()
        if m["token0"] in CORE_TOKENS or m["token1"] in CORE_TOKENS
    ]
    swap_topic="0x"+Web3.keccak(text="Swap(address,address,uint256,uint256,uint256,uint256)").hex()
    rows=[]
    seen=set()
    for idx,pool in enumerate(selected,1):
        m=meta[pool]
        raw=blockscout_logs(pool,start,end,swap_topic)
        for x in raw:
            key=(x["transactionHash"],x["logIndex"])
            if key in seen: continue
            seen.add(key)
            data=(x.get("data") or "0x")[2:]
            if len(data)<64*4:
                continue
            words=[int(data[i:i+64],16) for i in range(0,64*4,64)]
            rows.append({
                "protocol":"Aerodrome","chain":"base","pool":pool,
                "block_number":int(x["blockNumber"],16),"timestamp":int(x["timeStamp"],16),
                "tx_hash":x["transactionHash"],"log_index":int(x["logIndex"],16),
                "amount0_in":str(words[0]),"amount1_in":str(words[1]),
                "amount0_out":str(words[2]),"amount1_out":str(words[3]),
                "token0":m["token0"],"token1":m["token1"],
                "dec0":m["dec0"],"dec1":m["dec1"],"stable":m["stable"],
                "token0_priced_symbol":CORE_TOKENS.get(m["token0"],{}).get("symbol",""),
                "token1_priced_symbol":CORE_TOKENS.get(m["token1"],{}).get("symbol",""),
            })
        if idx%25==0:
            print("AERO_PROGRESS",idx,"/",len(selected),"rows",len(rows),flush=True)
    keys=["protocol","chain","pool","block_number","timestamp","tx_hash","log_index",
          "amount0_in","amount1_in","amount0_out","amount1_out","token0","token1","dec0","dec1","stable",
          "token0_priced_symbol","token1_priced_symbol"]
    with (OUT/"aerodrome_swaps.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(sorted(rows,key=lambda r:(r["block_number"],r["log_index"])))
    (OUT/"aerodrome_pools.json").write_text(json.dumps({
        "all_pools_current_count":len(pools),
        "metadata_count":len(meta),
        "selected_priced_lower_bound_pool_count":len(selected),
        "core_tokens":{k:v for k,v in CORE_TOKENS.items()},
        "selected_pools":{p:meta[p] for p in selected},
    },indent=2),encoding="utf-8")
    return rows,pools,meta,selected


def main():
    start=block_by_time(T0,"after")
    end=block_by_time(T1,"before")
    if start!=36_640_428 or end!=36_718_926:
        print("BOUNDARY_NOTE",start,end,flush=True)
    across=collect_across(start,end)
    aero,pools,meta,selected=collect_aerodrome(start,end)
    manifest={
        "classification":"BASE_OBSERVED_EXTERNAL_FLOW_LOWER_BOUND_RAW_ONCHAIN_EVENTS",
        "time_window":{"start":T0,"end":T1},
        "base_bounds":{"start":start,"end":end,"source":"Base Blockscout getblocknobytime"},
        "across":{"addresses":{k:v["address"] for k,v in ACROSS.items()},
                  "event_rows":len(across),"unique_tx":len({r["tx_hash"] for r in across})},
        "aerodrome":{"factory":AERO_FACTORY,"all_pools_current_count":len(pools),
                     "selected_priced_lower_bound_pool_count":len(selected),
                     "swap_rows":len(aero),"unique_tx":len({r["tx_hash"] for r in aero})},
        "pricing_scope":["USDC","WETH","AERO"],
        "files":["across_events.csv","aerodrome_swaps.csv","aerodrome_pools.json"],
        "note":"Raw Base lower-bound evidence. Blockscout supplies historical blocks/logs; ordinary current RPC is used only for immutable Aerodrome pool enumeration/metadata. USD valuation and private SYNERGY replay happen outside this collector."
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str),encoding="utf-8")
    print(json.dumps(manifest,indent=2,default=str),flush=True)


if __name__=="__main__":
    main()
