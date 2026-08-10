"""Por que um programa entra ou sai da lista.

O GOAL.md define quatro requisitos ELIMINATÓRIOS: aula à noite, presencial em
São Carlos, gratuito e público. Um programa que falha em qualquer um não é uma
opção pior — é uma opção falsa.

Quatro colunas booleanas em ``GraduateProgram`` resolveriam o armazenamento e
perderiam o que importa. Três coisas forçaram uma tabela:

**"Desconhecido" não é "não".** O PPGCC foi eliminado por evidência: a grade de
2026/2 publica só 08–12 e 14–18. O PPGCI ainda não foi olhado. Tratar os dois
como "não atende" apagaria a diferença entre um fato e uma lacuna — e é a lacuna
que vira trabalho.

**A evidência é a informação.** Saber que um programa foi eliminado sem saber
por quê obriga a refazer a pesquisa inteira a cada dúvida. Cada veredito carrega
o texto que o sustenta e, quando existe, a fonte monitorada de onde veio.

**Requisitos mudam.** Se amanhã entrar "aceita orientação em IA aplicada", uma
linha nova na enum resolve; quatro migrações de coluna, não.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, pg_enum
from app.models.academic import GraduateProgram
from app.models.provenance import Source


class Requirement(enum.StrEnum):
    """Os quatro do GOAL.md, na ordem em que eliminam."""

    EVENING_CLASSES = "evening_classes"
    IN_PERSON_SAO_CARLOS = "in_person_sao_carlos"
    TUITION_FREE = "tuition_free"
    PUBLIC_INSTITUTION = "public_institution"


class RequirementStatus(enum.StrEnum):
    MET = "met"
    NOT_MET = "not_met"
    UNKNOWN = "unknown"  # ainda não verificado — vira tarefa, não veredito


class ProgramVerdict(enum.StrEnum):
    APPROVED = "approved"  # os quatro verificados e atendidos
    ELIMINATED = "eliminated"  # ao menos um verificado e não atendido
    PENDING = "pending"  # nenhum falhou, mas falta verificar


class ProgramRequirement(Base):
    __tablename__ = "program_requirement"
    __table_args__ = (UniqueConstraint("program_id", "requirement"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("graduate_program.id"))
    requirement: Mapped[Requirement] = mapped_column(pg_enum(Requirement, "requirement"))
    status: Mapped[RequirementStatus] = mapped_column(
        pg_enum(RequirementStatus, "requirement_status")
    )

    # O que sustenta o veredito, em uma frase legível. Sem isso, "eliminado"
    # obriga a refazer a pesquisa toda vez que alguém duvidar.
    evidence: Mapped[str | None] = mapped_column(Text)

    # De onde veio, quando veio de uma fonte vigiada. Nulo quando o fato foi
    # apurado fora do coletor — o que é comum e não deve ser escondido.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("source.id"))
    verified_on: Mapped[date | None] = mapped_column()

    program: Mapped[GraduateProgram] = relationship()
    source: Mapped[Source | None] = relationship()


def verdict_for(requirements: list[ProgramRequirement]) -> ProgramVerdict:
    """Um único NOT_MET elimina. Só APPROVED com os quatro verificados.

    A assimetria é deliberada e é a regra central do projeto: para descartar
    basta uma falha comprovada; para aprovar não basta a ausência de falhas.
    """
    seen = {r.requirement: r.status for r in requirements}
    if any(s is RequirementStatus.NOT_MET for s in seen.values()):
        return ProgramVerdict.ELIMINATED
    if all(seen.get(r) is RequirementStatus.MET for r in Requirement):
        return ProgramVerdict.APPROVED
    return ProgramVerdict.PENDING


# ─────────────────────────────────────────────────────────────────────────────
# Aderência ao trabalho na FAI
# ─────────────────────────────────────────────────────────────────────────────
# Os cinco sinais de docs/ADERENCIA.md, derivados do item 4.1 do Edital FAI
# 001/2026. Separados dos requisitos porque respondem a perguntas diferentes:
# requisito decide SE dá para cursar, aderência decide se VALE A PENA. Misturar
# os dois foi o que fez o PPGCC ser investigado a fundo estando eliminado.


class AdherenceSignal(enum.StrEnum):
    ORGANIZATIONAL_ADOPTION = "organizational_adoption"  # 4.1b, 4.1f
    TECHNICAL_AI = "technical_ai"  # 4.1a
    DATA_AND_PROCESS = "data_and_process"  # 2.2, 4.1c
    GOVERNANCE = "governance"  # 4.1d
    TRAINING = "training"  # 4.1e


class AdherenceLevel(enum.StrEnum):
    STRONG = "strong"
    PARTIAL = "partial"
    ABSENT = "absent"
    UNKNOWN = "unknown"


_POINTS = {
    AdherenceLevel.STRONG: 2,
    AdherenceLevel.PARTIAL: 1,
    AdherenceLevel.ABSENT: 0,
    AdherenceLevel.UNKNOWN: 0,
}


class ProgramAdherence(Base):
    __tablename__ = "program_adherence"
    __table_args__ = (UniqueConstraint("program_id", "signal"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("graduate_program.id"))
    signal: Mapped[AdherenceSignal] = mapped_column(pg_enum(AdherenceSignal, "adherence_signal"))
    level: Mapped[AdherenceLevel] = mapped_column(pg_enum(AdherenceLevel, "adherence_level"))

    evidence: Mapped[str | None] = mapped_column(Text)

    # False quando o nível vem do ESCOPO DECLARADO do programa e não de algo
    # lido — docente, disciplina ofertada, projeto. A régua em ADERENCIA.md diz
    # que nome de linha de pesquisa nunca conta como verificado, e foi assim que
    # a AMPLN do PPGCC pareceu perfeita.
    verified: Mapped[bool] = mapped_column(default=False)

    source_id: Mapped[int | None] = mapped_column(ForeignKey("source.id"))
    verified_on: Mapped[date | None] = mapped_column()

    program: Mapped[GraduateProgram] = relationship()
    source: Mapped[Source | None] = relationship()


def adherence_index(rows: list[ProgramAdherence]) -> int | None:
    """0–100 sobre os CINCO sinais, sempre.

    O denominador é fixo (5 sinais x 2 pontos) e `unknown` vale zero. Isso faz um
    programa pouco investigado pontuar baixo, o que é o comportamento correto:
    "não sabemos" não é elogio. Quem quiser saber se o índice é confiável olha
    quantos sinais foram avaliados — daí `signals_assessed` andar sempre junto.

    Normalizar pelo que já se sabe daria 100 a um programa com um único sinal
    forte, e um número desses convida a decisão errada.
    """
    if not rows:
        return None
    return round(100 * sum(_POINTS[r.level] for r in rows) / (2 * len(AdherenceSignal)))
