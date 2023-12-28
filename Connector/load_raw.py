from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StringType, ArrayType, DoubleType

# Create a Spark session
spark = SparkSession \
        .builder \
        .appName("Stock Analyzer") \
        .master("spark://192.168.79.106:7077") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector-assembly_2.12:3.4.1") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", True) \
        .getOrCreate()

# Define the schema for the incoming Kafka messages
schema = StructType().add("message", StringType())

# Define Kafka parameters
kafka_params = {
    "kafka.bootstrap.servers": "192.168.79.106:9092",
    "subscribe": "demo-stock-1",
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

price_schema = ArrayType(     \
     StructType()             \
    .add('p',   DoubleType()) \
    .add('cp',  DoubleType()) \
    .add('rcp', DoubleType()) \
    .add('v',   DoubleType()) \
    .add('dt',  StringType()))
    
comm_schema = ArrayType(      \
     StructType()             \
    .add('ap1', DoubleType()) \
    .add('bp1', DoubleType()) \
    .add('av1', DoubleType()) \
    .add('bv1', DoubleType()) \
    .add('t',   StringType()))

detail_schema = StructType() \
    .add('ticker', StringType()) \
    .add('data', price_schema) \
    .add('bidAskLog', comm_schema)

kafka_stream_df = kafka_stream_df \
    .select(from_json(col='value', schema=detail_schema).alias('data'))

kafka_stream_df = kafka_stream_df.select('data.*')

query = kafka_stream_df \
    .writeStream \
    .format("console") \
    .start()

# Start the streaming query
query.awaitTermination()
