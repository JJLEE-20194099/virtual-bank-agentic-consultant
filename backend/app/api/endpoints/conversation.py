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
from app.agents.core.agent_orchestrator import run_agent
import os
load_dotenv() 
from datetime import datetime
from app.storage.memory_store import save_message, load_history, build_context

from app.core.bedrock_instance import bedrock_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
service = MarketService()
market_analysis_agent = MarketAnalysisAgent()

from app.clients.cache import RedisClient
redis_client = RedisClient()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatSessionRequest(BaseModel):
    user_id: str = "C00001"
    message: str = "Đánh giá rủi ro danh mục đầu tư của tôi"
    session_id: str = "C00001"
    agent_id: str = "P4RQTQCYVA"
    agent_alias_id: str = "TSTALIASID"

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

PORTFOLIO_INTENTS = {
    "portfolio",
    "buy_sell",
    "risk",
    "allocation",
    "recommendation",
}   
def need_portfolio(intent, user_message):
    keywords = [
        "danh mục",
        "portfolio",
        "tôi đang giữ",
        "rủi ro",
        "lãi",
        "lỗ",
        "PnL",
        "nên bán",
        "nên giữ",
    ]

    return (
        intent in PORTFOLIO_INTENTS
        or any(k.lower() in user_message.lower() for k in keywords)
    )
            

