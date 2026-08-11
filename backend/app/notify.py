"""Avisar as pessoas. É o passo que faltava para o monitor servir de algo.

    python -m app.notify              # computa, envia e grava
    python -m app.notify --dry-run    # mostra o que enviaria

O monitor achou o Edital 01/2026 do PPGAdS em 10/08/2026 e ninguém soube. Eu só vi
porque fui olhar o diff à mão. Um monitor que detecta e não avisa é quase o problema
original de volta, só com mais passos.

**O que NÃO é notificado, e por quê.** Não existe evento "conteúdo mudou". O hash de
uma página muda por motivo nenhum — contador de visitas, PDF regerado, banner
rotativo — e um canal que avisa disso ensina a ignorar o canal. Depois do terceiro
alerta inútil, o quarto não é lido, e o que estava no quarto era o edital.

Então os eventos são cinco, e cada um responde a "isso faz alguém agir?":

| Evento | Faz agir porque |
| --- | --- |
| `cycle_open` | apareceu processo que dá para fazer |
| `deadline_soon` | o prazo está chegando e o projeto leva semanas |
| `notice_changed` | o EDITAL mudou — retificação muda regra |
| `source_blind` | paramos de conseguir ver uma fonte; o silêncio virou cegueira |
| `schedule_verdict` | a grade mudou o veredito de horário — pode ter aberto noturno |

O último é o mais valioso do projeto: é ele que avisa se o PPGCC passar a oferecer
aula à noite.
"""

from __future__ import annotations

import argparse
import asyncio
import difflib
import hashlib
import os
import re
import smtplib
from dataclasses import dataclass
from datetime import UTC, date, datetime
from email.message import EmailMessage

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.collector import TIMEOUT, USER_AGENT
from app.db import Session
from app.extract import evening_offer, is_error_page
from app.models import (
    AdmissionCycle,
    Notification,
    NotificationKind,
    ProgramRequirement,
    Requirement,
    RequirementStatus,
    Source,
    SourceSnapshot,
    SourceType,
)

# Lembretes em marcos decrescentes. Não é um por dia: para um prazo de cinco
# semanas, um alerta diário treina a pessoa a arquivar sem ler, e o dia em que
# importa é indistinguível dos vinte anteriores.
REMINDERS = (30, 14, 7, 3, 1)

SITE = os.environ.get("SITE_URL", "https://pos.v1cferr.dev")

# Páginas onde um edital NOVO é anunciado. Distinto de página de programa: uma
# muda por contador de visitas, a outra muda porque abriu processo.
ANNOUNCING = (SourceType.ADMISSION_PAGE, SourceType.PROGRAM_INDEX)

# O que faz uma linha ACRESCENTADA parecer anúncio. O caso real que motivou isto:
# em 10/08/2026 a página do PPGAdS ganhou "Processo Seletivo 2026 / Para a turma
# que iniciará as atividades em 2027 / Acesse o edital de seleção 2026", e o
# notificador não disse nada porque só olhava PDF de edital.
_ANNOUNCEMENT = re.compile(
    r"\b(?:edital|processo\s+seletivo|processos\s+seletivos|inscri[çc][õo]?[ea]s?|"
    r"sele[çc][ãa]o|vagas|ingresso)\b",
    re.IGNORECASE,
)


def announcement_lines(before: str, after: str) -> list[str]:
    """As linhas que APARECERAM e parecem anúncio de processo.

    Olhar só o hash diria "mudou"; olhar as linhas acrescentadas diz O QUE mudou,
    e é a diferença entre um alerta que se ignora e um que se lê. Só adições
    contam: texto de navegação já estava lá antes e não entra no diff.
    """
    added = [
        line.strip()
        for line in difflib.unified_diff(before.splitlines(), after.splitlines(), n=0)
        if line.startswith("+") and not line.startswith("+++")
    ]
    return [
        line[1:].strip()
        for line in added
        if len(line) > 12 and _ANNOUNCEMENT.search(line)
    ]


@dataclass(frozen=True)
class Event:
    kind: NotificationKind
    dedupe_key: str
    title: str
    body: str


# ─────────────────────────────────────────────────────────────────────────────
# Computar os eventos
# ─────────────────────────────────────────────────────────────────────────────


