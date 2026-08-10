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
    AdherenceLevel,
    AdherenceSignal,
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
    ProgramAdherence,
    ProgramRequirement,
    RequiredDocument,
    Requirement,
    RequirementStatus,
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


# ── PPGPEP — o único programa que passa nos requisitos eliminatórios ─────────
# Mestrado PROFISSIONAL em Engenharia de Produção. Aulas à noite, de segunda a
# sexta; "Pós-Graduação Stricto Sensu 100% gratuita" (portfólio oficial).
# Ver docs/research/ufscar-oferta-noturna.md.
PPGPEP_URL = "https://www.ppgpep.ufscar.br/pt-br"

PPGPEP_LINES: list[tuple[str, str, str]] = [
    (
        "PCsP",
        "Planejamento e Controle de Sistemas Produtivos",
        (
            "Como planejar e controlar a produção: capacidade, estoques, programação "
            "e a operação do dia a dia."
        ),
    ),
    (
        "GQ",
        "Gestão da Qualidade",
        "Métodos para medir, controlar e melhorar qualidade em processos e produtos.",
    ),
    (
        "TOTI",
        "Trabalho, Organizações, Tecnologia e Inovação",
        (
            "Como organizações adotam tecnologia e inovam — incluindo o efeito sobre "
            "o trabalho. É a linha mais próxima de adoção institucional de IA."
        ),
    ),
]

# Edital PPGPEP/UFSCar n. 001/2026, lido do PDF (digitalizado, sem camada de
# texto — foi preciso renderizar as páginas para ler).
PPGPEP_STAGES = [
    (1, "Avaliação do Projeto de Pesquisa", None, None, date(2026, 11, 6)),
    (2, "Defesa do Projeto de Pesquisa", date(2026, 11, 23), date(2026, 12, 1), date(2026, 12, 4)),
]

PPGPEP_DOCS = [
    ("Projeto de pesquisa", True),
    ("Diploma de graduação ou certificado de conclusão", True),
    ("Histórico escolar", True),
    ("Currículo Lattes", True),
    ("Documento de identidade", True),
    ("Declaração de vínculo com membros do corpo docente (Anexo II)", True),
]

# ── Índices de descoberta ────────────────────────────────────────────────────
# Não descrevem um programa: listam TODOS os de uma instituição. Uma mudança
# aqui pode ser um programa novo, e é o único jeito de descobrir uma opção sem
# alguém ir procurar à mão.
# ── MECAI/ICMC — o candidato do próximo ciclo ────────────────────────────────
# O processo 002/2026 fechou em 14/05/2026. Vigiado para pegar o próximo: é o
# programa de maior aderência técnica que ainda pode passar nos quatro requisitos.
MECAI_SOURCES = [
    ("https://www.icmc.usp.br/pos-graduacao/mecai/ingresso", SourceType.ADMISSION_PAGE,
     "MECAI — ingresso e processo seletivo", None),
    ("https://web2.icmc.usp.br/SVPGRAD/portal/mecai/editalmecai.pdf", SourceType.EDITAL_PDF,
     "MECAI — edital vigente (002/2026)", None),
    ("https://www.icmc.usp.br/pos-graduacao/mecai/perguntas-frequentes",
     SourceType.GRADUATE_PROGRAM_PAGE, "MECAI — perguntas frequentes", None),
    ("https://www.ppgads.ufscar.br/pt-br/processos-seletivos", SourceType.ADMISSION_PAGE,
     "PPGAdS — processos seletivos", None),
]

INDEX_SOURCES = [
    (
        "https://www.propg.ufscar.br/pt-br/pos-na-ufscar/programas",
        SourceType.PROGRAM_INDEX,
        "UFSCar ProPG — todos os programas de pós",
        None,
    ),
    (
        "https://www.icmc.usp.br/pos-graduacao",
        SourceType.PROGRAM_INDEX,
        "USP ICMC — pós-graduação",
        None,
    ),
]

PPGPEP_SOURCES = [
    (f"{PPGPEP_URL}/processo-seletivo/processo-seletivo", SourceType.ADMISSION_PAGE,
     "PPGPEP — processo seletivo", None),
    (f"{PPGPEP_URL}/o-programa", SourceType.GRADUATE_PROGRAM_PAGE, "PPGPEP — o programa", None),
    (f"{PPGPEP_URL}/informacoes-academicas/disciplinas", SourceType.COURSE_CATALOG,
     "PPGPEP — disciplinas", None),
    (f"{PPGPEP_URL}/informacoes-academicas/calendarios-e-horarios", SourceType.SCHEDULE_PDF,
     "PPGPEP — calendários e horários", None),
    ("https://www.ppgpep.ufscar.br/en/assets/arquivos/edital-ppgpep-2026.pdf",
     SourceType.EDITAL_PDF, "PPGPEP — Edital 001/2026 (ingresso 2027)", None),
]


