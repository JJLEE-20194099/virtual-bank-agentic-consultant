from app.clients.bedrock import BedrockClient
import json

def detect_intent(message: str):
    response = bedrock_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS,
        sessionId="intent-session",
        inputText=f"""
            Return JSON only:
            {{
            "intent": "...",
            "entities": {{}}
            }}

            User: {message}
            """
        )

    result = ""
    for e in response["completion"]:
        if "chunk" in e:
            result += e["chunk"]["bytes"].decode()

    return json.loads(result)