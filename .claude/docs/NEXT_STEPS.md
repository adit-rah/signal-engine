# NEXT_STEPS.md

## Purpose Of This Document

This document records the immediate next steps for the Signal Engine project after the architectural and design documentation has been completed.

It is a living, short-lived artifact. It will be superseded as work progresses and can be safely archived once Phase 1 of the roadmap begins in earnest.

It is written to be self-contained so that another contributor (human or agent) can pick it up and continue without needing the prior conversation history.

---

## State Of The Project

* The full architectural and design documentation is complete and internally coherent (31 documents in this directory, indexed by [`README.md`](./README.md)).
* No code has been written.
* No data has been acquired.
* No models have been trained.
* V1 scope is committed to earnings call transcripts (see [`CONTEXT.md`](./CONTEXT.md) §8 and [`SCOPE.md`](./SCOPE.md) Initial Scope).
* The model-ownership posture is in-house, small, specialized, with no external LLM APIs in critical paths (see [`CONTEXT.md`](./CONTEXT.md) §6).
* V1 is English-first.
* The false-positive posture and thin-history posture are both reliability-preferring.
* Every load-bearing decision made so far is recorded in [`DECISION_LOG.md`](./DECISION_LOG.md).

---

## The Critical Path

One thing blocks everything else: **can the project actually acquire earnings call transcripts with sufficient historical depth, acceptable quality, and a licensing posture compatible with training in-house models, under the low-capital constraint?**

Until this is answered with real evidence, every downstream piece of work (ingestion parsers, representation-model training, evaluation harness) is speculative.

This is the subject of the data acquisition feasibility spike, described below.

---

## Step 1: Commit The Documentation To Git

Before any implementation work begins, commit the current document set to git. A single commit captures the full design baseline and gives all subsequent changes a clear reference point.

This step is mechanical; no decisions are pending.

---

## Step 2: Data Acquisition Feasibility Spike

The first real engineering task. Timebox: **1 to 2 weeks** of focused effort.

### Question To Answer

Can the project obtain earnings call transcripts that simultaneously satisfy:

* **Historical depth** — enough quarters per Entity to construct meaningful Baselines (typically a few years)
* **Quality** — speaker attribution preserved, punctuation meaningful, completeness sufficient for analysis
* **Licensing posture** — terms that permit training use of in-house models, not only read-only analytical use
* **Cost profile** — compatible with the low-capital posture

If yes: the answer feeds the elaboration of [`DATA_ACQUISITION.md`](./DATA_ACQUISITION.md) from stub into full document, and the first implementation slice can begin.

If no or partial: the project's v1 domain or model-ownership posture may need to bend, and this becomes a decision recorded in [`DECISION_LOG.md`](./DECISION_LOG.md).

### Sources To Investigate

Survey, at a minimum, the following. For each, document: availability, historical depth typically available, licensing posture (training-compatible, analytical-only, incompatible-or-ambiguous), quality characteristics, access method, estimated cost.

* **SEC EDGAR** — 10-K, 10-Q, and 8-K filings are in the public domain and programmatically accessible. Some 8-K filings include transcript-like exhibits. Start here because it is free and legally unambiguous.
* **Company Investor Relations pages** — most public companies post transcripts, prepared remarks, or audio recordings on their own IR sites. Survey twenty or so representative companies across sectors; note historical archive depth per company.
* **Third-party aggregators** — platforms that aggregate earnings transcripts (for example, analyst-oriented services and financial media outlets). Read their terms of service carefully; many explicitly prohibit training use. Classify each source by Licensing Posture per [`DOMAIN_GLOSSARY.md`](./DOMAIN_GLOSSARY.md).
* **Open-licensed academic corpora** — check for research datasets of earnings transcripts released under permissive licenses. Some exist in the NLP research literature.
* **Direct-capture paths** — audio-to-text of publicly broadcast earnings calls, done in-house. Assess feasibility under the low-capital constraint (ASR quality, compute cost, Licensing Posture implications).

### Output Expected

A short findings document (3 to 10 pages) covering:

* Source-by-source survey with the fields above
* A recommended acquisition strategy for v1 (which sources, in what combination, under what posture)
* Identified risks to the v1 domain commitment, if any
* Any proposed decisions to add to [`DECISION_LOG.md`](./DECISION_LOG.md)
* A concrete proposal for elaborating [`DATA_ACQUISITION.md`](./DATA_ACQUISITION.md) from its current stub

The findings document can be drafted directly in [`RESEARCH_NOTES.md`](./RESEARCH_NOTES.md) as a Finding entry and referenced from the DATA_ACQUISITION.md rewrite.

### Voice And Style For The Findings

Match the voice of [`CONTEXT.md`](./CONTEXT.md) — hedged, bulleted, no emojis, no marketing, no first-person.

### Working Assumptions During The Spike

The spike may assume:

* The project is single-user and low-capital (see [`ASSUMPTIONS.md`](./ASSUMPTIONS.md)).
* External LLM APIs are not available as a paid solution; inference budget is minimal.
* V1 is English-first.
* The project is willing to start with fewer Entities and more historical depth, rather than many Entities with shallow history.

### What Is Out Of Scope For The Spike

* Building any ingestion code.
* Selecting specific parsers or storage technology.
* Training any models.
* Negotiating commercial licenses.

