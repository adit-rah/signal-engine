# SIGNAL_DEFINITIONS.md

## Purpose Of This Document

SIGNAL_DEFINITIONS.md defines the authoritative structural representation of Signals: what every Signal is, how each of the five confirmed initial types (CONTEXT §4) is operationally elaborated, and how the taxonomy is extended.

This document is the contract between the Intelligence Core ([ARCHITECTURE.md](./ARCHITECTURE.md)'s Fusion Engine, Heuristic Analysis, and Learned Analysis), downstream consumers (API Boundary, Evaluation Harness), and the user-facing surface (USER_EXPERIENCE.md).

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Signal data shape is defined in [DATA_MODEL.md](./DATA_MODEL.md).

---

## How To Read This Document

* Signal Anatomy describes what every Signal has, regardless of type
* each signal type section provides operational definition, required evidence, strong-vs-weak criteria, and common false-positive patterns
* Signal Lifecycle describes how Signals move from candidate to retired
* Extension describes how new signal types enter the taxonomy
* scoring formulas, ranking algorithms, and API serialization shapes are not here; deferrals are listed at the end

---

## Signal Anatomy

Every Signal, regardless of type, has the following structural components. Data model representation is in [DATA_MODEL.md](./DATA_MODEL.md); this section describes the anatomy conceptually.

### Identity

A stable, project-owned identifier. Immutable once emitted.

### Type

One of the confirmed initial types (below) or an approved extension. The type is declared at emission and does not change for that Signal record.

### Subject

The Entity the Signal concerns. For types that are Speaker-scoped (Confidence Shift, intra-source Contradiction Event, Speaker-level Structural Anomaly), the Subject is narrowed to an Entity + Speaker pair.

### Temporal Scope

* **subject time** — the time or interval the Signal describes
* **emission time** — when the Signal was produced
* for types that compare to a Baseline, the Baseline's valid-time is carried alongside the Signal's temporal scope

### Basis

The chain of contributions that produced the Signal:

* which heuristic rules contributed, and with what outcomes
* which learned analyses contributed, and with what outputs
* the Fusion Engine's DerivationRun reference
* any Basis disagreement that the Fusion Engine had to resolve

Basis is mandatory on every Signal (CONTEXT §3.3). A Signal whose Basis chain cannot be resolved must not be emitted.

### Evidence

One or more Evidence records referencing Spans. Every Signal carries at least one Evidence record. Evidence is mandatory (CONTEXT §3.3, §9).

### Strength

A representation of how far the observed phenomenon rises above the noise floor for its type. The exact representation — scalar score, discrete band, categorical tier — is deferred. What is invariant:

* Strength is a type-relative statement, not a cross-type ranking value
* Strength is not a probability of anything external (e.g. price movement)
* Strength is bounded; extreme values are exceptional by construction

*Specific Strength representation is deferred to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md.*

### Confidence

A representation of the system's epistemic certainty in the Signal itself — distinct from Strength. High Strength with low Confidence is coherent: the observed deviation is large, but the system is not sure it is real (for example, thin Baseline, contested Basis, or narrow Evidence).

Confidence exists to honor CONTEXT §3.4 structured skepticism. Confidence reflects, at minimum:

* Baseline thinness where the Signal depends on a Baseline
* Basis disagreement between heuristic and learned contributions
* Evidence Span precision and quantity

Confidence is not a probability of correctness; claiming otherwise would violate structured skepticism.

### Lifecycle State

One of: candidate, surfaced, stale, superseded, retired. Semantics are specified below.

### Lineage

References to prior Signals this Signal supersedes (if any) and the Signal that supersedes it (if any). Lineage is populated by lifecycle transitions, not by emission.

### Commentary

A human-readable explanation generated at emission time, describing what the Signal observes and why it is considered meaningful. Commentary is bound to the Signal and is immutable. Every Signal has non-empty Commentary.

*Commentary generation method is deferred to MODEL_STRATEGY.md; user-facing surface of Commentary is deferred to USER_EXPERIENCE.md.*

---

## What A Signal Is Not

Restated from CONTEXT §4 and [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)'s Deliberate Non-Definitions:

* a Signal is not a prediction of future state
* a Signal is not a recommendation
* a Signal is not a sentiment score
* a Signal is not an alpha or trading signal
* a Signal is not a claim of causation

A Signal is an observation about change in a narrative, with traceable Basis and Evidence.

---

## The Confirmed Initial Taxonomy

The five types below are the confirmed initial taxonomy (CONTEXT §4). They are extensible (see Extension below).

Each type section follows the same shape:

* operational definition
* required evidence
* strong vs weak instances
* common false-positive patterns

---

### Narrative Drift

**Operational definition.** A gradual change in an Entity's (or Speaker's) framing, emphasis, or strategic communication, observed across temporally separated Documents. Drift is about *what is said* — topic focus, framing of strategic priorities, emphasis distribution.

