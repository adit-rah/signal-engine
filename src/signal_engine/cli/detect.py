"""CLI: run the Fusion Engine over feature bundles + baselines, emit Signals."""

from __future__ import annotations

import argparse

from signal_engine.analysis.baselines import index_baselines
from signal_engine.analysis.fusion.engine import FusionEngine
from signal_engine.io import load_json
from signal_engine.paths import BASELINE_DIR, FEATURES_DIR, relative
from signal_engine.store import FilesystemSignalStore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default=None,
                        help="Single ticker (default: every entity that has features and baselines)")
    parser.add_argument("--threshold", type=float, default=2.0,
                        help="z-score threshold for emission (default: 2.0)")
    parser.add_argument("--min-observations", type=int, default=4,
                        help="Minimum prior observations to compute a baseline (default: 4)")
    args = parser.parse_args()

    if args.ticker:
        entity_ids = [args.ticker.lower()]
    else:
        if not FEATURES_DIR.exists():
            raise SystemExit("No features found. Run analysis/features.")
        entity_ids = sorted(p.name for p in FEATURES_DIR.iterdir() if p.is_dir())

    engine = FusionEngine()
    store = FilesystemSignalStore()

    grand_total = 0
    type_counts: dict[str, int] = {}
    for entity_id in entity_ids:
        baseline_path = BASELINE_DIR / f"{entity_id}.json"
        if not baseline_path.exists():
            print(f"[{entity_id}] no baselines at {baseline_path}; run analysis/baseline")
            continue
        baselines_idx = index_baselines(load_json(baseline_path))

        bundle_files = sorted((FEATURES_DIR / entity_id).glob("*.json"))
        all_sigs = []
        for bf in bundle_files:
            bundle = load_json(bf)
            sigs = engine.run(bundle, baselines_idx, args.threshold, args.min_observations)
            all_sigs.extend(sigs)
            for s in sigs:
                type_counts[s.type] = type_counts.get(s.type, 0) + 1

        out = store.write_signals(entity_id, all_sigs)
        grand_total += len(all_sigs)
        type_summary = ", ".join(
            f"{k}={sum(1 for s in all_sigs if s.type==k)}"
            for k in sorted({s.type for s in all_sigs})
        ) or "(none)"
        print(f"[{entity_id}] {len(all_sigs):4d} signals  [{type_summary}]  -> "
              f"{relative(out)}")

    print()
    print(f"Total signals across entities: {grand_total}")
    if type_counts:
        for t, c in sorted(type_counts.items(), key=lambda kv: -kv[1]):
            print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
