"""API router configuration."""
from fastapi import APIRouter
from app.api.endpoints import transaction, conversation

api_router = APIRouter()

api_router.include_router(
    transaction.router,
    prefix="/transaction",
    tags=["transaction"]
)


api_router.include_router(
    conversation.router,
    prefix="/conversation",
    tags=["conversation"]
)

