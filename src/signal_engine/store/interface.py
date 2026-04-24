"""Abstract Signal Store (ARCHITECTURE.md component 9).

The Signal Store holds durable, immutable Signals with their Basis,
Evidence, and lifecycle state. Lifecycle transitions are expressed as
new records with lineage references (DATA_MODEL.md Immutability).

This base class names the surface area; the filesystem implementation
is in `filesystem.py`. Downstream consumers (review surface, API
Boundary) depend on this interface rather than the concrete file format.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from signal_engine.domain.signal import Signal


class SignalStore(ABC):
    """Read + write Signals grouped by Entity."""

    @abstractmethod
    def write_signals(self, entity_id: str, signals: Iterable[Signal]) -> None: ...

    @abstractmethod
    def read_signals(self, entity_id: str) -> list[dict]: ...

    @abstractmethod
    def list_entities(self) -> list[str]: ...
