"""Library: idempotent step-tracking helpers for the PDF batch runner.

Orchestration that iterates a manifest and invokes fetch → normalize
sits in `cli/pdf_batch.py`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from signal_engine.paths import MANIFEST_DIR, PDF_RAW_ROOT, TRANSCRIPT_DIR


@dataclass
class StageResult:
    ticker: str
    call_date: str
    stage: str
    status: str
    message: str
    attempt_time: str


def pdf_raw_exists(ticker: str, date: str) -> bool:
    return (PDF_RAW_ROOT / ticker / date / "raw_text.txt").exists()


def normalized_exists(ticker: str, date: str) -> bool:
    return (TRANSCRIPT_DIR / ticker / f"{date}.txt").exists()


def append_run_log(ticker: str, results: list[StageResult]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    log_path = MANIFEST_DIR / f"{ticker}_pdf_pipeline_runs.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + "\n")
