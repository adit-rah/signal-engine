"""CLI viewer for emitted Signals.

Reads data/signals/<ENTITY>.jsonl and renders Signals as human-readable
output — ranked, filterable, with evidence excerpts. This is the V1
stand-in for the Evaluation Harness review surface (ARCHITECTURE.md
component 12). A proper review UI is deferred to USER_EXPERIENCE.md.
"""

from __future__ import annotations

import argparse
import json

from signal_engine.store import FilesystemSignalStore


SEVERITY_BAR = {"high": "█████", "moderate": "███", "low": "█"}

TYPE_LABELS = {
    "confidence_shift": "Confidence Shift",
    "structural_anomaly": "Structural Anomaly",
    "narrative_drift": "Narrative Drift",
    "omission_event": "Omission Event",
    "contradiction_event": "Contradiction Event",
}


def load_all_signals(entity_filter: str | None) -> list[dict]:
    store = FilesystemSignalStore()
    out: list[dict] = []
    for entity_id in store.list_entities():
        if entity_filter and entity_id.lower() != entity_filter.lower():
            continue
        out.extend(store.read_signals(entity_id))
    return out


def render_signal(s: dict, verbose: bool = False) -> str:
    type_label = TYPE_LABELS.get(s["type"], s["type"])
    bar = SEVERITY_BAR.get(s["confidence_label"], "·")
    head = (
        f"[{s['confidence_label'].upper():<8}] {bar:<5} "
        f"{type_label:<22} | {s['entity_canonical_id'].upper():<5} "
        f"{s['subject_time']}  z={s['strength']:.2f}"
    )
    if s.get("subject_speaker"):
        head += f"  speaker={s['subject_speaker']}"
    lines = [head, f"  {s['commentary']}"]

    if verbose:
        basis = s.get("basis", {})
        lines.append(f"  basis: {basis.get('rule_id')}")
        for k in ("observed", "baseline_n", "baseline_mean", "baseline_stdev",
                  "z_score", "direction"):
            if k in basis:
                v = basis[k]
                if isinstance(v, float):
                    v = f"{v:.4f}"
                lines.append(f"    {k}: {v}")
        excerpts = s.get("evidence", {}).get("excerpts", [])
        for ex in excerpts[:3]:
            speaker = ex.get("speaker_handle") or "?"
            lines.append(f"  ↳ [{speaker}] {ex.get('excerpt', '')}")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entity", default=None, help="Filter to one entity (e.g. nvda)")
    p.add_argument("--type", default=None, help="Filter to one signal type")
    p.add_argument("--min-strength", type=float, default=0.0,
                   help="Minimum |z| / strength to display")
    p.add_argument("--since", default=None,
                   help="Only show signals with subject_time >= this date")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--verbose", action="store_true",
                   help="Show basis details and evidence excerpts")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON one per line, no pretty render")
    args = p.parse_args()

    signals = load_all_signals(args.entity)
    if args.type:
        signals = [s for s in signals if s["type"] == args.type]
    if args.since:
        signals = [s for s in signals if s.get("subject_time", "") >= args.since]
    signals = [s for s in signals if s["strength"] >= args.min_strength]

    severity_rank = {"high": 0, "moderate": 1, "low": 2}
    signals.sort(key=lambda s: (
        severity_rank.get(s["confidence_label"], 99),
        -s["strength"],
        s.get("subject_time", ""),
    ))
    signals = signals[:args.limit]

    if args.json:
        for s in signals:
            print(json.dumps(s))
        return

    if not signals:
        print("No signals match those filters.")
        return

    print(f"Showing {len(signals)} signal(s):\n")
    for i, s in enumerate(signals, start=1):
        print(render_signal(s, verbose=args.verbose))
        if i < len(signals):
            print()


if __name__ == "__main__":
    main()
