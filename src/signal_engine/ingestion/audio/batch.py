"""Library: helpers for the audio pipeline batch runner.

Date parsing from manifest entries and "have we already done this
stage?" checks. The orchestration loop itself lives in
`cli/audio_batch.py`.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from signal_engine.ingestion.audio.patterns import MONTHS
from signal_engine.io import now_iso
from signal_engine.paths import AUDIO_RAW_ROOT, MANIFEST_DIR, TRANSCRIPT_DIR


@dataclass
class StageResult:
    ticker: str
    call_date: str
    stage: str
    status: str
    message: str
    attempt_time: str


def parse_call_date(call: dict) -> str | None:
    """Parse YYYY-MM-DD from a manifest entry. Returns None if impossible."""
    if call.get("call_date"):
        return call["call_date"]
    blob = " ".join(str(call.get(k, "")) for k in ("title", "link_text", "event_page_url"))
    m = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", blob)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    m = re.search(
        r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2}),?\s+(20\d{2})\b",
        blob, re.IGNORECASE,
    )
    if m:
        mo = MONTHS[m.group(1).lower()]
        return f"{m.group(3)}-{mo}-{int(m.group(2)):02d}"
    m = re.search(r"\b(20\d{2})(\d{2})(\d{2})\b", blob)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def audio_exists(ticker: str, date: str) -> bool:
    d = AUDIO_RAW_ROOT / ticker / date
    if not d.exists():
        return False
    return any(
        p.suffix.lower() in {".mp3", ".m4a", ".wav", ".opus", ".flac", ".webm"}
        for p in d.glob("source.*")
    )


def whisperx_output_exists(ticker: str, date: str) -> bool:
    return (AUDIO_RAW_ROOT / ticker / date / "whisperx_raw.json").exists()


def normalized_exists(ticker: str, date: str) -> bool:
    return (TRANSCRIPT_DIR / ticker / f"{date}.txt").exists()


def skip_result(ticker: str, date: str, stage: str, msg: str) -> StageResult:
    return StageResult(
        ticker=ticker, call_date=date, stage=stage,
        status="skip", message=msg, attempt_time=now_iso(),
    )


def append_run_log(ticker: str, results: list[StageResult]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    log_path = MANIFEST_DIR / f"{ticker}_pipeline_runs.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + "\n")
