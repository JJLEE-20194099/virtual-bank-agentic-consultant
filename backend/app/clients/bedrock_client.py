import boto3

bedrock_runtime = boto3.client("bedrock-agent-runtime")
bedrock_agent = boto3.client("bedrock-agent")