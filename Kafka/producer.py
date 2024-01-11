import os
import json
import time

from confluent_kafka import Producer

from Constant.const import bootstrap_servers, topic

# Create a Kafka producer configuration
producer_config = {'bootstrap.servers': bootstrap_servers}

# Create a Kafka producer instance
producer = Producer(producer_config)

# data_path = '..\\sample_crawler_data\\v1-sample.json'
directory = 'D:/learningProgrammingLanguages/Python/BigDataStockAnalyzer/2024-01-05-18-27-41'

for root, dirs, files in os.walk(directory):
    for index, filename in enumerate(files):
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)
            # Produce messages to Kafka topic
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                print('Data is:', str(data))
                producer.produce(topic=topic, value=str(data))
                producer.flush()
                print('Sent {}'.format(index))
            time.sleep(1)

print("Producer terminated.")
