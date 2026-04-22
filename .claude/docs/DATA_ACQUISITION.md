# DATA_ACQUISITION.md

## Purpose Of This Document

DATA_ACQUISITION.md defines how source documents enter the system: where they come from, under what terms, with what quality properties, and under what posture toward cost and cadence.

This document is conceptual. It does not select vendors, negotiate contracts, or specify file formats. It defines the posture within which downstream ingestion and data-partnership decisions are made.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Downstream handling of the artifact once it has arrived is owned by [INGESTION_SPEC.md](./INGESTION_SPEC.md).

---

## How To Read This Document

* acquisition is described at the level of posture and pipeline, not at the level of specific sources
* the boundary against [INGESTION_SPEC.md](./INGESTION_SPEC.md) is stated explicitly and held throughout
* licensing is treated as a posture, not a legal specification; legal review is deferred and flagged
* new vocabulary introduced here is flagged for glossary extension in the closing summary

---

## Guiding Commitments

Inherited from upstream documents and held as invariants for acquisition:

* v1 initial domain is Earnings Call Transcripts (CONTEXT §8; SCOPE Initial Scope)
* the in-house model ownership posture (CONTEXT §6) constrains which licensing terms are compatible with training use
* the low-capital operating posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5) bounds the scale and cost of acquisition
* acquisition is feasible in principle (ASSUMPTIONS D1) but treated here as an engineering concern, not a background task (ASSUMPTIONS T5)
* v1 is English-first (CONTEXT §8 Language Posture); other languages are a deferred concern
* multi-modal inputs (audio-to-text, image-to-text) are out of v1 scope (ASSUMPTIONS D8; SCOPE Deferred)

---

## Boundary Against INGESTION_SPEC.md

The boundary between acquisition and ingestion is the moment an acquired artifact first exists as a Raw artifact within the system, attributed to its Source and assigned an Observation Time.

Anything upstream of that moment — where the artifact came from, through what channel, under what licensing terms, and with what quality properties — is DATA_ACQUISITION.md's concern.

Anything downstream of it — how the artifact is parsed, how its Document identity is established, how it is normalized into canonical text and structure, and how it is landed into the Raw and Normalized layers — is [INGESTION_SPEC.md](./INGESTION_SPEC.md)'s concern.

This boundary statement is restated identically in [INGESTION_SPEC.md](./INGESTION_SPEC.md) and is held as a cross-document invariant.

---

## Source Landscape For Earnings Call Transcripts

The v1 domain is supplied by several conceptual source categories. Each is described by its acquisition shape, the properties it tends to bring, and the trade-offs it presents. No specific publisher, provider, or platform is named here.

### Issuer Channels

Transcripts or near-transcripts published by the Entity itself — for example, on an investor-relations page, as a recording, or as a formal disclosure. Often the most authoritative source of the Entity's own words; may lag in availability, may vary in fidelity, and may not be released for all Entities.

### Regulatory Channels

Public filing channels that publish or reference call content as part of formal disclosure. Typically high-fidelity for what they contain; typically constrained to subsets of what was said; typically under a licensing posture permissive for analytical use.

### Third-Party Transcript Providers

Dedicated providers whose product is the transcript itself. Typically broader coverage and faster availability than issuer channels; typically richer speaker attribution and segmentation; typically subject to provider-specific licensing terms whose compatibility with the in-house model ownership posture must be evaluated per provider.

### Aggregators Of Public Content

Platforms that collect and republish content sourced from the above. Typically broader coverage with uneven fidelity; typically the hardest category to evaluate for licensing posture because the aggregator's rights may not be transparent.

### Direct Capture

Capture of the call event itself, followed by transcription. Theoretically possible but operationally disproportionate under the low-capital posture and outside v1 scope. Deferred.

---

## Source Landscape Trade-Offs

The source categories above are not substitutes for one another. The trade-offs are:

* **fidelity** — issuer and regulatory channels tend to produce the highest-fidelity text but with narrower scope; third-party providers typically offer richer structure (Speaker attribution, Segment boundaries) at the cost of licensing constraints
* **coverage** — third-party providers typically offer the broadest Entity coverage; issuer channels cover only the Entity itself; regulatory channels cover only what is filed
* **availability latency** — varies across categories; acquisition posture under CONTEXT §8's quarterly cadence tolerates a latency measured in days, not minutes (ASSUMPTIONS U6)
* **licensing compatibility** — described below; this is the dimension with the tightest coupling to CONTEXT §6

The practical v1 posture is expected to compose multiple source categories rather than rely on a single one. Composition strategy is deferred.

---

## Licensing Postures

Licensing is a property of the Source, not a property of a single artifact. Each Source has a licensing posture that governs what the system may do with artifacts from that Source. The posture has three conceptual categories.

### Training-Compatible

Terms permit the Source's text to be used for training in-house models, including the Domain-Adapted Representation Model and task-specific specialized models. Compatible with CONTEXT §6 in full.

### Analytical-Only

