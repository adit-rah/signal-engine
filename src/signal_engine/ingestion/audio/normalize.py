"""Library: normalize WhisperX ASR output into a structured Transcript.

Coalesces consecutive same-speaker segments into Utterances and tags
Prepared-Remarks-vs-Q&A via heuristic cues (see patterns.QA_START_RE).
Output shape matches the PDF path, so downstream consumers don't care
about the source.
"""

from __future__ import annotations

import re

from signal_engine.ingestion.audio.patterns import QA_START_RE


def coalesce_utterances(segments: list[dict]) -> list[dict]:
    """Merge consecutive WhisperX segments that share a speaker."""
    utterances: list[dict] = []
    current: dict | None = None
    for seg in segments:
        speaker = seg.get("speaker", "UNKNOWN")
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", start))
        if current and current["speaker"] == speaker:
            current["text"] = f"{current['text']} {text}".strip()
            current["end"] = end
        else:
            if current is not None:
                utterances.append(current)
            current = {"speaker": speaker, "text": text, "start": start, "end": end}
    if current is not None:
        utterances.append(current)
    return utterances


def assign_segments(utterances: list[dict]) -> list[dict]:
    """Tag each utterance as Prepared Remarks or Q&A using heuristic cues."""
    in_qa = False
    for utt in utterances:
        if not in_qa and QA_START_RE.search(utt["text"]):
            in_qa = True
        utt["segment"] = "Q&A" if in_qa else "Prepared Remarks"
    return utterances


def normalize_whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def build_transcript_text(utterances: list[dict]) -> tuple[str, list[dict]]:
    """Build clean transcript text + char-offset-enriched utterance records."""
    lines: list[str] = []
    pos = 0
    enriched: list[dict] = []
    for i, utt in enumerate(utterances, start=1):
        speaker = utt["speaker"]
        text = normalize_whitespace(utt["text"])
        line = f"[{speaker}] {text}"
        start_char = pos
        lines.append(line)
        pos += len(line) + 1
        end_char = pos - 1
        enriched.append({
            "utterance_id": f"U{i:04d}",
            "speaker_handle": speaker,
            "segment": utt["segment"],
            "ordinal": i,
            "audio_start_seconds": round(utt["start"], 2),
            "audio_end_seconds": round(utt["end"], 2),
            "char_start": start_char,
            "char_end": end_char,
            "text": text,
        })
    return "\n".join(lines), enriched
