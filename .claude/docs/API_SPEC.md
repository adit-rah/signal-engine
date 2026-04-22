# API_SPEC.md

## Purpose Of This Document

API_SPEC.md defines the external API contract of the Signal Engine at a conceptual level: the resources exposed, the query patterns supported, the response shapes that carry Signals across the wire, and the boundaries against neighboring documents.

This document is conceptual. It does not commit to a specific protocol (REST, GraphQL, gRPC, or other), to authentication and authorization mechanics, to rate-limiting policy, or to versioning. Those are downstream implementation concerns named in the Deferred Decisions section.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). The underlying components are specified in [ARCHITECTURE.md](./ARCHITECTURE.md); the data shape is specified in [DATA_MODEL.md](./DATA_MODEL.md); Signal anatomy is specified in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). User-facing presentation is specified in [USER_EXPERIENCE.md](./USER_EXPERIENCE.md); this document is designed to carry what that document surfaces.

---

## How To Read This Document

* resources are described by what they represent, not by URL paths or schema keywords
* query patterns are described by parameter name and intent, not by encoding
* response shapes are described as structured payloads; the specific serialization format is deferred
* every Signal anatomy field is mapped to a serialization position
* concerns owned by neighboring documents are explicitly bounded

---

## Protocol-Agnostic Posture

The specific transport protocol is deferred to implementation. This document uses the vocabulary of **resources**, **projections**, **parameters**, and **payloads**, which is compatible with REST, GraphQL, gRPC, and other plausible bindings.

When this document says "the API exposes a resource," it means: the external contract makes this object queryable by a stable identifier and by structured parameters, and returns a structured representation. It does not prescribe a specific URL, schema, or operation name.

When this document says "a parameter", it means a request-level input the caller provides, regardless of whether it travels as a query string, header, field selection, or request body.

---

## Guiding API Commitments

Inherited from [CONTEXT.md](./CONTEXT.md), [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md), [DATA_MODEL.md](./DATA_MODEL.md), and [USER_EXPERIENCE.md](./USER_EXPERIENCE.md), and held as API-level invariants:

* every Signal serialized across the wire carries its full anatomy ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) or a clearly projected subset of it; no field is silently omitted
* Basis and Evidence are first-class response elements, not metadata endpoints
* Confidence is not serialized as a probability; its representation honors CONTEXT §3.4
* Strength and Confidence are distinct fields, never collapsed
* as-of queries are supported on every resource where the conceptual data model supports them
* the Candidate vs Surfaced distinction is a first-class query dimension, not an inferred property
* the API exposes read access to analytical outputs; it does not expose write endpoints for analytical internals
* the API does not carry fields for concepts excluded by [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions (no sentiment, no prediction, no recommendation, no alpha, no trading signal)
* the API does not expose model internals (weights, raw scores, activations); it exposes analytical outputs with Basis
* the API relies on the Query & Retrieval Surface ([ARCHITECTURE.md](./ARCHITECTURE.md) component 13); internal query mechanics are owned by SEARCH_AND_RETRIEVAL.md and not duplicated here

---

## Conceptual Resources

The resources below are drawn from [DATA_MODEL.md](./DATA_MODEL.md). Each is described by what the API exposes about it, not by storage representation. All resources are addressed by their Canonical Identifier ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)). Native Identifiers are exposed alongside Canonical Identifiers where relevant but never substituted.

### Entity

The subject of a financial narrative (a public company in v1).

Exposed:

* Canonical identifier
* Native identifiers (ticker, legal name, registry IDs as available), each with its Source
* versioned facts (industry classification, name history, corporate actions) over time
* Baseline thinness summary for the Entity, as of the query's Effective Time
* navigation to related Signals, Documents, Speakers, Themes, Baselines, and NarrativeState

Writes: none. Entity identity is a backend concern.

### Document

An ingested textual artifact. In v1, the exposed subtype is **Transcript**; the contract is designed to accept further subtypes (Filing, Press Release, News Article) without breaking.

Exposed:

