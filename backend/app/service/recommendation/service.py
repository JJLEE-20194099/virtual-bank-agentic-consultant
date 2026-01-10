from kafka import KafkaProducer, KafkaConsumer
import json
from app.config.endpoint import TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT, TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT
from app.service.recommendation.engine import recommend

producer = KafkaProducer(
    bootstrap_servers=TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT,
    value_serializer=lambda v: json.dumps(v).encode()
)

consumer = KafkaConsumer(
    "conversation.compliance",
    bootstrap_servers=TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT,
    value_deserializer=lambda m: json.loads(m.decode()),
    group_id="compliance-service"
)


for msg in consumer:
    event = msg.value
    session_id = event["session_id"]
    payload = event["payload"]
    
    nlp = payload["nlp"]
    compliance_issue_result = payload["compliance_issue"]
    customer_data = payload["customer_data"]
    
    recommendations = recommend(nlp, compliance_issue_result, customer_data)

    producer.send("conversation.recommendation", {
        "session_id": session_id,
        "payload": {
            "recommendations": recommendations,
            "safe_to_propose": True
        }
    })