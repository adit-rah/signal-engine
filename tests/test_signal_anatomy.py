"""Signal serialization matches SIGNAL_DEFINITIONS.md anatomy.

Checks every required Signal field is present and serializable, and
that the filesystem store round-trips.
"""

import tempfile
from dataclasses import asdict
from pathlib import Path

from signal_engine.domain.signal import LIFECYCLE_STATES, Signal
from signal_engine.store.filesystem import FilesystemSignalStore


REQUIRED_FIELDS = {
    "signal_id", "type", "entity_canonical_id", "subject_speaker",
    "subject_time", "emission_time", "lifecycle_state", "strength",
    "confidence_label", "basis", "evidence", "commentary", "lineage",
}


def _sample_signal() -> Signal:
    return Signal(
        signal_id="S_nvda_2025-05-28_test",
        type="confidence_shift",
        entity_canonical_id="nvda",
        subject_speaker="nvda_huang_jensen",
        subject_time="2025-05-28",
        emission_time="2026-04-23T12:00:00+00:00",
        lifecycle_state="candidate",
        strength=2.5,
        confidence_label="moderate",
        basis={
            "rule_id": "speaker_hedge_density_z_score",
            "z_score": 2.5,
            "baseline_n": 6,
        },
        evidence={
            "document_id": "nvda_2025-05-28_transcript",
            "utterance_ids": ["U0005", "U0008"],
        },
        commentary="Hedging density increased vs baseline.",
    )


def test_signal_has_all_required_fields():
    s = _sample_signal()
    for field in REQUIRED_FIELDS:
        assert hasattr(s, field), f"Signal missing {field}"


def test_signal_serializes_to_legacy_shape():
    s = _sample_signal()
    d = asdict(s)
    assert set(d.keys()) == REQUIRED_FIELDS
    assert d["lineage"] == {"supersedes": [], "superseded_by": None}
    assert d["lifecycle_state"] in LIFECYCLE_STATES


def test_filesystem_store_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        store = FilesystemSignalStore(root=Path(td))
        s = _sample_signal()
        out = store.write_signals("nvda", [s])
        assert out.exists()
        assert store.list_entities() == ["nvda"]
        rows = store.read_signals("nvda")
        assert len(rows) == 1
        row = rows[0]
        assert row["signal_id"] == s.signal_id
        assert row["basis"] == s.basis
        assert row["evidence"] == s.evidence


def test_basis_field_is_mutable_dict_for_future_learned_contribs():
    """MODEL_STRATEGY.md Basis Disagreement: the learned-side slot must
    be addable to Basis without a schema break. Keeping Basis as a plain
    dict preserves that extension point."""
    s = _sample_signal()
    assert isinstance(s.basis, dict)
    s.basis["learned_contribution"] = {"rule_id": "future_ml_model", "score": 0.7}
    s.basis["basis_disagreement"] = {"present": True, "kind": "direction"}
    assert "learned_contribution" in s.basis
