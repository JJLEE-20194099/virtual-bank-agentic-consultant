from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
import os
import pandas as pd
import json
import ast
import sqlite3
import uuid

from app.service.feature_engine.job import run_feature_job
from app.agents.ai_orchestrator_agent.orchestrator import run_consultant

router = APIRouter()

DATA_PATH = "app/data/raw/transactions.csv"
DB_PATH = "app/storage/transactions.db"


class TransactionEvent(BaseModel):
    user_id: str
    type: str 
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    trx_time: Optional[datetime] = None


@router.get("/{user_id}")
def get_transactions(
    user_id: str,
    from_date: str = Query(..., alias="from", example="2025-12-30"),
    to_date: str = Query(..., alias="to", example="2026-02-06")
):
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Transactions data not found")

    
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format must be YYYY-MM-DD")

    df = pd.read_csv(DATA_PATH)

    df["trx_time"] = pd.to_datetime(df["trx_time"])
    result = df[
        (df["user_id"] == user_id) &
        (df["trx_time"] >= from_dt) &
        (df["trx_time"] <= to_dt)
    ]

    if len(result) == 0:
        return {
            "user_id": user_id,
            "total_transactions": 0,
            "transactions": []
        }

    def parse_installment(x):
        if pd.isna(x):
            return None
        try:
            return json.loads(x)
        except Exception:
            return ast.literal_eval(x)

    if "installment" in result.columns:
        result["installment"] = result["installment"].apply(parse_installment)
    
    return {
        "user_id": user_id,
        "from": from_date,
        "to": to_date,
        "total_transactions": len(result),
        "transactions": result.to_dict(orient="records")
    }


@router.post("/trigger")
def trigger_transaction(event: TransactionEvent):
   
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

   
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            trx_id TEXT PRIMARY KEY,
            user_id TEXT,
            type TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            trx_time TEXT,
            created_at TEXT
        )
        """
    )

    trx_time = event.trx_time or datetime.utcnow()
    cursor.execute(
        "INSERT OR REPLACE INTO transactions (trx_id, user_id, type, amount, category, description, trx_time, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            event.user_id,
            event.type,
            event.amount,
            event.category,
            event.description,
            trx_time.isoformat(),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    run_feature_job()

    result = run_consultant(
        user_id=event.user_id,
        query=None,
        intent_score=None,
        is_transaction_trigger=True,
    )

    return {
        "status": "ok",
        "user_id": event.user_id,
        "transaction": event.dict(),
        "result": result,
    }
