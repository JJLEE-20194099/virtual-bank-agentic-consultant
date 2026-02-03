from kafka import KafkaConsumer
import json

def process_transaction(msg):
    return msg

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers=["localhost:9092"],
    value_deserializer=lambda v: json.loads(v.decode())
)

for msg in consumer:
    process_transaction(msg.value)