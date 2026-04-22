# FAILURE_MODES.md

## Purpose Of This Document

FAILURE_MODES.md enumerates the ways each architectural component and cross-cutting concern in the Signal Engine can go wrong: what the failure is, what causes it, how it is detected, what invariants it threatens, how the system degrades, and how the system recovers at a conceptual level.

This document is conceptual. It does not specify alerting thresholds, runbooks, on-call rotation, or incident-response automation.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Components referenced here are specified in [ARCHITECTURE.md](./ARCHITECTURE.md). Invariants referenced here are specified in [DATA_MODEL.md](./DATA_MODEL.md) and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

---

## How To Read This Document

* each failure mode follows the same shape: cause, detection, blast radius, invariants threatened, degradation posture, and recovery sketch
* causes are categorized against a small cause taxonomy (below) so that modes can be compared
* every failure mode has a detection hook in [OBSERVABILITY.md](./OBSERVABILITY.md) and, where applicable, a testing hook in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
* modes are enumerated per [ARCHITECTURE.md](./ARCHITECTURE.md) component; cross-cutting modes follow
* deferred concerns — specific thresholds, automated recovery, incident-response rotation — are named with the downstream owner

---

## Guiding Commitments

Inherited from [CONTEXT.md](./CONTEXT.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md):

* no failure mode may silently violate a system-wide invariant; where an invariant could be violated, the mode is categorized as fatal and its recovery sketch includes restoration of the invariant
* the invariants this document treats as load-bearing:
  * traceability of every Signal to Basis, Evidence, and source Spans ([CONTEXT.md](./CONTEXT.md) §3.3)
  * re-derivability of all derived artifacts from Raw plus DerivationRuns ([DATA_MODEL.md](./DATA_MODEL.md))
  * immutability of Raw, of Signals once emitted, and of derived artifacts under their DerivationRun ([DATA_MODEL.md](./DATA_MODEL.md))
  * Signal lifecycle expressed as new records with Lineage, never as mutation ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
  * no external LLM API in critical paths ([CONTEXT.md](./CONTEXT.md) §6.1)
  * non-empty Basis, Evidence, and Commentary on every emitted Signal ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)
* the system is hybrid and each layer can fail independently; partial operation is preferred over all-or-nothing failure unless an invariant is at stake
* the deliberate, batch operating posture allows recovery to take time; this document does not assume real-time self-healing

---

## Cause Categories

Each failure mode's cause is drawn from the following categories. Some modes have multiple causes; the categorization is for reasoning, not for exclusive labeling.

* **Data-quality** — the input Document is malformed, truncated, mis-attributed, or otherwise does not match the structure downstream components expect
* **Upstream** — the source that should have provided data did not, or provided it late, or provided it inconsistently (for example, a provider changes its transcript format without notice)
* **Compute** — a component's logic or model produced an incorrect, inconsistent, or non-terminating result for a given input
* **Infrastructure** — the substrate (storage, network, orchestration) failed or degraded
* **Logic** — the component's specification or its code embodies an error; the component did what it was told, and what it was told was wrong

---

## Invariant Classification

Each failure mode below names the invariants it could threaten. The set is finite:

* **T (Traceability)** — a Signal cannot be traced back to Basis, Evidence, or Spans
* **R (Re-derivability)** — derived artifacts cannot be re-derived from Raw plus DerivationRuns
* **I (Immutability)** — a Raw artifact, a Signal, or a DerivationRun-bound derived artifact has been mutated in place
* **L (Lifecycle)** — a Signal lifecycle transition has been expressed as mutation rather than as a new record with Lineage, or a Signal has been emitted without a valid lifecycle state
* **C (Critical-Path Isolation)** — an external large-language-model API has appeared in, or has been relied on by, a critical path
* **E (Explainability)** — a Signal has been emitted whose Basis, Evidence, or Commentary is absent or unresolvable

A failure mode that threatens any of T, R, I, L, C, or E is **fatal** — it must stop the pipeline at the relevant scope, and its recovery must restore the invariant. A failure mode that threatens none of these is **absorbable** — processing may continue for unaffected work with reduced capability while the mode is investigated.

The distinction is structural. Absorbable does not mean unimportant; it means that partial operation is safe.

---

## Component Failure Modes

The modes below are organized by component as named in [ARCHITECTURE.md](./ARCHITECTURE.md). For each, representative modes are listed. The list is not exhaustive; Wave 2 architects may discover further modes during detailed work and are expected to add them here rather than handle them silently.

