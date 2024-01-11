from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, ArrayType, DoubleType, DateType, TimestampType, StructField
from pyspark.sql.functions import col, udf, month, dayofweek, avg, log, year, from_json, explode, count, window, lag, expr, max_by, min_by, arrays_zip, when
from pyspark.sql.streaming import StreamingQueryListener
from datetime import datetime

# Set the Kafka server address
bootstrap_servers = 'kafka-1:9092'
LOCAL_IP = "127.0.0.1"
SPARK_IP = "192.168.79.101"
CASSANDRA_IP = "localhost"

# Set the Kafka topic
topic = 'stock'

# Kafka In/Out parameters
kafka_source_params = {
	"kafka.bootstrap.servers": bootstrap_servers,
	"subscribe": topic,
	"startingOffsets": "earliest"
}

spark = SparkSession \
		.builder \
		.appName("Stock Analyzer") \
		.config("spark.cassandra.connection.host", "cassandra") \
		.config("spark.cassandra.connection.port", "9042") \
		.config("spark.cassandra.auth.username", "cassandra")\
		.config("spark.cassandra.auth.password", "cassandra")\
		.config("spark.sql.streaming.checkpointLocation", "/opt/tmp") \
		.getOrCreate()
# .master("spark://" + SPARK_IP + ":7077") \

kafka_stream_df = spark \
	.readStream \
	.format("kafka") \
	.options(**kafka_source_params) \
	.load()

kafka_stream_df = kafka_stream_df.selectExpr("CAST(value AS STRING)")


# https://www.databricks.com/blog/2022/05/27/how-to-monitor-streaming-queries-in-pyspark.html
class QueryMonitor(StreamingQueryListener):
	def onQueryStarted(self, event):
		print("[LOG] Starting Query:")

	def onQueryIdle(self, event):
		print("[LOG] Waiting for new data...")

	def onQueryProgress(self, event):
		print(event)

	def onQueryTerminated(self, event):
		print("[LOG] Query stopped.")
		pass


spark.streams.addListener(QueryMonitor())
# Input JSON schema:
# {
#  ticker: "..."
#  data: [ { ... } ... ]         <--- join on dt.split(' ')[1]
#  bidAskLog: [ { ... } ... ]    <---          t 
# }

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

kafka_stream_df = kafka_stream_df.select(from_json(col='value', schema=detail_schema).alias('data')).select('data.*')


@udf(returnType=StringType())
def timesplit(x):
	if x is None:
		return ''
	return x.split(' ')[1]


@udf(returnType=TimestampType())
def parse_ts(x):
	if x is None:
		return datetime.fromtimestamp(0)
	ts = datetime.strptime(x, '%d/%m %H:%M')

	if ts.month == 12:
		ts = ts.replace(year=2023)
	else:
		ts = ts.replace(year=2024)

	return ts


data_spark = kafka_stream_df.select('ticker',
	explode(arrays_zip('data', 'bidAskLog'))) \
	.select('ticker', 'col.data.*', 'col.bidAskLog.*') \
	.withColumn('ts', parse_ts('dt')) \
	.withWatermark('ts', '1 day') \
	.select('ticker', 'ts', 'p', 'cp', 'rcp', 'v', 'ap1', 'bp1', 'av1', 'bv1')

print("[LOG] Data schema:")
data_spark.printSchema()

# Ticker đang có biến động nhiều nhất
df_weekly_vol = data_spark.select('ticker', 'v', 'ts') \
	.groupBy(window('ts', '1 week', '1 day'), 'ticker') \
	.agg({'v': 'sum'}).withColumnRenamed('sum(v)', 'v') \
	.select('ticker', 'v', 'window.*')

df_weekly_vol.printSchema()


def weekly_f(df, epoch_id):
	print(epoch_id, df)
	df.collect() # weird bug goes away
	df.show(100)


# query1 = df_weekly_vol \
# 	.writeStream \
# 	.format("console") \
# 	.outputMode('complete') \
# 	.start()

query1 = df_weekly_vol.writeStream \
	.format("console") \
	.outputMode("append") \
	.start()

# query1 = df_weekly_vol \
# 	.writeStream \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="weekly_vol", keyspace="stock_demo") \
# 	.outputMode('append') \
# 	.start()
#
# # Biểu đồ giá của các ticker
# df_price_fluctuations = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy(window('ts', '2 minute', '1 minute'), 'ticker') \
# 	.agg(expr('min_by(p, ts)').alias('p_prev'),
# 	     expr('max_by(p, ts)').alias('p_curr')) \
# 	.withColumn('p_delta', col('p_curr') - col('p_prev')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'p_delta')
#
# df_price_fluctuations.printSchema()
#
#
# def price_fluctuations_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)


