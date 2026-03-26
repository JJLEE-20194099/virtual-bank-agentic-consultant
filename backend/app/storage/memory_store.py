import boto3
import time
import json
from dotenv import load_dotenv      
import os
load_dotenv()
from app.core.boto_instance import boto_client

TABLE = "chat_memory"

def build_context(history):
    return "\n".join([
        f"{h['role']['S']}: {h['message']['S']}"
        for h in history
    ])


def save_message(user_id, role, message, metadata, session_id):

    boto_client.ddb.put_item(
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
    res = boto_client.ddb.query(
        TableName=TABLE,
        KeyConditionExpression="user_id = :u",
        ExpressionAttributeValues={
            ":u": {"S": user_id}
        }
    )
    return res.get("Items", [])