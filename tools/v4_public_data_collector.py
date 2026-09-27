from __future__ import annotations
import bisect, csv, io, json, math, time, zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import requests

START_BLOCK=23_544_921
END_BLOCK=23_557_920
BLOCK_COUNT=13_000
ASSETS=("WETH","cbBTC","VVV","VIRTUAL","AERO","cbETH","USDe","cbXRP","TOSHI","MORPHO")
XATU_ROOT="https://data.ethpandaops.io/xatu/mainnet/databases/default/canonical_execution_block/1000"
OUT=Path("v4_public_data")
S=requests.Session()
S.headers.update({"User-Agent":"SYNERGY-V4-public-data-collector/1.0"})

def get(url,*,params=None,attempts=6,timeout=60):
    last=None
    for i in range(attempts):
        try:
            r=S.get(url,params=params,timeout=timeout)
            if r.status_code==429:
                time.sleep(min(2**i,15)); continue
            r.raise_for_status(); return r
        except Exception as e:
            last=e; time.sleep(min(2**i,15))
    raise RuntimeError(f"GET failed: {url}: {last!r}")

def epoch_seconds(v):
    if isinstance(v,datetime):
        if v.tzinfo is None: v=v.replace(tzinfo=timezone.utc)
        return int(v.timestamp())
    if isinstance(v,np.datetime64):
        return int(v.astype("datetime64[s]").astype(np.int64))
    t=str(v)
    if t.isdigit():
        n=int(t)
        if n>10**15: return n//1_000_000
        if n>10**12: return n//1_000
        return n
    return int(datetime.fromisoformat(t.replace("Z","+00:00")).timestamp())

