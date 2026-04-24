"""Library: discover earnings-call webcast URLs from a company IR page.

Crawls a starting URL, extracts earnings-event candidate links, follows
them to event detail pages, and extracts candidate media URLs (direct
MP3/M3U8, Brightcove, ON24, Open Exchange, generic iframe srcs).

Fetcher selection (plain HTTP vs. Playwright) is controlled by the
caller via the `use_browser` argument to `discover`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from signal_engine.ingestion.audio import browser as _browser
from signal_engine.ingestion.audio import http as _http
from signal_engine.ingestion.audio import wayback as _wayback
from signal_engine.ingestion.audio.patterns import EARNINGS_LINK_RE, MEDIA_URL_RE
from signal_engine.io import now_iso


@dataclass
class DiscoveredCall:
    ticker: str
    title: str
    link_text: str
    event_page_url: str
    event_page_snapshot_source: str
    candidate_media_urls: list[str] = field(default_factory=list)
    notes: str = ""
    discovered_at: str = ""


def fetch_html(url: str, use_browser: bool, timeout: int = 20, verbose: bool = False) -> str | None:
    if use_browser:
        return _browser.fetch_html_browser(url, timeout=max(timeout, 30), verbose=verbose)
    return _http.fetch_html(url, timeout=timeout, verbose=verbose)


def iter_candidate_links(html: str, base_url: str, verbose: bool) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue
        text = a.get_text(strip=True) or ""
        combined = f"{text} {href}"
        if not EARNINGS_LINK_RE.search(combined):
            if verbose:
                print(f"  skip  {text[:60]!r} -> {href[:80]}")
            continue
        absolute = urljoin(base_url, href)
        if absolute in seen:
            continue
        seen.add(absolute)
        out.append((absolute, text))
    return out


def extract_media_urls(html: str, base_url: str) -> list[str]:
    found: set[str] = set()
    for m in re.finditer(r"https?://[^\s\"'<>]+", html):
        url = m.group(0).rstrip(").,;")
        if MEDIA_URL_RE.search(url):
            found.add(url)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["iframe", "video", "audio", "source"]):
        src = tag.get("src") or tag.get("data-src")
        if not src:
            continue
        src = urljoin(base_url, src.strip())
        if MEDIA_URL_RE.search(src) or "player" in src.lower():
            found.add(src)
    return sorted(found)


def process_event_page(
    url: str,
    snapshot_source: str,
    link_text: str,
    ticker: str,
    use_browser: bool,
    verbose: bool = False,
) -> DiscoveredCall | None:
    html = fetch_html(url, use_browser=use_browser, verbose=verbose)
    if not html:
        return None
    media = extract_media_urls(html, url)
    if not media:
        return None
    soup = BeautifulSoup(html, "html.parser")
    page_title = ""
    if soup.title and soup.title.get_text(strip=True):
        page_title = soup.title.get_text(strip=True)
    h1 = soup.find(["h1", "h2"])
    if h1:
        page_title = page_title or h1.get_text(strip=True)
    title = page_title or link_text
    return DiscoveredCall(
        ticker=ticker,
        title=title[:200],
        link_text=link_text[:200],
        event_page_url=url,
        event_page_snapshot_source=snapshot_source,
        candidate_media_urls=media,
        discovered_at=now_iso(),
    )


def discover(
    ticker: str,
    start_url: str,
    use_wayback: bool,
    verbose: bool,
    use_browser: bool = False,
) -> list[DiscoveredCall]:
    print(f"[{ticker}] fetching index: {start_url}")
    index_html = fetch_html(start_url, use_browser=use_browser, verbose=True)
    if not index_html:
        print(f"[{ticker}] FAILED to fetch index page (see diagnostics above)")
        if use_wayback:
            print(f"[{ticker}] attempting Wayback Machine snapshot of index page...")
            for snap in _wayback.wayback_snapshot_urls(start_url, limit=5):
                print(f"[{ticker}]   trying snapshot: {snap}")
                index_html = fetch_html(snap, use_browser=use_browser, verbose=True)
                if index_html:
                    start_url = snap
                    print(f"[{ticker}]   using snapshot as index")
                    break
        if not index_html:
            return []

    candidates = iter_candidate_links(index_html, start_url, verbose)
    print(f"[{ticker}] {len(candidates)} candidate links on index page")

    calls: list[DiscoveredCall] = []
    for event_url, link_text in candidates:
        call = process_event_page(
            event_url, "live", link_text, ticker, use_browser, verbose=verbose
        )
        if call:
            calls.append(call)
            print(f"[{ticker}] + {call.title[:70]!r:80} "
                  f"({len(call.candidate_media_urls)} media url(s))")
        else:
            if verbose:
                print(f"[{ticker}]   no media on {event_url}")
            if use_wayback:
                for snap in _wayback.wayback_snapshot_urls(event_url, limit=3):
                    snap_call = process_event_page(
                        snap, "wayback", link_text, ticker, use_browser, verbose=verbose
                    )
                    if snap_call:
                        snap_call.notes = f"from wayback: {snap}"
                        calls.append(snap_call)
                        print(
                            f"[{ticker}] +wayback {snap_call.title[:60]!r:70} "
                            f"({len(snap_call.candidate_media_urls)} media url(s))"
                        )
                        break
    return calls
