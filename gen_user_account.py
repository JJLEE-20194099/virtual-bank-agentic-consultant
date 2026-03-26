from backend.app.clients.db import PostgresClient
import asyncio
import numpy as np
import os
import random
from urllib.parse import urlparse
database_url = os.getenv("DATABASE_URL", "postgresql://swin:swin@localhost:5432/vbac")
parsed = urlparse(database_url)

db_client = PostgresClient(
    user=parsed.username or "swin",
    password=parsed.password or "swin",
    database=parsed.path.lstrip("/") or "vbac",
    host=parsed.hostname or "postgres",
    port=parsed.port or 5432
)

async def run():

    await db_client.connect()
    await db_client.init_user_table()

    user_ids = await db_client.get_all_customer_ids()
    for user_id in user_ids:
        try:
            portfolio_data = await db_client.get_portfolio(user_id)
            total_val = portfolio_data["total_portfolio_value"]
            total_unrealized_pnl = portfolio_data["total_unrealized_pnl"]
            detail = portfolio_data["portfolio_stats"]

            symbols = list(portfolio_data["portfolio_stats"].keys())

            stock_summaries = await db_client.get_stock_summary_by_symbols(symbols)

            has_big_loss = 0
            if total_unrealized_pnl < 0 and np.abs(total_unrealized_pnl) / total_val >= 0.01:
                has_big_loss = 1
            has_bullish_stock = any(d["data"]["trend"] == "bullish" for d in stock_summaries)

            rand = random.random()

            if total_val > 100000 and rand < 0.25:
                cash_ratio = random.uniform(0.08, 0.15)
                
            elif has_big_loss and rand < 0.5:
                cash_ratio = random.uniform(0.16, 0.25)
                
            elif has_bullish_stock and rand < 0.75:
                cash_ratio = random.uniform(0.01, 0.045)
            
            else:
                cash_ratio = random.uniform(0.41, 0.60)

            available_cash = round(total_val * cash_ratio, 2)

            await db_client.insert_user(user_id, {"available_cash": available_cash})
            
        except Exception as e:
            print(e)
            print("error:", user_id)
    
if __name__ == "__main__":
    asyncio.run(run())
