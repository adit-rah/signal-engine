"""Omission Event detector (theme recurrence-then-absence).

Per SIGNAL_DEFINITIONS.md Omission Event: disappearance of a previously
recurring theme. The unit of measurement is absence of expected
ThemeInstances, not the presence of negating language.

Thin-History Policy (SIGNAL_DEFINITIONS.md): Omission Events require a
minimum recurrence threshold in the prior history; below that threshold
the Signal is not emitted at all. V1 uses a 4-observation window and a
3-of-4 minimum.

Ignores threshold / min_observations parameters; uses its own
recurrence-window parameters instead.
"""

from __future__ import annotations

from signal_engine.domain.signal import Signal
from signal_engine.io import now_iso


def detect_omissions(
    bundle: dict,
    baselines_idx: dict,
    threshold: float = 0.0,
    min_observations: int = 0,
    min_recurrence_window: int = 4,
    min_recurrence_count: int = 3,
) -> list[Signal]:
    """Emit an Omission Signal if any theme is absent here despite prior recurrence."""
    entity_id = bundle["entity_canonical_id"]
    date = bundle.get("call_date", "")
    doc_id = bundle.get("document_id", "")
    omitted: list[dict] = []
    for theme_id, observed in (bundle.get("theme_counts") or {}).items():
        if observed > 0:
            continue
        b = baselines_idx.get(("theme", theme_id, "count"))
        if not b:
            continue
        prior = sorted(
            (o for o in b["observations"] if o["date"] < date),
            key=lambda o: o["date"],
            reverse=True,
        )[:min_recurrence_window]
        if len(prior) < min_recurrence_window:
            continue
        n_present = sum(1 for o in prior if o["value"] > 0)
        if n_present >= min_recurrence_count:
            omitted.append({
                "theme": theme_id,
                "prior_window": min_recurrence_window,
                "prior_present_count": n_present,
                "prior_dates_present": [o["date"] for o in prior if o["value"] > 0],
            })
    if not omitted:
        return []
    trailing = f" (+{len(omitted)-8} more)" if len(omitted) > 8 else ""
    sig = Signal(
        signal_id=f"S_{entity_id}_{date}_omission",
        type="omission_event",
        entity_canonical_id=entity_id,
        subject_speaker=None,
        subject_time=date,
        emission_time=now_iso(),
        lifecycle_state="candidate",
        strength=float(max(o["prior_present_count"] for o in omitted)),
        confidence_label="moderate",
        basis={
            "rule_id": "theme_recurrence_then_absence",
            "omitted_themes": omitted,
            "min_recurrence_window": min_recurrence_window,
            "min_recurrence_count": min_recurrence_count,
        },
        evidence={
            "document_id": doc_id,
            "utterance_ids": [],
            "note": "Omission Evidence is absence; cite prior-document utterances via prior_dates_present.",
        },
        commentary=(
            f"On {date}, {len(omitted)} previously-recurring theme(s) appeared zero times: "
            + ", ".join(o["theme"] for o in omitted[:8])
            + trailing
            + ". Each had prior presence in at least "
            f"{min_recurrence_count}/{min_recurrence_window} of its prior observations."
        ),
    )
    return [sig]
