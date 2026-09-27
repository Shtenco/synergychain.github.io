from __future__ import annotations
import csv, json, os
from pathlib import Path
import v5_public_external_flow_collector as c
from v5_across_only import v2_address_logs

CHAIN=os.environ["CHAIN"].strip().lower()
OUT=Path("v5_across_shard")

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def event_logs_rate_aware(base_url: str, address: str, start: int, end: int, topic0: str, initial_chunk: int):
    endpoint=base_url+"/api"
    out=[]; seen=set(); cur=int(start); chunk=int(initial_chunk)
    while cur<=end:
        hi=min(int(end),cur+chunk-1)
        params={
            "module":"logs","action":"getLogs","fromBlock":str(cur),"toBlock":str(hi),
            "address":address,"topic0":topic0,
        }
        last=None
        for attempt in range(10):
            try:
                r=c.S.get(endpoint,params=params,timeout=45)
                if r.status_code==429:
                    import time
                    retry=float(r.headers.get("Retry-After","0") or 0)
                    time.sleep(max(retry,min(3*(attempt+1),30)))
                    continue
                r.raise_for_status()
                j=r.json()
                if str(j.get("status"))=="0" and j.get("message") not in ("No logs found","No transactions found"):
                    raise RuntimeError(j)
                rows=j.get("result",[]) if isinstance(j.get("result"),list) else []
                break
            except Exception as e:
                last=e
                if attempt==9:
                    raise RuntimeError(f"rate-aware getLogs failed {base_url} {cur}-{hi}: {last!r}")
                import time
                time.sleep(min(3*(attempt+1),30))
        if len(rows)>=1000:
            if cur==hi:
                raise RuntimeError(f"single block exceeds 1000-log cap: {cur}")
            chunk=max(1,chunk//2)
            continue
        for row in rows:
            key=(row.get("transactionHash"),row.get("logIndex"),row.get("address"))
            if key not in seen:
                seen.add(key); out.append(row)
        cur=hi+1
        if chunk<initial_chunk:
            chunk=min(initial_chunk,chunk*2)
        import time
        time.sleep(0.60)
    return out

def main():
    OUT.mkdir(exist_ok=True)
    topics={c.TOPIC_OLD_DEPOSIT.lower(),c.TOPIC_NEW_DEPOSIT.lower()}
    if CHAIN=="ethereum":
        start,end=c.ETH_START,c.ETH_END
        raw=[]
        for topic in sorted(topics):
            raw.extend(event_logs_rate_aware("https://eth.blockscout.com",c.ETH_SPOKE,start,end,topic,5_000))
        v4_ts=c.load_v4_timestamp_map()
        rows=[]
        for item in raw:
            norm=c.decode_blockscout_log({
                "address":item.get("address",{}).get("hash",c.ETH_SPOKE) if isinstance(item.get("address"),dict) else item.get("address",c.ETH_SPOKE),
                "topics":item.get("topics",[]),"data":item.get("data","0x"),
                "blockNumber":str(item.get("block_number",0)),
                "transactionHash":item.get("transaction_hash",""),
                "logIndex":str(item.get("index",0)),
                "timestamp":item.get("block_timestamp"),
            })
            r=c.decode_deposit(norm,1)
            n=int(r["block_number"])
            if n not in v4_ts: raise RuntimeError(f"ETH event outside V4 map: {n}")
            r["timestamp"]=v4_ts[n]; rows.append(r)
        chain_id=1; spoke=c.ETH_SPOKE
    elif CHAIN=="base":
        start=c.base_block_by_time(c.START_TS,"after"); end=c.base_block_by_time(c.END_TS,"before")
        raw=[]
        for topic in sorted(topics):
            raw.extend(event_logs_rate_aware("https://base.blockscout.com",c.BASE_SPOKE,start,end,topic,10_000))
        rows=[]
        for item in raw:
            norm=c.decode_blockscout_log({
                "address":item.get("address",{}).get("hash",c.BASE_SPOKE) if isinstance(item.get("address"),dict) else item.get("address",c.BASE_SPOKE),
                "topics":item.get("topics",[]),"data":item.get("data","0x"),
                "blockNumber":str(item.get("block_number",0)),
                "transactionHash":item.get("transaction_hash",""),
                "logIndex":str(item.get("index",0)),
                "timestamp":item.get("block_timestamp"),
            })
            r=c.decode_deposit(norm,8453)
            r["timestamp"]=c.log_timestamp(norm,lambda n=int(r["block_number"]): c.base_block_timestamp(n))
            rows.append(r)
        chain_id=8453; spoke=c.BASE_SPOKE
    else:
        raise RuntimeError(CHAIN)

    for r in rows:
        r["selected_eth_base_corridor"]=(
            (r["origin_chain_id"]==1 and r["destination_chain_id"]==8453) or
            (r["origin_chain_id"]==8453 and r["destination_chain_id"]==1)
        )
    rows.sort(key=lambda r:(r["timestamp"],r["block_number"],r["tx_hash"]))
    fields=["event","origin_chain_id","destination_chain_id","deposit_id","block_number","timestamp","tx_hash",
            "input_token","output_token","input_amount","output_amount","quote_timestamp","fill_deadline",
            "exclusivity_deadline","selected_eth_base_corridor","raw_topic0","raw_data"]
    write_csv(OUT/"across_events.csv",rows,fields)
    manifest={
      "classification":"PUBLIC_RAW_ACROSS_CHAIN_SHARD",
      "chain":CHAIN,"chain_id":chain_id,"spokepool":spoke,
      "block_range":[start,end],"rows":len(rows),
      "eth_base_corridor_rows":sum(bool(x["selected_eth_base_corridor"]) for x in rows),
      "cursor_api":"Blockscout v2 address logs",
      "event_topics":sorted(topics),
      "no_synthetic_prices":True
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    if len(rows)==0: raise RuntimeError("zero Across rows")

if __name__=="__main__": main()
