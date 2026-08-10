"""O notificador, e principalmente o que ele se recusa a enviar.

A falha que estes testes existem para impedir não é "não avisou". É "avisou demais":
um canal que dispara a cada mudança de hash treina a pessoa a arquivar sem ler, e o
dia em que o aviso importa fica indistinguível dos vinte anteriores. O monitor que
ninguém lê já foi o problema deste projeto uma vez.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    GraduateProgram,
    Notification,
    NotificationKind,
    Source,
    SourceSnapshot,
    SourceType,
)
from app.notify import REMINDERS, active_channels, collect_events, run

TODAY = date(2026, 8, 10)


async def _keys(db: AsyncSession, today: date = TODAY) -> set[str]:
    return {e.dedupe_key for e in await collect_events(db, today)}


class TestOpenCycles:
    async def test_both_open_calls_are_announced(self, db: AsyncSession, seeded: None):
        keys = await _keys(db)
        assert "cycle_open:PPGPEP:2027/1" in keys
        assert "cycle_open:PPGAdS:2027/1" in keys

    async def test_a_closed_cycle_is_never_announced(self, db: AsyncSession, seeded: None):
        """O PPGCC 2026/2 fechou em 26/04. Anunciá-lo seria o oposto do trabalho."""
        assert not any(k.startswith("cycle_open:PPGCC:2026/2") for k in await _keys(db))

    async def test_an_expected_cycle_without_dates_is_not_announced(
        self, db: AsyncSession, seeded: None
    ):
        """O PPGCC 2027/1 é previsto, sem data. Anunciar "processo aberto" para ele
        seria inventar um prazo que ninguém publicou."""
        assert not any(k.startswith("cycle_open:PPGCC:2027/1") for k in await _keys(db))


class TestDeadlineReminders:
    async def test_no_reminder_while_the_deadline_is_far(self, db: AsyncSession, seeded: None):
        """Em 10/08 faltam 35 dias para o PPGPEP; o primeiro marco é 30."""
        assert not any(k.startswith("deadline:PPGPEP") for k in await _keys(db))

    @pytest.mark.parametrize(("days_left", "mark"), [(30, 30), (20, 30), (14, 14), (7, 7), (5, 7), (2, 3), (0, 1)])
    async def test_each_milestone_fires_once(
        self, db: AsyncSession, seeded: None, days_left: int, mark: int
    ):
        """O marco MAIS APERTADO já cruzado, e só ele.

        Duas coisas de uma vez. Cruzar 30 dias não pode enviar cinco mensagens no
        mesmo dia — a primeira lição de um canal assim é ignorá-lo. E com sete dias
        restantes o aviso tem de dizer "7", não "30": este teste pegou justamente
        isso, porque iterar uma tupla decrescente e parar no primeiro `left <= mark`
        casa sempre o maior.

        Os casos (20, 30) e (5, 7) documentam a outra metade: entre dois marcos, o
        que vale é o último cruzado — e o dedupe faz nada ser reenviado, porque ele
        já disparou no dia em que foi cruzado.
        """
        close = date(2026, 9, 14)
        today = date.fromordinal(close.toordinal() - days_left)
        keys = {k for k in await _keys(db, today) if k.startswith("deadline:PPGPEP")}
        assert keys == {f"deadline:PPGPEP:2027/1:{mark}"}

    async def test_reminders_are_milestones_not_daily(self):
        """Um alerta por dia durante cinco semanas é ruído por construção."""
        assert REMINDERS == (30, 14, 7, 3, 1)


class TestWhatIsNotNotified:
    async def test_a_changed_page_is_not_an_event(self, db: AsyncSession, seeded: None):
        """Só EDITAL mudado avisa. Página de programa muda por contador de visitas,
        banner rotativo, data de "última atualização" — nada disso faz agir."""
        src = (
            await db.scalars(
                select(Source).where(Source.source_type == SourceType.GRADUATE_PROGRAM_PAGE)
            )
        ).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                content_hash="deadbeef",
                text="conteúdo qualquer, sem horário",
                changed=True,
            )
        )
        await db.flush()
        assert not any(k.startswith("notice:") for k in await _keys(db))

    async def test_a_changed_edital_is_an_event(self, db: AsyncSession, seeded: None):
        src = (
            await db.scalars(select(Source).where(Source.source_type == SourceType.EDITAL_PDF))
        ).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                content_hash="cafe1234",
                text="edital retificado",
                changed=True,
            )
        )
        await db.flush()
        assert f"notice:{src.id}:cafe1234" in await _keys(db)

    async def test_an_unknown_schedule_verdict_is_not_an_event(
        self, db: AsyncSession, seeded: None
    ):
        """Ausência de dado não é notícia — a mesma regra que o `verify` aprendeu."""
        src = (
            await db.scalars(
                select(Source).where(Source.source_type == SourceType.COURSE_CATALOG)
            )
        ).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                content_hash="nada",
                text="lista de disciplinas sem nenhum horário",
                changed=True,
            )
        )
        await db.flush()
        assert not any(k.startswith("verdict:") for k in await _keys(db))


class TestGoingBlind:
    async def test_a_failing_source_is_reported(self, db: AsyncSession, seeded: None):
        src = (await db.scalars(select(Source))).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                error="ConnectTimeout: nada respondeu",
            )
        )
        await db.flush()
        assert any(k.startswith(f"blind:{src.id}:") for k in await _keys(db))

    async def test_a_soft_404_is_reported_too(self, db: AsyncSession, seeded: None):
        """HTTP 200 com página de erro. Sem isto a fonte ficaria verde para sempre."""
        src = (await db.scalars(select(Source))).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                content_hash="erro",
                text="Erro 404\n\nPágina não encontrada",
                changed=True,
            )
        )
        await db.flush()
        events = await collect_events(db, TODAY)
        blind = [e for e in events if e.kind is NotificationKind.SOURCE_BLIND]
        assert blind and "HTTP 200" in blind[0].body


class TestScheduleVerdictChange:
    async def test_an_evening_band_appearing_is_the_headline(
        self, db: AsyncSession, seeded: None
    ):
        """O evento mais valioso do projeto: o PPGCC abrindo horário noturno."""
        program = (
            await db.scalars(select(GraduateProgram).where(GraduateProgram.acronym == "PPGCC"))
        ).first()
        src = (
            await db.scalars(
                select(Source).where(
                    Source.source_type == SourceType.SCHEDULE_PDF,
                    Source.program_id == program.id,
                )
            )
        ).first()
        db.add(
            SourceSnapshot(
                source_id=src.id,
                retrieved_at=datetime.now(UTC),
                content_hash="noturno",
                text="Grade 2027/1\nSegunda 19h às 22h\nQuarta 19h às 22h",
                changed=True,
            )
        )
        await db.flush()

        events = [e for e in await collect_events(db, TODAY) if e.dedupe_key.startswith("verdict:")]
        assert events, "uma faixa às 19h tem de gerar evento"
        assert "ABRIU" in events[0].title
        assert "19:00" in events[0].body


class TestDeduplication:
    async def test_running_twice_sends_nothing_the_second_time(
        self, db: AsyncSession, seeded: None
    ):
        first, _ = await run(db, TODAY, dry_run=False)
        assert first > 0
        second, delivered = await run(db, TODAY, dry_run=False)
        assert (second, delivered) == (0, 0)

    async def test_dry_run_records_nothing(self, db: AsyncSession, seeded: None):
        before = len((await db.scalars(select(Notification))).all())
        n, delivered = await run(db, TODAY, dry_run=True)
        assert n > 0 and delivered == 0
        assert len((await db.scalars(select(Notification))).all()) == before

    async def test_undelivered_is_recorded_as_undelivered(
        self, db: AsyncSession, seeded: None, monkeypatch: pytest.MonkeyPatch
    ):
        """Sem canal configurado, grava o evento mas NÃO marca como entregue.

        Marcar entregue sem entrega tornaria a tabela um registro de mentiras — e o
        dedupe garantiria que nunca mais se tentasse enviar.
        """
        monkeypatch.delenv("NOTIFY_CHANNELS", raising=False)
        await run(db, TODAY, dry_run=False)
        rows = (await db.scalars(select(Notification))).all()
        assert rows
        assert all(r.delivered_at is None for r in rows)
        assert all("nenhum canal" in (r.delivery_note or "") for r in rows)


class TestChannelGating:
    def test_a_channel_without_credentials_is_not_active(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Canal declarado sem credencial falharia calado a cada execução, e o
        sintoma — "não recebo nada" — é idêntico a "não houve novidade"."""
        monkeypatch.setenv("NOTIFY_CHANNELS", "ntfy,telegram")
        monkeypatch.delenv("NTFY_TOPIC", raising=False)
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        assert active_channels() == []

    def test_ntfy_needs_only_a_topic(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("NOTIFY_CHANNELS", "ntfy")
        monkeypatch.setenv("NTFY_TOPIC", "gradradar-teste")
        assert active_channels() == ["ntfy"]

    def test_telegram_needs_both_token_and_chat(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("NOTIFY_CHANNELS", "telegram")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x")
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
        assert active_channels() == []
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "y")
        assert active_channels() == ["telegram"]
