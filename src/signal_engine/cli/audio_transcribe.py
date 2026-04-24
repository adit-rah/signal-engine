"""CLI: transcribe earnings call audio with WhisperX."""

from __future__ import annotations

import argparse
import os

from signal_engine.ingestion.audio.transcribe import transcribe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="Uppercase ticker symbol")
    parser.add_argument("date", help="Earnings call date, YYYY-MM-DD")
    parser.add_argument("--model", default="large-v3",
                        help="Whisper model size. Default: large-v3")
    parser.add_argument("--device", default="auto",
                        help="Compute device (cuda, cpu, mps, auto). Default: auto")
    parser.add_argument("--compute-type", default="int8",
                        help="Whisper compute type. Default: int8 for broad compatibility.")
    parser.add_argument("--language", default="en", help="Source language code. Default: en.")
    parser.add_argument("--no-diarize", action="store_true",
                        help="Skip speaker diarization (faster but no speaker labels).")
    parser.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"),
                        help="Hugging Face token for pyannote model download. "
                             "Can also be set via HF_TOKEN env var.")
    args = parser.parse_args()

    transcribe(
        args.ticker,
        args.date,
        model=args.model,
        device=args.device,
        compute_type=args.compute_type,
        language=args.language,
        diarize=not args.no_diarize,
        hf_token=args.hf_token,
    )


if __name__ == "__main__":
    main()
