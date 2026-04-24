# DATA_MODEL.md

## Purpose Of This Document

DATA_MODEL.md defines the conceptual data model the system reasons over: the core entities, their identities, the relationships between them, how time is represented, how evidence provenance is preserved, and how derivation layers relate.

This is a conceptual schema. It makes no decisions about storage technology, indexing, physical schema, or serialization.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Ownership of the components that produce and consume artifacts described here is defined in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## How To Read This Document

* entities are described by what they represent, not by how they are stored
* each entity has a clear identity model and a clear temporal model
* relationships are named between entities, not between tables
* derivation layers describe how raw inputs become Signals, not how bytes move
* every derived artifact ultimately traces back to source Spans

---

## Guiding Principles For The Data Model

* raw source artifacts are immutable once ingested
* derived data is re-derivable from raw sources plus versioned derivation logic
* every derived artifact carries provenance to the source Spans that support it
* temporal reasoning is a first-class property; the system can reconstruct prior states
* identity is reconciled, not assumed; canonical identity is a project-owned concept
* the model is extensible to new Entity classes and new Document subtypes without restructuring existing ones
* v1 elaboration is bounded to earnings call transcripts (CONTEXT §8); other domains are structural extensions, not rewrites

---

## Core Entities

Each entity below is described by: what it represents, its identity model, its temporal model, and its key relationships. No field-level schema is given; that belongs to Wave 2.

### Entity

**Represents.** The subject of a financial narrative. In v1, typically a public company. In later domains, may include industries, issuers, or other canonical subjects.

**Identity.** A project-owned canonical identifier, reconciled from external identifiers (ticker, legal name, registry IDs). External identifiers are preserved alongside the canonical ID; the canonical ID is the stable reference across Documents and time.

**Temporal model.** Entities have a lifespan (e.g. from incorporation to dissolution) but are generally stable across the analytical horizon. Attributes that change over time (industry classification, name changes, corporate actions) are tracked as versioned facts rather than mutated in place.

**Relationships.** Documents concern an Entity. Speakers are associated with an Entity. Baselines are maintained per Entity. Signals name a subject Entity.

### Source

**Represents.** The origin of a Document — a specific publisher, filing channel, transcript provider, or equivalent.

**Identity.** A project-owned Source identifier. Multiple aliases for the same Source are reconciled to a canonical ID.

**Temporal model.** Sources have creation and (possible) deprecation timestamps. Source characteristics that change over time are tracked as versioned facts.

**Relationships.** Every Document has a Source. Cross-source analysis (CONTEXT §11) depends on Source identity being stable.

### Document

**Represents.** A single ingested textual artifact. The unit of ingestion.

**Identity.** A stable project-owned identifier plus a Source identifier plus a Source-native identifier when the Source provides one. Duplicate detection is a Document Processing concern; this model assumes a stable project-owned identifier has been assigned by Ingestion.

**Temporal model.** Three timestamps are mandatory:

* **event time** — what the Document is about (for a Transcript, the call time; for a filing, the period covered)
* **document time** — when the Document was published or finalized by the Source
* **observation time** — when the system ingested the Document

Event time and document time may be distinct; in Transcripts they are typically close but not identical.

**Relationships.** A Document belongs to a Source and concerns an Entity. A Document contains Segments and Utterances (for subtypes where those apply). A Document is referenced by derived artifacts via the Evidence & Provenance Store.

**Extensibility.** Document is a base concept; specific Document types (Transcript, Filing, Press Release, News Article) extend it with type-specific structure. In v1 only the Transcript subtype is elaborated.

### Transcript (v1 Document subtype)

**Represents.** An earnings call transcript (CONTEXT §8).

**Identity.** Inherits from Document. Additionally associated with a fiscal period.

**Structure.** Contains a sequence of Segments (for example, prepared remarks, Q&A) and a sequence of Utterances, each attributed to a Speaker.

**Extensibility.** Additional Document subtypes are added without altering Transcript.

### Segment

**Represents.** A structurally meaningful region of a Document — for a Transcript, sections such as prepared remarks or Q&A.

**Identity.** A Document-scoped identifier plus an ordinal and a type label.

**Temporal model.** Segments inherit the Document's temporal metadata. No separate temporal identity.

