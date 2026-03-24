from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.user import StockUserBehaviourBase
import requests
from tasks import update_stock_product_recommendation
from app.agents.market_analysis_agent import MarketAnalysisAgent
from app.core.data_instance import data_client
from app.utils.clean import clean_financial_data
from app.utils.stock import generate_question_set
market_analysis_agent = MarketAnalysisAgent()

router = APIRouter()
service = MarketService()


def score_new_stock(stock, PREFERRED_SECTORS, MARKET_TREND):
    score = 0
    if stock["sector"] in PREFERRED_SECTORS:
        score += 2
    else:
        score -= 0.5  

    pe = stock["pe_ratio"]
    if pe < 8:
        score += 3
    elif pe < 15:
        score += 2
    elif pe < 25:
        score += 0.5
    else:
        score -= 2


    profit = stock["profit_before_tax_billion_vnd"]
    if profit > 10000:
        score += 2
    elif profit > 3000:
        score += 1

    cap = stock["market_cap_billion_vnd"]
    try:
        if cap > 100000:
            score += 2
        elif cap > 30000:
            score += 1
    except:pass

    div = stock["dividend_yield_percent"]
    try:
        if div >= 6:
            score += 3
        elif div >= 4:
            score += 2
        elif div >= 2:
            score += 1
    except:pass
    if MARKET_TREND == "bearish":
        try:
            if div >= 4:
                score += 1
        except:pass
        try:
            if pe < 10:
                score += 1
        except:pass
        try:
            if cap > 50000:
                score += 1
        except:pass

    return score

def recommend_new_stocks(stock_list, my_stocks, PREFERRED_SECTORS, MARKET_TREND):
    results = []

    for symbol in stock_list.keys():
        if symbol in my_stocks:
            continue
        stock = stock_list[symbol]
        s = score_new_stock(stock, PREFERRED_SECTORS, MARKET_TREND)

        results.append({
            "name": stock["name"],
            "sector": stock["sector"],
            "pe": stock["pe_ratio"],
            "dividend": stock["dividend_yield_percent"],
            "score": round(s, 2),
            "symbol": symbol
        })

    df = pd.DataFrame(results)
    df = df.sort_values(by="score", ascending=False)

    def label(score):
        if score >= 8:
            return "STRONG BUY"
        elif score >= 5:
            return "BUY"
        elif score >= 2:
            return "WATCHLIST"
        else:
            return "SKIP"

    df["recommendation"] = df["score"].apply(label)

    df = df[df["recommendation"] == "STRONG BUY"]

    return df.to_dict(orient="records")


@router.get(("/summary/{user_id}"))
async def get_stocks_portfolio_summary_by_user_id(user_id: str):
    portfolio_summary = await db_client.get_portfolio(user_id)

    user_summary = await db_client.get_user(user_id)

    symbols = list(portfolio_summary["portfolio_stats"].keys())

    market_summary = await db_client.get_stock_summary_by_symbols(["VN30"])


    if len(symbols) == 0:
        return {
            "market-news": market_summary[0]["data"]
        }

    stock_summaries = await db_client.get_stock_summary_by_symbols(symbols)


    keys = [
        item["symbol"] for item in stock_summaries
    ]

   

    data = [
        {
            "key": key,
            "unrealized_pnl": portfolio_summary["portfolio_stats"][key]["unrealized_pnl"]
        }
        for key in keys
    ]

    df = pd.DataFrame(data)

    df = df.sort_values(by="unrealized_pnl", ascending=True)

    try:
        df["risk_rank"] = pd.qcut(
            df["unrealized_pnl"],
            10,
            labels=range(10, 0, -1)
        )

        overall_risk = df["risk_rank"].astype(int).mean()

        risk_rank = dict(zip(df["key"].values.tolist(), df["risk_rank"].astype(int).values.tolist()))
    except:
        m = df["unrealized_pnl"].mean()
        if m < 0:
            overall_risk = 7
            risk_rank = dict(zip(df["key"].values.tolist(), [overall_risk for _ in range(len(keys))]))
        else:
            overall_risk = 3
            risk_rank = dict(zip(df["key"].values.tolist(), [overall_risk for _ in range(len(keys))]))




    company_summary = [
       json.load(open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{key}/summary.json", "r", encoding="utf-8")) for key in keys
    ]

    values = [
        {
            "risk": risk_rank[key],
            "stock_summary": stock_summaries[i],
            "portfolio_summary": portfolio_summary["portfolio_stats"][key],
            "company_summary": company_summary[i]
        }
        for i, key in enumerate(keys)
    ]

    del portfolio_summary["portfolio_stats"]

    data = {
        "market-news": market_summary[0]["data"],
        "overall": {
            **portfolio_summary,
            **user_summary,
            "cash_ratio": user_summary["available_cash"] / (portfolio_summary["total_portfolio_value"] + user_summary["available_cash"]),
            "total_money": portfolio_summary["total_portfolio_value"] + user_summary["available_cash"],
            "overall_risk": overall_risk
        },
        "detail": dict(zip(keys, values))
    }

    PREFERRED_SECTORS = data["overall"]["preferred_categories"]
    MARKET_TREND = data["market-news"]["trend"]

    company_summaries = data_client.company_summaries
    company_analysis = data_client.company_analysis

    recommend_data = recommend_new_stocks(company_summaries, keys, PREFERRED_SECTORS, MARKET_TREND)

    recommend_data = clean_financial_data(recommend_data)

    recommend_data = [{**item, **(company_analysis[item["symbol"]])} for item in recommend_data]

    return {
        **data,
        "recommend_data": recommend_data
    }


@router.get(("/behaviour/{user_id}"))
async def get_stock_behaviour_by_user_id(user_id: str):
    stock_user_behaviour = await db_client.get_stock_user_behaviour(user_id)

    return stock_user_behaviour

@router.get(("/recommend/{user_id}"))
async def get_stock_product_recommendation(user_id: str):
    data = await db_client.get_stock_product_recommendation(user_id)

    return data

@router.post(("/recommend/{user_id}"))
async def create_recommendation(user_id: str):
    update_stock_product_recommendation.delay({"customer_id": user_id})


@router.post(("/question-list/{user_id}"))
async def get_question_recommendation_by_user_id(user_id: str):
    symbols = await db_client.get_unique_stock_codes(user_id)

    return generate_question_set(symbols)



@router.get(("/analyze/{user_id}"))
async def analyze_stock_portfolio(user_id: str):

    data = await db_client.get_portfolio_advice(user_id)
    
    if data != None:
        return data
    
    user_portfolio_data = await get_stocks_portfolio_summary_by_user_id(user_id)

    portfolio_advice = market_analysis_agent.analyze_stock_portfolio(user_portfolio_data)

    await db_client.save_portfolio_advice(user_id, portfolio_advice)
    return portfolio_advice






@router.post(("/behaviour/create"))
async def save_stock_behaviour(payload: StockUserBehaviourBase):
    data = payload.model_dump()
    await db_client.save_stock_user_behaviour(data["customer_id"], data["behaviour_data"])

    return {"status": "ok"}



@router.post("/behaviour/delete-table/")
async def delete_stock_user_behaviour_table():
    await db_client.delete_stock_user_behaviour_table()

@router.post("/behaviour/delete/{user_id}")
async def delete_stock_user_behaviour(user_id: str):
    await db_client.delete_stock_user_behaviour(user_id = user_id)
    return {"status": "ok"}



@router.get("/list/")
async def get_all_customer_ids():
    return await db_client.get_all_customer_ids()
    


@router.post("/delete/")
async def delete_user_table():
    return await db_client.delete_user_table()
    
