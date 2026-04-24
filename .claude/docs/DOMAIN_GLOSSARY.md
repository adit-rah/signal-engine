# DOMAIN_GLOSSARY.md

## Purpose Of This Document

DOMAIN_GLOSSARY.md establishes the authoritative vocabulary for the project. Every downstream document uses these terms. Inconsistent definitions cause the document set to drift; this glossary is the source of truth against that drift.

Where this document extends a definition already given in CONTEXT.md, the extension sharpens operational usability and must not contradict the original.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative.

---

## How To Use This Glossary

* Definitions are operational. A downstream architect should be able to use the term in a specification without ambiguity.
* Terms are grouped by conceptual area. Within a group, related terms appear near each other.
* Cross-references use the term name exactly. If a term is referenced but not defined here, that is a defect.
* Definitions that would require an architectural decision to be fully unambiguous are marked with a deferral note rather than filled in with invented detail.

---

## Core Framing Terms

### Financial Narrative Intelligence System

The project's working self-description, inherited from CONTEXT §1. A system that detects meaningful changes in meaning, confidence, framing, and consistency across time in financial text.

Used in preference to "sentiment tool", "analytics tool", or "AI assistant", each of which implies a different system.

### Financial Text

Any written or transcribed communication whose subject is financial performance, market behavior, company operations, or macroeconomic conditions. Includes but is not limited to earnings call transcripts, SEC filings, press releases, financial news, and analyst commentary (CONTEXT §8).

### Financial Narrative

The evolving, multi-document account of an entity's communication, operations, and circumstance. Narratives are the unit of interpretation for this project; individual documents are inputs to a narrative, not narratives themselves.

### Narrative Intelligence Engine

The colloquial name for the system (CONTEXT §19; VISION.md North Star). Emphasizes temporal narrative analysis as the system's central orientation.

---

## The Signal

### Signal

A meaningful, explainable deviation or pattern in financial narrative structure over time (CONTEXT §4).

Operationally, a Signal has:

* a Type, drawn from the confirmed taxonomy or an extension approved through the pattern owned by SIGNAL_DEFINITIONS.md
* a Basis — the contributions that produced it
* Evidence — Spans in source text that support it
* Strength and Confidence (distinct; see below)
* a Lifecycle State
* a Lineage when it supersedes or retires a prior Signal

A Signal is not a prediction, a recommendation, or a sentiment score. See Deliberate Non-Definitions.

### Signal Taxonomy

The structured set of Signal types recognized by the system. The confirmed initial taxonomy is defined in CONTEXT §4. The taxonomy is extensible; the pattern for extending it is owned by SIGNAL_DEFINITIONS.md.

### Signal Type

A category within the Signal taxonomy. Each Signal type has its own operational definition. Cross-type relationships — for example, a Confidence Shift co-occurring with an Omission Event — are a modeling concern owned by NARRATIVE_ANALYSIS.md and represented as Signal Interaction Records.

### Narrative Drift

A Signal type. Gradual change in framing, emphasis, or strategic communication over time (CONTEXT §4).

Operationally, Narrative Drift is identified by comparing narrative content across temporally separated Documents and detecting shifts that exceed a threshold of meaningfulness. The threshold is deferred to SIGNAL_DEFINITIONS.md and NARRATIVE_ANALYSIS.md.

Distinct from Confidence Shift: Narrative Drift concerns *what* is said; Confidence Shift concerns *how*.

### Confidence Shift

A Signal type. Change in certainty, hedging, or assertiveness in communication (CONTEXT §4).

Operationally, Confidence Shift is identified by comparing certainty-bearing features of communication over time — hedging language, qualifiers, conditional framing, and their inverses.

Distinct from Narrative Drift: Confidence Shift concerns the speaker's stance toward claims, not the claims themselves.

### Omission Event

A Signal type. Disappearance of previously recurring themes or priorities (CONTEXT §4).

Operationally, an Omission Event requires:

* prior presence of a Theme with enough recurrence to establish it as expected
* absence or materially reduced presence in a later period
* a reasonable attribution that the absence is not artefactual

Distinct from Contradiction: Omission is the absence of expected material; Contradiction is the presence of inconsistent material.

### Contradiction Event

A Signal type. Inconsistency across time or sources (CONTEXT §4).

Operationally, a Contradiction Event requires:

* two or more statements that can be brought into direct comparison
* a judgment that the statements are incompatible rather than merely different
* a trace to the specific statements and Sources involved

Contradictions may be intra-source (the same Entity over time) or cross-source (different Sources at roughly the same time).

### Structural Anomaly

A Signal type. Unusual deviation from established communication patterns (CONTEXT §4).

Operationally, Structural Anomaly is identified against a Baseline of expected communication structure — length, topic distribution, segment ordering, speaker share, and similar structural features.

Distinct from the other four: Structural Anomaly concerns the shape of communication rather than its content, framing, or certainty.

### Baseline

An Entity-specific or Speaker-specific reference against which deviations are measured. A Baseline summarizes expected patterns for the subject at a given point in time. Baselines are a prerequisite for Narrative Drift, Confidence Shift, and Structural Anomaly detection.

A Baseline has a valid-time interval. A historical Baseline can be retrieved as-of any past date.

See Entity Baseline and Speaker Baseline for scope-specific uses.

*Baseline construction method is owned by NARRATIVE_ANALYSIS.md.*