### Utterance

**Represents.** A single speaker turn within a Transcript.

**Identity.** A Document-scoped identifier plus an ordinal.

**Relationships.** Belongs to a Segment. Attributed to a Speaker.

**Span.** An Utterance is itself a Span (see below) and is the default locus for evidence citations in Transcripts.

### Speaker

**Represents.** An individual whose statements are attributed within a Transcript (CONTEXT §5.3).

**Identity.** A project-owned canonical Speaker identifier, reconciled from within-document names and roles, and stable across Documents. Reconciliation imperfections are recorded rather than hidden.

**Temporal model.** Speakers have roles that change over time (a CFO who departs, a CEO appointed mid-year). Roles are versioned facts.

**Relationships.** Associated with an Entity. Attributed on Utterances. Baselines may be maintained per Speaker.

### Span

**Represents.** The primitive unit of evidence: a locus within a Document's normalized text (or equivalent for non-textual extensions), identified with sufficient precision to be unambiguously re-resolved.

**Identity.** Document identifier plus a locus description. Locus precision is source-type appropriate: for a Transcript, Spans are at least Utterance-bounded and may be finer (character offsets within an Utterance); for future Document types, span precision is specified when those types are added.

**Temporal model.** A Span's time is the Document's event time unless the Document itself establishes finer-grained temporal structure.

**Relationships.** Every Evidence record references one or more Spans. Every Signal references Evidence, which references Spans.

### Theme

**Represents.** A recurring topic, concept, or strategic emphasis the system tracks across a narrative over time.

**Identity.** A project-owned identifier. Themes may be human-curated, discovered by heuristic rules, or proposed by unsupervised learned analysis (CONTEXT §5.4). Theme identity is stable across Documents once established.

**Temporal model.** Themes have a creation time and may be retired. Theme prominence for an Entity varies over time.

**Relationships.** ThemeInstances bind Themes to Documents.

*Theme curation and promotion workflow is deferred to NARRATIVE_ANALYSIS.md.*

### ThemeInstance

**Represents.** An occurrence of a Theme within a Document. The unit that supports omission tracking, narrative drift, and similar comparisons.

**Identity.** Theme identifier plus Document identifier plus intra-document locus (Spans).

**Temporal model.** Inherits from the Document.

**Relationships.** References the Theme, the Document, and one or more Spans.

### Baseline

**Represents.** The evolving reference state for an Entity (and, where relevant, a Speaker) against which deviations are measured. A Baseline summarizes the patterns expected for the subject at a given point in time. Baseline thinness — the sufficiency of the underlying history — is a queryable property of the Baseline.

**Identity.** Entity identifier (or Entity + Speaker) plus a valid-time interval.

**Temporal model.** Baselines have explicit valid-time. A historical Baseline can be retrieved as-of any past date. When the Baseline construction method changes, older Baselines are retained; the new method produces a new valid-time series.

**Relationships.** Signals of the types Narrative Drift, Confidence Shift, and Structural Anomaly reference the Baseline(s) against which they were computed.

*Baseline construction method is deferred to NARRATIVE_ANALYSIS.md and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).*

### NarrativeState

**Represents.** A point-in-time snapshot of an Entity's narrative, suitable for reconstructing "what did the narrative look like as of date X". Aggregates recent Documents, Themes, and relevant Baselines for that Entity.

**Identity.** Entity identifier plus effective time.

**Temporal model.** Materialization strategy is a storage concern deferred to downstream infrastructure work. Conceptually, NarrativeState is queryable as-of any past effective time.

**Relationships.** Derived from Documents, ThemeInstances, and Baselines.

### Evidence

**Represents.** The linkage between a derived artifact and the Spans supporting it. The atomic unit of traceability (CONTEXT §3.3).

**Identity.** A project-owned identifier. Bound to the derived artifact that references it.

**Temporal model.** Inherits from the Spans it references.

**Relationships.** References one or more Spans. Referenced by Signals and by intermediate derived artifacts (heuristic features, learned features, candidate evidence).

### Signal

**Represents.** The final output of the system: a meaningful, explainable deviation or pattern in financial narrative structure over time (Signal, [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)).

