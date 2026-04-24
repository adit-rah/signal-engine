"""Verify config loaders return usable data.

Smoke-tests loading only; doesn't check the content of the lexicons
since those are owned by NARRATIVE_ANALYSIS.md / investigator judgment.
"""

from signal_engine.config import load_hedging_lexicon, load_themes_for, load_v1_companies
from signal_engine.domain import load_entities, load_entity_by_ticker


def test_hedging_lexicon_loads():
    hedges, boosters = load_hedging_lexicon()
    assert isinstance(hedges, list) and len(hedges) > 0
    assert isinstance(boosters, list) and len(boosters) > 0
    assert all(isinstance(h, str) for h in hedges)
    assert all(isinstance(b, str) for b in boosters)


def test_entities_registry_has_v1_tickers():
    by_ticker = load_entity_by_ticker()
    for ticker in ("NVDA", "INTC", "META"):
        assert ticker in by_ticker, f"{ticker} missing from config/entities.json"
    nvda = by_ticker["NVDA"]
    assert nvda.canonical_id == "nvda"
    assert any(s.role == "CEO" for s in nvda.speakers)


def test_themes_keyed_by_canonical_id():
    for entity in load_entities().values():
        themes = load_themes_for(entity.canonical_id)
        assert isinstance(themes, dict)
        for phrases in themes.values():
            assert isinstance(phrases, list)
            assert all(isinstance(p, str) for p in phrases)


def test_v1_companies_config_readable():
    companies = load_v1_companies()
    assert len(companies) >= 1
    assert all("ticker" in c and "ir_quarterly_url" in c for c in companies)