async def _cycle_events(db: AsyncSession, today: date) -> list[Event]:
    stmt = select(AdmissionCycle).options(
        selectinload(AdmissionCycle.program), selectinload(AdmissionCycle.seats)
    )
    out: list[Event] = []
    for c in (await db.scalars(stmt)).all():
        if not c.applications_close_on or c.applications_close_on < today:
            continue
        acronym = c.program.acronym
        term = f"{c.year}/{c.semester}"
        seats = sum(s.seats for s in c.seats)
        left = (c.applications_close_on - today).days
        url = c.official_url or SITE

        # Um processo que dá para fazer. Avisado uma vez por ciclo.
        out.append(
            Event(
                NotificationKind.CYCLE_OPEN,
                f"cycle_open:{acronym}:{term}",
                f"{acronym}: processo seletivo aberto",
                f"Inscrições até {c.applications_close_on:%d/%m/%Y} · {seats} vagas.\n"
                f"{url}\n{SITE}",
            )
        )

        # O marco MAIS APERTADO já cruzado — `min`, não o primeiro de uma tupla
        # decrescente. Iterar 30,14,7,3,1 e parar no primeiro `left <= mark`
        # casava sempre o 30: com sete dias restantes, o aviso diria "30 dias".
        #
        # Com o dedupe, cada marco dispara uma vez só na vida do ciclo — inclusive
        # se a máquina passar dias desligada e o timer `Persistent` recuperar
        # depois: o marco não é perdido nem repetido.
        crossed = [m for m in REMINDERS if left <= m]
        if crossed:
            mark = min(crossed)
            out.append(
                Event(
                    NotificationKind.DEADLINE_SOON,
                    f"deadline:{acronym}:{term}:{mark}",
                    f"{acronym}: faltam {left} dia(s)",
                    f"As inscrições fecham em {c.applications_close_on:%d/%m/%Y}.\n{url}",
                )
            )

    return out


async def _source_events(db: AsyncSession) -> list[Event]:
    """Edital alterado e fonte que cegou.

    Só EDITAL_PDF entra em "mudou": é o documento que carrega regra, e retificação
    de edital muda prazo e exigência. Mudança em página de programa não faz ninguém
    agir.
    """
    sources = (
        await db.scalars(select(Source).options(selectinload(Source.program)))
    ).all()
    out: list[Event] = []
    for src in sources:
        snap = (
            await db.scalars(
                select(SourceSnapshot)
                .where(SourceSnapshot.source_id == src.id)
                .order_by(SourceSnapshot.retrieved_at.desc())
                .limit(1)
            )
        ).first()
        if snap is None:
            continue

        who = src.program.acronym if src.program else "geral"

        if snap.error or (snap.text and is_error_page(snap.text)):
            why = snap.error or "a fonte devolve página de erro com HTTP 200"
            out.append(
                Event(
                    NotificationKind.SOURCE_BLIND,
                    # A chave inclui o motivo: se a falha mudar de natureza, avisa
                    # de novo. Se for a mesma, cala.
                    f"blind:{src.id}:{why[:60]}",
                    f"{who}: fonte inacessível",
                    f"{src.title}\n{why}\nA URL pode ter mudado.",
                )
            )
            continue

        # Anúncio numa página vigiada. O que fecha o buraco: o edital do PPGAdS
        # apareceu numa admission_page, e antes disto só edital_pdf avisava.
        if snap.changed and src.source_type in ANNOUNCING:
            previous = (
                await db.scalars(
                    select(SourceSnapshot)
                    .where(
                        SourceSnapshot.source_id == src.id,
                        SourceSnapshot.text.isnot(None),
                        SourceSnapshot.id != snap.id,
                    )
                    .order_by(SourceSnapshot.retrieved_at.desc())
                    .limit(1)
                )
            ).first()
            if previous and snap.text:
                new_lines = announcement_lines(previous.text, snap.text)
                if new_lines:
                    quoted = "\n".join(f"· {line}" for line in new_lines[:6])
                    out.append(
                        Event(
                            NotificationKind.ANNOUNCEMENT,
                            # Chave pelo CONTEÚDO acrescentado, não pelo hash da
                            # página: a página muda de novo por outros motivos e o
                            # mesmo anúncio não deve voltar.
                            f"announce:{src.id}:"
                            f"{hashlib.sha256(quoted.encode()).hexdigest()[:16]}",
                            f"{who}: apareceu anúncio de processo seletivo",
                            f"{src.title}\n\n{quoted}\n\n{src.url}",
                        )
                    )

        if snap.changed and src.source_type is SourceType.EDITAL_PDF:
            out.append(
                Event(
                    NotificationKind.NOTICE_CHANGED,
                    f"notice:{src.id}:{snap.content_hash}",
                    f"{who}: o edital mudou",
                    f"{src.title}\n"
                    + (
                        "Detectado por hash de BYTES (PDF digitalizado) — pode ser "
                        "apenas um novo escaneamento do mesmo documento.\n"
                        if snap.notes and "bytes" in snap.notes
                        else "O texto do documento mudou — provável retificação.\n"
                    )
                    + f"{src.url}",
                )
            )
    return out