**Identity.** A project-owned identifier. Immutable once emitted.

**Temporal model.** A Signal has:

* **subject time** — the event time or time range the Signal describes
* **emission time** — when the Signal was produced
* **lifecycle state** — see [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)

Lifecycle transitions (stale, superseded, retired) are expressed as subsequent Signal records with lineage references, not as mutations of the original.

**Relationships.** References an Entity (the subject), zero or more Speakers (if type-relevant), one or more Evidence records, and its Basis (below).

*Detailed Signal anatomy lives in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); this section specifies only what the data model must represent.*

### Basis

**Represents.** The chain of contributions that produced a Signal — which heuristic rules fired, which learned outputs contributed, and how the Fusion Engine combined them.

**Identity.** Bound to a Signal; not independently referenced.

**Relationships.** References the heuristic features and learned features used. References a fusion-run identifier that captures the Fusion Engine's DerivationRun at emission time.

**Why separated.** Explainability (CONTEXT §3.3) requires reconstructing how a Signal was produced, not only what text supported it. Basis is the structural home for that reconstruction.

### DerivationRun

**Represents.** A named, versioned instance of a derivation process (normalization, feature extraction, learned analysis, fusion). Every derived artifact references the DerivationRun that produced it.

**Identity.** A project-owned identifier plus a logical name plus a version.

**Temporal model.** DerivationRuns have a creation time and are immutable. Re-derivation under new logic produces a new DerivationRun.

**Relationships.** Referenced by all derived artifacts. A Signal's Basis references DerivationRuns for both heuristic and learned contributions and for the fusion step.

---

## Identity Model

The system uses three kinds of identifiers.

* **Native identifiers** — whatever the external world uses (ticker, legal name, Source-native Document ID, Speaker name as spoken).
* **Canonical identifiers** — project-owned, stable references for Entities, Sources, Speakers, Themes, Documents, Signals, and other artifacts requiring stable reference.
* **Locus identifiers** — for Spans, a structured description sufficient to re-resolve the locus within the Document's normalized form.

Reconciliation from Native to Canonical is a deliberate operation with failure modes. The data model records reconciliation confidence where imperfect, rather than asserting canonical identity silently.

---

## Temporal Model

The system distinguishes several kinds of time. Each derived artifact records the kinds relevant to it.

* **Event time** — when the phenomenon being described occurred (the call, the period reported, the announcement).
* **Document time** — when the Document was published or finalized by the Source.
* **Observation time** — when the system ingested the Document.
* **Processing time** — when a derived artifact was produced.
* **Valid time** — for artifacts with a validity interval (notably Baselines and versioned facts), the interval over which the artifact applies.
* **Emission time** — for Signals, the time the Signal was emitted.
* **Effective time** — for queries, the time at which the caller wants the system's state reconstructed.

The data model supports:

* **as-of queries** — reconstructing the state of Baselines, NarrativeState, and emitted Signals as of any past effective time
* **temporal integrity** — no derived artifact depends on information that did not exist at its processing time, except by explicit retroactive annotation that is itself a new DerivationRun

---

## Derivation Layers

Derived data is organized into conceptual layers. Each layer may be re-derived from lower layers plus versioned logic. Every layer has a clearly named owner in [ARCHITECTURE.md](./ARCHITECTURE.md).

* **Raw** — the source artifact as received. Immutable. Owned by Ingestion.
* **Normalized** — canonical text and structure. Re-derivable from Raw plus the Document Processing DerivationRun. Owned by Document Processing.
* **Enriched** — Entity and Speaker attribution, Segment and Utterance tagging, ThemeInstances. Re-derivable from Normalized plus the appropriate enrichment DerivationRuns. Ownership is shared across Entity Resolution and those parts of Heuristic Analysis and Learned Analysis that produce enrichments.
* **Analytical** — heuristic features, learned features, Baselines, comparisons. Re-derivable from Enriched plus the respective DerivationRuns. Ownership is shared across Heuristic Analysis, Representation, Learned Analysis, and Baseline Maintenance.
* **Signal** — emitted Signals with Basis and Evidence. Re-derivable from Analytical plus the Fusion Engine's DerivationRun. Owned by the Fusion Engine and the Signal Store.

