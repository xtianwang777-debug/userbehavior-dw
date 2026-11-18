# 独立计算与 Spark 交叉验证

使用 Python 标准库 CSV 独立计算清洗后原始 CSV 的 DAU、次日留存分子和漏斗 UV，再与 Spark ADS 结果逐行比较。当前环境的 Pandas 二进制包存在 Windows 访问冲突，因此校验实现不依赖 Pandas。

| 校验项 | 结果 |
|---|---|
| DAU | 一致 |
| 次日留存分子 | 一致 |
| 漏斗UV | 一致 |

总体结果：**PASS**