* Canonical identifier
* Source identifier
* Entity identifier (reconciled); reconciliation confidence if imperfect
* event time, document time, observation time
* Segments, Utterances, and Speakers (for Transcripts)
* Spans addressable within the Document, to the source-type-appropriate precision
* navigation to Signals, ThemeInstances, and Evidence references involving this Document

Writes: none.

### Speaker

An individual whose Utterances are attributed within a Transcript.

Exposed:

* Canonical identifier
* Native identifiers (name as spoken, role) with their Documents
* Entity association
* role history over time (versioned facts)
* Baseline thinness for the Speaker, as of the query's Effective Time
* navigation to Utterances, Signals whose Subject names this Speaker, and Baselines

Writes: none.

### Theme

A recurring topic, concept, or strategic emphasis tracked across narratives.

Exposed:

* Canonical identifier
* creation time, retirement time (where applicable)
* provenance (human-curated, heuristic, learned) — exposed as a property, not a quality judgment
* navigation to ThemeInstances, Entities where this Theme is prominent, and Omission Events concerning this Theme

Writes: none.

### Baseline

The evolving reference state for an Entity (and optionally a Speaker).

Exposed:

* Entity (and Speaker, where applicable)
* valid-time interval
* Baseline thinness (a structured property, not an inferred flag)
* DerivationRun reference
* a summary of the structural features the Baseline summarizes (for example, for a Transcript Baseline, the framing features, certainty features, structural features the Baseline covers) — without exposing learned model internals
* as-of resolution: a Baseline is addressable at any past Effective Time for which it was valid

Writes: none.

### Signal

The core resource. Every exposed Signal carries the anatomy defined in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); serialization is specified below (Signal Serialization).

Exposed:

* full anatomy (Identity, Type, Subject, Temporal Scope, Basis, Evidence, Strength, Confidence, Lifecycle State, Lineage, Commentary) at the default projection depth
* as-of resolution: a Signal is queryable at an Effective Time, which resolves to the Signal's lifecycle state and Lineage as of that time
* supports projections (see Projection Depth below) for callers that want a sparse representation

Writes: none. The API does not accept user-modifiable Signal content. Lifecycle transitions are system-internal.

### NarrativeState

A point-in-time snapshot of an Entity's narrative.

Exposed:

* Entity identifier and Effective Time
* Surfaced Signals active at that time, in a compact projection
* Baselines applicable at that time, with Baseline thinness
* Themes prominent for the Entity at that time
* recent Documents relevant at that time
* navigation to the individual Signals, Baselines, Themes, and Documents referenced

Writes: none.

### Evidence

The linkage between a derived artifact and the Spans supporting it.

Exposed:

* Evidence identifier
* referenced Spans, each resolved to (Document, Segment, Utterance or sub-Utterance locus, Speaker, event time) and to the excerpt text
* the derived artifact that references it (typically a Signal)

Writes: none.

### Span

The primitive unit of evidence.

Exposed:

* Document identifier
* structured locus description (segment, utterance, character range, as applicable)
* resolved excerpt text
* event time inherited from the Document

Spans are typically accessed via Evidence rather than directly; a direct address is available for stability under re-derivation.

### DerivationRun

A named, versioned instance of a derivation process.

Exposed:

* Canonical identifier
* logical name and version
* creation time
* brief description of the derivation step (ingestion, normalization, enrichment, heuristic analysis, representation, learned analysis, fusion)
* references from artifacts produced by this run (pagination applies for large sets)

DerivationRuns are how callers understand re-derivation lineage. They are read-only.

### Candidate-Type Pool (Read-Only Metadata)

A read-only view of proposed new Signal types that have not yet been promoted into the canonical taxonomy ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md); [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension).

Exposed:

* proposed type name and provenance (research-driven or discovery-driven)
* draft operational definition
* observed example Signals held under the candidate type (as a reference list)
* current review state — this document exposes the read view; promotion workflow is owned by EVALUATION.md

Writes: none. Promotion is not an API-level operation.

---

## Signal Serialization

Every Signal crossing the external boundary carries its anatomy. The following mapping is authoritative for any serialization.

