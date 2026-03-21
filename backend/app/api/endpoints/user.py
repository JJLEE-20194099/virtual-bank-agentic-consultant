from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client


router = APIRouter()
service = MarketService()

@router.get(("/summary/{user_id}"))
async def get_stocks_by_user_id(user_id: str):
    return await db_client.get_portfolio(user_id)

