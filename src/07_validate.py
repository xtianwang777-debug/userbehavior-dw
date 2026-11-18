import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADS = ROOT / 'output' / 'ads'


def read(name):
    path = ADS / name / 'data.csv'
    if not path.exists():
        path = sorted((ADS / name).glob('part-*.csv'))[0]
    with path.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


names = ['ads_dau_daily', 'ads_retention_daily', 'ads_funnel_daily', 'ads_category_top10', 'ads_repurchase']
checks = []
for name in names:
    path = ADS / name
    checks.append((name, path.exists() and ((path / 'data.csv').exists() or any(path.glob('part-*.csv')))))
if not all(ok for _name, ok in checks):
    raise SystemExit('missing ADS output: ' + str(checks))

dau = read('ads_dau_daily')
funnel = read('ads_funnel_daily')
retention = read('ads_retention_daily')
top = read('ads_category_top10')
rep = read('ads_repurchase')

for row in dau:
    assert int(row['dau']) >= 0
for row in funnel:
    assert all(int(row[key]) >= 0 for key in ['pv_uv', 'cart_uv', 'fav_uv', 'buy_uv'])
for row in retention:
    assert 0 <= float(row['retention_1d']) <= 1
    assert 0 <= float(row['retention_7d']) <= 1
assert top and len(rep) == 1
print({'ads_tables': len(checks), 'dau_days': len(dau), 'top10_rows': len(top), 'validation': 'PASS'})
