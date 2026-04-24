# MIGRATION_NOTES.md

Record of the `bin/scripts/` → `src/signal_engine/` refactor.

## What changed

* Business logic migrated from `bin/scripts/` into a proper Python
  package at `src/signal_engine/`, installable via `uv pip install -e .`.
* Files in `bin/scripts/` are now thin shims that import and invoke
  `signal_engine.cli.*:main`. Every documented invocation in the prior
  `bin/scripts/README.md` still works verbatim.
* Three installable console entry points were added to `pyproject.toml`
  under `[project.scripts]`: `signal-engine-ingest`, `signal-engine-analyze`,
  `signal-engine-review`. The shim paths remain canonical; entry points
  are a convenience.
* Each overly-long module was split into single-responsibility units.
  Every module under `src/signal_engine/` is now under 200 lines
  (largest: `ingestion/pdf/factset.py` at 173 lines).
* Each detector became its own module under
  `src/signal_engine/analysis/detectors/`, collected in a `HEURISTIC_DETECTORS`
  registry consumed by the Fusion Engine. Adding a new detector means
  adding a module and a row in `detectors/__init__.py` — no other changes.
* The Fusion Engine (`analysis/fusion/engine.py`) is now a single named
  component per ARCHITECTURE.md §8. Its contract accepts a sequence of
  heuristic detectors (populated in V1) and a sequence of learned
  detectors (empty in V1; the architectural seam is preserved per
  DECISION_LOG DL-2026-015).
* The Signal Store gained an abstract interface
  (`store/interface.py`) with a filesystem-backed implementation
  (`store/filesystem.py`). The on-disk JSONL format and the
  `data/signals/<entity>.jsonl` path are unchanged.
* Duplicated helpers — `PROJECT_ROOT` computation (19 copies), `load_json`
  / `write_jsonl`, SHA-256 file hashing, the Chrome user-agent string,
  ISO timestamp formatting — collapsed into `signal_engine/paths.py`
  and `signal_engine/io.py`.
* CLI argparse was removed from every library module and rehomed to
  dedicated modules under `src/signal_engine/cli/`. No library module
  does more than one of: load config, transform data, persist results,
  parse CLI args.

## What did NOT change (by design)

* Artifact paths: `data/raw/…`, `data/normalized/…`, `data/analytical/…`,
  `data/signals/…`, `data/manifests/…` are unchanged. Re-running after
  the refactor reuses existing outputs idempotently.
* Signal on-disk schema: every field in `data/signals/<entity>.jsonl`
  matches the pre-refactor output. Pre- and post-refactor `nvda.jsonl`
  (37 rows) and `meta.jsonl` (19 rows) are byte-for-byte identical
  modulo `emission_time` (a wall-clock stamp that necessarily differs
  between runs).
* Detector semantics: every detector produces the same Signals at the
  same thresholds. No "smarter" rewrites.
* Dependency set in `pyproject.toml` is unchanged. `pytest` was added
  under the new `[project.optional-dependencies] dev` group; no runtime
  dependency was added.
* V1 analysis is heuristic-only per DECISION_LOG DL-2026-015. No ML
  dependencies were introduced. No stub ML modules were added beyond
  `detect_contradictions` which existed before (and now lives in its
  own module).
* The `bin/scripts/` directory still exists as the canonical invocation
  path. The three installable entry points in `[project.scripts]` are
  additive.
* Voice of docstrings matches `.claude/docs/CONTEXT.md` — hedged,
  bulleted where useful, no emojis, no marketing.

## File-by-file mapping

### Ingestion (`bin/scripts/` → `src/signal_engine/`)

| Old path | New library module | New CLI module | Shim |
|---|---|---|---|
| `v1_ingest.py` | — | `cli/v1_ingest.py` | `bin/scripts/v1_ingest.py` |
| `edgar/fetch.py` | `ingestion/edgar/fetch.py` | `cli/edgar_fetch.py` | `bin/scripts/edgar/fetch.py` |
| `edgar/extract_press_releases.py` | `ingestion/edgar/press_releases.py` + `ingestion/edgar/sgml.py` | `cli/edgar_press_releases.py` | `bin/scripts/edgar/extract_press_releases.py` |
| `pdf/discover.py` | `ingestion/pdf/discover.py` + `ingestion/pdf/discover_patterns.py` | `cli/pdf_discover.py` | `bin/scripts/pdf/discover.py` |
| `pdf/build_manifest.py` | `ingestion/pdf/manifest.py` + `ingestion/pdf/url_probing.py` | `cli/pdf_manifest.py` | `bin/scripts/pdf/build_manifest.py` |
| `pdf/fetch.py` | `ingestion/pdf/fetch.py` | `cli/pdf_fetch.py` | `bin/scripts/pdf/fetch.py` |
| `pdf/normalize.py` | `ingestion/pdf/normalize.py` + `ingestion/pdf/factset.py` + `ingestion/pdf/factset_patterns.py` | `cli/pdf_normalize.py` | `bin/scripts/pdf/normalize.py` |
| `pdf/batch.py` | `ingestion/pdf/batch.py` | `cli/pdf_batch.py` | `bin/scripts/pdf/batch.py` |
| `audio/discover.py` | `ingestion/audio/discover.py` + `ingestion/audio/patterns.py` + `ingestion/audio/http.py` + `ingestion/audio/browser.py` + `ingestion/audio/wayback.py` | `cli/audio_discover.py` | `bin/scripts/audio/discover.py` |
| `audio/fetch.py` | `ingestion/audio/fetch.py` | `cli/audio_fetch.py` | `bin/scripts/audio/fetch.py` |
| `audio/transcribe.py` | `ingestion/audio/transcribe.py` | `cli/audio_transcribe.py` | `bin/scripts/audio/transcribe.py` |
| `audio/normalize.py` | `ingestion/audio/normalize.py` | `cli/audio_normalize.py` | `bin/scripts/audio/normalize.py` |
| `audio/batch.py` | `ingestion/audio/batch.py` | `cli/audio_batch.py` | `bin/scripts/audio/batch.py` |

