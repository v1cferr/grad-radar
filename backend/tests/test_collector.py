"""What must be true for the monitor to be worth reading.

The failure mode this guards against is not "the collector crashed" — that is
loud and gets fixed. It is the collector reporting a change on every run because
it hashes something unstable, until nobody reads the alerts any more.
"""

from __future__ import annotations

import httpx

from app import collector
from app.collector import digest, html_to_text, normalise


class TestNormalisation:
    def test_reflow_is_not_a_change(self):
        """Same words, different wrapping — the hash must not move."""
        a = normalise("Edital  01/2026\n\n\n  Inscrições   de 19/03 a 26/04 ")
        b = normalise("Edital 01/2026\n\nInscrições de 19/03 a 26/04")
        assert digest(a) == digest(b)

    def test_real_edit_is_a_change(self):
        a = normalise("Inscrições de 19/03 a 26/04")
        b = normalise("Inscrições de 19/03 a 30/04")
        assert digest(a) != digest(b)

    def test_crlf_matches_lf(self):
        assert normalise("linha 1\r\nlinha 2") == normalise("linha 1\nlinha 2")


class TestHtmlExtraction:
    def test_scripts_and_styles_are_dropped(self):
        """They carry build hashes that change on every deploy.

        Keeping them would make every check look like a content change on a page
        whose text never moved.
        """
        page = b"""
        <html><head><style>.a{color:red}</style>
        <script>window.__BUILD__="abc123"</script></head>
        <body><h1>Processo seletivo</h1><p>19/03 a 26/04</p></body></html>
        """
        text = html_to_text(page)
        assert "Processo seletivo" in text
        assert "19/03 a 26/04" in text
        assert "abc123" not in text
        assert "color:red" not in text

    def test_two_builds_of_the_same_page_hash_alike(self):
        build = (
            b'<html><head><script>window.__BUILD__="%s"</script></head>'
            b"<body><p>Edital 02/2026</p></body></html>"
        )
        assert digest(html_to_text(build % b"aaa")) == digest(html_to_text(build % b"bbb"))

    def test_visible_edit_still_registers(self):
        one = html_to_text(b"<html><body><p>23 vagas</p></body></html>")
        two = html_to_text(b"<html><body><p>21 vagas</p></body></html>")
        assert digest(one) != digest(two)


class TestPdfWithoutATextLayer:
    """The PPGPEP edital is 18 scanned pages. Extraction returns nothing.

    Before this, every image-only PDF hashed to the digest of "" — identical to
    each other and immovable, so a replaced edital read as "no change". Silence
    that looks like good news is the one failure this project cannot afford.
    """

    def test_empty_extraction_is_indistinguishable(self):
        """Why the fallback is necessary, stated as a fact rather than a comment."""
        assert digest(normalise("")) == digest(normalise("  \n\n "))

    async def test_falls_back_to_bytes_and_says_so(self, monkeypatch):
        monkeypatch.setattr(collector, "pdf_to_text", lambda raw: "")
        one = await _fetch_bytes(b"%PDF-1.4 scan A")
        two = await _fetch_bytes(b"%PDF-1.4 scan B")

        assert one.text_extractable is False
        assert one.content_hash != two.content_hash

    async def test_a_real_text_pdf_still_hashes_its_text(self, monkeypatch):
        body = "Edital PPGPEP 001/2026 " * 40  # comfortably over MIN_PDF_TEXT
        monkeypatch.setattr(collector, "pdf_to_text", lambda raw: body)
        one = await _fetch_bytes(b"build-1")
        two = await _fetch_bytes(b"build-2")

        # Same words, regenerated file: NOT a change. The original guarantee.
        assert one.text_extractable is True
        assert one.content_hash == two.content_hash


async def _fetch_bytes(raw: bytes):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=raw, headers={"content-type": "application/pdf"})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        return await collector.fetch("https://example.org/edital.pdf", client)
