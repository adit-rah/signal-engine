# EVENTS_AND_PIPELINES.md

## Purpose Of This Document

EVENTS_AND_PIPELINES.md specifies how data moves between components in the Signal Engine: the event model that couples components, the per-component operating mode (batch, on-demand, scheduled), the re-derivation scheduling and throttling strategy under the low-capital constraint, the failure semantics that preserve immutability and traceability, and the pipeline-versioning mechanism that makes historical replay reproducible.

This document is conceptual. It does not select queue technologies, orchestration products, or scheduler implementations. It defines the semantics that any realization of the pipeline must satisfy so that the [ARCHITECTURE.md](./ARCHITECTURE.md) components operate as a coherent system.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Component ownership is defined in [ARCHITECTURE.md](./ARCHITECTURE.md); temporal semantics are defined in [DATA_MODEL.md](./DATA_MODEL.md).

---

## How To Read This Document

* the event model is described by the coupling type (event, shared state, direct call) and the contract each implies
* operating mode is stated per component, not globally
* re-derivation is discussed as a first-class scheduling concern because the low-capital constraint makes it so
* pipeline versioning is the mechanism that makes re-derivation reproducible; it is described once here and referenced in downstream documents

---

## Guiding Commitments

Inherited from upstream documents and held as invariants for pipelines:

* v1 operating posture is deliberate, batch-oriented, or on-demand ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T2, T3, U6; [ARCHITECTURE.md](./ARCHITECTURE.md) Operating Posture) — continuous real-time streaming is out of scope
* low-capital constraint ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint) — pipelines must not assume continuously-running stream infrastructure
* immutability and re-derivability are data-model invariants (DATA_MODEL.md §Immutability And History, §Derivation Layers) — pipelines must preserve them under all failure modes
* traceability is a system-wide property (CONTEXT §3.3; [ARCHITECTURE.md](./ARCHITECTURE.md) Traceability And Explainability) — every inter-component transition emits provenance
* replaceability of components ([ARCHITECTURE.md](./ARCHITECTURE.md) Replaceability) — pipeline coupling must not bake in a specific implementation of any component

---

## Derivation Layer Ownership Across This Cluster

For clarity, the derivation layers of [DATA_MODEL.md](./DATA_MODEL.md) are realized across the Data & Ingestion cluster as follows. Pipeline behavior below is described against this mapping.

* **Raw** — produced by Ingestion; specification owned by [INGESTION_SPEC.md](./INGESTION_SPEC.md)
* **Normalized** — produced by Document Processing; specification owned by [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md). Segments and Utterances as structural identification belong here as "canonical text and structure" (DATA_MODEL.md §Derivation Layers)
* **Enriched** — tags and annotations attached to Normalized structure, produced across multiple components: canonical Entity and Speaker reconciliation by Entity Resolution; ThemeInstances by Heuristic Analysis and Learned Analysis jointly; additional enrichment annotations on Segments and Utterances (for example, canonical Speaker linking) by Entity Resolution. DATA_MODEL.md notes that Enriched/Normalized boundaries are directional rather than strict; this cluster honors that posture
* **Analytical** — produced by Heuristic Analysis, Representation, Learned Analysis, and Baseline Maintenance; specification owned by NARRATIVE_ANALYSIS.md and MODEL_STRATEGY.md (out of this cluster)
* **Signal** — produced by the Fusion Engine and stored by the Signal Store; specification owned by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)

Pipeline decisions in this document are shaped by this ownership mapping: events flow along this progression, and re-derivation is scoped to the DerivationRuns that own each layer's transformation.

---

## Event Model

Component coupling takes three forms. Each has a clear contract.

### Event-Based Coupling (Default)

Most coupling between components is event-based: component A produces an artifact of a known class, and component B reacts to artifacts of that class by performing its own derivation. Component B does not call component A; component B observes that an artifact has arrived.