### Analysis

| Old path | New library module | New CLI module | Shim |
|---|---|---|---|
| `analysis/features.py` | `analysis/features.py` + `analysis/press_release_features.py` + `analysis/feature_primitives.py` | `cli/features.py` | `bin/scripts/analysis/features.py` |
| `analysis/baseline.py` | `analysis/baselines.py` | `cli/baseline.py` | `bin/scripts/analysis/baseline.py` |
| `analysis/detect.py` | `analysis/detectors/{base,confidence_shift,structural_anomaly,narrative_drift,omission,contradiction}.py` + `analysis/fusion/{confidence,engine}.py` + `domain/signal.py` | `cli/detect.py` | `bin/scripts/analysis/detect.py` |
| `analysis/pipeline.py` | — | `cli/analyze.py` | `bin/scripts/analysis/pipeline.py` |
| `analysis/review.py` | `store/{interface,filesystem}.py` | `cli/review.py` | `bin/scripts/analysis/review.py` |

### New modules with no direct predecessor

* `signal_engine/paths.py` — project paths, formerly 19 duplicated `PROJECT_ROOT = Path(__file__).resolve().parents[N]` expressions
* `signal_engine/io.py` — shared `load_json`, `write_jsonl`, `sha256_file`, `USER_AGENT`, `now_iso`
* `signal_engine/domain/entity.py` — `Entity`, `Speaker` dataclasses + loaders (DATA_MODEL.md types materialized)
* `signal_engine/domain/signal.py` — `Signal` dataclass + `LIFECYCLE_STATES`, previously inline in `detect.py`
* `signal_engine/config/{lexicons,themes,companies}.py` — config loaders, previously duplicated
* `signal_engine/store/interface.py` + `filesystem.py` — `SignalStore` ABC + concrete impl, replacing ad-hoc file I/O in `detect.py` and `review.py`
* `signal_engine/analysis/fusion/engine.py` + `confidence.py` — `FusionEngine` class wrapping what was inline orchestration in `detect.py`; `confidence_label` extracted

## Behavioral preservation check

A single `uv run python bin/scripts/analysis/pipeline.py` run was
executed before and after the refactor against the same
`data/normalized/` corpus (4 NVDA transcripts, 86 press releases
across NVDA/META).

* Pre-refactor: 56 signals total (NVDA 37, META 19)
* Post-refactor: 56 signals total (NVDA 37, META 19)

Every Signal row is byte-for-byte identical in the pre/post JSONL
modulo the `emission_time` field (wall-clock stamp, unavoidable).
Verification script:

```python
def canonicalize(row):
    row = dict(row); row.pop('emission_time', None)
    return json.dumps(row, sort_keys=True)
pre  = [canonicalize(json.loads(l)) for l in open('pre/nvda.jsonl')]
post = [canonicalize(json.loads(l)) for l in open('post/nvda.jsonl')]
assert pre == post
```

## Decisions and rationale

### Shims in `bin/scripts/` (not only entry points)

The refactor preserves every `uv run python bin/scripts/...` path as a
thin shim that imports from `signal_engine.cli.*`. An alternative
design — only expose `[project.scripts]` entry points — would have
broken every command in the legacy README. Since the user's mandate
was to preserve every CLI invocation, shims stayed. Entry points are
additive.

### Pipeline orchestrators keep subprocess isolation

`v1_ingest` and `analyze` (formerly `analysis/pipeline.py`) orchestrate
their stages as subprocesses. The current behavior is that a failed
stage logs an exit code but does not kill the batch. Collapsing to
in-process function calls would have changed that failure-isolation
semantic. Subprocess stayed. The inner command changed from
`python <shim_path>` to `python -m signal_engine.cli.<stage>` so the
orchestrator no longer depends on on-disk script paths; users who
invoke shims directly still go through the shim.

### Detector registry instead of a hard-coded list