### 1. Ingestion

**Mode: Upstream source unavailable.**

* Cause: Upstream.
* Detection: Component Health ([OBSERVABILITY.md](./OBSERVABILITY.md) Plane 2) surfaces drops in throughput from an expected source; Document Journey shows no new Documents from the source within the expected cadence window.
* Blast radius: Documents from the affected source do not enter the system; downstream work on those Documents is deferred, not corrupted.
* Invariants threatened: none. Absorbable.
* Degradation posture: the system continues to operate on Documents from other sources. Per-Entity Baselines may become thin relative to expectation; Baseline Maintenance surfaces this through the existing thinness signal, not as a new concept.
* Recovery sketch: upstream is restored; Ingestion resumes from the cadence point. Gaps are recorded as gaps rather than backfilled silently.

**Mode: Source format silently changes.**

* Cause: Upstream, typically surfacing as Data-quality once encountered.
* Detection: Component Health — changes in output characteristics for Ingestion and Document Processing (for example, sharp drops in Utterance counts per Transcript, or spikes in normalization failure rate).
* Blast radius: affected Documents either fail downstream or are misparsed; misparsing is more dangerous than failing.
* Invariants threatened: potentially T if a misparsed Document's Spans no longer correspond to its source text.
* Degradation posture: fail-loud for the affected source; do not emit Signals based on Documents whose normalization failed.
* Recovery sketch: Document Processing logic is updated; affected Documents are re-normalized under a new DerivationRun; Signals that depended on the misparsed form are retired under the existing lifecycle.

**Mode: Duplicate ingestion of the same artifact.**

* Cause: Upstream or Infrastructure.
* Detection: Document identity reconciliation at Ingestion; duplicate flag surfaced through Component Health.
* Blast radius: without deduplication, duplicate Documents could inflate Baselines and distort comparisons.
* Invariants threatened: R indirectly, if the duplicate is counted as new history. Immutability is preserved either way.
* Degradation posture: fail-loud on duplicates that have not been explicitly reconciled; do not blend.
* Recovery sketch: identify the canonical Document; record the duplicate as a known alias; re-derive Baselines and ThemeInstances affected.

### 2. Document Processing

**Mode: Normalization produces invalid structure.**

* Cause: Data-quality or Logic.
* Detection: structural validation at the boundary between Document Processing and downstream components; Component Health surfaces invalid-structure rates.
* Blast radius: the affected Documents do not proceed to analysis; downstream Signals for those Documents are not emitted.
* Invariants threatened: T if an invalid Document is allowed to proceed. Fatal per-Document; absorbable at the system level.
* Degradation posture: reject the Document; do not emit partial results.
* Recovery sketch: Document Processing is updated; the Document is re-normalized under a new DerivationRun; its journey resumes.

**Mode: Segmentation misidentifies Transcript sections.**

* Cause: Data-quality (format variability) or Logic.
* Detection: Component Health — distribution of Segment counts and types per Transcript compared against the expected shape for the source; divergence surfaced as a drift indicator.
* Blast radius: downstream heuristic and learned analyses operate on the wrong scope; Signal quality is affected without the system necessarily failing.
* Invariants threatened: none directly. Absorbable but high-priority.
* Degradation posture: continue processing; flag affected Documents; allow the Evaluation Harness to surface the downstream Signal-quality effect through its own channels.
* Recovery sketch: update segmentation logic; re-derive under a new DerivationRun; retire and replace Signals affected by the segmentation error via the lifecycle.

### 3. Entity Resolution

**Mode: Document mis-attributed to wrong Entity.**

* Cause: Data-quality (ambiguous source metadata) or Logic (reconciliation error).
* Detection: reconciliation confidence drops below an expected range; downstream anomalies in Baseline updates for Entities that should not have received the Document.
* Blast radius: an Entity's Baseline is contaminated; Signals for that Entity become untrustworthy.
* Invariants threatened: T and E, because Basis and Evidence for Signals on the mis-attributed Document reference text that is not actually about the named Entity.
* Degradation posture: fatal for the affected Entity. Retire dependent Signals; re-derive Baselines after correction.
* Recovery sketch: re-reconcile the Document; re-derive dependent artifacts under new DerivationRuns; retire Signals whose Basis depends on the mis-attribution.

**Mode: Speaker reconciliation fails or is ambiguous.**

