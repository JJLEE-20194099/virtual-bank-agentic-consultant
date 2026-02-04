import json
import pandas as pd
from kafka import KafkaProducer

TOPIC = "transactions"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
)

def publish_transactions():
    df = pd.read_csv("../data/raw/transactions.csv")

    for _, row in df.iterrows():
        producer.send(TOPIC, row.to_dict())

    producer.flush()
    print("Published transactions to Kafka")

if __name__ == "__main__":
    publish_transactions()
