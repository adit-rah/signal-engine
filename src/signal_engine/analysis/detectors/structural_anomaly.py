"""Structural Anomaly detector (transcript-shape z-scores).

Per SIGNAL_DEFINITIONS.md Structural Anomaly: unusual deviation from an
Entity's established communication structure — not content, framing,
or certainty, but the *shape* of communication. This detector evaluates
transcript-shape features (word counts, prep/Q&A balance, Q&A turn
counts) against the entity's baseline and emits a single composite
Signal capturing every simultaneous deviation.

Transcripts only. Press releases lack the structural features.
"""

from __future__ import annotations

from signal_engine.analysis.baselines import baseline_excluding, z_score
from signal_engine.analysis.fusion.confidence import confidence_label
from signal_engine.domain.signal import Signal
from signal_engine.io import now_iso


STRUCTURAL_FEATURES = [
    "qa_turn_count", "qa_avg_question_length",
    "prep_word_count", "qa_word_count", "word_count",
]


def detect_structural_anomalies(
    bundle: dict,
    baselines_idx: dict,
    threshold: float,
    min_observations: int,
) -> list[Signal]:
    if bundle.get("document_subtype") != "transcript":
        return []
    entity_id = bundle["entity_canonical_id"]
    date = bundle.get("call_date", "")
    doc_id = bundle.get("document_id", "")
    deviations: list[dict] = []
    for feat in STRUCTURAL_FEATURES:
        observed = bundle["document_level"].get(feat, 0)
        b = baselines_idx.get(("document", "transcript", feat))
        if not b:
            continue
        prior = baseline_excluding(b, date)
        if prior["n"] < min_observations:
            continue
        z = z_score(observed, prior["mean"], prior["stdev"])
        if abs(z) >= threshold:
            deviations.append({
                "feature": feat, "observed": observed,
                "baseline_mean": prior["mean"], "baseline_stdev": prior["stdev"],
                "baseline_n": prior["n"], "z_score": z,
            })
    if not deviations:
        return []
    max_abs_z = max(abs(d["z_score"]) for d in deviations)
    sig = Signal(
        signal_id=f"S_{entity_id}_{date}_structural",
        type="structural_anomaly",
        entity_canonical_id=entity_id,
        subject_speaker=None,
        subject_time=date,
        emission_time=now_iso(),
        lifecycle_state="candidate",
        strength=max_abs_z,
        confidence_label=confidence_label(
            max_abs_z, min(d["baseline_n"] for d in deviations),
            basis_disagreement=False, thin_history=False,
        ),
        basis={
            "rule_id": "transcript_shape_z_scores",
            "deviations": deviations,
        },
        evidence={
            "document_id": doc_id,
            "utterance_ids": [],
            "note": "Structural anomaly is shape-of-call, not a quoteable utterance.",
        },
        commentary=(
            f"Transcript shape on {date} departs from the historical baseline "
            f"on {len(deviations)} feature(s): "
            + ", ".join(
                f"{d['feature']} ({'+' if d['z_score']>=0 else ''}{d['z_score']:.2f}σ)"
                for d in deviations
            )
            + "."
        ),
    )
    return [sig]
