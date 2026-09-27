from __future__ import annotations
import csv, json, os
from pathlib import Path
from tools import v5_public_external_flow_collector as c

OUT=Path("v5_aero_shard")
SHARD_INDEX=int(os.environ["SHARD_INDEX"])
SHARD_TOTAL=int(os.environ["SHARD_TOTAL"])

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    base_start=c.base_block_by_time(c.START_TS,"after")
    base_end=c.base_block_by_time(c.END_TS,"before")
    pools=c.discover_aero_pools(base_end)
    pools=sorted(pools,key=lambda p:p["pool"])
    shard=[p for i,p in enumerate(pools) if i % SHARD_TOTAL == SHARD_INDEX]
    swaps,selected,scanned,failures=c.collect_swaps(shard,base_start,base_end)

    write_csv(OUT/"aerodrome_swaps.csv",swaps,[
        "protocol","chain_id","block_number","timestamp","tx_hash","log_index","pool","token0","token1",
        "stable","amount0_in","amount1_in","amount0_out","amount1_out"
    ])
    write_csv(OUT/"aerodrome_pools.csv",shard,[
        "pool","token0","token1","stable","factory_index","created_block","selected_for_pricing"
    ])
    manifest={
        "classification":"PUBLIC_RAW_AERODROME_V2_SHARD_LOWER_BOUND",
        "shard_index":SHARD_INDEX,
        "shard_total":SHARD_TOTAL,
        "base_blocks":[base_start,base_end],
        "all_selected_pools":len(pools),
        "shard_pool_count":len(shard),
        "successfully_scanned_pools":scanned,
        "failed_pool_scans":len(failures),
        "scan_failures":failures,
        "scan_coverage_fraction":(scanned/len(shard)) if shard else 1.0,
        "swap_rows":len(swaps),
        "factory":c.AERO_FACTORY,
        "swap_signature":c.SWAP_SIG,
        "selection":"Aerodrome V2 pools where token0 or token1 is Base USDC/WETH/AERO",
        "no_synthetic_prices":True
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    print("V5 AERODROME SHARD DONE")

if __name__=="__main__":
    main()
