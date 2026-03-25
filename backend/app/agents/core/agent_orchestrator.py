from app.storage.memory_store import save_message, load_history
from app.processor.intent_processor import detect_intent
from app.clients.bedrock import BedrockClient
from app.agents.bedrock_agent import AGENT_ID, AGENT_ALIAS
import json

bedrock_client = BedrockClient()


def build_context(history):
    return "\n".join([
        f"{h['role']['S']}: {h['message']['S']}"
        for h in history
    ])


def run_agent(user_id: str, message: str, session_id: str):

    save_message(user_id, "user", message, session_id)
    intent = detect_intent(message)

    data = None
    if intent["intent"] == "portfolio":
        data = {
            "user_id": user_id,
            "portfolio": {"VIC": 1}
        }

    history = load_history(user_id)
    context = build_context(history)

    response = bedrock_client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS,
        sessionId=session_id,
        inputText=json.dumps({
            "context": context,
            "intent": intent,
            "data": data,
            "user_message": message
        })
    )

    result = ""
    for e in response["completion"]:
        if "chunk" in e:
            result += e["chunk"]["bytes"].decode()

    save_message(user_id, "assistant", result, session_id)

    return result