### Entity Baseline

A Baseline scoped to an Entity as a whole. Aggregates structural, framing, and topic-distribution patterns across Documents concerning the Entity.

### Speaker Baseline

A Baseline scoped to a specific Speaker within an Entity. Carries communication-pattern features (hedging density, assertive-language rate, Q&A behavior, topic ownership) specific to the individual.

### Baseline Thinness

A queryable property of a Baseline indicating the sufficiency of the underlying history. A thin Baseline has insufficient historical depth to support high-Confidence Signal emission; Baselines are not hidden from consumers when thin but are exposed as such.

Related to but distinct from **Historical Depth**: Historical Depth is an Entity-level property of the data available; Baseline Thinness is a Baseline-level property that may reflect Historical Depth, selection window, or Baseline-construction choices.

Thin-History Policy governs how thin Baselines are treated at Signal emission time.

### Freshness Window

The temporal window within which a Baseline is considered current for use by the analytical layer. Outside the Freshness Window, a Baseline may require update before use.

*Specific window policy is owned by NARRATIVE_ANALYSIS.md.*

### Signal Strength

The degree to which a given Signal rises above the noise floor for its Type. Specific representation — scalar score, discrete band, categorical tier — is deferred to SIGNAL_DEFINITIONS.md and MODEL_STRATEGY.md.

Invariants:

* Strength is a type-relative statement, not a cross-type ranking value
* Strength is not a probability of anything external (for example, price movement)
* Strength is bounded; extreme values are exceptional by construction

### Signal Confidence

A representation of the system's epistemic certainty in a Signal itself, distinct from Strength.

High Strength with low Confidence is coherent: the observed deviation is large, but the system is not sure it is real (for example, thin Baseline, Basis Disagreement, or narrow Evidence).

Confidence reflects, at minimum:

* Baseline Thinness (where the Signal depends on a Baseline)
* Basis Disagreement between heuristic and learned contributions
* Evidence Span precision and quantity

Confidence is not a probability of correctness; claiming otherwise would violate structured skepticism (CONTEXT §3.4).

*Specific representation is deferred to SIGNAL_DEFINITIONS.md and MODEL_STRATEGY.md. User-facing surfacing is deferred to USER_EXPERIENCE.md.*

### Signal Rank

An ordering of Signals by importance or priority. A ranked Signal output is confirmed (CONTEXT §9); ranking methodology is owned by NARRATIVE_ANALYSIS.md and EVALUATION.md.

Policy posture (from NARRATIVE_ANALYSIS.md): Strength provides within-type ordering; Confidence gates surfacing rather than ranks; no cross-type aggregate Strength is emitted.

### Basis

The chain of contributions that produced a Signal: which heuristic rules contributed, which learned analyses contributed, and how the Fusion Engine combined them.

Basis is mandatory on every Signal (CONTEXT §3.3). A Signal whose Basis chain cannot be resolved is not emitted.

### Basis Disagreement

The condition in which heuristic and learned contributions to a Signal reach divergent conclusions about its existence, type, or magnitude. Basis Disagreement is a first-class input to Signal Confidence.

*How Basis Disagreement is detected, represented, and resolved is owned by MODEL_STRATEGY.md.*

### Commentary

A human-readable explanation generated at Signal emission time, describing what the Signal observes and why it is considered meaningful. Commentary is bound to the Signal and is immutable.

Every Signal has non-empty Commentary. Commentary is generated under a Grounding Check (see Model And Evaluation Terms) that anchors output to Basis and Evidence.

*Commentary generation method is owned by MODEL_STRATEGY.md. User-facing surface is owned by USER_EXPERIENCE.md.*

### Lineage

References on a Signal to prior Signals it supersedes and to subsequent Signals that supersede it. Lineage is populated by lifecycle transitions, not by emission.

### Lifecycle State

One of: Candidate, Surfaced, Stale, Superseded, Retired. Transitions are expressed as new Signal records with Lineage, not as mutations of the original.

### Candidate Signal

A Signal produced by the Fusion Engine but not promoted to the Surfaced pool. Candidate Signals are visible to the Evaluation Harness and to downstream analytical processes but are not expected to be surfaced to users.

Note: "Candidate" names a lifecycle state, not a quality judgment.

### Surfaced Signal

A Signal eligible for user-facing surfaces. Promotion from Candidate may be automatic (thresholds met) or gated (for example, human review for Signal types marked for review, or Thin-History Policy rules).

### Stale Signal

A Surfaced Signal that has aged past the point where its observation is current. Stale Signals remain queryable for historical purposes but are not emphasized on current-state surfaces.

### Superseded Signal

A Signal replaced by a subsequent Signal concerning the same subject and temporal scope. The Superseded record is retained; the subsequent Signal's Lineage references it.

### Retired Signal

A Signal withdrawn — typically because its Basis has been invalidated (for example, a DerivationRun was recalled) or its Evidence was found to be incorrect. Retirement is expressed as a new record with Lineage; the original Signal is not deleted.

### Candidate-Type Pool

The holding area for proposed new Signal types that have not yet been promoted into the canonical taxonomy. Candidate types enter through either Research-Driven Extension or Discovery-Driven Extension and are reviewed through the Evaluation Harness.

Ownership split:

* SIGNAL_DEFINITIONS.md owns the state machine and type definition
* EVALUATION.md owns the promotion workflow and review mechanics
* NARRATIVE_ANALYSIS.md owns how a promoted type is used in production analysis

### Research-Driven Extension

A path by which a new Signal type enters the taxonomy: proposed from analytical or research work with a draft operational definition, required evidence pattern, strong-vs-weak criteria, and common false-positive patterns.

### Discovery-Driven Extension

A path by which a new Signal type enters the taxonomy: proposed by the Learned Analysis component under CONTEXT §5.4. A user-confirmed policy permits unsupervised discovery to propose new types, not only new instances of existing types.

### Thin-History Policy

The set of rules governing Signal emission for Entities with limited historical depth. The policy is reliability-preferring: Signals that depend on a Baseline are subject to Baseline Thinness-driven Confidence adjustment; severely thin Baselines may hold Signals at Candidate status pending human review; Omission Events require a minimum prior-recurrence threshold.

Policy shape is committed in SIGNAL_DEFINITIONS.md. Numeric thresholds are owned by NARRATIVE_ANALYSIS.md.

### False-Positive Posture

The project's standing preference, in early development, for minimizing false-positive Signals at the cost of accepting higher false-negative rates. User-confirmed (CONTEXT §14). Documented so that downstream tuning, ranking, and evaluation work defaults to the same priority.

### Signal Interaction Record

An analytical artifact representing a non-trivial relationship between two or more Signals: co-occurrence, reinforcing evidence, or contradiction-between-Signals.

Interactions are represented as relationships, not as collapsed Signal types. Multiple related Signals are not merged into one; they are linked via an Interaction Record.

*Owned by NARRATIVE_ANALYSIS.md.*

### Signal Headline

The short human-readable text appearing at the top of a Signal presentation. Used in both UX progressive-disclosure (Headline → Summary → Full) and API projections. Canonical name for this concept.

"Signal Digest" (below) is the API projection depth that delivers a Signal in compact form; the Signal Headline is part of every projection.

### Signal Digest

The API projection depth that returns a Signal in compact form (identity, subject, type, headline, minimal metadata). One of three projection depths alongside Signal Summary and Signal Full.

### Signal Summary

The API projection depth that returns a Signal with Strength, Confidence, Evidence references, and Commentary, but not the full Basis chain.

### Signal Full

The API projection depth that returns a Signal with the complete anatomy: Basis chain, Evidence, Lineage, and DerivationRun references.

### Projection Depth

The per-request control over how much of a Signal's anatomy is serialized. Three depths: Digest, Summary, Full. Projection Depth is an API concern (API_SPEC.md) that mirrors the UX progressive-disclosure pattern.

### Absence Marker

A UX rendering element used for Omission Event Signals, which cannot be evidenced by quotable text. Indicates the shape and extent of an expected-but-absent Theme or pattern, with reference to the prior Documents that establish the expectation.

### Absence-Pattern Evidence

The API serialization of an Absence Marker: a structured representation of prior-recurrence cites plus the current scope in which the expected material is absent. Distinct from ordinary Evidence, which cites present text.

### Thin-History Indicator

A UX rendering element, and corresponding API field, that exposes Baseline Thinness on a Signal without turning it into a warning. Makes the Thin-History Policy legible to the user.

### As-Of View

A user-facing or API-facing view of the system's state reconstructed to a specified Effective Time. Exposes NarrativeState, Baselines, and the Signals surfaced at that time. The external-facing surface for the As-of Query capability (CONTEXT §11).

### Epistemic Surface

A convenience term for the cluster of user-facing constraints that together communicate the system's epistemic limits: Strength, Confidence, Basis Disagreement, Baseline Thinness, Lifecycle State, Lineage. The Epistemic Surface is a UX-level concept (USER_EXPERIENCE.md) that composes these elements; it is not a new data structure.

### Hallucination Surface

The subset of system outputs generated by a small-footprint language model — principally Commentary — where text risks departing from Basis. Named so that protections (Grounding Check, immutability, Basis binding) can be clearly scoped to this surface.

---

## Architectural Layers (Conceptual)

These terms refer to conceptual layers named in CONTEXT §3.2 and §12. They are not a commitment to a specific implementation architecture.

### Heuristic Layer

The structural, rule-based component of the system, conceptually. Responsible for entity extraction, document segmentation, time alignment, rule-based comparisons, omission tracking logic, and contradiction detection scaffolding (CONTEXT §3.2.A, §7).

Also referred to as the Structural Layer (CONTEXT §12.1). The two terms are synonymous in this project.

### ML Layer

The learned-representation component of the system, conceptually. Responsible for embedding-based representation, narrative similarity and drift detection, probabilistic signal scoring, latent feature extraction, and unsupervised pattern discovery (CONTEXT §3.2.B, §5).

Also referred to as the Semantic Layer (CONTEXT §12.2). The two terms are synonymous.

### Fusion Layer

The third sub-layer of the hybrid intelligence model (CONTEXT §3.2.C). A **conceptual** layer, not a specific architectural component.

Responsible at the conceptual level for integrating heuristic and ML outputs into final Signals, resolving conflicts between structure and learned outputs, and ensuring explainability and traceability of combined Signals.

Deliberately the least specified conceptual layer of the system, and treated as a hard design problem owned by downstream architecture work.

The architectural realization of the Fusion Layer is the **Fusion Engine** component; see below.

