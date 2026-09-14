#!/usr/bin/env python3
"""Explainable provider benchmarking with source lineage and fail-safe thresholds."""
import csv,json,hashlib,statistics,pathlib,collections,datetime
ROOT=pathlib.Path(__file__).parent; DATA=ROOT/'data'; OUT=ROOT/'docs'; OUT.mkdir(exist_ok=True)
rows=list(csv.DictReader(open(DATA/'claims.csv')))
for r in rows:
 for k in ('age','complexity','units'):r[k]=int(r[k])
 for k in ('unit_price','paid'):r[k]=float(r[k])
 r['referred']=r['referred']=='true'
# legitimate-adjustment cells: condition+treatment+region+provider type+complexity. Breed/age remain drill-down slices.
def cohort(r): return (r['condition'],r['treatment'],r['region'],r['provider_type'],r['complexity'])
cells=collections.defaultdict(list)
for r in rows: cells[cohort(r)].append(r)
cellstats={k:{'n':len(v),'median_price':statistics.median(x['unit_price'] for x in v),'median_units':statistics.median(x['units'] for x in v),'referral_rate':sum(x['referred'] for x in v)/len(v)} for k,v in cells.items()}
prov=collections.defaultdict(list)
for r in rows:prov[r['provider_id']].append(r)
insights=[]
for pid,rs in sorted(prov.items()):
 comps=[]
 for r in rs:
  s=cellstats[cohort(r)]
  comps.append({'claim_id':r['claim_id'],'condition':r['condition'],'treatment':r['treatment'],'observed_price':r['unit_price'],'expected_price':s['median_price'],'price_ratio':r['unit_price']/s['median_price'],'units':r['units'],'expected_units':s['median_units'],'referred':r['referred'],'expected_referral_rate':s['referral_rate'],'cohort':{'condition':r['condition'],'treatment':r['treatment'],'region':r['region'],'provider_type':r['provider_type'],'complexity':r['complexity'],'n':s['n']}})
 n=len(comps); price=statistics.median(x['price_ratio'] for x in comps); unit_excess=sum(x['units']>x['expected_units'] for x in comps)/n; ref_rate=sum(x['referred'] for x in comps)/n; ref_exp=sum(x['expected_referral_rate'] for x in comps)/n
 reasons=[]
 if n>=120 and price>=1.18:reasons.append({'type':'price_variance','observed':round(price,3),'threshold':1.18,'basis':'median unit-price ratio after condition/treatment/region/provider-type/complexity adjustment'})
 if n>=120 and unit_excess>=.38:reasons.append({'type':'service_intensity_variance','observed':round(unit_excess,3),'threshold':.38,'basis':'share of claims above adjusted cohort median units'})
 if n>=120 and ref_rate-ref_exp>=.20:reasons.append({'type':'referral_variance','observed':round(ref_rate,3),'expected':round(ref_exp,3),'threshold_delta':.20,'basis':'referral-rate delta from adjusted cohorts'})
 quality='sufficient' if n>=120 else 'insufficient'
 insights.append({'insight_id':'INS-'+hashlib.sha256(pid.encode()).hexdigest()[:10],'provider_id':pid,'status':'candidate_review' if reasons else ('no_flag' if quality=='sufficient' else 'insufficient_evidence'),'not_fraud_label':True,'sample_size':n,'data_quality':quality,'reasons':reasons,'adjustments':['condition','treatment','region','provider_type','complexity'],'drilldown_claim_ids':[x['claim_id'] for x in comps if x['price_ratio']>=1.18 or x['units']>x['expected_units']][:20],'model_version':'provider-benchmark-v0.1','review':{'required':True,'state':'pending' if reasons else 'not_required','choices':['agree','clinically_justified','cohort_wrong','data_wrong','needs_more_evidence']}})
# monthly inflation decomposition: price, volume, mix shown as observations only.
months=sorted(set(r['month'] for r in rows)); monthly=[]
for mi,m in enumerate(months):
 x=[r for r in rows if r['month']==m]
 item={'month':m,'claims':len(x),'paid':round(sum(r['paid'] for r in x),2),'mean_paid':round(statistics.mean(r['paid'] for r in x),2),'mean_unit_price':round(statistics.mean(r['unit_price'] for r in x),2),'mean_units':round(statistics.mean(r['units'] for r in x),3)}
 if mi:
  prior=[r for r in rows if r['month']==months[mi-1]]; prior_total=sum(r['paid'] for r in prior); current_total=sum(r['paid'] for r in x)
  volume=(len(x)-len(prior))*(prior_total/len(prior))
  # Exact bridge: volume first; within-cell price/intensity on current mix;
  # residual is cohort mix/new-cell change. Cells are condition+treatment+provider type.
  key=lambda r:(r['condition'],r['treatment'],r['provider_type'])
  a=collections.defaultdict(list);b=collections.defaultdict(list)
  for r in prior:a[key(r)].append(r['paid'])
  for r in x:b[key(r)].append(r['paid'])
  price_intensity=sum(len(v)*(statistics.mean(v)-statistics.mean(a[k])) for k,v in b.items() if k in a)
  mix=current_total-prior_total-volume-price_intensity
  item['change_from_prior']={'total':round(current_total-prior_total,2),'volume':round(volume,2),'within_cohort_price_intensity':round(price_intensity,2),'cohort_mix_and_new_cells':round(mix,2),'identity_check':round(volume+price_intensity+mix,2),'not_causal':True}
 monthly.append(item)
package={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixture':'fully synthetic; no PetSure data','method':{'purpose':'decision support only','cohort':'condition+treatment+region+provider_type+complexity','minimum_provider_claims':120,'price_ratio_threshold':1.18,'service_intensity_threshold':.38,'referral_delta_threshold':.20},'summary':{'claims':len(rows),'providers':len(prov),'candidate_providers':sum(bool(x['reasons']) for x in insights)},'monthly':monthly,'provider_insights':insights}
(OUT/'results.json').write_text(json.dumps(package,indent=2))
# chain source and each insight. Review/actions will append later, never overwrite.
prev=hashlib.sha256(b'vet-provider-intelligence-v0').hexdigest(); ledger=[]
def add(kind,ident,payload):
 global prev
 h=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(); e={'seq':len(ledger)+1,'kind':kind,'id':ident,'payload_hash':h,'prev_hash':prev};e['chain_hash']=hashlib.sha256((prev+json.dumps({k:e[k] for k in ('seq','kind','id','payload_hash')},sort_keys=True,separators=(',',':'))).encode()).hexdigest();ledger.append(e);prev=e['chain_hash']
add('source','claims.csv',{'sha256':hashlib.sha256((DATA/'claims.csv').read_bytes()).hexdigest(),'rows':len(rows),'fixture':'synthetic-v1'})
for x in insights:add('provider_insight',x['insight_id'],x)
(OUT/'audit-ledger.json').write_text(json.dumps({'genesis':hashlib.sha256(b'vet-provider-intelligence-v0').hexdigest(),'entries':ledger,'tip':prev,'audit_valid':True},indent=2))
print(json.dumps(package['summary']))
