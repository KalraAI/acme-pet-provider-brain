#!/usr/bin/env python3
"""Verify source bytes, insight payload hashes, chain adjacency, and tip."""
import json,hashlib,pathlib,sys
root=pathlib.Path(__file__).parent
ledger=json.loads((root/'docs'/'audit-ledger.json').read_text())
results=json.loads((root/'docs'/'results.json').read_text())
claims=root/'data'/'claims.csv'
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
payloads={'claims.csv':{'sha256':hashlib.sha256(claims.read_bytes()).hexdigest(),'rows':results['summary']['claims'],'fixture':'synthetic-v1'}}
payloads.update({x['insight_id']:x for x in results['provider_insights']})
prev=ledger['genesis'];ok=True;bad=None
for i,e in enumerate(ledger['entries'],1):
 payload=payloads.get(e['id'])
 if payload is None or hashlib.sha256(canon(payload)).hexdigest()!=e['payload_hash']:
  ok=False;bad=i;break
 body={k:e[k] for k in ('seq','kind','id','payload_hash')}
 expect=hashlib.sha256((prev+canon(body).decode()).encode()).hexdigest()
 if e['seq']!=i or e['prev_hash']!=prev or e['chain_hash']!=expect:
  ok=False;bad=i;break
 prev=e['chain_hash']
ok=ok and prev==ledger['tip'] and ledger.get('audit_valid') is True
print(json.dumps({'audit_valid':ok,'entries':len(ledger['entries']),'break_at':bad,'tip':prev,'source_and_payloads_verified':ok}))
sys.exit(0 if ok else 1)
