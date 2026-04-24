# OBSERVABILITY.md

## Purpose Of This Document

OBSERVABILITY.md defines how the Signal Engine exposes its operational state at runtime: what can be seen about the system's execution, at what granularity, and through what surfaces. It is the operator-facing view of the system.

This document is conceptual. It makes no commitment to specific tools, vendors, protocols, or storage substrates.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Components referenced here are specified in [ARCHITECTURE.md](./ARCHITECTURE.md). Artifacts referenced here are specified in [DATA_MODEL.md](./DATA_MODEL.md).

---

## How To Read This Document

* observability concerns are described by what they reveal about system state, not by how they are collected
* the boundary between observability and Signal-quality evaluation (EVALUATION.md) is stated explicitly and is load-bearing
* instrumentation is described as a structural property of the system, not as a layer added at the end
* deferrals to downstream infrastructure work are named with the owner where possible
* new operational terms are flagged for glossary extension in the closing summary of the cluster rather than silently defined inline

---

## Guiding Commitments

Inherited from [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [ARCHITECTURE.md](./ARCHITECTURE.md), and [ASSUMPTIONS.md](./ASSUMPTIONS.md), and held as constraints on what observability may become:

* every component that produces derived data must expose operational state sufficient to confirm it ran as intended ([CONTEXT.md](./CONTEXT.md) §3.3; [ARCHITECTURE.md](./ARCHITECTURE.md) Cross-Cutting Concerns)
* observability is system-health instrumentation, distinct from the Signal-quality evaluation owned by the Evaluation Harness and EVALUATION.md
* observability must not undermine the traceability invariant, and must not be used as a substitute for it
* the system's operating posture is deliberate and batch-oriented ([ARCHITECTURE.md](./ARCHITECTURE.md) Operating Posture); real-time streaming observability is not assumed
* instrumentation must fit the low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5); a system whose instrumentation dominates its cost is out of scope
* external services may be used for observability infrastructure (log shipping, dashboarding, aggregation) but must not introduce a critical-path external dependency for the Signal Engine ([CONTEXT.md](./CONTEXT.md) §6.1)

---

## The Observability / Evaluation Boundary

The line between this document and EVALUATION.md is load-bearing. Drawing it loosely would allow system-health concerns to leak into Signal-quality concerns, or the other way around; both forms of leakage degrade the document set.

* **Observability** asks: did the system execute its pipeline as specified? Did each component do its job? Can the journey of a Document from source to Signal be reconstructed operationally? Is the system healthy?
* **Evaluation** asks: are the Signals the system emits useful, meaningful, consistent, and non-obvious? Are they surfaced in a way that reduces cognitive load? This is a judgment about the content of what the system produced.

The two can produce similar-looking artifacts — both generate numbers over time, both trigger human attention — but they answer different questions. A Signal that is wrong on the merits can arrive through a perfectly healthy pipeline. A pipeline that is unhealthy can produce Signals that happen to be correct. Collapsing the two would conceal both failure modes.

This boundary is restated, in the same terms, in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md).

---

## What Is Observable

Observability in this system is organized around three planes. The planes are conceptual; how they are implemented (logs, metrics, traces, structured events, dashboards) is a downstream tooling concern.

### Plane 1: Document Journey

The per-Document operational view of the pipeline. For any given Document, the system can reconstruct the sequence of steps it passed through from Ingestion to the Signal Store, the DerivationRuns involved, and whether each step completed as expected.

This plane answers questions of the form:

* did this Document's normalization succeed?
* was Entity Resolution applied, with what reconciliation confidence?
* did Heuristic Analysis, Representation, and Learned Analysis produce candidate evidence for this Document?
* did the Fusion Engine emit Signals for this Document, and if not, why not?
* at what stage did processing stop, if it stopped before reaching the Signal Store?

This plane is distinct from the signal-level traceability owned by the Evidence & Provenance Store. The Evidence & Provenance Store answers "what source Spans support this Signal?" — a question about the content of explanation. The Document Journey plane answers "what operational steps produced this artifact?" — a question about the execution of the pipeline. The two are complementary and must not collapse into each other.

### Plane 2: Component Health

The per-component operational view. For each component in [ARCHITECTURE.md](./ARCHITECTURE.md), a view of whether it is functioning, how much work it is doing, and what its outputs look like in aggregate.