A Narrative Drift Signal is the observation that accumulated change exceeds a threshold of meaningfulness relative to the prior Baseline.

**Required evidence.**

* at least one prior Document contributing to the Baseline against which drift is measured
* at least one current Document establishing the drift
* Spans citing the framing elements that changed
* reference to the Baseline's valid-time used for the comparison

**Strong vs weak instances.**

* **strong**: sustained drift over multiple observation periods, consistent across Speakers, visible in multiple framing features (topics, emphasis, priority ordering), and supported by both heuristic and learned Basis contributions
* **weak**: single-observation change detectable only by one analytical method, sensitive to threshold choice, or explainable by a surface-level transcript formatting change

**Common false-positive patterns.**

* boilerplate change — legal or compliance language is updated while narrative framing is unchanged
* formatting change — the transcript provider changes segmentation conventions between periods
* seasonal content — agenda items that naturally shift between quarterly reports
* Speaker turnover — a new Speaker uses different but substantively equivalent framing

For thin-history Entities, Narrative Drift is high-risk for false positives by construction. See the Thin-History Policy below.

---

### Confidence Shift

**Operational definition.** A change in the certainty, hedging, or assertiveness of an Entity's communication — typically narrowed to a specific Speaker — across time. Confidence Shift is about *how something is said*: the density of hedging language, the presence of qualifiers, the movement between assertive and conditional framings.

**Required evidence.**

* at least one prior Document contributing to the Speaker Baseline
* at least one current Document establishing the shift
* Spans exhibiting the shift in certainty-bearing features
* reference to the Speaker Baseline's valid-time

**Strong vs weak instances.**

* **strong**: sustained shift over multiple observation periods from a stable Speaker, visible in multiple certainty features (hedging frequency, conditional framing, direct assertions), consistent with Basis contributions from both heuristic and learned layers
* **weak**: shift detectable only under one analytical configuration, sensitive to sample size, or concentrated in a single topic where external circumstances might explain the shift

**Common false-positive patterns.**

* topic-specific hedging — a Speaker hedges more about a genuinely uncertain subject (for example, guidance during a disclosed disruption); the shift is about the subject, not about the Speaker
* scripted vs. unscripted difference — prepared-remarks Utterances are structurally more assertive than Q&A Utterances; mis-normalizing the two looks like a shift
* reporter or translator artefact — transcription style changes between providers
* novel Speaker — a new Speaker's hedging patterns are mis-read as a shift from the prior Speaker

Distinct from Narrative Drift: Confidence Shift concerns stance, not topic.

---

### Omission Event

**Operational definition.** The disappearance of a previously recurring Theme, priority, or emphasis from an Entity's communication. The unit of measurement is the absence of expected ThemeInstances, not the presence of negating language.

**Required evidence.**

* evidence of prior recurrence — multiple prior Documents containing ThemeInstances establishing the Theme as expected
* the current Document (or sequence of Documents) in which the Theme is absent
* Spans from the prior Documents citing the now-absent Theme (since the current omission cannot itself be cited as text)
* explicit check that the omission is not artefactual — Document scope, Segment structure, or Speaker changes that could explain absence without narrative meaning

**Strong vs weak instances.**

* **strong**: Theme with long and consistent prior recurrence; absence sustained across multiple current Documents; not explained by a change in Document scope; supported by both heuristic recurrence counts and learned semantic absence
* **weak**: Theme with shallow prior recurrence; single-Document absence; correlated with Document scope changes that could independently explain the absence

**Common false-positive patterns.**

* Document scope change — a filing section is moved, removed, or restructured, and the Theme is discussed elsewhere
* compression — a prior recurring Theme is summarized more tersely but is still present at lower Theme prominence
* Speaker change — the Speaker who emphasized the Theme departs; the Theme is now discussed by someone else under different language, evading heuristic recurrence counting
* retirement — a strategic program has genuinely ended and the Entity has disclosed its conclusion elsewhere

Omission Events demand cross-Document context. An Omission Event Signal with single-Document evidence is structurally weak.

---

### Contradiction Event

**Operational definition.** An inconsistency between two or more statements that can be brought into direct comparison, where the statements are judged incompatible rather than merely different.

Contradictions may be:

* **intra-source** — the same Entity (and typically the same Speaker) asserting incompatible claims across time
* **cross-source** — different Sources asserting incompatible claims about the same Entity at roughly the same time

