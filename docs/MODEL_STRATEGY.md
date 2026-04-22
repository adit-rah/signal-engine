# MODEL_STRATEGY.md

## Purpose Of This Document

MODEL_STRATEGY.md defines the conceptual model stack that realizes the ML Layer ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)) and the model-level mechanics of the Fusion Engine ([ARCHITECTURE.md](./ARCHITECTURE.md) component 8): what conceptual models exist, what role each plays, how they are trained and run, how they interoperate, how they are versioned and replaced, and what the system does when one of them is unavailable.

The document is conceptual. It commits no specific architectures, libraries, frameworks, or vendors. Those choices are deferred to downstream infrastructure work and, if one later emerges, to a dedicated TRAINING_DATA.md.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* the Model Stack Shape section names the conceptual models the system requires, without committing to architectures
* each conceptual model is described by role, inputs, outputs, and training-data posture
* Fusion Engine mechanics live in this document at the model level; operational policy (thresholds, lifecycle transitions, ranking) lives in NARRATIVE_ANALYSIS.md and is referenced but not duplicated here
* Strength and Confidence are specified as distinct computations with disjoint input families, preserving the distinction from [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
* deferred decisions are named at the end with their downstream owners

---

## Guiding Commitments Inherited

These are held as invariants throughout:

* models are in-house, trained and operated by the project; external large-language-model APIs do not appear in critical paths ([CONTEXT.md](./CONTEXT.md) §6.1)
* the stack favors small, specialized models over a single large general-purpose model ([CONTEXT.md](./CONTEXT.md) §6.2)
* training must be feasible on modest hardware budgets ([CONTEXT.md](./CONTEXT.md) §6.3; [ASSUMPTIONS.md](./ASSUMPTIONS.md) H5)
* every model output must be resolvable to a Basis chain; black-box outputs are excluded by construction ([CONTEXT.md](./CONTEXT.md) §3.3, §6.4)
* model complexity is justified only when it produces measurably better Signals than simpler alternatives ([CONTEXT.md](./CONTEXT.md) §6.4)
* v1 is English-first ([CONTEXT.md](./CONTEXT.md) §8 Language Posture; [ASSUMPTIONS.md](./ASSUMPTIONS.md) D5)
* false positives are costlier to user trust than false negatives in early development ([CONTEXT.md](./CONTEXT.md) §14 False-Positive Posture; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3)
* Strength and Confidence are structurally distinct ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)
* the ML Layer does not act as sole decision-maker ([CONTEXT.md](./CONTEXT.md) §5 ML Constraints); the Fusion Engine and the Evaluation Harness are the backstops

---

## Model Stack Shape

The system relies on a stack of specialized models, each scoped to a narrow task. No single model is responsible for producing a Signal end-to-end; Signals emerge from the Fusion Engine combining heuristic and learned contributions ([CONTEXT.md](./CONTEXT.md) §3.2.C).

The stack is organized into three conceptual families. The term **Model Family** is used here to name a group of models serving the same conceptual purpose; it is flagged for glossary extension.

* **Representation models** — produce learned semantic representations of financial text. Consumed by many downstream analyses.
* **Analytical models** — produce learned features relevant to a specific Signal concern (for example, certainty-bearing features for Confidence Shift; structural-deviation features for Structural Anomaly).
* **Generative models** — produce Commentary text. Scoped tightly and kept small; see the Commentary section below.

Unsupervised pattern-discovery capability ([CONTEXT.md](./CONTEXT.md) §5.4) is a property of selected Analytical models, not a separate family.

Each model is a member of a family but is independently versioned and independently replaceable.

---

## Conceptual Models And Their Roles

The list below is conceptual. Each entry names what the model is for, what it consumes, what it produces, and what kind of training data it depends on. No architecture is committed.

### Representation Model (Domain-Adapted)