The event is the artifact's commit. Events carry only the artifact's identifier and its class (Raw, Normalized, Enriched, Analytical, Signal) — they do not carry payload. Component B reads the artifact by identifier and reads its provenance from the Evidence & Provenance Store.

Event-based coupling preserves component replaceability: producers and consumers share only the artifact contract, not an execution contract.

### Shared-State Coupling

Two stores are shared across the pipeline:

* the **Evidence & Provenance Store** ([ARCHITECTURE.md](./ARCHITECTURE.md) §11) — every derived artifact writes its DerivationRun and span references here; every downstream component reads provenance from here rather than receiving it as payload
* the **Baseline** ([ARCHITECTURE.md](./ARCHITECTURE.md) §4) — Baseline Maintenance writes, and Heuristic Analysis, Learned Analysis, and the Fusion Engine read — typically at emission time

Shared-state coupling is the alternative to inflating the event payload. It keeps events small and preserves the property that provenance is queryable independently of the pipeline.

### Direct-Call Coupling (Reserved)

Direct, synchronous calls between components are reserved for cases where a consumer needs a read at a specific point in its own processing — for example, the Fusion Engine reading the Baseline at emission time, or the Query & Retrieval Surface reading the Signal Store in response to a caller. Direct calls are reads, not writes; writes always happen via artifact commits and shared-state updates.

Direct-call coupling never replaces an event. A consumer that reacts to new artifacts always reacts via the event channel; it does not poll a producer directly.

---

## Orchestration Of Document Flow

A single Document travels through the cluster as follows. This extends [ARCHITECTURE.md](./ARCHITECTURE.md)'s Document Travel narrative with pipeline semantics.

* **Ingestion** commits a Document record and a Raw artifact, and writes ingestion provenance to the Evidence & Provenance Store. Commit emits a "Document committed" event.
* **Document Processing** reacts to the "Document committed" event by producing a Normalized artifact, Segments, Utterances, and within-Document Speaker handles, under its own DerivationRun. Commit emits a "Normalized produced" event.
* **Entity Resolution** reacts to the "Normalized produced" event by attaching canonical Entity identity and reconciling within-Document Speaker handles to canonical Speakers. Commit emits an "Enrichment produced" event.
* **Heuristic Analysis** and **Representation** react to "Enrichment produced" independently and in parallel. Each commits its own Analytical-layer artifacts and emits their commits as events. **Learned Analysis** reacts to "Representation produced" events.
* **Baseline Maintenance** reads the prior Baseline (direct call on behalf of Heuristic Analysis and Learned Analysis for comparison) and writes updated Baselines as new valid-time intervals after the Analytical-layer artifacts for the Document commit.
* **The Fusion Engine** reacts to the readiness of all required Analytical-layer artifacts for the Document — heuristic features, learned features, Baselines — and emits Signals. Commit writes to the Signal Store and emits a "Signal emitted" event.
* **Ranking & Surfacing**, the **API Boundary**, and the **Evaluation Harness** consume Signals via the Query & Retrieval Surface or via "Signal emitted" events as appropriate.

Each transition writes provenance to the Evidence & Provenance Store. The "readiness" of the Fusion Engine's upstream inputs is a shared-state concern, not an event-payload concern: the Fusion Engine checks readiness by reading artifact presence, not by aggregating events.

---

## Per-Component Operating Mode

Each component operates in one of three modes. The choice is driven by the low-capital constraint and the deliberate posture.

### Batch

The component processes a bounded set of artifacts on a schedule or on demand. Batch is the default for components that benefit from amortization (Representation, Baseline Maintenance during bulk recomputation) or that rely on cross-artifact analysis (Heuristic Analysis for omission tracking, Learned Analysis for cluster-level signals).

Batch does not imply large scale; a batch of one is a valid batch.

### On-Demand

The component produces output in response to an explicit request — either a downstream consumer needing a just-in-time computation or an operator triggering a re-derivation. On-demand is appropriate where computation is expensive and output is queried rarely.

