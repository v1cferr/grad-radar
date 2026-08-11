"""Ler uma grade horária e decidir o requisito de horário — sem modelo.

Este módulo existe para tirar uma pessoa do circuito. Baixar o PDF do PPGCTS é
trivial e o coletor já faz; concluir que `8h às 12h` e `14h às 17h` significa
"sem oferta noturna" foi o que consumiu atenção, e foi feito à mão seis vezes.

**Por que regex e não LLM.** Os seis documentos reais lidos na varredura de
10/08/2026 usam cinco formatos numéricos e um em prosa. Nenhum precisa de
compreensão de texto — precisa de um padrão e de uma regra. Regex é
determinística, testável contra as seis fixtures em tests/fixtures/schedules/, e
**não inventa**. Um modelo que alucina "há disciplina às 19h" produz exatamente a
falha que este projeto existe para evitar, com aparência de resposta. Ver
docs/AUTOMACAO.md.

**A decisão mais importante aqui é quando NÃO responder.** Prosa que apenas
PERMITE aula à noite — "poderão ser oferecidas no período noturno" — não é oferta,
e devolver MET nesses casos seria transformar uma permissão em fato. Foi essa
distinção que separou o veredito correto do errado no MECAI, e ela está codificada
em `_HEDGES`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import time

from app.models import RequirementStatus

# Fração de faixas noturnas a partir da qual a grade conta como noturna. Abaixo
# disso o veredito é "não sabemos", não "atende": uma ou duas disciplinas à noite
# numa grade diurna não permitem cursar o programa trabalhando 08–18. Descoberto
# lendo a grade da Eng. de Produção da EESC/USP, que tem 3 faixas noturnas em 18 —
# uma disciplina recorrente, e remota.
EVENING_MAJORITY = 0.5

# Formatos vistos nos documentos reais, em ordem de aparição:
#   8h às 12h · 14h às 17h        (PPGCTS, PPGEP)
#   08h - 12h · 14h - 18h         (PPGCC)
#   8:00 -- 10:00                 (PPGEE, hífen DUPLO)
#   08:00 - 09:40                 (PIPGEs)
# O separador é obrigatório: sem ele, "8:56 24/07/2026" viraria uma faixa.
_BAND = re.compile(
    r"(?<!\d)(\d{1,2})\s*[:h]\s*(\d{2})?\s*(?:às|as|--|—|–|-|a)\s*(\d{1,2})\s*[:h]\s*(\d{2})?",
    re.IGNORECASE,
)

# Grades em prosa. Faixas convencionais, usadas SÓ para decidir se há noturno —
# nunca para afirmar horário exato de uma disciplina.
_PERIOD_WORDS = {
    "manhã": False,
    "manha": False,
    "tarde": False,
    "noite": True,
    "noturno": True,
    "noturna": True,
}

# Verbos e adverbios que transformam oferta em POSSIBILIDADE. Quando aparecem
# perto de uma menção a noturno, a resposta correta é "não sabemos", não "atende".
_HEDGES = re.compile(
    r"\b(?:poder[ãa]o?|podendo|preferencialmente|eventualmente|quando houver|"
    r"caso haja|poder[áa])\b",
    re.IGNORECASE,
)

# Páginas de erro servidas com HTTP 200. O ICMC faz isso, e o efeito no monitor é
# grave: a fonte reportaria "mudou" uma vez e "igual" para sempre, nunca
# "falhou". Ver docs/AUTOMACAO.md.
_ERROR_PAGE = re.compile(
    r"\b(?:erro\s*40[34]|error\s*40[34]|página\s+não\s+encontrada|"
    r"page\s+not\s+found|not\s+found)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TimeBand:
    starts_at: time
    ends_at: time
    raw: str

    def __str__(self) -> str:
        return f"{self.starts_at:%H:%M}–{self.ends_at:%H:%M}"


@dataclass(frozen=True)
class EveningOffer:
    """O veredito do requisito 1 mais a frase que o sustenta.

    A evidência não é decoração: é o que vai para `ProgramRequirement.evidence` e
    aparece no hover da tabela. Um veredito sem o porquê obriga a refazer a
    pesquisa toda vez que alguém duvidar.
    """

    status: RequirementStatus
    evidence: str
    bands: tuple[TimeBand, ...] = ()


def time_bands(text: str) -> list[TimeBand]:
    """Toda faixa horária plausível do documento, deduplicada e ordenada."""
    found: dict[tuple[time, time], TimeBand] = {}
    for m in _BAND.finditer(text):
        h1, m1, h2, m2 = m.groups()
        try:
            start = time(int(h1), int(m1 or 0))
            end = time(int(h2), int(m2 or 0))
        except ValueError:  # 25h, 61min — não é horário
            continue
        # Faixa tem de avançar no tempo. Descarta "12h a 8h" e casamentos
        # acidentais em números soltos.
        if end <= start:
            continue
        found.setdefault((start, end), TimeBand(start, end, " ".join(m.group(0).split())))
    return sorted(found.values(), key=lambda b: (b.starts_at, b.ends_at))


def period_words(text: str) -> set[str]:
    """Menções a manhã/tarde/noite, normalizadas."""
    return {
        w.lower()
        for w in re.findall(r"\b(?:manh[ãa]|tarde|noite|noturn[oa])\b", text, re.IGNORECASE)
    }


def is_error_page(text: str) -> bool:
    """Detecta página de erro servida com HTTP 200.

    Conservador de propósito: casa apenas marcadores explícitos, e só perto do
    começo do documento. Um edital que MENCIONA "não encontrado" no meio de 30 mil
    caracteres não é uma página de erro, e marcar como tal esconderia o edital.
    """
    return bool(_ERROR_PAGE.search(text[:400]))


def evening_offer(text: str, work_ends_at: time = time(18, 0)) -> EveningOffer:
    """Decide o requisito 1: existe aula que comece depois da jornada?

    A regra é sobre o INÍCIO, não o fim. Uma disciplina de 14h às 18h conflita
    integralmente com quem trabalha até as 18h, e foi assim que o PPGEP e o PPGEE
    caíram — a última faixa deles TERMINA quando a jornada termina.
    """
    if is_error_page(text):
        return EveningOffer(
            RequirementStatus.UNKNOWN,
            "O documento é uma página de erro servida com HTTP 200 — não há grade para ler.",
        )

    bands = tuple(time_bands(text))
    if bands:
        evening = [b for b in bands if b.starts_at >= work_ends_at]
        listed = ", ".join(str(b) for b in bands[:8]) + ("…" if len(bands) > 8 else "")
        if evening and len(evening) / len(bands) >= EVENING_MAJORITY:
            return EveningOffer(
                RequirementStatus.MET,
                f"{len(evening)} de {len(bands)} faixas começam {work_ends_at:%H:%M} ou "
                f"depois: {', '.join(str(b) for b in evening[:4])}. Faixas no documento: {listed}.",
                bands,
            )
        if evening:
            # EXISTIR NÃO É INTEGRALIZAR. A grade da Eng. de Produção da EESC/USP
            # tem 3 faixas noturnas em 18 — uma disciplina recorrente, e remota. Um
            # slot noturno isolado não permite cursar o programa trabalhando 08–18,
            # e chamar isso de "atende" faria o sistema recomendar o impossível.
            # É a mesma distinção que separou o veredito certo do errado no MECAI.
            return EveningOffer(
                RequirementStatus.UNKNOWN,
                f"Só {len(evening)} de {len(bands)} faixas começam {work_ends_at:%H:%M} ou "
                f"depois ({', '.join(str(b) for b in evening[:4])}) — existir não é "
                f"integralizar. Falta saber se as obrigatórias cabem no noturno. "
                f"Faixas no documento: {listed}.",
                bands,
            )
        latest = max(bands, key=lambda b: b.starts_at)
        return EveningOffer(
            RequirementStatus.NOT_MET,
            f"Nenhuma das {len(bands)} faixas começa {work_ends_at:%H:%M} ou depois — a mais "
            f"tarde começa {latest.starts_at:%H:%M}. Faixas no documento: {listed}.",
            bands,
        )

    words = period_words(text)
    if words:
        has_evening = any(_PERIOD_WORDS.get(w, False) for w in words)
        hedged = bool(_HEDGES.search(text))
        if has_evening and hedged:
            # O caso MECAI: o edital PERMITE noturno sem se comprometer com a
            # oferta. Permissão não é fato, e chamar de MET seria inventar.
            return EveningOffer(
                RequirementStatus.UNKNOWN,
                "O documento menciona período noturno, mas em linguagem de POSSIBILIDADE "
                "(\"poderão\", \"preferencialmente\"). Permissão não é oferta — falta a "
                f"grade real. Períodos citados: {', '.join(sorted(words))}.",
            )
        if has_evening:
            return EveningOffer(
                RequirementStatus.MET,
                f"O documento afirma oferta em período noturno. Períodos citados: "
                f"{', '.join(sorted(words))}.",
            )
        return EveningOffer(
            RequirementStatus.NOT_MET,
            f"O documento indica os períodos {', '.join(sorted(words))} e nenhuma menção a "
            "noite, sem faixas numéricas.",
        )

    return EveningOffer(
        RequirementStatus.UNKNOWN,
        "Nenhuma faixa horária nem menção a período no documento — não há o que decidir.",
    )