# query2 = df_price_fluctuations.writeStream \
# 	.outputMode("append") \
# 	.format("console") \
# 	.start()
#
# query2 = df_price_fluctuations.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="price_fluctuations", keyspace="stock_demo") \
# 	.start()
#
# # Mỗi ticker đều xem được giá cao nhất và thấp nhất trong 1 ngày hoặc 1 tuần
# df_price_minmax = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy(window('ts', '1 week', '6 hours'), 'ticker') \
# 	.agg(expr('min(p)').alias('p_min'),
# 	     expr('max(p)').alias('p_max')) \
# 	.select('ticker', 'window.*', 'p_min', 'p_max')
#
# df_price_minmax.printSchema()
#
#
# def price_minmax_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query3 = df_price_minmax.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query3 = df_price_minmax.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="price_minmax", keyspace="stock_demo") \
# 	.start()
#
# # Giá hiện tại của ticker
# df_price_current = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy('ticker').agg(max_by('p', 'ts').alias('p_now')) \
# 	.withWatermark('ts', '1 minute') \
#
# df_price_current.printSchema()
#
#
# def price_current_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query4 = df_price_current.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query4 = df_price_current.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="price_current", keyspace="stock_demo") \
# 	.start()
#
# # Chênh lệch so với khởi điểm
# df_price_diff = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy(window('ts', '1 week', '6 hours'), 'ticker') \
# 	.agg(expr('min_by(p, ts)').alias('p_start'),
# 	     expr('max_by(p, ts)').alias('p_end')) \
# 	.withColumn('p_diff', col('p_end') - col('p_start')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'p_diff')
#
# df_price_diff.printSchema()
#
#
# def price_diff_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query5 = df_price_diff.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query5 = df_price_diff.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="price_diff", keyspace="stock_demo") \
# 	.start()
#
# # Biên độ ngày biên độ tuần
# df_price_amplitude = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy(window('ts', '1 week', '1 day'), 'ticker') \
# 	.agg(expr('min(p)').alias('p_min'),
# 	     expr('max(p)').alias('p_max')) \
# 	.withColumn('p_ampl', col('p_max') - col('p_min')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'p_ampl')
#
# df_price_amplitude.printSchema()
#
#
# def price_amplitude_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query6 = df_price_amplitude.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query6 = df_price_amplitude.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="price_amplitude", keyspace="stock_demo") \
# 	.start()
#
# # Bảng xếp loại theo biên độ
# df_fluctuation_rank = data_spark.select('ticker', 'p', 'ts') \
# 	.groupBy(window('ts', '1 week', '1 day'), 'ticker') \
# 	.agg(expr('min(p)').alias('p_min'),
# 	     expr('max(p)').alias('p_max')) \
# 	.withColumn('p_ampl', col('p_max') - col('p_min')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'p_ampl')
#
# df_fluctuation_rank.printSchema()
#
#
# def fluctuation_rank_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query7 = df_fluctuation_rank.writeStream \
# # 	.outputMode("complete") \
# # 	.format("console") \
# # 	.start()
#
# query7 = df_fluctuation_rank.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="fluctuation_rank", keyspace="stock_demo") \
# 	.start()
#
# # Các cổ phiếu hoạt động mạnh nhất theo khối lượng giao dịch
# # query1
# # Giá đóng cửa hôm trước, mở cửa hôm nay
# # ?
# # Khối lượng
# # ?
# # Khối lượng trung bình tuần
# df_weekly_avg = data_spark.select('ticker', 'v', 'ts') \
# 	.groupBy(window('ts', '1 week', '1 day'), 'ticker') \
# 	.agg(expr('avg(v)').alias('v')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'v')
#
# df_weekly_avg.printSchema()
#
#
# def weekly_avg_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query8 = df_weekly_avg.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query8 = df_weekly_avg.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="weekly_avg", keyspace="stock_demo") \
# 	.start()
#
# # Số lệnh mua lệnh bán trong tuần
# df_weekly_bid = data_spark.select('ticker', 'ts', 'v') \
# 	.groupBy(window('ts', '1 week', '1 day'), 'ticker') \
# 	.agg(count(when(col('v') > 0, 1)).alias('num')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'num')
#
# df_weekly_bid.printSchema()
#
#
# def weekly_bid_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect() # weird bug goes away
# 	df.show(100)
#
#
# # query9 = df_weekly_bid.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query9 = df_weekly_bid.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="weekly_bid", keyspace="stock_demo") \
# 	.start()

# Đồ thị MA
# df_moving_avg = data_spark.select('ticker', 'ts', 'p') \
# 	.groupBy(window('ts', '6 hours', '1 hour'), 'ticker') \
# 	.agg(avg('p').alias('avg')) \
# 	.withWatermark('ts', '1 minute') \
# 	.select('ticker', 'window.*', 'avg')
#
# df_moving_avg.printSchema()
#
#
# def moving_avg_f(df, epoch_id):
# 	print(epoch_id, df)
# 	df.collect()  # weird bug goes away
# 	df.show(100)
#
#
# # query10 = df_moving_avg.writeStream \
# # 	.outputMode("append") \
# # 	.format("console") \
# # 	.start()
#
# query10 = df_moving_avg.writeStream \
# 	.outputMode("append") \
# 	.format("org.apache.spark.sql.cassandra") \
# 	.options(table="moving_avg", keyspace="stock_demo") \
# 	.start()
# Điểm giới hạn
# ??
# Các cổ phiếu % tăng, giảm cao nhất

print("Wait for termination muahaha!!!")
query1.awaitTermination()
# query2.awaitTermination()
# query3.awaitTermination()
# query4.awaitTermination()
# query5.awaitTermination()
# query6.awaitTermination()
# query7.awaitTermination()
# query8.awaitTermination()
# query9.awaitTermination()
# query10.awaitTermination()
