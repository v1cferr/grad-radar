"""O que já foi avisado, para não avisar duas vezes.

Sem esta tabela o notificador reenviaria tudo a cada execução — duas vezes por dia,
para sempre. E notificação repetida não é só irritante: é o mesmo modo de falha do
monitor que ninguém lê. Depois do terceiro "PPGPEP fecha em 14/09" no mesmo dia, o
quarto não é lido, e o que estava no quarto era outra coisa.

A chave de deduplicação é construída pelo evento e é UNIQUE no banco. É o banco que
garante, não a lógica: uma execução concorrente do timer não consegue duplicar.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, pg_enum


class NotificationKind(enum.StrEnum):
    """Só o que faz uma pessoa AGIR ou o que indica que o sistema cegou.

    Deliberadamente NÃO existe um "conteúdo mudou": o hash de uma página muda por
    motivo nenhum — um contador de visitas, um PDF regerado — e um canal que avisa
    disso ensina a ignorar o canal.
    """

    CYCLE_OPEN = "cycle_open"  # apareceu processo que dá para fazer
    DEADLINE_SOON = "deadline_soon"  # o prazo está chegando
    NOTICE_CHANGED = "notice_changed"  # o EDITAL mudou — retificação
    SOURCE_BLIND = "source_blind"  # paramos de conseguir ver uma fonte
    SCHEDULE_VERDICT = "schedule_verdict"  # a grade mudou o veredito de horário


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[NotificationKind] = mapped_column(pg_enum(NotificationKind, "notification_kind"))

    # UNIQUE: é o banco que impede o reenvio, não um `if` que pode ficar de fora
    # de um caminho novo.
    dedupe_key: Mapped[str] = mapped_column(String(200), unique=True)

    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Nulo enquanto nenhum canal aceitou. Registrado separado de `created_at`
    # porque "computamos o evento" e "alguém foi avisado" são fatos diferentes, e
    # confundi-los esconderia exatamente a falha que interessa: o canal quebrado.
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivery_note: Mapped[str | None] = mapped_column(Text)
