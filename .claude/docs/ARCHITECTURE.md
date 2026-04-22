# ARCHITECTURE.md

## Purpose Of This Document

ARCHITECTURE.md defines the structural shape of the Signal Engine: the components that exist, what each owns, how they interact, how data flows, and how the commitments in CONTEXT.md and SCOPE.md are realized structurally.

This document is conceptual. It does not commit to technologies, vendors, frameworks, or deployment topology. It defines the skeleton within which Wave 2 architects make those choices.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* components are described by responsibility, not by implementation
* each component has a clearly named non-responsibility to prevent scope creep
* cross-cutting concerns (explainability, traceability, temporal reasoning, extensibility) are addressed after the components, because they must be preserved across all of them
* deferred decisions are named with the document that owns them
* vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md); new terms introduced here are flagged for glossary extension

---

## Guiding Structural Commitments

Inherited from [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md), and held as structural invariants:

* the system is hybrid — heuristic, learned, and fused — at an architectural level, not only at a conceptual level (CONTEXT §3.2)
* the Fusion Engine is a first-class component and a designated hard design problem (CONTEXT §3.2.C)
* every component preserves traceability; explainability is a system-wide property, not a layer added at the end (CONTEXT §3.3)
* components are replaceable without restructuring the system (CONTEXT §6.3)
* external large-language-model APIs do not appear in critical paths (CONTEXT §6.1)
* temporal reasoning and cross-document comparison are first-class concerns (CONTEXT §11)
* v1 operates on earnings call transcripts (CONTEXT §8); extensibility to additional domains is structural, not a rewrite
* v1 operates under a low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5, plus user-confirmed constraint): architectural choices that multiply infrastructure cost without corresponding signal-quality gains are out of scope

---

## Mapping Conceptual Layers To Architecture

CONTEXT §12 names three conceptual layers: Structural, Semantic, and Signal. CONTEXT §3.2 names three sub-layers of hybrid intelligence: Heuristic, ML, and Fusion.

These are concerns that cut across components, not literal component boundaries. A given piece of logic — for example, omission tracking — may involve heuristic scaffolding, learned verification, and fusion reconciliation. It lives in the components that own each concern and is bound at the Fusion Engine.

The mapping:

* the Structural / Heuristic concern is realized primarily in Ingestion, Document Processing, Entity Resolution, Baseline Maintenance, and Heuristic Analysis
* the Semantic / ML concern is realized primarily in Representation and Learned Analysis
* the Fusion concern is realized in the **Fusion Engine**, a single named component
* the Signal concern is realized in the Signal Store and the Ranking & Surfacing component

The Heuristic Layer and ML Layer (as defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)) are therefore realized as multiple components each. The Fusion Layer concept (DOMAIN_GLOSSARY.md) is realized as a single named component — the **Fusion Engine** — to keep the conceptual layer and its architectural realization distinguishable.

---

## Components

Each component below is described as a responsibility, not a service. Whether a given component runs as a process, a library, a batch job, or a cluster is not decided here.

### 1. Ingestion

**Owns.** Acquiring, attributing, and recording source artifacts. Preserving the raw artifact as received. Attaching source metadata (Source identity, publication time, observation time).

**Does not own.** Parsing or normalization beyond what is needed to preserve the raw artifact. Content interpretation. Deduplication of semantic content.

**Feeds.** Document Processing.

**Consumes.** External sources. Acquisition cadence, licensing, and provider selection are deferred to a future data-acquisition document (not yet created; see the closing summary and this document's open questions).

### 2. Document Processing

**Owns.** Normalizing raw artifacts into canonical text and structure. Segmenting Documents into conceptually meaningful units (for v1 Transcripts: prepared remarks, Q&A, speaker turns). Producing the normalized form that downstream analysis consumes.

**Does not own.** Entity attachment. Semantic interpretation. Signal detection.

**Feeds.** Entity Resolution; Heuristic Analysis; Representation.

*Specific parsing and normalization mechanics are deferred to INGESTION_SPEC.md and DOCUMENT_PROCESSING.md.*

### 3. Entity Resolution

**Owns.** Attaching Documents to the Entity they concern. Maintaining canonical Entity identity across heterogeneous source identifiers. Attaching Speaker identity within a Document. Recording reconciliation confidence where imperfect.

**Does not own.** Analytical state about an Entity (owned by Baseline Maintenance). Cross-Entity semantic comparison.

**Feeds.** Baseline Maintenance; Heuristic Analysis; Representation; Learned Analysis.

### 4. Baseline Maintenance

**Owns.** Maintaining, per-Entity and per-Speaker, the evolving reference state against which deviations are measured. Updating the Baseline as new Documents arrive. Exposing historical Baselines (as-of queries) for temporal comparison. Exposing Baseline thinness as a queryable property.

**Does not own.** Signal detection itself. The Baseline exists to support Signal detection but does not produce Signals.

**Feeds.** Heuristic Analysis; Learned Analysis; Fusion Engine.

*Baseline construction method is deferred to NARRATIVE_ANALYSIS.md and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).*