* Cause: Data-quality (missing or ambiguous speaker names) or Logic.
* Detection: reconciliation confidence is recorded on-artifact ([ARCHITECTURE.md](./ARCHITECTURE.md) §3); Component Health surfaces the distribution.
* Blast radius: Confidence Shift and behavioral profiling lose fidelity. Omission Events may be mis-attributed across Speakers.
* Invariants threatened: none if reconciliation confidence is honestly recorded; E is at risk if the ambiguity is silently asserted as certainty.
* Degradation posture: emit Speaker-scoped Signals with reduced Confidence; do not assert strong Confidence Shift when Speaker identity is uncertain.
* Recovery sketch: improve reconciliation logic; re-derive Speaker-scoped analyses.

### 4. Baseline Maintenance

**Mode: Baseline construction method changes without versioning.**

* Cause: Logic (intentional change performed without a new DerivationRun).
* Detection: Derivation Traceability ([OBSERVABILITY.md](./OBSERVABILITY.md) Plane 3) surfaces the new DerivationRun; Baselines under the new run must occupy distinct valid-time intervals from those under the old run.
* Blast radius: if historical Baselines are overwritten rather than superseded, temporal reasoning is corrupted.
* Invariants threatened: R and I — Baselines are versioned artifacts ([DATA_MODEL.md](./DATA_MODEL.md)) and a changed construction method must produce new valid-time intervals rather than mutate existing ones.
* Degradation posture: fatal. Baseline updates under an unversioned method change must be blocked at the Baseline Maintenance boundary.
* Recovery sketch: assign a new DerivationRun; produce new valid-time Baselines; retain prior Baselines untouched; re-run Signal-level comparisons that should use the new Baselines.

**Mode: Baseline thinness under-reported.**

* Cause: Logic.
* Detection: thinness is a queryable property ([ARCHITECTURE.md](./ARCHITECTURE.md) §4; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Baseline Thinness). An operator-facing check compares reported thinness against underlying history count.
* Blast radius: thin-history Signals are emitted with higher Confidence than warranted ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Thin-History Policy).
* Invariants threatened: none structurally, but the Thin-History Policy is violated in effect.
* Degradation posture: treat as absorbable for non-Signal-producing flows but fatal at Signal emission — the Fusion Engine's Confidence computation depends on accurate thinness.
* Recovery sketch: correct thinness reporting; re-derive affected Signals; lifecycle prior Signals as Superseded.

### 5. Heuristic Analysis

**Mode: A rule does not fire when it should.**

* Cause: Logic or Data-quality (input structure the rule was not written for).
* Detection: regression testing ([TESTING_STRATEGY.md](./TESTING_STRATEGY.md)); Component Health — rule firing rates drift unexpectedly; the Evaluation Harness may surface downstream Signal-quality effects over time.
* Blast radius: candidate evidence is missing; the Fusion Engine produces fewer or weaker Signals.
* Invariants threatened: none directly.
* Degradation posture: absorbable. The system produces a narrower pool of candidate evidence; Basis Disagreement Confidence adjustments absorb the effect at the Fusion Engine.
* Recovery sketch: update the rule; re-derive under a new DerivationRun; the Fusion Engine re-emits Signals where appropriate.

**Mode: A rule fires when it should not.**

* Cause: Logic or Data-quality.
* Detection: regression testing; Component Health — rule firing rate spikes; downstream Basis shows heuristic-only contributions that disagree systematically with learned contributions.
* Blast radius: candidate evidence is noisy; the Fusion Engine may emit weaker Signals.
* Invariants threatened: none directly; Signal Confidence is expected to reflect Basis disagreement.
* Degradation posture: absorbable. The Fusion Engine's Confidence computation is expected to downweight, per [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).
* Recovery sketch: update the rule; re-derive; retire Signals whose Basis depended on the incorrect rule firing.

### 6. Representation

**Mode: Representation model outputs are degenerate or unstable.**

* Cause: Compute (model drift or numerical instability) or Logic (training or versioning error).
* Detection: Component Health — distribution of representation outputs over a reference set; monitoring for sudden distribution shifts; behavioral and golden-set replay in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md).
* Blast radius: downstream Learned Analysis produces candidate evidence from degraded representations; Signal quality is affected.
* Invariants threatened: none directly. E is at risk if the Fusion Engine asserts Basis contributions that depend on a known-degraded representation without adjusting Confidence.
* Degradation posture: fatal for the affected DerivationRun. Fall back to the previous Representation DerivationRun for critical-path use; emit Signals only from configurations known to be stable.
* Recovery sketch: investigate root cause; retrain or roll back; re-derive learned features under a new DerivationRun; retire Signals whose Basis depends on the degraded representation.

