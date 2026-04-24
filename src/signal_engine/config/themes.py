"""Per-entity theme loader."""

from __future__ import annotations

from signal_engine.io import load_json
from signal_engine.paths import CONFIG_DIR


def load_themes_for(entity_canonical_id: str) -> dict[str, list[str]]:
    """Returns {theme_id: [surface_forms]} for the given entity.

    Empty dict if the entity has no theme config. Themes are per-entity
    by design (DATA_MODEL.md Theme) since surface vocabulary varies by
    sector and strategy.
    """
    cfg = load_json(CONFIG_DIR / "themes.json")
    return cfg.get("entities", {}).get(entity_canonical_id, {}).get("themes", {})


def load_all_themes() -> dict[str, dict[str, list[str]]]:
    """Returns {entity_canonical_id: {theme_id: [surface_forms]}}."""
    cfg = load_json(CONFIG_DIR / "themes.json")
    return {
        entity_id: entry.get("themes", {})
        for entity_id, entry in cfg.get("entities", {}).items()
    }
