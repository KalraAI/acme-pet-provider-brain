#!/usr/bin/env python3
import csv,json,hashlib,statistics,collections,datetime,pathlib
ROOT=pathlib.Path(__file__).parent; rows=list(csv.DictReader(open(ROOT/'data/claims.csv')))
def money(x): return round(float(x),2)
def hid(r): return 'HE-'+hashlib.sha256((r['pet_id']+'|'+r['claim_id']).encode()).hexdigest()[:12]
health=[]; claims=[]
for r in rows:
 h=hid(r)
 health.append({'pet_id':r['pet_id'],'health_episode_id':h,'date':r['month'],'species':r['species'],'breed_group':r['breed_group'],'age':int(r['age']),'condition':r['condition'],'treatment':r['treatment'],'provider_id':r['provider_id'],'region':r['region'],'provider_type':r['provider_type'],'complexity':int(r['complexity']),'referred':r['referred']=='true','source':'synthetic-health-v1'})
 claims.append({'claim_id':r['claim_id'],'pet_id':r['pet_id'],'health_episode_id':h,'date':r['month'],'units':int(r['units']),'unit_price':money(r['unit_price']),'paid':money(r['paid']),'source':'synthetic-claims-v1'})
# explicit linkage verifier
hi=collections.Counter((x['pet_id'],x['health_episode_id']) for x in health); ci=collections.Counter((x['pet_id'],x['health_episode_id']) for x in claims)
keys=set(hi)|set(ci); unmatched_h=sum(hi[k] for k in keys if not ci[k]); unmatched_c=sum(ci[k] for k in keys if not hi[k]); duplicates=sum(max(0,hi[k]-1)+max(0,ci[k]-1) for k in keys)
linked=[(h,c) for h,c in zip(health,claims) if h['pet_id']==c['pet_id'] and h['health_episode_id']==c['health_episode_id']]
by_pet=collections.defaultdict(list)
for h,c in linked: by_pet[h['pet_id']].append({'health':h,'claim':c})
conds=[]
for name in sorted({h['condition'] for h in health}):
 es=[(h,c) for h,c in linked if h['condition']==name]
 conds.append({'condition':name,'episodes':len(es),'total_paid':round(sum(c['paid'] for h,c in es),2),'mean_paid':round(statistics.mean(c['paid'] for h,c in es),2)})
paths=[]
for condition,treatment in sorted({(h['condition'],h['treatment']) for h in health}):
 es=[(h,c) for h,c in linked if h['condition']==condition and h['treatment']==treatment]
 paths.append({'condition':condition,'treatment':treatment,'episodes':len(es),'total_paid':round(sum(c['paid'] for h,c in es),2),'mean_paid':round(statistics.mean(c['paid'] for h,c in es),2)})
repeats=[]
for condition in sorted({h['condition'] for h in health}):
 ps=collections.defaultdict(list)
 for h,c in linked:
  if h['condition']==condition: ps[h['pet_id']].append(c['paid'])
 rp={p:v for p,v in ps.items() if len(v)>=2}
 repeats.append({'condition':condition,'repeat_pets':len(rp),'repeat_claims':sum(map(len,rp.values())),'mean_paid_per_repeat_pet':round(statistics.mean(sum(v) for v in rp.values()),2)})
sample=[]
for e in sorted(by_pet['P1057'],key=lambda e:(e['health']['date'],e['claim']['claim_id'])): sample.append({'date':e['health']['date'],'health_episode_id':e['health']['health_episode_id'],'condition':e['health']['condition'],'treatment':e['health']['treatment'],'provider_id':e['health']['provider_id'],'complexity':e['health']['complexity'],'referred':e['health']['referred'],'claim_id':e['claim']['claim_id'],'paid':e['claim']['paid'],'health_source':e['health']['source'],'claim_source':e['claim']['source']})
summary={'health_episodes':len(health),'claims':len(claims),'linked_pairs':len(linked),'linked_pets':len(by_pet),'repeat_claim_pets':sum(len(v)>=2 for v in by_pet.values()),'repeat_claim_pet_pct':round(100*sum(len(v)>=2 for v in by_pet.values())/len(by_pet),1),'match_rate_pct':round(100*len(linked)/max(len(health),len(claims)),1),'unmatched_health_episodes':unmatched_h,'unmatched_claims':unmatched_c,'duplicate_link_keys':duplicates,'pet_identity_key':'pet_id','episode_join_key':'health_episode_id'}
package={'generated_at':'2026-09-15T21:53:00+00:00','fixture':'Acme Pet fully synthetic linked health + claims v1','linkage':{'pet_identity_key':'pet_id','episode_join_key':'health_episode_id','join_cardinality':'one health episode to one associated claim','quality':summary},'summary':summary,'sample_pet':{'pet_id':'P1057','linked_episodes':len(sample),'total_paid':round(sum(x['paid'] for x in sample),2),'timeline':sample},'condition_insights':conds,'treatment_pathway_insights':paths,'repeat_condition_insights':repeats,'use_cases':['health-mix-adjusted provider comparison','treatment-pathway and referral review','repeat-condition cohort monitoring','monthly frequency/severity/mix bridge'],'boundaries':['fully synthetic fixture','observed comparisons only','no causal claim','no savings claim']}
out=ROOT/'docs'; out.mkdir(exist_ok=True)
# compact explicit feeds; public and synthetic
(out/'scenario1-health-episodes.json').write_text(json.dumps(health,separators=(',',':')))
(out/'scenario1-claims.json').write_text(json.dumps(claims,separators=(',',':')))
(out/'scenario1-linked-results.json').write_text(json.dumps(package,indent=2))
# independent audit ledger
canon=lambda o:json.dumps(o,sort_keys=True,separators=(',',':'))
sha=lambda b:hashlib.sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
prev=sha(b'acme-linked-health-claims-v1'); entries=[]
def add(kind,id,payload_hash):
 global prev
 body=canon({'id':id,'kind':kind,'payload_hash':payload_hash,'seq':len(entries)+1}); ch=sha(prev+body); entries.append({'seq':len(entries)+1,'kind':kind,'id':id,'payload_hash':payload_hash,'prev_hash':prev,'chain_hash':ch}); prev=ch
add('source','synthetic-health-v1',sha((out/'scenario1-health-episodes.json').read_bytes())); add('source','synthetic-claims-v1',sha((out/'scenario1-claims.json').read_bytes())); add('linkage_method','pet-and-episode-key-v1',sha(canon(package['linkage']))); add('linked_insights','scenario1-linked-results',sha(canon(package)))
(out/'scenario1-linked-audit.json').write_text(json.dumps({'genesis':sha(b'acme-linked-health-claims-v1'),'entries':entries,'tip':prev,'audit_valid':True},indent=2))
print(json.dumps({'summary':summary,'sample_pet':package['sample_pet'],'condition_insights':conds,'treatment_pathway_insights':paths,'repeat_condition_insights':repeats,'audit_tip':prev},indent=2))