Each component exposes, at minimum:

* **throughput** — how many artifacts it has processed over a relevant interval
* **latency** — time taken per artifact, expressed in a cadence appropriate to the batch-oriented posture
* **error rate** — fraction of inputs that could not be processed
* **output characteristics** — basic aggregate shape of outputs; for example, typical number of Utterances per Transcript for Document Processing, or typical count of candidate Signals per Document for the Fusion Engine. These serve as drift indicators; they are not themselves claims about Signal quality.

Component Health is about the component, not about the artifacts it produces. A component may be healthy and still produce useless output; a component may be unhealthy and produce, by accident or by recent changes, plausible-looking output. Health is orthogonal to quality.

### Plane 3: Derivation Traceability

The DerivationRun-centric operator view. Given an artifact, which DerivationRun produced it, under which logic version, at what time, and under what configuration.

This plane answers operational questions of the form:

* which DerivationRun produced this Baseline?
* which model version generated these learned features?
* when was the current Fusion Engine DerivationRun installed, and which artifacts have been produced under it?
* if a DerivationRun is recalled, which artifacts require retirement or re-derivation?

Derivation Traceability is operationally exposed even though DerivationRun is a [DATA_MODEL.md](./DATA_MODEL.md) artifact, because operators need to reason about which run produced what without traversing the Evidence & Provenance Store as a user would. The store is authoritative; this plane provides the operator surface into it.

---

## How Observability Supports System-Wide Invariants

### Re-Derivability

[DATA_MODEL.md](./DATA_MODEL.md) commits re-derivability as an invariant: derived data is re-derivable from Raw plus versioned DerivationRuns. Observability supports this invariant in two ways:

* **DerivationRun lineage is operationally visible.** An operator can enumerate the artifacts produced under a given DerivationRun, and — given a new DerivationRun — can identify the artifacts that need to be re-derived.
* **Divergence detection is observable.** When re-derivation is executed (for auditing, for a model version change, or for correction), the system can surface the difference between the prior artifact and the re-derived artifact. The existence of divergence is an observability concern; the judgment about whether a specific divergence is acceptable is a [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) or EVALUATION.md concern.

The system does not require re-derivation to be continuous. It does require that when re-derivation is performed, its results are observable.

### Traceability And Explainability

Traceability is a data-model property realized through the Evidence & Provenance Store ([ARCHITECTURE.md](./ARCHITECTURE.md) §11). Observability confirms that traceability is maintained — that every derived artifact carries its Basis and Evidence references — but does not itself substitute for it.

Observability fails safe. If a Signal is produced whose Basis or Evidence cannot be resolved, the observability plane surfaces this as an operational anomaly rather than allow the Signal to be emitted. The invariant that every Signal has a resolvable Basis and non-empty Evidence ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy) is enforced at emission; observability is the check that the enforcement held.

### Signal Lifecycle Integrity

Signal lifecycle transitions (Candidate, Surfaced, Stale, Superseded, Retired) are expressed as new Signal records with Lineage references ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)). Observability surfaces:

* the rate of transitions in each direction
* the fraction of Signals in each lifecycle state over time
* the Lineage chain for any given Signal — what it supersedes, what supersedes it

These indicators are operational. Whether a given rate of transitions is healthy or unhealthy in substance is a judgment for EVALUATION.md; whether the transitions are structurally well-formed is a concern of this plane.

### Temporal Integrity

The system's as-of query capability depends on derived artifacts not referring to information that did not exist at their processing time ([DATA_MODEL.md](./DATA_MODEL.md) Temporal Model). Observability surfaces the temporal metadata on derived artifacts — event time, observation time, processing time, valid-time — sufficient for an operator to check that no artifact has a processing time earlier than its inputs' observation times and that Baselines' valid-time intervals are monotone.

### Critical-Path Isolation

[CONTEXT.md](./CONTEXT.md) §6.1 commits to the absence of external large-language-model APIs in critical paths. Observability surfaces, through Component Health and scheduled dependency audits, any component in the critical path whose operation requires network access to a third-party model provider. The audit is an observability artifact, not a test; its place in the testing hierarchy is discussed in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md).

---

## Granularity And Cadence

Observability granularity is matched to the system's operating posture.

