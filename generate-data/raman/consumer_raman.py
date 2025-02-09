from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka configurations
kafka_broker = "localhost:9094"  # Update with your Kafka broker address
kafka_topic = "raman_metric"  # Update with your Kafka topic
group_id = "raman-dev-1"  # Specify a consumer group ID

# Initialize Kafka consumer
consumer = Consumer(
    {
        "bootstrap.servers": kafka_broker,
        "group.id": group_id,
        "auto.offset.reset": "earliest",  # Start reading from the beginning if no offset is committed
    }
)

# Subscribe to the Kafka topic
consumer.subscribe([kafka_topic])

print(f"Subscribed to topic: {kafka_topic}")

try:
    while True:
        msg = consumer.poll(1.0)  # Poll for messages, timeout is 1 second

        if msg is None:
            continue  # No message received, continue polling
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(
                    f"Reached end of partition: {msg.topic()}[{msg.partition()}] at offset {msg.offset()}"
                )
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            # Print the key and value of the received message
            print(
                f"Received message: Key={msg.key()}, Value={msg.value().decode('utf-8')}"
            )

except KeyboardInterrupt:
    print("Consumer stopped by user.")
finally:
    # Ensure the consumer is properly closed
    consumer.close()
