"""Smoke tests for feature-extraction primitives.

Uses inline synthetic text rather than on-disk fixtures so a fresh
checkout passes even when data/ is empty.
"""

from signal_engine.analysis.feature_primitives import (
    count_phrase_matches,
    density,
    tokenize_words,
)


def test_tokenize_words_lowercases_and_splits():
    assert tokenize_words("Hello, World!") == ["hello", "world"]


def test_tokenize_words_handles_empty_and_none():
    assert tokenize_words("") == []
    assert tokenize_words(None) == []


def test_count_phrase_matches_word_boundary_and_case_insensitive():
    text = "We may or may not. We believe this is MAY-driven."
    # "may" matches twice as a bare word (ignoring the hyphen compound)
    assert count_phrase_matches(text, ["may"]) == 3
    # multi-word phrase
    assert count_phrase_matches(text, ["we believe"]) == 1
    # case-insensitive
    assert count_phrase_matches(text, ["MAY"]) == 3


def test_density_safe_when_no_words():
    assert density(0, 0) == 0.0
    assert density(5, 100) == 0.05
