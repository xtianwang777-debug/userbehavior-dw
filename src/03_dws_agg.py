import argparse, time, json
from utils import build_spark, write_parquet, DATA, DOCS
from pyspark.sql import functions as F

p=argparse.ArgumentParser(); p.add_argument('--shuffle',type=int,default=400); a=p.parse_args()
spark=build_spark('userbehavior-dws-agg', a.shuffle); t=time.perf_counter()
try:
    d=spark.read.parquet(str(DATA/'dwd'))
    user=(d.groupBy('user_id','dt').agg(F.sum('is_pv').alias('pv_cnt'),F.sum('is_cart').alias('cart_cnt'),F.sum('is_fav').alias('fav_cnt'),F.sum('is_buy').alias('buy_cnt')).withColumn('is_active',F.lit(1)))
    item=(d.groupBy('item_id','dt').agg(F.sum('is_pv').alias('pv_cnt'),F.sum('is_cart').alias('cart_cnt'),F.sum('is_fav').alias('fav_cnt'),F.sum('is_buy').alias('buy_cnt'),F.countDistinct(F.when(F.col('is_buy')==1,F.col('user_id'))).alias('buy_uv')).withColumn('pv_to_buy_rate',F.when(F.col('pv_cnt')>0,F.col('buy_cnt')/F.col('pv_cnt')).otherwise(F.lit(0.0))))
    cat=(d.groupBy('category_id','dt').agg(F.sum('is_pv').alias('pv_cnt'),F.sum('is_buy').alias('buy_cnt'),F.countDistinct(F.when(F.col('is_buy')==1,F.col('user_id'))).alias('buy_uv')))
    from pyspark.sql.window import Window
    w=Window.partitionBy('dt'); cat=cat.withColumn('category_buy_share',F.when(F.sum('buy_cnt').over(w)>0,F.col('buy_cnt')/F.sum('buy_cnt').over(w)).otherwise(F.lit(0.0)))
    checks={'user_grain_duplicate_keys':user.groupBy('user_id','dt').count().filter('count>1').count(),'item_grain_duplicate_keys':item.groupBy('item_id','dt').count().filter('count>1').count(),'category_grain_duplicate_keys':cat.groupBy('category_id','dt').count().filter('count>1').count()}
    for df,name in [(user,'user_agg_1d'),(item,'item_agg_1d'),(cat,'category_agg_1d')]: write_parquet(df, DATA/'dws'/name)
    DOCS.mkdir(exist_ok=True); (DOCS/'grain_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print({'elapsed_seconds':round(time.perf_counter()-t,3),'shuffle_partitions':a.shuffle,'user_rows':user.count(),'item_rows':item.count(),'category_rows':cat.count(),'checks':checks})
finally: spark.stop()
