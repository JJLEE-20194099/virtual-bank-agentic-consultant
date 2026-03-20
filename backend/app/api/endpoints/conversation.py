from fastapi import APIRouter
from pydantic import BaseModel
from app.service.intent.engine import classify_intent
from app.service.finance.market.market_service import MarketService
from app.service.finance.market.company_service import get_company_info
from openai import OpenAI
from dotenv import load_dotenv
from app.agents.market_analysis_agent import MarketAnalysisAgent
import os
load_dotenv() 
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
service = MarketService()
market_analysis_agent = MarketAnalysisAgent()

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

@router.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message
    context = {}

    query_parser = parse_query(user_message)

    symbols = query_parser["symbols"]
    intent = query_parser["intent"]
    context["ohlcv"] = {}
    for external_factor in query_parser["external_factors"]:
        if external_factor["type"] == "exchange_rate":
            context["exchange_rate"] = service.get_exchange_rate(today_str())
        if external_factor["type"] == "interest_rate":
            context["interest_rate"] = service.get_interest_rate(today_str())
        
        if external_factor["type"] == "gold":
            if external_factor["scope"] == "domestic":
                context["ohlcv"]["domestic_gold_price"] = {
                    "today": service.get_domestic_gold_price(today_str()),
                    "history": service.get_domestic_gold_price_history(length=7)
                }
            elif external_factor["scope"] == "global":
                context["ohlcv"]["global_gold_price"] = {
                    "today": service.get_global_gold_price(today_str()),
                    "history": service.get_global_gold_price_history(length=7)
                }

        if external_factor["type"] == "oil":
            if external_factor["scope"] == "domestic":
                context["ohlcv"]["domestic_oil_price"] = {
                    "today": service.get_domestic_oil_price(today_str()),
                    "history": service.get_domestic_oil_price_history(length=7)
                }
            elif external_factor["scope"] == "global":
                context["ohlcv"]["global_oil_price"] = {
                    "today": service.get_global_oil_price(today_str()),
                    "history": service.get_global_oil_price_history(length=7)
                }

    if len(symbols) > 0:
        if "company_info" in [factor["type"] for factor in query_parser["external_factors"]]:
            if query_parser["requires_company_data"]:
                context["company_info"] = {}
                for symbol in symbols:
                    context["company_info"][symbol] = get_company_info(symbol)
    
    
        for symbol in symbols:
            context["ohlcv"][symbol] = service.get_ohlcv_by_length(symbol, length=7, interval="1d")


    return context
