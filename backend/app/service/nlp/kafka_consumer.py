from kafka import KafkaConsumer
import json
from app.service.nlp.kafka_producer import publish_nlp
from app.service.nlp.engine import analyze
from app.config.endpoint import TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT

consumer = KafkaConsumer(
    "conversation.transcript",
    bootstrap_servers=TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="nlp-service"
)

for msg in consumer:
    event = msg.value
    payload = event["payload"]

    if not payload["is_final"]:
        continue
    result = analyze(payload["text"])
    
    publish_nlp(
        session_id=event["session_id"],
        event_id=event["event_id"],
        result=result
    )