import argparse, csv, random, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--rows',type=int,default=120000); p.add_argument('--output',default='data/raw/UserBehavior.csv'); a=p.parse_args()
r=random.Random(20261118); start=datetime(2017,11,25,tzinfo=timezone.utc); users=range(1001,6001); items=range(10001,30001); cats=range(1,501); behaviors=['pv','cart','fav','buy']; weights=[0.88,0.05,0.05,0.02]
Path(a.output).parent.mkdir(parents=True,exist_ok=True); t=time.perf_counter()
with open(a.output,'w',newline='',encoding='utf-8') as f:
 w=csv.writer(f)
 for i in range(a.rows):
  day=r.randrange(9); sec=r.randrange(86400); ts=int((start+timedelta(days=day,seconds=sec)).timestamp())
  if i%5000==0: ts=int((start-timedelta(days=2)).timestamp())
  user=None if i%7000==0 else r.choice(tuple(users)); item=None if i%11000==0 else r.choice(tuple(items)); cat=r.choice(tuple(cats)); b=r.choices(behaviors,weights)[0]
  row=[user,item,cat,b,ts]; w.writerow(row)
  if i and i%17000==0: w.writerow(row)
print({'rows_requested':a.rows,'output':a.output,'elapsed_seconds':round(time.perf_counter()-t,3)})