| Anatomy field ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) | Serialization position                                                                                                                 |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Identity                                                          | Canonical identifier, stable across lifecycle records                                                                                  |
| Type                                                              | Typed enumeration drawn from the canonical taxonomy; extensions appear as named types once promoted                                     |
| Subject                                                           | Entity reference; Speaker reference where the Type narrows to a Speaker                                                                 |
| Temporal Scope                                                    | Structured object with subject time (instant or interval), emission time, and, where applicable, Baseline valid-time                    |
| Basis                                                             | Structured object listing heuristic contributions, learned contributions, Fusion Engine DerivationRun, and any Basis Disagreement state |
| Evidence                                                          | List of Evidence references; each resolvable inline or by follow-up query depending on projection depth                                  |
| Strength                                                          | Type-relative indicator; representation follows [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); explicit type label carried           |
| Confidence                                                        | Separate field from Strength; qualitative structure; **not** a probability; accompanied by structured reason fields (below)              |
| Lifecycle State                                                   | Enumerated value: candidate, surfaced, stale, superseded, retired                                                                       |
| Lineage                                                           | Structured references: `supersedes` (prior Signal identifiers) and `superseded_by` (subsequent Signal identifier)                      |
| Commentary                                                        | Immutable text bound to this Signal record                                                                                              |

Constraints on the serialization:

* no anatomy field is silently omitted; a projection that omits a field must name the omission
* Confidence is always accompanied by structured reason fields naming the factors contributing to it: Baseline thinness, Basis Disagreement, Evidence density
* Strength and Confidence are distinct fields; the API never emits a merged "score"
* the serialization carries no probability of price movement, no directional forecast, no buy/sell/hold code, no sentiment polarity, and no recommendation
* a Signal with unresolvable Basis is not emitted; the API does not need to represent that case

### Signal Digest

The sparse projection of a Signal, intended for list responses and summary surfaces. Carries:

* Identity
* Type
* Subject
* subject time (not the full Temporal Scope object)
* Strength indicator
* Confidence indicator, with at least one reason field when reasons apply
* lifecycle state
* Commentary excerpt
* presence indicators for Basis Disagreement and Thin-History (so the caller can surface them without deeper fetch)
* links to the full Signal representation and to Evidence

"Signal Digest" is flagged for glossary extension.

### Signal Full

The complete projection of a Signal. Carries every anatomy field in full, including the resolved Basis chain, all Evidence references (resolvable or inline per projection depth), full Lineage with identifiers for superseded and superseding Signals, and DerivationRun references.

### Projection Depth

Callers may request a projection depth for Signal resources and for list responses containing Signals. Three conceptual depths are committed:

* **headline** — a minimal projection equivalent to what a Signal list surface renders as a Signal Headline in [USER_EXPERIENCE.md](./USER_EXPERIENCE.md). No Basis chain; Evidence not inlined.
* **summary** — the Signal Digest shape above. Basis summarized (presence indicators only); Evidence referenced by identifier, not inlined.
* **full** — the complete Signal Full representation. Basis and Evidence inlined where feasible; otherwise referenced with follow-up identifiers.

The specific encoding of projection depth (for example, as a field-selection mechanism in GraphQL or as a `depth` parameter in REST) is a binding detail deferred to implementation.

"Projection Depth" is flagged for glossary extension.

---

## Query Patterns

The API supports the following query patterns across relevant resources. Each pattern is described by intent; the parameter names given are illustrative, not prescriptive.

### Entity-Centric

Signals for a specified Entity over a specified window.

* parameters: Entity identifier; optional subject-time range; optional emission-time range; optional Speaker filter; optional Theme filter; optional Type filter; optional lifecycle-state filter; optional Strength floor; optional Confidence floor; optional Baseline-thinness filter; optional Basis-Disagreement filter; projection depth.
* returns: list of Signals matching the filters, ordered as ranked upstream (Ranking & Surfacing in [ARCHITECTURE.md](./ARCHITECTURE.md)); secondary orderings available by subject time or emission time.
* notes: the default lifecycle-state filter is `surfaced`. Callers explicitly opt into Candidate, Stale, Superseded, or Retired.

### Signal Type-Scoped (Cross-Entity)

Signals of a specified Type across Entities.

