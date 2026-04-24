"""Top-level V1 ingestion orchestrator.

Reads config/v1_companies.json and runs the full pipeline for every
ticker: EDGAR fetch -> press-release extraction -> PDF manifest build
-> PDF batch. Idempotent; re-running only fetches what's missing.

Per-stage invocations go through `python -m signal_engine.cli.<stage>`
so the orchestrator doesn't depend on on-disk shim paths.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from signal_engine.config.companies import load_v1_companies
from signal_engine.paths import (
    EDGAR_ROOT,
    MANIFEST_DIR,
    PRESS_RELEASE_DIR,
    PROJECT_ROOT,
    TRANSCRIPT_DIR,
    relative,
)


STAGES = ("filings", "press_releases", "discover", "transcripts")


def run(cmd: list[str], label: str) -> int:
    print(f"    -> {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print(f"    [{label}] exit {proc.returncode}")
    return proc.returncode


def count_files(path, pattern: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob(pattern))


def count_manifest_rows(path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.open() if line.strip())


def summarize(ticker: str) -> dict:
    return {
        "ticker": ticker,
        "edgar_filings": count_files(EDGAR_ROOT / ticker / "8-K", "full-submission.txt"),
        "press_releases": count_files(PRESS_RELEASE_DIR / ticker, "*.txt"),
        "transcript_pdfs_in_manifest": count_manifest_rows(
            MANIFEST_DIR / f"{ticker}_transcript_pdfs.jsonl"
        ),
        "normalized_transcripts": count_files(TRANSCRIPT_DIR / ticker, "*.txt"),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", nargs="+", default=None,
                   help="Restrict to these tickers (default: all)")
    p.add_argument("--stage", choices=STAGES, default=None,
                   help="Run only one stage of the pipeline.")
    p.add_argument("--after", default="2019-01-01",
                   help="Earliest filing date for edgar/fetch")
    p.add_argument("--limit", type=int, default=0,
                   help="Pass --limit to pdf/batch")
    args = p.parse_args()

    companies = load_v1_companies(args.only)
    print(f"v1 ingestion across {len(companies)} ticker(s): "
          f"{[c['ticker'] for c in companies]}")
    print(f"Stages: {[args.stage] if args.stage else list(STAGES)}")
    print()

    def should_run(stage: str) -> bool:
        return args.stage is None or args.stage == stage

    for entry in companies:
        ticker = entry["ticker"]
        ir_url = entry["ir_quarterly_url"]
        print(f"=== {ticker} — {entry.get('narrative_profile', '')[:80]} ===")

        if should_run("filings"):
            print(f"  [filings] edgar/fetch")
            run([sys.executable, "-m", "signal_engine.cli.edgar_fetch",
                 ticker, "--after", args.after], "filings")

        if should_run("press_releases"):
            print(f"  [press_releases] edgar/extract_press_releases")
            run([sys.executable, "-m", "signal_engine.cli.edgar_press_releases"],
                "press_releases")

        if should_run("discover"):
            print(f"  [discover] pdf/build_manifest")
            run([sys.executable, "-m", "signal_engine.cli.pdf_manifest",
                 ticker, ir_url], "discover")

        if should_run("transcripts"):
            manifest = MANIFEST_DIR / f"{ticker}_transcript_pdfs.jsonl"
            if not manifest.exists():
                print(f"  [transcripts] SKIP — no manifest at {relative(manifest)}")
            else:
                print(f"  [transcripts] pdf/batch")
                cmd = [sys.executable, "-m", "signal_engine.cli.pdf_batch", str(manifest)]
                if args.limit:
                    cmd.extend(["--limit", str(args.limit)])
                run(cmd, "transcripts")

        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    header = f"{'ticker':<8} {'filings':>10} {'press_rel':>10} {'manifest':>10} {'transcripts':>12}"
    print(header)
    print("-" * len(header))
    for entry in companies:
        s = summarize(entry["ticker"])
        print(f"{s['ticker']:<8} {s['edgar_filings']:>10} "
              f"{s['press_releases']:>10} {s['transcript_pdfs_in_manifest']:>10} "
              f"{s['normalized_transcripts']:>12}")


if __name__ == "__main__":
    main()
