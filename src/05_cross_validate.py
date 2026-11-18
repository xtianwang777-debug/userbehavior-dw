import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw' / 'UserBehavior.csv'
ADS = ROOT / 'output' / 'ads'
DOCS = ROOT / 'docs'
START_DATE = '2017-11-25'
END_DATE = '2017-12-03'


def read_clean_rows():
    rows = []
    seen = set()
    with RAW.open('r', encoding='utf-8', newline='') as fh:
        for values in csv.reader(fh):
            if len(values) < 5:
                continue
            try:
                user_id = int(values[0]) if values[0] else None
                item_id = int(values[1]) if values[1] else None
                category_id = int(values[2]) if values[2] else None
                ts = int(values[4]) if values[4] else None
                dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')
            except (TypeError, ValueError, OverflowError, OSError):
                continue
            if not (START_DATE <= dt <= END_DATE) or user_id is None or item_id is None:
                continue
            key = (user_id, item_id, values[3], ts)
            if key in seen:
                continue
            seen.add(key)
            rows.append((user_id, item_id, category_id, values[3], ts, dt))
    return rows


def read_ads(name):
    path = ADS / name / 'data.csv'
    if not path.exists():
        path = sorted((ADS / name).glob('part-*.csv'))[0]
    with path.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


rows = read_clean_rows()
active = defaultdict(set)
funnel = defaultdict(lambda: defaultdict(set))
for user_id, _item_id, _category_id, behavior, _ts, dt in rows:
    active[dt].add(user_id)
    funnel[dt][behavior].add(user_id)

dates = sorted(active)
p_dau = [{'dt': dt, 'dau': len(active[dt])} for dt in dates]
p_ret = []
for row in p_dau:
    next_date = (datetime.strptime(row['dt'], '%Y-%m-%d').date()).fromordinal(
        datetime.strptime(row['dt'], '%Y-%m-%d').date().toordinal() + 1
    ).strftime('%Y-%m-%d')
    p_ret.append({'dt': row['dt'], 'next_day_uv': len(active[row['dt']] & active.get(next_date, set()))})
p_fun = [
    {'dt': dt, **{f'{behavior}_uv': len(funnel[dt].get(behavior, set())) for behavior in ['pv', 'cart', 'fav', 'buy']}}
    for dt in dates
]

s_dau = read_ads('ads_dau_daily')
s_ret = read_ads('ads_retention_daily')
s_fun = read_ads('ads_funnel_daily')


def norm_int(rows, fields):
    return [{field: (int(row[field]) if field != 'dt' else row[field]) for field in fields} for row in rows]


checks = [
    ('DAU', norm_int(p_dau, ['dt', 'dau']) == norm_int(s_dau, ['dt', 'dau'])),
    ('次日留存分子', norm_int(p_ret, ['dt', 'next_day_uv']) == norm_int(s_ret, ['dt', 'next_day_uv'])),
    ('漏斗UV', norm_int(p_fun, ['dt', 'pv_uv', 'cart_uv', 'fav_uv', 'buy_uv']) == norm_int(s_fun, ['dt', 'pv_uv', 'cart_uv', 'fav_uv', 'buy_uv'])),
]
result = 'PASS' if all(ok for _name, ok in checks) else 'FAIL'
DOCS.mkdir(exist_ok=True)
lines = [
    '# 独立计算与 Spark 交叉验证',
    '',
    '使用 Python 标准库 CSV 独立计算清洗后原始 CSV 的 DAU、次日留存分子和漏斗 UV，再与 Spark ADS 结果逐行比较。当前环境的 Pandas 二进制包存在 Windows 访问冲突，因此校验实现不依赖 Pandas。',
    '',
    '| 校验项 | 结果 |',
    '|---|---|',
]
lines += [f'| {name} | {"一致" if ok else "不一致"} |' for name, ok in checks]
lines += ['', f'总体结果：**{result}**']
(DOCS / 'cross_validation.md').write_text('\n'.join(lines), encoding='utf-8')
print({'checks': checks, 'result': result})
if result != 'PASS':
    raise SystemExit(1)