### Fusion Engine

The specific architectural component in ARCHITECTURE.md that realizes the Fusion Layer concept. A singular component, not a collection.

Owns: integration of heuristic-layer and learned-layer candidate evidence into emitted Signals; resolution of conflicts between rules and learned outputs; preservation of Basis on every Signal; computation of Signal-level Confidence.

The designated hard design problem per CONTEXT §3.2.C.

Distinct from Fusion Layer: the Fusion Layer is a concept; the Fusion Engine is its implementation.

### Signal Layer

The conceptual layer at which interpretable narrative Signals are produced for downstream consumption (CONTEXT §12.3).

Distinct from the Fusion Layer: the Signal Layer concerns the shape of what emerges; the Fusion Layer concerns how it is combined. The Signal Layer is what the user ultimately consumes; the Fusion Layer is an upstream concern.

Also used as the name of the topmost Derivation Layer (see below). The two uses are consistent: derived Signals are the output of the Signal Layer.

### Hybrid Intelligence

The combination of the Heuristic Layer, the ML Layer, and the Fusion Layer (CONTEXT §3.2). The project is hybrid by design, not by expedience.

---

## Identity Terms

The system uses three kinds of identifiers, named in DATA_MODEL.md.

### Native Identifier

Whatever the external world uses to identify something: a stock ticker, a legal name, a Source-native Document ID, a Speaker name as spoken in a transcript. Native Identifiers are preserved alongside Canonical Identifiers, never replaced by them.

### Canonical Identifier

A project-owned, stable reference for Entities, Sources, Speakers, Themes, Documents, Signals, and other artifacts requiring stable reference. Canonical Identifiers are the references used in all cross-artifact relationships within the system.

Reconciliation from Native to Canonical is a deliberate operation with failure modes. Reconciliation confidence is recorded where imperfect, rather than asserted silently.

### Locus Identifier

For Spans, a structured description sufficient to re-resolve a position within a Document's normalized form. Span precision is source-type appropriate: for Transcripts, Spans are at least Utterance-bounded and may be finer.

---

## Temporal Terms

The system distinguishes several kinds of time. Each derived artifact records the kinds relevant to it (DATA_MODEL.md).

### Event Time

When the phenomenon being described occurred: the call time for a Transcript, the period covered by a filing, the announcement date for a press release.

### Document Time

When the Document was published or finalized by the Source. Typically close to but distinct from Event Time.

### Observation Time

When the system first ingested the Document.

### Processing Time

When a derived artifact was produced. May be significantly later than Observation Time under re-derivation.

### Valid Time

For artifacts with a validity interval — notably Baselines and versioned facts — the interval over which the artifact applies.

### Emission Time

For Signals, the time the Signal was produced by the Fusion Engine.

### Effective Time

For as-of queries, the time at which the caller wants the system's state reconstructed.

### Subject Time

For Signals, the time or interval the Signal describes. Distinct from Emission Time: a Signal may be emitted now about a subject time in the past.

### As-of Query

A query that reconstructs the system's state as of a specified Effective Time. Supported for Baselines, NarrativeState, and emitted Signals. The fundamental mechanism for CONTEXT §3 temporal reasoning.

Externally exposed as an As-Of View.

---

## Derivation Layers

Derived data is organized into conceptual layers (DATA_MODEL.md). Each layer may be re-derived from lower layers plus versioned logic. Every layer has a clearly named owner in ARCHITECTURE.md.

### Raw (Derivation Layer)

The source artifact as received. Immutable. Owned by Ingestion.

### Normalized (Derivation Layer)

Canonical text and structure. Re-derivable from Raw plus the Document Processing DerivationRun. Owned by Document Processing.

### Enriched (Derivation Layer)

Entity and Speaker attribution, Segment and Utterance tagging, ThemeInstances. Re-derivable from Normalized plus the appropriate enrichment DerivationRuns. Ownership is shared across Entity Resolution and relevant parts of Heuristic Analysis and Learned Analysis.

### Analytical (Derivation Layer)

Heuristic features, learned features, Baselines, comparisons. Re-derivable from Enriched plus the respective DerivationRuns. Ownership is shared across Heuristic Analysis, Representation, Learned Analysis, and Baseline Maintenance.

### Signal (Derivation Layer)

Emitted Signals with Basis and Evidence. Re-derivable from Analytical plus the Fusion Engine's DerivationRun. Owned by the Fusion Engine and the Signal Store.

Layer boundaries are not rigid; they describe a direction of dependency, not a strict partition.

---

## Core Properties And Principles

### Explainability

The property that every surfaced output is traceable to source text, structural rules, and model-derived scores as applicable (CONTEXT §3.3). Not a binary property; it is maintained continuously at every stage of the pipeline.

### Traceability

The specific mechanism by which Explainability is achieved: the ability to follow any surfaced output back to the inputs, rules, and scores that produced it. Required of every Signal (CONTEXT §11).

### Critical-Path Isolation

The system-wide invariant that no critical-path component depends on an external LLM API (CONTEXT §6.1).

Exhaustive test enforcement is infeasible under the low-capital constraint; the invariant is **structurally enforced and audit-observed**. Peripheral tooling (offline research, evaluation tooling) that sits outside the critical path is not forbidden but must be clearly out-of-path; any emerging critical-path-like use must be caught by dependency audit.

### Structured Skepticism

