from fastapi import APIRouter
from pydantic import BaseModel
from app.service.intent.engine import classify_intent
from app.agents.ai_orchestrator_agent.orchestrator import run_consultant


router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    # Classify intent to decide which agent path to follow.
    intent = classify_intent(req.message)

    result = run_consultant(
        user_id=req.user_id,
        query=req.message,
        intent_score=intent.get("score"),
        is_transaction_trigger=False,
    )

    return {
        "intent": intent,
        "result": result
    }
