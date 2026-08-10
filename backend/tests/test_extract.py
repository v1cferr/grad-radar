"""O extrator, contra os documentos reais que foram lidos à mão.

Cada fixture em `fixtures/schedules/` é o texto que o coletor extraiu de um
documento oficial de verdade, e a resposta esperada é a que uma pessoa produziu
lendo o mesmo texto. É o que dá para dizer que o extrator substitui a leitura
manual em vez de apenas parecer que substitui.

O `ppgcc-2026-2.txt` veio do arquivo do próprio monitor — a URL original passou a
devolver 404, o que é uma demonstração incidental de por que os snapshots são
guardados.
"""

from __future__ import annotations

import pathlib
from datetime import time

import pytest

from app.extract import evening_offer, is_error_page, period_words, time_bands
from app.models import RequirementStatus

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "schedules"

MET = RequirementStatus.MET
NOT_MET = RequirementStatus.NOT_MET
UNKNOWN = RequirementStatus.UNKNOWN


def load(name: str) -> str:
    return (FIXTURES / f"{name}.txt").read_text()


# (fixture, veredito esperado, motivo — o que uma pessoa concluiu lendo)
CASES = [
    ("ppgcc-2026-2", NOT_MET, "08h–12h e 14h–18h; 13 disciplinas, nenhuma após 18h"),
    ("ppgee-2026-2", NOT_MET, "8:00--10:00 até 16:00--18:00, com hífen duplo"),
    ("pipges-2026-2", NOT_MET, "08:00–09:40 até 16:00–17:40"),
    ("ppgcts-2026-2", NOT_MET, "8h às 12h e 14h às 17h, 11 disciplinas"),
    ("ppgep-2026-2", NOT_MET, "08h–12h, 10h–12h, 14h–18h — a última TERMINA às 18h"),
    ("ppgci-2026-1", NOT_MET, "prosa: 'Horário de oferta: Manhã e Tarde', sem faixas"),
    ("mecai-edital-002-2026", UNKNOWN, "diz noturno, mas com 'poderão' — permissão, não oferta"),
    ("icmc-soft-404", UNKNOWN, "página de erro servida com HTTP 200"),
]


@pytest.mark.parametrize(("name", "expected", "why"), CASES)
def test_verdict_matches_the_human_reading(name: str, expected: RequirementStatus, why: str):
    result = evening_offer(load(name))
    assert result.status is expected, f"{name} ({why}) → {result.status}: {result.evidence}"
    assert result.evidence, "todo veredito carrega a frase que o sustenta"


def test_every_fixture_is_covered():
    """Fixture nova sem caso esperado é fixture que ninguém checou."""
    on_disk = {p.stem for p in FIXTURES.glob("*.txt")}
    assert on_disk == {name for name, _, _ in CASES}


class TestTimeBands:
    def test_it_reads_the_five_real_formats(self):
        assert [str(b) for b in time_bands("8h às 12h")] == ["08:00–12:00"]
        assert [str(b) for b in time_bands("14h - 18h")] == ["14:00–18:00"]
        assert [str(b) for b in time_bands("8:00 -- 10:00")] == ["08:00–10:00"]
        assert [str(b) for b in time_bands("08:00 - 09:40")] == ["08:00–09:40"]
        assert [str(b) for b in time_bands("19h às 22h30")] == ["19:00–22:30"]

    def test_a_date_is_not_a_time_band(self):
        """O cabeçalho do PPGEE traz '24/07/2026 08:56' — casar isso inventaria
        uma faixa, e uma faixa inventada muda um veredito."""
        assert time_bands("Última atualização 24/7/26 8:56 24/07/2026 08:56") == []
        assert time_bands("inscrições de 05/08/2026 a 14/09/2026") == []

    def test_impossible_and_backwards_bands_are_dropped(self):
        assert time_bands("25h às 30h") == []
        assert time_bands("12h às 8h") == []

    def test_bands_are_deduplicated_and_ordered(self):
        bands = time_bands("14h às 18h; 8h às 12h; 14h às 18h")
        assert [str(b) for b in bands] == ["08:00–12:00", "14:00–18:00"]


class TestTheRuleIsAboutTheStart:
    def test_a_class_ending_at_eighteen_still_conflicts(self):
        """Foi assim que o PPGEP e o PPGEE caíram: a última faixa TERMINA às 18h.
        Olhar o fim em vez do início os teria aprovado por engano."""
        assert evening_offer("14h às 18h").status is NOT_MET

    def test_a_class_starting_at_eighteen_is_accepted(self):
        assert evening_offer("18h às 22h").status is MET

    def test_the_working_day_is_a_parameter(self):
        """Se alguém trabalhar até as 17h, 17h–19h passa a servir."""
        assert evening_offer("17h às 19h").status is NOT_MET
        assert evening_offer("17h às 19h", work_ends_at=time(17, 0)).status is MET


class TestPermissionIsNotOffer:
    """A distinção que separou o veredito certo do errado no MECAI."""

    def test_hedged_evening_is_unknown(self):
        for hedge in [
            "as aulas poderão ser oferecidas no período noturno",
            "aulas preferencialmente às sextas, períodos da manhã, tarde e noite",
            "podendo ser oferecidas de segunda a sexta (manhã, tarde ou noite)",
        ]:
            assert evening_offer(hedge).status is UNKNOWN, hedge

    def test_an_assertion_about_evening_is_met(self):
        assert evening_offer("As aulas ocorrem à noite, de segunda a sexta.").status is MET

    def test_morning_and_afternoon_only_is_not_met(self):
        assert evening_offer("Horário de oferta: Manhã e Tarde").status is NOT_MET

    def test_numeric_bands_win_over_prose(self):
        """Uma grade com faixas decide; a palavra 'noturno' num rodapé não."""
        r = evening_offer("Programa noturno.\nSegunda 8h às 12h\nTerça 14h às 17h")
        assert r.status is NOT_MET
        assert len(r.bands) == 2


class TestErrorPageDetection:
    """Fecha a armadilha do soft 404 — ver docs/AUTOMACAO.md."""

    def test_it_catches_the_icmc_page(self):
        assert is_error_page(load("icmc-soft-404"))

    def test_a_real_document_is_not_an_error_page(self):
        for name, _, _ in CASES:
            if name != "icmc-soft-404":
                assert not is_error_page(load(name)), name

    def test_a_mention_deep_in_a_long_document_does_not_count(self):
        """Um edital que diz 'não encontrado' na página 12 não é página de erro.
        Marcar como tal esconderia o edital, que é pior que não marcar."""
        assert not is_error_page("A" * 500 + " página não encontrada")


class TestPeriodWords:
    def test_it_normalises_accents_and_case(self):
        assert period_words("Manhã, TARDE e Noite") == {"manhã", "tarde", "noite"}
        assert period_words("período noturno") == {"noturno"}
