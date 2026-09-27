from __future__ import annotations
import csv, json, time
from pathlib import Path
import requests
from web3 import Web3

T0=1760070203
T1=1760227199
OUT=Path("v5_public_flow")
OUT.mkdir(exist_ok=True)

RPC={
    "ethereum":"https://ethereum-rpc.publicnode.com",
    "base":"https://base-rpc.publicnode.com",
}
W3={k:Web3(Web3.HTTPProvider(v,request_kwargs={"timeout":60})) for k,v in RPC.items()}

ACROSS={
    "ethereum":{
        "legacy":"0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5",
        "current":"0xFBc81a18EcDa8E6A91275cFDF5FC6d91A7C5AE80",
        "abi_url":"https://raw.githubusercontent.com/across-protocol/contracts/master/deployments/mainnet/Ethereum_SpokePool.json",
    },
    "base":{
        "legacy":"0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64",
        "current":"0x6C99671B249af73B2847D92123d823Cb3875E399",
        "abi_url":"https://raw.githubusercontent.com/across-protocol/contracts/master/deployments/base/Base_SpokePool.json",
    },
}
AERO_FACTORY=Web3.to_checksum_address("0x420DD381b31aEf6683db6B902084cB0FFECe40Da")
SWAP_TOPIC=Web3.keccak(text="Swap(address,address,uint256,uint256,uint256,uint256)").hex()

S=requests.Session()
S.headers.update({"User-Agent":"SYNERGY-V5-public-flow-collector/1.0"})

def get_json(url):
    r=S.get(url,timeout=60); r.raise_for_status(); return r.json()