Terms permit derived analysis, Signal emission, and Evidence citation, but do not permit the Source's text to be used as training data. Derived artifacts (features, Baselines, Signals) may be produced from the text; models may not be trained on it.

### Incompatible Or Ambiguous

Terms prohibit one or both of the above uses, or are unclear enough that use would depend on interpretation. Treated as excluded from v1 use until the posture is clarified.

---

## Licensing-Posture Rules For V1

The v1 posture follows from CONTEXT §6 and ASSUMPTIONS D6:

* Sources in the Training-Compatible category are the preferred v1 Sources.
* Sources in the Analytical-Only category are acceptable as Evidence Sources for Signals but are not eligible as training input; the system must be able to enforce this distinction technically (this is a governance requirement, detailed in [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)).
* Sources in the Incompatible Or Ambiguous category are excluded from v1 until their posture is clarified or they are reclassified.

The classification of a given Source is a deliberate operation with failure modes. A Source without a determined posture is not Incompatible by default; it is a queryable state of its own ("unclassified") and blocks ingestion until classified.

*Specific licensing negotiation, contract language, and legal review are deferred to non-technical work. This document specifies only the posture the system operates under.*

---

## Acquisition Pipeline (Conceptual)

Acquisition is conceptually a pipeline of stages that end at the boundary with [INGESTION_SPEC.md](./INGESTION_SPEC.md). The pipeline is described at the conceptual level; physical implementation is deferred.

### 1. Source Identification

Identification of candidate Sources, their licensing posture, their coverage, and their quality properties. Produces a Source record in the system's model (DATA_MODEL.md §Source).

### 2. Coverage Commitment

For each acceptable Source, a commitment to the Entities for which that Source will be acquired, and to the historical depth retained (see below).

### 3. Channel Establishment

Establishment of a durable channel by which new artifacts appear — an API, a feed, a scheduled poll, or a one-off historical pull. The channel itself is a property of the Source, recorded alongside the Source.

### 4. Artifact Retrieval

Retrieval of a specific artifact by the channel. This stage terminates at the boundary: once retrieval has produced a byte sequence attributed to the Source, ingestion begins.

### 5. Source Quality Sampling

An observational stage running alongside retrieval: Source quality metrics (completeness, attribution fidelity, punctuation integrity, structural regularity) are sampled over time per Source. Results feed [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)'s quality tracking, not this document.

The pipeline is not assumed to be real-time. It runs on a deliberate cadence appropriate to the domain.

---

## Historical Depth

For each committed Source and each covered Entity, the system commits to a target historical depth — the length of retained history for that Entity from that Source.

### Target Depth For V1

V1's target is a historical depth sufficient to establish meaningful Baselines for the Signal types that depend on them (Narrative Drift, Confidence Shift, Structural Anomaly; see [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)). The sufficiency criterion is qualitative at this stage: enough quarterly Transcripts to support cross-period comparison with acceptable Baseline thinness.

Specific minimum-period thresholds are deferred to NARRATIVE_ANALYSIS.md, which owns the numeric thinness thresholds. This document commits the shape — "enough depth for Baselines to be meaningful" — not the numbers.

### Thin-History Policy Coordination

Not every covered Entity will meet the target depth. The Thin-History Policy, committed in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and extended here, governs onboarding of such Entities:

* Entities below the target depth are still acquired and ingested; their status as "thin" is a queryable property of their Baselines, not a reason to withhold acquisition
* Signals produced for thin-history Entities carry the Confidence implications already committed in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
* the acquisition posture does not hide thin-history Entities; it exposes their thinness so downstream consumers can reason about it

Acquisition is not the locus of reliability preference — emission is. This document's job is to ensure thinness is visible to the system, not to filter thin Entities out at acquisition time.

---

## Quality Criteria For An Acceptable Source

A Source is acceptable for v1 use when its artifacts tend to exhibit the following properties. None of these is a sharp cutoff; a Source is evaluated on the balance.

### Speaker Attribution

Utterances can be attributed to a specific Speaker with acceptable precision. Attribution may be provided by the Source or reconstructable from structural cues, but its absence is a meaningful quality concern given that Confidence Shift and Behavioral Communication Profiling depend on it (ASSUMPTIONS D3).

### Punctuation Fidelity

Sentence and clause boundaries are recoverable from the text. Punctuation need not be perfect, but the text must support segmentation into Utterance-internal structure where needed.

### Completeness

The text reasonably covers the call event: prepared remarks and Q&A are both present, or their absence is known and attributable. Partial transcripts are acceptable where their scope is known and recorded.

### Structural Regularity

Segment boundaries (prepared remarks vs. Q&A, speaker turns) are recoverable from the text. This is the property CONTEXT §8 and ASSUMPTIONS D2 rely on for heuristic segmentation.

### Normalization Stability

The Source's conventions — how Speaker names are formatted, how Segments are delimited, how time references are rendered — are stable across artifacts and over time. Instability is not disqualifying, but it is tracked, because Source-convention drift creates structural-anomaly false positives ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)'s Structural Anomaly false-positive patterns).

### Provenance Transparency

