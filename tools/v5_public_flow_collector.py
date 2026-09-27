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


def get_json(url, *, params=None, attempts=12, timeout=60):
    last = None
    for i in range(attempts):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                retry = r.headers.get("Retry-After")
                delay = float(retry) if retry and retry.replace(".","",1).isdigit() else min(2 ** i, 20)
                time.sleep(max(1.0, delay))
                continue
            r.raise_for_status()
            time.sleep(0.20)
            return r.json()
        except Exception as e:
            last = e
            time.sleep(min(2 ** i, 20))
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
    j = get_json(BLOCKSCOUT, params={"module":"block","def blockscout_logs(address, start, end, topic0=None):
    seen = {}

    def fetch_range(a, b, depth=0):
        params = {
            "module":"logs",
            "action":"getLogs",
            "fromBlock":str(a),
            "toBlock":str(b),
            "address":address,
        }
        if topic0:
            params["topic0"] = topic0
        try:
            j = get_json(BLOCKSCOUT, params=params, timeout=90)
        except Exception:
            if a < b and depth < 12:
                mid = (a + b) // 2
                fetch_range(a, mid, depth + 1)
                fetch_range(mid + 1, b, depth + 1)
                return
            raise

        status = str(j.get("status"))
        if status == "0":
            msg = str(j.get("message","")) + " " + str(j.get("result",""))
            if "No logs" in msg or "No records" in msg:
                return
            if a < b and depth < 12:
                mid = (a + b) // 2
                fetch_range(a, mid, depth + 1)
                fetch_range(mid + 1, b, depth + 1)
                return
            raise RuntimeError(f"Blockscout logs failed {address} {a}-{b}: {j}")

        result = j.get("result", [])
        # Defensive cap handling: if a range returns a very large page,
        # split it to prove we did not silently truncate events.
        if len(result) >= 950 and a < b and depth < 12:
            mid = (a + b) // 2
            fetch_range(a, mid, depth + 1)
            fetch_range(mid + 1, b, depth + 1)
            return

        for x in result:
            key = (x.get("transactionHash"), x.get("logIndex"))
            seen[key] = x

    fetch_range(start, end)
    return list(seen.values())
