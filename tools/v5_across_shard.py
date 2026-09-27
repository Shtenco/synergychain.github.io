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

def main():
    OUT.mkdir(exist_ok=True)
    topics={c.TOPIC_OLD_DEPOSIT.lower(),c.TOPIC_NEW_DEPOSIT.lower()}
    if CHAIN=="ethereum":
        start,end=c.ETH_START,c.ETH_END
        raw=v2_address_logs("https://eth.blockscout.com",c.ETH_SPOKE,start,end,topics)
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
        raw=v2_address_logs("https://base.blockscout.com",c.BASE_SPOKE,start,end,topics)
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
