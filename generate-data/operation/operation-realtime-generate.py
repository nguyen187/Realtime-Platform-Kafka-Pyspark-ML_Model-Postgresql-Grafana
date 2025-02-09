import random
import psutil
import pandas as pd
import os
import socket
import json
import time
from confluent_kafka import Producer
from datetime import datetime

# Kafka configurations
kafka_broker = "localhost:9094"  # Update with your Kafka broker address
kafka_topic = "operation_metric"  # Update with your Kafka topic

# Initialize Kafka producer
producer = Producer({"bootstrap.servers": kafka_broker})

Cust = "TRU"
Project_ID = "TRU-01"
BatchID = 1

# Load data
data = pd.read_csv("Offline_operation1.csv")
data = data.drop(columns=["Time (h)"])
data.insert(0, "Cust", Cust, True)
data.insert(1, "Project_ID", Project_ID, True)
data.insert(2, "BatchID", BatchID, True)

i = 0
df_json = data.apply(lambda x: x.to_json(), axis=1)
N = df_json.shape[0]
Scan = 0

try:
    for i in df_json.index:
        print("Start send .......................")

        # Prepare the message
        Scan += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_data_with_time = json.loads(df_json[i])
        event_data_with_time = {"Scan": Scan, **event_data_with_time}
        event_data_with_time = {"Time stream": current_time, **event_data_with_time}

        print(event_data_with_time)

        # Send the message to Kafka
        producer.produce(
            kafka_topic, key=str(Scan), value=json.dumps(event_data_with_time)
        )
        producer.flush()  # Ensure the message is sent

        time.sleep(5)  # Delay for 1 second
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    # Ensure the producer is properly closed
    producer.flush()
