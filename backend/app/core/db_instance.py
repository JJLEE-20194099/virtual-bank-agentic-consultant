import os

from app.clients.db import PostgresClient

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