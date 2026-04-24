"""CLI: discover transcript PDFs on a company IR site."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from signal_engine.ingestion.pdf.discover import (
    extract_pdf_links_from_page,
    filter_transcript_pdfs,
)
from signal_engine.paths import MANIFEST_DIR, relative


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker", help="Uppercase ticker symbol")
    p.add_argument("start_url", help="Primary IR page URL (usually quarterly results)")
    p.add_argument("--also", action="append", default=[],
                   help="Additional pages to scan; repeatable.")
    p.add_argument("--dump-pdfs", action="store_true",
                   help="Print every PDF URL found on the page (for debugging filters)")
    args = p.parse_args()

    ticker = args.ticker.upper()
    pages = [args.start_url] + args.also

    all_records = []
    for page_url in pages:
        print(f"[{ticker}] scanning: {page_url}")
        links = extract_pdf_links_from_page(page_url)
        print(f"  found {len(links)} PDF link(s) on page")
        if args.dump_pdfs:
            print("  --- all PDF URLs (for filter tuning) ---")
            for url, text in links:
                print(f"    {text[:60]!r:65}  {url}")
            print("  --- end ---")
        transcripts = filter_transcript_pdfs(links, ticker, page_url)
        print(f"  -> {len(transcripts)} look like earnings-call transcripts")
        for t in transcripts:
            q_year = ""
            if t.fiscal_quarter and t.fiscal_year_hint:
                q_year = f" (Q{t.fiscal_quarter} {t.fiscal_year_hint})"
            print(f"    + {t.call_date or '????-??-??'}{q_year}  {t.title[:80]}")
            print(f"      {t.pdf_url}")
        all_records.extend(transcripts)

    deduped = {r.pdf_url: r for r in all_records}
    records = sorted(deduped.values(), key=lambda r: r.call_date or "")

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{ticker}_transcript_pdfs.jsonl"
    with manifest_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r)) + "\n")

    print()
    print(f"Discovered {len(records)} transcript PDF(s).")
    print(f"Manifest: {relative(manifest_path)}")
    if not records:
        sys.exit(1)


if __name__ == "__main__":
    main()