### Scheduled

The component runs on a defined cadence — typically daily or weekly for v1 — independent of specific input arrivals. Scheduled is appropriate for maintenance operations (Baseline updates that amortize over multiple Documents, Source-quality sampling).

### Mode Per Component

Not prescriptive; stated so downstream infrastructure work has a consistent starting point. Components may run in more than one mode.

* **Ingestion** — event-driven per arrival; operates as each artifact arrives
* **Document Processing** — event-driven per Document commit, with an on-demand mode for re-normalization
* **Entity Resolution** — event-driven per Document, with a scheduled mode for cross-Document reconciliation refresh
* **Heuristic Analysis** — event-driven per Enrichment commit, with a scheduled mode for cross-Document analyses (omission tracking, for example)
* **Representation** — batch, event-triggered, where each batch amortizes shared model-loading cost
* **Learned Analysis** — batch, reacting to Representation outputs
* **Baseline Maintenance** — batch or scheduled, typically running after Analytical-layer updates for a Document
* **Fusion Engine** — event-driven on upstream-readiness, with on-demand re-emission for re-derivations
* **Ranking & Surfacing** — on-demand, driven by query load through the Query & Retrieval Surface
* **Evaluation Harness** — scheduled or on-demand for sampling; event-driven for new-Signal observation
* **Query & Retrieval Surface** and **API Boundary** — on-demand, per caller

Nothing in v1 requires a component to run continuously. A component whose inputs are idle is idle.

---

## Re-Derivation Scheduling And Throttling

Re-derivation — re-running a DerivationRun of a later version against prior inputs — is a first-class operation (DATA_MODEL.md §Derivation Layers). Under the low-capital constraint, it must be bounded.

### Re-Derivation Triggers

Three triggers exist:

* **scheduled** — a component's DerivationRun is refreshed on a defined cadence against an eligible subset of its inputs. Used for periodic refreshes (Baseline recomputation, scheduled re-normalization after a DerivationRun version bump).
* **event-triggered** — a change in an upstream artifact (a re-normalized Document, a reclassified Source) triggers re-derivation of downstream artifacts that depended on the prior version.
* **on-demand** — an operator or an automated quality signal triggers re-derivation explicitly, scoped to specific artifacts.

### Coalescing

Event-triggered re-derivation is coalesced: if multiple upstream changes arrive in a window, a single downstream re-derivation covers all of them. Coalescing is bounded by a window appropriate to the component's cost; the specific window is deferred to downstream implementation.

### Throttling

Re-derivation is throttled by two independent mechanisms:

* **bounded concurrency per DerivationRun class** — at most a configured number of re-derivation runs of a given class proceed simultaneously
* **per-subject rate caps** — re-derivation against a single Entity, Source, or Document does not exceed a configured rate, to prevent a single subject from saturating re-derivation capacity

Specific numbers are deferred to downstream infrastructure work. The shape — concurrency cap plus per-subject rate cap — is committed here.

### Priority

Re-derivation operations have a priority ordering:

* **corrective** — re-deriving to remedy a known quality defect (highest priority)
* **version-cascading** — re-deriving to bring downstream artifacts current with an upstream DerivationRun version bump
* **scheduled refresh** — periodic re-derivation without a specific trigger (lowest priority)

Priority is implemented as queue discipline; specific queue mechanics are deferred.

### Budget

Re-derivation consumes a bounded portion of total computation. The budget is a policy input, not an emergent property. Without such a bound, continuous re-derivation under a long upstream-change history would violate the low-capital constraint.

### No Continuous Streams

Re-derivation never runs as a continuous stream. A "re-derivation worker" is a scheduled or event-triggered component that does bounded work and then idles, not a process perpetually chewing through the history.

---

## Failure Semantics Under Immutability

Pipelines fail. Failure modes must not violate the immutability invariants that the data model depends on.

