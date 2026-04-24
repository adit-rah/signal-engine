"""V1 company list loader (DECISION_LOG DL-2026-014a: NVDA, INTC, META)."""

from __future__ import annotations

from signal_engine.io import load_json
from signal_engine.paths import CONFIG_DIR


def load_v1_companies(only: list[str] | None = None) -> list[dict]:
    """Returns the list of company entries from config/v1_companies.json.

    When `only` is provided (case-insensitive tickers), filters to that
    subset and raises SystemExit if none match — legacy v1_ingest behavior.
    """
    path = CONFIG_DIR / "v1_companies.json"
    if not path.exists():
        raise SystemExit(f"Missing config: {path}")
    cfg = load_json(path)
    companies = cfg.get("companies", [])
    if only:
        only_set = {t.upper() for t in only}
        companies = [c for c in companies if c["ticker"].upper() in only_set]
        if not companies:
            raise SystemExit(f"No match in v1 config for: {only}")
    return companies
