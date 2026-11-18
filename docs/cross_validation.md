# Pandas 与 Spark 交叉验证

独立使用 Pandas 对清洗后的原始 CSV 重新计算 DAU、次日留存分子和漏斗 UV，再与 Spark ADS 结果逐行比较。

| 校验项 | 结果 |
|---|---|
| DAU | 一致 |
| 次日留存分子 | 一致 |
| 漏斗UV | 一致 |

总体结果：**PASS**