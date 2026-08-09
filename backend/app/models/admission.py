"""Admission cycles, notices and their stages.

A program persists for years; an admission cycle is temporal. `2026-1o-semestre`
and `2026-2o-semestre` are archived siblings of one program, never separate
programs.

The status of a cycle is **derived from its dates**, never from the label the
site puts on it. The 2026/2 cycle is published as "Processo vigente" while its
application window closed on 26/04/2026 and every stage has already published
results. A collector that trusted the wording would announce an opportunity that
does not exist — the precise failure this project exists to prevent.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, pg_enum
from app.models.academic import GraduateProgram


class DegreeLevel(enum.StrEnum):
    MASTER = "master"
    DOCTORATE = "doctorate"
    DIRECT_DOCTORATE = "direct_doctorate"
    POSTDOC = "postdoc"


class EntryMode(enum.StrEnum):
    """Entry mode is a separate axis from degree level.

    The program lists Mestrado, Doutorado, Aluno Especial and Graduação-Mestrado
    as peers in its own navigation, but they are not comparable things: special
    student is a *way in*, not a degree. Its mechanics differ too — it follows
    the academic calendar and has no edital at all.
    """

    REGULAR = "regular"
    SPECIAL_STUDENT = "special_student"
    GRADUATION_TRACK = "graduation_track"


class CycleStatus(enum.StrEnum):
    EXPECTED = "expected"  # inferred from the historical pattern, no page yet
    ANNOUNCED = "announced"  # notice published, applications not open
    OPEN = "open"  # applications open right now
    IN_PROGRESS = "in_progress"  # applications closed, stages running
    CONCLUDED = "concluded"


class AdmissionCycle(Base):
    __tablename__ = "admission_cycle"
    __table_args__ = (UniqueConstraint("program_id", "year", "semester", "entry_mode"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("graduate_program.id"))
    year: Mapped[int] = mapped_column()
    semester: Mapped[int] = mapped_column()
    entry_mode: Mapped[EntryMode] = mapped_column(pg_enum(EntryMode, "entry_mode"))
    degree_level: Mapped[DegreeLevel | None] = mapped_column(
        pg_enum(DegreeLevel, "degree_level")
    )

    applications_open_on: Mapped[date | None] = mapped_column()
    applications_close_on: Mapped[date | None] = mapped_column()

    # When the candidate finally knows. Not derivable from the stages: the last
    # stage publishes ITS notes, and the definitive result comes after a further
    # appeal window — 04/12 vs 18/12 in the PPGPEP cycle. A tracking system whose
    # whole job is "when will we know" should be able to answer it directly.
    final_result_on: Mapped[date | None] = mapped_column()

    # What the institution calls it. Kept for traceability, NEVER used to decide
    # status — see the module docstring.
    site_label: Mapped[str | None] = mapped_column(String(120))
    official_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    program: Mapped[GraduateProgram] = relationship()
    stages: Mapped[list[AdmissionStage]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan", order_by="AdmissionStage.ordinal"
    )
    seats: Mapped[list[AdmissionSeat]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )
    notices: Mapped[list[AdmissionNotice]] = relationship(back_populates="cycle")
    required_documents: Mapped[list[RequiredDocument]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )

    def status_on(self, today: date) -> CycleStatus:
        """Derive status from dates alone."""
        if self.applications_open_on is None:
            return CycleStatus.EXPECTED
        if today < self.applications_open_on:
            return CycleStatus.ANNOUNCED
        if self.applications_close_on is None or today <= self.applications_close_on:
            return CycleStatus.OPEN
        last = max((s.result_on or s.ends_on for s in self.stages if s.result_on or s.ends_on), default=None)
        if last is not None and today <= last:
            return CycleStatus.IN_PROGRESS
        return CycleStatus.CONCLUDED


class AdmissionStage(Base):
    """An ordered, dated step. The source publishes results per numbered stage."""

    __tablename__ = "admission_stage"
    __table_args__ = (UniqueConstraint("cycle_id", "ordinal"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("admission_cycle.id"))
    ordinal: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(200))
    starts_on: Mapped[date | None] = mapped_column()
    ends_on: Mapped[date | None] = mapped_column()
    result_on: Mapped[date | None] = mapped_column()
    eliminatory: Mapped[bool | None] = mapped_column()

    cycle: Mapped[AdmissionCycle] = relationship(back_populates="stages")


class AdmissionSeat(Base):
    """Seats are allocated PER RESEARCH LINE, not to the program as a whole.

    In Edital 02/2026 the same cycle offers 7 seats to VC and 1 to ES. A single
    ``seats`` integer on the cycle would erase the only number that tells a
    candidate their real odds.
    """

    __tablename__ = "admission_seat"
    __table_args__ = (UniqueConstraint("cycle_id", "research_line_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("admission_cycle.id"))
    research_line_id: Mapped[int | None] = mapped_column(ForeignKey("research_line.id"))
    seats: Mapped[int] = mapped_column()

    cycle: Mapped[AdmissionCycle] = relationship(back_populates="seats")


class RequiredDocument(Base):
    __tablename__ = "required_document"

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("admission_cycle.id"))
    name: Mapped[str] = mapped_column(String(250))
    mandatory: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text)

    cycle: Mapped[AdmissionCycle] = relationship(back_populates="required_documents")


class AdmissionNotice(Base):
    """The edital itself — a document, distinct from the cycle it governs."""

    __tablename__ = "admission_notice"

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("admission_cycle.id"))
    number: Mapped[str] = mapped_column(String(40))
    title: Mapped[str | None] = mapped_column(String(300))
    url: Mapped[str | None] = mapped_column(Text)

    cycle: Mapped[AdmissionCycle] = relationship(back_populates="notices")
    versions: Mapped[list[AdmissionNoticeVersion]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )


class AdmissionNoticeVersion(Base):
    """Notices get revised mid-cycle.

    Not a hypothesis: one published artifact of the 2026/1 cycle is literally
    titled "Comissões de avaliação por linha de pesquisa (**retificada**)".
    Keeping only the latest version would discard exactly the information F5
    needs to alert on — *what changed*.
    """

    __tablename__ = "admission_notice_version"

    id: Mapped[int] = mapped_column(primary_key=True)
    notice_id: Mapped[int] = mapped_column(ForeignKey("admission_notice.id"))
    snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("source_snapshot.id"))
    label: Mapped[str | None] = mapped_column(String(120))
    is_rectification: Mapped[bool] = mapped_column(default=False)
    diff_summary: Mapped[str | None] = mapped_column(Text)

    notice: Mapped[AdmissionNotice] = relationship(back_populates="versions")