**Role.** The shared semantic representation of financial text — the Domain-Adapted Representation Model named in [CONTEXT.md](./CONTEXT.md) §6.2 and [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

**Consumes.** Normalized text Segments and Utterances produced by Document Processing ([DATA_MODEL.md](./DATA_MODEL.md) Derivation Layers).

**Produces.** Dense learned representations at the Utterance, Segment, and Document levels. These are features consumed by multiple Analytical models and by the Fusion Engine's Basis Disagreement check.

**Training-data posture.** Self-supervised adaptation over acquired earnings-call transcripts and related domain text. Feasibility on modest hardware ([ASSUMPTIONS.md](./ASSUMPTIONS.md) H5) is a first-class constraint. Licensing posture is assumed to permit training ([ASSUMPTIONS.md](./ASSUMPTIONS.md) D6).

**Replaceability.** The representation model is the most load-bearing single model in the stack. Replacing it is expected to require re-derivation of downstream Analytical features; the DerivationRun mechanism carries that cost explicitly.

---

### Narrative-Similarity And Drift Model

**Role.** Quantifies shift in framing and emphasis across temporally separated Documents, contributing learned evidence for Narrative Drift Signals.

**Consumes.** Representation-model outputs over the current Document and the Baseline-contributing prior Documents; ThemeInstances where relevant.

**Produces.** Learned drift features indicating magnitude and character of change relative to the Baseline.

**Training-data posture.** Weak supervision from heuristic drift features plus structured human judgments recorded by the Evaluation Harness. No external labels are assumed available.

---

### Confidence-Feature Model

**Role.** Identifies certainty-bearing features in Speaker communication — hedging density, conditional framing, assertive constructions — contributing learned evidence for Confidence Shift Signals.

**Consumes.** Representation-model outputs over Utterances attributed to a Speaker; Segment context.

**Produces.** Learned certainty features at Utterance granularity, which the Fusion Engine compares against the Speaker Baseline.

**Training-data posture.** Weak supervision from heuristic hedging detectors plus human-reviewed exemplars. The scripted-versus-unscripted distinction is treated as a feature, not as a label.

---

### Contradiction-Alignment Model

**Role.** Brings candidate statement pairs into comparable form and estimates incompatibility, contributing learned evidence for Contradiction Event Signals. Addresses the comparability-gate requirement in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

**Consumes.** Representation-model outputs over pairs of Utterances together with Document, Speaker, and temporal metadata.

**Produces.** A learned incompatibility judgment per candidate pair, plus a representation of the comparability basis — what the two statements share that makes comparison meaningful.

**Training-data posture.** Human-reviewed exemplars; synthetic near-contradiction pairs generated from heuristically aligned claim templates; structured negative examples drawn from the updated-fact and scope-mismatch false-positive patterns named in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

---

### Omission-Verification Model

**Role.** Verifies that an apparent Theme absence is semantically real rather than a surface restatement — addressing the compression and Speaker-change false-positive patterns named in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

**Consumes.** Representation-model outputs over the current Document, prior Documents that established the Theme, and the Theme's own representation.

**Produces.** A learned judgment on whether the Theme is semantically absent from the current Document, distinct from the heuristic recurrence count that triggered the candidate.

**Training-data posture.** Heuristic-plus-human-reviewed exemplars; negative examples mined from prior false-positive patterns.

---

### Structural-Baseline Model

**Role.** Learns an Entity-specific or Speaker-specific structural profile — length distributions, topic distribution across Segments, Speaker share — contributing learned evidence for Structural Anomaly Signals.

**Consumes.** Structural features extracted by Heuristic Analysis plus representation outputs over the Document as a whole.

**Produces.** Learned structural profile and per-Document deviation estimates against that profile.

**Training-data posture.** Self-supervised over an Entity's historical Documents; thin-history Entities produce thin profiles, and the model must expose profile thinness to downstream consumers.

---

### Theme-Discovery Model

**Role.** Unsupervised proposal of Themes that may warrant curation, and — under [CONTEXT.md](./CONTEXT.md) §5.4 and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)'s Discovery-Driven Extension path — proposal of candidate Signal *types* for entry into the Candidate-Type Pool.

**Consumes.** Representation-model outputs over the corpus.

