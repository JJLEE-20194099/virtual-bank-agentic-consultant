from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.user import StockUserBehaviourBase


router = APIRouter()
service = MarketService()

@router.get(("/summary/{user_id}"))
async def get_stocks_portfolio_summary_by_user_id(user_id: str):
    portfolio_summary = await db_client.get_portfolio(user_id)

    user_summary = await db_client.get_user(user_id)

    symbols = list(portfolio_summary["portfolio_stats"].keys())

    stock_summaries = await db_client.get_stock_summary_by_symbols(symbols)

    market_summary = await db_client.get_stock_summary_by_symbols(["VN30"])


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

    return {
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


@router.get(("/behaviour/{user_id}"))
async def get_stock_behaviour_by_user_id(user_id: str):
    stock_user_behaviour = await db_client.get_stock_user_behaviour(user_id)

    return stock_user_behaviour

@router.get(("/recommend/{user_id}"))
async def get_stock_product_recommendation(user_id: str):
    data = await db_client.get_stock_product_recommendation(user_id)

    return data




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
    
