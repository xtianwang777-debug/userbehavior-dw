import time
from utils import build_spark, DATA, csv_export
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark=build_spark('userbehavior-ads-metrics', 400); t=time.perf_counter()
try:
 d=spark.read.parquet(str(DATA/'dwd')); active=d.select('user_id','dt').distinct()
 dau=active.groupBy('dt').agg(F.countDistinct('user_id').alias('dau')).orderBy('dt')
 a=active.alias('a'); b=active.alias('b')
 next1=(a.join(b,(F.col('a.user_id')==F.col('b.user_id'))&(F.col('b.dt')==F.date_add(F.to_date('a.dt'),1)),'left').groupBy(F.col('a.dt').alias('dt')).agg(F.countDistinct('a.user_id').alias('dau'),F.countDistinct('b.user_id').alias('next_day_uv')).withColumn('retention_1d',F.when(F.col('dau')>0,F.col('next_day_uv')/F.col('dau')).otherwise(0.0)))
 next7=(a.join(b,(F.col('a.user_id')==F.col('b.user_id'))&(F.to_date('b.dt')>F.to_date('a.dt'))&(F.to_date('b.dt')<=F.date_add(F.to_date('a.dt'),7)),'left').groupBy(F.col('a.dt').alias('dt')).agg(F.countDistinct('b.user_id').alias('retention_7d_uv')))
 retention=(next1.join(next7,'dt','left').withColumn('retention_7d',F.when(F.col('dau')>0,F.col('retention_7d_uv')/F.col('dau')).otherwise(0.0)).orderBy('dt'))
 f=(d.groupBy('dt').agg(*[F.countDistinct(F.when(F.col('behavior_type')==x,F.col('user_id'))).alias(x+'_uv') for x in ['pv','cart','fav','buy']]).withColumn('pv_to_cart_rate',F.when(F.col('pv_uv')>0,F.col('cart_uv')/F.col('pv_uv')).otherwise(0.0)).withColumn('cart_to_buy_rate',F.when(F.col('cart_uv')>0,F.col('buy_uv')/F.col('cart_uv')).otherwise(0.0)).withColumn('pv_to_buy_rate',F.when(F.col('pv_uv')>0,F.col('buy_uv')/F.col('pv_uv')).otherwise(0.0)).orderBy('dt'))
 cat=spark.read.parquet(str(DATA/'dws/category_agg_1d')); w=Window.partitionBy('dt').orderBy(F.col('buy_cnt').desc(),F.col('category_id')); top=cat.withColumn('rank_no',F.row_number().over(w)).filter('rank_no<=10').select('dt','category_id','buy_cnt','buy_uv','rank_no').orderBy('dt','rank_no')
 buys=d.filter(F.col('is_buy')==1).groupBy('user_id').agg(F.countDistinct('dt').alias('buy_days'))
 rep_df=(buys.agg(F.count(F.lit(1)).alias('buyer_cnt'),F.sum(F.when(F.col('buy_days')>=2,1).otherwise(0)).alias('repurchase_user_cnt'))
   .withColumn('window_start',F.lit('2017-11-25')).withColumn('window_end',F.lit('2017-12-03'))
   .withColumn('repurchase_rate',F.when(F.col('buyer_cnt')>0,F.col('repurchase_user_cnt')/F.col('buyer_cnt')).otherwise(0.0))
   .select('window_start','window_end','buyer_cnt','repurchase_user_cnt','repurchase_rate'))
 for df,name in [(dau,'ads_dau_daily'),(retention,'ads_retention_daily'),(f,'ads_funnel_daily'),(top,'ads_category_top10'),(rep_df,'ads_repurchase')]: csv_export(df,name)
 print({'elapsed_seconds':round(time.perf_counter()-t,3),'dau_peak':dau.agg(F.max('dau')).first()[0]})
finally: spark.stop()

