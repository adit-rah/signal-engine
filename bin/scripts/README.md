# bin/scripts

Shims for the Signal Engine, organized by pipeline.

Each file is a thin one-line wrapper over
`signal_engine.cli.*:main`. The actual business logic lives in
`src/signal_engine/`. Every legacy `uv run python bin/scripts/...`
invocation documented here continues to work.

Three pipelines produce Raw and Normalized layer artifacts as defined
in `.claude/docs/DATA_MODEL.md` and processed as described in
`.claude/docs/DOCUMENT_PROCESSING.md`. All scripts are ticker- and
date-parameterized and make no ticker-specific assumptions in their
logic.

---

## Directory layout

```
bin/scripts/
├── README.md                       (this file)
├── v1_ingest.py                    (ingestion orchestrator; reads config/v1_companies.json)
├── edgar/                          # Pipeline A — SEC filings
│   ├── fetch.py                    download 8-K filings
│   └── extract_press_releases.py   extract EX-99.1 press releases
├── audio/                          # Pipeline B — IR webcasts + ASR
│   ├── discover.py                 scrape IR page for webcast event URLs
│   ├── fetch.py                    download webcast audio via yt-dlp
│   ├── transcribe.py               run WhisperX ASR + diarization
│   ├── normalize.py                turn ASR output into structured Transcript
│   └── batch.py                    orchestrate fetch → transcribe → normalize
├── pdf/                            # Pipeline C — issuer-published PDF transcripts
│   ├── discover.py                 scrape IR page for transcript PDFs (Playwright)
│   ├── build_manifest.py           scrape + historical URL probing
│   ├── fetch.py                    download PDF + extract text via pymupdf
│   ├── normalize.py                parse FactSet-format transcript into Utterances
│   └── batch.py                    orchestrate fetch → normalize
└── analysis/                       # V1 analysis layer (heuristic Fusion Engine)
    ├── features.py                 extract per-document features (hedging, themes, shape)
    ├── baseline.py                 compute per-(entity, speaker, feature) Baselines
    ├── detect.py                   Fusion Engine v0 — emit Signals from feature-vs-baseline z-scores
    ├── pipeline.py                 orchestrate features → baselines → detect
    └── review.py                   CLI viewer for emitted Signals
```

Supporting files live under:

- `config/v1_companies.json` — the v1 target company list (DL-2026-014a)
- `config/entities.json` — canonical Entity + Speaker registry
- `config/hedging_lexicon.json` — hedge / booster word lists for Confidence Shift
- `config/themes.json` — per-entity theme keywords for Narrative Drift / Omission
- `data/raw/sec-edgar-filings/<TICKER>/8-K/` — raw SEC filings
- `data/raw/transcripts_pdf/<TICKER>/<DATE>/` — raw PDFs and extracted text
- `data/raw/audio/<TICKER>/<DATE>/` — raw webcast audio and WhisperX output
- `data/normalized/press_releases/<TICKER>/` — Normalized press-release Documents
- `data/normalized/transcripts/<TICKER>/` — Normalized Transcript Documents
- `data/analytical/features/<ENTITY>/` — per-Document feature bundles
- `data/analytical/baselines/<ENTITY>.json` — rolling Baselines per (Entity, Speaker, feature)
- `data/signals/<ENTITY>.jsonl` — emitted Signals
- `data/manifests/<TICKER>_*.jsonl` — discovered / probed URL manifests
- `data/manifests/<TICKER>_*_pipeline_runs.jsonl` — batch run logs

---

## Where the code lives

The library code lives in `src/signal_engine/`. Files in this directory
are one-line shims that import `main` from the corresponding
`signal_engine.cli.*` module. See `src/signal_engine/README.md` for the
package layout. Install with `uv pip install -e .`.

The same commands can be invoked three ways:

```bash
# 1. Legacy shim path (this directory)
uv run python bin/scripts/analysis/pipeline.py

# 2. Module invocation
uv run python -m signal_engine.cli.analyze

# 3. Installed console entry point (pyproject.toml [project.scripts])
signal-engine-analyze
```

---

## Which pipeline for which document subtype

| Subtype | Pipeline | Rationale |
|---|---|---|
| Press Release | A (edgar) | SEC EDGAR, public domain, trivially clean. |
| Transcript (company publishes PDF) | C (pdf) | Strictly better than ASR: clean, authoritative, fast. |
| Transcript (no PDF available) | B (audio) | Fallback via yt-dlp + WhisperX. Higher effort. |

NVIDIA and many other Q4 Inc.-hosted IR sites publish PDF transcripts.
Most companies overall do not. For v1 we deliberately chose only
companies that do (see DECISION_LOG DL-2026-014).

---

## The v1 workflow (the normal way to run things)

Single command brings the v1 corpus up to date. Idempotent.

```bash
uv run python bin/scripts/v1_ingest.py
```

What it does, per ticker in `config/v1_companies.json`:

1. `edgar/fetch.py` — pull 8-K filings (for call dates + press releases)
2. `edgar/extract_press_releases.py` — extract press-release Documents
3. `pdf/build_manifest.py` — scrape live IR page + probe historical URLs using SEC 8-K call dates
4. `pdf/batch.py` — fetch + normalize every transcript in the manifest