# ── Vereditos eliminatórios ──────────────────────────────────────────────────
# Um programa por linha, com a EVIDÊNCIA de cada requisito. PPGEE e PIPGEs foram
# varridos e eliminados em docs/research/ufscar-oferta-noturna.md, mas nunca
# tinham entrado no banco — a lista de opções mostrava só o que já estava
# modelado, que é o oposto de uma lista de opções.
MORE_PROGRAMS: list[tuple[str, str, str, str, str]] = [
    (
        "PPGEE",
        "Departamento de Engenharia Elétrica",
        "DEE",
        "Programa de Pós-Graduação em Engenharia Elétrica",
        "https://www.ppgee.ufscar.br/pt-br",
    ),
    (
        "PIPGEs",
        "Departamento de Estatística",
        "DEs",
        "Programa Interinstitucional de Pós-Graduação em Estatística (UFSCar/USP)",
        "https://www.pipges.ufscar.br/pt-br",
    ),
]

# ── Varredura de 10/08/2026: os candidatos aderentes ao edital da FAI ────────
# Departamento, nome, site. Todos de São Carlos; os de Sorocaba/Araras/Lagoa do
# Sino falham no requisito 2 por definição e não entram.
SWEPT_PROGRAMS: list[tuple[str, str, str, str, str, str]] = [
    ("PPGCTS", "UFSCar", "Departamento de Ciência, Tecnologia e Sociedade", "DCTS",
     "Programa de Pós-Graduação em Ciência, Tecnologia e Sociedade",
     "https://www.ppgcts.ufscar.br/pt-br"),
    ("PPGCI", "UFSCar", "Departamento de Ciência da Informação", "DCI",
     "Programa de Pós-Graduação em Ciência da Informação",
     "https://www.ppgci.ufscar.br/pt-br"),
    ("PPGEP", "UFSCar", "Departamento de Engenharia de Produção", "DEP",
     "Programa de Pós-Graduação em Engenharia de Produção",
     "https://www.ppgep.ufscar.br/pt-br"),
    ("PPGAdS", "UFSCar", "Departamento de Administração e Sociedade", "DAdS",
     "Programa de Pós-Graduação Profissional em Administração e Sociedade",
     "https://www.ppgads.ufscar.br/pt-br"),
    ("MECAI", "USP", "Instituto de Ciências Matemáticas e de Computação", "ICMC",
     "Mestrado Profissional em Matemática, Estatística e Computação Aplicadas à Indústria",
     "https://www.icmc.usp.br/pos-graduacao/mecai"),
    ("CCMC", "USP", "Instituto de Ciências Matemáticas e de Computação", "ICMC",
     "Programa de Pós-Graduação em Ciências de Computação e Matemática Computacional",
     "https://www.icmc.usp.br/pos-graduacao"),
]

_NIGHT = Requirement.EVENING_CLASSES
_LOCAL = Requirement.IN_PERSON_SAO_CARLOS
_FREE = Requirement.TUITION_FREE
_PUBLIC = Requirement.PUBLIC_INSTITUTION
_MET, _NO, _UNK = RequirementStatus.MET, RequirementStatus.NOT_MET, RequirementStatus.UNKNOWN