**Produces.** Candidate Themes and, separately, candidate Signal-type proposals characterized by recurring patterns not reducible to existing types.

**Training-data posture.** Unsupervised. Outputs are proposals, not emissions. The promotion workflow for a candidate type is owned by EVALUATION.md; the operational use of a promoted type is owned by NARRATIVE_ANALYSIS.md.

---

### Commentary Generation Model (Constrained)

**Role.** Produces the Commentary field required on every Signal ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy).

**Consumes.** The emitted Signal's Basis chain, Evidence Spans, and a type-specific template scaffold supplied by the Fusion Engine.

**Produces.** A short human-readable explanation grounded in the supplied Basis and Evidence.

**Training-data posture.** Human-written exemplars of good Commentary paired with their Basis and Evidence. Because Commentary is grounded in supplied Basis — not in free generation over the Document corpus — the model can be small. A local small-footprint language model ([CONTEXT.md](./CONTEXT.md) §6.2) is the intended shape; this is not a commitment to a specific architecture.

**Constraint.** Commentary must not introduce claims unsupported by the supplied Basis and Evidence. The Fusion Engine applies a grounding check at emission time and rejects Commentary that fails it; the precise shape of the grounding check is deferred to downstream work. A Signal whose Commentary cannot be grounded is held at Candidate status pending human review.

---

## Training Posture

Training is a sustained activity, not a one-time event. Several properties hold across the stack.

* training is feasible on modest hardware ([ASSUMPTIONS.md](./ASSUMPTIONS.md) H5); models that require unbounded compute are excluded on that ground alone
* self-supervised adaptation over domain text precedes task-specific training; domain adaptation is concentrated in the Representation Model and reused downstream
* weak supervision from Heuristic Analysis outputs is treated as a bootstrap signal, not as ground truth
* human-reviewed outputs from the Evaluation Harness ([ARCHITECTURE.md](./ARCHITECTURE.md) component 12) are the highest-quality training signal the system produces and are expected to accumulate over time
* training-data curation specifics — sourcing, labeling protocols, reviewer calibration — are deferred to EVALUATION.md (for review-driven data) and to a potential TRAINING_DATA.md (for broader training strategy) if one later emerges

No assumption is made that clean ground-truth labels exist for any Signal type ([CONTEXT.md](./CONTEXT.md) §13.3). Training loops are designed to tolerate their absence.

---

## Inference Posture

Inference cost is a first-class design constraint ([CONTEXT.md](./CONTEXT.md) §6.3; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint).

* inference runs per Document (or per Baseline update), not continuously
* representation outputs are cacheable and keyed by DerivationRun so that re-derivation is explicit
* Analytical models consume cached representations rather than re-encoding text
* the Commentary Generation Model is invoked at most once per emitted Signal
* the Theme-Discovery Model runs on a deliberate cadence, not per-Document
* nothing in the critical path requires network access to third-party model providers ([ARCHITECTURE.md](./ARCHITECTURE.md) Model Ownership Posture)

Specific serving infrastructure, scheduling, and batching strategies are deferred to downstream infrastructure work and to EVENTS_AND_PIPELINES.md.

---

## Fusion Engine: Model-Level Mechanics

The Fusion Engine is the designated hard design problem ([CONTEXT.md](./CONTEXT.md) §3.2.C; [ARCHITECTURE.md](./ARCHITECTURE.md) component 8). This section describes its mechanics at the model level: what it takes in, how it combines, what it produces, and how Basis is preserved across the combination. Operational policy — thresholds, lifecycle transitions, ranking — is specified in NARRATIVE_ANALYSIS.md and is not duplicated here.

### Inputs

For each candidate Signal, the Fusion Engine receives:

* heuristic-layer candidate evidence from Heuristic Analysis — typed features with values and supporting Spans
* learned-layer candidate evidence from Learned Analysis — typed features with values, supporting Spans, and a reference to the DerivationRun that produced them
* Baseline state from Baseline Maintenance, including Baseline thinness ([DATA_MODEL.md](./DATA_MODEL.md) Baseline)
* Entity and, where relevant, Speaker context
* for Baseline-dependent types, the Baseline's valid-time

