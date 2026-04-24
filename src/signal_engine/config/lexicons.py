"""Hedging lexicon loader."""

from __future__ import annotations

from signal_engine.io import load_json
from signal_engine.paths import CONFIG_DIR


def load_hedging_lexicon() -> tuple[list[str], list[str]]:
    """Returns (hedges, boosters). See CODE_STANDARDS.md Traceability: this
    is the input to the Confidence-Shift heuristic detector."""
    cfg = load_json(CONFIG_DIR / "hedging_lexicon.json")
    return cfg.get("hedges", []), cfg.get("boosters", [])
