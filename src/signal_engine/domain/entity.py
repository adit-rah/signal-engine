"""Entity + Speaker registry (DATA_MODEL.md Entity, Speaker).

Loads from config/entities.json. The registry is the canonical source
for Entity identity and Speaker identity reconciliation. Native names
(e.g. 'Jen Hsun Huang') are reconciled to canonical ids (e.g.
'nvda_huang_jensen') via name_variants.

V1 treats entities as a small hand-curated list. Automated reconciliation
(DATA_MODEL.md Identity Model) is a future concern; the shape exposed
here is forward-compatible with it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from signal_engine.io import load_json
from signal_engine.paths import CONFIG_DIR


@dataclass(frozen=True)
class Speaker:
    canonical_id: str
    role: str
    name_variants: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, d: dict) -> "Speaker":
        return cls(
            canonical_id=d["canonical_id"],
            role=d.get("role", ""),
            name_variants=tuple(d.get("name_variants", [])),
        )


@dataclass(frozen=True)
class Entity:
    canonical_id: str
    ticker: str
    name: str
    cik: str
    fiscal_year_end_month: int
    speakers: tuple[Speaker, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, d: dict) -> "Entity":
        return cls(
            canonical_id=d["canonical_id"],
            ticker=d["ticker"],
            name=d.get("name", ""),
            cik=d.get("cik", ""),
            fiscal_year_end_month=d.get("fiscal_year_end_month", 12),
            speakers=tuple(Speaker.from_dict(s) for s in d.get("speakers", [])),
        )

    def speakers_as_dicts(self) -> list[dict]:
        """Dict form matches the legacy shape used by features.extract_*."""
        return [
            {
                "canonical_id": s.canonical_id,
                "role": s.role,
                "name_variants": list(s.name_variants),
            }
            for s in self.speakers
        ]


def load_entities() -> dict[str, Entity]:
    """Returns a map of canonical_id -> Entity."""
    cfg = load_json(CONFIG_DIR / "entities.json")
    return {e["canonical_id"]: Entity.from_dict(e) for e in cfg.get("entities", [])}


def load_entity_by_ticker() -> dict[str, Entity]:
    return {e.ticker: e for e in load_entities().values()}


def resolve_speaker_handle_to_canonical(
    handle: str, speakers: Iterable[dict | Speaker]
) -> str | None:
    """Map a within-document handle (e.g. 'Jen Hsun Huang') to a canonical
    id (e.g. 'nvda_huang_jensen'). Returns None if no variant matches.

    Accepts either the dict form (legacy) or Speaker objects so callers
    on both sides of the migration can use it.
    """
    if not handle:
        return None
    h = handle.strip().lower()
    for sp in speakers:
        if isinstance(sp, Speaker):
            variants = sp.name_variants
            canonical = sp.canonical_id
        else:
            variants = sp.get("name_variants", [])
            canonical = sp["canonical_id"]
        for variant in variants:
            if variant.lower() == h:
                return canonical
    return None
