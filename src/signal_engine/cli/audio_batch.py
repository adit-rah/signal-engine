"""CLI: batch runner for Pipeline B (audio -> transcript)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from signal_engine.ingestion.audio.batch import (
    StageResult,
    append_run_log,
    audio_exists,
    normalized_exists,
    parse_call_date,
    skip_result,
    whisperx_output_exists,
)
from signal_engine.io import now_iso


def run_stage(cmd: list[str], stage: str, ticker: str, date: str) -> StageResult:
    now = now_iso()
    print(f"    -> {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False, capture_output=False)
    status = "ok" if proc.returncode == 0 else "error"
    return StageResult(
        ticker=ticker, call_date=date, stage=stage,
        status=status, message=f"exit {proc.returncode}", attempt_time=now,
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", help="Path to manifest JSONL from audio/discover")
    p.add_argument("--no-transcribe", action="store_true",
                   help="Stop after fetching audio; skip transcribe + normalize.")
    p.add_argument("--limit", type=int, default=0, help="Process at most N calls")
    p.add_argument("--overwrite-audio", action="store_true",
                   help="Re-download audio even if present.")
    p.add_argument("--no-diarize", action="store_true",
                   help="Pass --no-diarize to transcribe (faster, no speaker labels).")
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

    summary = {"processed": 0, "audio_ok": 0, "transcript_ok": 0, "skipped": 0, "errors": 0}

    for i, call in enumerate(entries, start=1):
        ticker = call["ticker"]
        date = parse_call_date(call)
        title = call.get("title", "")
        print(f"[{i}/{len(entries)}] {ticker} {date or '??'} — {title[:70]}")

        results: list[StageResult] = []

        if not date:
            msg = "could not parse call date from manifest entry; add call_date field to override"
            print(f"    SKIP: {msg}")
            results.append(skip_result(ticker, "", "parse_date", msg))
            summary["skipped"] += 1
            append_run_log(ticker, results)
            continue

        urls = call.get("candidate_media_urls", [])
        if call.get("event_page_url"):
            urls = [call["event_page_url"]] + urls
        if not urls:
            print("    SKIP: no candidate URLs in manifest entry")
            results.append(skip_result(ticker, date, "fetch_audio", "no candidate urls"))
            summary["skipped"] += 1
            append_run_log(ticker, results)
            continue

        if audio_exists(ticker, date) and not args.overwrite_audio:
            print("    AUDIO: already present, skipping fetch")
            results.append(skip_result(ticker, date, "fetch_audio", "already present"))
            summary["audio_ok"] += 1
            audio_got = True
        else:
            audio_got = False
            for url in urls:
                cmd = [
                    sys.executable, "-m", "signal_engine.cli.audio_fetch",
                    ticker, date, url, "--title", title[:200],
                ]
                if args.overwrite_audio:
                    cmd.append("--overwrite")
                r = run_stage(cmd, "fetch_audio", ticker, date)
                results.append(r)
                if r.status == "ok" and audio_exists(ticker, date):
                    audio_got = True
                    summary["audio_ok"] += 1
                    break
            else:
                print("    AUDIO: all candidate URLs failed")
                summary["errors"] += 1

        if args.no_transcribe or not audio_got:
            summary["processed"] += 1
            append_run_log(ticker, results)
            continue

        if whisperx_output_exists(ticker, date):
            print("    WHISPERX: already present, skipping")
            results.append(skip_result(ticker, date, "transcribe", "already present"))
        else:
            cmd = [sys.executable, "-m", "signal_engine.cli.audio_transcribe", ticker, date]
            if args.no_diarize:
                cmd.append("--no-diarize")
            results.append(run_stage(cmd, "transcribe", ticker, date))

        if normalized_exists(ticker, date):
            print("    NORMALIZE: already present, skipping")
            results.append(skip_result(ticker, date, "normalize", "already present"))
            summary["transcript_ok"] += 1
        else:
            cmd = [sys.executable, "-m", "signal_engine.cli.audio_normalize", ticker, date]
            r = run_stage(cmd, "normalize", ticker, date)
            results.append(r)
            if r.status == "ok":
                summary["transcript_ok"] += 1

        summary["processed"] += 1
        append_run_log(ticker, results)

    print()
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
