"""Database engine and a connectivity probe.

F0 has no models on purpose: this module exists only so that ``/api/health`` can
prove the backend actually reaches PostgreSQL. The ORM layer and the Alembic
migrations arrive in F1, together with the domain model.

The async engine is created once at import and reused. Creating one per request
would build a fresh connection pool every time, which is the classic way to
exhaust ``max_connections`` under load.
"""

from __future__ import annotations

import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def _database_url() -> str:
    """Read DATABASE_URL, failing with an actionable message instead of KeyError."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env "
            "(the compose file passes it in via env_file)."
        )
    return url


# pool_pre_ping: the dev stack is torn down constantly (`just down`, `just
# fresh`), which leaves dead connections in the pool. Pre-ping discards them
# instead of surfacing a confusing OperationalError on the next request.
engine: AsyncEngine = create_async_engine(_database_url(), pool_pre_ping=True)


async def check_connection() -> None:
    """Round-trip a trivial query. Raises if the database is unreachable."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