* parameters: Type (one or more); optional subject-time range; optional Entity filter (inclusion); optional Theme filter; projection depth; lifecycle-state filter.
* returns: list of Signals matching filters. Entity appears as a first-class field on each Signal Digest.
* notes: cross-Entity queries may be rate-limited or bounded in result-set size under the low-capital constraint ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint). Specific bounds are deferred.

### Speaker-Scoped

Signals whose Subject narrows to a specific Speaker.

* parameters: Speaker identifier; optional subject-time range; optional Type filter; projection depth; lifecycle-state filter.
* returns: list of Signals with this Speaker in Subject.
* notes: primarily relevant for Confidence Shift and Speaker-level Structural Anomaly.

### Theme-Scoped

Signals involving a specific Theme.

* parameters: Theme identifier; optional Type filter (Omission Event is the most natural fit); optional Entity filter; optional subject-time range; projection depth; lifecycle-state filter.
* returns: list of Signals that reference the Theme through Evidence or through the comparison chain.

### Time-Range Queries

Every Signal-returning query accepts either a subject-time range, an emission-time range, or both. The API requires the caller to name which time they are querying; it does not silently conflate them.

* subject-time range — signals about a phenomenon that occurred in the window
* emission-time range — signals the system produced in the window

Mixing the two is legal; the contract is explicit.

### Lifecycle-State Queries

Lifecycle state is a first-class filter dimension, not an inferred property.

* default filter: `surfaced`
* filters may include any subset of `candidate`, `surfaced`, `stale`, `superseded`, `retired`
* the API does not silently include Candidate Signals when the caller asked only for Surfaced; the inclusion is always explicit

### As-Of Queries

Every resource whose conceptual model supports as-of reconstruction accepts an `as_of` parameter ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) As-of Query):

* Signals — lifecycle state, Lineage, and presence-in-result-set are resolved as of the specified Effective Time
* Baselines — the Baseline as valid at the Effective Time is returned
* NarrativeState — the snapshot is reconstructed as of the Effective Time
* Entities and Speakers — versioned facts are resolved as of the Effective Time

`as_of` is an Effective Time. The default is "now". The parameter must round-trip precisely; a response returns the Effective Time it was reconstructed at, so callers can confirm they received what they asked for.

The API does not guarantee that any arbitrary past Effective Time is addressable; retention is a governance concern. What is guaranteed is:

* the contract is stable — the same shape is returned regardless of Effective Time
* when an Effective Time is unavailable, the error is explicit

The API boundary with SEARCH_AND_RETRIEVAL.md preserves as-of semantics: retrieval mechanics honor Effective Time internally; the API does not re-implement them.

---

## Candidate Versus Surfaced

The Candidate vs Surfaced distinction is a lifecycle-state distinction ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)). It is exposed at the API as follows:

* lifecycle state is a field on every Signal serialization
* lifecycle state is a filter on every Signal-returning query
* the default filter includes Surfaced only; the default explicitly excludes Candidate, Stale, Superseded, and Retired
* Candidate Signals are queryable when the caller opts in; the API does not hide them
* Candidate Signals carry the same anatomy as Surfaced Signals; they are not reduced-quality variants
* the reason a Candidate has not been promoted — where the system has articulated it — is exposed on the Signal

This posture matches the UX posture ([USER_EXPERIENCE.md](./USER_EXPERIENCE.md) Candidate Signal Review) and avoids introducing a new lifecycle semantics at the API that disagrees with the internal contract.

---

## Evidence And Provenance Exposure

Evidence is a first-class element of every Signal, not a side channel. The chain, inherited from [DATA_MODEL.md](./DATA_MODEL.md):

Signal → Basis (DerivationRuns) → Candidate Evidence → Features → Evidence → Spans → Document → Raw

The API exposes this chain in layered fashion:

* at `summary` projection, a Signal carries Evidence references (identifiers) and Basis presence indicators
* at `full` projection, Evidence references resolve to inline records with resolved Spans, each excerpt rendered at source-type-appropriate precision
* Basis is always carried at `full` projection; at `summary` it is referenced with presence indicators for Basis Disagreement
* DerivationRun references are exposed at every projection but resolvable only under direct fetch — they are metadata about derivation, not payload

