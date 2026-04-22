from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, trim, when, split, size, desc, lit, to_timestamp, concat,
    min as spark_min, max as spark_max, avg as spark_avg,
    sum as spark_sum, count as spark_count,
    percentile_approx, window
)

# Hardcoded paths for Dataproc simple UI
INPUT_PATH = "gs://big_data_oppe_1/input/Train_details_22122017.csv"
OUTPUT_BASE = "gs://big_data_oppe_1/output"

spark = SparkSession.builder.appName("RailwayStopAnalysis").getOrCreate()

# =========================================================
# 1. Read CSV
# =========================================================
raw_df = (
    spark.read
    .option("header", True)
    .option("sep", ",")
    .csv(INPUT_PATH)
)

# =========================================================
# 2. Select required columns
# =========================================================
df = raw_df.select(
    trim(col("Train No")).alias("train_no"),
    trim(col("Train Name")).alias("train_name"),
    trim(col("SEQ")).alias("seq"),
    trim(col("Station Code")).alias("station_code"),
    trim(col("Station Name")).alias("station_name"),
    trim(col("Arrival time")).alias("arrival_time"),
    trim(col("Departure Time")).alias("departure_time")
)

# =========================================================
# 3. Remove bad / missing rows
# =========================================================
df = df.filter(
    col("train_no").isNotNull() &
    col("seq").isNotNull() &
    col("station_code").isNotNull() &
    col("station_name").isNotNull() &
    col("arrival_time").isNotNull() &
    col("departure_time").isNotNull() &
    (col("train_no") != "") &
    (col("seq") != "") &
    (col("station_code") != "") &
    (col("station_name") != "") &
    (col("arrival_time") != "") &
    (col("departure_time") != "")
)

df = df.withColumn("seq", col("seq").cast("int"))

# =========================================================
# 4. Convert HH:MM:SS into seconds
# =========================================================
def hms_to_seconds_expr(cname):
    parts = split(col(cname), ":")
    return when(
        size(parts) == 3,
        parts.getItem(0).cast("int") * 3600 +
        parts.getItem(1).cast("int") * 60 +
        parts.getItem(2).cast("int")
    )

df = df.withColumn("arrival_sec_raw", hms_to_seconds_expr("arrival_time"))
df = df.withColumn("departure_sec_raw", hms_to_seconds_expr("departure_time"))

df = df.filter(
    col("arrival_sec_raw").isNotNull() &
    col("departure_sec_raw").isNotNull()
)

# =========================================================
# 5. Handle placeholder 0:00:00 values
# =========================================================
df = df.withColumn(
    "arrival_sec",
    when((col("seq") == 1) & (col("arrival_time") == "0:00:00"), None)
    .otherwise(col("arrival_sec_raw"))
)

df = df.withColumn(
    "departure_sec",
    when((col("seq") > 1) & (col("departure_time") == "0:00:00"), None)
    .otherwise(col("departure_sec_raw"))
)

# =========================================================
# 6. Compute stop duration in minutes
# If departure < arrival, assume next day
# =========================================================
df = df.withColumn(
    "stop_duration_min",
    when(
        col("arrival_sec").isNotNull() & col("departure_sec").isNotNull(),
        when(
            col("departure_sec") >= col("arrival_sec"),
            (col("departure_sec") - col("arrival_sec")) / 60.0
        ).otherwise(
            (col("departure_sec") + 86400 - col("arrival_sec")) / 60.0
        )
    )
)

stops_df = df.filter(
    col("stop_duration_min").isNotNull() &
    (col("stop_duration_min") >= 0)
)

# =========================================================
# 7. Create artificial timestamp for sliding window
# =========================================================
stops_df = stops_df.withColumn(
    "arrival_ts",
    when(
        col("arrival_sec").isNotNull(),
        to_timestamp(
            concat(lit("1970-01-01 "), col("arrival_time")),
            "yyyy-MM-dd H:mm:ss"
        )
    )
)

# =========================================================
# Section A – Stop Duration Statistics
# =========================================================
station_stats = stops_df.groupBy("station_code", "station_name").agg(
    spark_min("stop_duration_min").alias("min_stop_duration"),
    spark_max("stop_duration_min").alias("max_stop_duration"),
    spark_avg("stop_duration_min").alias("avg_stop_duration"),
    percentile_approx("stop_duration_min", 0.9).alias("p90_stop_duration"),
    spark_count("*").alias("stoppage_count")
)

top5_stations = station_stats.orderBy(desc("stoppage_count")).limit(5)

# =========================================================
# Section B – Station Load Analysis
# =========================================================
station_load = stops_df.groupBy("station_code", "station_name").agg(
    spark_sum("stop_duration_min").alias("total_stop_duration"),
    spark_avg("stop_duration_min").alias("avg_stop_duration"),
    spark_max("stop_duration_min").alias("max_stop_duration"),
    spark_count("*").alias("stoppage_count")
)

anomaly_stations = station_load.filter(
    col("max_stop_duration") > 3 * col("avg_stop_duration")
)

# =========================================================
# 8. Sliding 2-hour window for one top-5 station
# =========================================================
top5_rows = top5_stations.collect()
selected_station_code = top5_rows[0]["station_code"] if top5_rows else None
selected_station_name = top5_rows[0]["station_name"] if top5_rows else None

if selected_station_code:
    selected_df = stops_df.filter(
        (col("station_code") == selected_station_code) &
        col("arrival_ts").isNotNull()
    )

    arrivals_2hr = selected_df.groupBy(
        window(col("arrival_ts"), "2 hours", "1 minute")
    ).agg(
        spark_count("*").alias("arrivals_in_window")
    )

    max_arrivals_2hr = (
        arrivals_2hr
        .orderBy(desc("arrivals_in_window"))
        .limit(1)
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("arrivals_in_window")
        )
        .withColumn("station_code", lit(selected_station_code))
        .withColumn("station_name", lit(selected_station_name))
    )
else:
    max_arrivals_2hr = spark.createDataFrame(
        [],
        "window_start timestamp, window_end timestamp, arrivals_in_window long, station_code string, station_name string"
    )

# =========================================================
# 9. Write outputs to GCS
# =========================================================
station_stats.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/station_stats")
top5_stations.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/top5_stations")
station_load.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/station_load")
anomaly_stations.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/anomaly_stations")
max_arrivals_2hr.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/max_arrivals_2hr")

final_summary = station_stats.select(
    "station_code",
    "station_name",
    "min_stop_duration",
    "max_stop_duration",
    "avg_stop_duration",
    "p90_stop_duration",
    "stoppage_count"
)

final_summary.coalesce(1).write.mode("overwrite").option("header", True).csv(OUTPUT_BASE + "/final_summary")

print("=== TOP 5 STATIONS ===")
top5_stations.show(truncate=False)

print("=== ANOMALY STATIONS ===")
anomaly_stations.show(truncate=False)

print(f"=== SELECTED STATION FOR 2-HOUR WINDOW: {selected_station_code} - {selected_station_name} ===")
max_arrivals_2hr.show(truncate=False)

spark.stop()