async def _verdict_events(db: AsyncSession) -> list[Event]:
    """A grade passou a dizer outra coisa sobre horário.

    É o evento mais valioso do projeto: se o PPGCC abrir uma faixa às 19h, é aqui
    que alguém descobre — sem abrir PDF, sem esperar que alguém pense em conferir.
    """
    sources = (
        await db.scalars(
            select(Source)
            .options(selectinload(Source.program))
            .where(
                Source.source_type.in_((SourceType.SCHEDULE_PDF, SourceType.COURSE_CATALOG)),
                Source.program_id.isnot(None),
            )
        )
    ).all()
    out: list[Event] = []
    for src in sources:
        snap = (
            await db.scalars(
                select(SourceSnapshot)
                .where(SourceSnapshot.source_id == src.id, SourceSnapshot.text.isnot(None))
                .order_by(SourceSnapshot.retrieved_at.desc())
                .limit(1)
            )
        ).first()
        if snap is None or is_error_page(snap.text or ""):
            continue

        offer = evening_offer(snap.text or "")
        if offer.status is RequirementStatus.UNKNOWN:
            continue  # ausência de dado não é notícia

        stored = (
            await db.scalars(
                select(ProgramRequirement).where(
                    ProgramRequirement.program_id == src.program_id,
                    ProgramRequirement.requirement == Requirement.EVENING_CLASSES,
                )
            )
        ).first()
        if stored is None or stored.status is offer.status:
            continue

        acronym = src.program.acronym
        good = offer.status is RequirementStatus.MET
        out.append(
            Event(
                NotificationKind.SCHEDULE_VERDICT,
                f"verdict:{src.id}:{offer.status.value}:{snap.content_hash}",
                f"{acronym}: {'ABRIU horário noturno' if good else 'horário mudou'}",
                f"{src.title}\n{offer.evidence}\n"
                f"Antes: {stored.status.value}. Agora: {offer.status.value}.\n{SITE}",
            )
        )
    return out


async def collect_events(db: AsyncSession, today: date) -> list[Event]:
    return [
        *await _cycle_events(db, today),
        *await _source_events(db),
        *await _verdict_events(db),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Entregar
# ─────────────────────────────────────────────────────────────────────────────


async def _send_ntfy(client: httpx.AsyncClient, ev: Event) -> str:
    """ntfy é o primeiro canal porque já é o padrão do host.

    Os dotfiles já usam ntfy para o duo-streak-daemon, então o app está no celular
    e o hábito existe. Zero papelada, ao contrário da WhatsApp Cloud API, que exige
    número dedicado e template aprovado.
    """
    base = os.environ.get("NTFY_URL", "https://ntfy.sh").rstrip("/")
    topic = os.environ["NTFY_TOPIC"]
    urgent = ev.kind in (NotificationKind.DEADLINE_SOON, NotificationKind.CYCLE_OPEN)
    r = await client.post(
        f"{base}/{topic}",
        content=ev.body.encode(),
        headers={
            "Title": ev.title,
            "Priority": "high" if urgent else "default",
            "Tags": "calendar" if urgent else "mag",
        },
    )
    r.raise_for_status()
    return f"ntfy {r.status_code}"


async def _send_telegram(client: httpx.AsyncClient, ev: Event) -> str:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    r = await client.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": f"*{ev.title}*\n\n{ev.body}", "parse_mode": "Markdown"},
    )
    r.raise_for_status()
    return f"telegram {r.status_code}"