Clients wanting only surface data take `summary` or `headline`. Clients performing audit, evaluation, or downstream analysis take `full` and follow DerivationRun references as needed.

Evidence for Omission Events follows the special case described in [USER_EXPERIENCE.md](./USER_EXPERIENCE.md): the Spans carried are from prior Documents citing the now-absent Theme, and an absence indicator accompanies them. The serialization reflects this structurally — the Evidence record is marked as an absence-pattern Evidence, with prior-recurrence context and the current Document's scope attached.

---

## Relationship To SEARCH_AND_RETRIEVAL.md

SEARCH_AND_RETRIEVAL.md (not yet written) owns the internal query and retrieval mechanics of the system: indexing, query planning, result materialization, caching, and internal retrieval primitives. It does not own the external API contract.

This document and SEARCH_AND_RETRIEVAL.md share the following boundary:

* the Query & Retrieval Surface ([ARCHITECTURE.md](./ARCHITECTURE.md) component 13) is the internal abstraction that retrieval mechanics expose upward
* the API Boundary ([ARCHITECTURE.md](./ARCHITECTURE.md) component 14) consumes the Query & Retrieval Surface and exposes the external contract defined in this document
* retrieval mechanics internal to the system — index structure, query-plan choices, cache strategy — are opaque to API callers and owned by SEARCH_AND_RETRIEVAL.md
* query *intent* — what callers can ask for, how it is parameterized, what the response shape is — is owned by this document
* when SEARCH_AND_RETRIEVAL.md commits to a specific retrieval mechanic that affects caller-observable behavior (for example, a bounded maximum as-of depth), this document inherits that bound as a contract limit and surfaces it in error semantics

The two documents must agree on:

* which resources and query patterns are supported
* as-of query semantics — both documents preserve the same Effective Time semantics
* pagination posture for large result sets (described below)

If they drift, this document yields on retrieval mechanics and SEARCH_AND_RETRIEVAL.md yields on external shape.

---

## Pagination, Filtering, And Large Result Sets

The API is designed for depth-seeking callers, not for continuous high-throughput consumption (ASSUMPTIONS U6; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint). Result-set handling is posture, not mechanism:

* every list-returning query supports pagination; the specific pagination mechanism (cursor, offset, page-token) is deferred to implementation
* filters are the primary tool for bounding result sets; the API encourages narrow queries and will bound overly wide queries
* the API exposes result-count semantics honestly — either total counts or bounded "at least this many" — and is explicit about which
* very large result sets may be served as references (a persistent identifier for the result) rather than inlined payloads, to respect the low-capital constraint; this is a deferral to implementation
* the API may reject queries that materially exceed a result-set or computational bound, with an explicit error naming the reason and suggesting narrower filters

### Rate Limiting And Quotas

Deferred. No commitment is made here.

### Streaming Or Change-Feed Access

Not exposed in v1. The system is not positioned as a real-time stream ([ARCHITECTURE.md](./ARCHITECTURE.md) Operating Posture; [SCOPE.md](./SCOPE.md) Deferred). A future change-feed is a possible extension but requires a dedicated specification.

---

## Error Semantics

Described at a conceptual level. Specific error codes, structured payloads, and error taxonomies are deferred.

Categories the contract must handle:

* **resource not found** — a Canonical Identifier does not resolve
* **reconciliation imperfect** — a resource is addressed by a Native Identifier that reconciles with non-trivial ambiguity; the response includes reconciliation confidence and, where plural, candidate Canonical Identifiers
* **as-of unavailable** — the requested Effective Time is outside the addressable history; the error names the earliest addressable time
* **query exceeds bounds** — the query would materialize a result set larger than the API is willing to serve; the error names the offending dimension and suggests narrower filters
* **projection depth unsupported** — the caller requested a depth the resource does not support (rare, but possible for some metadata resources)
* **authorization** — deferred to SECURITY_AND_PRIVACY.md

Errors are structured payloads, not plain strings. Specific structure is deferred.

---

## What Is Deliberately Not In The API

The following are excluded by design:

