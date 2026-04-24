"""Library: extract earnings press releases from SEC 8-K filings.

Walks data/raw/sec-edgar-filings/, filters to earnings-related 8-Ks
(Item 2.02), extracts EX-99.1 (falling back to EX-99.2), strips HTML,
and writes normalized artifacts + sibling meta JSON under
data/normalized/press_releases/<TICKER>/.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from signal_engine.ingestion.edgar.sgml import (
    HTMLStripper,
    extract_exhibit,
    is_earnings_filing,
    parse_sec_header,
)
from signal_engine.paths import (
    EDGAR_ROOT,
    PRESS_RELEASE_DIR,
    PRESS_RELEASE_INDEX,
    PROJECT_ROOT,
    relative,
)


@dataclass
class FilingMetadata:
    ticker: str
    accession_number: str
    form_type: str
    filed_date: str
    period_of_report: str
    items: list[str]
    cik: str
    company_name: str
    is_earnings: bool
    raw_source: str
    raw_sha256: str
    extracted_exhibit: str | None
    normalized_text_path: str | None
    normalized_char_count: int | None
    observation_time: str


def process_filing(raw_path: Path, ticker: str) -> FilingMetadata | None:
    try:
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"  ! unreadable: {raw_path.name}: {exc}")
        return None

    raw_sha = hashlib.sha256(raw_text.encode("utf-8", errors="replace")).hexdigest()[:16]
    header = parse_sec_header(raw_text)
    is_earnings = is_earnings_filing(header.get("items", []))

    meta = FilingMetadata(
        ticker=ticker,
        accession_number=header.get("accession_number", raw_path.parent.name),
        form_type=header.get("form_type", "8-K"),
        filed_date=header.get("filed_date", ""),
        period_of_report=header.get("period_of_report", ""),
        items=header.get("items", []),
        cik=header.get("cik", ""),
        company_name=header.get("company_name", ""),
        is_earnings=is_earnings,
        raw_source=str(raw_path.relative_to(PROJECT_ROOT)),
        raw_sha256=raw_sha,
        extracted_exhibit=None,
        normalized_text_path=None,
        normalized_char_count=None,
        observation_time=datetime.utcnow().isoformat(timespec="seconds") + "Z",
    )

    if not is_earnings:
        return meta

    for exhibit_type in ("EX-99.1", "EX-99.2"):
        html = extract_exhibit(raw_text, exhibit_type)
        if not html:
            continue
        stripper = HTMLStripper()
        stripper.feed(html)
        clean = stripper.text()
        if len(clean) < 500:
            continue
        out_dir = PRESS_RELEASE_DIR / ticker
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{meta.period_of_report or meta.filed_date}_{meta.accession_number}"
        text_path = out_dir / f"{stem}.txt"
        text_path.write_text(clean, encoding="utf-8")
        meta.extracted_exhibit = exhibit_type
        meta.normalized_text_path = relative(text_path)
        meta.normalized_char_count = len(clean)
        (out_dir / f"{stem}.meta.json").write_text(
            json.dumps(asdict(meta), indent=2), encoding="utf-8"
        )
        break

    return meta


def extract_all_press_releases() -> list[FilingMetadata]:
    """Scan every ticker + 8-K under EDGAR_ROOT. Writes the aggregated index."""
    if not EDGAR_ROOT.exists():
        raise SystemExit(f"Raw directory not found: {EDGAR_ROOT}")

    PRESS_RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    PRESS_RELEASE_INDEX.parent.mkdir(parents=True, exist_ok=True)

    print(f"Scanning: {EDGAR_ROOT}")
    print(f"Writing normalized output to: {PRESS_RELEASE_DIR}")
    print(f"Writing index to: {PRESS_RELEASE_INDEX}")
    print()

    all_records: list[FilingMetadata] = []
    tickers = sorted(p.name for p in EDGAR_ROOT.iterdir() if p.is_dir())
    if not tickers:
        raise SystemExit("No tickers found under raw directory.")

    for ticker in tickers:
        print(f"[{ticker}]")
        for form_dir in sorted((EDGAR_ROOT / ticker).iterdir()):
            if not form_dir.is_dir() or form_dir.name != "8-K":
                continue
            for filing_dir in sorted(form_dir.iterdir()):
                raw_path = filing_dir / "full-submission.txt"
                if not raw_path.exists():
                    continue
                meta = process_filing(raw_path, ticker)
                if meta:
                    all_records.append(meta)

        n_total = sum(1 for r in all_records if r.ticker == ticker)
        n_earn = sum(1 for r in all_records if r.ticker == ticker and r.is_earnings)
        n_extracted = sum(
            1 for r in all_records if r.ticker == ticker and r.normalized_text_path
        )
        print(
            f"  processed {n_total} filings | "
            f"{n_earn} earnings-related | "
            f"{n_extracted} press releases extracted"
        )

    with PRESS_RELEASE_INDEX.open("w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(asdict(rec)) + "\n")

    return all_records
