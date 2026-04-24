"""CLI: download earnings call audio via yt-dlp."""

from __future__ import annotations

import argparse
import json
import subprocess

from signal_engine.ingestion.audio.fetch import find_audio_in
from signal_engine.io import now_iso, sha256_file
from signal_engine.paths import AUDIO_RAW_ROOT, PROJECT_ROOT, relative


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", help="Uppercase ticker symbol, e.g. NVDA")
    parser.add_argument("date", help="Earnings call date, YYYY-MM-DD")
    parser.add_argument("url", help="Webcast URL, event page, or direct media URL")
    parser.add_argument("--title", default="", help="Optional title, e.g. 'Q1 FY26'")
    parser.add_argument("--format", default="mp3", help="Audio format (default: mp3)")
    parser.add_argument("--debug", action="store_true", help="Verbose yt-dlp output")
    parser.add_argument("--overwrite", action="store_true", help="Re-download even if audio exists")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    out_dir = AUDIO_RAW_ROOT / ticker / args.date
    out_dir.mkdir(parents=True, exist_ok=True)

    existing = find_audio_in(out_dir)
    if existing and not args.overwrite:
        print(f"Audio already exists: {relative(existing)}")
        print("Use --overwrite to re-download.")
        return

    print(f"Ticker: {ticker}")
    print(f"Date:   {args.date}")
    print(f"URL:    {args.url}")
    print(f"Output: {out_dir.relative_to(PROJECT_ROOT)}")
    print()

    cmd = [
        "yt-dlp", "-x",
        "--audio-format", args.format,
        "-o", str(out_dir / "source.%(ext)s"),
    ]
    if args.debug:
        cmd.append("--verbose")
    else:
        cmd.extend(["--no-warnings"])
    cmd.append(args.url)

    print("Running:", " ".join(cmd))
    print()
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print()
        print("-" * 60)
        print("yt-dlp could not extract audio from this URL.")
        print("Try:")
        print("  1. Re-run with --debug to see the full yt-dlp error output.")
        print("  2. Open the page in Chrome, DevTools -> Network, filter for")
        print("     'mp3' or 'm3u8'. Start the audio, grab the stream URL")
        print("     that appears, and pass that URL to this script.")
        print("  3. If the page uses JavaScript to load the player, you may")
        print("     need to click 'Listen' first, then capture the resulting")
        print("     stream URL.")
        raise SystemExit(result.returncode)

    audio_path = find_audio_in(out_dir)
    if not audio_path:
        raise SystemExit(
            f"yt-dlp reported success but no audio file landed under {out_dir}"
        )

    meta = {
        "ticker": ticker,
        "call_date": args.date,
        "title": args.title,
        "source_url": args.url,
        "audio_path": relative(audio_path),
        "audio_format": audio_path.suffix.lstrip("."),
        "audio_sha256": sha256_file(audio_path),
        "audio_bytes": audio_path.stat().st_size,
        "fetched_with": "yt-dlp",
        "observation_time": now_iso(),
        "licensing_posture": "training_compatible",
        "licensing_rationale": (
            "Direct capture of publicly broadcast earnings call. Transcript "
            "derived from this capture is the project's own work product."
        ),
    }
    (out_dir / "source.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print()
    print(f"Audio: {relative(audio_path)} ({meta['audio_bytes']:,} bytes)")
    print(f"Meta:  {relative(out_dir / 'source.meta.json')}")


if __name__ == "__main__":
    main()
