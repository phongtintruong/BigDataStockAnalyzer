import time
import json

from confluent_kafka import Producer

from Constant.const import bootstrap_servers, topic

# Create a Kafka producer configuration
producer_config = {'bootstrap.servers': bootstrap_servers}

# Create a Kafka producer instance
producer = Producer(producer_config)

data_path = '..\\sample_crawler_data\\v1-sample.json'

# Produce messages to Kafka topic
with open(data_path, 'r', encoding='utf-8') as json_file:
    print("Start load data")
    data = json.load(json_file)
    print('Data is ', data)
    producer.produce(topic=topic, value=str(data))
    producer.flush()
    print('Sent 1')

print("Producer terminated.")
