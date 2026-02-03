from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode()
)

def publish_transactions(df):
    for _, row in df.iterrows():
        producer.send("transactions", row.to_dict())