REQUIREMENTS: dict[str, list[tuple[Requirement, RequirementStatus, str]]] = {
    "PPGCTS": [
        (_NIGHT, _NO, (
            "Quadro de Disciplinas 2026/2 (Ofício 96/2026/PPGCTS, SEI 2345246): 11 "
            "disciplinas em duas faixas só — 8h às 12h e 14h às 17h. Nenhuma menção a "
            "noite no documento."
        )),
        (_LOCAL, _MET, "Sala Multiuso do PPGCTS, campus São Carlos."),
        (_FREE, _UNK, "Não verificado — eliminado antes por horário."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "PPGCI": [
        (_NIGHT, _NO, (
            "Oferta 2026/1 (Deliberação 6/2025/PPGCI, SEI 2200336): as seis disciplinas "
            "com 'Horário de oferta: Manhã e Tarde', em blocos concentrados de dias "
            "seguidos. Exige dias inteiros de ausência, não só a tarde."
        )),
        (_LOCAL, _MET, "Campus São Carlos, com parte síncrona a distância."),
        (_FREE, _UNK, "Não verificado — eliminado antes por horário."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "PPGEP": [
        (_NIGHT, _NO, (
            "Horário de Disciplinas 2026/2: faixas 08h–12h, 10h–12h e 14h–18h em 10 "
            "disciplinas. A última TERMINA às 18h, quando a jornada acaba."
        )),
        (_LOCAL, _MET, "Campus São Carlos, mesmo departamento do PPGPEP."),
        (_FREE, _UNK, "Não verificado — eliminado antes por horário."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "PPGAdS": [
        (_NIGHT, _UNK, (
            "Edital 2025/1 item 2.2: aulas 'podendo ser oferecidas de segunda a "
            "sexta-feira (manhã, tarde ou noite)'. PERMITE noite, mas 'podendo ser' não "
            "compromete — falta a grade real de um semestre."
        )),
        (_LOCAL, _MET, "Edital 2.2: campus São Carlos, Rod. Washington Luís km 235."),
        (_FREE, _UNK, "Não verificado."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "MECAI": [
        (_NIGHT, _UNK, (
            "Edital 002/2026 item 7.1: as aulas da ênfase Ciência de Dados 'poderão ser "
            "oferecidas de segunda à quinta-feira no período NOTURNO ou às sextas-feiras "
            "(períodos da manhã, tarde e noite)', com possibilidade de sábado pela manhã. "
            "O edital vigente CONTEMPLA noturno — a FAQ do site, que só citava sextas, "
            "está desatualizada. Falta saber a oferta real de um semestre."
        )),
        (_LOCAL, _MET, "FAQ: 'As aulas presenciais são oferecidas na cidade de São Carlos – SP'."),
        (_FREE, _MET, (
            "FAQ: 'Os cursos de Pós-Graduação oferecidos pelo ICMC são gratuitos' e 'Não "
            "há taxa de matrícula para alunos regulares'. Há taxa de INSCRIÇÃO no "
            "processo (~R$ 214–259), com critérios de isenção — não é mensalidade."
        )),
        (_PUBLIC, _MET, "USP — universidade pública estadual."),
    ],
    "CCMC": [
        (_NIGHT, _UNK, "Não olhado. Programa acadêmico — mesmo perfil de risco do PPGCC."),
        (_LOCAL, _MET, "ICMC, campus USP São Carlos."),
        (_FREE, _MET, "FAQ do ICMC: os cursos de pós-graduação do instituto são gratuitos."),
        (_PUBLIC, _MET, "USP — universidade pública estadual."),
    ],
    "PPGCC": [
        (_NIGHT, _NO, (
            "Grade 2026/2 publica apenas 08:00–12:00 e 14:00–18:00 — as 13 disciplinas "
            "do semestre estão no banco e nenhuma começa às 18h."
        )),
        (_LOCAL, _MET, "Presencial em São Carlos; parte das disciplinas é espelhada em Sorocaba."),
        (_FREE, _UNK, (
            "Nenhuma página consultada afirma gratuidade. Programa federal, mas inferência "
            "não é fato."
        )),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "PPGEE": [
        (_NIGHT, _NO, (
            "Grade 2026/2: faixas 8:00–10:00, 10:00–12:00, 14:00–16:00 e 16:00–18:00. "
            "A última termina às 18h, exatamente quando a jornada acaba."
        )),
        (_LOCAL, _MET, "Presencial em São Carlos."),
        (_FREE, _UNK, "Não verificado — eliminado antes por horário."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
    "PIPGEs": [
        (_NIGHT, _NO, (
            "Grade 2026/2 vai de 08:00–09:40 a 16:00–17:40. Nada depois das 18h, apesar de "
            "ser o programa com linha explícita de Aprendizado de Máquina."
        )),
        (_LOCAL, _MET, "Presencial em São Carlos, interinstitucional UFSCar/USP."),
        (_FREE, _UNK, "Não verificado — eliminado antes por horário."),
        (_PUBLIC, _MET, "UFSCar e USP — ambas públicas."),
    ],
    "PPGPEP": [
        (_NIGHT, _MET, (
            "Programa Trilha Graduação: as aulas do mestrado profissional ocorrem à noite, "
            "de segunda a sexta; o diurno é complemento opcional."
        )),
        (_LOCAL, _MET, "Presencial no campus São Carlos da UFSCar."),
        (_FREE, _MET, "Portfólio oficial: \"Pós-Graduação Stricto Sensu 100% gratuita\"."),
        (_PUBLIC, _MET, "UFSCar — universidade federal."),
    ],
}


_ORG = AdherenceSignal.ORGANIZATIONAL_ADOPTION
_TECH = AdherenceSignal.TECHNICAL_AI
_DATA = AdherenceSignal.DATA_AND_PROCESS
_GOV = AdherenceSignal.GOVERNANCE
_TRAIN = AdherenceSignal.TRAINING
_S, _P, _A, _U = (
    AdherenceLevel.STRONG,
    AdherenceLevel.PARTIAL,
    AdherenceLevel.ABSENT,
    AdherenceLevel.UNKNOWN,
)

# Aderência ao item 4.1 do Edital FAI 001/2026. Ver docs/ADERENCIA.md para a régua
# e docs/PROGRAMAS.md para o veredito. `verified=False` quando o nível vem do
# escopo declarado e não de docente, disciplina ou projeto lido.
ADHERENCE: dict[str, list[tuple[AdherenceSignal, AdherenceLevel, bool, str]]] = {
    "PPGPEP": [
        (_ORG, _S, False, (
            "Linha TOTI — Trabalho, Organizações, Tecnologia e Inovação — descreve quase "
            "literalmente o item 4.1b. Escopo declarado; docentes e projetos não levantados."
        )),
        (_TECH, _A, True, (
            "Engenharia de produção profissional. Nenhuma disciplina de ML, PLN ou LLM "
            "no catálogo do programa."
        )),
        (_DATA, _S, False, "Linha PCsP: planejamento e controle de produção é sistematização de processos."),
        (_GOV, _U, False, "Não investigado."),
        (_TRAIN, _P, False, "Mestrado profissional tem transferência para a organização como propósito."),
    ],
    "PPGCC": [
        (_ORG, _A, True, "Programa de computação; nenhuma linha sobre organizações."),
        (_TECH, _S, True, (
            "Linha AMPLN com 9 docentes e disciplinas de ML e PLN ofertadas de fato em "
            "2026/2 — CCO-724 Aprendizado de Máquina está na grade lida."
        )),
        (_DATA, _P, True, "Linha BD — Banco de Dados; nenhuma disciplina ofertada em 2026/2."),
        (_GOV, _A, True, "Nada sobre regulação, LGPD ou risco no catálogo."),
        (_TRAIN, _A, True, "Nada de formação ou extensão."),
    ],
    "PPGCTS": [
        (_ORG, _S, False, "Ciência, Tecnologia e Sociedade: tecnologia em contexto organizacional é o objeto."),
        (_TECH, _A, True, "Nenhuma disciplina técnica de IA no quadro 2026/2."),
        (_DATA, _P, False, "Indicadores de C&T tocam organização de dados."),
        (_GOV, _S, False, (
            "O ÚNICO programa varrido cujo escopo cobre restrições ao uso de tecnologia "
            "— item 4.1d. É o que se perde com a eliminação por horário."
        )),
        (_TRAIN, _S, False, "Comunicação e publicação científica, PESCD: formação é parte do programa."),
    ],
    "PPGCI": [
        (_ORG, _P, False, "Gestão da Inovação está na oferta 2026/1."),
        (_TECH, _A, True, "Nenhuma disciplina de IA técnica na oferta lida."),
        (_DATA, _S, False, (
            "'Organização de informações' é o texto literal do item 2.2 do edital da FAI. "
            "É o núcleo da Ciência da Informação."
        )),
        (_GOV, _P, False, "Epistemologia e indicadores tocam governança sem ser o foco."),
        (_TRAIN, _P, False, "Mediação pedagógica e formação de usuários aparecem no programa."),
    ],
    "PPGEP": [
        (_ORG, _S, False, (
            "ENP 129 Tópicos Avançados em Governança e Organizações e ENP 191 Economia e "
            "Estratégia Empresarial estão na grade 2026/2 lida."
        )),
        (_TECH, _P, True, (
            "ENP 188 Ferramentas Computacionais para Planejamento e ENP 190 Métodos "
            "Estatísticos: computacional aplicado, não IA."
        )),
        (_DATA, _S, True, "Sequenciamento da produção, métodos estatísticos, eficiência — na grade."),
        (_GOV, _P, False, "Governança aparece em ENP 129, mas de organizações, não de tecnologia."),
        (_TRAIN, _A, False, "Nada de formação no catálogo."),
    ],
    "PPGAdS": [
        (_ORG, _S, False, "Linha 1 Instituições, Organizações e Estratégias; Linha 2 Gestão e Inovação."),
        (_TECH, _A, False, "Programa de administração; nenhuma disciplina técnica de IA."),
        (_DATA, _P, False, "Administração da produção e gestão da qualidade tocam processos."),
        (_GOV, _P, False, "Linha 3 Estado, Burocracia e Gestão de Políticas Públicas."),
        (_TRAIN, _P, False, "Gestão de pessoas por competências toca capacitação."),
    ],
    "MECAI": [
        (_ORG, _P, False, "Aplicação à indústria implica contexto organizacional, sem ser o objeto."),
        (_TECH, _S, False, (
            "Ciência de dados, mineração de dados, inteligência computacional e otimização "
            "são a área de concentração declarada. CAPES 5. Disciplinas não conferidas."
        )),
        (_DATA, _S, False, "Estatística e ciência de dados aplicadas são o núcleo do programa."),
        (_GOV, _U, False, "Não investigado."),
        (_TRAIN, _A, False, "Nada de formação organizacional."),
    ],
    "CCMC": [
        (_ORG, _A, False, "Programa de computação; organizações não são objeto."),
        (_TECH, _S, False, "O programa técnico de referência da região em IA/ML. Grade não conferida."),
        (_DATA, _S, False, "Computação e matemática computacional cobrem dados amplamente."),
        (_GOV, _U, False, "Não investigado."),
        (_TRAIN, _U, False, "Não investigado."),
    ],
    "PIPGEs": [
        (_ORG, _A, True, "Programa de estatística."),
        (_TECH, _S, True, "Linha explícita de Aprendizado de Máquina."),
        (_DATA, _S, True, "Estatística é o núcleo."),
        (_GOV, _A, False, "Nada sobre regulação ou risco."),
        (_TRAIN, _A, False, "Nada de formação."),
    ],
    "PPGEE": [
        (_ORG, _A, True, "Engenharia elétrica."),
        (_TECH, _P, True, "Processamento digital de sinais e smart grids: adjacente, não IA."),
        (_DATA, _P, True, "Sinais e sistemas tocam dados."),
        (_GOV, _A, False, "Nada."),
        (_TRAIN, _A, False, "Nada."),
    ],
}


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

    # ── PPGPEP ──────────────────────────────────────────────────────────────
    dep = await _get_or_create(
        db, Department, {"acronym": "DEP", "website": "https://www.dep.ufscar.br"},
        campus_id=sc.id, name="Departamento de Engenharia de Produção",
    )
    ppgpep = await _get_or_create(
        db, GraduateProgram,
        {
            "department_id": dep.id,
            "name": "Programa de Pós-Graduação Profissional em Engenharia de Produção",
            "website": PPGPEP_URL,
            # "Pós-Graduação Stricto Sensu 100% gratuita" — portfólio oficial.
            "tuition_free": True,
            "notes": "Mestrado profissional. Aulas à NOITE, de segunda a sexta — único "
                     "programa da UFSCar investigado que atende ao requisito de horário. "
                     "Edital 001/2026: não dispõe de bolsas de CAPES/CNPq.",
        },
        acronym="PPGPEP",
    )
    pep_lines: dict[str, ResearchLine] = {}
    for acronym, name, description in PPGPEP_LINES:
        pep_lines[acronym] = await _get_or_create(
            db, ResearchLine, {"name": name, "description": description},
            program_id=ppgpep.id, acronym=acronym,
        )

    pep_cycle = await _get_or_create(
        db, AdmissionCycle,
        {
            "applications_open_on": date(2026, 8, 20),
            "applications_close_on": date(2026, 9, 14),
            "final_result_on": date(2026, 12, 18),
            "site_label": "Processo Seletivo para ingresso em 2027",
            "official_url": f"{PPGPEP_URL}/processo-seletivo",
            "notes": "25 vagas (17 ampla concorrência + 8 de ações afirmativas). "
                     "Edital 3.6: NÃO há distribuição de vagas por linha de pesquisa. "
                     "Exige PROJETO DE PESQUISA — é a Etapa 1.",
        },
        program_id=ppgpep.id, year=2027, semester=1, entry_mode=EntryMode.REGULAR,
    )
    pep_cycle.degree_level = "master"
    for ordinal, name, starts, ends, result in PPGPEP_STAGES:
        await _get_or_create(
            db, AdmissionStage,
            {"name": name, "starts_on": starts, "ends_on": ends, "result_on": result},
            cycle_id=pep_cycle.id, ordinal=ordinal,
        )
    # research_line_id NULO de propósito: o edital diz que as vagas NÃO são
    # distribuídas por linha, ao contrário do PPGCC. O modelo já permitia.
    await _get_or_create(
        db, AdmissionSeat, {"seats": 25}, cycle_id=pep_cycle.id, research_line_id=None
    )
    pep_existing = {d.name for d in (await db.scalars(
        select(RequiredDocument).where(RequiredDocument.cycle_id == pep_cycle.id))).all()}
    for name, mandatory in PPGPEP_DOCS:
        if name not in pep_existing:
            db.add(RequiredDocument(cycle_id=pep_cycle.id, name=name, mandatory=mandatory))
    await _get_or_create(
        db, AdmissionNotice,
        {"title": "Edital PPGPEP/UFSCar n. 001/2026 — ingresso em 2027",
         "url": "https://www.ppgpep.ufscar.br/en/assets/arquivos/edital-ppgpep-2026.pdf"},
        cycle_id=pep_cycle.id, number="001/2026",
    )
    counts["admission_cycles"] = 2
    counts["research_lines"] = len(lines) + len(pep_lines)

    # ── Programas varridos e eliminados, que só existiam nos docs ───────────
    for acronym, dep_name, dep_acr, name, site in MORE_PROGRAMS:
        d = await _get_or_create(
            db, Department, {"acronym": dep_acr}, campus_id=sc.id, name=dep_name
        )
        await _get_or_create(
            db, GraduateProgram,
            {"department_id": d.id, "name": name, "website": site},
            acronym=acronym,
        )

    # ── Programas da varredura de 10/08/2026 ────────────────────────────────
    institutions = {"UFSCar": (ufscar, sc)}
    for acronym, inst_acr, dep_name, dep_acr, name, site in SWEPT_PROGRAMS:
        if inst_acr not in institutions:
            other = await _get_or_create(
                db, Institution,
                {"city": "São Paulo", "state": "SP", "website": "https://www5.usp.br"},
                name="Universidade de São Paulo", acronym="USP",
            )
            institutions[inst_acr] = (
                other,
                await _get_or_create(db, Campus, {}, institution_id=other.id, name="São Carlos"),
            )
        _, campus = institutions[inst_acr]
        d = await _get_or_create(
            db, Department, {"acronym": dep_acr}, campus_id=campus.id, name=dep_name
        )
        await _get_or_create(
            db, GraduateProgram,
            {"department_id": d.id, "name": name, "website": site},
            acronym=acronym,
        )

    # ── Os quatro requisitos, com a evidência de cada um ────────────────────
    all_programs = {
        p.acronym: p for p in (await db.scalars(select(GraduateProgram))).all()
    }
    for acronym, rows in REQUIREMENTS.items():
        program = all_programs.get(acronym)
        if program is None:
            continue
        for requirement, status, evidence in rows:
            await _get_or_create(
                db, ProgramRequirement,
                {"status": status, "evidence": evidence, "verified_on": date(2026, 8, 8)},
                program_id=program.id, requirement=requirement,
            )
    counts["program_requirements"] = sum(len(r) for r in REQUIREMENTS.values())

    for acronym, rows in ADHERENCE.items():
        program = all_programs.get(acronym)
        if program is None:
            continue
        for signal, level, verified, evidence in rows:
            await _get_or_create(
                db, ProgramAdherence,
                {
                    "level": level,
                    "evidence": evidence,
                    "verified": verified,
                    "verified_on": date(2026, 8, 10),
                },
                program_id=program.id, signal=signal,
            )
    counts["program_adherence"] = sum(len(r) for r in ADHERENCE.values())

    for url, kind, title, redirect in SOURCES + PPGPEP_SOURCES + MECAI_SOURCES + INDEX_SOURCES:
        await _get_or_create(
            db, Source,
            {"source_type": kind, "title": title, "institution_id": ufscar.id,
             "redirects_to": redirect, "last_checked_at": datetime(2026, 8, 8, tzinfo=UTC)},
            url=url,
        )
    counts["sources"] = (
        len(SOURCES) + len(PPGPEP_SOURCES) + len(MECAI_SOURCES) + len(INDEX_SOURCES)
    )

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
