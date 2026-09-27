from __future__ import annotations
import csv, json
from pathlib import Path
from tools import v5_public_external_flow_collector as c

OUT=Path("v5_across_raw")

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    base_start=c.base_block_by_time(c.START_TS,"after")
    base_end=c.base_block_by_time(c.END_TS,"before")
    v4_ts_map=c.load_v4_timestamp_map()

    eth_logs_raw=[]
    for topic in (c.TOPIC_OLD_DEPOSIT,c.TOPIC_NEW_DEPOSIT):
        eth_logs_raw.extend(c.eth_logs(c.ETH_SPOKE,c.ETH_START,c.ETH_END,topic0=topic))
    eth_rows=[]
    for raw in eth_logs_raw:
        norm=c.decode_blockscout_log(raw)
        row=c.decode_deposit(norm,1)
        n=int(row["block_number"])
        if n not in v4_ts_map:
            raise RuntimeError(f"Ethereum Across event outside V4 map: {n}")
        row["timestamp"]=v4_ts_map[n]
        eth_rows.append(row)

    base_logs_raw=[]
    for topic in (c.TOPIC_OLD_DEPOSIT,c.TOPIC_NEW_DEPOSIT):
        base_logs_raw.extend(c.base_logs(c.BASE_SPOKE,base_start,base_end,topic0=topic))
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