### Combination Approach

The combination is not a single scalar score. It produces a structured emission whose components are kept separable so that Basis is preserved and the combination step itself remains inspectable.

* heuristic evidence and learned evidence are treated as parallel inputs, not as stages of a pipeline; neither is privileged by construction
* the combination is conflict-aware — disagreement between heuristic and learned contributions is represented explicitly rather than averaged away
* the combination is not initially learned end-to-end; early versions are explicit combination rules parameterized by the operational policy NARRATIVE_ANALYSIS.md supplies. Learning the combination itself is a later possibility, gated by the Evaluation Harness and bounded by the explainability requirement
* per-type combination rules differ — a combination rule appropriate for Narrative Drift is not assumed to be appropriate for Contradiction Event

The choice to keep the combination explicit in early versions is a deliberate trade: it sacrifices potential learned sophistication for inspectability and replaceability. This is consistent with [CONTEXT.md](./CONTEXT.md) §6.4 — complexity is justified only when simpler alternatives are measurably worse.

### Basis Disagreement

Basis Disagreement ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)) is the condition in which heuristic and learned contributions disagree on a candidate Signal's existence, type, or magnitude.

* disagreement is detected by per-type rules that define what agreement looks like — both contributions exceeding their type-specific thresholds; agreement on the Spans that drive the candidate; consistent direction of deviation
* disagreement is represented on the emitted Signal's Basis as a first-class field — not suppressed, not hidden
* disagreement is a first-class input to Confidence (see below); it does not suppress emission by itself
* the shape of the disagreement record is standardized across types: which contributions were present, which crossed their thresholds, and on what they differ

The Fusion Engine does not resolve disagreement by picking a side. It emits the Signal with the disagreement recorded and lets Confidence reflect the epistemic weakness. The decision on whether to surface a low-Confidence Signal is a Ranking & Surfacing concern owned by NARRATIVE_ANALYSIS.md.

### Strength Computation

Strength represents how far the observed phenomenon rises above the noise floor for its type ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)).

* Strength inputs are magnitude-of-deviation quantities drawn from both heuristic and learned contributions
* Strength is type-relative — a Narrative Drift Strength is not comparable to a Confidence Shift Strength
* Strength is bounded; saturation at the upper bound is an exceptional condition by construction
* Strength explicitly excludes epistemic factors (Baseline thinness, Basis Disagreement, Evidence breadth); those feed Confidence, not Strength

The representation — scalar, band, or tier — is a design decision made in NARRATIVE_ANALYSIS.md alongside ranking policy. This document commits that whatever the representation, the input family is disjoint from the Confidence input family so that the distinction is preserved structurally.

### Confidence Computation

Confidence represents the system's epistemic certainty in the Signal itself ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy).

Confidence inputs are epistemic:

* Baseline thinness — a queryable property of the Baseline ([DATA_MODEL.md](./DATA_MODEL.md) Baseline)
* Basis Disagreement — as detected and represented above
* Evidence Span precision and quantity — narrow or singular Evidence lowers Confidence
* type-specific additional factors — for Contradiction Event, the strength of the comparability basis; for Omission Event, the prior recurrence depth

Confidence is not a probability of correctness ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Signal Confidence). Asserting such a probability would violate structured skepticism ([CONTEXT.md](./CONTEXT.md) §3.4).

The default policy when evidence is thin is to lower Confidence rather than raise Strength. This is how the False-Positive Posture ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3) manifests in computation: low-Confidence Signals are emitted but are gated downstream by the surfacing policy owned by NARRATIVE_ANALYSIS.md.

### Commentary Generation

For every emitted Signal, the Fusion Engine assembles a Commentary request containing:

* the Signal's type, Strength, and Confidence
* the Basis chain, including the disagreement record where present
* the Evidence Spans
* the Baseline reference where relevant
* a type-specific scaffold that constrains what the Commentary must address

