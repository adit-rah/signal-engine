"""Narrative Drift detector (per-theme count distribution shift).

Per SIGNAL_DEFINITIONS.md Narrative Drift: gradual change in an Entity's
framing, emphasis, or strategic communication. This heuristic detector
measures per-theme count deviation against the entity's baseline. If
any theme crosses the threshold, a composite Signal is emitted listing
every drifted theme.
"""

from __future__ import annotations

from signal_engine.analysis.baselines import baseline_excluding, z_score
from signal_engine.analysis.fusion.confidence import confidence_label
from signal_engine.domain.signal import Signal
from signal_engine.io import now_iso


def detect_narrative_drift(
    bundle: dict,
    baselines_idx: dict,
    threshold: float,
    min_observations: int,
) -> list[Signal]:
    entity_id = bundle["entity_canonical_id"]
    date = bundle.get("call_date", "")
    doc_id = bundle.get("document_id", "")
    theme_evidence = bundle.get("evidence", {}).get("theme_utterance_ids", {})
    drifts: list[dict] = []
    for theme_id, observed in (bundle.get("theme_counts") or {}).items():
        b = baselines_idx.get(("theme", theme_id, "count"))
        if not b:
            continue
        prior = baseline_excluding(b, date)
        if prior["n"] < min_observations:
            continue
        z = z_score(observed, prior["mean"], prior["stdev"])
        if abs(z) >= threshold:
            drifts.append({
                "theme": theme_id, "observed": observed,
                "baseline_mean": prior["mean"], "baseline_stdev": prior["stdev"],
                "baseline_n": prior["n"], "z_score": z,
                "evidence_utts": theme_evidence.get(theme_id, [])[:5],
            })
    if not drifts:
        return []
    max_abs_z = max(abs(d["z_score"]) for d in drifts)
    commentary_bits = "; ".join(
        f"{d['theme']} {'+' if d['z_score']>=0 else ''}{d['z_score']:.2f}σ "
        f"(observed={d['observed']}, baseline={d['baseline_mean']:.1f})"
        for d in drifts[:5]
    )
    sig = Signal(
        signal_id=f"S_{entity_id}_{date}_narrative_drift",
        type="narrative_drift",
        entity_canonical_id=entity_id,
        subject_speaker=None,
        subject_time=date,
        emission_time=now_iso(),
        lifecycle_state="candidate",
        strength=max_abs_z,
        confidence_label=confidence_label(
            max_abs_z, min(d["baseline_n"] for d in drifts),
            basis_disagreement=False, thin_history=False,
        ),
        basis={
            "rule_id": "theme_count_z_scores",
            "drifted_themes": drifts,
        },
        evidence={
            "document_id": doc_id,
            "utterance_ids": sorted({u for d in drifts for u in d["evidence_utts"]})[:10],
        },
        commentary=(
            f"Topic emphasis on {date} drifted on {len(drifts)} theme(s) vs prior baseline: "
            + commentary_bits
            + ("…" if len(drifts) > 5 else "")
        ),
    )
    return [sig]
