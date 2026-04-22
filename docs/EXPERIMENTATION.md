# EXPERIMENTATION.md

## Purpose Of This Document

EXPERIMENTATION.md defines how experiments are proposed, specified, run, measured, and integrated back into the system: what kinds of experiments the system supports, how they are written down, how they exploit re-derivability to compare configurations without duplicating live pipelines, how a validated experiment graduates to production, and how institutional knowledge about past experiments is preserved.

This document is conceptual. It does not specify an A/B testing platform, does not select tooling, and does not commit specific experimental hardware.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* experiments are bounded activities with explicit hypothesis, method, and success criteria
* replay against re-derivability is the primary experimental substrate; parallel live pipelines are not
* experiments reuse human review through the Evaluation Harness; they do not build a shadow evaluation surface
* graduation to production is a review, not a threshold
* the Experiment Registry records experiments regardless of outcome, so the project accumulates knowledge
* what is out of scope in v1 is stated explicitly

---

## Guiding Commitments Inherited

Held as invariants throughout:

* the system is exploratory, not predictive ([CONTEXT.md](./CONTEXT.md) §16; [SCOPE.md](./SCOPE.md) Non-Goals)
* the re-derivability invariant ([DATA_MODEL.md](./DATA_MODEL.md) Guiding Principles, Derivation Layers) exists to support experimentation among its other purposes; this document exercises it
* the low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint) rules out experimental mechanisms that would multiply infrastructure cost
* evaluation is authoritative on Signal quality, not experiments ([CONTEXT.md](./CONTEXT.md) §14); experiments propose changes, evaluation judges them
* observability and evaluation boundaries are preserved ([OBSERVABILITY.md](./OBSERVABILITY.md); EVALUATION.md)
* institutional knowledge is a first-class concern ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T4 notes the risk of perpetually-evolving artifacts; experiments should produce durable records rather than ephemeral state)

---

## Types Of Experiments Supported

V1 supports four conceptual kinds of experiments. The list is not exhaustive; new kinds may be added as needs emerge, through amendment to this document.

### Offline Model Experiments

Changes to a model in the stack from MODEL_STRATEGY.md — a new Representation Model, a revised Analytical model, an adjustment to the Commentary Generation Model.

* the experiment is executed by producing a new DerivationRun under the candidate model and running it over a replayed historical period
* outputs are compared against the incumbent DerivationRun's outputs over the same period
* differences surface as divergences; the Evaluation Harness samples diverging cases for human review
* the experiment does not replace the incumbent in production until graduation

### Signal-Quality Experiments

Changes to the Fusion Engine's combination logic, threshold shapes in NARRATIVE_ANALYSIS.md, or Thin-History Policy levers.

* the experiment is executed by producing a new DerivationRun for the Fusion Engine under the revised policy and replaying
* outputs are compared Signal-by-Signal against the incumbent; divergences are the diffing unit
* the Evaluation Harness samples diverging cases, with stratification aware of which side of the experiment produced them
* success criteria are measured in terms of per-type review-rubric outcomes, per EVALUATION.md

### Baseline Method Experiments

Changes to how Baselines are constructed from Documents (NARRATIVE_ANALYSIS.md Baseline Construction And Maintenance), including changes to what a Baseline holds, how it updates, or how Baseline thinness is computed.

* the experiment produces a new DerivationRun for Baseline Maintenance and replays
* downstream Signals are re-derived under the new Baselines, enabling end-to-end comparison
* the cost is higher than for Fusion-only experiments because downstream re-derivation is required; the low-capital constraint bounds the scope of such experiments

### Theme-Curation Experiments

Changes to Theme proposal, merging, promotion, or retirement (NARRATIVE_ANALYSIS.md Theme Curation), or to the Theme-Discovery Model's cadence or output filtering.

* the experiment modifies the Theme curation workflow and replays
* ThemeInstances change shape; Narrative Drift and Omission Event Signals are consequently re-derived
* evaluation reviews both Theme changes themselves (new Themes, merged Themes, retired Themes) and the downstream Signal differences

### Not A Separate Kind: Ranking Experiments

Changes to ranking policy (NARRATIVE_ANALYSIS.md Ranking And Surfacing Policy) are executed under Signal-Quality Experiments. They do not require re-derivation of Signals, only re-ranking, and are therefore the least costly experimental kind.

---

## Experiment Specification

Every experiment is specified in advance. The specification is a durable artifact registered in the Experiment Registry (see below) regardless of outcome.

The specification carries, at minimum:

