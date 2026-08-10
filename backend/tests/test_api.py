"""Integration tests — the real app, the real database, no server.

These assert against the **verified PPGCC data**, so they double as a regression
guard on the seed: if someone edits a figure the sources do not support, a test
here fails and points at the research note.
"""

from __future__ import annotations

from httpx import AsyncClient


class TestPrograms:
    async def test_ppgcc_is_seeded_with_its_seven_lines(self, client: AsyncClient):
        r = await client.get("/api/programs")
        assert r.status_code == 200
        program = next(p for p in r.json() if p["acronym"] == "PPGCC")
        assert program["institution"] == "UFSCar"
        assert program["capes_rating"] == 5
        assert len(program["research_lines"]) == 7

    async def test_tuition_is_unknown_not_false(self, client: AsyncClient):
        """No consulted source states it, so the API must say `null`.

        Reporting `false` would be a lie; reporting `true` would be an inference
        presented as a fact. Both are worse than admitting the gap.
        """
        r = await client.get("/api/programs")
        ppgcc = next(p for p in r.json() if p["acronym"] == "PPGCC")
        assert ppgcc["tuition_free"] is None

    async def test_unknown_program_is_404(self, client: AsyncClient):
        assert (await client.get("/api/programs/999999")).status_code == 404


async def _cycle(client: AsyncClient, program: str, year: int, semester: int) -> dict:
    """Look a cycle up by programme AND term, never by position.

    Indexing [0] broke when a second programme was seeded. Filtering by programme
    alone broke again when the PPGCC got a second cycle — the 2027/1 `expected`
    one, which has no dates. Um programa tem vários ciclos por definição; só o
    termo identifica um.
    """
    cycles = (await client.get("/api/admission-cycles")).json()
    return next(
        c
        for c in cycles
        if c["program"] == program and c["year"] == year and c["semester"] == semester
    )


class TestAdmissionCycles:
    async def test_status_contradicts_the_site_label(self, client: AsyncClient):
        """The headline behaviour of the whole system, end to end.

        The PPGCC site labels this cycle "Processo vigente" while its window
        closed on 26/04/2026. The API must report it closed anyway.
        """
        cycle = await _cycle(client, "PPGCC", 2026, 2)
        assert cycle["site_label"] == "Processo vigente"
        assert cycle["status"] == "concluded"

    async def test_seats_are_per_research_line(self, client: AsyncClient):
        cycle = await _cycle(client, "PPGCC", 2026, 2)
        seats = {s["research_line"]: s["seats"] for s in cycle["seats"]}
        assert seats == {"AMPLN": 4, "VC": 7, "SDARC": 7, "SAR": 2, "BD": 1, "ES": 1, "CCH": 1}
        # The edital says "23 (vinte e três)". A first reading of the PDF said 21;
        # the per-line breakdown is what caught it.
        assert cycle["total_seats"] == 23

    async def test_stages_are_ordered_and_dated(self, client: AsyncClient):
        cycle = await _cycle(client, "PPGCC", 2026, 2)
        assert [s["ordinal"] for s in cycle["stages"]] == [1, 2]
        assert cycle["stages"][0]["starts_on"] == "2026-05-13"


class TestPpgpep:
    """The only programme that survives all four eliminatory requirements.

    Evening classes, in person in São Carlos, free, public. Everything else the
    project looked at fails on the first one — see docs/research/.
    """

    async def test_it_is_free_and_that_is_verified_not_assumed(self, client: AsyncClient):
        program = next(
            p for p in (await client.get("/api/programs")).json() if p["acronym"] == "PPGPEP"
        )
        assert program["tuition_free"] is True

    async def test_the_2027_call_is_open_for_applications(self, client: AsyncClient):
        """The reason the monitor exists. If this ever regresses, nobody applies."""
        cycle = await _cycle(client, "PPGPEP", 2027, 1)
        assert cycle["applications_open_on"] == "2026-08-20"
        assert cycle["applications_close_on"] == "2026-09-14"
        assert cycle["status"] in {"announced", "open"}

    async def test_it_says_when_we_will_actually_know(self, client: AsyncClient):
        """Não derivável das etapas: a última publica SUAS notas em 04/12 e o
        resultado definitivo sai em 18/12, depois do prazo de recurso."""
        cycle = await _cycle(client, "PPGPEP", 2027, 1)
        assert cycle["final_result_on"] == "2026-12-18"
        assert cycle["stages"][-1]["result_on"] == "2026-12-04"

    async def test_seats_are_not_split_by_research_line(self, client: AsyncClient):
        """Edital 3.6, and the opposite of PPGCC — the model had to allow both."""
        cycle = await _cycle(client, "PPGPEP", 2027, 1)
        assert cycle["total_seats"] == 25
        assert [s["research_line"] for s in cycle["seats"]] == [None]


