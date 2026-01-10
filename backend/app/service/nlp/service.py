import json
from kafka import KafkaProducer, KafkaConsumer
from app.service.nlp.engine import analyze
from app.config.endpoint import TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT, TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

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
    
    producer.send("conversation.nlp", {
        "event_type": "NLP_INSIGHT",
        "session_id": event["session_id"],
        "parent_event_id": event["event_id"],
        "payload": result
    })