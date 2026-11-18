# 淘宝用户行为离线数仓

这是一个可在本地 `local[*]` 模式运行的 PySpark 离线数仓项目，按 ODS → DWD → DWS → ADS 四层组织淘宝用户行为数据。项目代码同时提供一个可重复生成的小型演示数据集，便于没有 1 亿条原始数据时先跑通全链路。

## 项目结构

```text
userbehavior-dw/
├── src/
│   ├── 00_generate_demo.py  # 生成带脏数据的演示 CSV
│   ├── 01_ods_load.py       # 原始 CSV -> ODS Parquet
│   ├── 02_dwd_clean.py      # 清洗、去重、质量统计
│   ├── 03_dws_agg.py        # 用户/商品/类目三张汇总表
│   ├── 04_ads_metrics.py    # 五类业务指标
│   ├── 05_cross_validate.py # Pandas 与 Spark 交叉验证
│   ├── 06_charts.py         # 生成 4 张图
│   ├── 07_validate.py       # ADS 结果检查
│   ├── 08_tuning_benchmark.py # shuffle/broadcast 实验
│   └── utils.py
├── data/raw/                # 原始 CSV（已 gitignore）
├── data/ods|dwd|dws/        # Parquet 中间层（已 gitignore）
├── output/ads/              # 指标 CSV
├── output/charts/           # 可视化输出
├── docs/                    # 架构、口径、质量与调优文档
└── requirements.txt
```

## 环境

- Python 3.9+
- Java 8/11/17
- PySpark 3.5+
- PyArrow、Matplotlib；交叉验证脚本使用 Python 标准库 CSV

Windows 本地运行建议先设置 `JAVA_HOME`；Linux 服务器可直接使用系统 Java。若使用真实数据，下载阿里天池 UserBehavior 数据集并放到 `data/raw/UserBehavior.csv`，文件不带表头，字段为 `user_id,item_id,category_id,behavior_type,timestamp`。

## 从零运行演示数据

```powershell
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1
```

Windows 运行前请安装 Java 8/11/17 并设置 `JAVA_HOME`；Linux 服务器直接使用系统 Java 和 `python3` 即可。

## 业务指标

- DAU：当日去重活跃用户数。
- 次日留存：当日活跃用户中次日仍活跃的用户数 / 当日活跃用户数。
- 7 日留存：当日活跃用户中未来 1-7 日任意一天仍活跃的用户数 / 当日活跃用户数。
- 漏斗：PV、加购、收藏、购买的去重用户数及相邻转化率。
- 类目 Top10：按当日购买次数降序，输出购买人数和排名。
- 复购率：窗口内购买用户中，至少在两个不同日期购买的用户占比。

详细口径见 `docs/metric_definitions.md`，质量统计见 `docs/data_quality.md`；交叉验证见 `docs/cross_validation.md`，调优数据见 `docs/tuning_report.md`。

## 真实数据运行注意

演示数据只用于验证程序逻辑，不代表淘宝全量数据结论。将真实 CSV 放入 `data/raw/UserBehavior.csv` 后重新执行四个脚本，简历中的数据量、过滤率、耗时和指标必须使用真实运行结果填写。




