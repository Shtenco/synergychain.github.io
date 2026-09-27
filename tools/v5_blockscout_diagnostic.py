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


print("\n--- V2 FACTORY LOG PAGINATION PROBE ---")
u="https://base.blockscout.com/api/v2/addresses/0x420DD381b31aEf6683db6B902084cB0FFECe40Da/logs"
r=S.get(u,timeout=45)
print("V2 STATUS",r.status_code)
print(r.text[:4000])
r.raise_for_status()
j=r.json()
print("V2 ITEMS",len(j.get("items",[])))
print("V2 NEXT",j.get("next_page_params"))
assert isinstance(j.get("items"),list)