class TestOfferings:
    async def test_every_offering_collides_with_a_commercial_day(self, client: AsyncClient):
        """The finding that motivated the project, computed rather than asserted."""
        offerings = (await client.get("/api/offerings?candidate=Victor")).json()
        assert len(offerings) == 13
        assert all(o["conflicts_with_work"] is True for o in offerings)

    async def test_only_two_time_bands_exist_and_neither_is_evening(self, client: AsyncClient):
        offerings = (await client.get("/api/offerings")).json()
        bands = {(o["starts_at"], o["ends_at"]) for o in offerings}
        assert bands == {("08:00:00", "12:00:00"), ("14:00:00", "18:00:00")}

    async def test_conflict_is_null_without_a_candidate(self, client: AsyncClient):
        """No candidate means no working day to compare against — not "no conflict"."""
        offerings = (await client.get("/api/offerings")).json()
        assert all(o["conflicts_with_work"] is None for o in offerings)

    async def test_machine_learning_offering_carries_its_real_attribution(
        self, client: AsyncClient
    ):
        offerings = (await client.get("/api/offerings")).json()
        ml = next(o for o in offerings if o["code"] == "CCO-724")
        assert ml["research_line"] == "AMPLN"
        assert ml["professor"] == "Tiago Agostinho de Almeida"
        # Two rooms, because the same class runs at both campuses — and this one
        # ORIGINATES in Sorocaba, with São Carlos as the remote end.
        assert len(ml["locations"]) == 2


class TestFaculty:
    async def test_ampln_has_nine_members(self, client: AsyncClient):
        assert len((await client.get("/api/faculty?line=AMPLN")).json()) == 9

    async def test_a_member_can_belong_to_two_lines(self, client: AsyncClient):
        """Auri Vincenzi — the case a single foreign key would have destroyed."""
        people = (await client.get("/api/faculty")).json()
        auri = next(p for p in people if p["name"].startswith("Auri"))
        assert sorted(auri["research_lines"]) == ["BD", "ES"]

    async def test_a_member_can_belong_to_none(self, client: AsyncClient):
        people = (await client.get("/api/faculty")).json()
        cruvinel = next(p for p in people if p["name"].startswith("Paulo Estevão"))
        assert cruvinel["research_lines"] == []

    async def test_external_affiliation_is_recorded(self, client: AsyncClient):
        """"Faculty of PPGCC" is not "employed by UFSCar"."""
        people = (await client.get("/api/faculty")).json()
        diego = next(p for p in people if p["name"].startswith("Diego"))
        assert diego["external_affiliation"] == "icmc.usp.br"


class TestOptions:
    """A tabela de opções — a pergunta "já olhamos esse?"."""

    async def test_eliminated_programmes_stay_in_the_list(self, client: AsyncClient):
        """Removê-los faria a mesma varredura ser refeita todo mês."""
        options = (await client.get("/api/options")).json()
        assert {o["acronym"] for o in options} >= {"PPGPEP", "PPGCC", "PPGEE", "PIPGEs"}

    async def test_approved_comes_first(self, client: AsyncClient):
        """A ordem da tabela é a ordem em que gastar atenção."""
        options = (await client.get("/api/options")).json()
        assert options[0]["acronym"] == "PPGPEP"
        assert options[0]["verdict"] == "approved"
        # Sem contagem literal: a varredura cresce, e um número fixo aqui falharia
        # por sucesso da pesquisa. O que importa é a ORDEM.
        rank = {"approved": 0, "pending": 1, "eliminated": 2}
        ranks = [rank[o["verdict"]] for o in options]
        assert ranks == sorted(ranks)
        assert options[-1]["verdict"] == "eliminated"

    async def test_one_proven_failure_eliminates(self, client: AsyncClient):
        """Assimetria deliberada: para descartar basta uma falha comprovada."""
        options = {o["acronym"]: o for o in (await client.get("/api/options")).json()}
        ppgcc = options["PPGCC"]
        assert ppgcc["verdict"] == "eliminated"
        status = {r["requirement"]: r["status"] for r in ppgcc["requirements"]}
        assert status["evening_classes"] == "not_met"
        # ...mesmo com um requisito ainda desconhecido: a falha já basta.
        assert status["tuition_free"] == "unknown"

    async def test_absence_of_failures_is_not_approval(self, client: AsyncClient):
        """E a recíproca: sem os quatro verificados, o veredito é 'pending'."""
        from app.models import Requirement, RequirementStatus, verdict_for

        class _R:
            def __init__(self, requirement, status):
                self.requirement, self.status = requirement, status

        partial = [_R(Requirement.EVENING_CLASSES, RequirementStatus.MET)]
        assert verdict_for(partial).value == "pending"

    async def test_every_verdict_carries_its_evidence(self, client: AsyncClient):
        """Um veredito sem o porquê obriga a refazer a pesquisa a cada dúvida."""
        for o in (await client.get("/api/options")).json():
            for r in o["requirements"]:
                if r["status"] != "unknown":
                    assert r["evidence"], f"{o['acronym']}/{r['requirement']} sem evidência"

    async def test_a_closed_cycle_is_not_a_deadline(self, client: AsyncClient):
        options = {o["acronym"]: o for o in (await client.get("/api/options")).json()}
        assert options["PPGPEP"]["days_left"] is not None
        # O PPGCC tem ciclo, mas encerrado — não pode aparecer como prazo.
        assert options["PPGCC"]["days_left"] is None