### 5. Heuristic Analysis

**Owns.** Rule-based features, structural comparisons, omission tracking scaffolding, contradiction detection scaffolding, and other deterministic analyses (CONTEXT §3.2.A, §7). Produces heuristic-layer candidate evidence for the Fusion Engine.

**Does not own.** Learned representations. Final Signal emission. Ranking.

**Feeds.** Fusion Engine.

### 6. Representation

**Owns.** Computing and maintaining semantic representations of financial text: embeddings, narrative similarity, narrative clustering (CONTEXT §5.1). Producing the learned features that downstream Learned Analysis depends on.

**Does not own.** Signal scoring. Baseline maintenance. Heuristic logic.

**Feeds.** Learned Analysis; Baseline Maintenance (as a feature input).

*Model specifics are deferred to MODEL_STRATEGY.md.*

### 7. Learned Analysis

**Owns.** Model-driven analyses that depend on semantic representations: drift detection beyond heuristic thresholds, uncertainty modeling, latent structure detection, communication pattern profiling (CONTEXT §5.2, §5.3). Proposes candidate Signals and, under CONTEXT §5.4, candidate Signal types. Produces learned-layer candidate evidence for the Fusion Engine.

**Does not own.** Rule-based logic. Final Signal emission.

**Feeds.** Fusion Engine.

*Model architectures and training strategy are deferred to MODEL_STRATEGY.md.*

### 8. Fusion Engine

**Owns.** Integrating heuristic-layer and learned-layer candidate evidence into a single, explainable Signal (CONTEXT §3.2.C). Resolving conflicts between rules and learned outputs. Preserving the Basis chain — which rules and which model outputs contributed — on every emitted Signal. Producing Signal-level Confidence that honors CONTEXT §3.4 structured skepticism.

**Does not own.** Raw candidate generation (belongs to Heuristic Analysis and Learned Analysis). Ranking for the user surface. Storage.

**Feeds.** Signal Store.

**Treated as the designated hard design problem per CONTEXT §3.2.C.** The Fusion Engine is the component that realizes the Fusion Layer concept; its resolution mechanics are not defined here. The concerns it must address are enumerated:

* combining heuristic and learned evidence into a single Signal
* resolving conflicts when rules and learned analysis disagree
* preserving Basis — the specific contributions from each side — on every output
* producing Signal-level Confidence that reflects Basis disagreement, Baseline thinness, and Evidence precision
* maintaining traceability across the combination step

The Fusion Engine's upstream contract (with Heuristic Analysis and Learned Analysis) and its downstream contract (with the Signal Store and, through it, Ranking & Surfacing) are the load-bearing surfaces for architectural extensibility. Changes to them are expected to be cautious.

*Specific fusion mechanics — conflict resolution strategy, weighting, Confidence computation — are deferred to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md.*

### 9. Signal Store

**Owns.** Durable, immutable storage of emitted Signals with their Basis, Evidence, and lifecycle state. Maintaining the Signal lifecycle (candidate, surfaced, stale, superseded, retired) as subsequent records with lineage references, not as mutations. Supporting as-of queries.

**Does not own.** Ranking. User-facing presentation. Scoring logic.

**Feeds.** Ranking & Surfacing; API Boundary; Evaluation Harness.

*Signal lifecycle semantics are specified in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). Conceptual data shape of the Signal is in [DATA_MODEL.md](./DATA_MODEL.md). Storage technology and indexing are deferred downstream.*

### 10. Ranking & Surfacing

**Owns.** Producing the user-ordered view of Signals. Applying prioritization policy. Exposing recency, importance, and user-relevance orderings.

**Does not own.** Emission of Signals. Storage of Signals. User interface design. Final decision on what any individual user sees (that is a USER_EXPERIENCE.md concern composed on top of this component's output).

**Feeds.** API Boundary.

*Ranking methodology is deferred to NARRATIVE_ANALYSIS.md and EVALUATION.md.*

### 11. Evidence & Provenance Store

**Owns.** Immutable, span-level references from any derived artifact (features, candidate evidence, Signals) back to source text. Stores DerivationRun records. This is the traceability substrate.

**Does not own.** Derived analysis itself. Signals. User presentation.

The Evidence & Provenance Store is cross-cutting. Every component that produces derived data writes provenance here, rather than passing it along the pipeline as a payload.

### 12. Evaluation Harness

**Owns.** Sampling Signals and Candidate Signals for human review, recording reviewer feedback, and producing evaluation artifacts aligned with CONTEXT §14. Also executes the review workflow for Candidate Signal types drawn from the Candidate-Type Pool (CONTEXT §5.4 and user-confirmed policy that unsupervised discovery may propose types). The Candidate-Type Pool itself is defined in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); the review mechanics are owned by EVALUATION.md.

