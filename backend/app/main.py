"""GradRadar API.

The ``/api`` prefix lives in the app rather than being stripped by the reverse
proxy, so the same URL works through Caddy and when hitting the container
directly (``docker compose exec``) — which keeps debugging simple.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import router
from app.db import check_connection

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GradRadar API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)


@app.get("/api/health")
async def health() -> JSONResponse:
    """Report process liveness and database reachability.

    Returns 503 when the database is unreachable: the compose healthcheck curls
    this endpoint with ``-f``, so a degraded backend must not report itself
    healthy.
    """
    try:
        await check_connection()
    except Exception as exc:  # noqa: BLE001 — any failure here means "not ready"
        logger.warning("Health check could not reach the database: %s", exc)
        return JSONResponse(status_code=503, content={"ok": False, "db": "unreachable"})

    return JSONResponse(content={"ok": True, "db": "ok"})


app.include_router(router)
