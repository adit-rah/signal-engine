"""Heuristic detectors.

Each detector is an independent module implementing the
`(bundle, baselines_idx, threshold, min_obs) -> list[Signal]` contract
defined in `base.py`. The `DETECTORS` registry below is what the Fusion
Engine iterates; adding a new detector means adding a module and a row
here, with no other changes needed.

Per DECISION_LOG DL-2026-015, V1 is heuristic-only; the Contradiction
Event detector is a stub that returns [] until the ML layer lands.
"""

from signal_engine.analysis.detectors.base import Detector
from signal_engine.analysis.detectors.confidence_shift import detect_confidence_shifts
from signal_engine.analysis.detectors.contradiction import detect_contradictions
from signal_engine.analysis.detectors.narrative_drift import detect_narrative_drift
from signal_engine.analysis.detectors.omission import detect_omissions
from signal_engine.analysis.detectors.structural_anomaly import (
    detect_structural_anomalies,
)


HEURISTIC_DETECTORS: tuple[Detector, ...] = (
    detect_confidence_shifts,
    detect_structural_anomalies,
    detect_narrative_drift,
    detect_omissions,
    detect_contradictions,
)

__all__ = [
    "Detector",
    "HEURISTIC_DETECTORS",
    "detect_confidence_shifts",
    "detect_structural_anomalies",
    "detect_narrative_drift",
    "detect_omissions",
    "detect_contradictions",
]
