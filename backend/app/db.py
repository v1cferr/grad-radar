"""Database engine, session factory and the declarative base.

The async engine is created once at import and reused: one engine per process,
one connection pool. Creating an engine per request is the classic way to
exhaust ``max_connections``.

There is deliberately **no** ``metadata.create_all()`` anywhere in this package.
Schema changes go through Alembic, always — a table that appears because the app
booted is a table nobody reviewed.
"""

from __future__ import annotations

import os

from sqlalchemy import Enum as SAEnum
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base shared by every model. Alembic autogenerate reads its metadata."""


def database_url() -> str:
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
engine: AsyncEngine = create_async_engine(database_url(), pool_pre_ping=True)

Session = async_sessionmaker(engine, expire_on_commit=False)


async def check_connection() -> None:
    """Round-trip a trivial query. Raises if the database is unreachable."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


def pg_enum(py_enum: type, name: str) -> SAEnum:
    """A PostgreSQL ENUM that stores the member VALUE, not its Python name.

    Without ``values_callable`` SQLAlchemy persists ``PERMANENT`` while the API
    serialises ``permanent`` — the same fact spelled two ways depending on where
    you look. Raw SQL should read like the JSON.
    """
    return SAEnum(py_enum, name=name, values_callable=lambda e: [m.value for m in e])