* no write endpoints for analytical internals — no client-submitted Signal content, no client edits to Commentary, Basis, Strength, Confidence, Lineage, or lifecycle state; these are system outputs
* no endpoint that would allow a caller to alter ranking — ranking is owned upstream (Ranking & Surfacing in [ARCHITECTURE.md](./ARCHITECTURE.md))
* no endpoint that would permit a caller to re-weight Strength or Confidence for presentation purposes; re-weighting is a concern upstream, not a client concern
* no Entity-level or Speaker-level aggregate "score"; no endpoint returning a composite sentiment, mood, or direction metric
* no field named "sentiment", "polarity", "positive", "negative", "bullish", "bearish", or equivalents
* no field named "prediction", "forecast", "projected", "likelihood", or equivalents implying future state
* no field named "recommendation", "buy", "sell", "hold", "rating" in a recommending sense, "action", or equivalents
* no field named "alpha" or "alpha signal"
* no model-internal fields — no weights, raw scores that claim probabilistic calibration, or activations exposed to callers
* no user-authored content endpoints (notes, comments, annotations) in v1; collaboration is deferred ([SCOPE.md](./SCOPE.md) Deferred)
* no endpoint that admits external LLM API responses as first-class input into analytical pipelines; this would violate CONTEXT §6.1

These exclusions are structural, not policy. The API does not expose these surfaces because the system does not produce them.

---

## Honoring The Deliberate Non-Definitions

[DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)'s Deliberate Non-Definitions are enforced at the API level by exclusion of field names, query parameters, and response shapes that would introduce them.

* Sentiment — there is no sentiment resource, no sentiment field, no sentiment filter. Where callers reach for "sentiment", the appropriate API concept is a Confidence Shift Signal, a Narrative Drift Signal, or another Signal type.
* Prediction — there is no prediction resource, no forecast field, no "likely movement" filter. The API returns observations of change, not claims about the future.
* Recommendation — there is no recommendation resource or field. The API does not advise action.
* Trading Signal / Alpha — not exposed. "Signal" in this API is always a narrative Signal.
* AI / AI-powered — not used as framing in field names, resource labels, or error language. The API names components: "heuristic analysis", "learned analysis", "Fusion Engine".
* Black-Box Model — the API exposes only outputs with Basis; model internals are not exposed.
* Autonomous Agent — no action endpoint; the API does not act.
* Accuracy — not used as a field. Where callers might reach for "accuracy", the API exposes Confidence (with its explicit non-probability semantics), Basis Disagreement, and Baseline thinness.

The exclusion is by name, by concept, and by shape. A downstream implementation introducing any of these fields would violate the contract.

---

## Consistency With USER_EXPERIENCE.md

Every anatomy field surfaced in [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) has a serialization in this document. The following cross-reference is authoritative for any divergence.

| Anatomy field       | UX surface treatment                                                                    | API serialization position                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Identity            | Stable across all surfaces; shown on Signal Detail                                      | Canonical identifier at all projections                                                             |
| Type                | Always visible at the Signal Headline                                                    | Typed enumeration                                                                                   |
| Subject             | Entity (and Speaker where relevant) at the Signal Headline                              | Entity and optional Speaker references                                                              |
| Temporal Scope      | Compact subject-time at Headline; full Temporal Scope at Signal Detail                   | subject-time at Digest; full Temporal Scope object at Full                                          |
| Basis               | Summarized on Signal Detail; expanded on Basis Inspector                                 | Presence indicators at Digest; full chain at Full                                                   |
| Evidence            | Referenced on Signal Detail; expanded on Evidence View                                   | References at Digest; resolved Span-level records at Full                                           |
| Strength            | Separate qualitative indicator at Headline; labeled with a magnitude-of-deviation term   | Separate field; type-relative; never merged with Confidence                                         |
| Confidence          | Separate qualitative indicator at Headline; reason alongside                             | Separate field; qualitative structure; accompanied by structured reason fields; never a probability |
| Lifecycle State     | Visible at Headline when non-Surfaced; default filter elsewhere                          | Enumerated field; first-class filter dimension                                                      |
| Lineage             | Renders as a navigable chain; reachable from any Signal                                  | `supersedes` and `superseded_by` reference fields                                                   |
| Commentary          | Excerpted at Headline; full at Signal Detail; immutable per Signal record                | Immutable text; carried at Digest (excerpted) and Full (complete)                                    |
| Basis Disagreement  | Surfaced honestly on Basis Inspector                                                     | Presence indicator at Digest; structured state at Full                                               |
| Baseline Thinness   | Thin-History Indicator on affected Signals; explained in Commentary                      | Structured property on Baseline and on affected Signals                                              |

