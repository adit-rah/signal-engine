"""Press-release feature extraction.

Press releases are not speaker-attributed and have no Q&A structure, so
they produce a tighter feature bundle than transcripts. Keyed the same
way downstream: themes + document-level hedging/boosters.
"""

from __future__ import annotations

from signal_engine.analysis.feature_primitives import (
    count_phrase_matches,
    density,
    tokenize_words,
)
from signal_engine.config.themes import load_themes_for
from signal_engine.io import load_json, now_iso
from signal_engine.paths import PRESS_RELEASE_DIR, relative


def extract_press_release_features(
    ticker: str,
    stem: str,
    entity: dict,
    hedges: list[str],
    boosters: list[str],
) -> dict:
    """`stem` is the text file's stem, e.g. '2025-06-28_0001045810-25-000115'."""
    pr_dir = PRESS_RELEASE_DIR / ticker
    text_path = pr_dir / f"{stem}.txt"
    meta_path = pr_dir / f"{stem}.meta.json"
    if not text_path.exists():
        raise SystemExit(f"Missing press release text: {text_path}")
    text = text_path.read_text(encoding="utf-8")
    meta = load_json(meta_path) if meta_path.exists() else {}
    themes = load_themes_for(entity["canonical_id"])

    words = tokenize_words(text)
    n = len(words)
    h = count_phrase_matches(text, hedges)
    b = count_phrase_matches(text, boosters)
    theme_counts = {t: count_phrase_matches(text, phrases) for t, phrases in themes.items()}
    period = meta.get("period_of_report") or stem.split("_")[0]

    return {
        "document_id": f"{ticker}_{stem}_press_release",
        "entity_canonical_id": entity["canonical_id"],
        "ticker": ticker,
        "call_date": period,
        "document_subtype": "press_release",
        "source_meta_path": relative(meta_path) if meta_path.exists() else "",
        "extraction_time": now_iso(),
        "document_level": {
            "word_count": n,
            "hedge_count": h,
            "booster_count": b,
            "hedge_density": density(h, n),
            "booster_density": density(b, n),
            "certainty_score": density(b, n) - density(h, n),
        },
        "per_speaker": {},
        "theme_counts": theme_counts,
        "evidence": {
            "hedge_utterance_ids": {},
            "theme_utterance_ids": {},
        },
    }