**Mode: Representation model unavailable.**

* Cause: Infrastructure.
* Detection: Component Health — Representation fails to produce output.
* Blast radius: Learned Analysis cannot produce new candidate evidence; the Fusion Engine continues to operate with heuristic-only contributions, producing fewer Signals with the appropriate Basis Disagreement posture.
* Invariants threatened: none directly.
* Degradation posture: absorbable. The system continues to operate on heuristic-only Basis with adjusted Confidence. A prolonged outage escalates to fatal if it prevents re-derivation or threatens traceability.
* Recovery sketch: restore the model; resume Learned Analysis; re-derive where warranted.

### 7. Learned Analysis

**Mode: Learned Analysis disagrees systematically with Heuristic Analysis.**

* Cause: Compute (model drift) or Logic (either rule or model specification error).
* Detection: the Fusion Engine records Basis Disagreement per Signal; aggregate disagreement rate is surfaced through Component Health.
* Blast radius: Signal quality is affected; Confidence computation is load-bearing under this mode.
* Invariants threatened: none directly. E is preserved so long as Basis Disagreement is honestly represented on emitted Signals.
* Degradation posture: absorbable. Confidence adjustment is the containment.
* Recovery sketch: investigate; re-train, re-rule, or reconcile the specifications; re-derive; lifecycle prior Signals as appropriate.

**Mode: Candidate Signal type proposal unsound.**

* Cause: Compute (unsupervised discovery produces spurious candidate types).
* Detection: Candidate-Type Pool review workflow (EVALUATION.md); Component Health surfaces the pool's throughput and review-outcome distribution.
* Blast radius: none if the pool's review gate holds; the gate must hold for unsound proposals not to reach the canonical taxonomy.
* Invariants threatened: none if the gate is honored.
* Degradation posture: absorbable. The gate is designed for this mode.
* Recovery sketch: reject at review; adjust proposal generation if rejection rate is persistently high.

### 8. Fusion Engine

**Mode: A Signal is emitted without resolvable Basis or Evidence.**

* Cause: Logic.
* Detection: Signal emission precondition at the Signal Store boundary — reject emission if the Basis chain is unresolvable or Evidence is empty; rejection is surfaced through Component Health. Also exercised at the Signal lifecycle test layer in [TESTING_STRATEGY.md](./TESTING_STRATEGY.md).
* Blast radius: none if the precondition check holds. If the check fails, the invariant is violated.
* Invariants threatened: T and E. Fatal.
* Degradation posture: fatal. Signal emission halts until the precondition check is restored.
* Recovery sketch: restore the precondition; audit recently emitted Signals for compliance; retire any non-compliant Signals via the lifecycle.

**Mode: Conflict resolution between heuristic and learned contributions produces inconsistent Signals.**

* Cause: Logic (resolution strategy error) or Compute (numerical or configuration issue).
* Detection: contract and integration tests ([TESTING_STRATEGY.md](./TESTING_STRATEGY.md)); Component Health surfaces shifts in the distribution of Basis Disagreement outcomes; the Evaluation Harness surfaces quality effects downstream.
* Blast radius: Signal quality suffers; traceability is preserved so long as Basis is recorded honestly.
* Invariants threatened: E indirectly if Basis representation conceals the conflict.
* Degradation posture: absorbable for individual Signals; fatal if Basis representation is found to conceal conflicts rather than represent them.
* Recovery sketch: correct the resolution strategy; re-derive; lifecycle affected Signals.

**Mode: Fusion Engine fails entirely.**

* Cause: Compute or Infrastructure.
* Detection: Component Health — Fusion Engine throughput drops to near zero.
* Blast radius: the Signal Store does not receive new Signals. Upstream components continue; candidate evidence accumulates pending fusion.
* Invariants threatened: none directly. Candidate evidence remains available for re-derivation once fusion is restored.
* Degradation posture: absorbable. The system operates as a pipeline whose final step is delayed.
* Recovery sketch: restore the Fusion Engine; re-run emission for accumulated candidate evidence; record a DerivationRun for the recovery.