Variations:

```bash
# Just one ticker
uv run python bin/scripts/v1_ingest.py --only NVDA

# Just one stage across all tickers
uv run python bin/scripts/v1_ingest.py --stage discover

# Smoke test: first N transcripts only
uv run python bin/scripts/v1_ingest.py --limit 2
```

At the end it prints a summary table: filings pulled, press releases
extracted, transcript PDFs in manifest, and normalized Transcripts per
ticker.

---

## Manual / individual-stage invocations

When debugging or running ad-hoc.

### Pipeline A — SEC filings

```bash
uv run python bin/scripts/edgar/fetch.py NVDA MSFT --after 2019-01-01
uv run python bin/scripts/edgar/extract_press_releases.py
```

### Pipeline C — PDF transcripts

```bash
# Discover + probe historical
uv run python bin/scripts/pdf/build_manifest.py NVDA \
    https://investor.nvidia.com/financial-info/quarterly-results/default.aspx

# Fetch + normalize one call
uv run python bin/scripts/pdf/fetch.py NVDA 2025-05-28 "<pdf_url>"
uv run python bin/scripts/pdf/normalize.py NVDA 2025-05-28

# Batch everything in the manifest
uv run python bin/scripts/pdf/batch.py data/manifests/NVDA_transcript_pdfs.jsonl
```

### Pipeline B — audio + ASR

```bash
# Discover webcast URLs (real browser required for Cloudflare)
uv run python bin/scripts/audio/discover.py NVDA "<ir_url>" --browser --wayback

# Fetch + transcribe + normalize one call
uv run python bin/scripts/audio/fetch.py NVDA 2025-05-28 "<webcast_url>"
uv run python bin/scripts/audio/transcribe.py NVDA 2025-05-28
uv run python bin/scripts/audio/normalize.py NVDA 2025-05-28

# Batch
uv run python bin/scripts/audio/batch.py data/manifests/NVDA_earnings_calls.jsonl
```

---

## Provenance and the Raw / Normalized boundary

Every stage writes a sidecar `*.meta.json` recording the source URL,
SHA-256, timestamps, tool versions, and Licensing Posture. This is the
per-artifact provenance chain supporting the traceability invariant in
`.claude/docs/CONTEXT.md` §3.3.

Raw artifacts (SEC filings, MP3s, ASR JSON, PDFs) are immutable once
written. Re-running ingestion for an existing key skips by default where
applicable; re-running extraction / transcription / normalization is
always safe and produces fresh output.

The Normalized Transcript output schema is identical whether the source
was audio-ASR (Pipeline B) or issuer-PDF (Pipeline C). Only the
`source_origin` field in the meta distinguishes them.

---

## V1 analysis: end-to-end run

After ingestion has produced Normalized Documents, run the analysis
pipeline to emit Signals.

```bash
# Single command: features -> baselines -> detect
uv run python bin/scripts/analysis/pipeline.py

# Browse what came out
uv run python bin/scripts/analysis/review.py --verbose
```

Common review-time filters:

```bash
# Only NVDA, only confidence shifts, sorted by strength
uv run python bin/scripts/analysis/review.py --entity nvda --type confidence_shift

# Only signals strong enough to merit attention (z >= 2.5)
uv run python bin/scripts/analysis/review.py --min-strength 2.5

# Only recent ones
uv run python bin/scripts/analysis/review.py --since 2024-01-01 --verbose
```

Tune the detector (defaults: z>=2.0, min 4 prior observations):

```bash
# More aggressive — emits more Signals, including weaker ones
uv run python bin/scripts/analysis/pipeline.py --threshold 1.5

# Less aggressive — only very strong deviations
uv run python bin/scripts/analysis/pipeline.py --threshold 3.0 --min-observations 6
```

V1 Signal types implemented:

| Type | Detector module | Notes |
|------|------------------|-------|
| Confidence Shift | `signal_engine.analysis.detectors.confidence_shift` | Per-speaker hedge-density z-score |
| Structural Anomaly | `signal_engine.analysis.detectors.structural_anomaly` | Transcript-shape z-scores (qa_turn_count, prep/qa balance, etc.) |
| Narrative Drift | `signal_engine.analysis.detectors.narrative_drift` | Per-theme count z-scores |
| Omission Event | `signal_engine.analysis.detectors.omission` | Theme present in ≥3 of last 4 obs and absent here |
| Contradiction Event | `signal_engine.analysis.detectors.contradiction` (stub) | Requires the ML/learned representation layer; not in V1 |

---

## Dependencies

Installed via `uv`:

- `sec-edgar-downloader` — Pipeline A fetch
- `beautifulsoup4`, `requests` — HTML parsing (everywhere)
- `playwright` + `playwright install chromium` — Pipeline B and C discovery (Cloudflare-protected sites)
- `yt-dlp` — Pipeline B audio download
- `whisperx` (+ `HF_TOKEN` env for pyannote diarization) — Pipeline B transcription
- `pymupdf` — Pipeline C PDF text extraction

See `pyproject.toml` for pinned versions.
