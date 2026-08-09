"""Test fixtures.

Three layers, each answering a different question:

* **unit** (`test_domain_rules.py`) — pure functions, no I/O. Milliseconds.
* **integration** (this file's fixtures) — the real FastAPI app against the real
  PostgreSQL, driven in-process by httpx's ASGITransport. No server, no socket.
* **e2e** — a browser against the running stack. Playwright's job, not pytest's.

The session below is bound to a transaction that is **always rolled back**, so a
test can write freely and leave nothing behind. `join_transaction_mode` is the
load-bearing detail: without `create_savepoint`, a `commit()` inside the code
under test would end the outer transaction and the rollback would have nothing
left to undo.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import get_session
from app.db import Session, engine
from app.main import app
from app.models import GraduateProgram
from app.seed import seed


@pytest.fixture(scope="session")
async def seeded() -> None:
    """Guarantee the verified PPGCC data exists.

    The seed is idempotent, so running it here is cheap and makes the suite
    self-sufficient instead of silently depending on whoever ran `just seed`
    last.
    """
    async with Session() as db:
        count = await db.scalar(select(func.count()).select_from(GraduateProgram))
        if not count:
            await seed(db)


@pytest.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
async def client(db: AsyncSession, seeded: None) -> AsyncIterator[AsyncClient]:
    """The real app, in-process. Every request runs in the rolled-back session."""
    app.dependency_overrides[get_session] = lambda: db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as http:
            yield http
    finally:
        app.dependency_overrides.clear()
