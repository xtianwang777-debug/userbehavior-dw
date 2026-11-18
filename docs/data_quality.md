# 数据质量报告

本报告基于当前 `data/raw/UserBehavior.csv` 运行生成。

| 指标 | 数值 |
|---|---:|
| ODS 总行数 | 120,007 |
| DWD 有效行数 | 119,955 |
| 时间越界过滤 | 25 |
| 空值过滤 | 22 |
| 重复行为过滤 | 5 |
| 总过滤行数 | 52 |
| 过滤率 | 0.04% |
| DWD 重复主键数 | 0 |

## ODS 字段空值率

| 字段 | 空值率 |
|---|---:|
| user_id | 0.02% |
| item_id | 0.01% |
| category_id | 0.00% |
| behavior_type | 0.00% |
| ts | 0.00% |

主键校验：`(user_id, item_id, behavior_type, ts)` 在 DWD 层执行去重，并复查重复主键数。
