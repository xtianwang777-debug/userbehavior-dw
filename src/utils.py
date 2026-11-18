from pathlib import Path
import json
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "UserBehavior.csv"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
OUTPUT = ROOT / "output"
START_DATE = "2017-11-25"
END_DATE = "2017-12-03"

def build_spark(app_name: str, shuffle_partitions: int = 200):
    return (SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", str(shuffle_partitions))
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.memory", "4g")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.hadoop.hadoop.native.lib", "false")
        .config("spark.hadoop.io.native.lib.available", "false")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .getOrCreate())

def read_raw(spark, path=None):
    path = str(path or RAW)
    schema = "user_id long, item_id long, category_id long, behavior_type string, ts long"
    return (spark.read.schema(schema).option("header", "false").option("mode", "PERMISSIVE").csv(path))

def with_dt(df):
    return df.withColumn("dt", F.to_date(F.from_unixtime("ts")).cast("string"))

def write_json(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def csv_export(df, name):
    out = OUTPUT / "ads" / name
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(str(out))
    parts = list(out.glob("part-*.csv"))
    if len(parts) == 1:
        parts[0].replace(out / "data.csv")
    for p in out.glob(".*"):
        p.unlink(missing_ok=True)
    for p in out.glob("_SUCCESS"):
        p.unlink(missing_ok=True)
    return out

