# EVALUATION.md

## Purpose Of This Document

EVALUATION.md defines how Signal quality is evaluated: what is measured, how structured human review is organized, how the Evaluation Harness samples Signals without biasing the reviewed population, how the Candidate-Type Pool promotion workflow runs, how reviewer feedback interacts with the Signal lifecycle, how the false-positive posture is operationalized, and how evaluation methodology matures as the system accumulates history.

This document is conceptual. It commits to the shape of evaluation but does not specify review tooling, reviewer selection procedures, compensation, or evaluation-specific user interface.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* evaluation is Signal-quality evaluation; system-health instrumentation is owned by [OBSERVABILITY.md](./OBSERVABILITY.md) and the boundary is stated explicitly
* human review is the first-line method; automatic metrics do not substitute for it in early development ([CONTEXT.md](./CONTEXT.md) §14)
* the false-positive posture ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3) is load-bearing throughout
* the Candidate-Type Pool promotion workflow lives here, while its state machine lives in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and its in-production use lives in NARRATIVE_ANALYSIS.md
* maturation of evaluation is described as trajectory, not schedule
* what evaluation does not measure is stated explicitly

---

## Guiding Commitments Inherited

* evaluation during early development relies on structured human review, qualitative analyst feedback, internal dogfooding, and retrospective study ([CONTEXT.md](./CONTEXT.md) §14)
* automatic metrics are not expected to substitute for human judgment during early development ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) N3)
* false positives are costlier than false negatives to user trust in early development ([CONTEXT.md](./CONTEXT.md) §14 False-Positive Posture; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3)
* the absence of clean ground truth is a central evaluation challenge, not a solved problem ([CONTEXT.md](./CONTEXT.md) §13.3)
* signal quality is recognizable by humans before it is measurable by automated metrics ([ASSUMPTIONS.md](./ASSUMPTIONS.md) S4)
* reviewer calibration is flagged as a potential downstream concern if expert disagreement proves persistent ([ASSUMPTIONS.md](./ASSUMPTIONS.md) X5)
* evaluation is an evolving artifact ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) T4)
* the low-capital posture bounds reviewer load and tooling ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint)

---

## Evaluation Methodology In Early Development

The evaluation methodology acknowledges two facts: most Signal types lack clean ground truth, and the system's utility is judged by humans before it is measurable by any automated metric. These two facts together set the shape.

### Primary Mode: Structured Human Review

The primary evaluation mode is structured human review of surfaced and Candidate Signals. Structured means:

* reviewers see the Signal, its Basis chain, its Evidence, its Commentary, and where relevant the Baseline reference and Baseline thinness
* reviewers record judgments against a fixed set of questions — a **Review Rubric** — rather than open-ended commentary; the term is flagged for glossary extension
* rubric responses are stored alongside the Signal record as reviewer feedback, not mutations of the Signal itself

A review is a record, not a verdict on the Signal's Basis or Evidence. Whether a Signal is retained, retired, or held depends on the aggregated review record together with lifecycle policy in NARRATIVE_ANALYSIS.md.

### Secondary Modes

Three secondary modes supplement structured review ([CONTEXT.md](./CONTEXT.md) §14):

* **qualitative analyst feedback** — unstructured commentary from analysts engaging with the system outside the review queue; used to identify review-rubric gaps and evaluation blind spots
* **internal dogfooding** — the team uses the system on known historical narratives as a qualitative evaluation mode; dogfooding outcomes are recorded against the same Signal identifiers used by structured review so that the two modes inform each other
* **retrospective study** — review of past narrative changes with known outcomes (for example, a disclosed strategic pivot, a publicly acknowledged correction), used to ask whether the system would have flagged the change and, if so, how it characterized it

None of these modes substitute for structured review. They inform the rubric and identify failure modes the rubric should cover.

### What Evaluation Measures

The dimensions evaluation tracks are drawn from [CONTEXT.md](./CONTEXT.md) §14:

* usefulness of detected Signals
* clarity of explanations (Commentary and Basis legibility)
* consistency over time (same input shape, same Signal shape; Baseline-relative comparisons behave predictably)
* reduction of human cognitive load (a Signal that surfaces a change faster than a reader would have noticed is valuable; one that does not is not)
* ability to surface non-obvious narrative changes (the reader did not already know; the Signal added something)

