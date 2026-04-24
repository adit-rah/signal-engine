"""Detector protocol shared across all heuristic detectors.

A Detector is a callable with the signature

    (bundle: dict, baselines_idx: dict,
     threshold: float, min_observations: int) -> list[Signal]

Callable functions satisfy this Protocol; the Fusion Engine does not
require a class. The Protocol exists so new detectors can be added by
writing a single function and registering it in the DETECTORS tuple.

Detectors may ignore threshold or min_observations — Omission Event,
for example, uses its own recurrence-window parameters. The extra
kwargs are forwarded only when the signature accepts them.
"""

from __future__ import annotations

from typing import Callable, Protocol

from signal_engine.domain.signal import Signal


class Detector(Protocol):
    """Callable returning a list of candidate Signals for one bundle."""

    def __call__(
        self,
        bundle: dict,
        baselines_idx: dict,
        threshold: float,
        min_observations: int,
    ) -> list[Signal]: ...


DetectorFn = Callable[..., list[Signal]]
