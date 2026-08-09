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