The spike answers a feasibility question. It does not start implementation.

---

## Step 3: First Implementation Slice

Only after the acquisition spike returns a confident "yes."

The goal is to prove the structural spine end-to-end with one real document, not to build anything production-grade. Timebox: **2 to 4 weeks** after acquisition is resolved.

### Minimum Slice

* Acquire one earnings call transcript under a Training-Compatible Licensing Posture (ideally from SEC EDGAR or a company IR page, to avoid third-party terms).
* Land it as a Raw artifact per [`DATA_MODEL.md`](./DATA_MODEL.md).
* Produce a Normalized artifact per [`DOCUMENT_PROCESSING.md`](./DOCUMENT_PROCESSING.md).
* Resolve the Entity and Within-Document Speaker Handles.
* Compute one trivial heuristic feature (for example, count of hedging words per Utterance).
* Show the Span provenance chain from the feature all the way back to the original transcript text.

### What This Slice Proves

* The 5-layer derivation model holds up against real data.
* The identity model (Native, Canonical, Locus Identifier) is workable.
* Span provenance is preserved end-to-end.
* The Document Journey (operational view) is distinct from Evidence (signal-level view) in practice, not just on paper.

### What This Slice Does Not Prove

* Signal quality.
* Fusion Engine mechanics.
* Model strategy.
* Evaluation harness readiness.

Those come later. This slice only validates the structural spine.

### What This Slice Fails To Prove If It Succeeds Too Easily

If the slice feels trivial, re-check that Span provenance is actually round-tripping. The most common silent failure in systems of this kind is provenance that works in happy-path testing but breaks on real text (quoted speech, parenthetical interjections, speaker-turn boundaries).

---

## Step 4: Iterate On The Structural Spine

After the minimum slice holds up, the roadmap's Phase 1 takes over. See [`ROADMAP.md`](./ROADMAP.md) for phase-level discipline.

At a high level, the iteration sequence is:

* add more real transcripts to exercise the data model at volume
* add a second Entity to exercise Entity Resolution across Documents
* add the Representation component (open-weights embedding model, locally hosted)
* add one ML-layer feature that complements the heuristic feature
* wire the simplest possible Fusion Engine that combines the two
* emit a first Signal with full Basis, Evidence, and Commentary

At that point, the Evaluation Harness becomes relevant — and [`EVALUATION.md`](./EVALUATION.md) is the guide.

---

## Guardrails During Implementation

A short list to re-read before major implementation decisions.

* **Critical-Path Isolation** — no external LLM APIs in critical paths ([`CONTEXT.md`](./CONTEXT.md) §6.1, [`DECISION_LOG.md`](./DECISION_LOG.md) DL-2026-002).
* **Traceability** — every derived artifact must resolve back to Spans ([`CONTEXT.md`](./CONTEXT.md) §3.3).
* **Re-derivability** — raw is immutable; derived artifacts are re-derivable from raw plus a Pipeline Version.
* **False-Positive Posture** — in early development, prefer reliability over coverage.
* **Vocabulary** — cite [`DOMAIN_GLOSSARY.md`](./DOMAIN_GLOSSARY.md); do not redefine terms inline.
* **Decision discipline** — any non-trivial architectural choice gets a [`DECISION_LOG.md`](./DECISION_LOG.md) entry.

---

## What Not To Do Next

* Do not start writing production code before the acquisition spike returns.
* Do not select a specific embedding model, parser library, or storage technology before running the minimum slice.
* Do not add new non-v1 features to scope pressure from anything other than a completed v1 ([`ROADMAP.md`](./ROADMAP.md) anti-criteria).
* Do not let the documentation drift. If implementation surfaces a conflict with a document, resolve it with a [`DECISION_LOG.md`](./DECISION_LOG.md) entry and a targeted update, not a side-channel rewrite.

---

## Handoff Notes

If this document is handed to a fresh agent for the acquisition spike:

* The agent should read [`CONTEXT.md`](./CONTEXT.md), [`SCOPE.md`](./SCOPE.md), [`ASSUMPTIONS.md`](./ASSUMPTIONS.md), and [`DATA_ACQUISITION.md`](./DATA_ACQUISITION.md) before starting.
* The agent's output is the findings document described in Step 2 above.
* The agent should not make architectural decisions; anything that would change a commitment in [`CONTEXT.md`](./CONTEXT.md) or [`SCOPE.md`](./SCOPE.md) must be surfaced as a proposed entry for [`DECISION_LOG.md`](./DECISION_LOG.md) rather than silently enacted.
* The agent should match the voice of [`CONTEXT.md`](./CONTEXT.md) in any writing it produces.

---

## Relationship To Other Documents

* [`CONTEXT.md`](./CONTEXT.md) and [`SCOPE.md`](./SCOPE.md) are authoritative.
* [`DATA_ACQUISITION.md`](./DATA_ACQUISITION.md) is the document that will absorb this spike's findings.
* [`RESEARCH_NOTES.md`](./RESEARCH_NOTES.md) is the appropriate home for the findings themselves, pending incorporation into DATA_ACQUISITION.md.
* [`DECISION_LOG.md`](./DECISION_LOG.md) is where any scope-level conclusions are recorded.
* [`ROADMAP.md`](./ROADMAP.md) governs what happens after Step 3.
