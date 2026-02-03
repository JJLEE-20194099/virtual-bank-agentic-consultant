from fastapi import FastAPI, WebSocket
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VBAC API",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
 