Layer boundaries are not rigid: a ThemeInstance is both Enriched (it tags a Document) and Analytical (it is derived by heuristic or learned analysis). The layers describe a direction of dependency, not a strict partition.

Every derived artifact names the DerivationRun that produced it. Re-derivation on demand is a property of the model; whether derivations are materialized or computed on the fly is a storage concern deferred downstream.

---

## Immutability And History

The following hold:

* Raw artifacts are immutable.
* Normalized artifacts are immutable given a specific Normalization DerivationRun; re-normalization produces new Normalized artifacts rather than mutating.
* Analytical artifacts are immutable given their DerivationRun.
* Signals are immutable once emitted. Lifecycle transitions (see [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) are expressed as new Signal records with lineage references to prior Signals.
* Baselines are immutable per valid-time interval; updates produce new valid-time intervals.
* Canonical Entity, Source, and Speaker identities are mutable in that their attributes change over time, but those changes are stored as versioned facts, not in-place edits.

History is reconstructible by replaying immutable artifacts under the appropriate DerivationRuns.

---

## Evidence Provenance And Traceability

Every derived artifact — feature, candidate evidence, Signal — references Evidence, which references one or more Spans. The chain is:

Signal → Basis (DerivationRuns) → Candidate Evidence → Features → Evidence → Spans → Document → Raw.

No artifact may be emitted without its position in this chain being resolvable. This is the substrate for CONTEXT §3.3 explainability.

Span precision is source-type appropriate. For Transcripts, Spans are at least Utterance-bounded and may be finer (character offsets within an Utterance). For future Document types, span precision is specified when those types are added.

---

## Entity-Centric Orientation

The analytical orientation of the system is centered on the Entity. This has concrete data-model consequences:

* every Document is reconciled to an Entity (or flagged as unreconciled)
* Baselines and NarrativeStates are Entity-scoped (and optionally Speaker-scoped within an Entity)
* Signals name a subject Entity
* cross-Entity analysis (industry-wide, macro) is possible but is deferred as a v2+ concern (SCOPE Deferred)

An Entity with insufficient historical depth is a first-class concern, not an error case. Policies for Signal behavior on thin-history Entities are owned by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and NARRATIVE_ANALYSIS.md. This document ensures the data model can represent "Entity known, history thin" as a queryable state rather than as missing data. Baseline thinness is accordingly a property exposed on the Baseline, not an inference the consumer must make.

---

## Extensibility

The model extends along known axes:

* **new Document subtypes** — add a subtype of Document with type-specific structure (analogous to Transcript) without altering the base Document's identity or temporal model
* **new Entity classes** — add canonical identifier scheme and versioned-facts pattern for the new class; Document-to-Entity reconciliation extends naturally
* **new Sources** — add a Source record and, if needed, a Document subtype for its artifacts
* **new Theme provenance** — Themes may be human-curated, heuristic, or learned; the identity model does not care which produced them
* **new derived artifacts** — register a DerivationRun and emit artifacts that reference Evidence and Spans

Extensions are additive. The existing model does not change shape; new concepts attach to it.

---

## What This Document Does Not Specify

* storage technology, physical schema, indexing, or sharding — deferred to downstream infrastructure work
* ingestion parser specifics — INGESTION_SPEC.md
* normalization and segmentation rules — DOCUMENT_PROCESSING.md
* retrieval and query patterns — SEARCH_AND_RETRIEVAL.md
* retention, deletion, and governance policy — DATA_GOVERNANCE.md
* serialization and API payload shapes — API_SPEC.md
* Baseline construction method — NARRATIVE_ANALYSIS.md and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
* Theme curation and promotion — NARRATIVE_ANALYSIS.md
* thin-history policy semantics — [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and NARRATIVE_ANALYSIS.md

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [VISION.md](./VISION.md) and [ASSUMPTIONS.md](./ASSUMPTIONS.md) bound the posture.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary.
* [ARCHITECTURE.md](./ARCHITECTURE.md) owns the components that read and write the artifacts described here; every derivation layer has a clear component owner in its Component Responsibility Matrix.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) owns the internal anatomy and lifecycle of Signals; this document specifies only what the data model must represent about them.