class TestAdherence:
    """O índice de aderência ao trabalho na FAI — docs/ADERENCIA.md."""

    async def test_the_index_never_normalises_away_what_we_do_not_know(self, client: AsyncClient):
        """O denominador é fixo em cinco sinais.

        Normalizar pelo que já se sabe daria 100% a um programa com um único sinal
        forte, e um número desses convida a decisão errada.
        """
        from app.models import AdherenceLevel, AdherenceSignal, adherence_index

        class _A:
            def __init__(self, level):
                self.level = level

        one_strong = [_A(AdherenceLevel.STRONG)]
        assert adherence_index(one_strong) == 20  # 2 de 10 pontos, não 100%

        todos = [_A(AdherenceLevel.STRONG) for _ in AdherenceSignal]
        assert adherence_index(todos) == 100

    async def test_coverage_travels_with_the_number(self, client: AsyncClient):
        """Um índice sobre dois sinais não é comparável a um sobre cinco."""
        for o in (await client.get("/api/options")).json():
            assert o["adherence"] is not None
            assert 0 <= o["signals_assessed"] <= 5
            assert len(o["adherence_signals"]) == 5

    async def test_the_most_adherent_programme_is_eliminated(self, client: AsyncClient):
        """A tensão central do projeto, agora computada em vez de afirmada.

        O PPGCTS tem a maior aderência de todos e não tem aula à noite. Se este
        teste passar a falhar, alguma coisa boa aconteceu — ou o horário mudou, ou
        apareceu programa melhor.
        """
        options = {o["acronym"]: o for o in (await client.get("/api/options")).json()}
        top = max(options.values(), key=lambda o: o["adherence"])
        assert top["acronym"] == "PPGCTS"
        assert top["verdict"] == "eliminated"
        assert options["PPGPEP"]["adherence"] < top["adherence"]

    async def test_declared_scope_is_never_marked_verified(self, client: AsyncClient):
        """Nome de linha de pesquisa não é evidência. Foi assim que a AMPLN
        pareceu perfeita e a grade horária derrubou tudo."""
        options = {o["acronym"]: o for o in (await client.get("/api/options")).json()}
        toti = next(
            s for s in options["PPGPEP"]["adherence_signals"]
            if s["signal"] == "organizational_adoption"
        )
        assert toti["level"] == "strong"
        assert toti["verified"] is False


class TestNoticePdf:
    """A rota que serve o edital pela nossa origem."""

    async def test_it_refuses_a_notice_without_a_document(self, client: AsyncClient):
        assert (await client.get("/api/notices/999999/pdf")).status_code == 404

    async def test_the_option_points_at_our_route_not_the_original(self, client: AsyncClient):
        """Os PDFs da UFSCar respondem X-Frame-Options: SAMEORIGIN — um iframe
        para a URL original abre em branco, sem erro visível."""
        options = {o["acronym"]: o for o in (await client.get("/api/options")).json()}
        notice = options["PPGPEP"]["notices"][0]
        assert notice["url"].startswith("https://www.ppgpep.ufscar.br")
        assert notice["pdf_url"] == f"/api/notices/{notice['id']}/pdf"


class TestHealth:
    async def test_health_reports_the_database(self, client: AsyncClient):
        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"ok": True, "db": "ok"}
