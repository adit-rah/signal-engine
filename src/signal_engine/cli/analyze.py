"""Run the V1 analysis pipeline end to end.

Stages: features -> baselines -> detect. Idempotent: re-running
re-extracts features, recomputes baselines, and re-emits signals.
Orchestrates via subprocess so a stage failure doesn't kill the batch.
"""

from __future__ import annotations

import argparse
import subprocess
import sys


def run(cmd: list[str], label: str) -> int:
    print(f"\n=== {label} ===")
    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print(f"  [{label}] exit {proc.returncode}")
    return proc.returncode


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", default=None, help="Restrict to one ticker for all stages.")
    p.add_argument("--threshold", type=float, default=2.0,
                   help="Signal-emission z-score threshold (default 2.0).")
    p.add_argument("--min-observations", type=int, default=4,
                   help="Minimum baseline-observation count (default 4).")
    p.add_argument("--skip-features", action="store_true")
    p.add_argument("--skip-baselines", action="store_true")
    p.add_argument("--skip-detect", action="store_true")
    args = p.parse_args()

    if not args.skip_features:
        cmd = [sys.executable, "-m", "signal_engine.cli.features", "all"]
        if args.only:
            cmd.append(args.only)
        run(cmd, "Stage 1: features")

    if not args.skip_baselines:
        cmd = [sys.executable, "-m", "signal_engine.cli.baseline",
               "--min-observations", str(args.min_observations)]
        if args.only:
            cmd.extend(["--ticker", args.only])
        run(cmd, "Stage 2: baselines")

    if not args.skip_detect:
        cmd = [sys.executable, "-m", "signal_engine.cli.detect",
               "--threshold", str(args.threshold),
               "--min-observations", str(args.min_observations)]
        if args.only:
            cmd.extend(["--ticker", args.only])
        run(cmd, "Stage 3: detect")

    print("\nPipeline complete. To browse Signals, run:")
    print("  uv run python bin/scripts/analysis/review.py")


if __name__ == "__main__":
    main()
