import asyncpg
import json
from typing import Any, Dict, Optional, List


class PostgresClient:
    def __init__(self, user: str, password: str, database: str, host: str = "localhost", port: int = 5432):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        self.conn = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )

    async def close(self):
        if self.conn:
            await self.conn.close()


    async def init_portfolio_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_summary (
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def save_portfolio(self, user_id: str, portfolio: Dict[str, Any]):
        await self.conn.execute("""
            INSERT INTO portfolio_summary(user_id, data)
            VALUES($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(portfolio)   
    )


    async def get_portfolio(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT data
            FROM portfolio_summary
            WHERE user_id = $1
        """, user_id)

        return json.loads(row["data"]) if row else None


    async def delete_portfolio(self, user_id: str):
        await self.conn.execute("""
            DELETE FROM portfolio_summary
            WHERE user_id = $1
        """, user_id)

    

    async def init_stock_summary_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_summary (
            symbol TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def save_stock_summary(self, symbol: str, stock_summary: Dict[str, Any]):
        await self.conn.execute("""
            INSERT INTO stock_summary(symbol, company, data)
            VALUES($1, $2, $3)
            ON CONFLICT (symbol)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        symbol,
        symbol,
        json.dumps(stock_summary)   
    )


    async def get_stock_summary(self, symbol: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT *
            FROM stock_summary
            WHERE symbol = $1
        """, symbol)

        row["data"] = json.loads(row["data"])
        return row



    async def get_stock_summary_by_symbols(self, symbols: List[str]):
        rows = await self.conn.fetch("""
            SELECT *
            FROM stock_summary
            WHERE symbol = ANY($1)
        """, symbols)

        return [{**item, "data": json.loads(item["data"])} for item in rows]



    async def delete_stock_summary(self, symbol: str):
        await self.conn.execute("""
            DELETE FROM stock_summary
            WHERE symbol = $1
        """, symbol)