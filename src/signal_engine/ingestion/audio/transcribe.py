"""Library: WhisperX transcribe + align + diarize.

In-house model ownership (CONTEXT.md §6): runs locally; no external
API at inference time. `transcribe` takes resolved arguments; the CLI
layer parses argparse and calls in.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from signal_engine.io import now_iso
from signal_engine.paths import AUDIO_RAW_ROOT, relative


def resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def transcribe(
    ticker: str,
    date: str,
    *,
    model: str,
    device: str,
    compute_type: str,
    language: str,
    diarize: bool,
    hf_token: str | None,
) -> Path:
    """Run WhisperX on data/raw/audio/<TICKER>/<DATE>. Returns the output path."""
    ticker = ticker.upper()
    in_dir = AUDIO_RAW_ROOT / ticker / date
    audio_candidates = sorted(
        p for p in in_dir.glob("source.*")
        if p.suffix.lower() in {".mp3", ".m4a", ".wav", ".opus", ".flac"}
    )
    if not audio_candidates:
        raise SystemExit(f"No audio found under {in_dir}. Run audio/fetch first.")
    audio_path = audio_candidates[0]
    output_path = in_dir / "whisperx_raw.json"

    print(f"Audio:       {relative(audio_path)}")
    print(f"Model:       {model}")
    print(f"Device:      {device}")
    print(f"Compute:     {compute_type}")
    print(f"Diarization: {'enabled' if diarize else 'skipped'}")
    print(f"Output:      {relative(output_path)}")
    print()

    import whisperx

    device = resolve_device(device)
    if device != "auto":
        print(f"Auto-detected device: {device}")

    t0 = time.time()

    print("Loading Whisper model...")
    model_obj = whisperx.load_model(
        model, device, compute_type=compute_type, language=language
    )
    print("Loading audio...")
    audio = whisperx.load_audio(str(audio_path))
    print("Transcribing (this may take several minutes)...")
    result = model_obj.transcribe(audio, batch_size=16)

    print("Loading alignment model...")
    model_a, metadata = whisperx.load_align_model(
        language_code=result.get("language", language), device=device
    )
    print("Aligning...")
    result = whisperx.align(
        result["segments"], model_a, metadata, audio, device, return_char_alignments=False
    )

    if diarize:
        if not hf_token:
            raise SystemExit(
                "Diarization requires a Hugging Face token. "
                "Set HF_TOKEN or pass --hf-token. Or use --no-diarize to skip."
            )
        print("Loading diarization pipeline...")
        diarize_model = whisperx.DiarizationPipeline(
            use_auth_token=hf_token, device=device
        )
        print("Diarizing speakers...")
        diarize_segments = diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_segments, result)

    clean = {
        "language": result.get("language", language),
        "segments": result["segments"],
    }
    if "word_segments" in result:
        clean["word_segments"] = result["word_segments"]

    elapsed = time.time() - t0
    envelope = {
        "ticker": ticker,
        "call_date": date,
        "audio_path": relative(audio_path),
        "whisper_model": model,
        "whisper_compute_type": compute_type,
        "device": device,
        "diarization": diarize,
        "language": clean.get("language"),
        "elapsed_seconds": round(elapsed, 1),
        "observation_time": now_iso(),
        "result": clean,
    }
    output_path.write_text(json.dumps(envelope), encoding="utf-8")

    n_segs = len(clean["segments"])
    print()
    print(f"Done. {n_segs} segments, {elapsed:.1f}s elapsed.")
    print(f"Output: {relative(output_path)}")
    return output_path
