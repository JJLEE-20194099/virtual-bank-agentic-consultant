from kafka import KafkaProducer
import json
from config.endpoint import KAFKA_PRODUCER_ENDPOINT

producer = KafkaProducer(
    bootstrap_servers=KAFKA_PRODUCER_ENDPOINT,
    value_serializer=lambda v: v 
)

def publish_audio(session_id: str, audio_chunk: bytes):
    producer.send(
        topic="stt.audio.stream",
        key=session_id.encode(),
        value=audio_chunk
    )
