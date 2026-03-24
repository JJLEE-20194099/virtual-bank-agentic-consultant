from fastapi import APIRouter
from pydantic import BaseModel
import requests
from app.service.intent.engine import classify_intent
from app.service.finance.market.market_service import MarketService
from app.service.finance.market.company_service import get_company_info
from openai import OpenAI
import json
from dotenv import load_dotenv
from app.agents.market_analysis_agent import MarketAnalysisAgent
from fastapi.responses import StreamingResponse
import os
load_dotenv() 
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
service = MarketService()
market_analysis_agent = MarketAnalysisAgent()

from app.clients.cache import RedisClient
redis_client = RedisClient()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: dict
    context: dict

def parse_query(message: str):
    return market_analysis_agent.analyse_market_question(message)

def today_str():
    return datetime.today().strftime("%Y-%m-%d")

def load_company_info(symbol):
    return get_company_info(symbol)

def get_user_context(user_id:str):
    cache_key = f"user_context:{user_id}"
    
    try:
        cached = redis_client.get(cache_key)
        return cached
    except Exception as e:
        print(e)
        res = requests.get(f"http://localhost:8080/api/v1/user/summary/{user_id}")
        if res.status_code == 200:
            user_context = res.json()

            redis_client.set(
                cache_key,
                json.dumps(user_context),
                ex=60 * 5
            )

            return user_context
            

@router.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message
    context = {}

    query_parser = json.loads(parse_query(user_message).replace('\\"', '"').replace("```json", "").replace("```", ""))
    symbols = query_parser["symbols"]
    intent = query_parser["intent"]
    context["ohlcv"] = {}
    for external_factor in query_parser["external_factors"]:
        if external_factor["type"] == "exchange_rate":
            context["exchange_rate"] = service.get_exchange_rate(today_str())
        
        if external_factor["type"] == "gold":
            if external_factor["scope"] == "global":
                context["ohlcv"]["global_gold_price"] = service.get_global_gold_price()
            else:
                context["ohlcv"]["domestic_gold_price"] = service.get_domestic_gold_price()
            


        if external_factor["type"] == "oil":
            if external_factor["scope"] == "global":
                context["ohlcv"]["global_oil_price"] = service.get_global_oil_price()
            else:
                context["ohlcv"]["domestic_oil_price"] = service.get_domestic_oil_price()

    if len(symbols) > 0:
        if "company_info" in [factor["type"] for factor in query_parser["external_factors"]]:
            if query_parser["requires_company_data"]:
                context["company_info"] = {}
                for symbol in symbols:
                    context["company_info"][symbol] = get_company_info(symbol)
    
    
        for symbol in symbols:
            context["ohlcv"][symbol] = service.get_ohlcv_by_length(symbol, length=7, interval="1d")


    context["portfolio"] = get_user_context(req.user_id)
    
    def event_stream():
        for chunk in market_analysis_agent.response_market_question(context, user_message, query_parser):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")


