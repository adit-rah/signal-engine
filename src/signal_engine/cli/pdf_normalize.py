"""CLI: normalize a PDF-sourced earnings-call transcript."""

from __future__ import annotations

import argparse
import json

from signal_engine.ingestion.pdf.factset import normalize_factset
from signal_engine.ingestion.pdf.normalize import build_transcript_text
from signal_engine.io import now_iso
from signal_engine.paths import PDF_RAW_ROOT, TRANSCRIPT_DIR, relative


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="Uppercase ticker symbol")
    parser.add_argument("date", help="Earnings call date, YYYY-MM-DD")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    in_dir = PDF_RAW_ROOT / ticker / args.date
    raw_text_path = in_dir / "raw_text.txt"
    source_meta_path = in_dir / "source.meta.json"

    if not raw_text_path.exists():
        raise SystemExit(
            f"Missing raw text: {raw_text_path}. Run pdf/fetch first."
        )

    raw_text = raw_text_path.read_text(encoding="utf-8")
    source_meta = (
        json.loads(source_meta_path.read_text(encoding="utf-8"))
        if source_meta_path.exists() else {}
    )

    print(f"Ticker: {ticker}")
    print(f"Date:   {args.date}")
    print(f"Source: {relative(raw_text_path)}")
    print()

    utterances, corporate, analysts, stats = normalize_factset(raw_text)
    print(f"Cleaned lines: {stats['raw_line_count']}")
    print(f"Segments: {stats['segments_observed']}")
    print(f"Total utterances parsed: {stats['utterance_count_total']}")
    print(f"Content utterances (Prepared Remarks + Q&A): {stats['utterance_count_content']}")
    print(f"Corporate roster: {list(corporate.keys())}")
    print(f"Analyst roster: {list(analysts.keys())}")

    if not utterances:
        raise SystemExit(
            "Parser produced 0 content utterances. "
            "The transcript format may be different from what this parser handles."
        )

    segment_counts: dict[str, int] = {}
    speaker_counts: dict[str, int] = {}
    for u in utterances:
        segment_counts[u["segment"]] = segment_counts.get(u["segment"], 0) + 1
        speaker_counts[u["speaker"]] = speaker_counts.get(u["speaker"], 0) + 1
    for seg, n in segment_counts.items():
        print(f"  {seg}: {n} utterance(s)")
    print(
        "Speaker turn counts: "
        f"{dict(sorted(speaker_counts.items(), key=lambda kv: -kv[1]))}"
    )

    text, enriched = build_transcript_text(utterances)

    out_dir = TRANSCRIPT_DIR / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    text_path = out_dir / f"{args.date}.txt"
    meta_path = out_dir / f"{args.date}.meta.json"
    utt_path = out_dir / f"{args.date}.utterances.jsonl"

    text_path.write_text(text, encoding="utf-8")
    with utt_path.open("w", encoding="utf-8") as f:
        for u in enriched:
            f.write(json.dumps(u) + "\n")

    meta = {
        "ticker": ticker,
        "call_date": args.date,
        "document_subtype": "Transcript",
        "source_origin": "issuer_published_pdf",
        "source_meta": source_meta,
        "corporate_roster": corporate,
        "analyst_roster": analysts,
        "utterance_count": len(enriched),
        "segment_counts": segment_counts,
        "speaker_turn_counts": speaker_counts,
        "char_count": len(text),
        "normalized_text_path": relative(text_path),
        "utterances_path": relative(utt_path),
        "observation_time": now_iso(),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print()
    print(f"Transcript: {relative(text_path)} ({len(text):,} chars)")
    print(f"Utterances: {relative(utt_path)} ({len(enriched)} records)")
    print(f"Meta:       {relative(meta_path)}")


if __name__ == "__main__":
    main()