**Does not own.** Ranking policy. Model training. Signal emission. Live production-path decisions.

*Specific evaluation methodology is deferred to EVALUATION.md. Experimentation methodology is deferred to EXPERIMENTATION.md.*

### 13. Query & Retrieval Surface

**Owns.** Query access to the Signal Store, the Evidence & Provenance Store, and historical temporal state (Baselines, NarrativeState). Supports as-of queries across historical state.

**Does not own.** The API surface itself. Storage technology choices.

*Retrieval mechanics are deferred to SEARCH_AND_RETRIEVAL.md.*

### 14. API Boundary

**Owns.** The external contract of the system. Authentication, request validation, response shape.

**Does not own.** Business logic. User interface. Storage.

*Specific API surface is deferred to API_SPEC.md.*

---

## Document Travel: Source To Signal

A single earnings call transcript travels through the system roughly as follows. The narrative is directional; components may exchange further information through the Baseline and the Evidence & Provenance Store.

* **Ingestion** records the raw artifact and source metadata.
* **Document Processing** normalizes and segments the artifact into canonical text units.
* **Entity Resolution** attaches the canonical Entity and resolves Speakers within the Document.
* **Heuristic Analysis** extracts rule-based features; **Representation** computes learned features. These may proceed in parallel.
* **Baseline Maintenance** exposes the prior Baseline for comparison and updates the Baseline with the new observation.
* **Heuristic Analysis** and **Learned Analysis** each produce candidate evidence relative to the prior Baseline.
* The **Fusion Engine** integrates candidate evidence into emitted Signals with preserved Basis.
* The **Signal Store** records the Signals immutably; the **Evidence & Provenance Store** carries the span-level trace back to the original text.
* **Ranking & Surfacing** produces user-ordered views on demand, via the **API Boundary** and **Query & Retrieval Surface**.
* **Evaluation Harness** samples Signals (and candidate Signals) for human review without blocking the flow.

The flow is described at rest. Whether it runs synchronously per Document, in batch, or as an event-driven pipeline is deferred to EVENTS_AND_PIPELINES.md and downstream infrastructure work.

---

## Cross-Cutting Concerns

### Traceability And Explainability

Every component that produces derived data writes provenance to the Evidence & Provenance Store. Every Signal carries a Basis chain: which rules contributed, which model outputs contributed, and which source Spans support each. This is not a presentation feature; it is a system-wide invariant (CONTEXT §3.3).

User-facing surfaces may present a subset of this chain; that decision belongs to USER_EXPERIENCE.md. The chain itself exists independent of how it is shown.

### Temporal Reasoning

Temporal reasoning is realized at the architectural level through:

* immutable historical records in the Signal Store, the Evidence & Provenance Store, and the raw ingestion store
* versioned Baselines exposed by Baseline Maintenance, supporting as-of reconstruction
* explicit temporal metadata on every Document (event time, document time, observation time)
* query support for "what did the narrative look like as of date X" via the Query & Retrieval Surface
* emission time and lineage on every Signal, supporting reconstruction of what the system believed at any past point

Detailed temporal semantics are specified in [DATA_MODEL.md](./DATA_MODEL.md).

### Extensibility

The system is extensible along three axes:

* **new Document types** — by adding parsers and normalization paths in Document Processing without altering downstream components
* **new Signal types** — by emitting a new type through the Fusion Engine; the extension pattern is defined in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and includes both research-driven and discovery-driven paths
* **new analytical modules** — heuristic or learned — by attaching them as feature contributors to the Fusion Engine without altering the Fusion Engine's contract

The Fusion Engine's contract is therefore load-bearing for extensibility. Changes to it are expected to be cautious and reviewed.

### Replaceability

Each component has a single responsibility and bounded upstream and downstream contracts. Replacing a component — for example, swapping a Learned Analysis module — is expected to be bounded to that component. This is a design attitude, not a mechanism; enforcement is a concern for CODE_STANDARDS.md and TESTING_STRATEGY.md.

### Model Ownership Posture

CONTEXT §6 commits the system to in-house models with no external LLM API in critical paths. Structurally this means:

* Representation and Learned Analysis are internal components, not API clients
* any optional use of local small-footprint language models (CONTEXT §6.2) is in-process or on-infrastructure, not remote
* the system must remain functional if external model providers are unavailable
* nothing in the critical path requires network access to third-party model providers

Non-critical-path uses of external models (for example, offline research or evaluation tooling) are not forbidden by this architecture, but any such use must be clearly out of the critical path and is outside this document's scope to authorize.

### Operating Posture

