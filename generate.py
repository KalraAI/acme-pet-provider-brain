#!/usr/bin/env python3
"""Generate a deterministic, fully synthetic veterinary claims fixture."""
import csv, random, pathlib, datetime
R=random.Random(20260914); OUT=pathlib.Path(__file__).parent/'data'; OUT.mkdir(exist_ok=True)
conditions=[('otitis','consult',145),('otitis','cytology',95),('dermatitis','consult',155),('dermatitis','medication',125),('gastroenteritis','consult',165),('gastroenteritis','pathology',185)]
regions=[('metro',1.00),('regional',1.06),('rural',1.13)]; types=[('gp',1.00),('emergency',1.42),('specialty',1.66)]
providers=[]
for i in range(36):
 region,rm=regions[i%3]; typ,tm=types[(i//3)%3]
 providers.append((f'VET-{i+1:03}',region,typ,rm*tm))
rows=[]; start=datetime.date(2025,1,1)
for month in range(12):
 for pidx,(pid,region,typ,mult) in enumerate(providers):
  volume=14+R.randrange(14)+(5 if typ=='gp' else 0)
  for j in range(volume):
   condition,treatment,base=conditions[R.randrange(len(conditions))]
   age=1+R.randrange(14); complexity=R.choice([0,0,0,1,1,2]); repeat=R.random()<.16
   legitimate=mult*(1+.12*complexity)*(1+.04*max(0,age-8))
   price=base*legitimate*(1+.004*month)*R.uniform(.88,1.12)
   units=1+(R.random()<(.18+.10*complexity))
   referral=typ!='gp' or (R.random()<(.07+.07*complexity))
   # planted synthetic signals: price, intensity, and referral; never labelled fraud.
   if pid=='VET-007' and treatment in ('consult','cytology'): price*=1.38
   if pid=='VET-019' and condition=='dermatitis': units+=1
   if pid=='VET-028' and typ=='gp': referral=R.random()<.58
   claim=f'C{month:02}{pidx:02}{j:03}'
   note=f'{condition}; age {age}; complexity {complexity}; '+('repeat visit; ' if repeat else '')+('referral noted' if referral else 'managed in setting')
   rows.append({'claim_id':claim,'pet_id':f'P{R.randrange(2400):04}','provider_id':pid,'month':f'2025-{month+1:02}','region':region,'provider_type':typ,'species':R.choice(['dog','dog','cat']),'breed_group':R.choice(['small','medium','large','mixed']),'age':age,'complexity':complexity,'condition':condition,'treatment':treatment,'units':units,'unit_price':f'{price:.2f}','paid':f'{price*units:.2f}','referred':str(referral).lower(),'vet_note':note,'source':'synthetic-v1'})
with open(OUT/'claims.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(f'wrote {len(rows)} synthetic claims across {len(providers)} providers')
