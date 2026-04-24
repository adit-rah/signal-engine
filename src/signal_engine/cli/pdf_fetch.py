"""CLI: download a transcript PDF and extract raw text."""

from __future__ import annotations

import argparse
import json

import requests

from signal_engine.ingestion.pdf.fetch import extract_text
from signal_engine.io import USER_AGENT, now_iso, sha256_file
from signal_engine.paths import PDF_RAW_ROOT, PROJECT_ROOT, relative


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker", help="Uppercase ticker symbol")
    p.add_argument("date", help="Earnings call date, YYYY-MM-DD")
    p.add_argument("url", help="PDF URL (typically on an IR CDN)")
    p.add_argument("--title", default="", help="Optional title, e.g. 'Q3 FY26'")
    p.add_argument("--overwrite", action="store_true",
                   help="Re-download / re-extract even if artifacts exist")
    args = p.parse_args()

    ticker = args.ticker.upper()
    out_dir = PDF_RAW_ROOT / ticker / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "source.pdf"
    text_path = out_dir / "raw_text.txt"

    if pdf_path.exists() and text_path.exists() and not args.overwrite:
        print(f"Artifacts already present at {out_dir.relative_to(PROJECT_ROOT)}")
        print("Use --overwrite to re-fetch.")
        return

    print(f"Ticker: {ticker}")
    print(f"Date:   {args.date}")
    print(f"URL:    {args.url}")
    print(f"Output: {out_dir.relative_to(PROJECT_ROOT)}")
    print()

    if not pdf_path.exists() or args.overwrite:
        print(f"Downloading PDF...")
        resp = requests.get(
            args.url, headers={"User-Agent": USER_AGENT},
            timeout=60, allow_redirects=True,
        )
        if resp.status_code != 200:
            raise SystemExit(
                f"Download failed: status={resp.status_code} for {args.url}"
            )
        ctype = resp.headers.get("Content-Type", "")
        if "pdf" not in ctype.lower() and not args.url.lower().endswith(".pdf"):
            print(f"  WARNING: Content-Type is {ctype!r}, may not be a PDF")
        pdf_path.write_bytes(resp.content)
        print(f"  wrote {relative(pdf_path)} ({len(resp.content):,} bytes)")

    print("Extracting text with pymupdf...")
    text, extraction_meta = extract_text(pdf_path)
    text_path.write_text(text, encoding="utf-8")
    print(f"  wrote {relative(text_path)} "
          f"({extraction_meta['char_count']:,} chars across "
          f"{extraction_meta['page_count']} pages)")

    source_meta = {
        "ticker": ticker,
        "call_date": args.date,
        "title": args.title,
        "source_url": args.url,
        "pdf_path": relative(pdf_path),
        "pdf_sha256": sha256_file(pdf_path),
        "pdf_bytes": pdf_path.stat().st_size,
        "raw_text_path": relative(text_path),
        "raw_text_char_count": extraction_meta["char_count"],
        "fetched_with": "requests",
        "extracted_with": extraction_meta["extracted_with"],
        "page_count": extraction_meta["page_count"],
        "page_char_offsets": extraction_meta["page_char_offsets"],
        "pdf_metadata": extraction_meta["pdf_metadata"],
        "observation_time": now_iso(),
        "licensing_posture": "training_compatible",
        "licensing_rationale": (
            "Published directly by the issuer on its own IR site as a "
            "voluntary, public disclosure for all investors."
        ),
    }
    (out_dir / "source.meta.json").write_text(
        json.dumps(source_meta, indent=2), encoding="utf-8"
    )
    print()
    print(f"Meta: {relative(out_dir / 'source.meta.json')}")


if __name__ == "__main__":
    main()
