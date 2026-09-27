import json, requests, sys
BASE="https://base.blockscout.com/api"
S=requests.Session(); S.headers["User-Agent"]="SYNERGY-V5-blockscout-diagnostic/1.0"

def q(params):
    r=S.get(BASE,params=params,timeout=45)
    print("URL",r.url)
    print("STATUS",r.status_code)
    print(r.text[:2000])
    r.raise_for_status()
    return r.json()

a=q({"module":"block","action":"getblocknobytime","timestamp":"1760070203","closest":"after"})
assert str(a.get("status"))=="1", a
bn=int(a["result"]["blockNumber"] if isinstance(a["result"],dict) else a["result"])
print("BLOCK",bn)
b=q({"module":"logs","action":"getLogs","fromBlock":str(bn),"toBlock":str(bn+5000),"address":"0x420DD381b31aEf6683db6B902084cB0FFECe40Da"})
assert "result" in b, b
print("LOGS",len(b.get("result",[])))
