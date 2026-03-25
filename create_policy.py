import boto3
import json

iam = boto3.client("iam")

ROLE_NAME = "AmazonBedrockExecutionRole"
USER_NAME = "sen404"

iam.put_user_policy(
    UserName="sen404",
    PolicyName="AssumeBedrockRole",
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::436756555762:role/AmazonBedrockExecutionRole"
        }]
    })
)

iam.put_role_policy(
    RoleName="AmazonBedrockExecutionRole",
    PolicyName="BedrockAccess",
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeAgent",
                "bedrock-agent-runtime:*"
            ],
            "Resource": "*"
        }]
    })
)

iam.update_assume_role_policy(
    RoleName="AmazonBedrockExecutionRole",
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    })
)

\