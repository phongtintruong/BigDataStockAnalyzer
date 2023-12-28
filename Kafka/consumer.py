from confluent_kafka import Consumer, KafkaError

from Constant.const import bootstrap_servers, topic

# Create a Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest'  # Start consuming from the beginning of the topic
}

# Create a Kafka consumer instance
consumer = Consumer(consumer_config)

# Subscribe to the Kafka topic
consumer.subscribe([topic])

i = 1

# Consume messages from Kafka topic
try:
    while True:
        msg = consumer.poll(1.0)  # Timeout set to 1 second
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event, not an error
                continue
            else:
                print(msg.error())
                break
        print(i)
        print('Received message: {}'.format(msg.value().decode('utf-8')), end='\n')
        i += 1
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
    print("Consumer terminated.")
