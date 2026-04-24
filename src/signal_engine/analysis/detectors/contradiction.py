"""Contradiction Event detector — V1 stub.

DECISION_LOG DL-2026-015: V1 is heuristic-only. Contradiction Event
detection requires semantic comparison across documents (claim
alignment + incompatibility judgment) per MODEL_STRATEGY.md
Contradiction-Alignment Model, which depends on the learned
Representation layer. Deliberately returns [] until the ML layer ships.

This module is present so the Fusion Engine's detector registry is
taxonomically complete (SIGNAL_DEFINITIONS.md taxonomy) and the seam
for the learned contribution is visible in code.
"""

from __future__ import annotations

from signal_engine.domain.signal import Signal


def detect_contradictions(
    bundle: dict,
    baselines_idx: dict,
    threshold: float = 0.0,
    min_observations: int = 0,
) -> list[Signal]:
    return []
