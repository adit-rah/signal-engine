"""CLI: build a complete transcript-PDF manifest (discover + probe)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import asdict

from signal_engine.ingestion.pdf.manifest import (
    ManifestRecord,
    load_manifest,
    read_earnings_dates,
    reconcile_dates_from_sec,
    write_manifest,
)
from signal_engine.ingestion.pdf.url_probing import (
    generate_candidates,
    head_probe,
    learn_template,
)
from signal_engine.io import now_iso
from signal_engine.paths import MANIFEST_DIR, relative


def run_discover(ticker: str, ir_url: str) -> int:
    print(f"[1/5] Running pdf/discover for {ticker}")
    cmd = [sys.executable, "-m", "signal_engine.cli.pdf_discover", ticker, ir_url]
    return subprocess.run(cmd, check=False).returncode


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker", help="Uppercase ticker symbol")
    p.add_argument("ir_url", help="IR page URL for pdf/discover")
    p.add_argument("--skip-discover", action="store_true",
                   help="Don't re-run pdf/discover; use existing manifest only.")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    ticker = args.ticker.upper()
    manifest_path = MANIFEST_DIR / f"{ticker}_transcript_pdfs.jsonl"

    if not args.skip_discover:
        rc = run_discover(ticker, args.ir_url)
        if rc != 0:
            print(f"  pdf/discover exited {rc}; continuing with whatever it wrote")

    scraped = load_manifest(manifest_path)
    print(f"[2/5] {len(scraped)} scraped entries in manifest")
    if not scraped:
        raise SystemExit(
            "No scraped entries. Either the IR page URL is wrong, the page "
            "requires --browser but discover didn't use it, or the filename "
            "patterns don't match anything. Try:\n"
            f"  uv run python bin/scripts/pdf/discover.py {ticker} <ir_url> --dump-pdfs\n"
            "to see what PDFs are actually on the page."
        )

    print(f"[3/5] Reading SEC earnings-call dates for {ticker}")
    sec_dates = read_earnings_dates(ticker)
    print(f"  {len(sec_dates)} earnings-call dates found in SEC 8-K data")
    if args.verbose:
        for d in sec_dates:
            print(f"    {d}")

    scraped, filled = reconcile_dates_from_sec(scraped, sec_dates)
    if filled:
        print(f"  filled {filled} missing call_date(s) from Q-Year + SEC match")

    scraped_dates = {e.get("call_date") for e in scraped if e.get("call_date")}
    scraped_with_dates = sum(1 for e in scraped if e.get("call_date"))
    print(f"  {scraped_with_dates}/{len(scraped)} scraped entries now have call_date")

    template = learn_template([e["pdf_url"] for e in scraped])
    if template:
        print(f"  template.base = {template.base}")
        print(f"  template.time = {template.time}")
    else:
        print("  URL template inference failed — skipping historical probing.")
        print("  (This is fine when the IR page already links every historical")
        print("   transcript, as with META's layout.)")

    probed: list[ManifestRecord] = []
    if template:
        print(f"[4/5] Probing historical URLs")
        sanity_url = next((e["pdf_url"] for e in scraped if e.get("pdf_url")), None)
        if sanity_url:
            sanity_ok = head_probe(sanity_url, verbose=True)
            if not sanity_ok:
                print("  SANITY FAIL: the probe mechanism could not confirm a")
                print("  known-live URL. Historical 'no match' results below are")
                print("  unreliable. This likely means the CDN is blocking the")
                print("  probe (rate-limit, UA filter) rather than files missing.")
            else:
                print(f"  sanity probe OK against known-live URL")

        now = now_iso()
        for sec_date in sec_dates:
            if sec_date in scraped_dates:
                if args.verbose:
                    print(f"  skip {sec_date} (already scraped)")
                continue
            candidates = generate_candidates(template, ticker, sec_date)
            hit = None
            for url in candidates:
                if head_probe(url, verbose=args.verbose):
                    hit = url
                    break
            if hit:
                probed.append(ManifestRecord(
                    ticker=ticker,
                    call_date=sec_date,
                    title=f"{ticker} Earnings Call {sec_date} (probed)",
                    pdf_url=hit,
                    discovery_source="probed",
                    source_page=args.ir_url,
                    observed_at=now,
                ))
                print(f"  + {sec_date}  probed: {hit.split('/')[-1]}")
            elif args.verbose:
                print(f"  - {sec_date}  no match across {len(candidates)} candidates")
    else:
        print(f"[4/5] Probing skipped (no template)")

    print(f"[5/5] Writing merged manifest")
    merged = scraped + [asdict(r) for r in probed]
    merged.sort(key=lambda r: r.get("call_date") or "")
    write_manifest(manifest_path, merged)

    with_dates = sum(1 for r in merged if r.get("call_date"))
    without_dates = len(merged) - with_dates
    print()
    print(f"Manifest: {relative(manifest_path)}")
    print(f"  scraped: {len(scraped)}")
    print(f"  probed:  {len(probed)}")
    print(f"  total:   {len(merged)}  ({with_dates} with call_date, "
          f"{without_dates} without)")


if __name__ == "__main__":
    main()
