"""Baseline Maintenance (ARCHITECTURE.md component 4).

Builds rolling per-(Entity, Speaker, feature) and per-(Entity, theme)
statistics from feature bundles. Exposes Baseline thinness as a queryable
property per SIGNAL_DEFINITIONS.md Thin-History Policy.

The Fusion Engine consumes Baselines through `index_baselines` and
`baseline_excluding` (as-of computation that excludes the current
document's observation from its own baseline).
"""

from __future__ import annotations

import statistics
from pathlib import Path

from signal_engine.io import load_json, now_iso, write_json
from signal_engine.paths import BASELINE_DIR, FEATURES_DIR


DOC_LEVEL_FEATURES = [
    "hedge_density", "booster_density", "certainty_score",
    "word_count", "prep_word_count", "qa_word_count",
    "qa_turn_count", "qa_avg_question_length",
]
SPEAKER_FEATURES = [
    "hedge_density", "booster_density", "certainty_score",
    "word_count", "turn_count",
]


def load_feature_bundles(entity_id: str) -> list[dict]:
    d = FEATURES_DIR / entity_id.lower()
    if not d.exists():
        return []
    return [load_json(p) for p in sorted(d.glob("*.json"))]


def collect_observations(
    bundles: list[dict], subtype: str | None = None
) -> dict[tuple[str, str, str, str], list[dict]]:
    """Returns {(entity_id, scope_type, scope_id, feature_key) -> [obs]}.

    scope_type is 'document', 'speaker', or 'theme'. The legacy code
    packed the document_subtype into scope_id for document-scoped
    baselines ('transcript' vs 'press_release'), preserved here.
    """
    obs: dict[tuple[str, str, str, str], list[dict]] = {}
    for b in bundles:
        if subtype and b.get("document_subtype") != subtype:
            continue
        entity_id = b["entity_canonical_id"]
        date = b.get("call_date", "")
        doc_id = b.get("document_id", "")

        doc_level = b.get("document_level", {})
        for feat in DOC_LEVEL_FEATURES:
            if feat in doc_level:
                key = (entity_id, "document", b.get("document_subtype", "?"), feat)
                obs.setdefault(key, []).append({
                    "value": doc_level[feat],
                    "date": date,
                    "document_id": doc_id,
                })

        for speaker_id, srec in (b.get("per_speaker") or {}).items():
            if speaker_id.startswith("unresolved::"):
                continue
            for feat in SPEAKER_FEATURES:
                if feat in srec:
                    key = (entity_id, "speaker", speaker_id, feat)
                    obs.setdefault(key, []).append({
                        "value": srec[feat],
                        "date": date,
                        "document_id": doc_id,
                    })

        for theme_id, count in (b.get("theme_counts") or {}).items():
            key = (entity_id, "theme", theme_id, "count")
            obs.setdefault(key, []).append({
                "value": count,
                "date": date,
                "document_id": doc_id,
                "subtype": b.get("document_subtype", "?"),
            })
    return obs


def stats_from(observations: list[dict]) -> dict:
    values = [o["value"] for o in observations]
    n = len(values)
    if n == 0:
        return {"n": 0}
    dated = [o["date"] for o in observations if o["date"]]
    return {
        "n": n,
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values) if n > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "first_date": min(dated) if dated else "",
        "last_date": max(dated) if dated else "",
    }


def build_baselines(bundles: list[dict], min_observations: int) -> dict:
    obs = collect_observations(bundles)
    baselines = []
    for (entity_id, scope_type, scope_id, feat), records in obs.items():
        st = stats_from(records)
        baselines.append({
            "entity_canonical_id": entity_id,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "feature": feat,
            "stats": st,
            "thin_history": st["n"] < min_observations,
            "observations": [
                {"value": r["value"], "date": r["date"], "document_id": r["document_id"]}
                for r in sorted(records, key=lambda r: r["date"])
            ],
        })
    return {
        "generated_at": now_iso(),
        "min_observations_threshold": min_observations,
        "baseline_count": len(baselines),
        "baselines": baselines,
    }


def index_baselines(baselines_obj: dict) -> dict:
    """Index by (scope_type, scope_id, feature) for O(1) lookup during detection."""
    return {
        (b["scope_type"], b["scope_id"], b["feature"]): b
        for b in baselines_obj.get("baselines", [])
    }


def baseline_excluding(b: dict, current_date: str) -> dict:
    """Stats over observations strictly before current_date.

    Prevents a document from being baselined against itself. Returns
    {'n': 0} if no prior observations exist.
    """
    prior = [o for o in b["observations"] if o["date"] < current_date]
    if not prior:
        return {"n": 0}
    values = [o["value"] for o in prior]
    n = len(values)
    return {
        "n": n,
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values) if n > 1 else 0.0,
        "first_date": min(o["date"] for o in prior),
        "last_date": max(o["date"] for o in prior),
    }


def z_score(observed: float, mean: float, stdev: float) -> float:
    if stdev <= 1e-12:
        return 0.0
    return (observed - mean) / stdev


def write_baselines(entity_id: str, baselines_obj: dict) -> Path:
    out_path = BASELINE_DIR / f"{entity_id}.json"
    write_json(out_path, baselines_obj)
    return out_path
