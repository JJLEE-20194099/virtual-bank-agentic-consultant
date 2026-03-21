import asyncpg
import json
from typing import Any, Dict, Optional


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