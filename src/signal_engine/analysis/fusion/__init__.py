"""Fusion Engine (ARCHITECTURE.md component 8; MODEL_STRATEGY.md).

Only `confidence_label` is re-exported here; `FusionEngine` is imported
lazily from `signal_engine.analysis.fusion.engine` to avoid a circular
import with the detector modules (each detector depends on
`confidence_label`).
"""

from signal_engine.analysis.fusion.confidence import confidence_label

__all__ = ["confidence_label"]
