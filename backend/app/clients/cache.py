import redis
import json
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            REDIS_URL,
            decode_responses=True
        )

    def set(self, key, value, ex=None):
        return self.client.set(key, value, ex=ex)

    def get(self, key):
        return json.loads(self.client.get(key))

    def delete(self, key):
        return self.client.delete(key)

    def set_many(self, data: dict, ex=None):
        """
        data = {
            "key1": value1,
            "key2": value2
        }
        """
        pipe = self.client.pipeline()

        for key, value in data.items():
            pipe.set(key, json.dumps(value), ex=ex)

        pipe.execute()