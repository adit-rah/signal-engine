# src/signal_engine

The Signal Engine package. Installable via `uv pip install -e .` from
the repo root. The legacy `bin/scripts/` paths are now thin shims over
`signal_engine.cli.*`.

Per DECISION_LOG DL-2026-015, V1 is heuristic-only. The Fusion Engine's
contract accepts both heuristic and learned contributions; the learned
slot is empty until MODEL_STRATEGY.md is implemented.

---

## Layout

```
signal_engine/
├── paths.py                        project paths (resolved via pyproject.toml)
├── io.py                           shared JSON/JSONL + SHA-256 + UA + ISO stamp
├── domain/                         DATA_MODEL.md entities (dataclasses + loaders)
│   ├── entity.py                   Entity, Speaker, load_entities, resolve_speaker_handle
│   └── signal.py                   Signal dataclass + lifecycle states
├── config/                         config-file loaders
│   ├── lexicons.py                 load_hedging_lexicon
│   ├── themes.py                   load_themes_for / load_all_themes
│   └── companies.py                load_v1_companies
├── ingestion/                      ARCHITECTURE.md component 1
│   ├── edgar/
│   │   ├── sgml.py                 SEC header parsing + HTML stripping + exhibit extraction
│   │   ├── fetch.py                download 8-K filings (sec-edgar-downloader wrapper)
│   │   └── press_releases.py       EX-99.1 extraction + per-filing meta
│   ├── pdf/
│   │   ├── discover_patterns.py    earnings-transcript URL regex + date parsing
│   │   ├── discover.py             Playwright scrape + filter
│   │   ├── url_probing.py          historical URL template inference + HEAD probe
│   │   ├── manifest.py             manifest helpers (read_earnings_dates, reconcile_dates_from_sec)
│   │   ├── fetch.py                pymupdf text extraction
│   │   ├── factset_patterns.py     FactSet transcript regex + line filters
│   │   ├── factset.py              block-level FactSet parsing → utterances
│   │   ├── normalize.py            whitespace normalization + utterance enrichment
│   │   └── batch.py                step-tracking dataclass + idempotency checks
│   └── audio/
│       ├── patterns.py             EARNINGS_LINK_RE, MEDIA_URL_RE, QA_START_RE, MONTHS
│       ├── http.py                 plain-HTTP fetch (requests)
│       ├── browser.py              Playwright-based fetch (Cloudflare)
│       ├── wayback.py              Wayback CDX snapshot lookup
│       ├── discover.py             webcast discovery orchestration
│       ├── fetch.py                audio-file discovery helpers
│       ├── transcribe.py           WhisperX transcribe + align + diarize
│       ├── normalize.py            ASR → Transcript (coalesce, segment, build text)
│       └── batch.py                batch helpers (date parse, idempotency, run-log)
├── analysis/                       ARCHITECTURE.md components 5, 4, 8 (partial)
│   ├── feature_primitives.py       tokenize_words, count_phrase_matches, density
│   ├── features.py                 transcript feature extraction + iteration + write
│   ├── press_release_features.py   press-release feature extraction
│   ├── baselines.py                Baseline Maintenance (build, index, as-of, stats, z_score)
│   ├── detectors/                  heuristic detectors
│   │   ├── base.py                 Detector Protocol
│   │   ├── confidence_shift.py     per-speaker hedge_density z-score
│   │   ├── structural_anomaly.py   transcript-shape z-scores
│   │   ├── narrative_drift.py     per-theme count z-scores
│   │   ├── omission.py             theme recurrence-then-absence
│   │   └── contradiction.py        V1 stub (requires ML layer)
│   └── fusion/                     Fusion Engine (ARCHITECTURE.md component 8)
│       ├── confidence.py           confidence_label (Baseline thinness + Basis disagreement)
│       └── engine.py               FusionEngine — runs detectors, attaches evidence excerpts
├── store/                          ARCHITECTURE.md component 9
│   ├── interface.py                SignalStore ABC
│   └── filesystem.py               JSONL-per-entity concrete implementation
└── cli/                            command-line entry points
    ├── v1_ingest.py                top-level ingestion orchestrator
    ├── analyze.py                  analysis pipeline orchestrator
    ├── review.py                   Signal review surface
    ├── features.py | baseline.py | detect.py        per-stage CLIs
    ├── edgar_fetch.py | edgar_press_releases.py
    ├── pdf_discover.py | pdf_manifest.py | pdf_fetch.py | pdf_normalize.py | pdf_batch.py
    └── audio_discover.py | audio_fetch.py | audio_transcribe.py | audio_normalize.py | audio_batch.py
```