* **hypothesis** — a short, testable statement of what the change is expected to do, stated in Signal-quality terms where possible
* **method** — what is changed, under what new DerivationRun, against what incumbent DerivationRun, over what historical replay period
* **scope** — which Entities, Speakers, and Signal types are included in the replay; thin-history Entities are included by default unless explicitly excluded with reason
* **success criteria** — what the reviewer evaluation outcome would have to show for the change to be judged successful, expressed in per-dimension rubric terms per EVALUATION.md
* **failure criteria** — conditions under which the experiment should be abandoned without full completion (for example, degenerate behavior, runaway divergence counts, cost overruns)
* **expected cost** — the replay scope's implied inference and review cost, bounded to the low-capital posture
* **rollback plan** — how the experiment is withdrawn if needed, with no lingering side effects on the production pipeline

A specification is immutable once registered. Revisions produce a new specification that references the prior; this is how the registry preserves the reasoning trail when an experiment is refined mid-stream.

The word **Experiment Specification** is flagged for glossary extension.

---

## Replay As Experimental Substrate

The re-derivability invariant ([DATA_MODEL.md](./DATA_MODEL.md)) is the substrate. Every derived artifact names the DerivationRun that produced it; any layer is re-derivable from lower layers plus versioned derivation logic. Experiments exploit this.

The term **Historical Replay** is used for the operation of re-deriving a defined historical period under an experimental DerivationRun set; it is flagged for glossary extension.

### Replay Mechanics

* a replay is bounded by a time window (typically a run of historical quarters) and a scope (a set of Entities and Speakers)
* within the window, the experiment's candidate DerivationRuns produce new versions of the affected derived artifacts
* the incumbent DerivationRuns' artifacts remain in place and are not disturbed
* at the artifact level, differences between the incumbent and candidate — new Signals, retired Signals, changed Commentary, changed Strength or Confidence — are enumerable as a divergence set
* the divergence set is the input to evaluation

### Why Replay, Not Parallel Live Pipelines

Parallel live pipelines are out of scope for three reasons.

* they multiply infrastructure cost without adding information — the historical corpus, replayed, already contains the relevant signal
* they require a model-and-policy surface that behaves correctly under concurrent alternative configurations — that surface is not v1 scope
* they blur the accountability line: a production user seeing an experimental Signal cannot distinguish it from a validated one

Replay is performed against historical data and is fully observable as a distinct activity.

### Partial Replay

Under the low-capital constraint, full replay over the entire corpus may not be feasible for every experiment. Partial replay is acceptable when the sampled scope is representative in the same sense the Evaluation Harness requires ([ARCHITECTURE.md](./ARCHITECTURE.md) Component 12; EVALUATION.md): stratified across Signal type, Strength, Confidence, and thin-history status.

A partial replay's specification names what was sampled and why it is representative. A partial replay cannot support a claim that generalizes beyond its scope.

### Temporal Integrity Of Replay

Replay must not violate temporal integrity ([DATA_MODEL.md](./DATA_MODEL.md) Temporal Model):

* replayed derived artifacts have processing times corresponding to the experiment execution, not to the original processing
* replayed artifacts reference the experimental DerivationRuns, not the incumbent
* no replayed artifact may reference information that did not exist at the original processing time; lookahead contamination is excluded by construction
* the experimental DerivationRuns' creation times are the experiment execution times, not retroactively set

This is the temporal-integrity guarantee that makes replay comparable to the original production pipeline rather than to a counterfactual that could not have run at the time.

---

## Graduation To Production

An experiment does not graduate to production by crossing a numeric threshold. It graduates through review.

### The Graduation Review

A graduation review is convened once an experiment's replay is complete and its evaluation outcomes are available.

* the review considers the experiment's hypothesis, method, success criteria, and actual review outcomes together
* the review is performed by an appropriate Reviewer Cohort — composition deferred, informed by EVALUATION.md's role definitions — and is recorded as a durable artifact
* the review answers: does this change do what the hypothesis claims, within the success criteria, and without causing regressions the False-Positive Posture would find intolerable?
* the review outcome is one of: **graduate**, **reject**, **hold**, or **narrow** (graduate within a reduced scope)

### Graduation Mechanics

When an experiment is graduated:

* the candidate DerivationRuns become the incumbents; the prior incumbents are retained and remain referenceable for historical query
* the relevant documents (NARRATIVE_ANALYSIS.md for thresholds and policies, MODEL_STRATEGY.md for model specifics where warranted, [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) when a new type is involved via the Candidate-Type Pool) are updated to reflect the change
* forward-production Signals are emitted under the new DerivationRuns
* historical Signals are not retroactively re-derived solely because the incumbent changed; re-derivation on demand is available but is a separate decision

### Rejection And Hold