### Artifact Commit Is Atomic

An artifact either commits or it does not. A partial artifact — normalized text without Utterances, a Signal without Evidence, a Baseline without valid-time — is not committed.

Atomicity is enforced at the component level. A component whose internal state is inconsistent must not commit.

### Failed DerivationRuns Are Recorded

Every DerivationRun, including failed ones, is recorded in the Evidence & Provenance Store. A failed DerivationRun records the failure condition, the inputs that were being processed, and any partial outputs that were safely discarded.

This is not a debugging nicety; it is required for replayability. A historical replay of the pipeline must be able to answer "why was this artifact not produced?" as well as "why was this artifact produced this way?"

### Retries Produce New DerivationRuns

A retry after a failure is a new DerivationRun, not a retry of the prior one. The prior failed DerivationRun stays on record; the new DerivationRun records its own inputs, outputs, and relationship to the prior one.

This preserves the rule that DerivationRuns are immutable once created.

### Quarantine Is A First-Class State

At every derivation layer, a quarantined artifact is a recorded state — a Document that failed ingestion, a Normalized artifact whose Segmentation could not be recovered, an Analytical artifact whose inputs were incomplete. Quarantined artifacts do not propagate downstream; downstream components observe their absence, not a malformed version.

[INGESTION_SPEC.md](./INGESTION_SPEC.md) defines ingestion-layer quarantine. Analogous states exist at each derivation layer and follow the same shape: preserve the upstream, record the failure, do not propagate.

### Traceability Of Failure

A failure in any component is traceable. The Evidence & Provenance Store is the single place to ask "what happened to artifact X?" Pipeline failures do not create silent gaps in the trace.

---

## Pipeline Versioning

A Pipeline Version is the mechanism that makes historical replay reproducible. This is a new term introduced here and flagged for glossary extension.

### Definition

A Pipeline Version pins the DerivationRun version of every stage a Document flows through — ingestion DerivationRun, normalization DerivationRun, enrichment DerivationRuns, analytical DerivationRuns (heuristic, learned, Baseline), and fusion DerivationRun.

### Properties

* a Pipeline Version is immutable; a change to any stage's DerivationRun version produces a new Pipeline Version
* a Pipeline Version has a creation time and a description of the changes that produced it
* every derived artifact records the Pipeline Version under which it was produced, in addition to the individual DerivationRuns it references
* a Pipeline Version is a pin, not a schedule; it does not by itself trigger re-derivation

### Replay

Replaying a Document (or a set of Documents) under a specific Pipeline Version reproduces the derived artifacts that Pipeline Version would produce. Replay is not destructive: it produces a parallel set of derived artifacts, tagged with the Pipeline Version, alongside any prior set.

Replay consumers — the Evaluation Harness, operator-driven backfills, retroactive Signal reconstruction — reference artifacts by Pipeline Version, not by a moving "current" pointer.

### Current Pipeline Version

At any time, one Pipeline Version is the current default for new Documents arriving through the pipeline. The current Pipeline Version moves deliberately; promotion to current is a governance operation coordinated with [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)'s version-tracking responsibilities.

Moving the current Pipeline Version does not invalidate or rewrite artifacts produced under prior versions. Downstream re-derivation is a separate, bounded operation under the scheduling and throttling rules above.

### Multiple Pipeline Versions Coexist

Because re-derivation is bounded and deliberate, multiple Pipeline Versions typically coexist in the system's state at any time. The Query & Retrieval Surface ([SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md)) exposes Pipeline Version as a queryable dimension.

---

## Backfill And Historical Re-Derivation

Backfill — re-deriving against a large historical set of Raw artifacts — is a special case of re-derivation. It follows the same invariants:

* backfill runs under a named Pipeline Version
* backfill produces a parallel set of derived artifacts rather than mutating existing ones
* backfill respects the throttling rules above; a backfill does not saturate the pipeline and block live ingestion
* backfill is observable through the Evidence & Provenance Store; its progress, completions, and failures are queryable

