from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data'/'raw'/'UserBehavior.csv'; ADS=ROOT/'output'/'ads'; DOCS=ROOT/'docs'
raw=pd.read_csv(RAW,header=None,names=['user_id','item_id','category_id','behavior_type','ts'])
raw['dt']=pd.to_datetime(raw['ts'],unit='s',utc=True).dt.strftime('%Y-%m-%d')
d=raw[raw['dt'].between('2017-11-25','2017-12-03')].dropna(subset=['user_id','item_id']).drop_duplicates(['user_id','item_id','behavior_type','ts']).copy()
d['user_id']=d['user_id'].astype('int64')
active=d[['user_id','dt']].drop_duplicates()
# independent pandas calculation
p_dau=active.groupby('dt',as_index=False).agg(dau=('user_id','nunique')).sort_values('dt')
next_uv=[]
for dt in p_dau['dt']:
 today=set(active.loc[active.dt==dt,'user_id']); nxt=(pd.Timestamp(dt)+pd.Timedelta(days=1)).strftime('%Y-%m-%d'); tomorrow=set(active.loc[active.dt==nxt,'user_id']); next_uv.append(len(today & tomorrow))
p_ret=p_dau.copy(); p_ret['next_day_uv']=next_uv; p_ret['retention_1d']=p_ret['next_day_uv']/p_ret['dau']
p_fun=(d.pivot_table(index='dt',columns='behavior_type',values='user_id',aggfunc=pd.Series.nunique,fill_value=0).reset_index())
for c in ['pv','cart','fav','buy']:
 if c not in p_fun: p_fun[c]=0
p_fun=p_fun.rename(columns={'pv':'pv_uv','cart':'cart_uv','fav':'fav_uv','buy':'buy_uv'}).sort_values('dt')
# load Spark outputs
rd=lambda n: pd.read_csv((ADS/n/'data.csv') if (ADS/n/'data.csv').exists() else next((ADS/n).glob('part-*.csv')))
s_dau=rd('ads_dau_daily').sort_values('dt'); s_ret=rd('ads_retention_daily').sort_values('dt'); s_fun=rd('ads_funnel_daily').sort_values('dt')
checks=[]
checks.append(('DAU',p_dau[['dt','dau']].reset_index(drop=True).equals(s_dau[['dt','dau']].reset_index(drop=True))))
checks.append(('次日留存分子',p_ret[['dt','next_day_uv']].reset_index(drop=True).equals(s_ret[['dt','next_day_uv']].reset_index(drop=True))))
checks.append(('漏斗UV',p_fun[['dt','pv_uv','cart_uv','fav_uv','buy_uv']].reset_index(drop=True).equals(s_fun[['dt','pv_uv','cart_uv','fav_uv','buy_uv']].reset_index(drop=True))))
result='PASS' if all(x[1] for x in checks) else 'FAIL'
DOCS.mkdir(exist_ok=True); lines=['# Pandas 与 Spark 交叉验证','','独立使用 Pandas 对清洗后的原始 CSV 重新计算 DAU、次日留存分子和漏斗 UV，再与 Spark ADS 结果逐行比较。','', '| 校验项 | 结果 |','|---|---|']
lines += [f'| {name} | {"一致" if ok else "不一致"} |' for name,ok in checks]; lines += ['',f'总体结果：**{result}**']
(DOCS/'cross_validation.md').write_text('\n'.join(lines),encoding='utf-8')
print({'checks':checks,'result':result})
if result!='PASS': raise SystemExit(1)

