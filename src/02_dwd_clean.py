import time, json
from pathlib import Path
from utils import build_spark, DATA, DOCS, START_DATE, END_DATE
from pyspark.sql import functions as F

spark=build_spark('userbehavior-dwd-clean', 400); t=time.perf_counter()
try:
    ods=spark.read.parquet(str(DATA/'ods'))
    ods_rows=ods.count()
    null_rates={c:round(ods.filter(F.col(c).isNull()).count()/ods_rows,8) if ods_rows else 0 for c in ['user_id','item_id','category_id','behavior_type','ts']}
    valid=ods.filter(F.col('dt').between(START_DATE,END_DATE)); valid_rows=valid.count(); time_invalid=ods_rows-valid_rows
    nonnull=valid.filter(F.col('user_id').isNotNull() & F.col('item_id').isNotNull()); null_filtered=valid_rows-nonnull.count()
    before_dedup=nonnull.count()
    key=['user_id','item_id','behavior_type','ts']
    dwd=(nonnull.dropDuplicates(key).withColumn('is_pv',F.when(F.col('behavior_type')=='pv',1).otherwise(0).cast('byte')).withColumn('is_cart',F.when(F.col('behavior_type')=='cart',1).otherwise(0).cast('byte')).withColumn('is_fav',F.when(F.col('behavior_type')=='fav',1).otherwise(0).cast('byte')).withColumn('is_buy',F.when(F.col('behavior_type')=='buy',1).otherwise(0).cast('byte')))
    dedup_filtered=before_dedup-dwd.count(); dwd_rows=dwd.count(); duplicate_keys=dwd.groupBy(key).count().filter('count>1').count()
    dwd.write.mode('overwrite').partitionBy('dt').parquet(str(DATA/'dwd'))
    q={'ods_rows':ods_rows,'dwd_rows':dwd_rows,'time_invalid_rows':time_invalid,'null_rows':null_filtered,'duplicate_rows':dedup_filtered,'filtered_rows':ods_rows-dwd_rows,'filter_rate':round((ods_rows-dwd_rows)/ods_rows,8) if ods_rows else 0,'null_rates':null_rates,'dwd_duplicate_keys':duplicate_keys,'elapsed_seconds':round(time.perf_counter()-t,3)}
    DOCS.mkdir(exist_ok=True); (DOCS/'data_quality.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
    null_md='\n'.join(f'| {c} | {null_rates[c]:.2%} |' for c in null_rates)
    md=f'''# 数据质量报告\n\n本报告基于当前 `data/raw/UserBehavior.csv` 运行生成。\n\n| 指标 | 数值 |\n|---|---:|\n| ODS 总行数 | {ods_rows:,} |\n| DWD 有效行数 | {dwd_rows:,} |\n| 时间越界过滤 | {time_invalid:,} |\n| 空值过滤 | {null_filtered:,} |\n| 重复行为过滤 | {dedup_filtered:,} |\n| 总过滤行数 | {ods_rows-dwd_rows:,} |\n| 过滤率 | {q["filter_rate"]:.2%} |\n| DWD 重复主键数 | {duplicate_keys:,} |\n\n## ODS 字段空值率\n\n| 字段 | 空值率 |\n|---|---:|\n{null_md}\n\n主键校验：`(user_id, item_id, behavior_type, ts)` 在 DWD 层执行去重，并复查重复主键数。\n'''
    (DOCS/'data_quality.md').write_text(md,encoding='utf-8'); print(q)
finally: spark.stop()
