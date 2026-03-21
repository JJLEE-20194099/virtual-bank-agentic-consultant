"""API router configuration."""
from fastapi import APIRouter
from app.api.endpoints import transaction, conversation, market, company, user, stock_transaction

api_router = APIRouter()


api_router.include_router(
    stock_transaction.router,
    prefix="/stock",
    tags=["stock"]
)


api_router.include_router(
    user.router,
    prefix="/user",
    tags=["user"]
)

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

