import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "storage", "transactions.db")

engine = create_engine(f"sqlite:///{DB_PATH}")


consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="transaction-consumer"
)

def consume():
    buffer = []

    for msg in consumer:
        buffer.append(msg.value)

        if len(buffer) >= 500:
            df = pd.DataFrame(buffer)
            df.to_sql("transactions", engine, if_exists="append", index=False)
            buffer.clear()
            print("Batch inserted")

if __name__ == "__main__":
    consume()
