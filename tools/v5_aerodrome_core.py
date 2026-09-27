from __future__ import annotations
import csv, json
from pathlib import Path
import v5_public_external_flow_collector as c

OUT=Path("v5_aero_core")
SUPPORTED={c.BASE_USDC,c.BASE_WETH,c.BASE_AERO}

def write_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    base_start=c.base_block_by_time(c.START_TS,"after")
    base_end=c.base_block_by_time(c.END_TS,"before")
    all_selected=c.discover_aero_pools(base_end)
    core=[
        p for p in all_selected
        if p["token0"] in SUPPORTED and p["token1"] in SUPPORTED and p["token0"]!=p["token1"]
    ]
    core=sorted(core,key=lambda p:(p["token0"],p["token1"],p["stable"],p["pool"]))
    swaps,selected,scanned,failures=c.collect_swaps(core,base_start,base_end)

    write_csv(OUT/"aerodrome_swaps.csv",swaps,[
        "protocol","chain_id","block_number","timestamp","tx_hash","log_index","pool","token0","token1",
        "stable","amount0_in","amount1_in","amount0_out","amount1_out"
    ])
    write_csv(OUT/"aerodrome_pools.csv",core,[
        "pool","token0","token1","stable","factory_index","created_block","selected_for_pricing"
    ])
    manifest={
      "classification":"AERODROME_CORE_PRICED_PAIR_OBSERVED_LOWER_BOUND",
      "base_blocks":[base_start,base_end],
      "broad_pricable_pool_universe":len(all_selected),
      "core_pool_count":len(core),
      "successfully_scanned_core_pools":scanned,
      "failed_core_pool_scans":len(failures),
      "scan_failures":failures,
      "core_scan_coverage_fraction":(scanned/len(core)) if core else 0.0,
      "swap_rows":len(swaps),
      "factory":c.AERO_FACTORY,
      "swap_signature":c.SWAP_SIG,
      "supported_tokens":{
        "USDC":c.BASE_USDC,
        "WETH":c.BASE_WETH,
        "AERO":c.BASE_AERO
      },
      "scope_rule":"both pool tokens must be in proven Base USDC/WETH/AERO set",
      "excluded_pool_count":len(all_selected)-len(core),
      "coverage_claim":"CORE_PAIR_LOWER_BOUND_ONLY; NOT ALL_AERODROME_VOLUME",
      "no_synthetic_prices":True
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    if not core: raise RuntimeError("zero core Aerodrome pools")
    if scanned<=0: raise RuntimeError("zero successfully scanned core pools")
    if not swaps: raise RuntimeError("zero core Aerodrome swaps")
    print(json.dumps(manifest,indent=2))
    print("V5 AERODROME CORE LOWER-BOUND: PASS")

if __name__=="__main__": main()