### 9. Signal Store

**Mode: Partial write — Signal recorded without Basis or Evidence reference.**

* Cause: Infrastructure (storage failure mid-commit) or Logic.
* Detection: post-commit integrity check at the Signal Store boundary; Component Health surfaces integrity anomalies.
* Blast radius: the invariant that every Signal has Basis and Evidence is at risk.
* Invariants threatened: T and E. Fatal.
* Degradation posture: fatal. A Signal that cannot be written atomically with its Basis and Evidence must not enter the Signal Store.
* Recovery sketch: atomic-write contract enforced at the Signal Store boundary; on failure, the Signal is not emitted and the Fusion Engine retries after the storage issue is resolved.

**Mode: Mutation of an emitted Signal.**

* Cause: Logic (incorrect lifecycle implementation).
* Detection: immutability checks; Component Health — direct write attempts to existing Signal records surface as anomalies.
* Blast radius: Lineage breaks; historical state is corrupted.
* Invariants threatened: I and L, and by extension R. Fatal.
* Degradation posture: fatal. Reject mutation attempts at the Signal Store boundary.
* Recovery sketch: restore from immutable history; identify which lifecycle transition was mis-expressed; re-express it as a new record with Lineage.

### 10. Ranking & Surfacing

**Mode: Ranking produces unstable or inconsistent orderings.**

* Cause: Logic or Compute.
* Detection: contract and integration tests; Component Health — instability measured by comparing successive rankings under unchanged inputs.
* Blast radius: user-facing surface quality degrades; emission is unaffected.
* Invariants threatened: none.
* Degradation posture: absorbable. Roll back to a stable Ranking DerivationRun if necessary.
* Recovery sketch: correct the ranking logic; re-derive.

**Mode: Ranking surfaces retired or invalid Signals.**

* Cause: Logic.
* Detection: lifecycle-state filtering check at the Ranking boundary; Component Health surfaces the rate.
* Blast radius: users see stale or invalidated Signals.
* Invariants threatened: L in effect, though lifecycle state is still recorded honestly on the underlying artifact.
* Degradation posture: fatal per item at the boundary; absorbable at the component level.
* Recovery sketch: enforce lifecycle filtering at Ranking; re-derive the affected views.

### 11. Evidence & Provenance Store

**Mode: Partial provenance write.**

* Cause: Infrastructure.
* Detection: at-write integrity check; cross-check between derived-artifact store and provenance store.
* Blast radius: derived artifacts may reference Spans the provenance store cannot resolve.
* Invariants threatened: T and E. Fatal.
* Degradation posture: fatal. The producing component must treat the write as not having occurred and retry; no downstream emission may proceed from an artifact whose provenance is not persisted.
* Recovery sketch: atomic-write contract; on failure, re-execute the producing step under a new DerivationRun if needed.

**Mode: Drift between derived-artifact store and provenance store.**

* Cause: Logic or Infrastructure.
* Detection: scheduled integrity audit; Component Health surfaces the audit's outcome.
* Blast radius: silent divergence would violate traceability for affected artifacts.
* Invariants threatened: T. Fatal on discovery.
* Degradation posture: fatal for affected artifacts; absorbable at the system level if the drift is isolated.
* Recovery sketch: re-derive affected artifacts; retire Signals whose provenance cannot be restored.

### 12. Evaluation Harness

**Mode: Evaluation Harness unavailable.**

* Cause: Infrastructure.
* Detection: Component Health.
* Blast radius: no new human review is recorded; Candidate-Type Pool review halts; surfacing gates that depend on human review may stall.
* Invariants threatened: none. The Evaluation Harness is outside the critical path for emission ([ARCHITECTURE.md](./ARCHITECTURE.md) §12).
* Degradation posture: absorbable. Emission continues; promotion to Surfaced may be paused for types gated on human review.
* Recovery sketch: restore the Evaluation Harness; process the queue of pending reviews.

**Mode: Reviewer feedback silently lost.**

* Cause: Infrastructure or Logic.
* Detection: cross-check between feedback records and audit logs; Component Health surfaces write-loss anomalies.
* Blast radius: evaluation artifacts are incomplete; Candidate-Type promotion decisions may be biased by incomplete evidence.
* Invariants threatened: none directly. EVALUATION.md owns the substantive response.
* Degradation posture: absorbable. Re-collect where possible.
* Recovery sketch: escalate to EVALUATION.md-owned recovery.

