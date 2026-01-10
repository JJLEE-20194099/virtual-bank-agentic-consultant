from kafka import KafkaConsumer, KafkaProducer
import json
from app.service.compliance.engine import run_compliance
from app.config.endpoint import TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT, TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT

consumer = KafkaConsumer(
    "conversation.nlp",
    bootstrap_servers=TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT,
    value_deserializer=lambda m: json.loads(m.decode()),
    group_id="compliance-service"
)

producer = KafkaProducer(
    bootstrap_servers=TRANSCRIPT_KAFKA_PRODUCER_ENDPOINT,
    value_serializer=lambda v: json.dumps(v).encode()
)

for msg in consumer:
    event = msg.value
    session_id = event["session_id"]
    nlp = event["payload"]

    # Fake customer context data
    customer_data = {
        "suitability_done": False,
        "risk_profile": "MEDIUM",
        "customer_profile": {}
    }

    # issues = run_compliance(nlp, customer_data)
    issues = []
    producer.send("conversation.compliance", {
        "event_type": "COMPLIANCE_RESULT",
        "session_id": session_id,
        "payload": {
            "nlp": nlp,
            "compliance_issue": issues,
            "compliant": len(issues) == 0,
            "customer_data": customer_data
        }
    })
