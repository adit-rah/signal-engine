"""Smoke tests for each detector against a synthetic baseline.

Builds inline bundles + baselines so no on-disk data is required.
Goal: prove the detector contract + emission shape is preserved, not
that the detectors are "correct" — that is a separate analytical
concern.
"""

from signal_engine.analysis.detectors import (
    detect_confidence_shifts,
    detect_contradictions,
    detect_narrative_drift,
    detect_omissions,
    detect_structural_anomalies,
)


def _baseline(scope_type, scope_id, feature, observations):
    """Helper: build a baseline row in the shape detectors expect."""
    return {
        "scope_type": scope_type,
        "scope_id": scope_id,
        "feature": feature,
        "thin_history": False,
        "observations": [
            {"value": v, "date": d, "document_id": f"doc_{d}"}
            for v, d in observations
        ],
    }


def _idx(baselines):
    return {(b["scope_type"], b["scope_id"], b["feature"]): b for b in baselines}


def test_confidence_shift_fires_on_large_deviation():
    baselines = [_baseline(
        "speaker", "nvda_huang_jensen", "hedge_density",
        [(0.01, "2023-01-01"), (0.012, "2023-04-01"),
         (0.011, "2023-07-01"), (0.01, "2023-10-01"), (0.013, "2024-01-01")],
    )]
    bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_2024-04-01_transcript",
        "per_speaker": {
            "nvda_huang_jensen": {"hedge_density": 0.08, "name_variant_seen": "Jensen Huang"},
        },
        "evidence": {"hedge_utterance_ids": {"nvda_huang_jensen": ["U0001"]}},
    }
    sigs = detect_confidence_shifts(bundle, _idx(baselines), threshold=2.0, min_observations=4)
    assert len(sigs) == 1
    s = sigs[0]
    assert s.type == "confidence_shift"
    assert s.subject_speaker == "nvda_huang_jensen"
    assert s.basis["rule_id"] == "speaker_hedge_density_z_score"
    assert s.basis["direction"] == "increased"
    assert s.evidence["document_id"] == "nvda_2024-04-01_transcript"


def test_confidence_shift_skips_when_below_threshold():
    baselines = [_baseline(
        "speaker", "nvda_huang_jensen", "hedge_density",
        [(0.01, "2023-01-01"), (0.012, "2023-04-01"),
         (0.011, "2023-07-01"), (0.01, "2023-10-01"), (0.013, "2024-01-01")],
    )]
    bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_2024-04-01_transcript",
        "per_speaker": {
            "nvda_huang_jensen": {"hedge_density": 0.0115, "name_variant_seen": "Jensen Huang"},
        },
        "evidence": {"hedge_utterance_ids": {}},
    }
    sigs = detect_confidence_shifts(bundle, _idx(baselines), threshold=2.0, min_observations=4)
    assert sigs == []


def test_structural_anomaly_only_for_transcripts():
    baselines = [_baseline(
        "document", "transcript", "qa_turn_count",
        [(20, "2023-01-01"), (22, "2023-04-01"),
         (21, "2023-07-01"), (20, "2023-10-01"), (22, "2024-01-01")],
    )]
    pr_bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_pr",
        "document_subtype": "press_release",
        "document_level": {"qa_turn_count": 99},
    }
    assert detect_structural_anomalies(pr_bundle, _idx(baselines), 2.0, 4) == []

    tx_bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_tx",
        "document_subtype": "transcript",
        "document_level": {"qa_turn_count": 99, "word_count": 0,
                           "prep_word_count": 0, "qa_word_count": 0,
                           "qa_avg_question_length": 0},
    }
    sigs = detect_structural_anomalies(tx_bundle, _idx(baselines), 2.0, 4)
    assert len(sigs) == 1
    assert sigs[0].type == "structural_anomaly"
    assert sigs[0].basis["rule_id"] == "transcript_shape_z_scores"


def test_narrative_drift_on_theme_spike():
    baselines = [_baseline(
        "theme", "blackwell", "count",
        [(2, "2023-01-01"), (3, "2023-04-01"),
         (2, "2023-07-01"), (3, "2023-10-01"), (2, "2024-01-01")],
    )]
    bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_tx",
        "theme_counts": {"blackwell": 40},
        "evidence": {"theme_utterance_ids": {"blackwell": ["U0001"]}},
    }
    sigs = detect_narrative_drift(bundle, _idx(baselines), 2.0, 4)
    assert len(sigs) == 1
    assert sigs[0].type == "narrative_drift"
    assert any(d["theme"] == "blackwell" for d in sigs[0].basis["drifted_themes"])


def test_omission_fires_on_recurring_then_absent():
    baselines = [_baseline(
        "theme", "blackwell", "count",
        [(5, "2023-01-01"), (6, "2023-04-01"),
         (4, "2023-07-01"), (5, "2023-10-01")],
    )]
    bundle = {
        "entity_canonical_id": "nvda",
        "call_date": "2024-04-01",
        "document_id": "nvda_tx",
        "theme_counts": {"blackwell": 0},
    }
    sigs = detect_omissions(bundle, _idx(baselines))
    assert len(sigs) == 1
    assert sigs[0].type == "omission_event"
    assert sigs[0].confidence_label == "moderate"


def test_contradiction_is_a_noop_stub():
    """DECISION_LOG DL-2026-015: heuristic-only V1; contradiction is ML."""
    assert detect_contradictions({}, {}) == []
