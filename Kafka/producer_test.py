import time
import json

from confluent_kafka import Producer

from Constant.const import bootstrap_servers, topic

# Create a Kafka producer configuration
producer_config = {'bootstrap.servers': bootstrap_servers}

# Create a Kafka producer instance
producer = Producer(producer_config)

data_path = '..\\Crawler\\PriceRealtime.jsonl'

# Produce messages to Kafka topic
with open(data_path, 'r', encoding='utf-8') as json_file:
    for index, line in enumerate(json_file.readlines()):
        obj = json.loads(line)
        time.sleep(1)
        producer.produce('test', value=str(obj))
        producer.flush()
        print('Sent ', index)

print("Producer terminated.")