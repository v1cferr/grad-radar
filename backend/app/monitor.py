"""Check every active source and record what it said.

Run one pass:  ``python -m app.monitor``  (or ``just monitor``)

Deliberately a **single pass**, not a daemon. The schedule belongs outside the
process — a systemd timer or a cron entry can be declared, inspected and disabled
without touching this code, and a scheduler living inside the API process would
die with the container. `restart: "no"` in the dev compose is on purpose, so a
long-lived in-process loop would silently stop watching after any reboot.

What counts as a change is decided in app/collector.py: the hash is over the
extracted TEXT. Comparing raw bytes would mark a regenerated PDF as new every
single run, and a monitor that cries wolf is one nobody reads.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collector import TIMEOUT, USER_AGENT, Fetched, fetch
from app.db import Session
from app.models import Source, SourceSnapshot


async def _previous_hash(db: AsyncSession, source_id: int) -> str | None:
    stmt = (
        select(SourceSnapshot.content_hash)
        .where(SourceSnapshot.source_id == source_id, SourceSnapshot.error.is_(None))
        .order_by(SourceSnapshot.retrieved_at.desc())
        .limit(1)
    )
    return await db.scalar(stmt)


async def check_source(db: AsyncSession, source: Source, client: httpx.AsyncClient) -> SourceSnapshot:
    result: Fetched = await fetch(source.url, client)
    previous = await _previous_hash(db, source.id)

    # First sight is never a "change": there is nothing to have changed from, and
    # reporting it as one would make the first run alert on every source at once.
    changed = bool(result.ok and previous is not None and previous != result.content_hash)

    snapshot = SourceSnapshot(
        source_id=source.id,
        retrieved_at=datetime.now(UTC),
        content_hash=result.content_hash or None,
        http_status=result.http_status or None,
        text=result.text or None,
        final_url=result.final_url,
        content_type=result.content_type or None,
        changed=changed,
        error=result.error,
        # Recorded, not hidden: a change flagged on a byte hash deserves a human
        # look before anyone acts on it.
        notes=None if result.text_extractable else "hash sobre bytes (PDF sem camada de texto)",
    )
    db.add(snapshot)

    # last_checked_at moves even on failure: "we tried and could not reach it" is
    # different from "we never looked", and only the first is recoverable by
    # retrying later.
    source.last_checked_at = snapshot.retrieved_at
    if result.redirected and result.final_url != source.url:
        source.redirects_to = result.final_url

    return snapshot


async def run_once(db: AsyncSession) -> list[tuple[Source, SourceSnapshot]]:
    sources = (await db.scalars(select(Source).where(Source.active.is_(True)))).all()
    out: list[tuple[Source, SourceSnapshot]] = []
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}
    ) as client:
        for source in sources:
            out.append((source, await check_source(db, source, client)))
    await db.commit()
    return out


async def main() -> None:
    parser = argparse.ArgumentParser(description="Check monitored sources once.")
    parser.add_argument("--quiet", action="store_true", help="only report changes and failures")
    args = parser.parse_args()

    async with Session() as db:
        results = await run_once(db)

    changed = [s for _, s in results if s.changed]
    failed = [(src, s) for src, s in results if s.error]

    for source, snap in results:
        if args.quiet and not snap.changed and not snap.error:
            continue
        if snap.error:
            mark, detail = "ERRO ", snap.error[:70]
        elif snap.changed:
            basis = " (bytes)" if snap.notes else ""
            mark, detail = "MUDOU", f"{len(snap.text or '')} chars{basis} · {snap.content_hash[:12]}"
        else:
            mark, detail = "igual", f"{len(snap.text or '')} chars"
        print(f"  {mark}  {source.title or source.url}\n         {detail}")

    print(
        f"\n  {len(results)} fonte(s) · {len(changed)} mudança(s) · {len(failed)} falha(s)"
    )


if __name__ == "__main__":
    asyncio.run(main())
