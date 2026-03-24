import boto3
import time

ddb = boto3.client("dynamodb")
TABLE = "chat_memory"

def save_message(user_id, role, message, session_id):
    ddb.put_item(
        TableName=TABLE,
        Item={
            "user_id": {"S": user_id},
            "ts": {"N": str(time.time())},
            "role": {"S": role},
            "message": {"S": message},
            "session_id": {"S": session_id}
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