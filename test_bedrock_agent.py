

import boto3
from backend.app.clients.bedrock import BedrockClient


bedrock_client = BedrockClient(roleArn = "arn:aws:iam::436756555762:role/AmazonBedrockExecutionRole")

def test_create_bedrock_agent():
    result = bedrock_client.create_full_agent(
        name="intent-agent-test",
        instruction="""
        You are an intent classifier.
        Return JSON only:
        {
        "intent": "...",
        "entities": {}
        }
        """,
        description="Agent that classifies user intent into structured JSON",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        alias_name = "staging"
    )

    return result

# agent_info = test_create_bedrock_agent()
# print(agent_info)
# print(bedrock_client.list_agent_aliases("JPWBPQC7BD"))
# bedrock_client.delete_agent_alias(agent_id = "MY86RM1MVM", agent_alias_id = "NHEAKSQBBJ")
# bedrock_client.delete_agent(agent_id = "JPWBPQC7BD")

agent_info = {'agent_id': 'ZDPA8A7OQA', 'alias_id': 'SIJVNYM0M0'}
message = "Tôi muốn đầu tư chứng khoán"
response = bedrock_client.invoke_agent(
    agent_id=agent_info["agent_id"],
    agent_alias_id=agent_info["alias_id"],
    session_id="intent-session",
    input_text=f"""
        Return JSON only:
        {{
        "intent": "...",
        "entities": {{}}
        }}

        User: {message}
        """
    )

print(response)

 








