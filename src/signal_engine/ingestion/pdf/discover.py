"""Library: discover earnings-call transcript PDFs on a company IR site.

Renders the IR page with Playwright (to defeat Cloudflare) and filters
linked PDFs to those that match the earnings-transcript filename
patterns. Historical-URL probing lives in `url_probing.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin

from signal_engine.ingestion.pdf.discover_patterns import (
    TRANSCRIPT_FILENAME_RE,
    parse_date_from_filename,
    parse_q_year_from_url,
)
from signal_engine.io import USER_AGENT, now_iso


@dataclass
class TranscriptPDF:
    ticker: str
    call_date: str
    fiscal_quarter: int
    fiscal_year_hint: int
    title: str
    pdf_url: str
    discovery_source: str
    source_page: str
    observed_at: str = field(default_factory=now_iso)


def extract_pdf_links_from_page(page_url: str) -> list[tuple[str, str]]:
    """Render page_url with Playwright and return (pdf_url, anchor_text) tuples.

    Lazy import: Playwright is heavy and only needed when running scrape.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Playwright is required. Run:\n"
            "  uv add playwright && uv run playwright install chromium"
        )

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            resp = page.goto(page_url, timeout=45_000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            for _ in range(8):
                page.evaluate("window.scrollBy(0, 1200)")
                page.wait_for_timeout(400)
            status = resp.status if resp else 0
            print(f"  playwright: status={status} url={page.url}")
            if status != 200:
                return []
            anchors = page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => [a.href, (a.textContent || '').trim()])"""
            )
            out = []
            for href, text in anchors:
                if not href or ".pdf" not in href.lower():
                    continue
                out.append((urljoin(page_url, href), text))
            return out
        finally:
            page.close()
            context.close()
            browser.close()


def filter_transcript_pdfs(
    links: list[tuple[str, str]], ticker: str, source_page: str
) -> list[TranscriptPDF]:
    results: list[TranscriptPDF] = []
    seen: set[str] = set()
    now = now_iso()
    for url, text in links:
        if url in seen:
            continue
        seen.add(url)
        path_lower = url.lower()
        text_lower = (text or "").lower()
        if not (TRANSCRIPT_FILENAME_RE.search(path_lower)
                or TRANSCRIPT_FILENAME_RE.search(text_lower)):
            continue
        filename = url.rsplit("/", 1)[-1]
        call_date = parse_date_from_filename(filename)
        q, year_hint = parse_q_year_from_url(url)
        title = text.strip() or filename
        results.append(TranscriptPDF(
            ticker=ticker,
            call_date=call_date,
            fiscal_quarter=q,
            fiscal_year_hint=year_hint,
            title=title[:200],
            pdf_url=url,
            discovery_source="scraped",
            source_page=source_page,
            observed_at=now,
        ))
    return results
