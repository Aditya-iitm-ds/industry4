from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

BOOTSTRAP_SERVERS = "10.128.0.3:9092"
TOPIC = "stream-demo-topic"

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("amount", IntegerType(), True),
    StructField("event_time", StringType(), True),
    StructField("source_file", StringType(), True),
    StructField("producer_id", StringType(), True),
    StructField("sent_at", StringType(), True),
])

spark = SparkSession.builder.appName("KafkaStructuredStreamingConsumer").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS)
    .option("subscribe", TOPIC)
    .option("startingOffsets", "earliest")
    .load()
)

json_df = raw_df.selectExpr(
    "CAST(value AS STRING) AS json_str",
    "timestamp AS kafka_timestamp"
)

parsed_df = (
    json_df
    .select(
        from_json(col("json_str"), schema).alias("data"),
        col("kafka_timestamp")
    )
    .select("data.*", "kafka_timestamp")
)

windowed_counts = (
    parsed_df
    .groupBy(
        window(col("kafka_timestamp"), "10 seconds", "5 seconds"),
        col("producer_id")
    )
    .count()
    .selectExpr(
        "CAST(window.start AS STRING) AS window_start",
        "CAST(window.end AS STRING) AS window_end",
        "producer_id",
        "count"
    )
)

query = (
    windowed_counts.writeStream
    .outputMode("update")
    .format("console")
    .option("truncate", "false")
    .trigger(processingTime="5 seconds")
    .start()
)

query.awaitTermination()