Backfill is not a first-class feature with its own pipeline; it is re-derivation at larger scale.

---

## Cross-Component Contracts

A short statement of each coupling in the cluster, for cross-reference.

* **Ingestion → Document Processing** — event ("Document committed"); Document Processing reads the Raw artifact by identifier
* **Document Processing → Entity Resolution** — event ("Normalized produced"); Entity Resolution reads the Normalized artifact and the within-Document Speaker handles
* **Entity Resolution → downstream analysis** — event ("Enrichment produced"); Heuristic Analysis, Representation, and Learned Analysis read Enriched artifacts
* **Analytical → Baseline Maintenance** — artifact commits trigger Baseline Maintenance to update; Baseline Maintenance updates are themselves artifact commits with valid-time intervals
* **Baseline → Fusion Engine and analyses** — direct read; consumers read the current Baseline (or a specified valid-time Baseline) when needed
* **Analytical readiness → Fusion Engine** — shared-state readiness; the Fusion Engine reads artifact presence, not events
* **Fusion Engine → Signal Store** — artifact commit; Signal emission is the write
* **Signal Store → Query & Retrieval Surface** — direct read on query
* **Any component → Evidence & Provenance Store** — write on derivation; read by any component that needs provenance
* **Any component → consumers of lifecycle events** — artifact commits emit events for subscribers (Evaluation Harness, Ranking & Surfacing)

---

## What This Document Is Not

* not an infrastructure selection (no queue technology, orchestration product, or scheduler implementation is chosen here)
* not a scaling document (scaling is a downstream infrastructure concern)
* not a deployment plan
* not an observability specification (owned by OBSERVABILITY.md)
* not a failure-mode catalog (owned by FAILURE_MODES.md)

---

## Deferred Decisions

* specific event transport — downstream infrastructure work
* specific orchestration product — downstream infrastructure work
* specific scheduler — downstream infrastructure work
* coalescing windows, concurrency caps, and rate-limit parameters — downstream infrastructure work
* retry policy and backoff — downstream infrastructure work, coordinated with [INGESTION_SPEC.md](./INGESTION_SPEC.md) and [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)
* specific Pipeline Version promotion workflow — [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) and downstream operational work
* re-derivation budget numbers — downstream infrastructure work
* observability and alerting — OBSERVABILITY.md
* detailed failure-mode response — FAILURE_MODES.md

---

## Open Questions

* How is Pipeline Version promotion coordinated with ongoing re-derivation? A naïve promotion during a large backfill doubles work; the promotion discipline is flagged as an operational concern.
* How does the Fusion Engine's "readiness" check scale as the number of analytical contributors grows? Shared-state readiness is simple at v1 component count; if Heuristic Analysis and Learned Analysis grow into many sub-modules, the readiness contract may need explicit declaration. Flagged.
* How are long-running Learned Analysis or Representation batches interrupted for a promotion of a higher-priority re-derivation? Pre-emption discipline is deferred.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the components this document orchestrates.
* [DATA_MODEL.md](./DATA_MODEL.md) defines immutability, re-derivability, and DerivationRuns, which this document's pipeline rules preserve.
* [INGESTION_SPEC.md](./INGESTION_SPEC.md) and [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md) define the upstream stages; their quarantine and DerivationRun rules compose under this document's pipeline semantics.
* [SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md) exposes Pipeline Version as a queryable dimension and consumes the pipeline's output.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) owns retention, deletion, and licensing enforcement across the artifacts these pipelines produce, plus Pipeline Version promotion workflow.
* FAILURE_MODES.md and OBSERVABILITY.md will consume the failure and provenance semantics defined here.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms introduced here (Pipeline Version, Coalescing, Quarantine at layer scope) are flagged for extension in the cluster's closing summary.
