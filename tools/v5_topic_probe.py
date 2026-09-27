import requests, json
BASE="https://base.blockscout.com/api"
SWAP="0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
tests=[
  ("topic_only_small",{"module":"logs","action":"getLogs","fromBlock":"36640428","toBlock":"36640528","topic0":SWAP}),
  ("topic_only_1k",{"module":"logs","action":"getLogs","fromBlock":"36640428","toBlock":"36641428","topic0":SWAP}),
]
for name,p in tests:
    r=requests.get(BASE,params=p,timeout=90)
    print("TEST",name,"STATUS",r.status_code,"URL",r.url)
    print(r.text[:12000])
