"""Candidate profiles.

There is no global "best program", so there is no global ranking. The same
opportunity can be top priority for one candidate and unviable for the other,
and the difference is usually the working day — which is why work hours are
first-class columns here rather than a note.

Scoring itself belongs to F2. This module only holds what scoring will read.
"""

from __future__ import annotations

from datetime import time

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Candidate(Base):
    __tablename__ = "candidate"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    email: Mapped[str | None] = mapped_column(String(200))

    employer: Mapped[str | None] = mapped_column(String(200))

    # Compared against CourseOffering.starts_at/ends_at. This pair is the reason
    # those are TIME columns and not a free-text band.
    work_starts_at: Mapped[time | None] = mapped_column()
    work_ends_at: Mapped[time | None] = mapped_column()

    notes: Mapped[str | None] = mapped_column(Text)

    interests: Mapped[list[CandidateInterest]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan"
    )


class CandidateInterest(Base):
    """A technical topic the candidate cares about, with a weight.

    Free-text topic rather than a foreign key to research lines on purpose: the
    research showed line names are a weak relevance signal (only AMPLN names AI,
    yet VC, ES and BD hold AI-adjacent work). Interests must be able to match
    below the line level — at faculty, lab and project.
    """

    __tablename__ = "candidate_interest"
    __table_args__ = (UniqueConstraint("candidate_id", "topic"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate.id"))
    topic: Mapped[str] = mapped_column(String(120))
    weight: Mapped[int] = mapped_column(default=1)

    candidate: Mapped[Candidate] = relationship(back_populates="interests")