async def _send_email(client: httpx.AsyncClient, ev: Event) -> str:
    """SMTP, e não uma API de terceiro.

    É o canal que chega onde os três já olham durante o trabalho, sem instalar
    nada — e um aviso de prazo com link resolve bem em texto puro. Zero risco de
    banimento, ao contrário do WhatsApp no número próprio (ver docs/WHATSAPP.md).

    Roda em thread porque `smtplib` é bloqueante: chamá-lo direto num `async def`
    travaria o loop, e num script de 30 segundos isso não dói — mas ele também é
    importado pela API, e ali travaria requisições.
    """
    msg = EmailMessage()
    msg["Subject"] = f"[GradRadar] {ev.title}"
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(f"{ev.body}\n\n—\n{SITE}")

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")

    def _send() -> None:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)

    await asyncio.to_thread(_send)
    return f"email → {os.environ['EMAIL_TO']}"


SENDERS = {"ntfy": _send_ntfy, "telegram": _send_telegram, "email": _send_email}

# O que cada canal precisa para ser considerado PRONTO. Um canal declarado sem
# credencial falharia calado a cada execução, e o sintoma — "não recebo nada" — é
# indistinguível de "não houve novidade".
REQUIRED_ENV = {
    "ntfy": ("NTFY_TOPIC",),
    "telegram": ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"),
    "email": ("SMTP_HOST", "SMTP_FROM", "EMAIL_TO"),
}


def active_channels() -> list[str]:
    """Canal ligado é canal com TODAS as variáveis dele definidas.

    Um canal habilitado sem credencial falharia em silêncio a cada execução, e o
    sintoma — "não recebo nada" — é indistinguível de "não houve novidade".

    Um nome desconhecido é ignorado em vez de derrubar a cadeia: deixar
    `whatsapp` no NOTIFY_CHANNELS enquanto o adaptador não existe (ver
    docs/WHATSAPP.md) não deve impedir o ntfy de funcionar.
    """
    declared = [c.strip() for c in os.environ.get("NOTIFY_CHANNELS", "").split(",") if c.strip()]
    return [
        c
        for c in declared
        if c in REQUIRED_ENV and all(os.environ.get(v) for v in REQUIRED_ENV[c])
    ]


async def run(db: AsyncSession, today: date, dry_run: bool) -> tuple[int, int]:
    events = await collect_events(db, today)

    seen = set(
        (
            await db.scalars(
                select(Notification.dedupe_key).where(
                    Notification.dedupe_key.in_([e.dedupe_key for e in events] or [""])
                )
            )
        ).all()
    )
    fresh = [e for e in events if e.dedupe_key not in seen]

    channels = active_channels()
    for e in fresh:
        print(f"  [{e.kind.value}] {e.title}")
        for line in e.body.splitlines():
            print(f"        {line}")

    if dry_run or not fresh:
        return len(fresh), 0

    delivered = 0
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        for e in fresh:
            notes: list[str] = []
            ok = False
            for name in channels:
                try:
                    notes.append(await SENDERS[name](client, e))
                    ok = True
                except Exception as exc:  # noqa: BLE001 — canal fora não é erro nosso
                    notes.append(f"{name} FALHOU: {type(exc).__name__}: {exc}")
            if not channels:
                notes.append("nenhum canal configurado — só registrado")

            now = datetime.now(UTC)
            db.add(
                Notification(
                    kind=e.kind,
                    dedupe_key=e.dedupe_key,
                    title=e.title,
                    body=e.body,
                    created_at=now,
                    # Só marca entregue se ALGUM canal aceitou. Gravar entregue sem
                    # entrega transformaria a tabela num registro de mentiras, e o
                    # dedupe garantiria que nunca mais se tentasse.
                    delivered_at=now if ok else None,
                    delivery_note="; ".join(notes),
                )
            )
            delivered += int(ok)
    await db.commit()
    return len(fresh), delivered


async def main() -> None:
    parser = argparse.ArgumentParser(description="Avisa sobre prazos e mudanças que importam.")
    parser.add_argument("--dry-run", action="store_true", help="mostrar sem enviar nem gravar")
    args = parser.parse_args()

    today = date.today()  # noqa: DTZ011 — prazo de edital é data civil
    async with Session() as db:
        fresh, delivered = await run(db, today, args.dry_run)

    channels = active_channels() or ["nenhum"]
    verb = "enviaria" if args.dry_run else "entregue(s)"
    print(f"\n  {fresh} evento(s) novo(s) · {delivered} {verb} · canais: {', '.join(channels)}")
    if fresh and not channels and not args.dry_run:
        print("  ⚠ Configure NOTIFY_CHANNELS e as credenciais — os eventos foram só registrados.")


if __name__ == "__main__":
    asyncio.run(main())
