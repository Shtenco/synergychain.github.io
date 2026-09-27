from __future__ import annotations
import csv,json,os,time
from pathlib import Path
from eth_abi import decode
import v5_public_external_flow_collector as c

POOL=os.environ["POOL"].lower()
TOKEN0=os.environ["TOKEN0"].lower()
TOKEN1=os.environ["TOKEN1"].lower()
STABLE=os.environ["STABLE"].lower()=="true"
OUT=Path("v5_aero_recovery")

def get_logs_rate_aware(start,end):
    endpoint="https://base.blockscout.com/api"
    cur=int(start); end=int(end); chunk=5000; initial=5000
    out=[]; seen=set()
    while cur<=end:
        hi=min(end,cur+chunk-1)
        params={
          "module":"logs","action":"getLogs","fromBlock":str(cur),"toBlock":str(hi),
          "address":POOL,"topic0":c.TOPIC_SWAP
        }
        rows=None; last=None
        for attempt in range(10):
            try:
                r=c.S.get(endpoint,params=params,timeout=45)
                if r.status_code==429:
                    retry=float(r.headers.get("Retry-After","0") or 0)
                    time.sleep(max(retry,min(3*(attempt+1),30))); continue
                r.raise_for_status()
                j=r.json()
                if str(j.get("status"))=="0" and j.get("message") not in ("No logs found","No transactions found"):
                    raise RuntimeError(j)
                result=j.get("result")
                rows=result if isinstance(result,list) else []
                break
            except Exception as e:
                last=e
                if attempt==9:
                    raise RuntimeError(f"targeted pool getLogs failed {POOL} {cur}-{hi}: {last!r}")
                time.sleep(min(3*(attempt+1),30))
        if len(rows)>=1000:
            if cur==hi: raise RuntimeError(f"single block exceeds cap {cur}")
            chunk=max(1,chunk//2); continue
        for row in rows:
            key=(row.get("transactionHash"),row.get("logIndex"))
            if key not in seen:
                seen.add(key); out.append(row)
        cur=hi+1
        if chunk<initial: chunk=min(initial,chunk*2)
        time.sleep(.6)
    return out

def main():
    OUT.mkdir(exist_ok=True)
    start=c.base_block_by_time(c.START_TS,"after")
    end=c.base_block_by_time(c.END_TS,"before")
    raw=get_logs_rate_aware(start,end)
    rows=[]
    for item in raw:
        x=c.decode_blockscout_log(item)
        if not x["topics"] or x["topics"][0].lower()!=c.TOPIC_SWAP.lower(): continue
        a0in,a1in,a0out,a1out=decode(["uint256","uint256","uint256","uint256"],bytes.fromhex(x["data"][2:]))
        bn=c.parse_intish(x["blockNumber"])
        ts=c.log_timestamp(x,lambda n=bn:c.base_block_timestamp(n))
        rows.append({
          "protocol":"AerodromeV2","chain_id":8453,"block_number":bn,"timestamp":ts,
          "tx_hash":x["transactionHash"],"log_index":c.parse_intish(x["logIndex"]),
          "pool":POOL,"token0":TOKEN0,"token1":TOKEN1,"stable":STABLE,
          "amount0_in":str(a0in),"amount1_in":str(a1in),
          "amount0_out":str(a0out),"amount1_out":str(a1out),
        })
    rows.sort(key=lambda r:(r["block_number"],r["log_index"]))
    fields=["protocol","chain_id","block_number","timestamp","tx_hash","log_index","pool","token0","token1","stable","amount0_in","amount1_in","amount0_out","amount1_out"]
    with (OUT/"aerodrome_swaps.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    m={
      "classification":"TARGETED_AERODROME_CORE_POOL_RECOVERY",
      "pool":POOL,"token0":TOKEN0,"token1":TOKEN1,"stable":STABLE,
      "base_blocks":[start,end],"swap_rows":len(rows),
      "source":"Blockscout legacy event-specific logs with cap splitting and rate-aware retry",
      "swap_signature":c.SWAP_SIG,"no_synthetic_prices":True
    }
    (OUT/"manifest.json").write_text(json.dumps(m,indent=2),encoding="utf-8")
    print(json.dumps(m,indent=2))
    print("V5 AERO TARGETED RECOVERY: PASS")

if __name__=="__main__": main()
