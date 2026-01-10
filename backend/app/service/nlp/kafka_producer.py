from kafka import KafkaProducer
import json
from app.config.endpoint import TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def publish_nlp(session_id, event_id, result):
    producer.send("conversation.nlp", {
        "event_type": "NLP_INSIGHT",
        "session_id": session_id,
        "parent_event_id": event_id,
        "payload": result
    })