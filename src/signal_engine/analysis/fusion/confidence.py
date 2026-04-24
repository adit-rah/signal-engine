"""Signal Confidence labelling.

Per SIGNAL_DEFINITIONS.md Confidence And Uncertainty At The Signal Level:
Confidence is distinct from Strength. Inputs are epistemic (Baseline
thinness, Basis disagreement, Evidence breadth) — not magnitude of
deviation.

Honors the False-Positive Posture (DECISION_LOG DL-2026-008) by leaning
conservative: thin baselines or Basis disagreement drop to 'low'.
"""

from __future__ import annotations


def confidence_label(
    z_score: float,
    baseline_n: int,
    basis_disagreement: bool,
    thin_history: bool,
) -> str:
    """Returns 'low', 'moderate', or 'high'.

    Thresholds match the legacy bin/scripts/analysis/detect.py: |z| >= 3
    and n >= 8 is 'high'; |z| >= 2 with a non-thin baseline is 'moderate';
    everything else defaults to 'low'.
    """
    if thin_history or baseline_n < 4:
        return "low"
    if basis_disagreement:
        return "low"
    if abs(z_score) >= 3.0 and baseline_n >= 8:
        return "high"
    if abs(z_score) >= 2.0:
        return "moderate"
    return "low"
