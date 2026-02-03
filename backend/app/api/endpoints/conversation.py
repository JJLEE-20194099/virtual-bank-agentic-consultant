from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.ai_orchestrator_agent.orchestrator import run_consultant


router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    result = run_consultant(req.user_id)
    return {
        "reply": result
    }    