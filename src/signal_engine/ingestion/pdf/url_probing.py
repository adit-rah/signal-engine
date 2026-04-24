"""Probe historical transcript-PDF URLs that are no longer linked.

Some companies remove old transcripts from the live IR index but keep
them on the CDN. Given a URL template learned from a scraped PDF and a
list of SEC earnings-call dates, we generate plausible historical URLs
and HEAD-probe each one.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass

import requests

from signal_engine.io import USER_AGENT


URL_TEMPLATE_RE = re.compile(
    r"^(?P<base>https?://[a-z0-9.-]+/\d+/files/doc_financials)"
    r"/(?P<fy>\d+)/q(?P<q>\d+)/"
    r"(?P<ticker>[A-Z]+)-Q(?P<q2>\d+)-(?P<fy2>\d+)-Earnings-Call-"
    r"(?P<day>\d+)-(?P<month>[A-Za-z]+)-(?P<year>\d+)-"
    r"(?P<time>[^.]+)\.pdf$",
    re.IGNORECASE,
)


@dataclass
class URLTemplate:
    base: str
    time: str


def learn_template(urls: list[str]) -> URLTemplate | None:
    for url in urls:
        m = URL_TEMPLATE_RE.match(url)
        if m:
            return URLTemplate(base=m.group("base"), time=m.group("time"))
    return None


def generate_candidates(template: URLTemplate, ticker: str, call_date: str) -> list[str]:
    """Generate plausible URL candidates for a given call date.

    Companies sometimes label fiscal years offset from the calendar
    year (NVIDIA's FY26 ended Jan 2026). This tries fiscal years
    spanning calendar year ±1 and quarters 1-4.
    """
    y, m, d = call_date.split("-")
    cal_year = int(y)
    month_num = int(m)
    day_num = int(d)
    month_name = calendar.month_name[month_num]

    candidates: list[str] = []
    for fy in (cal_year - 1, cal_year, cal_year + 1):
        for q in (1, 2, 3, 4):
            filename = (
                f"{ticker}-Q{q}-{fy}-Earnings-Call-"
                f"{day_num}-{month_name}-{cal_year}-"
                f"{template.time}.pdf"
            )
            candidates.append(f"{template.base}/{fy}/q{q}/{filename}")
    return candidates


def head_probe(url: str, timeout: int = 10, verbose: bool = False) -> bool:
    """Check whether a URL exists.

    Uses a ranged GET (bytes=0-0) rather than HEAD because several CDNs
    (q4cdn among them) 4xx on HEAD while happily serving GETs. Returns
    True for 200 (range ignored) or 206 (range honored).
    """
    try:
        r = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
            stream=True,
        )
        try:
            ok = r.status_code in (200, 206)
        finally:
            r.close()
        if verbose:
            print(f"    probe {r.status_code}  {url.rsplit('/', 1)[-1]}")
        return ok
    except requests.RequestException as e:
        if verbose:
            print(f"    probe ERR {type(e).__name__}  {url.rsplit('/', 1)[-1]}")
        return False