---

## Module boundaries

Each module does one of: load config, transform data, persist results,
parse CLI args. Argparse is confined to `cli/`. Library modules do not
import `argparse`.

Every module is under 200 lines. The detector registry in
`analysis/detectors/__init__.py` keeps the Fusion Engine free of any
detector-specific imports — adding a new detector means adding a module
and a row.

---

## Architectural seams preserved

Per ARCHITECTURE.md the Fusion Engine is a single named component with
a load-bearing upstream/downstream contract. The V1 implementation
honors this shape:

* `FusionEngine(heuristic_detectors=..., learned_detectors=...)` —
  learned side stays an empty tuple in V1 per DECISION_LOG DL-2026-015
* `Basis` is a `dict` that accepts arbitrary keys — the learned-side
  contributions and `basis_disagreement` will attach here without a
  schema break
* `SignalStore` is an abstract interface — the filesystem-backed
  implementation can be replaced without touching the Fusion Engine
  or the review surface

---

## Invoking the package

Three equivalent entry paths, listed in order of ergonomics:

```bash
# Installed entry points (pyproject.toml [project.scripts])
signal-engine-ingest
signal-engine-analyze
signal-engine-review

# Module invocation
uv run python -m signal_engine.cli.v1_ingest
uv run python -m signal_engine.cli.analyze
uv run python -m signal_engine.cli.review

# Legacy shim paths (still supported)
uv run python bin/scripts/v1_ingest.py
uv run python bin/scripts/analysis/pipeline.py
uv run python bin/scripts/analysis/review.py
```

See `bin/scripts/README.md` for the full pipeline walkthrough and
per-stage invocations.

---

## Extension points

The three axes from ARCHITECTURE.md (Extensibility):

* **new Document types** — add a parser + normalization under
  `ingestion/<subtype>/` and a subtype-aware branch in `cli/features.py`
* **new Signal types** — add a module under `analysis/detectors/` that
  implements the Detector Protocol from `detectors/base.py` and add it
  to `HEURISTIC_DETECTORS` in `detectors/__init__.py` (or to a new
  `LEARNED_DETECTORS` sequence when the ML layer ships). The Fusion
  Engine requires no change.
* **new analytical modules** — attach as detectors above, or as new
  components that produce Basis contributions consumed by the Fusion
  Engine

---

## Relationship to the design documents

* `.claude/docs/CONTEXT.md` — conceptual foundation; authoritative
* `.claude/docs/ARCHITECTURE.md` — components realized here: Ingestion
  (1), Document Processing (2, partial), Entity Resolution (3, partial),
  Baseline Maintenance (4), Heuristic Analysis (5), Fusion Engine (8,
  heuristic-only in V1), Signal Store (9), Ranking & Surfacing (10,
  minimal — the `review` CLI)
* `.claude/docs/DATA_MODEL.md` — entities materialized in `domain/`
* `.claude/docs/SIGNAL_DEFINITIONS.md` — Signal Anatomy lives in
  `domain/signal.py`; each type has a detector in
  `analysis/detectors/`
* `.claude/docs/MODEL_STRATEGY.md` — the learned layer is deferred per
  DL-2026-015; the Fusion Engine's contract accepts it when ready
* `.claude/docs/CODE_STANDARDS.md` — vocabulary, traceability,
  immutability, and component-boundary rules honored
