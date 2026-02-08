from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
import os
import pandas as pd
import json
import ast

router = APIRouter()

def fetch_from_postgres(user_id):
    return None

DATA_PATH = "app/data/raw/transactions.csv"

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
