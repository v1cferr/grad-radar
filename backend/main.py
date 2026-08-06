"""GradRadar backend — F0 smoke-test skeleton.

Exposes exactly ONE endpoint, ``GET /api/health``. Its job is to prove the
infrastructure works end to end: Caddy routes ``/api/*`` to this process, and
this process can reach PostgreSQL. There are no domain models, no CRUD and no
migrations yet — those are F1.

WHY the ``/api`` prefix lives in the app instead of being stripped by Caddy: the
same URL then works both through Caddy and when hitting the container directly
(``docker compose exec``), which keeps debugging simple. The OpenAPI docs are
moved under the same prefix for the same reason.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from db import check_connection

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GradRadar API",
    version="0.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)


@app.get("/api/health")
async def health() -> JSONResponse:
    """Report process liveness and database reachability.

    Returns 503 when the database is unreachable: the compose healthcheck curls
    this endpoint with ``-f``, so a degraded backend must not report itself
    healthy. Any driver exception counts as "not ready" — distinguishing the
    failure modes is not useful to a healthcheck.
    """
    try:
        await check_connection()
    except Exception as exc:  # noqa: BLE001 — any failure here means "not ready"
        logger.warning("Health check could not reach the database: %s", exc)
        return JSONResponse(status_code=503, content={"ok": False, "db": "unreachable"})

    return JSONResponse(content={"ok": True, "db": "ok"})