These dimensions are qualitative. They are not collapsed into a single scalar. A Signal may score well on clarity and weakly on usefulness, or vice versa; both facts are informative and are preserved separately in the review record.

### What Evaluation Does Not Measure With A Single Metric

The methodology avoids a single summary score for Signal quality. Reasons:

* a single score invites drift toward what the score measures rather than what users value ([VISION.md](./VISION.md) Drift Toward Ground-Truth Theater)
* the dimensions above are not commensurable
* the project accepts that evaluation is slower and less crisp in exchange for avoiding false objectivity

Aggregation of review records into summaries is possible and useful; those summaries are per-dimension, not per-Signal scalars.

---

## Human Review Structure

Human review is organized around three concepts: who reviews, what they see, and how feedback is recorded.

### Who Reviews

Reviewer roles are conceptual. Specific selection, training, and compensation are deferred.

* **primary reviewer** — a person with sufficient financial literacy ([ASSUMPTIONS.md](./ASSUMPTIONS.md) U1) to judge whether a narrative Signal is meaningful; the role that performs structured review against the rubric
* **secondary reviewer** — a second primary reviewer whose independent judgment is used on a sample of Signals to measure reviewer agreement
* **adjudicator** — invoked when primary and secondary reviewers disagree on a Signal meeting the disagreement threshold

The term **Reviewer Cohort** is used to name the group of reviewers operating at a given time; it is flagged for glossary extension. Cohort composition changes over time; the review records preserve which cohort version reviewed each Signal so that consistency-over-time can itself be evaluated.

### What Reviewers See

For each reviewed Signal, the reviewer sees:

* the Signal's Type, Subject (Entity and, where relevant, Speaker), and temporal scope
* Strength and Confidence, presented as the Signal carries them (representation deferred to NARRATIVE_ANALYSIS.md)
* the Basis chain — which heuristic rules contributed, which learned analyses contributed, and any Basis Disagreement recorded by the Fusion Engine
* the Evidence Spans, rendered in context
* the Commentary generated by MODEL_STRATEGY.md's Commentary Generation Model
* the relevant Baseline reference and Baseline thinness where the Signal depends on a Baseline
* any Signal Interaction Records linking this Signal to others (NARRATIVE_ANALYSIS.md Cross-Signal Interaction)

Reviewers do not see aggregate statistics about prior reviews of the same Signal unless the review explicitly supports that view for calibration purposes.

### How Feedback Is Recorded

Reviewer feedback is structured against the Review Rubric. The rubric covers at minimum:

* does this Signal describe a real change, or is it an artifact?
* if real, is the described change meaningful?
* is the Commentary accurate and grounded in the Evidence?
* is the Evidence sufficient to judge the Signal?
* is the Signal more likely a false positive, a true positive, or indeterminate?
* where relevant, does Confidence appropriately reflect epistemic weakness?

Each response is a structured category with optional short-form notes. Long-form commentary is supported but is secondary.

Feedback is stored as a review record attached to the Signal identifier and the reviewer identifier, with timestamps. Review records are immutable; a reviewer who changes their mind files a new review record.

### How Feedback Is Aggregated

Aggregation is per-dimension, not per-Signal scalar:

* per-Signal: the count of reviews, distribution of responses per rubric item, any adjudication outcome
* per-type: review distributions rolled up across Signals of that type, over a time window
* per-reviewer: response distributions, used for calibration (see below)
* per-cohort: response distributions under a fixed Reviewer Cohort version, used for consistency-over-time analysis

Aggregations are made available through the Query & Retrieval Surface ([ARCHITECTURE.md](./ARCHITECTURE.md) component 13) for internal use. User-facing presentation of evaluation outcomes is not a v1 concern; if ever, it is a [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) decision.

### Reviewer Calibration

[ASSUMPTIONS.md](./ASSUMPTIONS.md) X5 flags reviewer calibration as a potential downstream concern if expert disagreement is persistent. This document commits the shape rather than specifying the mechanics.

* a sample of Signals is reviewed by multiple reviewers, producing explicit disagreement measurements at the rubric-item level
* persistent disagreement on specific rubric items is itself a signal that the rubric or the Signal type's definition needs refinement
* calibration rounds — coordinated review of a small agreed-upon set of Signals — may be convened when disagreement crosses a threshold; the mechanics are deferred

