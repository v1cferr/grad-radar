"""Read-only API over the seeded domain.

F1 exposes only enough to verify that the model is useful. Mutation, auth and
scoring belong to later phases — this is still a research tool with two users.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import Session
from app.models import (
    AdmissionCycle,
    Campus,
    Candidate,
    CourseOffering,
    Department,
    FacultyMember,
    GraduateProgram,
    ResearchLine,
)

# The whole chain must be eager-loaded: an async session raises on lazy access
# outside a greenlet, so a forgotten link here becomes a 500 at request time.
_PROGRAM_LOADERS = (
    selectinload(GraduateProgram.research_lines).selectinload(ResearchLine.faculty),
    selectinload(GraduateProgram.department)
    .selectinload(Department.campus)
    .selectinload(Campus.institution),
)

router = APIRouter(prefix="/api")


async def get_session() -> AsyncSession:  # pragma: no cover - trivial wiring
    async with Session() as session:
        yield session


Db = Annotated[AsyncSession, Depends(get_session)]


# ── response shapes ──────────────────────────────────────────────────────────


class LinkOut(BaseModel):
    kind: str
    url: str


class FacultyOut(BaseModel):
    id: int
    name: str
    affiliation_status: str | None
    email: str | None
    external_affiliation: str | None
    research_lines: list[str]
    links: list[LinkOut]


class ResearchLineOut(BaseModel):
    id: int
    acronym: str
    name: str
    faculty_count: int


class ProgramOut(BaseModel):
    id: int
    name: str
    acronym: str
    website: str | None
    capes_rating: int | None
    tuition_free: bool | None
    institution: str
    campus: str
    research_lines: list[ResearchLineOut]


class StageOut(BaseModel):
    ordinal: int
    name: str
    starts_on: date | None
    ends_on: date | None
    result_on: date | None


class SeatOut(BaseModel):
    research_line: str | None
    seats: int


class CycleOut(BaseModel):
    id: int
    program: str
    year: int
    semester: int
    entry_mode: str
    degree_level: str | None
    applications_open_on: date | None
    applications_close_on: date | None
    site_label: str | None
    official_url: str | None
    status: str
    total_seats: int
    seats: list[SeatOut]
    stages: list[StageOut]
    required_documents: list[str]


class OfferingOut(BaseModel):
    id: int
    code: str
    name: str
    name_en: str | None
    credits: int | None
    year: int
    semester: int
    weekday: str | None
    starts_at: time | None
    ends_at: time | None
    language: str | None
    scope: str | None
    research_line: str | None
    professor: str | None
    locations: list[str]
    # None means "schedule unknown" — deliberately not False. See
    # CourseOffering.overlaps: not knowing is not the same as not conflicting.
    conflicts_with_work: bool | None


# ── endpoints ────────────────────────────────────────────────────────────────


@router.get("/programs", response_model=list[ProgramOut])
async def list_programs(db: Db) -> list[ProgramOut]:
    stmt = select(GraduateProgram).options(*_PROGRAM_LOADERS)
    programs = (await db.scalars(stmt)).all()
    return [_program_out(p) for p in programs]


@router.get("/programs/{program_id}", response_model=ProgramOut)
async def get_program(program_id: int, db: Db) -> ProgramOut:
    stmt = (
        select(GraduateProgram).where(GraduateProgram.id == program_id).options(*_PROGRAM_LOADERS)
    )
    program = (await db.scalars(stmt)).first()
    if program is None:
        raise HTTPException(status_code=404, detail="program not found")
    return _program_out(program)


def _program_out(p: GraduateProgram) -> ProgramOut:
    campus_obj = p.department.campus
    institution = campus_obj.institution
    return ProgramOut(
        id=p.id,
        name=p.name,
        acronym=p.acronym,
        website=p.website,
        capes_rating=p.capes_rating,
        tuition_free=p.tuition_free,
        institution=institution.acronym,
        campus=campus_obj.name,
        research_lines=[
            ResearchLineOut(
                id=line.id, acronym=line.acronym, name=line.name, faculty_count=len(line.faculty)
            )
            for line in sorted(p.research_lines, key=lambda x: x.acronym)
        ],
    )


@router.get("/research-lines", response_model=list[ResearchLineOut])
async def list_research_lines(db: Db) -> list[ResearchLineOut]:
    stmt = select(ResearchLine).options(selectinload(ResearchLine.faculty)).order_by(ResearchLine.acronym)
    return [
        ResearchLineOut(id=x.id, acronym=x.acronym, name=x.name, faculty_count=len(x.faculty))
        for x in (await db.scalars(stmt)).all()
    ]


@router.get("/faculty", response_model=list[FacultyOut])
async def list_faculty(
    db: Db,
    line: Annotated[str | None, Query(description="filter by research line acronym")] = None,
) -> list[FacultyOut]:
    stmt = (
        select(FacultyMember)
        .options(selectinload(FacultyMember.research_lines), selectinload(FacultyMember.links))
        .order_by(FacultyMember.name)
    )
    members = (await db.scalars(stmt)).all()
    if line:
        wanted = line.upper()
        members = [m for m in members if any(x.acronym == wanted for x in m.research_lines)]
    return [
        FacultyOut(
            id=m.id,
            name=m.name,
            affiliation_status=m.affiliation_status,
            email=m.email,
            external_affiliation=m.external_affiliation,
            research_lines=[x.acronym for x in m.research_lines],
            links=[LinkOut(kind=link.kind, url=link.url) for link in m.links],
        )
        for m in members
    ]


@router.get("/admission-cycles", response_model=list[CycleOut])
async def list_admission_cycles(db: Db) -> list[CycleOut]:
    stmt = (
        select(AdmissionCycle)
        .options(
            selectinload(AdmissionCycle.stages),
            selectinload(AdmissionCycle.seats),
            selectinload(AdmissionCycle.required_documents),
            selectinload(AdmissionCycle.program),
        )
        .order_by(AdmissionCycle.year.desc(), AdmissionCycle.semester.desc())
    )
    cycles = (await db.scalars(stmt)).all()
    lines = {x.id: x.acronym for x in (await db.scalars(select(ResearchLine))).all()}
    # UTC-anchored: `date.today()` reads the container's clock, and a deadline
    # that shifts with the host timezone is a deadline you cannot trust.
    today = datetime.now(UTC).date()
    return [
        CycleOut(
            id=c.id,
            program=c.program.acronym,
            year=c.year,
            semester=c.semester,
            entry_mode=c.entry_mode,
            degree_level=c.degree_level,
            applications_open_on=c.applications_open_on,
            applications_close_on=c.applications_close_on,
            site_label=c.site_label,
            official_url=c.official_url,
            status=c.status_on(today),
            total_seats=sum(s.seats for s in c.seats),
            seats=[
                SeatOut(research_line=lines.get(s.research_line_id), seats=s.seats)
                for s in sorted(c.seats, key=lambda s: -s.seats)
            ],
            stages=[
                StageOut(
                    ordinal=s.ordinal,
                    name=s.name,
                    starts_on=s.starts_on,
                    ends_on=s.ends_on,
                    result_on=s.result_on,
                )
                for s in c.stages
            ],
            required_documents=[d.name for d in c.required_documents],
        )
        for c in cycles
    ]


@router.get("/offerings", response_model=list[OfferingOut])
async def list_offerings(
    db: Db,
    year: int | None = None,
    semester: int | None = None,
    candidate: Annotated[str | None, Query(description="name; computes schedule conflict")] = None,
) -> list[OfferingOut]:
    """The weekly grid — and whether each slot collides with a candidate's job."""
    stmt = select(CourseOffering).options(
        selectinload(CourseOffering.discipline),
        selectinload(CourseOffering.locations),
    )
    if year:
        stmt = stmt.where(CourseOffering.year == year)
    if semester:
        stmt = stmt.where(CourseOffering.semester == semester)
    offerings = (await db.scalars(stmt)).all()

    work_start: time | None = None
    work_end: time | None = None
    if candidate:
        who = (
            await db.scalars(select(Candidate).where(Candidate.name.ilike(candidate)))
        ).first()
        if who is not None:
            work_start, work_end = who.work_starts_at, who.work_ends_at

    lines = {x.id: x.acronym for x in (await db.scalars(select(ResearchLine))).all()}
    people = {x.id: x.name for x in (await db.scalars(select(FacultyMember))).all()}

    out: list[OfferingOut] = []
    for o in offerings:
        conflict: bool | None = None
        if work_start and work_end:
            conflict = o.overlaps(work_start, work_end)
        out.append(
            OfferingOut(
                id=o.id,
                code=o.discipline.code,
                name=o.discipline.name,
                name_en=o.discipline.name_en,
                credits=o.discipline.credits,
                year=o.year,
                semester=o.semester,
                weekday=o.weekday,
                starts_at=o.starts_at,
                ends_at=o.ends_at,
                language=o.language,
                scope=o.scope,
                research_line=lines.get(o.research_line_id),
                professor=people.get(o.faculty_id),
                locations=[
                    f"{loc.room}" for loc in o.locations if loc.room
                ],
                conflicts_with_work=conflict,
            )
        )
    return out
