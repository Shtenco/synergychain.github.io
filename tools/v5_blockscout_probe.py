import json, requests
BASE="https://base.blockscout.com/api"
tests=[
 ("start_block",{"module":"block","action":"getblocknobytime","timestamp":"1760070203","closest":"after"}),
 ("end_block",{"module":"block","action":"getblocknobytime","timestamp":"1760227199","closest":"before"}),
 ("across_logs",{"module":"logs","action":"getLogs","fromBlock":"0","toBlock":"latest","address":"0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64","page":"1","offset":"5"}),
 ("factory_logs",{"module":"logs","action":"getLogs","fromBlock":"0","toBlock":"latest","address":"0x420DD381b31aEf6683db6B902084cB0FFECe40Da","page":"1","offset":"5"}),
]
for name,p in tests:
    r=requests.get(BASE,params=p,timeout=60)
    print("TEST",name,"URL",r.url,"STATUS",r.status_code)
    print(r.text[:5000])
