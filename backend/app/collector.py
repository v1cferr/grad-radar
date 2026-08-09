"""Fetch a monitored source and reduce it to comparable text.

Three lessons from the research phase are baked in here, and each one cost time
to learn:

**Follow redirects.** The page that publishes the semester timetable answers 302
to a PDF inside SEI. A client that does not follow it comes back with nothing and
reports success.

**The fact lives in the PDF.** Admission cycle pages are link hubs — dates, seats
and stages are inside the edital. Text extraction is not a nice-to-have.

**Except when there is no text to hash.** The PPGPEP edital is 18 scanned pages
with no text layer: extraction returns "". Hashing that would give every image-only
PDF the SAME digest as every other, so a replaced edital would read as "no change"
— the exact silence this project exists to break. Those fall back to the raw bytes
and say so, accepting the occasional false alarm over guaranteed blindness.

**Never hash raw bytes** (otherwise). A regenerated PDF differs byte-for-byte while saying the
same thing (embedded timestamps, object ids), and raw HTML changes on every
request (session tokens, ads, build hashes). Hashing the *extracted text* is what
makes "did this change?" mean "did the content change?" — the whole point of the
monitor.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

USER_AGENT = "GradRadar/0.1 (+https://github.com/v1cferr/grad-radar)"
TIMEOUT = httpx.Timeout(30.0, connect=15.0)

_WHITESPACE = re.compile(r"[ \t ]+")
_BLANKLINES = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class Fetched:
    """One retrieval. ``text`` is what gets hashed and compared."""

    final_url: str
    http_status: int
    content_type: str
    text: str
    content_hash: str
    redirected: bool
    error: str | None = None

    # False when the hash is over raw bytes because no text could be extracted.
    # Surfaced so a change on such a source is read with the right suspicion: it
    # may be a re-scan of an identical document.
    text_extractable: bool = True

    @property
    def ok(self) -> bool:
        return self.error is None and 200 <= self.http_status < 300


def normalise(text: str) -> str:
    """Collapse whitespace so cosmetic reflow does not read as a change."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return _BLANKLINES.sub("\n\n", text).strip()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def html_to_text(raw: bytes) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    # Script and style carry build hashes and inline state that change on every
    # request; keeping them would make every check look like a change.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return normalise(soup.get_text("\n"))


# Below this many characters a PDF is treated as having no text layer. A real
# edital page carries thousands; a scanned one yields a handful of stray marks
# from the OCR-less extractor, and 0 is not a safe threshold because of those.
MIN_PDF_TEXT = 200


def pdf_to_text(raw: bytes) -> str:
    from io import BytesIO

    reader = PdfReader(BytesIO(raw))
    return normalise("\n".join(page.extract_text() or "" for page in reader.pages))


async def fetch(url: str, client: httpx.AsyncClient | None = None) -> Fetched:
    """Retrieve a source and reduce it to normalised text.

    Never raises: a monitor that dies on one unreachable source stops watching
    the others. Failures come back as a ``Fetched`` with ``error`` set, so the
    caller can record the attempt and move on.
    """
    owned = client is None
    client = client or httpx.AsyncClient(
        follow_redirects=True, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}
    )
    try:
        response = await client.get(url)
        raw = response.content
        content_type = response.headers.get("content-type", "").split(";")[0].strip()

        extractable = True
        if "pdf" in content_type or url.lower().endswith(".pdf"):
            text = pdf_to_text(raw)
            if len(text) < MIN_PDF_TEXT:
                # Scanned pages. Keep whatever little was extracted for the record,
                # but hash the bytes — otherwise every such PDF collapses onto one
                # digest and no replacement is ever detectable.
                extractable = False
        elif "html" in content_type or not content_type:
            text = html_to_text(raw)
        else:
            text = normalise(raw.decode("utf-8", errors="replace"))

        return Fetched(
            final_url=str(response.url),
            http_status=response.status_code,
            content_type=content_type,
            text=text,
            content_hash=digest(text) if extractable else hashlib.sha256(raw).hexdigest(),
            redirected=str(response.url) != url,
            text_extractable=extractable,
        )
    except Exception as exc:  # noqa: BLE001 — any failure is "could not check"
        return Fetched(
            final_url=url,
            http_status=0,
            content_type="",
            text="",
            content_hash="",
            redirected=False,
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        if owned:
            await client.aclose()