`detect.py` previously hard-coded a list of five `detect_*` calls. The
new `HEURISTIC_DETECTORS` tuple in `analysis/detectors/__init__.py`
makes the set of detectors a data structure, so the Fusion Engine
iterates it without naming specific detectors. This is the
extensibility axis called out in ARCHITECTURE.md (Extensibility, "new
analytical modules — heuristic or learned — by attaching them as
feature contributors to the Fusion Engine without altering the Fusion
Engine's contract"). Adding a Contradiction Event detector in a future
phase means adding a module and a row — no Fusion Engine change.

### `FusionEngine` as a class, not a function

The V1 orchestration could have been a module-level `run_detectors`
function. It was made a class so learned-side detectors (Phase 1.5)
can be passed via constructor without changing callers, and so
configuration (custom transcript_dir in tests, for instance) has a
natural home. The class is still purely heuristic-only in V1.

### `Basis` stays a plain dict

The data-model document treats Basis as a structural component with
heuristic + learned contributions and a Basis Disagreement field. V1
populates only the heuristic side. The schema could have been locked
down with a dataclass, but keeping it a `dict` lets the learned-side
keys (`learned_contribution`, `basis_disagreement`) be added later
without a schema break. `test_basis_field_is_mutable_dict_for_future_learned_contribs`
exercises this.

### Omission detector ignores `threshold` / `min_observations`

`detect_omissions` uses its own `min_recurrence_window=4` /
`min_recurrence_count=3` policy rather than the generic detector
arguments. The legacy `detect.py` did this inline. The new
`detect_omissions` signature accepts (and ignores) the common kwargs
so the detector registry can be iterated uniformly from the Fusion
Engine. This preserved the legacy behavior exactly.

### `datetime.utcnow() + "Z"` in press-release extraction

The legacy `extract_press_releases.py` uniquely used `datetime.utcnow()
+ "Z"` while every other module used `datetime.now(tz=UTC).isoformat()`
which produces `+00:00`. The refactor preserved the `Z` suffix in
`signal_engine/ingestion/edgar/press_releases.py` to keep the
observation_time string format byte-identical. Worth unifying in a
follow-on.

### Hatchling as build backend

The legacy `pyproject.toml` had no `[build-system]`. Hatchling was
chosen because it is the simplest src-layout-compatible backend with
no runtime cost, and it cleanly supports
`[tool.hatch.build.targets.wheel] packages = ["src/signal_engine"]`.

## Follow-on work for a subsequent agent

* **Unify timestamp format.** The press-release extraction path writes
  `observation_time` in `...Z` form while every other derived artifact
  uses `...+00:00`. Downstream consumers do not currently care, but
  callers who parse these strings should not have to handle two forms.
  A single call to `io.now_iso()` would fix this; preserving the
  legacy format kept the behavioral-preservation check airtight.
* **Move `extraction_time` + `emission_time` out of the deterministic
  payload.** Currently every re-run of features → baselines → detect
  writes different `extraction_time`, `emission_time`, and
  `generated_at` values, so byte-diffing the output requires the
  canonicalization helper in this doc. Moving those fields into a
  sidecar `*.run.json` would make the primary artifacts deterministic.
  Out of scope for this refactor.
* **Delete `bin/scripts/analysis/__init__.py`.** No longer needed now
  that the shims are importable without the package marker. Left in
  place to avoid an unrelated change.
* **Add a `DerivationRun` type.** DATA_MODEL.md defines DerivationRun
  as first-class; the V1 code records it implicitly (via rule_id and
  the features/baselines file mtimes). Making it explicit is part of
  the Phase 1.5 work that introduces the learned side.
* **Phase 1.5 landing: Contradiction Event detector.** When the
  Representation model ships, `analysis/detectors/contradiction.py`
  is the landing site. The Fusion Engine already accepts learned
  detectors via `FusionEngine(learned_detectors=...)`; populating that
  sequence and emitting Signals that carry `basis.basis_disagreement`
  is the expected path.
* **Break up the audio batch StageResult helpers.** The helpers live
  in both `cli/audio_batch.py` (run_stage) and
  `ingestion/audio/batch.py` (skip_result, audio_exists, etc.). Both
  were kept small; if they grow, promote the shared dataclass and
  logging helpers into a `signal_engine/ingestion/batch_log.py`.

## Confirming the refactor passes its acceptance criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Every CLI from CRITICAL COMMITMENTS works | ✓ — all 11 paths verified via `--help` + full-pipeline run |
| 2 | Signals produced before/after are identical | ✓ — byte-identical modulo `emission_time` (see verification script above) |
| 3 | Every module under `src/signal_engine/` is under 200 lines | ✓ — largest is `ingestion/pdf/factset.py` at 173 |
| 4 | No module does more than one of {load config, transform, persist, parse CLI args} | ✓ — argparse is confined to `cli/`; library modules do not `import argparse` |
| 5 | Each detector is independently importable and testable | ✓ — `tests/test_detectors.py` exercises every detector in isolation |
| 6 | `tests/` passes | ✓ — 18/18 |
| 7 | `uv pip install -e .` succeeds | ✓ — verified |
| 8 | Old→new mapping documented | ✓ — this document |
| 9 | `bin/scripts/README.md` + `src/signal_engine/README.md` reflect the new layout | ✓ — both updated |
