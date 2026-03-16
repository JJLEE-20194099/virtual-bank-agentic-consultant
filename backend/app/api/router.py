"""API router configuration."""
from fastapi import APIRouter
from app.api.endpoints import transaction, conversation, market, company

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

api_router.include_router(
    market.router,
    prefix="/market",
    tags=["market"]
)

api_router.include_router(
    company.router,
    prefix="/company",
    tags=["company"]
)