### 13. Query & Retrieval Surface

**Mode: As-of query returns inconsistent historical state.**

* Cause: Logic or Infrastructure (incorrect valid-time handling).
* Detection: temporal-correctness tests ([TESTING_STRATEGY.md](./TESTING_STRATEGY.md)); Component Health surfaces as-of-query anomaly rate; operator audits.
* Blast radius: temporal reasoning is corrupted; user-facing surfaces could mislead.
* Invariants threatened: R indirectly, because temporal integrity is a property of re-derivability.
* Degradation posture: fatal for as-of-query paths; current-state paths may continue.
* Recovery sketch: correct valid-time handling; re-derive affected artifacts; verify temporal monotonicity.

**Mode: Retrieval returns artifacts that should have been filtered by lifecycle state.**

* Cause: Logic.
* Detection: lifecycle-state filtering check at the retrieval boundary.
* Blast radius: downstream consumers act on invalid data.
* Invariants threatened: L in effect, though lifecycle state is still recorded honestly on the underlying artifact.
* Degradation posture: fatal at the boundary; absorbable at the component level.
* Recovery sketch: enforce lifecycle filtering at the retrieval layer; audit consumers that may have acted on non-filtered results.

### 14. API Boundary

**Mode: Validation failure accepts malformed request.**

* Cause: Logic.
* Detection: contract tests ([TESTING_STRATEGY.md](./TESTING_STRATEGY.md)); anomaly in output vs. input for boundary calls.
* Blast radius: downstream components process unintended inputs; at worst, internal state is corrupted.
* Invariants threatened: none directly if downstream components themselves validate; T if a malformed request bypasses the traceability substrate.
* Degradation posture: fatal at the boundary; absorbable downstream if downstream validation catches the effect.
* Recovery sketch: tighten validation; audit for downstream effects.

---

## Cross-Cutting Failure Modes

### Critical-Path External Dependency Drift

**Mode.** Optional or peripheral tooling gradually absorbs a role that quietly becomes critical-path — for example, an external model API used initially for a non-critical purpose begins to be relied on by a component the Fusion Engine depends on. No single change introduces the dependency; the sum of changes does.

**Cause.** Logic, in aggregate.

**Detection.** Periodic audit of the dependency set crossed per pipeline step. The audit is an observability artifact rather than a test; any component in the critical path whose operation requires network access to a third-party model provider is flagged. Surfaced through [OBSERVABILITY.md](./OBSERVABILITY.md) Plane 2 and the Critical-Path Isolation support section.

**Invariants threatened.** C. Fatal.

**Degradation posture.** Fatal on discovery. The system must retain the ability to operate with no external model dependencies in the critical path ([ARCHITECTURE.md](./ARCHITECTURE.md) Model Ownership Posture).

**Recovery sketch.** Remove the dependency from the critical path. If the dependency is genuinely load-bearing, the project must revisit [CONTEXT.md](./CONTEXT.md) §6 explicitly rather than accept the drift.

### Derivation Replay Divergence

**Mode.** Re-derivation of an artifact under its recorded DerivationRun produces a result materially different from the stored artifact.

**Cause.** Logic (non-deterministic derivation) or Infrastructure (inputs changed in a way that should have been prevented by immutability).

**Detection.** Scheduled or ad hoc replay audits; Derivation Traceability surfaces divergence. Exercised in the re-derivability test layer ([TESTING_STRATEGY.md](./TESTING_STRATEGY.md)).

**Invariants threatened.** R. Fatal on discovery.

**Degradation posture.** Fatal. Re-derivability is load-bearing for audit and for correction workflows.

**Recovery sketch.** Identify whether the cause is non-determinism (the DerivationRun itself is at fault) or input mutation (immutability has been violated). Correct the root cause; re-derive; retire downstream Signals as needed.

### Evidence & Provenance Protection

The Evidence & Provenance Store is the substrate of traceability ([ARCHITECTURE.md](./ARCHITECTURE.md) §11). Its protection against partial writes is stated explicitly because multiple component-level modes above depend on it.

* writes to the Evidence & Provenance Store must be atomic with the writes to the derived-artifact stores that reference them. A component emitting a derived artifact that references provenance does so as a single logical transaction at whatever transactionality the downstream storage choice supports
* if the transaction cannot be completed, neither the derived artifact nor the provenance record persists; the component retries or escalates
* periodic integrity audits cross-check the two stores
* any drift between them is fatal on discovery per T above