The project's commitment to avoiding overconfident inference, causal claims from weak correlations, and sentiment reductionism (CONTEXT §3.4). A design discipline rather than a user-interface treatment.

### Temporal Reasoning

Analysis that treats Documents as part of a sequence rather than as isolated inputs. Mandatory in this system (CONTEXT §11).

### Cross-Document Comparison

Analysis that brings multiple Documents into direct comparison, whether across time for the same Entity or across Sources at the same time. A core capability (CONTEXT §11; SCOPE's Cross-Source Analysis).

### Structured Output

An output that combines a ranked Signal, explanatory context, and supporting excerpts (CONTEXT §9). The confirmed output shape for the system.

### Evidence

The source-text excerpts and metadata that support a Signal. Evidence is required for every Signal (CONTEXT §3.3, §9).

Represented in the data model as Evidence records referencing Spans (DATA_MODEL.md).

### Context Over Isolation

The principle that no Document is interpreted independently (CONTEXT §3.1). Every statement exists within a historical and cross-source context.

### Ranked Signal

A Signal that has been assigned a position in a prioritized set. The fact that Signals are ranked is confirmed (CONTEXT §9); the ranking methodology is owned by NARRATIVE_ANALYSIS.md and EVALUATION.md.

---

## Data And Domain Terms

### Earnings Call Transcript

A transcribed record of an earnings call, typically covering prepared remarks and a Q&A section. The committed initial domain for v1 (CONTEXT §8; SCOPE Initial Scope).

### Document

A single ingested text artifact, associated with its Source, Entity, and temporal metadata. The unit of ingestion.

A base concept; specific Document types (Transcript, Filing, Press Release, News Article) extend it with type-specific structure. In v1 only the Transcript subtype is elaborated.

### Transcript

The v1 Document subtype: an earnings call transcript. Contains a sequence of Segments (prepared remarks, Q&A) and a sequence of Utterances, each attributed to a Speaker.

### Segment

A structurally meaningful region of a Document — for a Transcript, sections such as prepared remarks or Q&A. Identified by Document-scoped ordinal and a type label.

### Utterance

A single speaker turn within a Transcript. Attributed to a Speaker and bounded within a Segment. An Utterance is itself a Span and is the default locus for Evidence citations in Transcripts.

### Span

The primitive unit of evidence: a locus within a Document's normalized text, identified with sufficient precision to be unambiguously re-resolved.

Span precision is source-type appropriate: for Transcripts, at least Utterance-bounded and potentially finer.

Every Evidence record references one or more Spans. Every Signal references Evidence, which references Spans.

### Locus Map

The bidirectional correspondence between characters in Raw and Normalized text that preserves Span precision through normalization. Owned by Document Processing.

### Default Normalized Artifact

The currently-preferred Normalized version for a Document when multiple Normalized artifacts exist (for example, after re-normalization under a new Normalization DerivationRun).

### Within-Document Speaker Handle

A Document-scoped Speaker label produced by Document Processing, distinct from a canonical Speaker Canonical Identifier which is Entity Resolution's output. Reconciliation of handles to canonical Speakers may be imperfect; reconciliation confidence is recorded.

### Entity

The subject of a financial narrative. In v1, typically a public company. In later domains, may include industries, issuers, or other canonical subjects.

Entities anchor comparisons over time. Documents concern an Entity; Speakers are associated with an Entity; Baselines are maintained per Entity; Signals name a subject Entity.

### Speaker

An individual whose statements are attributed within a Transcript (CONTEXT §5.3). Associated with an Entity. Speaker attribution is required to support Confidence Shift and behavioral communication profiling.

### Source

The origin of a Document — a specific publisher, filing channel, or transcript provider. Source identity is required for cross-source analysis (CONTEXT §11; SCOPE's Cross-Source Analysis).

### Theme

A recurring topic, concept, or strategic emphasis the system tracks across a narrative over time. Themes may be human-curated, discovered by heuristic rules, or proposed by unsupervised learned analysis (CONTEXT §5.4).

Theme identity is stable across Documents once established. Theme prominence for an Entity varies over time.

*Theme curation and promotion workflow is owned by NARRATIVE_ANALYSIS.md.*

### ThemeInstance

An occurrence of a Theme within a Document. The unit that supports Omission tracking, Narrative Drift, and similar comparisons.

A ThemeInstance references the Theme, the Document, and one or more Spans.

### NarrativeState

A point-in-time snapshot of an Entity's narrative, suitable for reconstructing what the narrative looked like as of any past Effective Time.

Aggregates recent Documents, Themes, and relevant Baselines for the Entity.

*Materialization strategy is deferred to downstream infrastructure work.*

### DerivationRun

A named, versioned instance of a derivation process — normalization, feature extraction, learned analysis, fusion. Every derived artifact references the DerivationRun that produced it.

DerivationRuns are immutable once created. Re-derivation under new logic produces a new DerivationRun. A Signal's Basis references DerivationRuns for both heuristic and learned contributions and for the fusion step.

Named sub-types used across the data pipeline:

* **Acquisition DerivationRun** — owned by Ingestion's upstream boundary (DATA_ACQUISITION.md)
* **Ingestion DerivationRun** — owned by Ingestion
* **Normalization DerivationRun** — owned by Document Processing
* **Entity Resolution DerivationRun** — owned by Entity Resolution

### Content Fingerprint

A conceptual summary of an artifact's content sufficient to recognize byte-level identity. Used by Ingestion for non-silent deduplication — duplicates are recognized and recorded rather than dropped.

### Quarantine

A Document- or derivation-layer state indicating a required stage could not complete. Quarantined artifacts are recorded and preserved, not dropped, consistent with immutability.

### Licensing Posture

The system-level classification of a Source's terms for operational compatibility. Three canonical postures:

* **Training-Compatible** — the Source's terms permit training use
* **Analytical-Only** — the Source's terms permit analytical use but not training
* **Incompatible-Or-Ambiguous** — the Source's terms are incompatible or not clearly compatible

Licensing Posture is carried with artifacts through the derivation layers (see Posture Carrying).

*Owned by DATA_ACQUISITION.md.*

### Source Terms Posture

The operational discipline governing how a Source is used: rate limits honored, attribution respected, licensing posture enforced. A narrower, operational-posture-level notion than Licensing Posture (above).

### Sensitivity Class

The four operational sensitivity classes used by SECURITY_AND_PRIVACY.md:

* source text
* derived analytical state
* model weights and corpora
* user-side state

Each class has its own handling posture; the system is designed so cross-class leakage does not occur silently.

### Posture Carrying

The rule that derived artifacts inherit the most restrictive Licensing Posture among their upstream dependencies. A Signal derived from an Analytical-Only Source is itself Analytical-Only for downstream purposes.

### Semantic Retrieval

Retrieval over precomputed embeddings at Utterance or Segment scope. V1-scoped. Owned by SEARCH_AND_RETRIEVAL.md; depends on Representation outputs.

### Temporal Regularity

The degree to which a domain produces documents on a predictable schedule. Cited as a virtue of earnings call transcripts (CONTEXT §8).

### Historical Depth

The length of the historical record available for an Entity. A prerequisite for meaningful temporal comparison (CONTEXT §8). Insufficient Historical Depth produces Baseline Thinness.

Historical Depth is a property of the data available. Baseline Thinness is a property of a constructed Baseline (which may be thin even when Historical Depth is sufficient, depending on construction choices).

### Data Domain

A category of financial text source. The v1 committed domain is earnings call transcripts; other domains are deferred (SCOPE Data Domains; CONTEXT §8).

---

## Pipeline And Operations Terms

### Pipeline Version

A pin across DerivationRuns defining a reproducible pipeline state. Load-bearing for replay and as-of semantics under re-derivation: given a Pipeline Version and the Raw inputs, the system can reproduce the exact derived artifacts that Pipeline Version produced.

The named mechanism by which historical replay is reproducible (CONTEXT §11).

*Owned by EVENTS_AND_PIPELINES.md.*

### Canary Emission

Installing a new DerivationRun on a bounded subset of new Documents before full-flow adoption. A conservative rollout pattern compatible with the low-capital posture.

### Shadow Run

Executing a candidate DerivationRun in parallel with the current one, storing outputs for comparison without emitting to the Signal Store. Used to evaluate a change's effect before it affects downstream artifacts.

### Replay

Re-processing an older Document set under current DerivationRuns to confirm behavior on known history.

Distinct from **re-derivation**, which is about regenerating a specific artifact. Replay is about running a collection under the current Pipeline Version.

### Golden-Set Replay

Replaying the system against a frozen Document + Signal corpus to surface diffs after a change. The diff produced is a **test artifact**, not a quality judgment — quality judgment on the diff belongs to EVALUATION.md.

---

## Governance Terms

### Tombstone

A governance record making an artifact's content inaccessible while preserving its existence and provenance. Tombstones honor immutability: no artifact is deleted; access is revoked via the Tombstone.

### Redaction Record

A Span-scope analog of a Tombstone, making partial content within an artifact inaccessible while preserving the artifact itself and its provenance.

### Source Quality

The tracked aggregate of acquisition-criteria performance for a Source over time. Distinct from Signal Quality, which is evaluated at the Signal level by EVALUATION.md.

### Ingestion Quality

The tracked aggregate of ingestion-stage outcomes per Source over time. Distinct from Source Quality (which is about the Source itself) and from Signal Quality.

### Governance Record

Any immutable record produced by a governance operation: quality sample, Licensing Posture reclassification, Tombstone, Redaction Record, Pipeline Version promotion. Governance Records are themselves provenance-tracked.

---

## Observability And Failure Terms

### Document Journey

The per-Document operational view of the pipeline: each stage a Document passed through, each DerivationRun applied, each timing, each success or failure. Distinct from signal-level traceability in the Evidence & Provenance Store: Document Journey is the operator's view; Evidence is the user's view.

*Owned by OBSERVABILITY.md.*

### Component Health

The per-component operational view: throughput, latency, error rate, output characteristics. Covers all ARCHITECTURE.md components. Distinct from Signal-quality evaluation.

### Derivation Traceability

The DerivationRun-centric operator view: the operational surface into the Evidence & Provenance Store. Answers "which DerivationRun produced this artifact" operationally.

### Fatal Failure Mode

A failure mode threatening at least one load-bearing invariant. Must stop the pipeline at the relevant scope and restore the invariant on recovery. Defined in FAILURE_MODES.md.

### Absorbable Failure Mode

A failure mode that threatens no load-bearing invariant; partial operation is safe during investigation. Defined in FAILURE_MODES.md.

---

## Model And Evaluation Terms

### In-House Model

A model the project trains, owns, and operates on its own infrastructure (CONTEXT §6). Contrasted with external API models, which are excluded from critical paths.

### Specialized Model

A model scoped to a narrow task, in the stack described by CONTEXT §6.2. Preferred over a single large general-purpose model.

### Domain-Adapted Representation Model

A representation model adapted to financial text, referenced conceptually in CONTEXT §6.2. Specific architecture and adaptation strategy are owned by MODEL_STRATEGY.md.

### Model Family

A grouping of conceptually related models in MODEL_STRATEGY.md's stack: Representation, Analytical, Generative.

### Representation Learning

The process by which the ML Layer derives semantic representations of financial text (CONTEXT §5.1).

### Latent Structure

Patterns in financial text that are not explicitly labeled or heuristically identifiable but are detectable through learned representations (CONTEXT §5.2).

### Behavioral Communication Profile

A model of a specific Entity's or Speaker's baseline communication behavior, against which deviations can be measured (CONTEXT §5.3; SCOPE's Behavioral Communication Profiling).

Privacy note: Speaker Behavioral Communication Profiles are derived from public attributed speech but aggregate per-person communication patterns. Treated as a privacy-adjacent artifact in SECURITY_AND_PRIVACY.md.

### Degraded Mode

The emission posture of the Fusion Engine when one or more model components are unavailable or known-degraded. Commentary may be withheld, Confidence may be reduced, and the Signal may be held at Candidate rather than Surfaced.

*Semantics owned by MODEL_STRATEGY.md; use in lifecycle transitions owned by NARRATIVE_ANALYSIS.md.*

### Grounding Check

A mechanism applied to generative outputs (principally Commentary) that anchors generated text to Basis and Evidence. Commentary that fails its Grounding Check is not emitted.

*Owned by MODEL_STRATEGY.md.*

### Evaluation Harness

The component in ARCHITECTURE.md that samples Signals and Candidate Signals for human review, records reviewer feedback, and hosts the promotion workflow for the Candidate-Type Pool. Acknowledged as an evolving artifact (CONTEXT §14).

*Specific evaluation methodology is owned by EVALUATION.md.*

### Review Rubric

The structured instrument reviewers use to evaluate surfaced Signals and Candidate Types. A first-class artifact of the Evaluation Harness. Expected to evolve alongside the harness (CONTEXT §14).

### Reviewer Cohort

The defined group of reviewers who apply the Review Rubric, with calibration procedures and feedback records maintained over time.

### Reviewer Feedback Record

The per-Signal (or per-Candidate-Type) record of reviewer judgment. Immutable once recorded. Aggregates inform threshold calibration and lifecycle transitions.

### Validated Quality

The operational definition of "signal quality has been validated on the initial domain" — the gate SCOPE.md implicitly uses for domain expansion. Explicitly defined in EVALUATION.md so the gate can be applied as a judgment rather than a threshold.

### Human Review

Structured evaluation of surfaced Signals by human readers; the primary evaluation mode in early development (CONTEXT §14).

### Dogfooding

Internal use of the system on known historical narratives as a form of qualitative evaluation (CONTEXT §14).

### Ground Truth

A reliable reference against which outputs can be judged. For many Signal types in this project, clean ground truth is absent (CONTEXT §13.3); the absence is treated as a central challenge rather than a solved problem.

---

## Experimentation Terms

### Experiment Specification

The immutable artifact describing an experiment: hypothesis, method, scope, success and failure criteria, expected cost, rollback plan. Registered at experiment creation and carried through graduation or rejection.

*Owned by EXPERIMENTATION.md.*

### Historical Replay

The substrate that experiments run on: re-processing bounded historical windows under the experiment's proposed DerivationRun changes and comparing against the current system's outputs. Exploits the re-derivability invariant rather than running parallel live pipelines.

Distinct from general **Replay** (Pipeline And Operations Terms): Historical Replay is specifically the experimental substrate.

### Experiment Registry

The durable institutional-knowledge store of Experiment Specifications, outcomes, Graduation Reviews, and findings. Enables experiments to be searched, cited, and learned-from across contributors.

### Graduation Review

The review step by which an experiment moves from running to adopted (or not). Four outcomes: graduate, reject, hold, narrow. The review is a distinct act from the experiment's running; it is not automated.

### Narrow Graduation

A Graduation Review outcome: a change is promoted for a bounded scope smaller than the experiment's original hypothesis (for example, adopted for one Entity class but not all). Open question about whether this permits Entity-scoped DerivationRun sets is tracked as a cross-document concern.

---

## Trust And Safety Terms

### Drift Watch

A standing vigilance list paired with VISION.md §Failure Modes. Enumerates the categories of drift the project watches against: drift toward sentiment reduction, drift toward prediction framing, drift toward hype language, drift toward coverage maximization at the cost of quality.

*Owned by ETHICS_AND_LIMITATIONS.md.*

---

## Auxiliary Process Terms

### Ingestion

The process of acquiring, attributing, and recording source artifacts (SCOPE's Data Ingestion; ARCHITECTURE.md Ingestion component).

*Acquisition strategy is owned by DATA_ACQUISITION.md. Parsing specifics are owned by INGESTION_SPEC.md.*

### Document Understanding

The process of interpreting a Document in context: Entity identification, topic extraction, relationship identification, statement segmentation, semantic interpretation, and contextual understanding of financial terminology (SCOPE's Document Understanding).

### Narrative Tracking

The maintenance of continuity across time for a given Entity: recurring Theme tracking, historical comparison, and strategic priority tracking (SCOPE's Narrative Tracking).

### Comparative Analysis

The bringing together of Documents across time, document types, Entities, industries, communication channels, or Speakers for the purpose of detecting meaningful change (SCOPE's Comparative Analysis).

### Signal Detection

The process of identifying candidate Signals from textual and contextual patterns (SCOPE's Signal Detection). A pipeline concern distinct from the definition of any given Signal type.

### Insight Presentation

The surfacing of Signals and their supporting context to the user (SCOPE's Insight Presentation).

*Specific design is owned by USER_EXPERIENCE.md.*

---

## Deliberate Non-Definitions

The following terms are deliberately not used as formal vocabulary in this project. Where a downstream document is tempted to use them, the alternative below should be used instead.

### Sentiment / Sentiment Score

The project rejects sentiment reduction (CONTEXT §3.4, §10; SCOPE's Design Principles). Where downstream work is tempted to reach for "sentiment", the appropriate alternative is Confidence Shift (for stance toward claims), Narrative Drift (for change in framing), or a more precise Signal type.

### Prediction / Forecast

The project is not predictive (CONTEXT §10; SCOPE Non-Goals). Surfaced outputs describe observed change, not future state. Where "prediction" is tempting, Signal is the correct term.

### Alpha / Alpha Signal

The project is not a trading or alpha-generation system (SCOPE Non-Goals). "Signal" in this project has a specific meaning and is not interchangeable with alpha-generation terminology.

### Recommendation

The project does not recommend actions (CONTEXT §10). Outputs surface information for a human to interpret, not instructions to follow.

### Trading Signal / Buy-Sell Signal

Not in scope (SCOPE Non-Goals). A Signal in this project is a narrative Signal, not a trade instruction.

### AI / AI-Powered

Marketing-adjacent language that obscures the distinction between the Heuristic Layer, the ML Layer, and the Fusion Layer. Downstream documents should name the specific component or layer rather than reach for "AI".

### Black-Box Model

Any model whose outputs cannot be traced to their inputs. Excluded by construction (CONTEXT §3.3, §6.4). The project does not use black-box models in critical paths.

### Autonomous Agent

Not in scope (CONTEXT §10; SCOPE Non-Goals). The system informs a human; it does not act.

### Accuracy

Avoided as a primary evaluation term. CONTEXT §14 explicitly rejects prediction accuracy as the measure of success. Where "accuracy" is tempting, prefer the specific qualitative dimensions listed in CONTEXT §14 — usefulness, clarity, consistency over time, reduction of cognitive load, and surfacing of non-obvious narrative changes.

### Aggregate Signal Score

The project does not emit cross-type or cross-entity aggregate Signal scores (SCOPE Non-Goals). Signal Strength is type-relative.

### Completeness (as a claim)

The project does not claim coverage is complete. Absence of a Signal is not absence of risk (ETHICS_AND_LIMITATIONS.md).

---

## Flagged For Downstream Ownership

The following terms are referenced in this document but require an architectural or analytical decision to be fully defined. They are listed here so that downstream documents can take ownership.

* Signal Strength representation — owned by SIGNAL_DEFINITIONS.md and MODEL_STRATEGY.md.
* Signal Confidence representation — owned by SIGNAL_DEFINITIONS.md and MODEL_STRATEGY.md; surface to users owned by USER_EXPERIENCE.md.
* Basis Disagreement detection and resolution — owned by MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md.
* Signal Rank methodology — owned by NARRATIVE_ANALYSIS.md and EVALUATION.md.
* Baseline construction method and numeric thresholds — owned by NARRATIVE_ANALYSIS.md.
* Thin-History Policy numeric thresholds — owned by NARRATIVE_ANALYSIS.md.
* Candidate-Type Pool promotion workflow — owned by EVALUATION.md.
* Commentary generation method — owned by MODEL_STRATEGY.md (content) and USER_EXPERIENCE.md (surface).
* Specific model architectures and training strategies — owned by MODEL_STRATEGY.md.
* Operating mode resolution (deliberate/batch/on-demand) — owned by ARCHITECTURE.md Operating Posture and EVENTS_AND_PIPELINES.md.
* Evaluation methodology beyond human review — owned by EVALUATION.md.
* Data acquisition strategy — owned by DATA_ACQUISITION.md.
* Pipeline Version promotion workflow — owned by EVENTS_AND_PIPELINES.md (pipeline side) and DATA_GOVERNANCE.md (governance side).

---

## Relationship To Other Documents

* CONTEXT.md and SCOPE.md are authoritative where they speak; this document formalizes the vocabulary they, VISION.md, and ASSUMPTIONS.md already use.
* VISION.md uses this vocabulary.
* ASSUMPTIONS.md uses this vocabulary.
* ARCHITECTURE.md, DATA_MODEL.md, and SIGNAL_DEFINITIONS.md use this vocabulary.
* All Wave 2 documents use this vocabulary.
* DECISION_LOG.md records project-level decisions, including those that update or extend entries here.
* Downstream documents should treat this glossary as canonical. Where a needed term is missing, it should be added here rather than redefined inline.
