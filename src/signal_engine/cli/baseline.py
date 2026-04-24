"""CLI: compute Baselines from per-document feature bundles."""

from __future__ import annotations

import argparse

from signal_engine.analysis.baselines import (
    build_baselines,
    load_feature_bundles,
    write_baselines,
)
from signal_engine.paths import BASELINE_DIR, FEATURES_DIR, relative


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default=None,
                        help="Single ticker (default: every v1 ticker with features on disk)")
    parser.add_argument("--min-observations", type=int, default=4,
                        help="Minimum observations for a Baseline to not be marked thin-history")
    args = parser.parse_args()

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    if args.ticker:
        entity_ids = [args.ticker.lower()]
    else:
        if not FEATURES_DIR.exists():
            raise SystemExit(
                f"No features directory at {FEATURES_DIR}. "
                f"Run analysis/features first."
            )
        entity_ids = sorted(p.name for p in FEATURES_DIR.iterdir() if p.is_dir())

    for entity_id in entity_ids:
        bundles = load_feature_bundles(entity_id)
        if not bundles:
            print(f"[{entity_id}] no feature bundles; skipping")
            continue
        out = build_baselines(bundles, args.min_observations)
        out_path = write_baselines(entity_id, out)
        n_total = out["baseline_count"]
        n_thin = sum(1 for b in out["baselines"] if b["thin_history"])
        print(f"[{entity_id}] {n_total} baselines ({n_thin} thin-history) -> "
              f"{relative(out_path)}")


if __name__ == "__main__":
    main()