def rpc(chain,method,params,attempts=6):
    last=None
    for i in range(attempts):
        try:
            r=S.post(RPC[chain],json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
            r.raise_for_status(); j=r.json()
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except Exception as e:
            last=e; time.sleep(min(2**i,10))
    raise RuntimeError(f"{chain} {method} failed: {last!r}")

def rpc_batch(chain,calls,attempts=5):
    payload=[{"jsonrpc":"2.0","id":i,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    last=None
    for k in range(attempts):
        try:
            r=S.post(RPC[chain],json=payload,timeout=90); r.raise_for_status(); js=r.json()
            by={x["id"]:x for x in js}
            out=[]
            for i in range(len(calls)):
                x=by[i]
                if "error" in x: raise RuntimeError(x["error"])
                out.append(x["result"])
            return out
        except Exception as e:
            last=e; time.sleep(min(2**k,10))
    raise RuntimeError(f"batch failed {chain}: {last!r}")

def block_ts(chain,n):
    b=rpc(chain,"eth_getBlockByNumber",[hex(n),False])
    return int(b["timestamp"],16)

def boundary(chain,target,left=True):
    if chain=="ethereum":
        if target==T0:
            return 23_544_921
        if target==T1:
            return 23_557_920
    hi=int(rpc(chain,"eth_blockNumber",[]),16)
    # Base produces roughly one block every ~2s.  The target is Oct-2025,
    # so searching the recent 25M-block window avoids pruned genesis history.
    lo=max(1,hi-25_000_000)
    # tighten the lower edge upward until it is queryable
    while lo<hi:
        try:
            block_ts(chain,lo)
            break
        except Exception:
            lo+=1_000_000
    while lo<hi:
        mid=(lo+hi)//2
        ts=block_ts(chain,mid)
        if ts<target or (not left and ts<=target):
            lo=mid+1
        else:
            hi=mid
    return lo if left else lo-1

def as_text(v):
    if isinstance(v,bytes): return "0x"+v.hex()
    if hasattr(v,"hex") and not isinstance(v,str):
        try:return v.hex()
        except:pass
    return str(v)

def load_across_abi(url):
    return get_json(url)["abi"]

def collect_across():
    rows=[]; bounds={}
    for chain in ("ethereum","base"):
        w3=W3[chain]
        start=boundary(chain,T0,True); end=boundary(chain,T1,False)
        bounds[chain]={"start":start,"end":end,"start_ts":block_ts(chain,start),"end_ts":block_ts(chain,end)}
        abi=load_across_abi(ACROSS[chain]["abi_url"])
        addresses=[]
        for role in ("legacy","current"):
            a=Web3.to_checksum_address(ACROSS[chain][role])
            if a not in addresses: addresses.append(a)
        for addr in addresses:
            c=w3.eth.contract(address=addr,abi=abi)
            for name in ("FundsDeposited","V3FundsDeposited","FilledRelay","FilledV3Relay"):
                try: ev=getattr(c.events,name)
                except Exception: continue
                for a in range(start,end+1,2000):
                    b=min(end,a+1999)
                    try:
                        logs=ev().get_logs(from_block=a,to_block=b)
                    except Exception as e:
                        print("ACROSS_RETRY",chain,addr,name,a,b,repr(e),flush=True)
                        time.sleep(1)
                        logs=ev().get_logs(from_block=a,to_block=b)
                    for log in logs:
                        args=dict(log["args"])
                        bn=int(log["blockNumber"]); ts=block_ts(chain,bn)
                        rows.append({
                            "protocol":"Across","chain":chain,"contract":addr,"event":name,
                            "block_number":bn,"timestamp":ts,
                            "tx_hash":log["transactionHash"].hex(),"log_index":int(log["logIndex"]),
                            "input_token":as_text(args.get("inputToken","")),
                            "output_token":as_text(args.get("outputToken","")),
                            "input_amount":str(args.get("inputAmount","")),
                            "output_amount":str(args.get("outputAmount","")),
                            "origin_chain_id":str(args.get("originChainId","")),
                            "destination_chain_id":str(args.get("destinationChainId","")),
                            "deposit_id":str(args.get("depositId","")),
                        })
    keys=["protocol","chain","contract","event","block_number","timestamp","tx_hash","log_index","input_token","output_token","input_amount","output_amount","origin_chain_id","destination_chain_id","deposit_id"]
    with (OUT/"across_events.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    return rows,bounds

def decode_addr_word(x):
    h=x[2:] if x.startswith("0x") else x
    return Web3.to_checksum_address("0x"+h[-40:])

def aero_pools_at(end_block):
    w3=W3["base"]
    abi=[
      {"inputs":[],"name":"allPoolsLength","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},
      {"inputs":[{"type":"uint256"}],"name":"allPools","outputs":[{"type":"address"}],"stateMutability":"view","type":"function"},
    ]
    c=w3.eth.contract(address=AERO_FACTORY,abi=abi)
    n=c.functions.allPoolsLength().call(block_identifier=end_block)
    pools=[]
    for i in range(0,n,100):
        calls=[]
        for j in range(i,min(i+100,n)):
            data=c.encode_abi("allPools",args=[j])
            calls.append(("eth_call",[{"to":AERO_FACTORY,"data":data},hex(end_block)]))
        vals=rpc_batch("base",calls)
        pools.extend(decode_addr_word(v) for v in vals)
    return pools

def get_logs_base(addresses,start,end):
    out=[]
    for ai in range(0,len(addresses),100):
        batch=addresses[ai:ai+100]
        for a in range(start,end+1,3000):
            b=min(end,a+2999)
            try:
                vals=rpc("base","eth_getLogs",[{"fromBlock":hex(a),"toBlock":hex(b),"address":batch,"topics":[SWAP_TOPIC]}])
            except Exception:
                vals=[]
                for x in batch:
                    vals.extend(rpc("base","eth_getLogs",[{"fromBlock":hex(a),"toBlock":hex(b),"address":x,"topics":[SWAP_TOPIC]}]))
            out.extend(vals)
    return out

def pool_metadata(pool,block):
    abi=[{"inputs":[],"name":"metadata","outputs":[{"type":"uint256"},{"type":"uint256"},{"type":"uint256"},{"type":"uint256"},{"type":"bool"},{"type":"address"},{"type":"address"}],"stateMutability":"view","type":"function"}]
    c=W3["base"].eth.contract(address=pool,abi=abi)
    try:
        dec0,dec1,_,_,stable,t0,t1=c.functions.metadata().call(block_identifier=block)
        return {"dec0":int(dec0),"dec1":int(dec1),"stable":bool(stable),"token0":t0,"token1":t1}
    except Exception:
        return None

def collect_aero(base_bounds):
    start=base_bounds["start"]; end=base_bounds["end"]
    pools=aero_pools_at(end)
    logs=get_logs_base(pools,start,end)
    meta={}
    rows=[]
    for x in logs:
        pool=Web3.to_checksum_address(x["address"])
        if pool not in meta: meta[pool]=pool_metadata(pool,end)
        m=meta[pool]
        data=x["data"][2:] if isinstance(x["data"],str) else x["data"].hex()
        words=[int(data[i:i+64],16) for i in range(0,256,64)]
        bn=int(x["blockNumber"],16); ts=block_ts("base",bn)
        rows.append({
          "protocol":"Aerodrome","chain":"base","pool":pool,"block_number":bn,"timestamp":ts,
          "tx_hash":x["transactionHash"],"log_index":int(x["logIndex"],16),
          "amount0_in":str(words[0]),"amount1_in":str(words[1]),"amount0_out":str(words[2]),"amount1_out":str(words[3]),
          "token0":m["token0"] if m else "","token1":m["token1"] if m else "",
          "dec0":m["dec0"] if m else "","dec1":m["dec1"] if m else "","stable":m["stable"] if m else "",
        })
    keys=["protocol","chain","pool","block_number","timestamp","tx_hash","log_index","amount0_in","amount1_in","amount0_out","amount1_out","token0","token1","dec0","dec1","stable"]
    with (OUT/"aerodrome_swaps.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    (OUT/"aerodrome_pools.json").write_text(json.dumps({"pool_count":len(pools),"pools":pools,"metadata":meta},indent=2),encoding="utf-8")
    return rows,pools,meta

def main():
    across,bounds=collect_across()
    aero,pools,meta=collect_aero(bounds["base"])
    manifest={
      "classification":"OBSERVED_EXTERNAL_FLOW_LOWER_BOUND_RAW_ONCHAIN_EVENTS",
      "time_window":{"start":T0,"end":T1},
      "chain_bounds":bounds,
      "across":{"addresses":ACROSS,"event_rows":len(across),"unique_tx":len({r["tx_hash"] for r in across})},
      "aerodrome":{"factory":AERO_FACTORY,"pool_count":len(pools),"swap_rows":len(aero),"unique_tx":len({r["tx_hash"] for r in aero})},
      "files":["across_events.csv","aerodrome_swaps.csv","aerodrome_pools.json"],
      "note":"Raw evidence only. USD valuation and private SYNERGY HardNAV replay are intentionally performed outside this public collector."
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2),flush=True)

if __name__=="__main__": main()