A rejected experiment is recorded with the reasons for rejection. The reasons are themselves institutional knowledge; a later proposal pursuing the same direction may reference the prior rejection and the material new evidence motivating reconsideration.

A held experiment is not yet ready for graduation but has not been rejected. Common reasons include insufficient sample size after partial replay, unresolved concerns surfaced during graduation review, or a preceding experiment that must graduate first. A hold is temporary; held experiments that age past a deferred threshold are surfaced for re-review or formal rejection.

### Narrow Graduation

A narrow graduation promotes a change within a scope smaller than the original hypothesis claimed — for example, graduating a new Confidence-Feature Model only for a specified class of Entities. This is distinct from rejection and from full graduation; it produces a commitment and a named scope, and the surface of the change is bounded to that scope.

---

## The Experiment Registry

The **Experiment Registry** is the durable store of experiment specifications, replay artifacts, and graduation outcomes. The term is flagged for glossary extension.

### What The Registry Holds

* the specification for every registered experiment, immutable, with references to any subsequent revisions
* the DerivationRun identifiers created for the experiment
* the scope and time window of the replay that was executed
* the divergence-set characterization (counts, per-type, per-stratum)
* the reviewer feedback collected during evaluation, attached to the relevant Signal identifiers
* the graduation review artifact and its outcome
* the rollback artifact if the experiment was abandoned

### What The Registry Does Not Hold

* full copies of the replayed artifacts themselves — those are in the relevant stores ([DATA_MODEL.md](./DATA_MODEL.md); Signal Store; Evidence & Provenance Store) under their experimental DerivationRun identifiers
* continuous telemetry about the experiment's execution — that is [OBSERVABILITY.md](./OBSERVABILITY.md)'s concern
* speculation or unregistered investigations; the registry is for registered experiments, not for all exploratory work

### Discoverability

The registry is indexed so that a contributor can find:

* all experiments that touched a given Signal type
* all experiments that modified a given model in MODEL_STRATEGY.md's stack
* all experiments whose hypothesis bore on thin-history posture
* all experiments with a given outcome (graduated, rejected, held)

The specific query surface is deferred; the property that matters is that institutional knowledge about past experiments is not lost.

### Versioning Of Specifications

When an experiment is refined mid-stream, the revised specification references the prior. The registry preserves both and records the sequence. This is how the reasoning trail behind a decision remains reconstructible after the fact.

---

## Interaction With Evaluation

EVALUATION.md owns Signal-quality evaluation; this document owns experiments. They interact tightly and must not duplicate.

### Shared Human Review

Experiments do not build a shadow evaluation surface. They use the Evaluation Harness through the same interfaces that production evaluation uses. Specifically:

* the divergence set produced by a replay is sampled for review using the same stratification rules EVALUATION.md's sampling design uses
* reviews are recorded against the same Review Rubric, with reviewer identity, cohort version, and Signal identifier attached
* reviewer feedback on experimental Signals is stored alongside production reviewer feedback but is tagged with the experiment identifier so it does not contaminate production calibration

### Reviewer Load Is Shared

Experimental review draws from the same bounded reviewer capacity as production evaluation. An experiment's expected cost in the specification includes its expected reviewer draw. Experiments that would exceed the budget are scoped down, queued, or rejected.

### Evaluation Is Authoritative On Outcomes

This document specifies how experiments are proposed and run. EVALUATION.md is authoritative on whether the replay's Signal-quality outcomes met the experiment's success criteria. The graduation review consults the evaluation outcome; it does not produce its own independent quality judgment.

### What This Document Does Not Duplicate

* the Review Rubric — owned by EVALUATION.md
* sampling design — owned by EVALUATION.md
* false-positive posture operationalization — owned by EVALUATION.md
* Candidate-Type Pool promotion workflow — owned by EVALUATION.md; an experiment may *propose* a candidate type via MODEL_STRATEGY.md's Theme-Discovery Model but the review and promotion remain EVALUATION.md's
* reviewer calibration — owned by EVALUATION.md

This document references each of these; it does not restate them.

---

## Out Of Scope For V1

V1 deliberately excludes several experimental capabilities, to honor the low-capital posture and the deliberate operating mode.

* **live A/B experimentation in production** — excluded; see Replay, Not Parallel Live Pipelines
* **real-time experiments** — excluded; the deliberate posture ([ARCHITECTURE.md](./ARCHITECTURE.md) Operating Posture) is incompatible with real-time experimental measurement
* **market-correlation experiments** — excluded; out of v1 scope per [SCOPE.md](./SCOPE.md) Deferred and [CONTEXT.md](./CONTEXT.md) §10
* **user-facing A/B experiments** — excluded; v1 has no multi-user surface and no randomized-user mechanism ([SCOPE.md](./SCOPE.md) Deferred, User Experience Goals)
* **automated experiment generation** — excluded; experiments are human-authored, reviewed, and recorded
* **multi-domain experiments** — v1 is earnings-call-transcript-only ([CONTEXT.md](./CONTEXT.md) §8); experiments that require another data domain are out of scope until that domain is in scope

