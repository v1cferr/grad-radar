"""Deterministic, idempotent seed of verified PPGCC/UFSCar data.

Every row here was read from an official source and is documented in
`docs/research/ufscar-ppgcc.md`. Nothing is inferred: fields the sources do not
state are left NULL, which in this schema means *unknown*, not *no*.

Rerunnable by design — it upserts on natural keys, so `just seed` twice leaves
the database identical.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import Session
from app.models import (
    AdmissionCycle,
    AdmissionNotice,
    AdmissionSeat,
    AdmissionStage,
    AffiliationStatus,
    Campus,
    Candidate,
    CandidateInterest,
    CourseOffering,
    Department,
    Discipline,
    DisciplineGroup,
    EntryMode,
    FacultyLink,
    FacultyMember,
    GraduateProgram,
    Institution,
    Language,
    LinkKind,
    OfferingLocation,
    OfferingScope,
    RequiredDocument,
    ResearchLine,
    Source,
    SourceType,
    Weekday,
)

PPGCC_URL = "https://www.ppgcc.ufscar.br/pt-br"

# acronym, official name (VERIFIED), plain-language gloss (EDITORIAL)
#
# The official page publishes names only — no descriptions. The third field is
# therefore OURS, written to make the acronyms legible to someone outside
# computing, and it is presented in the UI as an explanation, never as a quote.
# What grounds each tooltip is the verified data next to it: how many faculty the
# line has and which disciplines it actually offered this term.
RESEARCH_LINES: list[tuple[str, str, str]] = [
    (
        "AMPLN",
        "Aprendizado de Máquina e Processamento de Língua Natural",
        (
            "Ensinar computadores a aprender padrões a partir de dados, e a interpretar e "
            "gerar linguagem humana. É a linha de IA no sentido corrente do termo — inclui "
            "os modelos de linguagem."
        ),
    ),
    (
        "BD",
        "Banco de Dados",
        (
            "Como armazenar, indexar e consultar grandes volumes de dados de forma "
            "eficiente e confiável."
        ),
    ),
    (
        "CCH",
        "Computação Centrada no Humano",
        (
            "Como as pessoas de fato usam os sistemas: interface, usabilidade, "
            "acessibilidade e o efeito do software sobre quem o opera."
        ),
    ),
    (
        "ES",
        "Engenharia de Software",
        (
            "Como construir software de forma sistemática — arquitetura, testes, "
            "manutenção e qualidade ao longo do tempo, não só fazer funcionar."
        ),
    ),
    (
        "SAR",
        "Sistemas de Automação e Robótica",
        (
            "Máquinas que percebem o ambiente e agem sobre ele: robôs, drones, controle e "
            "automação industrial."
        ),
    ),
    (
        "SDARC",
        "Sistemas Distribuídos, Arquiteturas e Redes de Computadores",
        (
            "Sistemas que rodam em muitas máquinas ao mesmo tempo: redes, computação de "
            "alto desempenho, nuvem e a infraestrutura por baixo delas."
        ),
    ),
    (
        "VC",
        "Visão Computacional",
        (
            "Extrair informação de imagens e vídeo — reconhecer objetos, segmentar, "
            "classificar. Usa muito aprendizado profundo, então encosta em IA por outro "
            "caminho."
        ),
    ),
]

P, C, S = AffiliationStatus.PERMANENT, AffiliationStatus.COLLABORATOR, AffiliationStatus.SENIOR_PERMANENT

# name, status, lines, email, (link kind, url)
FACULTY: list[tuple[str, AffiliationStatus, list[str], str | None, tuple[LinkKind, str] | None] ] = [
    ("Alan Demétrius Baria Valejo", P, ["AMPLN"], "alanvalejo@ufscar.br", (LinkKind.PERSONAL, "http://www2.dc.ufscar.br/~alanvalejo/")),
    ("Alexandre Luís Magalhães Levada", P, ["VC"], "alexandre.levada@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/3341441596395463")),
    ("André Ricardo Backes", P, ["VC"], "arbackes@yahoo.com.br", (LinkKind.OTHER, "http://linktr.ee/progdescomplicada")),
    ("André Takeshi Endo", P, ["ES"], "andreendo@ufscar.br", (LinkKind.PERSONAL, "https://andreendo.github.io/")),
    ("Auri Marcelo Rizzo Vincenzi", P, ["BD", "ES"], "auri@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/0611351138131709")),
    ("Celso Jorge Villas-Bôas", P, ["SDARC"], "celsoboas@ufscar.br", None),
    ("Cesar Henrique Comin", P, ["VC"], "comin@ufscar.br", (LinkKind.LABORATORY, "https://www.inag.ufscar.br/")),
    ("Daniel Lucrédio", P, ["ES"], "daniel.lucredio@ufscar.br", (LinkKind.PERSONAL, "http://www2.dc.ufscar.br/~daniel/")),
    ("Diego Furtado Silva", C, ["AMPLN"], "diegofsilva@icmc.usp.br", (LinkKind.PERSONAL, "https://sites.google.com/view/diegofsilva")),
    ("Emerson Carlos Pedrino", P, ["SDARC"], "emerson@dc.ufscar.br", (LinkKind.PERSONAL, "https://www2.dc.ufscar.br/~emerson")),
    ("Fabiano Cutigi Ferrari", P, ["ES"], "fcferrari@ufscar.br", (LinkKind.LABORATORY, "http://lapes.dc.ufscar.br/members/faculties/fabiano-ferrari")),
    ("Fabio Luciano Verdi", P, ["SDARC"], "verdi@ufscar.br", (LinkKind.PERSONAL, "https://www.dcomp.ufscar.br/verdi/")),
    ("Helena de Medeiros Caseli", P, ["AMPLN"], "helenacaseli@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/6608582057810385")),
    ("Hélio Crestana Guardia", C, ["SDARC"], "helio.guardia@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/1780902767520967")),
    ("Heloisa de Arruda Camargo", P, ["AMPLN"], "heloisacamargo@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/0487231065057783")),
    ("Hermes Senger", C, ["SDARC"], "hermes@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/3691742159298316")),
    ("Joice Lee Otsuka", C, ["CCH"], "joice@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/8235968002513082")),
    ("Jurandy Gomes de Almeida Junior", P, ["VC"], "jurandy.almeida@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/4495269939725770")),
    ("Kelen Cristiane Teixeira Vivaldini", P, ["SAR"], "vivaldini@ufscar.br", (LinkKind.LABORATORY, "http://www.laris.ufscar.br/pt-br/pessoal/kelen_cristiane_teixeira_vivaldini")),
    ("Luciana Aparecida Martinez Zaina", P, ["CCH"], "lzaina@ufscar.br", (LinkKind.LABORATORY, "https://uxleris.dcomp.ufscar.br/lzaina/")),
    ("Marcela Xavier Ribeiro", C, ["BD"], "marcelaxr@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/0300141044144026")),
    ("Marilde Terezinha Prado Santos", S, ["BD"], "marilde.santos@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/9826026025118073")),
    ("Mário César San Felice", P, ["AMPLN"], "felice@ufscar.br", (LinkKind.PERSONAL, "https://www.aloc.ufscar.br/felice/")),
    ("Murilo Coelho Naldi", P, ["AMPLN"], "naldi@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/7924553462118511")),
    ("Orides Morandin Junior", P, ["SAR"], "orides@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/4192845106907956")),
    ("Paulo Estevão Cruvinel", C, [], "paulo.cruvinel@embrapa.br", (LinkKind.LATTES, "http://lattes.cnpq.br/7924553462118511")),
    ("Paulo Matias", C, ["SDARC"], "matias@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/3792055796261017")),
    ("Pedro Henrique Bugatti", P, ["VC"], "pedrobugatti@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/2177467029991118")),
    ("Priscila Tiemi Maeda Saito", P, ["VC"], "priscilasaito@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/6652293216938994")),
    ("Rafael Vidal Aroca", C, ["SAR"], "aroca@ufscar.br", (LinkKind.LABORATORY, "https://www.laris.ufscar.br/pt-br/pessoal/rafael_vidal_aroca")),
    ("Renato Bueno", C, ["BD"], "renato@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/7189857417959804")),
    ("Ricardo Augusto Souza Fernandes", P, ["AMPLN"], "ricardo.asf@ufscar.br", (LinkKind.LABORATORY, "https://liaa2.webnode.com/")),
    ("Ricardo Cerri", P, ["AMPLN"], "cerri@ufscar.br", (LinkKind.LABORATORY, "http://www.biomal.ufscar.br/")),
    ("Ricardo José Ferrari", P, ["VC"], "rferrari@ufscar.br", (LinkKind.LABORATORY, "https://www.bipgroup.dc.ufscar.br/")),
    ("Ricardo Rodrigues Ciferri", P, ["BD"], "rrc@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/8382221522817502")),
    ("Roberto Santos Inoue", P, ["SAR"], "rsinoue@ufscar.br", (LinkKind.LABORATORY, "http://www.laris.ufscar.br/pt-br/pessoal/roberto_santos_inoue")),
    ("Tiago Agostinho de Almeida", P, ["AMPLN"], "talmeida@ufscar.br", (LinkKind.PERSONAL, "https://www.servidores.ufscar.br/talmeida/")),
    ("Valter Vieira de Camargo", P, ["ES"], "valtervcamargo@ufscar.br", (LinkKind.LABORATORY, "https://www.advanse.ufscar.br/")),
    ("Vânia Paula de Almeida Neris", P, ["CCH"], "vania.neris@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/0268728255033469")),
    ("Vinicius Humberto Serapilha Durelli", C, ["ES"], "vinicius.durelli@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/8816910024419957")),
    ("Wanderley Lopes de Souza", S, ["SDARC"], "desouza@ufscar.br", (LinkKind.LATTES, "http://lattes.cnpq.br/3742302894743620")),
]

# The 2026/2 weekly grid, transcribed from the rendered PDF page.
# (code, name, name_en, group, weekday, band, professor, scope, line, language,
#  origin campus, origin room, other campus, other room)
MORNING = (time(8, 0), time(12, 0))
AFTERNOON = (time(14, 0), time(18, 0))
SC, SO = "São Carlos", "Sorocaba"

OFFERINGS = [
    ("CCO-310", "Metodologia de Pesquisa", "Research Methodology", "IV", Weekday.MONDAY, MORNING,
     "Heloisa de Arruda Camargo", OfferingScope.BASICA, None, Language.EN, SC, "Auditório", SO, "CCGT-1001"),
    ("CCO-129-7", "Introdução à Computação de Alto Desempenho", "Introduction to High Performance Computing", "III", Weekday.TUESDAY, MORNING,
     "Hélio Crestana Guardia", OfferingScope.ESPECIFICA, "SDARC", Language.EN, SC, "LE 6", SO, "CCGT-1001"),
    ("CCO-740", "Reconhecimento de Padrões", "Pattern Recognition", "II", Weekday.TUESDAY, MORNING,
     "Alexandre Luís Magalhães Levada", OfferingScope.ESPECIFICA, "VC", Language.EN, SC, "Auditório", SO, "CCGT-1001"),
    ("CCO-410", "Aspectos Formais da Computação", None, "I", Weekday.WEDNESDAY, MORNING,
     "Wanderley Lopes de Souza", OfferingScope.BASICA, None, Language.PT_BR, SC, "Sala 2", SO, "CCGT-1001"),
    ("CCO-04.1.02", "Tópicos em Sistemas Distribuídos e Redes: Computação Ubíqua, Computação Pervasiva e Internet das Coisas", "Topics in Distributed Systems and Networks", "III", Weekday.THURSDAY, MORNING,
     "Wanderley Lopes de Souza", OfferingScope.ESPECIFICA, "SDARC", Language.PT_BR, SC, "Sala 2", SO, "CCGT-1001"),
    ("CCO-04.2.01", "Segurança Cibernética", "Cybersecurity", "III", Weekday.FRIDAY, MORNING,
     "Paulo Matias", OfferingScope.ESPECIFICA, "SDARC", Language.PT_BR, SC, "Auditório", SO, "CCGT-1001"),
    ("CCO-741", "Processamento Digital de Imagens", "Digital Image Processing", "II", Weekday.MONDAY, AFTERNOON,
     "Ricardo José Ferrari", OfferingScope.ESPECIFICA, "VC", Language.PT_BR, SC, "LE 6", SO, "CCGT-1001"),
    # Origin campus is SOROCABA for this one — São Carlos is the remote end.
    ("CCO-724", "Aprendizado de Máquina", "Machine Learning", "II", Weekday.TUESDAY, AFTERNOON,
     "Tiago Agostinho de Almeida", OfferingScope.ESPECIFICA, "AMPLN", Language.PT_BR, SO, "CCGT-1001", SC, "Sala 2"),
    ("CCO-00.2.01", "Projeto e Análise de Algoritmos", "Design and Analysis of Algorithms", "I", Weekday.TUESDAY, AFTERNOON,
     "Alan Demétrius Baria Valejo", OfferingScope.BASICA, None, Language.PT_BR, SC, "Auditório", SO, "CCGT-1001"),
    ("CCO-00.2.03", "Seminários II", "Seminars II", "IV", Weekday.WEDNESDAY, AFTERNOON,
     "Fabiano Cutigi Ferrari", OfferingScope.BASICA, None, Language.EN, SC, "Auditório", SO, "CCGT-1001"),
    ("CCO-220", "Desenvolvimento de Software Orientado a Objetos", "Object Oriented Software Development", "II", Weekday.THURSDAY, AFTERNOON,
     "Valter Vieira de Camargo", OfferingScope.ESPECIFICA, "ES", Language.EN, SC, "LE 6", SO, "CCGT-1001"),
    ("CCO-03.2.02", "Aprendizado Profundo para Reconhecimento Visual", "Deep Learning for Visual Recognition", "II", Weekday.THURSDAY, AFTERNOON,
     "Jurandy Gomes de Almeida Junior", OfferingScope.ESPECIFICA, "VC", Language.PT_BR, SO, "CCGT-1001", SC, "Sala 2"),
    ("CCO-03.2.01", "Filtragem: Princípios e Aplicações", "Filtering: Principles and Applications", "II", Weekday.FRIDAY, AFTERNOON,
     "Roberto Santos Inoue", OfferingScope.ESPECIFICA, "SAR", Language.EN, SC, "LE 6", SO, "CCGT-1001"),
]

# Edital 02/2026, read from the SEI PDF.
SEATS = {"AMPLN": 4, "VC": 7, "SDARC": 7, "SAR": 2, "BD": 1, "ES": 1, "CCH": 1}

STAGES = [
    (1, "Análise documental", date(2026, 5, 13), date(2026, 5, 19), date(2026, 6, 24)),
    (2, "Entrevista estruturada", date(2026, 6, 7), date(2026, 6, 20), date(2026, 6, 24)),
]

DOCUMENTS = [
    ("Diploma de graduação ou certificado de conclusão", True),
    ("Histórico escolar oficial", True),
    ("Currículo Lattes", True),
    ("Documento de identidade", True),
    ("Carta de apresentação (máx. 800 palavras)", True),
    ("Comprovante de endereço", True),
    ("Certificado de proficiência em língua estrangeira", False),
    ("Certificado de proficiência em computação", False),
]

SOURCES = [
    (PPGCC_URL, SourceType.GRADUATE_PROGRAM_PAGE, "PPGCC — página inicial", None),
    (f"{PPGCC_URL}/programa/linhas-de-pesquisa", SourceType.GRADUATE_PROGRAM_PAGE, "Linhas de pesquisa", None),
    (f"{PPGCC_URL}/programa/docentes", SourceType.FACULTY_PAGE, "Docentes", None),
    (f"{PPGCC_URL}/processo-seletivo/mestrado", SourceType.ADMISSION_PAGE, "Processo seletivo — mestrado", None),
    (f"{PPGCC_URL}/processo-seletivo/mestrado/2026-2o-semestre", SourceType.ADMISSION_PAGE, "Mestrado 2026/2", None),
    (f"{PPGCC_URL}/processo-seletivo/aluno-especial", SourceType.ADMISSION_PAGE, "Aluno especial", None),
    (f"{PPGCC_URL}/programa/estrutura-curricular/disciplinas-do-programa_apos_jul_24", SourceType.COURSE_CATALOG, "Disciplinas (ingressantes após jul/24)", None),
    # The page is a 302 to SEI — recorded so a collector knows to follow it.
    (f"{PPGCC_URL}/programa/estrutura-curricular/disciplina-do-semestre", SourceType.SCHEDULE_PDF,
     "Calendário e disciplinas do semestre 2/2026", "https://sei.ufscar.br/sei/modulos/pesquisa/md_pesq_documento_consulta_externa.php"),
]


async def _get_or_create(db: AsyncSession, model, defaults: dict | None = None, **keys):
    obj = (await db.scalars(select(model).filter_by(**keys))).first()
    if obj is None:
        obj = model(**keys, **(defaults or {}))
        db.add(obj)
        await db.flush()
    elif defaults:
        for k, v in defaults.items():
            setattr(obj, k, v)
    return obj


async def seed(db: AsyncSession) -> dict[str, int]:
    counts: dict[str, int] = {}

    ufscar = await _get_or_create(
        db, Institution, {"city": "São Carlos", "state": "SP", "website": "https://www.ufscar.br"},
        name="Universidade Federal de São Carlos", acronym="UFSCar",
    )
    sc = await _get_or_create(
        db, Campus, {"address": "Rodovia Washington Luís, km 235 — São Carlos/SP"},
        institution_id=ufscar.id, name=SC,
    )
    so = await _get_or_create(db, Campus, {}, institution_id=ufscar.id, name=SO)
    dc = await _get_or_create(
        db, Department, {"acronym": "DC", "website": "https://www.dc.ufscar.br"},
        campus_id=sc.id, name="Departamento de Computação",
    )
    ppgcc = await _get_or_create(
        db, GraduateProgram,
        {
            "department_id": dc.id,
            "name": "Programa de Pós-Graduação em Ciência da Computação",
            "website": PPGCC_URL,
            "capes_rating": 5,
            # NULL = unknown. No consulted page states tuition status.
            "tuition_free": None,
        },
        acronym="PPGCC",
    )

    lines: dict[str, ResearchLine] = {}
    for acronym, name, description in RESEARCH_LINES:
        lines[acronym] = await _get_or_create(
            db, ResearchLine, {"name": name, "description": description},
            program_id=ppgcc.id, acronym=acronym,
        )
    counts["research_lines"] = len(lines)

    people: dict[str, FacultyMember] = {}
    for name, status, line_acronyms, email, link in FACULTY:
        external = None
        if email and not email.endswith("ufscar.br"):
            external = email.split("@")[-1]
        # Collections are eager-loaded on purpose: assigning to a relationship of
        # a persistent object first READS the current one, and an async session
        # cannot lazy-load — it raises MissingGreenlet.
        stmt = (
            select(FacultyMember)
            .options(selectinload(FacultyMember.research_lines), selectinload(FacultyMember.links))
            .where(FacultyMember.name == name)
        )
        member = (await db.scalars(stmt)).first()
        wanted_lines = [lines[a] for a in line_acronyms]
        if member is None:
            member = FacultyMember(
                name=name,
                affiliation_status=status,
                email=email,
                external_affiliation=external,
                research_lines=wanted_lines,
                links=[FacultyLink(kind=link[0], url=link[1])] if link else [],
            )
            db.add(member)
        else:
            member.affiliation_status = status
            member.email = email
            member.external_affiliation = external
            member.research_lines = wanted_lines
            if link and not member.links:
                member.links.append(FacultyLink(kind=link[0], url=link[1]))
        people[name] = member
    await db.flush()
    counts["faculty"] = len(people)

    campuses = {SC: sc, SO: so}
    for (code, name, name_en, group, weekday, band, prof, scope, line, lang,
         origin_campus, origin_room, other_campus, other_room) in OFFERINGS:
        disc = await _get_or_create(
            db, Discipline,
            {"name": name, "name_en": name_en, "credits": 8, "group": DisciplineGroup(group)},
            program_id=ppgcc.id, code=code, curriculum_version="apos_jul_24",
        )
        offering = await _get_or_create(
            db, CourseOffering,
            {
                "faculty_id": people[prof].id,
                "scope": scope,
                "research_line_id": lines[line].id if line else None,
                "weekday": weekday,
                "starts_at": band[0],
                "ends_at": band[1],
                "language": lang,
                "notes": "Todas as avaliações são integralmente presenciais no departamento.",
            },
            discipline_id=disc.id, year=2026, semester=2,
        )
        # Counted with a query rather than `offering.locations`: touching the
        # collection would lazy-load (see the faculty loop above).
        has_locations = (
            await db.scalars(
                select(OfferingLocation.id).where(OfferingLocation.offering_id == offering.id)
            )
        ).first()
        if has_locations is None:
            db.add(OfferingLocation(offering_id=offering.id, campus_id=campuses[origin_campus].id,
                                    room=origin_room, is_origin=True))
            db.add(OfferingLocation(offering_id=offering.id, campus_id=campuses[other_campus].id,
                                    room=other_room, is_origin=False))
    await db.flush()
    counts["offerings"] = len(OFFERINGS)

    cycle = await _get_or_create(
        db, AdmissionCycle,
        {
            "applications_open_on": date(2026, 3, 19),
            "applications_close_on": date(2026, 4, 26),
            "site_label": "Processo vigente",
            "official_url": f"{PPGCC_URL}/processo-seletivo/mestrado/2026-2o-semestre",
            "notes": "Reserva: 20% pretos e pardos, 5% PcD, 1 vaga indígena. "
                     "Proficiência em língua estrangeira é exigida APÓS a aprovação, não na inscrição.",
        },
        program_id=ppgcc.id, year=2026, semester=2, entry_mode=EntryMode.REGULAR,
    )
    cycle.degree_level = "master"
    for ordinal, name, starts, ends, result in STAGES:
        await _get_or_create(
            db, AdmissionStage, {"name": name, "starts_on": starts, "ends_on": ends, "result_on": result},
            cycle_id=cycle.id, ordinal=ordinal,
        )
    for acronym, seats in SEATS.items():
        await _get_or_create(
            db, AdmissionSeat, {"seats": seats}, cycle_id=cycle.id, research_line_id=lines[acronym].id
        )
    existing_docs = {d.name for d in (await db.scalars(
        select(RequiredDocument).where(RequiredDocument.cycle_id == cycle.id))).all()}
    for name, mandatory in DOCUMENTS:
        if name not in existing_docs:
            db.add(RequiredDocument(cycle_id=cycle.id, name=name, mandatory=mandatory))
    await _get_or_create(
        db, AdmissionNotice, {"title": "Edital 02/2026 — Processo Seletivo Mestrado 2026/2"},
        cycle_id=cycle.id, number="02/2026",
    )
    counts["admission_cycles"] = 1

    for url, kind, title, redirect in SOURCES:
        await _get_or_create(
            db, Source,
            {"source_type": kind, "title": title, "institution_id": ufscar.id,
             "redirects_to": redirect, "last_checked_at": datetime(2026, 8, 8, tzinfo=UTC)},
            url=url,
        )
    counts["sources"] = len(SOURCES)

    victor = await _get_or_create(
        db, Candidate,
        {"employer": "FAI-UFSCar", "work_starts_at": time(8, 0), "work_ends_at": time(18, 0),
         "notes": "Trabalha com adoção institucional de IA e integração de LLMs."},
        name="Victor",
    )
    jp = await _get_or_create(
        db, Candidate, {"work_starts_at": time(8, 0), "work_ends_at": time(18, 0)}, name="João Pedro"
    )
    cesar = await _get_or_create(
        db, Candidate, {"work_starts_at": time(8, 0), "work_ends_at": time(18, 0)}, name="César"
    )
    for cand, topics in (
        (victor, ["Artificial Intelligence", "Machine Learning", "NLP", "LLMs",
                  "Information Retrieval", "AI agents", "Software Engineering", "AI infrastructure"]),
        (jp, ["Artificial Intelligence", "Machine Learning"]),
        (cesar, ["Artificial Intelligence", "Machine Learning"]),
    ):
        have = {i.topic for i in (await db.scalars(
            select(CandidateInterest).where(CandidateInterest.candidate_id == cand.id))).all()}
        for topic in topics:
            if topic not in have:
                db.add(CandidateInterest(candidate_id=cand.id, topic=topic))
    counts["candidates"] = 3

    await db.commit()
    return counts


async def main() -> None:
    async with Session() as db:
        counts = await seed(db)
    for key, value in counts.items():
        print(f"  {key:20s} {value}")


if __name__ == "__main__":
    asyncio.run(main())
