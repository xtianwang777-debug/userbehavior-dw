from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; ADS=ROOT/'output'/'ads'
def read(name): return pd.read_csv((ADS/name/'data.csv') if (ADS/name/'data.csv').exists() else next((ADS/name).glob('part-*.csv')))
checks=[]
for name,key in [('ads_dau_daily','dt'),('ads_retention_daily','dt'),('ads_funnel_daily','dt'),('ads_category_top10','dt'),('ads_repurchase','window_start')]:
 p=ADS/name; ok=p.exists() and ((p/'data.csv').exists() or any(p.glob('part-*.csv'))); checks.append((name,ok))
if not all(x[1] for x in checks): raise SystemExit('missing ADS output: '+str(checks))
dau=read('ads_dau_daily'); funnel=read('ads_funnel_daily'); retention=read('ads_retention_daily'); top=read('ads_category_top10'); rep=read('ads_repurchase')
assert (dau.dau>=0).all() and (funnel[['pv_uv','cart_uv','fav_uv','buy_uv']]>=0).all().all()
assert retention.retention_1d.between(0,1).all() and retention.retention_7d.between(0,1).all()
assert len(top)>0 and len(rep)==1
print({'ads_tables':len(checks),'dau_days':len(dau),'top10_rows':len(top),'validation':'PASS'})


