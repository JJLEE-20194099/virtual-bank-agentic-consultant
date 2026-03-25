import boto3
import time
import json
from dotenv import load_dotenv      
import os
load_dotenv()

region_name = os.getenv("AWS_REGION", "ap-southeast-1")
print(region_name)
ddb = boto3.client("dynamodb", region_name=region_name)
TABLE = "chat_memory"

def ensure_table_exists():
    try:
        ddb.describe_table(TableName=TABLE)
        print(f"Table {TABLE} already exists")
        return

    except ddb.exceptions.ResourceNotFoundException:
        print(f"Creating table {TABLE}...")

        ddb.create_table(
            TableName=TABLE,
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "ts", "AttributeType": "N"},
            ],
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "ts", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        waiter = ddb.get_waiter("table_exists")
        waiter.wait(TableName=TABLE)

        print(f"Table {TABLE} created successfully")

def build_context(history):
    return "\n".join([
        f"{h['role']['S']}: {h['message']['S']}"
        for h in history
    ])


def save_message(user_id, role, message, metadata, session_id):

    ddb.put_item(
        TableName=TABLE,
        Item={
            "user_id": {"S": user_id},
            "ts": {"N": str(time.time())},
            "role": {"S": role},
            "message": {"S": message},
            "session_id": {"S": session_id},
            "metadata": {"S": json.dumps(metadata or {})}
        }
    )


def load_history(user_id):
    res = ddb.query(
        TableName=TABLE,
        KeyConditionExpression="user_id = :u",
        ExpressionAttributeValues={
            ":u": {"S": user_id}
        }
    )
    return res.get("Items", [])