The Commentary Generation Model produces the Commentary grounded in this input. Outputs that introduce claims not supported by the supplied Basis and Evidence are expected to fail the grounding check; regeneration or rejection follows. Commentary is immutable once emitted. A superseded or retired Signal carries its original Commentary; the superseding Signal carries its own.

### Traceability Across Combination

Every combination step writes to the Evidence & Provenance Store ([ARCHITECTURE.md](./ARCHITECTURE.md) component 11).

* the Fusion Engine's own DerivationRun is recorded
* references to the Heuristic Analysis and Learned Analysis DerivationRuns that supplied the inputs are carried on the Basis
* Span references are preserved unbroken from heuristic and learned inputs through to the emitted Signal's Evidence

No Signal is emitted whose Basis chain cannot be resolved from the emitted record back to the source Spans.

---

## Model Versioning, Comparison, And Replacement

Models are first-class versioned artifacts. Each inference is recorded against a DerivationRun ([DATA_MODEL.md](./DATA_MODEL.md)) identifying the model version used.

* no model is silently upgraded in place; a new version produces a new DerivationRun
* replacing a model means introducing a new DerivationRun and, where needed, re-deriving affected downstream artifacts
* before a replacement is promoted, the candidate model is run alongside the incumbent over a historical period drawn from the Evaluation Harness's review queue; differences are reviewed by humans
* the Fusion Engine does not mix outputs from two versions of the same model in a single Signal's Basis; a Signal is produced under one coherent DerivationRun set

Specifics of the side-by-side comparison, retention of previous DerivationRuns, and rollback procedure are deferred to EXPERIMENTATION.md (where replay is defined) and to downstream infrastructure work.

---

## Degraded Modes

The system must remain functional when a model is unavailable or has been found to be degraded. Degraded-mode handling is a first-class concern.

The term **Degraded Mode** is flagged for glossary extension. It refers to any operational state in which part of the model stack is not available or is not trusted.

The mechanics:

* if the Representation Model is unavailable, downstream Analytical models that depend on it cannot produce learned evidence; Heuristic Analysis continues unaffected
* in that state, the Fusion Engine may still emit Signals, but only those for which heuristic evidence alone meets the per-type thresholds supplied by NARRATIVE_ANALYSIS.md; Basis Disagreement is recorded as "learned side unavailable"
* if a specific Analytical model is unavailable, Signals of the types it supports may still be emitted if the type's heuristic contribution alone meets its threshold; the missing learned side is recorded on the Basis
* Confidence is reduced in degraded mode, reflecting the missing learned contribution
* degraded-mode operation is itself a property exposed on the emitted Signal — not a hidden state; downstream consumers may apply policy accordingly

Silent substitution of a missing model's output with a default value is excluded. Missing is a distinct state from present-and-zero.

Detection of degraded mode — that is, establishing that a model is in fact unavailable or misbehaving — is an operational concern owned by [OBSERVABILITY.md](./OBSERVABILITY.md) under Component Health. Recovery procedures are deferred to FAILURE_MODES.md.

---

## Interaction With Evaluation

The Evaluation Harness ([ARCHITECTURE.md](./ARCHITECTURE.md) component 12) feeds this document's training loops in two directions.

* reviewer judgments on emitted Signals become training data for Analytical models and for the Commentary Generation Model
* reviewer outcomes on Candidate-Type Pool members provide the signal for whether the Theme-Discovery Model's proposals are useful; the promotion workflow itself is owned by EVALUATION.md, and the in-production use of a promoted type is owned by NARRATIVE_ANALYSIS.md

This document does not specify evaluation methodology, reviewer selection, or how reviewer feedback is represented. Those are EVALUATION.md concerns. This document commits only that human-reviewed outputs are an available training input and that models are designed to benefit from them.

---

## What This Document Does Not Specify

