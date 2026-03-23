from fastapi import FastAPI, WebSocket
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.db_instance import db_client
from app.core.model_instance import model_client
from contextlib import asynccontextmanager

loaded_model = None
loaded_scaler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    await db_client.init_portfolio_table()
    await db_client.init_stock_transactions_table()
    await db_client.init_stock_user_behaviour_table()
    await db_client.init_user_table()
    await db_client.init_stock_product_recommendation_table()

    print("DB CONNECTED")

    model_client.load()
    print("MODEL LOADED")

    yield

    await db_client.close()
    print("DB CLOSED")

app = FastAPI(
    title="VBAC API",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
 