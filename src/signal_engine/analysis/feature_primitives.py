"""Low-level feature primitives: tokenize, count, normalize to density.

These are the shared helpers used by both transcript and press-release
feature extractors. They are deterministic and have no external state.
"""

from __future__ import annotations

import re


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def tokenize_words(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


def count_phrase_matches(text: str, phrases: list[str]) -> int:
    """Count case-insensitive, word-boundary occurrences of any phrase.

    Multi-word phrases (e.g. 'we believe') are handled — each phrase is
    escaped and wrapped with `\\b`. Returns 0 if text is empty.
    """
    if not text:
        return 0
    low = text.lower()
    total = 0
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
        total += len(re.findall(pattern, low))
    return total


def density(count: int, n_words: int) -> float:
    if n_words <= 0:
        return 0.0
    return count / n_words
