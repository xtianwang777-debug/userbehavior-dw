import json, time
from pathlib import Path
from utils import build_spark, DATA, DOCS
from pyspark.sql import functions as F

results={}
spark=build_spark('userbehavior-tuning',200)
try:
 d=spark.read.parquet(str(DATA/'dwd')).select('user_id','item_id','category_id','behavior_type','dt').cache(); d.count()
 for p in [200,400]:
  spark.conf.set('spark.sql.shuffle.partitions',str(p)); t=time.perf_counter(); rows=d.groupBy('dt','behavior_type').agg(F.countDistinct('user_id').alias('uv')).count(); results[f'shuffle_{p}']={'shuffle_partitions':p,'rows':rows,'elapsed_seconds':round(time.perf_counter()-t,3)}
 dim=d.select('category_id').distinct().withColumn('category_name',F.concat(F.lit('category_'),F.col('category_id'))).cache(); dim.count()
 t=time.perf_counter(); regular=d.join(dim,'category_id').count(); results['join_regular']={'rows':regular,'elapsed_seconds':round(time.perf_counter()-t,3)}
 t=time.perf_counter(); broadcast_rows=d.join(F.broadcast(dim),'category_id').count(); results['join_broadcast']={'rows':broadcast_rows,'elapsed_seconds':round(time.perf_counter()-t,3)}
finally: spark.stop()
DOCS.mkdir(exist_ok=True); (DOCS/'tuning_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# 调优实验记录\n\n以下数据来自当前输入数据的真实 Spark 运行，不能直接外推为 1 亿条全量数据的生产耗时。\n\n| 实验 | 配置 | 结果 | 耗时（秒） |\n|---|---|---:|---:|\n'''
for k,v in results.items():
 label={'shuffle_200':'shuffle 并行度基线','shuffle_400':'shuffle 并行度调整','join_regular':'普通 join','join_broadcast':'broadcast join'}[k]; cfg=v.get('shuffle_partitions','-'); md+=f'| {label} | {cfg} | {v["rows"]:,} | {v["elapsed_seconds"]:.3f} |\n'
md+='''\n解释：DWS/ADS 聚合中可通过 `spark.sql.shuffle.partitions` 调整并行度；小维表 join 可使用 `broadcast()`，减少不必要的 shuffle。真实数据运行后应在同一机器和相同输入下重复实验，并记录对应结果。\n'''
(DOCS/'tuning_report.md').write_text(md,encoding='utf-8'); print(results)

