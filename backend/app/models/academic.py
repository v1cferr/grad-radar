"""Institutions, programs, research lines and faculty.

Every structural choice here is forced by something observed on the official
PPGCC/UFSCar pages — see `docs/research/ufscar-ppgcc.md`. Where the shape looks
more elaborate than necessary, the research note explains which real record
would otherwise be lost.
"""

from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, pg_enum


class AffiliationStatus(enum.StrEnum):
    """How a faculty member is bound to the program.

    Three values because the source publishes three. It is not decoration: CAPES
    rules generally restrict who may advise, so the distinction is expected to
    drive "can this person be my advisor?" later.
    """

    PERMANENT = "permanent"
    COLLABORATOR = "collaborator"
    SENIOR_PERMANENT = "senior_permanent"


class LinkKind(enum.StrEnum):
    """Faculty links are heterogeneous — Lattes, lab, personal site, linktr.ee.

    A single ``lattes_url`` column would discard most of them, and the LAB link
    is the one that reveals actual research activity.
    """

    LATTES = "lattes"
    ORCID = "orcid"
    LABORATORY = "laboratory"
    PERSONAL = "personal"
    INSTITUTIONAL = "institutional"
    OTHER = "other"


class Institution(Base):
    __tablename__ = "institution"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    acronym: Mapped[str] = mapped_column(String(20), unique=True)
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(2))
    website: Mapped[str | None] = mapped_column(Text)

    campuses: Mapped[list[Campus]] = relationship(back_populates="institution")


class Campus(Base):
    __tablename__ = "campus"
    __table_args__ = (UniqueConstraint("institution_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institution.id"))
    name: Mapped[str] = mapped_column(String(120))
    address: Mapped[str | None] = mapped_column(Text)

    institution: Mapped[Institution] = relationship(back_populates="campuses")


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True)
    campus_id: Mapped[int] = mapped_column(ForeignKey("campus.id"))
    name: Mapped[str] = mapped_column(String(200))
    acronym: Mapped[str | None] = mapped_column(String(20))
    website: Mapped[str | None] = mapped_column(Text)

    campus: Mapped[Campus] = relationship()


class GraduateProgram(Base):
    __tablename__ = "graduate_program"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"))
    name: Mapped[str] = mapped_column(String(250))
    acronym: Mapped[str] = mapped_column(String(30), unique=True)
    website: Mapped[str | None] = mapped_column(Text)
    capes_rating: Mapped[int | None] = mapped_column()

    # NULL means UNKNOWN, not "no". Brazilian federal programs are tuition-free
    # by law, but no consulted page states it, and this project does not encode
    # inference as fact (see the research note's "Unknown / unresolved").
    tuition_free: Mapped[bool | None] = mapped_column()

    notes: Mapped[str | None] = mapped_column(Text)

    department: Mapped[Department] = relationship()
    research_lines: Mapped[list[ResearchLine]] = relationship(back_populates="program")


class ResearchLine(Base):
    __tablename__ = "research_line"
    __table_args__ = (UniqueConstraint("program_id", "acronym"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("graduate_program.id"))
    acronym: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(250))
    description: Mapped[str | None] = mapped_column(Text)

    program: Mapped[GraduateProgram] = relationship(back_populates="research_lines")
    faculty: Mapped[list[FacultyMember]] = relationship(
        secondary="faculty_research_line", back_populates="research_lines"
    )


class FacultyResearchLine(Base):
    """M:N, and both sides are optional.

    Proven by the source: Auri Vincenzi appears under BD *and* ES, while Paulo
    Cruvinel has no line at all. A ``research_line_id`` column on faculty would
    silently lose the first case and reject the second.
    """

    __tablename__ = "faculty_research_line"

    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty_member.id"), primary_key=True)
    research_line_id: Mapped[int] = mapped_column(ForeignKey("research_line.id"), primary_key=True)


class FacultyMember(Base):
    __tablename__ = "faculty_member"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    affiliation_status: Mapped[AffiliationStatus | None] = mapped_column(
        pg_enum(AffiliationStatus, "affiliation_status")
    )

    # Published obfuscated as `name(at)ufscar.br`; stored normalised.
    email: Mapped[str | None] = mapped_column(String(200))

    # "Faculty of PPGCC" is not "employed by UFSCar": one member's e-mail is
    # @icmc.usp.br and another's is @embrapa.br. Matters once ICMC-USP is added
    # and the same person may appear in two programs.
    external_affiliation: Mapped[str | None] = mapped_column(String(200))

    notes: Mapped[str | None] = mapped_column(Text)

    research_lines: Mapped[list[ResearchLine]] = relationship(
        secondary="faculty_research_line", back_populates="faculty"
    )
    links: Mapped[list[FacultyLink]] = relationship(
        back_populates="faculty", cascade="all, delete-orphan"
    )


class FacultyLink(Base):
    __tablename__ = "faculty_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty_member.id"))
    kind: Mapped[LinkKind] = mapped_column(pg_enum(LinkKind, "link_kind"))
    url: Mapped[str] = mapped_column(Text)

    faculty: Mapped[FacultyMember] = relationship(back_populates="links")