Calibration is a property of the evaluation methodology, not of the system under evaluation. A system whose Signals provoke persistent reviewer disagreement is not necessarily a system with bad Signals; it may be a system surfacing genuinely ambiguous changes. Calibration distinguishes the two cases.

---

## Evaluation Harness Sampling

The Evaluation Harness ([ARCHITECTURE.md](./ARCHITECTURE.md) component 12) samples Signals for human review. Sampling design is load-bearing: biased sampling produces biased evaluation.

### Sampling Principles

Sampling is guided by four principles:

* **stratification** — across Signal type, Strength band, Confidence band, thin-history versus non-thin-history Entity, Candidate versus Surfaced status
* **representativeness** — within each stratum, sampling aims for representative coverage of the emitted population rather than oversampling the most conspicuous Signals
* **unbiased selection** — within a stratum, selection does not preferentially draw from Signals the system already judges important; ranking position is not a sampling weight
* **operational feasibility** — the per-period sample size is bounded to what the Reviewer Cohort can process with attention

### Stratification

Stratification ensures that review coverage reflects the shape of the emitted population and that weak, uncertain, and thin-history Signals are not under-represented relative to their operational importance.

* per-type: review weights are set so that no type is systematically under-reviewed
* Strength bands: weak Signals are reviewed deliberately, not only strong ones, because weak Signals are the most sensitive to false-positive behavior
* Confidence bands: low-Confidence Signals are reviewed at a higher rate to calibrate whether Confidence is appropriately conservative
* thin-history Entities: deliberate oversampling, because the Thin-History Policy ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); NARRATIVE_ANALYSIS.md) is exactly what most needs empirical validation
* Candidate Signals: sampled for review in their own stratum because Candidates are the entry path for promotion decisions and for Thin-History Policy validation

### Candidate-Type Pool Sampling

The Candidate-Type Pool ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) contains Signals proposed under a Candidate Signal type that has not yet been promoted. Sampling these Signals is a separate concern from sampling Signals of promoted types:

* all Candidate-Type Pool members are considered for review; representative Signals from each proposed type are surfaced preferentially
* candidate types with insufficient instances remain in the pool until a representative sample accumulates
* sampling of Candidate-Type Pool members does not reduce the per-stratum sample of promoted-type Signals

### Avoiding Selection Bias

Bias is managed by construction:

* Signals whose lifecycle has transitioned (for example, from Candidate to Surfaced) are eligible for review both before and after transition; review of a Signal is not gated on its current lifecycle state
* Signals emitted under Degraded Mode are sampled at the same rate as normal-mode Signals, and their Degraded-Mode status is visible to the reviewer; this avoids the sampler inadvertently excluding them
* supersession does not retire a Signal from the sample pool until enough time has passed for the review to be meaningful
* Retired Signals remain reviewable; whether a Signal was retired correctly is itself an evaluation question

### Load Bounding

Sampling respects a bounded per-period reviewer load. When the available review capacity is less than the ideal per-stratum sample:

* under-represented strata (typically thin-history, Candidate, low-Confidence) retain their share
* over-represented strata (typically high-Strength, high-Confidence, non-thin-history) are reduced first
* the sampling policy prefers maintaining stratification over maximizing total review count

Specific per-period load numbers and capacity planning are deferred to operational work.

---

## Candidate-Type Pool Promotion Workflow

[SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the Candidate-Type Pool's state machine and what a pool member is. This document owns the review workflow and the promotion decision. NARRATIVE_ANALYSIS.md owns how a promoted type is used in production.

### What A Candidate Type Carries

A Candidate Type in the pool carries:

* a draft operational definition produced by the proposing mechanism (research-driven or discovery-driven, per [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
* a proposed required-evidence pattern
* proposed strong-vs-weak criteria
* common false-positive patterns the proposer has already identified
* representative Candidate Signals produced under the proposed type, with full Basis and Evidence
* where applicable, the originating DerivationRun reference (for discovery-driven proposals from the Theme-Discovery Model in MODEL_STRATEGY.md)

### Review Criteria

A Candidate Type is evaluated against criteria that exist to prevent three failure modes: promoting a rediscovery of an existing type, promoting a type that is not operationally definable, and promoting a type that does not add meaning to the system.

* **meaningfulness** — does the type describe a class of narrative change that a human reader would find worth knowing?
* **distinctness** — is the type distinct from existing types, or is it a rediscovery under a different name? An apparent new type that resolves to "Narrative Drift filtered by topic" is not a new type.
* **operational definability** — can reviewers apply the proposed operational definition consistently across the representative Signals?
* **evidence grounding** — do the representative Signals carry adequate Basis and Evidence under the proposed type?
* **false-positive manageability** — are the common false-positive patterns the proposer identified plausibly addressable?

### Decision Outcomes

Each Candidate Type review produces one of four outcomes:

* **promote** — the type enters the canonical taxonomy; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) is extended; NARRATIVE_ANALYSIS.md integrates the new type under its Use Of Promoted Candidate Types section
* **reject** — the type is not promoted and is not revisited without material new evidence; the decision and its basis are recorded
* **hold** — the type is retained in the pool, with a noted reason (insufficient representative Signals, unresolved distinctness concerns, rubric not yet able to evaluate)
* **merge** — the type is judged to be a refinement of an existing type or a rediscovery; it is retired from the pool with a reference to the existing type

The decision record is immutable and is stored alongside the proposal. A rejected type remains discoverable; a subsequent proposal invoking the same type may reference the prior rejection and the material new evidence.

### Who Reviews Candidate Types

Candidate Type review is a more demanding review than per-Signal review. The Reviewer Cohort that handles it may be narrower; specific composition is deferred. The review is conducted against the same Review Rubric shape, extended with the Candidate Type criteria above.

### Three-Way Ownership, Honored

[SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) owns the Candidate-Type Pool state machine and what a pool member is. This document owns the promotion workflow and the review. NARRATIVE_ANALYSIS.md owns the in-production integration once a type is promoted. Each document references the others; none duplicates their concerns.

---

## Review Outcomes And Signal Lifecycle

Review records produce outcomes that interact with the Signal lifecycle. The lifecycle transitions themselves are specified in NARRATIVE_ANALYSIS.md; this document specifies how review outcomes trigger them.

### Review Outcomes Per Signal

Per the Review Rubric, each reviewed Signal acquires judgments on:

* is the described change real?
* if real, is it meaningful?
* is Commentary grounded?
* is Evidence sufficient?
* is the Signal likely a false positive, true positive, or indeterminate?

Aggregated across reviewers, these judgments support three kinds of lifecycle interactions:

### Interaction 1: Candidate → Surfaced Gated Promotion

For gated promotions — thin-history, Commentary grounding failure, contested comparability — the review outcome is the explicit promotion decision. A review aggregate that judges the Signal real, meaningful, and grounded supports promotion; any contrary judgment above a threshold holds the Candidate.

### Interaction 2: Surfaced → Retired

A Surfaced Signal may be retired on review when aggregated review judges the Signal a false positive, the Commentary ungrounded, or the Evidence insufficient. Retirement is not automatic from a single review; it requires the aggregate to cross a threshold.

### Interaction 3: Feedback Into Threshold Calibration

Per-type, per-stratum review outcomes feed the empirical determination of thresholds in NARRATIVE_ANALYSIS.md. This is the slower, strategic interaction: review does not just decide individual Signals, it informs the threshold shapes that produce future Candidates and Surfaced Signals.

### Suppressed Versus Retired

A Signal that is held at Candidate indefinitely is not retired; it is suppressed from user-facing surfaces but remains available for analytical and evaluation purposes. A Signal that is retired is a stronger statement: the system should not have emitted it. The distinction is preserved because they feed different corrections:

* suppressed Signals feed Confidence and threshold calibration — the system's bar may be too low
* retired Signals feed Basis and Evidence corrections — the system's inputs may have been wrong

---

## False-Positive Posture In Evaluation

The False-Positive Posture ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3) is operationalized in evaluation in three places.

### In Sampling

Sampling weights are tilted toward strata where false positives are most dangerous: low-Confidence, thin-history, Candidate status. Reviewing those strata at elevated rates is how the system earns information about where its false-positive risk concentrates.

### In Rubric Weighting

The rubric does not treat false-positive and false-negative reports symmetrically. A reviewer-identified false positive contributes more weight to lifecycle transitions (hold, retire) than a reviewer-identified miss contributes to threshold relaxation. This is an explicit design choice reflecting the posture.

### In Promotion Threshold Setting

Thresholds for promotion — per-type Strength and Confidence minima, Thin-History Policy levers — are set using review data with the false-positive posture in view. A threshold candidate that would admit more Surfaced Signals at the cost of admitting more false positives is not accepted on the grounds of raw coverage; the coverage gain must be judged worth the trust cost.

### The Posture Is Stated, Not Derived

The posture is a project-level commitment, not a calculation. Reviewers and evaluation engineers operate inside it rather than deriving it from numbers. It is accordingly stated explicitly on evaluation artifacts so that downstream readers can identify where it is in force.

---

## Maturation Of Evaluation Methodology

[CONTEXT.md](./CONTEXT.md) §14 acknowledges evaluation as an evolving artifact. [ASSUMPTIONS.md](./ASSUMPTIONS.md) T4 raises the risk that a perpetually-evolving harness defers accountability. This document commits the shape of evolution, without committing a schedule.

### Trajectory, Not Schedule

Evolution proceeds along three axes as the system accumulates history:

* **rubric refinement** — rubric items are added, removed, or re-specified based on where reviewer disagreement or blind spots concentrate
* **quantitative supplements** — aggregate statistics over review records (agreement rates, false-positive rates per type) become available and are used as inputs to threshold calibration; they do not become substitutes for review
* **retrospective-study expansion** — as historical depth grows, retrospective study covers a wider range of known narrative changes and a wider range of Entities

The trajectory extends evaluation; it does not replace human judgment as the authoritative mode during early development. If the trajectory ever proposes replacement, that proposal is itself an amendment to [CONTEXT.md](./CONTEXT.md) §14 and is out of scope for this document.

### What Does Not Change

Several aspects are stable across maturation:

* human review remains the first-line method; quantitative supplements support it but do not override it
* the false-positive posture remains in force unless [CONTEXT.md](./CONTEXT.md) §14 is amended
* evaluation does not assume ground truth; the absence of clean ground truth is treated as structural, not provisional
* evaluation does not adopt a single-scalar Signal-quality metric; the dimensions remain separable

### Linkage To Validated-Quality Framing

[ASSUMPTIONS.md](./ASSUMPTIONS.md) E1 raises "validated quality" as an undefined criterion for domain expansion. This document is the owner of that criterion. "Validated quality" at the point of v2 domain expansion is operationally:

* stable per-type review-agreement rates at levels sufficient to support threshold setting
* per-type false-positive rates at levels consistent with the False-Positive Posture
* Commentary grounding-failure rates at acceptable levels
* evaluation methodology itself mature enough that the next domain's Signals can be reviewed without restructuring the review process

No numeric commitment is made here. The operational definition is what matters; numeric floors are set empirically as the system matures.

---

## The Evaluation / Observability Boundary

[OBSERVABILITY.md](./OBSERVABILITY.md) specifies the boundary from the observability side; this document specifies it from the evaluation side. The two are load-bearing in the same way and are intentionally restated here rather than referenced.

* **Evaluation** asks: are the Signals the system emits useful, meaningful, consistent, and non-obvious? Are they surfaced in a way that reduces cognitive load?
* **Observability** asks: did the system execute its pipeline as specified? Did each component do its job? Is the system healthy?

A healthy pipeline may emit poor Signals. A sick pipeline may, by coincidence, produce correct Signals. Collapsing the two would conceal both failure modes. This document does not attempt to observe the system's pipeline; [OBSERVABILITY.md](./OBSERVABILITY.md) does not attempt to judge the system's Signals.

Specific points of contact:

* the Evaluation Harness is itself a component; its health is observed under [OBSERVABILITY.md](./OBSERVABILITY.md) Component Health; its reviewer throughput is an operational metric
* reviewer feedback records are stored alongside Signals; storage of those records is an infrastructure concern, their use is an evaluation concern
* re-derivation divergence detection is observability; whether a particular divergence is acceptable is an evaluation or testing concern

---

## What Evaluation Does Not Measure

This document does not measure, and is not authoritative on:

* system latency, throughput, or availability — [OBSERVABILITY.md](./OBSERVABILITY.md)
* component-level error rates — [OBSERVABILITY.md](./OBSERVABILITY.md)
* DerivationRun completion and re-derivation divergence detection — [OBSERVABILITY.md](./OBSERVABILITY.md)
* pipeline correctness in the sense of "did the code do what the spec said" — TESTING_STRATEGY.md
* model-internal metrics (perplexity, embedding geometry, etc.) — MODEL_STRATEGY.md, downstream infrastructure
* user-facing presentation quality of evaluation artifacts — [USER_EXPERIENCE.md](./USER_EXPERIENCE.md), if ever surfaced
* trading outcomes, market correlations, or predictive accuracy — out of scope ([CONTEXT.md](./CONTEXT.md) §10; [SCOPE.md](./SCOPE.md) Non-Goals)

These are named to make the boundary explicit; their omission from evaluation is deliberate.

---

## Deferred Decisions

* specific review tooling — downstream operational work
* reviewer selection criteria, training, and compensation — downstream operational work
* specific Review Rubric item wording — downstream operational work, informed by this document's rubric shape
* Reviewer Cohort sizing and composition — downstream operational work
* calibration-round cadence and trigger thresholds — downstream operational work
* how aggregated review records are versioned as the rubric evolves — downstream infrastructure work, with a pointer from this document
* whether a probationary-promotion state for Candidate Types is introduced (flagged as an open question in NARRATIVE_ANALYSIS.md) — this document is the owner if it is introduced
* adjudication mechanics for primary/secondary disagreement — downstream operational work
* how "validated quality" is operationally measured at the point of domain expansion ([ASSUMPTIONS.md](./ASSUMPTIONS.md) E1) — this document specifies the shape; empirical thresholds remain deferred

---

## Open Questions

* whether the Review Rubric benefits from being type-specific at the rubric-item level, or whether a single rubric shape spans all types with type-specific guidance — flagged; the current posture is a single shape with type-specific guidance
* how to evaluate Commentary itself when Commentary is increasingly type-scaffolded and grounded — flagged; the current rubric treats Commentary grounding as a reviewer judgment, not a model-internal metric
* how to scale evaluation as data domains expand beyond earnings call transcripts — flagged for v2+ work; v1 evaluation is Transcript-specific in the texture of its Evidence rendering even though the rubric shape is general
* whether quantitative supplements, once available, should ever be allowed to override a human review outcome — the current answer is no; flagged so the answer is not lost

---

## Recommended Glossary Extensions

Flagged for addition to [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **Review Rubric** — the structured set of questions that reviewers answer for each Signal, producing reviewer feedback records
* **Reviewer Cohort** — the group of reviewers operating at a given time, versioned so consistency-over-time of evaluation itself can be tracked
* **Reviewer Feedback Record** — an immutable record attaching a reviewer's rubric responses to a Signal and a reviewer identifier, with timestamp
* **Validated Quality** — the operational readiness of evaluation methodology and per-type Signal quality metrics that permits domain expansion per [ASSUMPTIONS.md](./ASSUMPTIONS.md) E1

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes [CONTEXT.md](./CONTEXT.md) §14's evaluation philosophy operationally
* [VISION.md](./VISION.md) — the failure mode Drift Toward Ground-Truth Theater is explicitly avoided by this document's design
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) — S3, S4, T4, X5, E1 are directly operationalized here
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms are flagged above
* [ARCHITECTURE.md](./ARCHITECTURE.md) — the Evaluation Harness component is the architectural home of this document's mechanics
* [DATA_MODEL.md](./DATA_MODEL.md) — Signal, Basis, Evidence, DerivationRun are the artifacts reviewed; Reviewer Feedback Records attach to Signal identifiers
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) — owns Signal Anatomy, the Candidate-Type Pool state machine, and Thin-History Policy shape; this document executes the promotion workflow
* MODEL_STRATEGY.md — reviewer feedback is a training input to learned models; this document specifies the feedback, not the training
* NARRATIVE_ANALYSIS.md — owns the lifecycle transition policy and the threshold shapes; this document supplies the empirical information that determines the thresholds and triggers the transitions
* EXPERIMENTATION.md — experiments on thresholds, Baseline methods, and Theme curation flow through the same review mechanics; experiments consume reviewer capacity and must be bounded by it
* [OBSERVABILITY.md](./OBSERVABILITY.md) — the observability/evaluation boundary is load-bearing; this document states the boundary from the evaluation side and does not duplicate OBSERVABILITY.md's concerns
* TESTING_STRATEGY.md — exercises pipeline correctness, which is adjacent to but distinct from Signal-quality evaluation
