from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StringType

from Constant.const import bootstrap_servers, topic

# Create a Spark session
spark = SparkSession \
        .builder \
        .appName("Stock Analyzer") \
        .master("local[*]") \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector-assembly_2.12:3.4.1") \
        .config("spark.cassandra.connection.host", "127.0.0.1") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/stock/checkpoint") \
        .getOrCreate()

# Define the schema for the incoming Kafka messages
schema = StructType().add("message", StringType())

# Define Kafka parameters
kafka_params = {
    "kafka.bootstrap.servers": bootstrap_servers,
    "subscribe": topic,
    "startingOffsets": "earliest"
}

# Read from Kafka
kafka_stream_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_params) \
    .load()

# Convert the value column to a string and parse JSON
kafka_stream_df = kafka_stream_df.selectExpr("CAST(value AS STRING)")

detail_schema = StructType() \
    .add('date', StringType()) \
    .add('p', StringType()) \
    .add('cp', StringType()) \
    .add('rcp', StringType()) \
    .add('v', StringType()) \
    .add('ap1', StringType()) \
    .add('bp1', StringType()) \
    .add('av1', StringType()) \
    .add('bv1', StringType())

kafka_stream_df = kafka_stream_df \
    .select(from_json(col='value', schema=detail_schema).alias('data'))

kafka_stream_df = kafka_stream_df.select('data.*')

# Perform your processing on the streaming DataFrame
# For example, you can display the messages to the console
# query = kafka_stream_df \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()

query = kafka_stream_df \
    .writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("checkpointLocation", '/tmp/check_point/') \
    .options(table="tbl_pricerealtime", keyspace="stock_demo") \
    .outputMode('append') \
    .start()

# Start the streaming query
query.awaitTermination()
