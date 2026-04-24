"""Fusion Engine (ARCHITECTURE.md component 8).

V1 iterates a sequence of heuristic detectors and concatenates their
emitted Signals. The architectural seam for learned contributions —
Basis with heuristic + learned pieces, Basis Disagreement resolution —
is preserved as an expansion point: future versions can accept learned
Detector callables alongside heuristic ones without changing this
module's contract.

Per DECISION_LOG DL-2026-015, the learned slot is empty in V1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

from signal_engine.analysis.detectors import HEURISTIC_DETECTORS
from signal_engine.analysis.detectors.base import DetectorFn
from signal_engine.domain.signal import Signal
from signal_engine.paths import TRANSCRIPT_DIR


class FusionEngine:
    """Runs registered detectors against one feature bundle + baselines.

    V1 takes only heuristic detectors. Learned detectors will attach to
    `learned_detectors` in a subsequent phase; Basis Disagreement will
    be computed when both sides produce candidates.
    """

    def __init__(
        self,
        heuristic_detectors: Sequence[DetectorFn] = HEURISTIC_DETECTORS,
        learned_detectors: Sequence[DetectorFn] = (),
        transcript_dir: Path = TRANSCRIPT_DIR,
    ) -> None:
        self.heuristic_detectors = tuple(heuristic_detectors)
        self.learned_detectors = tuple(learned_detectors)
        self.transcript_dir = transcript_dir

    def run(
        self,
        bundle: dict,
        baselines_idx: dict,
        threshold: float,
        min_observations: int,
    ) -> list[Signal]:
        signals: list[Signal] = []
        for detector in self.heuristic_detectors:
            signals.extend(detector(bundle, baselines_idx, threshold, min_observations))
        for detector in self.learned_detectors:
            signals.extend(detector(bundle, baselines_idx, threshold, min_observations))
        return [self._attach_evidence_excerpts(s) for s in signals]

    def _attach_evidence_excerpts(self, sig: Signal) -> Signal:
        """For Signals that cite Utterance IDs, load short text excerpts.

        Keeps the stored Signal self-contained so the review surface can
        render quoteable context without re-reading the transcript.
        """
        utt_ids = sig.evidence.get("utterance_ids") or []
        if not utt_ids:
            return sig
        parts = (sig.evidence.get("document_id") or "").split("_")
        if len(parts) < 3:
            return sig
        ticker = parts[0].upper()
        date = parts[1]
        utt_path = self.transcript_dir / ticker / f"{date}.utterances.jsonl"
        if not utt_path.exists():
            return sig
        by_id: dict[str, dict] = {}
        for line in utt_path.open():
            if not line.strip():
                continue
            u = json.loads(line)
            by_id[u["utterance_id"]] = u
        excerpts: list[dict] = []
        for uid in utt_ids[:5]:
            u = by_id.get(uid)
            if not u:
                continue
            text = (u.get("text") or "").strip()
            excerpts.append({
                "utterance_id": uid,
                "speaker_handle": u.get("speaker_handle"),
                "char_span": [u.get("char_start"), u.get("char_end")],
                "excerpt": text[:300] + ("…" if len(text) > 300 else ""),
            })
        sig.evidence["excerpts"] = excerpts
        return sig

    def run_over_bundles(
        self,
        bundles: Iterable[dict],
        baselines_idx: dict,
        threshold: float,
        min_observations: int,
    ) -> list[Signal]:
        all_signals: list[Signal] = []
        for bundle in bundles:
            all_signals.extend(self.run(bundle, baselines_idx, threshold, min_observations))
        return all_signals
