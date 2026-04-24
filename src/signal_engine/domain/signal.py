"""Signal dataclass + lifecycle states.

Honors SIGNAL_DEFINITIONS.md Signal Anatomy: Identity, Type, Subject,
Temporal Scope, Basis, Evidence, Strength, Confidence, Lifecycle State,
Lineage, Commentary.

V1 is heuristic-only per DECISION_LOG DL-2026-015. The Basis field is a
dict so the learned-side contributions and Basis Disagreement can be
added later without a schema break — the Fusion Engine architectural
seam (ARCHITECTURE.md §8) remains visible.
"""

from __future__ import annotations

from dataclasses import dataclass, field


LIFECYCLE_STATES = ("candidate", "surfaced", "stale", "superseded", "retired")


@dataclass
class Signal:
    signal_id: str
    type: str
    entity_canonical_id: str
    subject_speaker: str | None
    subject_time: str
    emission_time: str
    lifecycle_state: str
    strength: float
    confidence_label: str
    basis: dict
    evidence: dict
    commentary: str
    lineage: dict = field(
        default_factory=lambda: {"supersedes": [], "superseded_by": None}
    )
