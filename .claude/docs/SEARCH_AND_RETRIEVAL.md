# SEARCH_AND_RETRIEVAL.md

## Purpose Of This Document

SEARCH_AND_RETRIEVAL.md specifies the conceptual contract of the Query & Retrieval Surface ([ARCHITECTURE.md](./ARCHITECTURE.md) §13): the query patterns the system supports internally, the as-of semantics across derivation layers, the v1 scope of semantic search, and the consistency guarantees these queries uphold against the immutability posture of [DATA_MODEL.md](./DATA_MODEL.md).

The Query & Retrieval Surface is strictly internal. Its consumers are the API Boundary ([ARCHITECTURE.md](./ARCHITECTURE.md) §14), the Ranking & Surfacing component, the Evaluation Harness, and other internal analytical processes. External callers reach it only through the API Boundary, under API_SPEC.md's contract.

This document is conceptual. It does not select a search engine, an index technology, a query language, or a serialization format. It defines the patterns and semantics any realization must honor.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* query patterns are described by what they let the caller ask, not by how they are executed
* as-of semantics are described once and then referenced; every query that returns historical state inherits them
* semantic search is scoped explicitly to what v1 supports; broader semantic search is flagged as deferred
* the boundary with API_SPEC.md is the last section, stated plainly

---

## Guiding Commitments

Inherited and held as invariants:

* every retrieval is consistent with the immutability posture (DATA_MODEL.md §Immutability And History) — retrievals return records, not mutable projections
* temporal reasoning is a first-class capability (CONTEXT §11, §3; DATA_MODEL.md §Temporal Model) — as-of query support is required, not optional
* explainability and traceability are preserved through retrieval (CONTEXT §3.3) — Signals retrieved carry their Basis and Evidence chains
* low-capital constraint ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5) bounds the ambition of v1 retrieval; not every conceivable query is supported in v1
* the Query & Retrieval Surface does not own the external contract; that is the API Boundary's job

---

## Boundary Against API_SPEC.md

The Query & Retrieval Surface is the internal query surface of the system. It exposes queries to internal callers — the API Boundary, Ranking & Surfacing, the Evaluation Harness, operator tooling, and analytical processes that need historical state.

API_SPEC.md owns the external contract. It decides which queries are exposed to external callers, under what authentication, with what shape, and with what rate limits. API_SPEC.md composes the external surface on top of the internal surface this document defines.

The two boundaries are not symmetric: every external query must be expressible against the internal surface, but not every internal query is exposed externally. Internal-only queries include operator-scoped historical replays, Pipeline Version introspection, and quality-monitoring reads.

This boundary is held as a cross-document invariant with API_SPEC.md.

---

## Subjects Of Retrieval

The Query & Retrieval Surface supports retrieval over the following classes of artifact. Each class has its own query patterns; the patterns are described in the next section.