### Signal Emission Protection From Fusion Engine Failure

The Signal Store is protected from Fusion Engine misbehavior by emission preconditions enforced at the Signal Store boundary:

* no Signal may be stored without a resolvable Basis chain and at least one Evidence reference ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)
* no Signal may be stored without non-empty Commentary
* no Signal may be stored without a valid lifecycle state ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Lifecycle)
* mutation of an emitted Signal is rejected at the boundary; lifecycle transitions must be expressed as new records with Lineage

These preconditions are the contract between the Fusion Engine and the Signal Store. A Fusion Engine failure may cause Signals to be withheld; it may not cause invariant-violating Signals to enter the store.

---

## Graceful Degradation

The system's components can run independently to meaningful degrees. This is not a resilience guarantee; it is a description of how failure compartmentalizes under the architecture.

* **Ingestion and Document Processing** can continue even when Representation, Learned Analysis, or the Fusion Engine are unavailable; Documents accumulate in the Enriched layer pending downstream recovery
* **Heuristic Analysis** is independent of Representation and Learned Analysis; it continues when the learned stack is unavailable
* **Representation and Learned Analysis** are independent of Heuristic Analysis; either can continue when the other is unavailable
* **The Fusion Engine** requires both heuristic and learned candidate evidence to produce its strongest Signals but may emit heuristic-only Signals with appropriate Basis Disagreement posture when Learned Analysis is absent ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)). This is a documented degradation, not an ad hoc fallback
* **Ranking & Surfacing** requires the Signal Store but does not block Signal emission; Ranking failures do not prevent new Signals from being stored
* **Evaluation Harness** is outside the critical path; its failure never halts emission
* **Query & Retrieval Surface** failures affect read access but not write paths

Partial operation is permitted only where no invariant is at stake. Degradations that would violate T, R, I, L, C, or E are fatal regardless of the component that caused them.

---

## Fatal Versus Absorbable: Summary

A compact summary of which modes are fatal and which are absorbable. Fatal modes threaten at least one invariant; absorbable modes do not. The list is illustrative, not exhaustive.

Fatal by construction:

* a Signal emitted without Basis, Evidence, or Commentary
* mutation of an emitted Signal
* partial provenance write
* drift between derived-artifact store and provenance store
* Baseline construction method change without versioning
* critical-path external dependency drift
* as-of query returning inconsistent historical state
* derivation replay divergence
* Document mis-attributed to wrong Entity
* Baseline thinness under-reported at Signal emission

Absorbable with recovery:

* upstream source unavailable
* rule-level heuristic errors (either direction)
* Representation model unavailable
* Fusion Engine unavailable
* Evaluation Harness unavailable
* ranking instability
* Speaker reconciliation ambiguity (provided reconciliation confidence is honestly recorded)
* segmentation errors in Transcript processing (provided affected Documents are flagged)

Absorbable does not mean unimportant; it means that partial operation is safe while the mode is investigated.

---

## Deferred Decisions

Named with the downstream owner:

* specific alert thresholds, severity classifications, and alert routing — downstream operations work
* automated recovery policies and self-healing behavior — downstream infrastructure work
* on-call rotation, escalation ladders, incident-response process — downstream operations work
* chaos-engineering exercises and resilience testing programs — outside v1 scope
* concrete integrity-audit cadences for Evidence & Provenance drift and replay divergence — downstream infrastructure work, bounded by the low-capital constraint
* recovery automation for non-deterministic DerivationRuns — interacts with MODEL_STRATEGY.md and [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
* specific transaction semantics at storage boundaries — downstream infrastructure work

---

## What This Document Is Not

* not an SRE runbook
* not a capacity plan
* not a chaos-engineering test plan
* not a specification of alerting policy
* not a recovery-automation specification
* not an incident-response process document

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) are authoritative; this document enumerates how each of their commitments can fail and what that failure looks like.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new classification terms introduced here (fatal / absorbable, invariant codes T/R/I/L/C/E) are flagged for glossary extension in the closing summary of the cluster.
* [OBSERVABILITY.md](./OBSERVABILITY.md) owns the detection hooks; every mode here has a detection story there.
* [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) owns the testing hooks; every mode here that can be exercised in test has a corresponding layer there.
* EVALUATION.md owns Signal-quality responses to modes whose effect is on Signal content rather than on pipeline state.
