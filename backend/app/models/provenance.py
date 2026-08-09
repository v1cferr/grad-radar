"""Where every fact came from.

This is an architectural requirement, not bookkeeping. When the system later
says "this line has high adherence to LLMs", it must be possible to walk down to
the evidence: program → line → faculty → lab → project → **source**.

The research phase settled the shape. The admission cycle page on the PPGCC site
contains *links and no facts* — dates, seats, documents and stages all live
inside a PDF served by SEI, and the page for the semester timetable is a 302 to
another SEI PDF. A `source_url` column on each fact could not express that: the
fact belongs to a *retrieved document*, at a *moment*, with a *hash*. Hence two
tables, from the first migration.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, pg_enum


class SourceType(enum.StrEnum):
    INSTITUTIONAL_PAGE = "institutional_page"
    GRADUATE_PROGRAM_PAGE = "graduate_program_page"
    ADMISSION_PAGE = "admission_page"
    EDITAL_PDF = "edital_pdf"
    SCHEDULE_PDF = "schedule_pdf"
    COURSE_CATALOG = "course_catalog"
    FACULTY_PAGE = "faculty_page"
    LABORATORY_PAGE = "laboratory_page"
    RESEARCH_GROUP_PAGE = "research_group_page"
    REGULATION_PDF = "regulation_pdf"
    LATTES = "lattes"
    ORCID = "orcid"
    NEWS = "news"


class Source(Base):
    """A location worth watching. F5 will poll these; F1 only registers them."""

    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text, unique=True)
    source_type: Mapped[SourceType] = mapped_column(pg_enum(SourceType, "source_type"))
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"))
    title: Mapped[str | None] = mapped_column(String(300))

    # A 302 to SEI is not an incidental detail: it is why naive scraping of the
    # HTML page returns nothing useful. Recorded so the collector knows to follow.
    redirects_to: Mapped[str | None] = mapped_column(Text)

    active: Mapped[bool] = mapped_column(default=True)
    check_frequency: Mapped[str | None] = mapped_column(String(30))
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    snapshots: Mapped[list[SourceSnapshot]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class SourceSnapshot(Base):
    """What a source contained at one moment.

    ``content_hash`` is what makes change detection possible without storing
    every byte forever, and ``retrieved_at`` is what lets a fact say *when* it
    was true rather than merely that someone believed it.
    """

    __tablename__ = "source_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String(64))
    http_status: Mapped[int | None] = mapped_column()
    content_path: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    source: Mapped[Source] = relationship(back_populates="snapshots")
