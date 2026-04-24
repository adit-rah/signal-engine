"""Filesystem-backed Signal Store.

Format: one JSONL file per entity at data/signals/<entity>.jsonl, one
Signal per line. The on-disk shape matches the legacy
bin/scripts/analysis/detect.py output exactly — this is a load-bearing
contract for the review surface and for behavioral preservation.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from signal_engine.domain.signal import Signal
from signal_engine.io import read_jsonl, write_jsonl
from signal_engine.paths import SIGNALS_DIR
from signal_engine.store.interface import SignalStore


class FilesystemSignalStore(SignalStore):
    def __init__(self, root: Path = SIGNALS_DIR) -> None:
        self.root = root

    def _path_for(self, entity_id: str) -> Path:
        return self.root / f"{entity_id}.jsonl"

    def write_signals(self, entity_id: str, signals: Iterable[Signal]) -> Path:
        path = self._path_for(entity_id)
        write_jsonl(path, (asdict(s) for s in signals))
        return path

    def read_signals(self, entity_id: str) -> list[dict]:
        return read_jsonl(self._path_for(entity_id))

    def list_entities(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.stem for p in self.root.glob("*.jsonl"))