Excluded does not mean forbidden forever. It means not assumed as a v1 capability. Should any become necessary, adoption is a decision on this document, and on [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) where relevant.

---

## What This Document Is Not

* not an A/B testing platform specification
* not a research agenda ([RESEARCH_NOTES.md](./RESEARCH_NOTES.md), where it exists, owns that)
* not an evaluation methodology
* not a deployment specification
* not a model training-data specification

---

## Deferred Decisions

* specific tooling for experiment execution and replay orchestration — downstream infrastructure work
* registry query surface and indexing — downstream infrastructure work
* cost budgeting and scheduling of experiments under the low-capital constraint — downstream operational work
* composition of the graduation-review Reviewer Cohort — downstream operational work, informed by EVALUATION.md
* cadence of retired-and-held-experiment audit — downstream operational work
* retention policy for experimental DerivationRuns and replayed artifacts — downstream infrastructure work with overlap on DATA_GOVERNANCE.md
* whether graduation of a Candidate Type from the Candidate-Type Pool is treated as an experiment in this document's sense or handled entirely through EVALUATION.md's workflow — current posture is the latter; flagged for review if pressure emerges

---

## Open Questions

* how to present replay divergences to reviewers without priming them about which side is incumbent and which is candidate — flagged; the current posture is that the reviewer sees the Signal on its own terms and the experiment-vs-incumbent identity is metadata on the feedback record, not an input to the review
* how narrow graduations are bounded against silent scope creep — flagged; the current posture is that narrow-graduation scope is a first-class field on the committed change and any expansion is itself a new experiment
* how experiment outcomes feed back into [ASSUMPTIONS.md](./ASSUMPTIONS.md) revisions when an assumption is challenged by experimental evidence — flagged; assumptions are authoritative but they can be wrong, and the registry's reasoning trail is the mechanism for surfacing them

---

## Recommended Glossary Extensions

Flagged for addition to [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **Experiment Specification** — the immutable, durable description of a proposed experiment, carrying hypothesis, method, scope, success and failure criteria, expected cost, and rollback plan
* **Historical Replay** — the execution of experimental DerivationRuns over a defined historical window and scope, producing artifacts comparable to the incumbent production artifacts over the same period
* **Experiment Registry** — the durable store of experiment specifications, replay artifacts, evaluation outcomes, and graduation decisions, indexed for discoverability
* **Graduation Review** — the human review that decides whether an experiment's outcomes warrant promoting the candidate configuration to production, with outcomes graduate, reject, hold, or narrow
* **Narrow Graduation** — an experiment outcome in which the candidate is promoted for a bounded scope smaller than the experiment's original hypothesis

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes the exploratory posture operationally
* [VISION.md](./VISION.md) — the Drift Toward Ground-Truth Theater failure mode is specifically avoided by routing experimental outcomes through human review rather than through automatic metrics
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) — T4 and S4 are operationalized here; this document is one of the mechanisms by which assumption revisions are surfaced over time
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms are flagged above
* [DATA_MODEL.md](./DATA_MODEL.md) — the re-derivability invariant and the DerivationRun mechanism are the substrate this document operates on
* [ARCHITECTURE.md](./ARCHITECTURE.md) — the Evaluation Harness is the component through which experimental review is performed; the Signal Store and Evidence & Provenance Store hold experimental artifacts under experimental DerivationRuns
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) — the Candidate-Type Pool state machine; discovery-driven proposals from experiments may create Candidate Types but their promotion is EVALUATION.md's workflow
* MODEL_STRATEGY.md — model versioning and replacement rely on this document's replay mechanics; this document references that replacement is a common source of experiments
* NARRATIVE_ANALYSIS.md — policy and threshold changes flow through this document's experimentation path; graduated changes update NARRATIVE_ANALYSIS.md
* EVALUATION.md — authoritative on Signal-quality evaluation, including of experimental replays; this document defers to it and does not duplicate
* [OBSERVABILITY.md](./OBSERVABILITY.md) — observes the execution of experiments as operational activity; does not judge experiment outcomes
* [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) — tests pipeline correctness under both incumbent and candidate DerivationRuns; distinct from this document's Signal-quality-centered view
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md), where it exists, owns the research agenda from which experiments emerge; this document concerns how research hypotheses become experiments once they are ready to be tested