The two documents must stay in sync. If an anatomy field's UX treatment changes, this document's serialization must be revisited; if this document's serialization changes, [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) must be revisited.

---

## What This Document Is Not

* not a protocol selection (REST, GraphQL, gRPC are equally compatible)
* not an authentication or authorization specification — deferred to SECURITY_AND_PRIVACY.md
* not a rate-limiting specification
* not a versioning specification
* not an SDK or client-library specification
* not a streaming or change-feed specification (not in v1)
* not a retrieval-mechanics specification — deferred to SEARCH_AND_RETRIEVAL.md
* not a ranking specification — deferred to NARRATIVE_ANALYSIS.md and EVALUATION.md
* not a storage, indexing, or deployment specification
* not a specification of UX — deferred to [USER_EXPERIENCE.md](./USER_EXPERIENCE.md)

---

## Deferred Decisions

* specific protocol (REST, GraphQL, gRPC, or other) — deferred to implementation
* authentication and authorization — deferred to SECURITY_AND_PRIVACY.md
* rate-limiting and quota policy — deferred
* versioning strategy (path-prefixed, header-based, content-negotiated, or other) — deferred
* pagination mechanism (cursor, offset, page-token, or other) — deferred
* specific encoding of projection depth — deferred
* error taxonomy and structured error payload shape — deferred
* caching semantics at the HTTP / transport layer — deferred
* long-running query support and result-reference handling — deferred; posture is named, mechanism is not
* streaming and change-feed — deferred; not in v1
* SDK and client-library shape — deferred
* retention boundaries for as-of availability — deferred to DATA_GOVERNANCE.md
* specific Strength and Confidence representation — owned by MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; this document commits only to serialization shape, not value representation
* specific Commentary generation — owned by MODEL_STRATEGY.md; this document carries whatever is generated, immutably
* ranking methodology — owned by NARRATIVE_ANALYSIS.md and EVALUATION.md; exposed here only as "upstream-ordered"

---

## Glossary Additions Recommended

The following terms are introduced in this document and should be promoted into [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **Signal Digest** — the sparse projection of a Signal used in list responses and summary surfaces. Mirrors the Signal Headline concept in [USER_EXPERIENCE.md](./USER_EXPERIENCE.md); either term may become glossary canonical with the other as a synonym.
* **Signal Full** — the complete projection of a Signal carrying every anatomy field.
* **Projection Depth** — the caller-specified level of detail for a Signal serialization, with `headline`, `summary`, and `full` as the committed values.
* **Absence-Pattern Evidence** — the structured Evidence form used for Omission Events, carrying prior Spans and an absence indicator rather than a direct quotation.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes their commitments at the external contract.
* [VISION.md](./VISION.md) establishes the orientation this document serves.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) U2, U4, U5, U6, and T3 bound the posture — depth-seeking, individual, tolerant of latency, low-capital.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; this document recommends additions listed above.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the underlying resources; this document exposes them.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the Signal anatomy this document serializes; the Signal Serialization section is authoritative for anatomy-to-wire mapping.
* [ARCHITECTURE.md](./ARCHITECTURE.md) components 13 (Query & Retrieval Surface) and 14 (API Boundary) are the architectural realization of this document's contract.
* [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) is the user-facing counterpart; the Consistency section is authoritative for cross-document alignment.
* SEARCH_AND_RETRIEVAL.md (when written) owns internal retrieval mechanics; the boundary is specified above.
* SECURITY_AND_PRIVACY.md (when written) owns authentication, authorization, and privacy posture.
* NARRATIVE_ANALYSIS.md and EVALUATION.md own ranking and lifecycle transition policy; this document exposes their outputs, it does not duplicate them.
* MODEL_STRATEGY.md owns model internals; this document does not expose them.
