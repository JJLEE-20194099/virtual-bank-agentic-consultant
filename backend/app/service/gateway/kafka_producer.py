from kafka import KafkaProducer
import json
import uuid
import time
from app.config.endpoint import KAFKA_PRODUCER_ENDPOINT

producer = KafkaProducer(
    bootstrap_servers=KAFKA_PRODUCER_ENDPOINT,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def publish_transcript(session_id, transcript):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "TRANSCRIPT",
        "session_id": session_id,
        "timestamp": int(time.time()),
        "version": "1.0",
        "payload": {
            "text": transcript.text,
            "is_final": transcript.is_final,
            "language": transcript.language
        }
    }
    producer.send("conversation.transcript", event)