The Source exposes enough metadata — publication time, native identifier, edits or retractions — that the three mandatory Document timestamps (event, document, observation) can be established reliably at ingestion.

---

## Source Evaluation And Onboarding

New Sources are not added opportunistically. Addition is a deliberate operation with the following shape.

* a Source candidate is identified, and its licensing posture is classified (Training-Compatible, Analytical-Only, or Incompatible Or Ambiguous)
* if the posture is acceptable, the Source's quality is sampled against the criteria above, using a representative sample of artifacts
* if the sample passes, the Source is recorded, its channel is established, and its initial coverage commitment is set
* the Source is added to the ongoing quality-monitoring loop defined in [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md); Source quality is not a one-time check

Deprecation of a Source — because its posture changed, its quality degraded, or it ceased operation — follows the mirror process. Deprecation does not delete prior artifacts from that Source; those remain queryable historical records, subject to deletion and retention policy owned by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md).

---

## Interaction With The Low-Capital Constraint

Acquisition has a direct cost dimension (channel cost, provider fees, storage) and an indirect one (ongoing quality monitoring, Source maintenance). Under ASSUMPTIONS T3 and H5, acquisition must not demand continuously-running infrastructure:

* channels are expected to be pull-oriented or low-frequency push, not continuous stream subscriptions
* acquisition cadence is aligned to the domain's natural cadence — quarterly for Earnings Call Transcripts — rather than to real-time availability
* re-acquisition of historical material is a bounded one-time operation per Source, not an ongoing expense
* Source quality sampling is periodic, not continuous

If a Source's only available channel is a continuously-running subscription whose cost is disproportionate to the signal gain it offers, that Source is not acquired in v1. This is a posture, not a prohibition; specific Sources are evaluated on the balance.

---

## What Acquisition Produces

Acquisition produces, at the boundary with [INGESTION_SPEC.md](./INGESTION_SPEC.md):

* a byte sequence or equivalent artifact attributed to a specific Source
* the Source's canonical identifier
* the Source-native identifier for the artifact (if the Source provides one)
* the retrieval channel and the acquisition timestamp
* the acquisition DerivationRun reference (the versioned record of the acquisition stage)
* the Source's licensing posture, carried forward so downstream components can honor it

No parsing, no segmentation, no Entity attachment, and no quality judgment have happened yet. Those are downstream concerns.

---

## What This Document Is Not

* not an ingestion parser specification (owned by [INGESTION_SPEC.md](./INGESTION_SPEC.md))
* not a normalization specification (owned by [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md))
* not a storage specification (storage technology is deferred to downstream infrastructure work)
* not a legal document; licensing is expressed as a system posture, not as contract language
* not a vendor selection document; specific Sources may inform this posture but are not committed here
* not a retention or deletion specification (owned by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md))

---

## Deferred Decisions

Named deferrals from this document, with owners where applicable:

* specific Source selection and vendor analysis — deferred to dedicated data-partnership work outside this document
* contract terms, legal review, and compliance review — deferred to non-technical work
* numeric historical-depth thresholds — deferred to NARRATIVE_ANALYSIS.md (which also owns the numeric thresholds for the Thin-History Policy in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
* storage technology and physical layout of acquired artifacts — deferred to downstream infrastructure work
* multi-modal acquisition (audio, video) — deferred beyond v1 (SCOPE Deferred; ASSUMPTIONS D8)
* multilingual acquisition — deferred beyond v1 (CONTEXT §8 Language Posture)
* retention and deletion policies for acquired artifacts — [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)
* ongoing Source quality monitoring mechanics — [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)
* specific channel and polling mechanics — downstream infrastructure work

---

## Open Questions

Flagged so downstream decisions do not silently take a position.

* What is the target covered-Entity set for v1? Acquisition posture is coverage-bounded; the specific bound is not committed here and is a project-scoping decision outside this document's mandate.
* How is re-classification of a Source's licensing posture handled operationally? The mechanism is a governance concern ([DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)) but the upstream signal originates at acquisition.
* How is Source redundancy handled — when the same call is acquired from two Sources with differing fidelity? Deduplication and update semantics are owned by [INGESTION_SPEC.md](./INGESTION_SPEC.md); this document only commits that Source identity is preserved, not collapsed.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies the beliefs (D1, D3, D5, D6, D7, D8, T3, T5, U6) this document depends on.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; terms introduced here that are not yet in the glossary (Licensing Posture, Source Quality, Pipeline Version, Acquisition DerivationRun) are flagged for extension in the cluster's closing summary.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the Ingestion component that this document feeds; acquisition sits immediately upstream of Ingestion and does not overlap with it.
* [INGESTION_SPEC.md](./INGESTION_SPEC.md) takes over at the stated boundary; the boundary is held identically in both documents.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) owns retention, deletion, licensing enforcement, and ongoing Source quality monitoring for the artifacts this document brings in.
* MODEL_STRATEGY.md (deferred) inherits the licensing-posture constraint: Training-Compatible Sources are eligible as training input; other postures are not.