* **Documents** (Raw and Normalized; DATA_MODEL.md §Document, §Transcript)
* **Segments and Utterances** (DATA_MODEL.md §Segment, §Utterance)
* **Spans and Evidence** (DATA_MODEL.md §Span, §Evidence)
* **Entities, Speakers, and Sources** (DATA_MODEL.md §Entity, §Speaker, §Source)
* **Themes and ThemeInstances** (DATA_MODEL.md §Theme, §ThemeInstance)
* **Baselines** (DATA_MODEL.md §Baseline)
* **NarrativeState** (DATA_MODEL.md §NarrativeState)
* **Signals** (DATA_MODEL.md §Signal; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
* **DerivationRuns and Pipeline Versions** (DATA_MODEL.md §DerivationRun; [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) Pipeline Versioning)

Retrieval is read-only. No query writes or mutates.

---

## Query Patterns

Patterns are described by what they let a caller ask. Specific query shape, parameter syntax, and pagination are deferred.

### Document Queries

* by canonical Document identifier
* by Source plus Source-native identifier
* by Entity over a temporal range of Event Time or Document Time
* by Source over a temporal range
* by ingestion state (committed, quarantined, superseded)
* by Pipeline Version under which the Document's current default Normalized artifact was produced

Document queries may request specific Normalized artifact versions (not only the default), identified by DerivationRun or by Pipeline Version.

### Segment And Utterance Queries

* by Document, returning Segments in order
* by Document and Segment, returning Utterances in order
* by Entity, Speaker, and temporal range, returning Utterances across Documents
* by Segment type (for example, all Q&A Segments across an Entity's Documents over time)

Utterance queries may filter on within-Document Speaker handle or canonical Speaker (after Entity Resolution has reconciled).

### Span And Evidence Queries

* by Span identifier, returning the Normalized text locus and the corresponding Raw locus via the locus map
* by Evidence identifier, returning referenced Spans and the derived artifact that the Evidence supports
* by Document, returning all Evidence records citing Spans in that Document
* by Entity over a temporal range, returning Evidence records that support derived artifacts concerning the Entity in that range

### Entity, Speaker, And Source Queries

* by canonical identifier
* by native identifier (ticker, legal name, Source-native ID, Speaker name)
* by ancillary properties tracked as versioned facts (industry classification for Entities, role for Speakers, channel for Sources)

Reconciliation-confidence filtering is supported: callers may require canonical identifiers whose reconciliation confidence meets a threshold.

### Theme And ThemeInstance Queries

* by Theme identifier
* by Entity plus temporal range, returning ThemeInstances in temporal order
* by Document, returning ThemeInstances within that Document

Theme prominence over time for an Entity is a query, not a materialized artifact; the Query & Retrieval Surface exposes the underlying ThemeInstances, and the caller (analytical component, Ranking & Surfacing) composes prominence from them. Materialization may happen downstream as a performance concern, but the conceptual shape is query-driven.

### Baseline Queries

* by Entity (and optionally Speaker)
* by Entity (and Speaker) plus Effective Time, returning the Baseline valid at that time
* by Entity (and Speaker) plus valid-time range, returning the sequence of Baselines over that range
* by Baseline thinness — callers may filter to thin or non-thin Baselines for a given Entity population

Baseline queries are central to as-of semantics and are described further below.

### NarrativeState Queries

* by Entity and Effective Time, returning a reconstructed NarrativeState
* by Entity and Effective Time range, returning a sequence of reconstructed NarrativeStates (conceptually; materialization is deferred)

NarrativeState is a queryable reconstruction, not a stored artifact, unless [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) and downstream infrastructure opt to materialize it for performance.

### Signal Queries

* by canonical Signal identifier
* by Entity, temporal range of Subject Time, and Signal type
* by Entity and Emission Time range
* by Signal lifecycle state (candidate, surfaced, stale, superseded, retired)
* by Signal Basis properties — which heuristic rules contributed, which learned analyses contributed
* by Signal Strength band or Confidence band (representation of these is deferred per [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); the query dimension is committed here)
* by Evidence properties — Signals citing a specific Span, Document, or Theme

Signal queries always return the Basis chain and the Evidence chain as part of the result; a Signal without its traceability chain is not a valid return.

### DerivationRun And Pipeline Version Queries

* by DerivationRun identifier
* by DerivationRun logical name and version
* by Pipeline Version identifier
* by the Pipeline Version an artifact was produced under

These queries are expected to be used heavily by the Evaluation Harness, operator tooling, and the Ranking & Surfacing component when reasoning about pipeline state; they are exposed minimally through the external API Boundary.

---

## As-Of Semantics

The Query & Retrieval Surface realizes the temporal model of DATA_MODEL.md §Temporal Model by supporting as-of queries across derivation layers.

### Effective Time

An as-of query specifies an Effective Time (DATA_MODEL.md §Temporal Model): the time at which the caller wants the system's state reconstructed. Given an Effective Time, the query returns the state of the requested artifact class as known to the system at that time.

### As-Of Across Layers

* **Raw** — Raw artifacts are immutable and do not change once landed; as-of queries at the Raw layer are filters on Observation Time
* **Normalized** — as-of queries may return the Normalized artifact whose DerivationRun was current at the Effective Time, or any version explicitly identified
* **Enriched** — as-of queries return Enrichment artifacts produced by DerivationRuns current at the Effective Time
* **Analytical** — Baselines are explicitly valid-time-versioned; other Analytical artifacts are queried by Processing Time or by DerivationRun version
* **Signal** — as-of queries return Signals whose Emission Time precedes the Effective Time; lifecycle state is reconstructed as of the Effective Time (a Signal that was Surfaced at the Effective Time but was later retired appears as Surfaced under an as-of query at that Effective Time)

As-of queries never invent state. They return the state as recorded, not an imputation of what state "should have been."

### Readjusted Views

Because re-derivation under new Pipeline Versions produces parallel artifacts rather than overwriting, a caller may ask "what would the Signal have been at Effective Time T under Pipeline Version V?" — a different question from "what was the Signal at Effective Time T?"

Both are supported. Pipeline Version is a parameter to as-of queries; when unspecified, the query returns the state under the Pipeline Version that was current at the Effective Time.

### Interaction With Ingestion Lineage

A Document that was updated (a superseded prior, a corrective republish) is returned as-of its Effective Time according to its ingestion lineage: the Document that was the active default at the Effective Time is what as-of queries return, even if a subsequent update has superseded it.

---

## Semantic Search Scope For V1

Semantic search — retrieval based on meaning rather than exact match — is scoped tightly in v1, reflecting the low-capital posture and the deliberate orientation.

### In Scope For V1

* **Utterance-level semantic retrieval** over learned representations (embeddings) produced by Representation ([ARCHITECTURE.md](./ARCHITECTURE.md) §6), scoped to an Entity, a temporal range, or both — intended for analysts and analytical components looking for similar Utterances across an Entity's history
* **Segment-level semantic retrieval** over the same representations, aggregated at the Segment level, scoped to an Entity — intended for narrative-similarity queries

Semantic retrieval returns Spans or Utterances as results, along with a similarity indication. The specific similarity representation (score, rank, band) is a [SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md) concern deferred to downstream implementation.

### Out Of Scope For V1

* **cross-layer semantic search** — for example, semantic search over Analytical artifacts or over Signals themselves — deferred; its utility is uncertain and its cost is high
* **free-text search over arbitrary natural-language queries** against the entire corpus — deferred; v1 retrieval assumes structured queries with semantic-similarity components, not free-form natural-language interrogation
* **generative retrieval** — retrieval that synthesizes an answer rather than returning stored artifacts — excluded by construction; the system does not generate Signals or Commentary on the retrieval path, and CONTEXT §3.3 requires outputs to be stored, traceable artifacts
* **semantic search that invokes an external large-language-model API** — excluded by CONTEXT §6.1 in critical paths

V1 semantic retrieval is a query over precomputed embeddings, not a runtime-model invocation.

### Interaction With Representation

Semantic retrieval depends on Representation's outputs. A change to Representation's DerivationRun may change which embeddings are current; semantic retrieval honors Pipeline Version in the same way other as-of queries do.

---

## Consistency With Immutability

Every query returns immutable records. The records a caller receives today are the records they will receive tomorrow if the query is restated with the same Effective Time and the same Pipeline Version.

A caller who restates an as-of query with a *later* Effective Time may receive different records, because more artifacts have been observed or emitted in the interim. This is not an inconsistency; it is what as-of semantics mean.

Lifecycle transitions (a Signal moving from Candidate to Surfaced, or from Surfaced to Retired) do not mutate the original Signal record. As-of queries return the lifecycle state reconstructed for the Effective Time by reading lifecycle-transition records with their own timestamps (DATA_MODEL.md §Immutability And History; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Lifecycle).

---

## Access Interfaces

The Query & Retrieval Surface exposes query patterns to internal callers. The access interface is conceptual:

* a request identifies the subject class (Document, Signal, Baseline, NarrativeState, and so on), the query pattern, and the parameters (identifiers, temporal range, Effective Time, Pipeline Version, filters)
* a response returns records of the subject class and a provenance reference sufficient to locate the Evidence & Provenance Store entries that support each record
* every response includes enough metadata for the caller to determine which Pipeline Version the records were produced under and which DerivationRuns contributed

Specific transport, serialization, authentication, rate limiting, and pagination are all deferred. The interface here is a contract about what a response contains, not a specification of a protocol.

---

## Pagination, Limits, And Long-Range Queries

Retrieval at scale is bounded. The Query & Retrieval Surface commits to:

* stable pagination over temporal-range queries — a paginated result set reflects a consistent snapshot, not a moving window
* explicit limits on result-set size — a caller who requests an unbounded temporal range receives a bounded page plus a continuation reference
* rate limits applied at the access interface — their specific numbers are deferred to downstream infrastructure work

These are conceptual commitments, not specific mechanisms. Specific pagination scheme, limit values, and rate-limit enforcement are deferred.

---

## Interaction With Ranking & Surfacing

Ranking & Surfacing ([ARCHITECTURE.md](./ARCHITECTURE.md) §10) is a consumer of the Query & Retrieval Surface, not a parallel query path. Ranking applies a prioritization policy on top of query results; it does not reach into stores directly.

This separation means ranking policy can change (NARRATIVE_ANALYSIS.md, EVALUATION.md) without altering retrieval semantics. Ranking is a view; retrieval is the substrate.

---

## Interaction With The Evaluation Harness

The Evaluation Harness ([ARCHITECTURE.md](./ARCHITECTURE.md) §12) samples from Signals and Candidate Signals using the Query & Retrieval Surface. Sampling queries typically request:

* Signals by temporal range and type, filtered by lifecycle state
* Candidate Signals for review
* historical Signals for retrospective review under current and past Pipeline Versions (for regression analysis)

The Evaluation Harness also reads DerivationRun metadata to understand how specific Signals were produced. Its queries are heavier in DerivationRun and Pipeline Version dimensions than typical analytical consumers.

---

## What This Document Is Not

* not an API specification (owned by API_SPEC.md)
* not a search-engine selection
* not an index-technology selection
* not a storage specification
* not a ranking policy (owned by NARRATIVE_ANALYSIS.md, EVALUATION.md)
* not a query-language specification

---

## Deferred Decisions

* specific query language, serialization, and request shape — downstream implementation work, in coordination with API_SPEC.md
* pagination scheme and size limits — downstream implementation work
* rate-limit numbers — downstream infrastructure work
* similarity representation for semantic retrieval (score, rank, band) — downstream implementation work, coordinated with MODEL_STRATEGY.md's representation decisions
* index technology and storage layout — downstream infrastructure work
* NarrativeState materialization versus query-time reconstruction — downstream infrastructure work, coordinated with [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)
* caching policy for heavy as-of queries — downstream infrastructure work

---

## Open Questions

* How is semantic retrieval cost bounded under the low-capital constraint when an Entity has many Documents? Re-ranking, candidate-set bounding, and embedding-footprint strategies are deferred. Flagged because they interact with the low-capital commitment.
* How is semantic retrieval over a Representation DerivationRun that has been deprecated (a prior model version) exposed? Flagged: historical as-of queries may require running older embeddings; whether those are retained, retired, or re-embedded on demand is a governance question coordinated with [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md).
* How is the Query & Retrieval Surface's backpressure communicated to heavy callers (the Evaluation Harness during a large retrospective study)? Flagged: a downstream infrastructure concern; the conceptual commitment is that such callers do not degrade live analytical retrieval.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the subject classes and the temporal model this document queries against.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the Query & Retrieval Surface component and its non-responsibilities.
* [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) defines Pipeline Versions, which this document exposes as a query dimension.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines Signal anatomy and lifecycle, which this document's Signal queries honor.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) owns retention of the artifacts retrieval queries against; a retention-tombstoned artifact produces a distinct retrieval state surfaced to the caller.
* API_SPEC.md (deferred) composes its external surface on top of the internal queries defined here; the boundary is held identically as a commitment to that future document.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms introduced here (Semantic Retrieval, As-Of Under Pipeline Version) are flagged for extension in the cluster's closing summary.
