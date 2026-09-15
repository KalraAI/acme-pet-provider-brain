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
if not ok: sys.exit(1)

# Demo 2 linked health + claims integrity
DOCS=root/'docs'
health=json.loads((DOCS/'scenario1-health-episodes.json').read_text())
claims=json.loads((DOCS/'scenario1-claims.json').read_text())
linked=json.loads((DOCS/'scenario1-linked-results.json').read_text())
linked_ledger=json.loads((DOCS/'scenario1-linked-audit.json').read_text())
health_keys=[(x['pet_id'],x['health_episode_id']) for x in health]
claim_keys=[(x['pet_id'],x['health_episode_id']) for x in claims]
assert len(health)==len(claims)==linked['summary']['linked_pairs']==9283
assert len(set(health_keys))==len(health_keys) and len(set(claim_keys))==len(claim_keys)
assert set(health_keys)==set(claim_keys)
assert linked['summary']['match_rate_pct']==100.0
assert linked['summary']['unmatched_health_episodes']==0
assert linked['summary']['unmatched_claims']==0
assert linked['summary']['duplicate_link_keys']==0
prev=linked_ledger['genesis']
for e in linked_ledger['entries']:
 body=json.dumps({'id':e['id'],'kind':e['kind'],'payload_hash':e['payload_hash'],'seq':e['seq']},sort_keys=True,separators=(',',':'))
 assert e['prev_hash']==prev
 assert e['chain_hash']==hashlib.sha256((prev+body).encode()).hexdigest()
 prev=e['chain_hash']
assert prev==linked_ledger['tip']
print(json.dumps({'linked_demo':'verified','health_episodes':len(health),'claims':len(claims),'linked_pairs':linked['summary']['linked_pairs'],'linked_pets':linked['summary']['linked_pets'],'audit_tip':prev}))

sys.exit(0)
