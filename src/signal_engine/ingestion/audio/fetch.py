"""Library: locate an existing downloaded-audio file.

The actual yt-dlp download is invoked from the CLI module. Exposing
`find_audio_in` here lets batch runners check for prior runs without
duplicating the glob.
"""

from __future__ import annotations

from pathlib import Path


AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".opus", ".flac", ".webm"}


def find_audio_in(dir_: Path) -> Path | None:
    candidates = [p for p in dir_.glob("source.*") if p.suffix.lower() in AUDIO_EXTS]
    return candidates[0] if candidates else None
