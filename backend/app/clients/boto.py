import boto3
import os
import json
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

class BotoClient:
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
        )
        self.ddb = None

    def init_dynamo_session(self):
        self.ddb = self.session.client("dynamodb")

    def init_memory_table(self):
        self.memory_table = "chat_memory"
        try:
            self.ddb.describe_table(TableName=self.memory_table)
            print(f"Table {self.memory_table} already exists")
        except self.ddb.exceptions.ResourceNotFoundException:
            print(f"Creating table {self.memory_table}...")

            self.ddb.create_table(
                TableName=self.memory_table,
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"},
                ],
                KeySchema=[
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                ],
                BillingMode="PAY_PER_REQUEST"
            )

            waiter = self.ddb.get_waiter("table_exists")
            waiter.wait(TableName=self.memory_table)

            print("Table created")

    def _to_dynamodb_json(self, data: Dict):
        return {"S": json.dumps(data)}

    def _from_dynamodb_json(self, item):
        return json.loads(item["S"])