from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; ADS=ROOT/'output'/'ads'; OUT=ROOT/'output'/'charts'; OUT.mkdir(parents=True,exist_ok=True)
def read(name): return pd.read_csv((ADS/name/'data.csv') if (ADS/name/'data.csv').exists() else next((ADS/name).glob('part-*.csv')))
plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']; plt.rcParams['axes.unicode_minus']=False
x=read('ads_dau_daily'); plt.figure(figsize=(8,4)); plt.plot(x['dt'],x['dau'],marker='o'); plt.xticks(rotation=30); plt.title('DAU趋势'); plt.tight_layout(); plt.savefig(OUT/'dau_trend.png',dpi=160); plt.close()
x=read('ads_retention_daily'); plt.figure(figsize=(8,4)); plt.plot(x['dt'],x['retention_1d'],marker='o',label='次日留存'); plt.plot(x['dt'],x['retention_7d'],marker='o',label='7日区间留存'); plt.legend(); plt.xticks(rotation=30); plt.title('留存趋势'); plt.tight_layout(); plt.savefig(OUT/'retention.png',dpi=160); plt.close()
x=read('ads_funnel_daily'); last=x.iloc[-1]; labels=['PV UV','Cart UV','Fav UV','Buy UV']; vals=[last['pv_uv'],last['cart_uv'],last['fav_uv'],last['buy_uv']]; plt.figure(figsize=(7,4)); plt.bar(labels,vals); plt.title(f"转化漏斗（{last['dt']}）"); plt.tight_layout(); plt.savefig(OUT/'funnel.png',dpi=160); plt.close()
x=read('ads_category_top10'); x=x[x['dt']==x['dt'].min()].sort_values('buy_cnt'); plt.figure(figsize=(7,5)); plt.barh(x['category_id'].astype(str),x['buy_cnt']); plt.title('首日购买类目 Top10'); plt.tight_layout(); plt.savefig(OUT/'category_top10.png',dpi=160); plt.close()
print('charts:', ', '.join(p.name for p in OUT.glob('*.png')))

