"""CLI: normalize WhisperX ASR output into a structured Transcript."""

from __future__ import annotations

import argparse
import json

from signal_engine.ingestion.audio.normalize import (
    assign_segments,
    build_transcript_text,
    coalesce_utterances,
)
from signal_engine.io import now_iso
from signal_engine.paths import AUDIO_RAW_ROOT, TRANSCRIPT_DIR, relative


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="Uppercase ticker symbol")
    parser.add_argument("date", help="Earnings call date, YYYY-MM-DD")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    in_dir = AUDIO_RAW_ROOT / ticker / args.date
    raw_path = in_dir / "whisperx_raw.json"
    audio_meta_path = in_dir / "source.meta.json"

    if not raw_path.exists():
        raise SystemExit(f"Missing ASR output: {raw_path}")

    envelope = json.loads(raw_path.read_text(encoding="utf-8"))
    segments = envelope.get("result", {}).get("segments", [])
    if not segments:
        raise SystemExit(f"No segments in {raw_path}")

    audio_meta = (
        json.loads(audio_meta_path.read_text(encoding="utf-8"))
        if audio_meta_path.exists() else {}
    )

    print(f"Ticker: {ticker}")
    print(f"Date:   {args.date}")
    print(f"Raw ASR segments: {len(segments)}")

    utterances = coalesce_utterances(segments)
    print(f"Coalesced utterances: {len(utterances)}")
    utterances = assign_segments(utterances)
    prep_count = sum(1 for u in utterances if u["segment"] == "Prepared Remarks")
    qa_count = sum(1 for u in utterances if u["segment"] == "Q&A")
    print(f"  Prepared Remarks: {prep_count}")
    print(f"  Q&A: {qa_count}")

    transcript_text, enriched = build_transcript_text(utterances)

    out_dir = TRANSCRIPT_DIR / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    text_path = out_dir / f"{args.date}.txt"
    meta_path = out_dir / f"{args.date}.meta.json"
    utt_path = out_dir / f"{args.date}.utterances.jsonl"

    text_path.write_text(transcript_text, encoding="utf-8")

    speakers = sorted({u["speaker_handle"] for u in enriched})
    meta = {
        "ticker": ticker,
        "call_date": args.date,
        "document_subtype": "Transcript",
        "source_origin": "ir_webcast_asr",
        "audio_meta": audio_meta,
        "whisper_model": envelope.get("whisper_model"),
        "diarization_used": envelope.get("diarization"),
        "language": envelope.get("language"),
        "speaker_handles": speakers,
        "utterance_count": len(enriched),
        "prepared_remarks_count": prep_count,
        "qa_count": qa_count,
        "char_count": len(transcript_text),
        "normalized_text_path": relative(text_path),
        "utterances_path": relative(utt_path),
        "observation_time": now_iso(),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    with utt_path.open("w", encoding="utf-8") as f:
        for utt in enriched:
            f.write(json.dumps(utt) + "\n")

    print()
    print(f"Transcript: {relative(text_path)} ({meta['char_count']:,} chars)")
    print(f"Utterances: {relative(utt_path)} ({meta['utterance_count']} records)")
    print(f"Meta:       {relative(meta_path)}")
    print(f"Speakers:   {', '.join(speakers)}")


if __name__ == "__main__":
    main()
