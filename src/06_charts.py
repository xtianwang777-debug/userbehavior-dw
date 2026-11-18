import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ADS = ROOT / 'output' / 'ads'
OUT = ROOT / 'output' / 'charts'
OUT.mkdir(parents=True, exist_ok=True)


def read(name):
    path = ADS / name / 'data.csv'
    if not path.exists():
        path = sorted((ADS / name).glob('part-*.csv'))[0]
    with path.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def number(row, key):
    return float(row[key])


plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

x = read('ads_dau_daily')
plt.figure(figsize=(8, 4))
plt.plot([r['dt'] for r in x], [number(r, 'dau') for r in x], marker='o')
plt.xticks(rotation=30)
plt.title('DAU趋势')
plt.tight_layout()
plt.savefig(OUT / 'dau_trend.png', dpi=160)
plt.close()

x = read('ads_retention_daily')
plt.figure(figsize=(8, 4))
plt.plot([r['dt'] for r in x], [number(r, 'retention_1d') for r in x], marker='o', label='次日留存')
plt.plot([r['dt'] for r in x], [number(r, 'retention_7d') for r in x], marker='o', label='7日区间留存')
plt.legend()
plt.xticks(rotation=30)
plt.title('留存趋势')
plt.tight_layout()
plt.savefig(OUT / 'retention.png', dpi=160)
plt.close()

x = read('ads_funnel_daily')
last = x[-1]
labels = ['PV UV', 'Cart UV', 'Fav UV', 'Buy UV']
vals = [number(last, key) for key in ['pv_uv', 'cart_uv', 'fav_uv', 'buy_uv']]
plt.figure(figsize=(7, 4))
plt.bar(labels, vals)
plt.title(f"转化漏斗（{last['dt']}）")
plt.tight_layout()
plt.savefig(OUT / 'funnel.png', dpi=160)
plt.close()

x = read('ads_category_top10')
first_dt = min(r['dt'] for r in x)
x = sorted((r for r in x if r['dt'] == first_dt), key=lambda r: number(r, 'buy_cnt'))
plt.figure(figsize=(7, 5))
plt.barh([r['category_id'] for r in x], [number(r, 'buy_cnt') for r in x])
plt.title('首日购买类目 Top10')
plt.tight_layout()
plt.savefig(OUT / 'category_top10.png', dpi=160)
plt.close()
print('charts:', ', '.join(p.name for p in OUT.glob('*.png')))