@router.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message
    context = {}

    query_parser = json.loads(parse_query(user_message).replace('\\"', '"').replace("```json", "").replace("```", ""))
    symbols = query_parser["symbols"]
    intent = query_parser["intent"]
    print(intent, symbols)
    context["ohlcv"] = {}
    for external_factor in query_parser["external_factors"]:
        if external_factor["type"] == "exchange_rate":

            cache_key = f"get_exchange_rate"

            try:
                context["exchange_rate"] = redis_client.get(cache_key)
                
            except:
                tmp = service.get_exchange_rate(today_str())

                redis_client.set(
                    cache_key,
                    json.dumps(tmp, default=str),
                    ex=60 * 30
                )

                context["exchange_rate"] = tmp
        
        if external_factor["type"] == "gold":
            if external_factor["scope"] == "global":

                cache_key = f"summary:global-gold-price"

                try:
                    context["ohlcv"]["global_gold_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_global_gold_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["global_gold_price"] = tmp

                 
            else:
                cache_key = f"summary:domestic-gold-price"

                try:
                    context["ohlcv"]["domestic_gold_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_domestic_gold_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["domestic_gold_price"] = tmp
            


        if external_factor["type"] == "oil":
            if external_factor["scope"] == "global":
                cache_key = f"summary:global-oil-price"

                try:
                    context["ohlcv"]["global_oil_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_global_oil_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )


                    context["ohlcv"]["global_oil_price"] = tmp
            else:
               

                cache_key = f"summary:domestic-oil-price"

                try:
                    context["ohlcv"]["domestic_oil_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_domestic_oil_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["domestic_oil_price"] = tmp

    if len(symbols) > 0:
        if "company_info" in [factor["type"] for factor in query_parser["external_factors"]]:
            if query_parser["requires_company_data"]:
                context["company_info"] = {}
                for symbol in symbols:
                    cache_key = f"summary:company_info{symbol}"
                    try:
                        context["company_info"][symbol] = redis_client.get(cache_key)
                    except:
                        context["company_info"][symbol] = get_company_info(symbol)
                        redis_client.set(
                            cache_key,
                            json.dumps(context["company_info"][symbol], default=str),
                            ex=60 * 10
                        )
    
    
        for symbol in symbols:
            context["ohlcv"][symbol] = service.get_ohlcv_by_length(symbol, length=7, interval="1d")

    if intent == "trend" and len(symbols) == 0:
        context["ohlcv"]["OHLCV OF MARKET (VNINDEX 30)"] = service.get_ohlcv_by_length("VN30", length=14, interval="1d")


    if need_portfolio(intent, user_message):
        context["portfolio"] = get_user_context(req.user_id)
    else:
        context["portfolio"] = {}
    
    def event_stream():
        for chunk in market_analysis_agent.response_market_question(context, user_message, query_parser, "[]"):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")




@router.post("/bedrock-chat")
def chat_with_bedrock_agent(req: ChatSessionRequest):

    context = {}

    user_message = req.message

    query_parser = json.loads(parse_query(user_message).replace('\\"', '"').replace("```json", "").replace("```", ""))
    symbols = query_parser["symbols"]
    intent = query_parser["intent"]
    print(intent, symbols, query_parser)

    save_message(req.user_id, "user", user_message, query_parser, req.session_id)

    context["ohlcv"] = {}
    for external_factor in query_parser["external_factors"]:
        if external_factor["type"] == "exchange_rate":

            cache_key = f"get_exchange_rate"

            try:
                context["exchange_rate"] = redis_client.get(cache_key)
                
            except:
                tmp = service.get_exchange_rate(today_str())

                redis_client.set(
                    cache_key,
                    json.dumps(tmp, default=str),
                    ex=60 * 30
                )

                context["exchange_rate"] = tmp
        
        if external_factor["type"] == "gold":
            if external_factor["scope"] == "global":

                cache_key = f"summary:global-gold-price"

                try:
                    context["ohlcv"]["global_gold_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_global_gold_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["global_gold_price"] = tmp

                 
            else:
                cache_key = f"summary:domestic-gold-price"

                try:
                    context["ohlcv"]["domestic_gold_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_domestic_gold_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["domestic_gold_price"] = tmp
            


        if external_factor["type"] == "oil":
            if external_factor["scope"] == "global":
                cache_key = f"summary:global-oil-price"

                try:
                    context["ohlcv"]["global_oil_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_global_oil_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )


                    context["ohlcv"]["global_oil_price"] = tmp
            else:
               

                cache_key = f"summary:domestic-oil-price"

                try:
                    context["ohlcv"]["domestic_oil_price"] = redis_client.get(cache_key)
                    
                except:
                    tmp = service.get_domestic_oil_price()

                    redis_client.set(
                        cache_key,
                        json.dumps(tmp, default=str),
                        ex=60 * 10
                    )

                    context["ohlcv"]["domestic_oil_price"] = tmp

    if len(symbols) > 0:
        if "company_info" in [factor["type"] for factor in query_parser["external_factors"]]:
            if query_parser["requires_company_data"]:
                context["company_info"] = {}
                for symbol in symbols:
                    cache_key = f"summary:company_info{symbol}"
                    try:
                        context["company_info"][symbol] = redis_client.get(cache_key)
                    except:
                        context["company_info"][symbol] = get_company_info(symbol)
                        redis_client.set(
                            cache_key,
                            json.dumps(context["company_info"][symbol], default=str),
                            ex=60 * 10
                        )

                context["company_info"] = json.dumps(context["company_info"], default=str)
    
        for symbol in symbols:
            cache_key = f"ohlcv:{symbol}"
            try:
                context["ohlcv"][symbol] = redis_client.get(cache_key)
            except:
                context["ohlcv"][symbol] = json.dumps(service.get_ohlcv_by_length(symbol, length=14, interval="1d"), default=str)
                redis_client.set(
                    cache_key,
                    json.dumps(context["ohlcv"][symbol], default=str),
                    ex=60 * 15
                )
            

        

    if intent == "trend" and len(symbols) == 0:
        cache_key = f"ohlcv:vn30"
        try:
            context["ohlcv"]["OHLCV OF MARKET (VNINDEX 30)"] = redis_client.get(cache_key)
        except:
            context["ohlcv"]["OHLCV OF MARKET (VNINDEX 30)"] = json.dumps(service.get_ohlcv_by_length("VN30", length=14, interval="1d"))
            redis_client.set(
                cache_key,
                json.dumps(context["ohlcv"]["OHLCV OF MARKET (VNINDEX 30)"], default=str),
                ex=60 * 15
            )

        

    context["ohlcv"] = json.dumps(context["ohlcv"], default=str)

    if need_portfolio(intent, user_message):
        context["portfolio"] = json.dumps(get_user_context(req.user_id), default=str)
    else:
        context["portfolio"] = ""

    history = load_history(req.user_id)

    history = build_context(history)

    input_text = market_analysis_agent.enrich_user_question(context, user_message, query_parser, history)

    try:
        
        def event_stream():
            for chunk in bedrock_client.invoke_agent(
                agent_id=req.agent_id,
                agent_alias_id=req.agent_alias_id,
                session_id=req.session_id,
                input_text=input_text,
                session_state={
                    "sessionAttributes": context
                },
                user_id = req.user_id
            ):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/plain")

    except Exception as e:
        print(e)
        return {}



@router.post("/test-chat")
def test_chat(req: ChatSessionRequest):
    return bedrock_client.offline_invoke_agent(
        agent_id=req.agent_id,
        agent_alias_id=req.agent_alias_id,
        session_id=req.session_id,
        input_text=req.message,
        session_state={
            "sessionAttributes": {}
        }
    )
