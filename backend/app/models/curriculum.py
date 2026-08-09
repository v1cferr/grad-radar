"""Disciplines and their semester offerings.

The distinction between the two is the most important modelling decision in this
file, and it comes straight from the sources: the catalogue page gives a
discipline a code, a name and its credits — nothing else. Everything that
decides whether a person can actually take it (professor, weekday, time band,
room, language, and whether it counts as `Básica` or `Específica <LINE>`) is
published per **semester offering**, in a different document.

`CCO-724` is not "an AMPLN discipline". It is *offered as* AMPLN-specific in
2026/2, by Tiago Agostinho de Almeida.
"""

from __future__ import annotations

import enum
from datetime import time

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, pg_enum


class DisciplineGroup(enum.StrEnum):
    """The four catalogue groups of PPGCC."""

    I = "I"  # Teoria da Computação, Análise de Algoritmos e Complexidade
    II = "II"  # Metodologia e Técnicas de Computação
    III = "III"  # Sistemas de Computação
    IV = "IV"  # Qualificação Discente


class Weekday(enum.StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"


class OfferingScope(enum.StrEnum):
    """Whether the offering counts as core or line-specific in a given term."""

    BASICA = "basica"
    ESPECIFICA = "especifica"


class Language(enum.StrEnum):
    PT_BR = "pt-BR"
    EN = "en"


class Discipline(Base):
    """A catalogue entry. Stable across semesters.

    ``curriculum_version`` exists because two catalogues coexist, keyed by entry
    date (`_apos_jul_24` and `_ate_jul_24`) — which disciplines are valid depends
    on when the student entered the program.
    """

    __tablename__ = "discipline"
    __table_args__ = (UniqueConstraint("program_id", "code", "curriculum_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("graduate_program.id"))
    code: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(300))
    name_en: Mapped[str | None] = mapped_column(String(300))
    credits: Mapped[int | None] = mapped_column()
    group: Mapped[DisciplineGroup | None] = mapped_column(
        pg_enum(DisciplineGroup, "discipline_group")
    )
    curriculum_version: Mapped[str] = mapped_column(String(30), default="apos_jul_24")
    syllabus: Mapped[str | None] = mapped_column(Text)

    offerings: Mapped[list[CourseOffering]] = relationship(back_populates="discipline")


class CourseOffering(Base):
    """One discipline, one term, one slot in the weekly grid."""

    __tablename__ = "course_offering"
    __table_args__ = (UniqueConstraint("discipline_id", "year", "semester"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    discipline_id: Mapped[int] = mapped_column(ForeignKey("discipline.id"))
    year: Mapped[int] = mapped_column()
    semester: Mapped[int] = mapped_column()

    # "Docente ministrante" — who teaches this term. Distinct from the
    # faculty↔research-line relation, which is about research, not teaching.
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_member.id"))

    scope: Mapped[OfferingScope | None] = mapped_column(pg_enum(OfferingScope, "offering_scope"))
    research_line_id: Mapped[int | None] = mapped_column(ForeignKey("research_line.id"))

    weekday: Mapped[Weekday | None] = mapped_column(pg_enum(Weekday, "weekday"))

    # Real TIME columns, not a free-text band, precisely so they can be COMPARED
    # to a working day. The published grid has only two slots (08:00–12:00 and
    # 14:00–18:00), so recurrence rules would be overengineering — but the
    # comparison itself is the product's whole point, and a string could not do it.
    starts_at: Mapped[time | None] = mapped_column()
    ends_at: Mapped[time | None] = mapped_column()

    language: Mapped[Language | None] = mapped_column(pg_enum(Language, "language"))
    notes: Mapped[str | None] = mapped_column(Text)

    discipline: Mapped[Discipline] = relationship(back_populates="offerings")
    locations: Mapped[list[OfferingLocation]] = relationship(
        back_populates="offering", cascade="all, delete-orphan"
    )

    def overlaps(self, work_start: time, work_end: time) -> bool | None:
        """Does this offering collide with a working day?

        Returns ``None`` when the schedule is unknown — deliberately not
        ``False``. "We don't know the time" and "it doesn't conflict" are
        opposite answers to the question this project exists to ask.
        """
        if self.starts_at is None or self.ends_at is None:
            return None
        return self.starts_at < work_end and work_start < self.ends_at


class OfferingLocation(Base):
    """Where an offering physically happens — and there is more than one.

    Every row of the PPGCC grid lists a São Carlos room *and* a Sorocaba room
    (`CCGT-1001`): the same discipline runs at two campuses simultaneously. A
    scalar ``room`` column on the offering would have been wrong on day one.
    """

    __tablename__ = "offering_location"

    id: Mapped[int] = mapped_column(primary_key=True)
    offering_id: Mapped[int] = mapped_column(ForeignKey("course_offering.id"))
    campus_id: Mapped[int | None] = mapped_column(ForeignKey("campus.id"))
    room: Mapped[str | None] = mapped_column(String(120))
    is_origin: Mapped[bool] = mapped_column(default=True)

    offering: Mapped[CourseOffering] = relationship(back_populates="locations")
