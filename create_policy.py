import boto3
import json

iam = boto3.client("iam")
ROLE_NAME = "AmazonBedrockExecutionRole"
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]

# 1. Cập nhật Trust Relationship (Cho phép Bedrock dùng Role này)
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": { "Service": "bedrock.amazonaws.com" },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": { "aws:SourceAccount": ACCOUNT_ID },
                "ArnLike": { "aws:SourceArn": f"arn:aws:bedrock:*:{ACCOUNT_ID}:agent/*" }
            }
        }
    ]
}


# 2. Cập nhật Permissions (Cho phép Role gọi Model Claude)
permissions_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
        }
    ]
}

try:
    # Cập nhật Trust Relationship
    iam.update_assume_role_policy(
        RoleName=ROLE_NAME,
        PolicyDocument=json.dumps(trust_policy)
    )
    # Cập nhật Inline Policy
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="BedrockModelAccess",
        PolicyDocument=json.dumps(permissions_policy)
    )
    print("🚀 Đã cấu hình xong IAM Role. Đợi 10s để AWS cập nhật rồi chạy lại InvokeAgent.")
except Exception as e:
    print(f"❌ Lỗi: {e}")