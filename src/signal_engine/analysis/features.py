"""Per-Document feature extraction for transcripts.

Press-release features live in `press_release_features.py`. The helpers
here — write_features, iter_transcript_dates, iter_press_release_stems
— are shared by both extractors and by the orchestration layer in
`cli/features.py`.
"""

from __future__ import annotations

from pathlib import Path

from signal_engine.analysis.feature_primitives import (
    count_phrase_matches,
    density,
    tokenize_words,
)
from signal_engine.config.themes import load_themes_for
from signal_engine.domain.entity import resolve_speaker_handle_to_canonical
from signal_engine.io import now_iso, read_jsonl, write_json
from signal_engine.paths import (
    FEATURES_DIR,
    PRESS_RELEASE_DIR,
    TRANSCRIPT_DIR,
    relative,
)


def extract_transcript_features(
    ticker: str,
    date: str,
    entity: dict,
    hedges: list[str],
    boosters: list[str],
) -> dict:
    utterances_path = TRANSCRIPT_DIR / ticker / f"{date}.utterances.jsonl"
    meta_path = TRANSCRIPT_DIR / ticker / f"{date}.meta.json"
    if not utterances_path.exists():
        raise SystemExit(f"Missing utterances: {utterances_path}")
    utterances = read_jsonl(utterances_path)
    speakers_cfg = entity.get("speakers", [])
    themes = load_themes_for(entity["canonical_id"])

    doc_words = doc_hedges = doc_boosters = 0
    prep_words = qa_words = qa_turns = 0
    qa_question_lengths: list[int] = []
    per_speaker: dict[str, dict] = {}
    hedge_evidence: dict[str, list[str]] = {}
    theme_counts: dict[str, int] = {t: 0 for t in themes}
    theme_evidence: dict[str, list[str]] = {t: [] for t in themes}

    for utt in utterances:
        text = utt.get("text") or ""
        speaker_handle = utt.get("speaker_handle") or ""
        utt_id = utt.get("utterance_id", "")
        segment = utt.get("segment", "")

        words = tokenize_words(text)
        n = len(words)
        h = count_phrase_matches(text, hedges)
        b = count_phrase_matches(text, boosters)

        doc_words += n
        doc_hedges += h
        doc_boosters += b

        if segment == "Prepared Remarks":
            prep_words += n
        elif segment == "Q&A":
            qa_words += n
            qa_turns += 1
            if "?" in text:
                qa_question_lengths.append(n)

        canonical = resolve_speaker_handle_to_canonical(speaker_handle, speakers_cfg) \
            or f"unresolved::{speaker_handle or 'unknown'}"

        rec = per_speaker.setdefault(canonical, {
            "word_count": 0, "turn_count": 0,
            "hedge_count": 0, "booster_count": 0,
            "name_variant_seen": speaker_handle,
        })
        rec["word_count"] += n
        rec["turn_count"] += 1
        rec["hedge_count"] += h
        rec["booster_count"] += b

        if h > 0:
            hedge_evidence.setdefault(canonical, []).append(utt_id)

        for theme_id, phrases in themes.items():
            cnt = count_phrase_matches(text, phrases)
            if cnt > 0:
                theme_counts[theme_id] += cnt
                theme_evidence[theme_id].append(utt_id)

    for rec in per_speaker.values():
        wc = rec["word_count"]
        rec["hedge_density"] = density(rec["hedge_count"], wc)
        rec["booster_density"] = density(rec["booster_count"], wc)
        rec["certainty_score"] = rec["booster_density"] - rec["hedge_density"]

    qa_avg_q_len = (sum(qa_question_lengths) / len(qa_question_lengths)
                    if qa_question_lengths else 0.0)

    return {
        "document_id": f"{ticker}_{date}_transcript",
        "entity_canonical_id": entity["canonical_id"],
        "ticker": ticker,
        "call_date": date,
        "document_subtype": "transcript",
        "source_meta_path": relative(meta_path) if meta_path.exists() else "",
        "extraction_time": now_iso(),
        "document_level": {
            "word_count": doc_words,
            "hedge_count": doc_hedges,
            "booster_count": doc_boosters,
            "hedge_density": density(doc_hedges, doc_words),
            "booster_density": density(doc_boosters, doc_words),
            "certainty_score": density(doc_boosters, doc_words)
            - density(doc_hedges, doc_words),
            "prep_word_count": prep_words,
            "qa_word_count": qa_words,
            "qa_turn_count": qa_turns,
            "qa_avg_question_length": qa_avg_q_len,
        },
        "per_speaker": per_speaker,
        "theme_counts": theme_counts,
        "evidence": {
            "hedge_utterance_ids": hedge_evidence,
            "theme_utterance_ids": theme_evidence,
        },
    }


def write_features(features: dict) -> Path:
    entity_id = features["entity_canonical_id"]
    out_dir = FEATURES_DIR / entity_id
    name = f"{features['call_date']}_{features['document_subtype']}.json"
    out_path = out_dir / name
    write_json(out_path, features)
    return out_path


def iter_transcript_dates(ticker: str):
    d = TRANSCRIPT_DIR / ticker
    if not d.exists():
        return
    for p in sorted(d.glob("*.utterances.jsonl")):
        yield p.name.replace(".utterances.jsonl", "")


def iter_press_release_stems(ticker: str):
    d = PRESS_RELEASE_DIR / ticker
    if not d.exists():
        return
    for p in sorted(d.glob("*.txt")):
        yield p.stem