**Required evidence.**

* the two (or more) statements, each with its Spans
* the Documents, Sources, and (where relevant) Speakers
* the comparison judgment — how the statements are brought into comparison, and why they are incompatible rather than merely different
* for intra-source contradictions, the temporal relation

**Strong vs weak instances.**

* **strong**: literal or nearly-literal contradiction on a concrete claim (a numeric figure, a stated commitment), with clear comparability, with both heuristic claim-alignment and learned semantic-incompatibility contributing to Basis
* **weak**: paraphrastic incompatibility where the claims could be reconciled under charitable interpretation; contradiction dependent on a single analytical method; reliant on thin comparison-matching logic

**Common false-positive patterns.**

* updated facts — a subsequent statement corrects an earlier one and discloses the correction; this is an update, not a contradiction
* scope mismatch — claims apply to different periods, segments, or units but are compared as if equivalent
* context loss — the second statement contains qualifying context that reconciles the apparent contradiction; truncated Spans hide the qualifier
* rhetorical vs. committed claims — a hypothetical or illustrative statement is compared to a committed statement

Distinct from Omission: Contradiction is the presence of inconsistent material; Omission is the absence of expected material.

---

### Structural Anomaly

**Operational definition.** An unusual deviation from an Entity's established communication structure — not about content, framing, or certainty, but about the shape of communication. For Transcripts, relevant structural features include length of prepared remarks, ratio of prepared-to-Q&A time, Speaker share, topic distribution across Segments, Segment order, and Q&A answer length patterns.

**Required evidence.**

* the Baseline of expected structural features for the Entity (and Speaker where relevant) with its valid-time
* the current Document's measured structural features
* Spans representative of the structural anomaly (for example, the unusually terse Segment, the unexpectedly long Q&A response, the absent or reordered Segment)

**Strong vs weak instances.**

* **strong**: multiple structural features simultaneously outside Baseline variance; sustained across the current Document rather than isolated to a brief passage; consistent with Basis from both heuristic structural comparison and learned pattern deviation
* **weak**: single-feature deviation; within Baseline variance when adjusted for plausible external factors; explicable by a disclosed operational change (call format change, new compliance format)

**Common false-positive patterns.**

* format change — the transcript provider or Entity has changed call format (for example, prerecorded remarks replacing live commentary)
* disclosed special circumstances — an unusual call (for example, a special-situation call) is compared against a routine Baseline
* small-sample Baseline — thin history means the Baseline is narrow; normal variability looks anomalous
* provider artefact — a normalization error in one Document distorts structural features

Distinct from the other four: Structural Anomaly is about the shape of communication, not its content, framing, or certainty. Correlations with the other types are expected; they are modeled at the Fusion Engine, not collapsed into a single type.

---

## Confidence And Uncertainty At The Signal Level

CONTEXT §3.3 requires explainability and §3.4 requires structured skepticism. At the Signal level:

* Confidence is always present and is distinct from Strength (see Signal Anatomy)
* low-Confidence Signals are not suppressed by construction; the decision to surface them is a Ranking & Surfacing and USER_EXPERIENCE.md concern
* Confidence reflects, at minimum: Baseline thinness, Basis disagreement, and Evidence span precision
* Confidence is not a probability of correctness; claiming otherwise would violate structured skepticism

