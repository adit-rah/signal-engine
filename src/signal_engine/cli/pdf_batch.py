"""CLI: batch runner for the PDF transcript pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from signal_engine.ingestion.pdf.batch import (
    StageResult,
    append_run_log,
    normalized_exists,
    pdf_raw_exists,
)
from signal_engine.io import now_iso


def run_stage(cmd: list[str], stage: str, ticker: str, date: str) -> StageResult:
    now = now_iso()
    print(f"    -> {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    status = "ok" if proc.returncode == 0 else "error"
    return StageResult(
        ticker=ticker, call_date=date, stage=stage,
        status=status, message=f"exit {proc.returncode}", attempt_time=now,
    )


def _skip_result(ticker: str, date: str, stage: str, msg: str) -> StageResult:
    return StageResult(
        ticker=ticker, call_date=date, stage=stage,
        status="skip", message=msg, attempt_time=now_iso(),
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", help="Path to manifest from pdf/discover")
    p.add_argument("--limit", type=int, default=0, help="Process at most N entries")
    p.add_argument("--overwrite", action="store_true",
                   help="Re-fetch and re-normalize even if present")
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    with manifest_path.open() as f:
        entries = [json.loads(line) for line in f if line.strip()]
    if args.limit:
        entries = entries[: args.limit]

    print(f"Manifest: {manifest_path}")
    print(f"Entries:  {len(entries)}")
    print()

    summary = {"processed": 0, "raw_ok": 0, "normalized_ok": 0, "skipped": 0, "errors": 0}

    for i, entry in enumerate(entries, start=1):
        ticker = entry["ticker"]
        date = entry.get("call_date", "").strip()
        title = entry.get("title", "")
        url = entry.get("pdf_url")
        print(f"[{i}/{len(entries)}] {ticker} {date or '??'} — {title[:70]}")

        results: list[StageResult] = []

        if not date:
            msg = "no call_date in manifest entry"
            print(f"    SKIP: {msg}")
            results.append(_skip_result(ticker, "", "parse_date", msg))
            summary["skipped"] += 1
            append_run_log(ticker, results)
            continue

        if pdf_raw_exists(ticker, date) and not args.overwrite:
            print("    FETCH: already present, skipping")
            results.append(_skip_result(ticker, date, "fetch_transcript_pdf", "already present"))
            summary["raw_ok"] += 1
            fetched = True
        else:
            cmd = [
                sys.executable, "-m", "signal_engine.cli.pdf_fetch",
                ticker, date, url, "--title", title[:200],
            ]
            if args.overwrite:
                cmd.append("--overwrite")
            r = run_stage(cmd, "fetch_transcript_pdf", ticker, date)
            results.append(r)
            fetched = r.status == "ok"
            if fetched:
                summary["raw_ok"] += 1
            else:
                summary["errors"] += 1

        if not fetched:
            summary["processed"] += 1
            append_run_log(ticker, results)
            continue

        if normalized_exists(ticker, date) and not args.overwrite:
            print("    NORMALIZE: already present, skipping")
            results.append(
                _skip_result(ticker, date, "normalize_pdf_transcript", "already present")
            )
            summary["normalized_ok"] += 1
        else:
            cmd = [sys.executable, "-m", "signal_engine.cli.pdf_normalize", ticker, date]
            r = run_stage(cmd, "normalize_pdf_transcript", ticker, date)
            results.append(r)
            if r.status == "ok":
                summary["normalized_ok"] += 1
            else:
                summary["errors"] += 1

        summary["processed"] += 1
        append_run_log(ticker, results)

    print()
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
