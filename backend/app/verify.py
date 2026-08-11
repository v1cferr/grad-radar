"""Re-derivar o requisito de horário a partir do que o monitor já baixou.

    python -m app.verify            # relata
    python -m app.verify --apply    # grava o que estiver diferente

É a peça que tira a leitura manual do circuito. O coletor já guarda o texto de
cada documento; o extrator já sabe decidir; faltava alguém comparar o que o
documento diz HOJE com o que está gravado no banco.

Quando a grade de 2027/1 sair, isto responde "o PPGCC passou a ter faixa às 19h"
sem ninguém abrir PDF — que é exatamente a pergunta que custou seis leituras
manuais.

**O default é relatar, não gravar.** Discordância entre o extrator e o banco é
informação: pode ser grade nova (ótimo), pode ser o extrator errando num formato
inédito (ruim). Sobrescrever em silêncio impediria de distinguir os dois, e o
segundo caso é o que corrompe a decisão.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import Session
from app.extract import evening_offer, is_error_page
from app.models import (
    ProgramRequirement,
    Requirement,
    RequirementStatus,
    Source,
    SourceSnapshot,
    SourceType,
)

# Só documentos que descrevem OFERTA. Um edital diz o que pode acontecer; a grade
# diz o que acontece — e a diferença entre os dois foi o erro do MECAI.
SCHEDULE_TYPES = (SourceType.SCHEDULE_PDF, SourceType.COURSE_CATALOG)


async def _latest_text(db: AsyncSession, source_id: int) -> tuple[str | None, datetime | None]:
    snap = (
        await db.scalars(
            select(SourceSnapshot)
            .where(SourceSnapshot.source_id == source_id, SourceSnapshot.text.isnot(None))
            .order_by(SourceSnapshot.retrieved_at.desc())
            .limit(1)
        )
    ).first()
    return (snap.text, snap.retrieved_at) if snap else (None, None)


async def run(db: AsyncSession, apply: bool) -> int:
    sources = (
        await db.scalars(
            select(Source)
            .options(selectinload(Source.program))
            .where(Source.source_type.in_(SCHEDULE_TYPES), Source.program_id.isnot(None))
            .order_by(Source.id)
        )
    ).all()

    disagreements = 0
    for source in sources:
        text, when = await _latest_text(db, source.id)
        program = source.program
        if not text:
            print(f"  sem snapshot  {program.acronym:<8} {source.title}")
            continue
        if is_error_page(text):
            # A armadilha do soft 404: HTTP 200 com página de erro. Nunca deixar
            # isso virar veredito.
            print(f"  ⚠ ERRO 200    {program.acronym:<8} {source.title}")
            print("                a fonte devolve página de erro com HTTP 200 — URL mudou?")
            disagreements += 1
            continue

        offer = evening_offer(text)
        stored = (
            await db.scalars(
                select(ProgramRequirement).where(
                    ProgramRequirement.program_id == program.id,
                    ProgramRequirement.requirement == Requirement.EVENING_CLASSES,
                )
            )
        ).first()

        # `unknown` do extrator NÃO é discordância: é ausência de dado. Um
        # catálogo que lista disciplinas sem horário não contradiz um veredito
        # verificado — só não tem o que dizer. Tratar como divergência enchia o
        # relatório de ruído e escondia a única linha que importa.
        if offer.status is RequirementStatus.UNKNOWN:
            # Duas coisas diferentes caem em UNKNOWN e não devem ler igual: um
            # catálogo sem horário nenhum, e uma grade com faixas noturnas em
            # minoria (o caso da EESC/USP). A segunda é uma pergunta a fazer; a
            # primeira é só ausência de dado.
            if offer.bands:
                print(f"  inconclusivo  {program.acronym:<8} ({when:%d/%m} · {source.title})")
                print(f"                {offer.evidence}")
            else:
                print(f"  sem horário   {program.acronym:<8} ({when:%d/%m} · {source.title})")
            continue

        agrees = stored is not None and stored.status is offer.status
        print(
            f"  {'ok' if agrees else 'DIVERGE':<12}  {program.acronym:<8} "
            f"extrator={offer.status.value:<8} banco={stored.status.value if stored else '—':<8} "
            f"({when:%d/%m} · {source.title})"
        )
        if agrees:
            continue

        disagreements += 1
        print(f"                {offer.evidence}")
        if apply and stored is not None:
            stored.status = offer.status
            stored.evidence = offer.evidence
            stored.source_id = source.id
            stored.verified_on = date.today()  # noqa: DTZ011 — data civil
            print("                → gravado")

    if apply:
        await db.commit()
    return disagreements


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="gravar os vereditos divergentes no banco (default: só relatar)",
    )
    args = parser.parse_args()

    async with Session() as db:
        n = await run(db, args.apply)

    stamp = datetime.now(UTC).strftime("%d/%m %H:%M")
    print(f"\n  {n} divergência(s) · {stamp}")
    if n and not args.apply:
        print("  Confira a evidência acima antes de rodar com --apply.")
    elif not n:
        print("  Todo documento com horário concorda com o banco.")


if __name__ == "__main__":
    asyncio.run(main())
