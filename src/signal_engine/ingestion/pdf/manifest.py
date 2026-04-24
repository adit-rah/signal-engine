"""Library: build a complete transcript-PDF manifest for a ticker.

Combines scrape-based discovery with historical-URL probing. Harvests
earnings dates from SEC 8-K filings (must be fetched first). The
orchestration that invokes this module is in `cli/pdf_manifest.py`.
"""

from __future__ import annotations

import calendar
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from signal_engine.paths import EDGAR_ROOT


@dataclass
class ManifestRecord:
    ticker: str
    call_date: str
    title: str
    pdf_url: str
    discovery_source: str
    source_page: str
    observed_at: str


def read_earnings_dates(ticker: str) -> list[str]:
    """Return YYYY-MM-DD call dates from the ticker's 8-K filings.

    Walks the filings dir and picks every 8-K that reports Item 2.02.
    Returns [] (with a warning) if no filings have been fetched.
    """
    filings_dir = EDGAR_ROOT / ticker / "8-K"
    if not filings_dir.exists():
        print(f"  WARNING: No SEC 8-K data at {filings_dir}. "
              f"Run edgar/fetch first.")
        return []
    dates: set[str] = set()
    for filing_dir in filings_dir.iterdir():
        full = filing_dir / "full-submission.txt"
        if not full.exists():
            continue
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        header = re.search(r"<SEC-HEADER>(.*?)</SEC-HEADER>", text, re.DOTALL)
        if not header:
            continue
        items = re.findall(r"ITEM INFORMATION:\s*(.+)", header.group(1))
        if not any("results of operations" in i.lower() for i in items):
            continue
        m = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d{8})", header.group(1))
        if m:
            yyyymmdd = m.group(1)
            dates.add(f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}")
    return sorted(dates)


def reconcile_dates_from_sec(
    scraped: list[dict], sec_dates: list[str]
) -> tuple[list[dict], int]:
    """Match scraped entries with empty call_date to the nearest SEC date.

    Uses fiscal_quarter + fiscal_year_hint from the scraped URL. Looks
    for an SEC date within 0-120 days after the calendar quarter end.
    Returns (updated_entries, fill_count).
    """
    if not sec_dates:
        return scraped, 0
    sec_dt = sorted(date.fromisoformat(d) for d in sec_dates)
    fills = 0
    out = []
    for entry in scraped:
        if entry.get("call_date"):
            out.append(entry)
            continue
        q = entry.get("fiscal_quarter") or 0
        year_hint = entry.get("fiscal_year_hint") or 0
        if not (q and year_hint):
            out.append(entry)
            continue
        month_end = q * 3
        last_day = calendar.monthrange(year_hint, month_end)[1]
        qe_cal = date(year_hint, month_end, last_day)
        best = None
        for d in sec_dt:
            delta = (d - qe_cal).days
            if 0 <= delta <= 120:
                if best is None or delta < (best - qe_cal).days:
                    best = d
        if best:
            entry = dict(entry)
            entry["call_date"] = best.isoformat()
            fills += 1
        out.append(entry)
    return out, fills


def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_manifest(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
