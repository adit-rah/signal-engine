"""Project paths.

PROJECT_ROOT is resolved by walking up from this file until we find a
directory that contains pyproject.toml. The old bin/scripts layout
computed this with parents[N] counts; migrating to pyproject-anchored
resolution decouples the computation from directory depth.
"""

from __future__ import annotations

from pathlib import Path


def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError(
        f"Could not locate pyproject.toml walking up from {here}"
    )


PROJECT_ROOT = _find_project_root()

CONFIG_DIR = PROJECT_ROOT / "config"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
NORMALIZED_DIR = DATA_DIR / "normalized"
ANALYTICAL_DIR = DATA_DIR / "analytical"
SIGNALS_DIR = DATA_DIR / "signals"
MANIFEST_DIR = DATA_DIR / "manifests"

EDGAR_ROOT = RAW_DIR / "sec-edgar-filings"
AUDIO_RAW_ROOT = RAW_DIR / "audio"
PDF_RAW_ROOT = RAW_DIR / "transcripts_pdf"

TRANSCRIPT_DIR = NORMALIZED_DIR / "transcripts"
PRESS_RELEASE_DIR = NORMALIZED_DIR / "press_releases"
PRESS_RELEASE_INDEX = NORMALIZED_DIR / "index.jsonl"

FEATURES_DIR = ANALYTICAL_DIR / "features"
BASELINE_DIR = ANALYTICAL_DIR / "baselines"


def relative(path: Path) -> str:
    """Best-effort path-relative-to-project for human-readable logging.

    Returns the absolute path if it does not sit under PROJECT_ROOT,
    matching what the legacy scripts printed.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)
