from __future__ import annotations
import csv, json
from pathlib import Path
import v5_public_external_flow_collector as c

OUT=Path("v5_across_raw")

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def v2_address_logs(base_url: str, address: str, start_block: int, end_block: int, topics: set[str]):
    url=f"{base_url}/api/v2/addresses/{address}/logs"
    params={"block_number":str(int(end_block)),"index":str(2_147_483_647),"items_count":"50"}
    out=[]
    while True:
        last=None
        for attempt in range(6):
            try:
                r=c.S.get(url,params=params,timeout=30)
                if r.status_code==429:
                    import time
                    time.sleep(min(2**attempt,10)); continue
                r.raise_for_status()
                page=r.json(); break
            except Exception as e:
                last=e
                if attempt==5:
                    raise RuntimeError(f"v2 logs failed {base_url} {address}: {last!r}")
                import time
                time.sleep(min(2**attempt,10))
        stop=False
        for item in page.get("items",[]):
            bn=int(item.get("block_number") or 0)
            if bn < start_block:
                stop=True; break
            if bn > end_block:
                continue
            t=item.get("topics") or []
            if t and t[0].lower() in topics:
                out.append(item)
        if stop:
            return out
        nxt=page.get("next_page_params")
        if not nxt:
            return out
        params={k:str(v) for k,v in nxt.items()}

def main():
    OUT.mkdir(exist_ok=True)
    base_start=c.base_block_by_time(c.START_TS,"after")
    base_end=c.base_block_by_time(c.END_TS,"before")
    v4_ts_map=c.load_v4_timestamp_map()

    deposit_topics={c.TOPIC_OLD_DEPOSIT.lower(),c.TOPIC_NEW_DEPOSIT.lower()}
    eth_logs_raw=v2_address_logs(
        "https://eth.blockscout.com",
        c.ETH_SPOKE,
        c.ETH_START,
        c.ETH_END,
        deposit_topics,
    )
    eth_rows=[]
    for raw in eth_logs_raw:
        norm=c.decode_blockscout_log(raw)
        row=c.decode_deposit(norm,1)
        n=int(row["block_number"])
        if n not in v4_ts_map:
            raise RuntimeError(f"Ethereum Across event outside V4 map: {n}")
        row["timestamp"]=v4_ts_map[n]
        eth_rows.append(row)

    base_logs_raw=v2_address_logs(
        "https://base.blockscout.com",
        c.BASE_SPOKE,
        base_start,
        base_end,
        deposit_topics,
    )
    base_rows=[]
    cache={}
    for raw in base_logs_raw:
        norm=c.decode_blockscout_log(raw)
        row=c.decode_deposit(norm,8453)
        n=int(row["block_number"])
        def fallback(n=n):
            if n not in cache:
                cache[n]=c.base_block_timestamp(n)
            return cache[n]
        row["timestamp"]=c.log_timestamp(norm,fallback)
        base_rows.append(row)

    rows=sorted(eth_rows+base_rows,key=lambda r:(r["timestamp"],r["origin_chain_id"],r["block_number"]))
    for r in rows:
        r["selected_eth_base_corridor"]=(
            (r["origin_chain_id"]==1 and r["destination_chain_id"]==8453) or
            (r["origin_chain_id"]==8453 and r["destination_chain_id"]==1)
        )

    fields=[
        "event","origin_chain_id","destination_chain_id","deposit_id","block_number","timestamp","tx_hash",
        "input_token","output_token","input_amount","output_amount","quote_timestamp","fill_deadline",
        "exclusivity_deadline","selected_eth_base_corridor","raw_topic0","raw_data"
    ]
    write_csv(OUT/"across_events.csv",rows,fields)

    manifest={
        "classification":"PUBLIC_RAW_ACROSS_ETHEREUM_BASE_DEPOSITS",
        "window":{"timestamp_start":c.START_TS,"timestamp_end":c.END_TS,"ethereum_blocks":[c.ETH_START,c.ETH_END],"base_blocks":[base_start,base_end]},
        "ethereum_spokepool":c.ETH_SPOKE,
        "base_spokepool":c.BASE_SPOKE,
        "event_signatures":[c.OLD_DEPOSIT_SIG,c.NEW_DEPOSIT_SIG],
        "deposit_rows_total":len(rows),
        "eth_base_corridor_deposits":sum(bool(x["selected_eth_base_corridor"]) for x in rows),
        "ethereum_rows":len(eth_rows),
        "base_rows":len(base_rows),
        "provenance":"Blockscout indexed historical logs + official Across deployed SpokePool addresses",
        "no_synthetic_prices":True
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    if manifest["eth_base_corridor_deposits"]<=0:
        raise RuntimeError("zero Ethereum<->Base Across deposits")
    print(json.dumps(manifest,indent=2))
    print("V5 ACROSS RAW EVIDENCE: PASS")

if __name__=="__main__":
    main()
