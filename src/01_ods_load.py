import argparse, time
from pathlib import Path
from utils import build_spark, read_raw, with_dt, DATA, DOCS

p=argparse.ArgumentParser(); p.add_argument('--input'); p.add_argument('--shuffle',type=int,default=200); args=p.parse_args()
spark=build_spark('userbehavior-ods-load', args.shuffle); t=time.perf_counter()
try:
    df=with_dt(read_raw(spark, args.input))
    out=DATA/'ods'
    df.write.mode('overwrite').partitionBy('dt').parquet(str(out))
    total=df.count(); by_day={r['dt']:r['count'] for r in df.groupBy('dt').count().orderBy('dt').collect()}
    DOCS.mkdir(exist_ok=True)
    (DOCS/'ods_stats.json').write_text(__import__('json').dumps({'rows':total,'partitions':by_day,'elapsed_seconds':round(time.perf_counter()-t,3)},ensure_ascii=False,indent=2),encoding='utf-8')
    print({'rows':total,'partitions':len(by_day),'elapsed_seconds':round(time.perf_counter()-t,3)})
finally: spark.stop()
