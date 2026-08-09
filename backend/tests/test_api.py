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
        assert r.json()[0]["tuition_free"] is None

    async def test_unknown_program_is_404(self, client: AsyncClient):
        assert (await client.get("/api/programs/999999")).status_code == 404


class TestAdmissionCycles:
    async def test_status_contradicts_the_site_label(self, client: AsyncClient):
        """The headline behaviour of the whole system, end to end.

        The PPGCC site labels this cycle "Processo vigente" while its window
        closed on 26/04/2026. The API must report it closed anyway.
        """
        cycle = (await client.get("/api/admission-cycles")).json()[0]
        assert cycle["site_label"] == "Processo vigente"
        assert cycle["status"] == "concluded"

    async def test_seats_are_per_research_line(self, client: AsyncClient):
        cycle = (await client.get("/api/admission-cycles")).json()[0]
        seats = {s["research_line"]: s["seats"] for s in cycle["seats"]}
        assert seats == {"AMPLN": 4, "VC": 7, "SDARC": 7, "SAR": 2, "BD": 1, "ES": 1, "CCH": 1}
        # The edital says "23 (vinte e três)". A first reading of the PDF said 21;
        # the per-line breakdown is what caught it.
        assert cycle["total_seats"] == 23

    async def test_stages_are_ordered_and_dated(self, client: AsyncClient):
        cycle = (await client.get("/api/admission-cycles")).json()[0]
        assert [s["ordinal"] for s in cycle["stages"]] == [1, 2]
        assert cycle["stages"][0]["starts_on"] == "2026-05-13"


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


class TestHealth:
    async def test_health_reports_the_database(self, client: AsyncClient):
        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"ok": True, "db": "ok"}