* specific model architectures, libraries, or frameworks — downstream infrastructure work
* training-data sourcing — [DATA_ACQUISITION.md](./DATA_ACQUISITION.md)
* training-data curation protocols — EVALUATION.md for review-driven data; a potential TRAINING_DATA.md for broader training strategy
* specific hardware or serving infrastructure — downstream infrastructure work
* serialization of model outputs on the wire — [API_SPEC.md](./API_SPEC.md)
* specific Strength representation (scalar, band, tier) — NARRATIVE_ANALYSIS.md
* specific Confidence representation — NARRATIVE_ANALYSIS.md
* thresholds per Signal type — NARRATIVE_ANALYSIS.md
* lifecycle transition policy — NARRATIVE_ANALYSIS.md and EVALUATION.md
* ranking policy — NARRATIVE_ANALYSIS.md and EVALUATION.md
* user-facing Commentary surface — [USER_EXPERIENCE.md](./USER_EXPERIENCE.md)
* reviewer calibration — EVALUATION.md; flagged as an open concern in [ASSUMPTIONS.md](./ASSUMPTIONS.md) X5
* multilingual extension — deferred; v1 is English-first

---

## Deferred Decisions

* whether the Fusion Engine's combination step itself is later learned end-to-end, and under what explainability constraints — open, gated by EVALUATION.md
* whether the Commentary Generation Model is retired in favor of template-based Commentary for some types — open, gated by EVALUATION.md
* how re-derivation is scheduled when a model is replaced — downstream infrastructure work; flagged in [ARCHITECTURE.md](./ARCHITECTURE.md) Open Structural Questions
* how training compute is allocated across model families under the low-capital constraint — downstream infrastructure work
* how the Theme-Discovery Model's cadence is set — NARRATIVE_ANALYSIS.md (where Theme curation lives) and EVALUATION.md (where promotion lives)

---

## Open Questions

* the balance between heuristic rigor and learned generalization per Signal type ([CONTEXT.md](./CONTEXT.md) §15) is only partially resolved here — the choice of per-type combination rules is committed in NARRATIVE_ANALYSIS.md; the empirical balance is an EVALUATION.md and EXPERIMENTATION.md concern
* whether a separate small model is needed for comparability-gate construction in Contradiction Event detection, or whether Representation-Model outputs suffice — an experimental question for EXPERIMENTATION.md
* whether thin-history Entities warrant an Entity-agnostic variant of the Structural-Baseline Model trained across a pool of similar Entities — an experimental question for EXPERIMENTATION.md; flagged because it interacts with [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)'s Thin-History Policy

---

## Recommended Glossary Extensions

The following terms appear in this document and are flagged for addition to [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **Model Family** — a group of specialized models serving the same conceptual purpose (Representation, Analytical, Generative), within which individual models are independently versioned and replaceable
* **Degraded Mode** — an operational state in which part of the model stack is unavailable or untrusted; the Fusion Engine records the missing side on emitted Signals' Basis and adjusts Confidence accordingly
* **Grounding Check** — the check applied to Commentary output to ensure it does not introduce claims unsupported by the supplied Basis and Evidence

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes their model-posture commitments
* [VISION.md](./VISION.md) and [ASSUMPTIONS.md](./ASSUMPTIONS.md) bound the posture this document operates under
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms are flagged above
* [ARCHITECTURE.md](./ARCHITECTURE.md) names the components that produce and consume model outputs; the Fusion Engine mechanics here implement its architectural responsibility
* [DATA_MODEL.md](./DATA_MODEL.md) defines Baseline, Evidence, Basis, DerivationRun, and Signal — the artifacts this document's mechanics produce and consume
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines Signal Anatomy and the Candidate-Type Pool state machine; this document implements the Anatomy at the model level
* NARRATIVE_ANALYSIS.md owns operational policy — thresholds, lifecycle, ranking; referenced extensively and not duplicated
* EVALUATION.md owns human review, the Candidate-Type Pool promotion workflow, and reviewer calibration
* EXPERIMENTATION.md owns replay, offline comparison, and graduation; referenced in the versioning and replacement section
* [OBSERVABILITY.md](./OBSERVABILITY.md) owns Component Health, through which Degraded Mode is detected operationally; this document defines how the system behaves under it, not how it is detected