def fetch_blocks():
    rows=[]; urls=[]
    for chunk in range((START_BLOCK//1000)*1000,(END_BLOCK//1000)*1000+1,1000):
        url=f"{XATU_ROOT}/{chunk}.parquet"; urls.append(url)
        tab=pq.read_table(io.BytesIO(get(url).content),columns=["block_date_time","block_number","gas_used","base_fee_per_gas"])
        d=tab.to_pydict()
        for i,n0 in enumerate(d["block_number"]):
            n=int(n0)
            if START_BLOCK<=n<=END_BLOCK:
                rows.append({"block_number":n,"timestamp":epoch_seconds(d["block_date_time"][i]),"gas_used":int(d["gas_used"][i]),"base_fee_per_gas":int(d["base_fee_per_gas"][i])})
    rows.sort(key=lambda x:x["block_number"])
    nums=[x["block_number"] for x in rows]
    assert len(rows)==BLOCK_COUNT
    assert nums[0]==START_BLOCK and nums[-1]==END_BLOCK
    assert all(b==a+1 for a,b in zip(nums,nums[1:]))
    return rows,urls

def fetch_rpc_gas_limits(blocks):
    endpoint="https://ethereum-rpc.publicnode.com"
    by_number={b["block_number"]:b for b in blocks}
    for start in range(0,len(blocks),100):
        batch=blocks[start:start+100]
        payload=[{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[hex(b["block_number"]),False],"id":b["block_number"]} for b in batch]
        last=None
        for attempt in range(6):
            try:
                r=S.post(endpoint,json=payload,timeout=60)
                if r.status_code==429:
                    time.sleep(min(2**attempt,15)); continue
                r.raise_for_status()
                data=r.json()
                if not isinstance(data,list): raise RuntimeError(f"non-batch RPC response: {data}")
                got={int(x["id"]):x.get("result") for x in data if "id" in x}
                for b in batch:
                    n=b["block_number"]; x=got.get(n)
                    if not x: raise RuntimeError(f"missing RPC block {n}")
                    ts=int(x["timestamp"],16); gas_used=int(x["gasUsed"],16); base=int(x["baseFeePerGas"],16); gas_limit=int(x["gasLimit"],16)
                    if ts!=b["timestamp"]: raise RuntimeError(f"timestamp mismatch {n}: Xatu={b['timestamp']} RPC={ts}")
                    if gas_used!=b["gas_used"]: raise RuntimeError(f"gasUsed mismatch {n}: Xatu={b['gas_used']} RPC={gas_used}")
                    if base!=b["base_fee_per_gas"]: raise RuntimeError(f"baseFee mismatch {n}: Xatu={b['base_fee_per_gas']} RPC={base}")
                    if gas_limit<=0: raise RuntimeError(f"invalid gasLimit {n}: {gas_limit}")
                    by_number[n]["gas_limit"]=gas_limit
                break
            except Exception as e:
                last=e
                time.sleep(min(2**attempt,15))
        else:
            raise RuntimeError(f"RPC gasLimit batch failed at {batch[0]['block_number']}: {last!r}")
        time.sleep(.05)
    assert all("gas_limit" in b and b["gas_limit"]>0 for b in blocks)
    return {"source":endpoint,"method":"eth_getBlockByNumber","batch_size":100,"cross_checked_fields":["timestamp","gasUsed","baseFeePerGas"]}

def iso(ts): return datetime.fromtimestamp(ts,timezone.utc).isoformat().replace("+00:00","Z")

def coinbase(product,t0,t1):
    out={}; cur=t0
    while cur<=t1:
        end=min(t1,cur+299*60)
        r=get(f"https://api.exchange.coinbase.com/products/{product}/candles",params={"granularity":60,"start":iso(cur),"end":iso(end)},timeout=40)
        j=r.json()
        if isinstance(j,dict): raise RuntimeError(f"Coinbase {product}: {j}")
        for x in j:
            if len(x)>=5: out[int(x[0])]=float(x[4])
        cur=end+60; time.sleep(.12)
    if len(out)<30: raise RuntimeError(f"Coinbase {product} insufficient: {len(out)}")
    return out

def date_range(t0,t1):
    a=datetime.fromtimestamp(t0,timezone.utc).date(); b=datetime.fromtimestamp(t1,timezone.utc).date(); out=[]
    while a<=b: out.append(a.isoformat()); a+=timedelta(days=1)
    return out

def parse_open_time(raw):
    n=int(raw)
    if n>10**15: return n//1_000_000
    if n>10**12: return n//1_000
    return n

def binance_vision(symbol,t0,t1):
    roots=[("spot","https://data.binance.vision/data/spot/daily/klines"),("futures_um","https://data.binance.vision/data/futures/um/daily/klines")]
    last=None
    for venue,root in roots:
        out={}
        try:
            for day in date_range(t0,t1):
                fn=f"{symbol}-1m-{day}.zip"
                r=get(f"{root}/{symbol}/1m/{fn}",attempts=3,timeout=45)
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    names=z.namelist()
                    if not names: raise RuntimeError("empty zip")
                    text=z.read(names[0]).decode("utf-8")
                for row in csv.reader(io.StringIO(text)):
                    if not row or not row[0].lstrip("-").isdigit(): continue
                    ts=parse_open_time(row[0])
                    if t0-120<=ts<=t1+120: out[(ts//60)*60]=float(row[4])
            if len(out)>=30: return out,f"Binance Vision {venue} {symbol}"
        except Exception as e: last=e
    raise RuntimeError(f"Binance {symbol}: {last!r}")

def bybit(symbol,t0,t1):
    out={}; cur=t0; url="https://api.bybit.com/v5/market/kline"
    while cur<=t1:
        end=min(t1,cur+900*60)
        j=get(url,params={"category":"spot","symbol":symbol,"interval":"1","start":cur*1000,"end":end*1000,"limit":1000},timeout=45).json()
        if j.get("retCode")!=0: raise RuntimeError(f"Bybit {symbol}: {j}")
        for x in j.get("result",{}).get("list",[]):
            out[(int(x[0])//1000//60)*60]=float(x[4])
        cur=end+60; time.sleep(.12)
    if len(out)<30: raise RuntimeError(f"Bybit {symbol} insufficient: {len(out)}")
    return out

def try_sources(asset,candidates):
    errs=[]
    for label,fn in candidates:
        try:
            v=fn()
            if isinstance(v,tuple): series,actual=v
            else: series,actual=v,label
            if len(series)<30: raise RuntimeError(f"only {len(series)} rows")
            return series,{"asset":asset,"source":actual,"attempted":[x[0] for x in candidates]}
        except Exception as e: errs.append(f"{label}: {e!r}")
    raise RuntimeError(f"No real feed for {asset}: {' | '.join(errs)}")

def fetch_prices(blocks):
    t0=blocks[0]["timestamp"]-600; t1=blocks[-1]["timestamp"]+120
    cb=lambda p: lambda:(coinbase(p,t0,t1),f"Coinbase Exchange {p}")
    bv=lambda s: lambda:binance_vision(s,t0,t1)
    by=lambda s: lambda:(bybit(s,t0,t1),f"Bybit spot {s}")
    plan={
      "WETH":[("Coinbase ETH-USD",cb("ETH-USD")),("Binance ETHUSDT",bv("ETHUSDT"))],
      "cbBTC":[("Coinbase BTC-USD",cb("BTC-USD")),("Binance BTCUSDT",bv("BTCUSDT"))],
      "VVV":[("Coinbase VVV-USD",cb("VVV-USD")),("Binance VVVUSDT",bv("VVVUSDT"))],
      "VIRTUAL":[("Coinbase VIRTUAL-USD",cb("VIRTUAL-USD")),("Binance VIRTUALUSDT",bv("VIRTUALUSDT"))],
      "AERO":[("Coinbase AERO-USD",cb("AERO-USD")),("Binance AEROUSDT",bv("AEROUSDT"))],
      "cbETH":[("Coinbase CBETH-USD",cb("CBETH-USD")),("Coinbase CBETH-USDC",cb("CBETH-USDC"))],
      "USDe":[("Coinbase USDE-USD",cb("USDE-USD")),("Coinbase USDE-USDC",cb("USDE-USDC")),("Bybit USDEUSDT",by("USDEUSDT")),("Binance USDEUSDT",bv("USDEUSDT"))],
      "cbXRP":[("Coinbase XRP-USD underlying",cb("XRP-USD")),("Binance XRPUSDT underlying",bv("XRPUSDT"))],
      "TOSHI":[("Coinbase TOSHI-USD",cb("TOSHI-USD")),("Coinbase TOSHI-USDC",cb("TOSHI-USDC")),("Binance TOSHIUSDT",bv("TOSHIUSDT"))],
      "MORPHO":[("Coinbase MORPHO-USD",cb("MORPHO-USD")),("Coinbase MORPHO-USDC",cb("MORPHO-USDC")),("Binance MORPHOUSDT",bv("MORPHOUSDT"))],
    }
    raw={}; prov={}
    for a in ASSETS: raw[a],prov[a]=try_sources(a,plan[a])
    aligned={}
    for a in ASSETS:
        times=sorted(raw[a]); vals=[]; ages=[]
        for b in blocks:
            target=(b["timestamp"]//60)*60-60
            i=bisect.bisect_right(times,target)-1
            if i<0: raise RuntimeError(f"No causal price for {a} before block {b['block_number']}")
            ts=times[i]; age=target-ts
            vals.append(raw[a][ts]); ages.append(age)
        future=sum(1 for x in ages if x<0); mn=min(ages); mx=max(ages)
        if future: raise RuntimeError(f"{a} future candle violations={future}")
        if mx>3600: raise RuntimeError(f"{a} staleness={mx}s")
        if any(v<=0 or not math.isfinite(v) for v in vals): raise RuntimeError(f"{a} invalid price")
        aligned[a]=vals
        prov[a].update({"candle_rows":len(raw[a]),"min_alignment_age_seconds":mn,"max_forward_fill_staleness_seconds":mx,"future_candle_violations":future,"alignment":"last fully completed 1-minute candle; causal backward lookup/forward-fill","price_role":"redeemable_1_to_1_underlying" if a in {"WETH","cbBTC","cbXRP"} else "direct_market_price"})
    return aligned,prov

def main():
    OUT.mkdir(exist_ok=True)
    blocks,urls=fetch_blocks()
    rpc_provenance=fetch_rpc_gas_limits(blocks)
    prices,prov=fetch_prices(blocks)
    csv_path=OUT/"ethereum_23544921_23557920_exact_gas_real_prices.csv"
    fields=["block_number","timestamp","gas_used","gas_limit","base_fee_per_gas","base_fee_gwei"]+[f"{a}_usd" for a in ASSETS]
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for i,b in enumerate(blocks):
            r=dict(b); r["base_fee_gwei"]=b["base_fee_per_gas"]/1e9
            for a in ASSETS: r[f"{a}_usd"]=prices[a][i]
            w.writerow(r)
    manifest={"classification":"PUBLIC RAW HISTORICAL INPUTS ONLY — NO PRIVATE V4 ECONOMIC FORMULAS","ethereum_blocks":{"start":START_BLOCK,"end":END_BLOCK,"count":len(blocks),"contiguous":True,"timestamp_start":blocks[0]["timestamp"],"timestamp_end":blocks[-1]["timestamp"],"xatu_partitions":urls},"market_inputs":{"assets":list(ASSETS),"factor_mapped_assets":[],"provenance":prov,"alignment":"last fully completed 1-minute candle; causal only"},"gas_input":{"xatu_exact_fields":["block_date_time","gas_used","base_fee_per_gas"],"rpc_exact_fields":["gasLimit"],"rpc_provenance":rpc_provenance,"cross_source_validation":"timestamp/gasUsed/baseFeePerGas must match Xatu exactly"}}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    assert len(blocks)==13000 and len(prov)==10
    assert all(v["future_candle_violations"]==0 and v["min_alignment_age_seconds"]>=0 for v in prov.values())
    print(json.dumps(manifest,indent=2))
    print("PUBLIC V4 DATA GATES: PASS")

if __name__=="__main__": main()