* per-Document granularity is the default for the Document Journey plane
* per-DerivationRun granularity is the default for Derivation Traceability
* per-component aggregate granularity is the default for Component Health; drilling down to per-Document detail is supported but not always materialized
* real-time streaming is not assumed. Near-real-time (on the order of minutes to tens of minutes) is acceptable where useful; specific cadences are deferred to downstream infrastructure work

Observability does not drive pipeline decisions. The pipeline does not consume its own observability output as a control signal in v1. Observability exists for operators, not for automation loops.

---

## The Operator View

An operator looking at the system, at any moment, is expected to be able to answer — without writing custom queries — the following questions:

* which Documents are currently being processed, and which have recently completed
* which components are healthy and which are not
* which DerivationRuns are current for each analytical layer
* which Signals have been emitted, updated, or retired in the recent window
* whether any upstream acquisition source is failing to deliver
* whether the Evidence & Provenance Store is receiving provenance writes from every producing component
* whether re-derivation, if run recently, produced divergences

The specific surfaces — dashboards, query interfaces, alert channels — are deferred to downstream infrastructure and operations work. This document defines what must be answerable; it does not define how the answer is presented.

---

## Cost Posture

Instrumentation is subject to the same low-capital constraint as the rest of the system ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint). In practice this means:

* sampling is acceptable where full-fidelity observability would be prohibitive
* retention of operational records is bounded; retention of derived artifacts is owned by DATA_GOVERNANCE.md and is not relaxed by this document
* high-throughput telemetry is out of scope in v1; the deliberate operating posture bounds telemetry volumes by ingestion volumes
* observability infrastructure (shipping, aggregation, dashboarding) may use external services where doing so is cost-rational and does not introduce a critical-path external dependency

---

## Out Of Scope: Signal-Quality Evaluation

The following concerns are owned by EVALUATION.md and are not within this document:

* whether a Signal is useful, meaningful, or non-obvious
* whether reviewers agree on Signal quality
* whether the Signal taxonomy is adequately decomposed
* whether the ranking of Signals reflects importance as a human reader would judge it
* whether emitted Confidence is well-calibrated against human judgment
* whether the Evaluation Harness is sampling the right Signals for review

These are evaluation questions. They interact with observability only in the operational sense — the Evaluation Harness is itself a component whose health is observed under Component Health above — but their substance is not within this document.

---

## Deferred Decisions

Named with the downstream owner where possible:

* specific logging, metrics, tracing, and dashboarding tools — downstream infrastructure work
* retention policy for operational records — downstream infrastructure work, with overlap against DATA_GOVERNANCE.md for derived-artifact retention
* alerting thresholds and alert routing policy — downstream operations work
* sampling rates and materialization strategy for Component Health drill-down — downstream infrastructure work
* on-call practice, incident response, escalation ladders — downstream operations work
* cadence of scheduled re-derivation audits — downstream infrastructure work, bounded by the low-capital constraint
* evaluation-specific observability (reviewer throughput, promotion pool depth, feedback turnaround) — EVALUATION.md

---

## What This Document Is Not

* not a tool selection document
* not a metrics catalog
* not an SLA or SLO specification for end-users
* not a specification of alerting policy or on-call rotation
* not a specification of dashboarding or visualization
* not a substitute for the Evidence & Provenance Store's traceability role

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [VISION.md](./VISION.md), and [ASSUMPTIONS.md](./ASSUMPTIONS.md) are authoritative; this document instruments their commitments operationally.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new operational terms introduced here (Document Journey, Component Health, Derivation Traceability) are flagged for glossary extension in the closing summary of the cluster.
* [ARCHITECTURE.md](./ARCHITECTURE.md) names the components whose health this document observes.
* [DATA_MODEL.md](./DATA_MODEL.md) names the artifacts (DerivationRun, Baseline, Signal, NarrativeState, Evidence) whose operational state this document exposes.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) owns Signal Anatomy and Lifecycle; this document observes them rather than defining them.
* [FAILURE_MODES.md](./FAILURE_MODES.md) names failure modes whose detection this document supplies; every mode in that document has a detection hook in one of the three planes above.
* [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) restates the observability / evaluation boundary in its own terms and exercises the invariants this document observes.
* EVALUATION.md owns Signal-quality questions that are explicitly out of scope here.