Per [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3 (and user-confirmed), false positives are costlier to user trust than false negatives in the early period. The default policy is to lower Confidence rather than raise Strength when evidence is thin, and to allow the Fusion Engine to emit lower-Confidence Signals rather than withhold them silently.

---

## Thin-History Policy

[ASSUMPTIONS.md](./ASSUMPTIONS.md) E1 and user confirmation acknowledge that Entities with limited historical depth are a first-class concern and that reliability should be preferred over coverage in those cases.

This document commits the following policies for Signals concerning thin-history Entities:

* Signals that depend on a Baseline (Narrative Drift, Confidence Shift, Structural Anomaly) carry reduced Confidence proportional to Baseline thinness. The Fusion Engine is the locus of this adjustment; Baseline Maintenance supplies Baseline thinness as an input.
* Signals with severely thin Baselines may be emitted as candidate-only and not promoted to surfaced without human review via the Evaluation Harness.
* Omission Events require a minimum recurrence threshold in the prior history; below that threshold, the Signal is not emitted at all.
* Contradiction Events are less dependent on history; they may be emitted normally for thin-history Entities.

Specific thresholds are deferred to NARRATIVE_ANALYSIS.md. The policy shape is committed here.

---

## Signal Lifecycle

Every Signal transits through a subset of the following states. Transitions are expressed as new Signal records with lineage references; no Signal record is mutated.

### Candidate

A Signal has been produced by the Fusion Engine but has not been promoted to the surfaced pool. Candidate Signals are visible to the Evaluation Harness and to downstream analytical processes but are not expected to be surfaced to users.

### Surfaced

A Signal is eligible for user-facing surfaces. Promotion from Candidate to Surfaced may be automatic (meets thresholds) or gated (for example, human review for types marked for review; thin-history policy rules).

### Stale

A surfaced Signal has aged past the point where its observation is current. Stale Signals remain available for historical query and for reasoning about past narrative state, but are not emphasized on current-state surfaces.

### Superseded

A subsequent Signal has replaced this Signal — for example, an updated Narrative Drift Signal concerning the same Entity and time window. The superseded Signal is retained; the subsequent Signal's Lineage references it.

### Retired

A Signal is withdrawn — typically because its Basis has been invalidated (for example, a DerivationRun was recalled) or its Evidence was found to be incorrect. Retirement is expressed as a new record with Lineage; the original Signal is not deleted.

Transition policy — when and why Signals move between states — is deferred to NARRATIVE_ANALYSIS.md and EVALUATION.md. This document specifies only the states and the immutability posture.

---

## Extension: Adding New Signal Types

The taxonomy is extensible (CONTEXT §4). Extensions enter by one of two paths.

### Research-Driven Extension

A new type is proposed from analytical or research work. The proposal includes:

* operational definition
* required evidence pattern
* strong-vs-weak criteria
* common false-positive patterns

The proposal is reviewed. If accepted, the type is added to this document. The Fusion Engine begins emitting the new type through the same contract as existing types.

### Discovery-Driven Extension

Per CONTEXT §5.4 and user-confirmed policy, Learned Analysis may propose candidate new Signal *types* — not only new instances of existing types. Candidate types enter a gated review pool:

* the candidate type is characterized with a draft operational definition and observed examples
* representative candidate Signals of the proposed type are held in the Candidate-Type Pool for human review (Evaluation Harness in [ARCHITECTURE.md](./ARCHITECTURE.md))
* a proposed type is promoted into the taxonomy only after human review confirms that it is meaningful, distinct from existing types, and not a rediscovery of an existing type under a new name

The Candidate-Type Pool is a first-class concept in this document, which owns the state machine and type definition. Promotion workflow and review mechanics are owned by EVALUATION.md. How a promoted type is used in production analysis once promoted is owned by NARRATIVE_ANALYSIS.md.

---

## What A Signal Does Not Contain

* no predicted future state
* no recommendation or action
* no sentiment polarity (the Deliberate Non-Definitions section of [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) applies)
* no cross-type aggregate score (Strength is type-relative)
* no user-facing formatting; presentation is a USER_EXPERIENCE.md concern

---

## Deferred Decisions

* Strength representation (scalar, band, tier, or other) — MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md
* Confidence representation — MODEL_STRATEGY.md, NARRATIVE_ANALYSIS.md; surfacing to users is USER_EXPERIENCE.md
* scoring algorithms — MODEL_STRATEGY.md
* ranking and prioritization policy — NARRATIVE_ANALYSIS.md and EVALUATION.md
* thresholds (what counts as "meaningful" per type, minimum Baseline depth, minimum recurrence for Omission) — NARRATIVE_ANALYSIS.md
* transition policy between lifecycle states — NARRATIVE_ANALYSIS.md and EVALUATION.md
* Commentary generation method — MODEL_STRATEGY.md (content) and USER_EXPERIENCE.md (surface)
* API serialization of Signals — API_SPEC.md
* storage and indexing — [DATA_MODEL.md](./DATA_MODEL.md) (conceptual) and downstream infrastructure (physical)
* review workflow for candidate-type promotion — EVALUATION.md
* cross-signal interaction modeling — NARRATIVE_ANALYSIS.md

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [VISION.md](./VISION.md), [ASSUMPTIONS.md](./ASSUMPTIONS.md), and [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) are authoritative; this document implements their commitments at the Signal level.
* [ARCHITECTURE.md](./ARCHITECTURE.md) describes the components that produce and consume Signals; the Fusion Engine and Signal Store share this document as their contract.
* [DATA_MODEL.md](./DATA_MODEL.md) represents the Signal structurally and carries its Evidence chain; that document holds the data shape, this document holds the semantic meaning.
* NARRATIVE_ANALYSIS.md, MODEL_STRATEGY.md, and EVALUATION.md own the deferred decisions listed above.
