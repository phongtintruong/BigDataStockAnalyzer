from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StringType, ArrayType, DoubleType

# Set the Kafka server address
bootstrap_servers = 'kafka-1:9092'
LOCAL_IP = "127.0.0.1"
SPARK_IP = "192.168.79.101"
CASSANDRA_IP = "localhost"

# Set the Kafka topic
topic = 'stock'

# Create a Spark session
spark = SparkSession \
        .builder \
        .appName("Stock Analyzer") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.cassandra.auth.username", "cassandra")\
        .config("spark.cassandra.auth.password", "cassandra")\
        .config("spark.sql.streaming.checkpointLocation", "/tmp/stock/checkpoint") \
        .getOrCreate()

# Define the schema for the incoming Kafka messages
schema = StructType().add("message", StringType())

# Define Kafka parameters
kafka_params = {
    "kafka.bootstrap.servers": bootstrap_servers,
    "subscribe": topic,
    "startingOffsets": "latest"
}

# Read from Kafka
kafka_stream_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_params) \
    .load()

# Convert the value column to a string and parse JSON
kafka_stream_df = kafka_stream_df.selectExpr("CAST(value AS STRING)")

# detail_schema = StructType() \
#     .add('date', StringType()) \
#     .add('p', StringType()) \
#     .add('cp', StringType()) \
#     .add('rcp', StringType()) \
#     .add('v', StringType()) \
#     .add('ap1', StringType()) \
#     .add('bp1', StringType()) \
#     .add('av1', StringType()) \
#     .add('bv1', StringType())

price_schema = ArrayType(
    StructType()
    .add('p',   DoubleType())
    .add('cp',  DoubleType())
    .add('rcp', DoubleType())
    .add('v',   DoubleType())
    .add('dt',  StringType())
)

comm_schema = ArrayType(
    StructType()
    .add('ap1', DoubleType())
    .add('bp1', DoubleType())
    .add('av1', DoubleType())
    .add('bv1', DoubleType())
    .add('t',   StringType())
)

detail_schema = StructType() \
    .add('ticker', StringType()) \
    .add('data', price_schema) \
    .add('bidAskLog', comm_schema)

# kafka_stream_df = kafka_stream_df.select('value')

kafka_stream_df = kafka_stream_df \
    .select(from_json(col='value', schema=detail_schema).alias('data')).select('data.*')

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
    .options(table="value_test", keyspace="stock_demo") \
    .outputMode('append') \
    .start()

# Start the streaming query
query.awaitTermination()