Per [ASSUMPTIONS.md](./ASSUMPTIONS.md) T2, T3, and U2, v1 operates as a deliberate, batch-oriented or on-demand system rather than a real-time stream. The system is not optimized for instantaneous response; it is optimized for careful, explainable analysis.

*Specific operating mode is deferred to EVENTS_AND_PIPELINES.md and downstream infrastructure work.*

### Low-Capital Constraint

V1 operates under explicit low-capital constraints. The preference for small, specialized models (CONTEXT §6.2) is inherited here and amplified by ASSUMPTIONS H5 and the user-confirmed individual-user, low-capital posture. Architectural consequences:

* components are designed so that inference cost scales with ingested volume, not with continuous background computation
* re-derivation is supported but not required to be precomputed; materialization is a downstream storage concern
* cross-component communication assumes moderate volume; high-throughput streaming is out of scope
* any feature that meaningfully multiplies infrastructure cost without clear signal-quality gain is out of scope

### Thin-History Handling

Per user confirmation on ASSUMPTIONS E1, the system prefers reliability over coverage for Entities with limited historical depth. Architecturally:

* Baseline Maintenance exposes Baseline thinness as a queryable property, not a hidden state
* the Fusion Engine is expected to incorporate Baseline thinness into Signal Confidence
* Ranking & Surfacing may apply policy that withholds or downweights thin-history Signals

*Specific thin-history policy is defined in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); the architecture exposes the inputs needed for that policy to operate.*

---

## Component Responsibility Matrix

A compact summary of ownership. For details, see each component's section above.

* Ingestion — acquire and attribute raw artifacts
* Document Processing — normalize and segment
* Entity Resolution — canonical Entity and Speaker identity
* Baseline Maintenance — evolving reference state per Entity and Speaker
* Heuristic Analysis — rule-based features and candidate evidence
* Representation — learned semantic representations
* Learned Analysis — learned candidate evidence; candidate Signal-type proposals
* Fusion Engine — integration of candidate evidence into Signals (the designated hard problem)
* Signal Store — durable, immutable Signals with lifecycle
* Ranking & Surfacing — prioritized views of Signals
* Evidence & Provenance Store — span-level traceability substrate
* Evaluation Harness — human review sampling, recording, candidate-type review
* Query & Retrieval Surface — as-of and ad hoc access
* API Boundary — external contract

---

## Deferred Decisions

Decisions adjacent to this document that are not made here, with named owners:

* deployment topology, scaling, environments — downstream infrastructure work (interacting with OBSERVABILITY.md)
* ingestion parsing specifics — INGESTION_SPEC.md
* document normalization and segmentation rules — DOCUMENT_PROCESSING.md
* event transport, pipeline orchestration, batch vs. streaming mode — EVENTS_AND_PIPELINES.md
* retrieval and query patterns — SEARCH_AND_RETRIEVAL.md
* conceptual data schema — [DATA_MODEL.md](./DATA_MODEL.md)
* model architectures, training, and inference — MODEL_STRATEGY.md
* fusion mechanics — MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md
* Signal internals and lifecycle details — [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
* ranking and prioritization policy — NARRATIVE_ANALYSIS.md and EVALUATION.md
* API surface — API_SPEC.md
* presentation — USER_EXPERIENCE.md
* observability — OBSERVABILITY.md
* failure modes — FAILURE_MODES.md
* testing strategy — TESTING_STRATEGY.md
* evaluation methodology — EVALUATION.md
* experimentation — EXPERIMENTATION.md
* ethics and limitations — ETHICS_AND_LIMITATIONS.md
* security and privacy — SECURITY_AND_PRIVACY.md
* data acquisition strategy — a future dedicated document (not yet created; recommended in the closing summary)
* data governance and retention — DATA_GOVERNANCE.md

---

## Open Structural Questions

Unresolved at this stage. Flagged here so downstream decisions do not silently assume a position.

* how the Fusion Engine exposes its internal conflict-resolution state to the Evaluation Harness — partly an EVALUATION.md concern, partly a fusion-internals concern owned by MODEL_STRATEGY.md
* how Baselines are versioned when the Baseline construction method itself changes — both a [DATA_MODEL.md](./DATA_MODEL.md) concern and a NARRATIVE_ANALYSIS.md concern
* how the Fusion Engine integrates the Candidate-Type Pool from Learned Analysis (CONTEXT §5.4) — the pool's state machine is owned by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and its review workflow by EVALUATION.md; flagged here because it interacts with the Fusion Engine's extensibility contract
* how re-derivation is scheduled and throttled under the low-capital constraint — downstream infrastructure concern, flagged because it affects the re-derivability invariant

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes their commitments structurally.
* [VISION.md](./VISION.md) sets the orientation; this document does not relitigate it.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies the beliefs this architecture depends on.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the entities this architecture's components read and write.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the Signal contract the Fusion Engine and Signal Store share.
* [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) remains deferred; nothing here pre-decides presentation.
