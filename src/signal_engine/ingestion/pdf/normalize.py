"""Library: normalize a PDF-sourced earnings-call transcript.

Transforms the raw pymupdf text into the DATA_MODEL.md Transcript
subtype shape (utterances, segments, rosters). The FactSet parser does
the block-level work; this module does the whitespace normalization
and utterance-record enrichment.
"""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def build_transcript_text(utterances: list[dict]) -> tuple[str, list[dict]]:
    """Build clean text + char-offset-enriched utterance records."""
    lines: list[str] = []
    pos = 0
    enriched: list[dict] = []
    for i, u in enumerate(utterances, start=1):
        speaker = u["speaker"]
        text = normalize_whitespace(u["text"])
        line = f"[{speaker}] {text}"
        start_char = pos
        lines.append(line)
        pos += len(line) + 1  # +1 newline
        end_char = pos - 1
        enriched.append({
            "utterance_id": f"U{i:04d}",
            "speaker_handle": speaker,
            "segment": u["segment"],
            "ordinal": i,
            "char_start": start_char,
            "char_end": end_char,
            "text": text,
        })
    return "\n".join(lines), enriched
