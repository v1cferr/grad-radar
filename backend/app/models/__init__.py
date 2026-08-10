"""Domain models.

Importing this package registers every mapper on ``Base.metadata`` — which is
what Alembic's autogenerate reads. A model that is not re-exported here is
invisible to migrations, so new modules must be added below.
"""

from app.models.academic import (
    AffiliationStatus,
    Campus,
    Department,
    FacultyLink,
    FacultyMember,
    FacultyResearchLine,
    GraduateProgram,
    Institution,
    LinkKind,
    ResearchLine,
)
from app.models.admission import (
    AdmissionCycle,
    AdmissionNotice,
    AdmissionNoticeVersion,
    AdmissionSeat,
    AdmissionStage,
    CycleStatus,
    DegreeLevel,
    EntryMode,
    RequiredDocument,
)
from app.models.candidate import Candidate, CandidateInterest
from app.models.curriculum import (
    CourseOffering,
    Discipline,
    DisciplineGroup,
    Language,
    OfferingLocation,
    OfferingScope,
    Weekday,
)
from app.models.eligibility import (
    AdherenceLevel,
    AdherenceSignal,
    ProgramAdherence,
    ProgramRequirement,
    ProgramVerdict,
    Requirement,
    RequirementStatus,
    adherence_index,
    verdict_for,
)
from app.models.provenance import Source, SourceSnapshot, SourceType

__all__ = [
    "AdherenceLevel",
    "AdherenceSignal",
    "AdmissionCycle",
    "AdmissionNotice",
    "AdmissionNoticeVersion",
    "AdmissionSeat",
    "AdmissionStage",
    "AffiliationStatus",
    "Campus",
    "Candidate",
    "CandidateInterest",
    "CourseOffering",
    "CycleStatus",
    "DegreeLevel",
    "Department",
    "Discipline",
    "DisciplineGroup",
    "EntryMode",
    "FacultyLink",
    "FacultyMember",
    "FacultyResearchLine",
    "GraduateProgram",
    "Institution",
    "Language",
    "LinkKind",
    "OfferingLocation",
    "OfferingScope",
    "ProgramAdherence",
    "ProgramRequirement",
    "ProgramVerdict",
    "RequiredDocument",
    "Requirement",
    "RequirementStatus",
    "ResearchLine",
    "Source",
    "SourceSnapshot",
    "SourceType",
    "Weekday",
    "adherence_index",
    "verdict_for",
]
