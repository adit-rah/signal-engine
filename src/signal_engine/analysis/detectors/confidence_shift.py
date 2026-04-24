"""Confidence Shift detector (per-speaker hedge density).

Per SIGNAL_DEFINITIONS.md Confidence Shift: change in certainty,
hedging, or assertiveness. This detector compares a speaker's current
hedge_density against that speaker's prior Baseline; crossing the
threshold emits a candidate Signal.

Scope: Entity + Speaker pair (narrows Subject per SIGNAL_DEFINITIONS.md
Signal Anatomy). Unresolved speakers are skipped because a Baseline
requires a stable canonical id.
"""

from __future__ import annotations

from signal_engine.analysis.baselines import baseline_excluding, z_score
from signal_engine.analysis.fusion.confidence import confidence_label
from signal_engine.domain.signal import Signal
from signal_engine.io import now_iso


def detect_confidence_shifts(
    bundle: dict,
    baselines_idx: dict,
    threshold: float,
    min_observations: int,
) -> list[Signal]:
    out: list[Signal] = []
    entity_id = bundle["entity_canonical_id"]
    date = bundle.get("call_date", "")
    doc_id = bundle.get("document_id", "")
    for speaker_id, srec in (bundle.get("per_speaker") or {}).items():
        if speaker_id.startswith("unresolved::"):
            continue
        observed = srec.get("hedge_density", 0.0)
        b = baselines_idx.get(("speaker", speaker_id, "hedge_density"))
        if not b:
            continue
        prior = baseline_excluding(b, date)
        if prior["n"] < min_observations:
            continue
        z = z_score(observed, prior["mean"], prior["stdev"])
        if abs(z) < threshold:
            continue
        evidence_utts = (
            bundle.get("evidence", {})
            .get("hedge_utterance_ids", {})
            .get(speaker_id, [])
        )[:6]
        direction = "increased" if z > 0 else "decreased"
        sig = Signal(
            signal_id=f"S_{entity_id}_{date}_{speaker_id}_confshift",
            type="confidence_shift",
            entity_canonical_id=entity_id,
            subject_speaker=speaker_id,
            subject_time=date,
            emission_time=now_iso(),
            lifecycle_state="candidate",
            strength=abs(z),
            confidence_label=confidence_label(
                z, prior["n"], basis_disagreement=False,
                thin_history=b.get("thin_history", False),
            ),
            basis={
                "rule_id": "speaker_hedge_density_z_score",
                "observed": observed,
                "baseline_n": prior["n"],
                "baseline_mean": prior["mean"],
                "baseline_stdev": prior["stdev"],
                "z_score": z,
                "direction": direction,
            },
            evidence={
                "document_id": doc_id,
                "utterance_ids": evidence_utts,
                "speaker_canonical_id": speaker_id,
            },
            commentary=(
                f"{speaker_id}'s hedging density on {date} is {observed:.4f} "
                f"({'+' if z >= 0 else ''}{z:.2f}σ vs {prior['n']}-observation "
                f"baseline of {prior['mean']:.4f}±{prior['stdev']:.4f}). "
                f"Hedging {direction}, suggesting a shift in speaker certainty."
            ),
        )
        out.append(sig)
    return out
