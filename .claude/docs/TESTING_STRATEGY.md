# TESTING_STRATEGY.md

## Purpose Of This Document

TESTING_STRATEGY.md defines what is tested in the Signal Engine, at what level, and how testing exercises the invariants defined elsewhere. It integrates general software testing concerns with the NLP-specific and temporal testing concerns surfaced by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and [DATA_MODEL.md](./DATA_MODEL.md).

This document is conceptual. It does not select test frameworks, CI/CD tooling, or test-runner infrastructure.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Components and invariants referenced here are specified in [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

---

## How To Read This Document

* testing layers are described by what they cover, not by what frameworks implement them
* the boundary with EVALUATION.md is load-bearing and is drawn in the same terms as in [OBSERVABILITY.md](./OBSERVABILITY.md)
* each system-wide invariant is either tested here, observed in [OBSERVABILITY.md](./OBSERVABILITY.md), or explicitly accepted as unverified with a reason
* deferrals to downstream tooling and developer-workflow work are named with the owner where possible
* new operational terms (canary, shadow, replay, golden-set replay) are flagged for glossary extension in the closing summary of the cluster rather than silently defined inline

---

## Guiding Commitments

Inherited from [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md), and [ASSUMPTIONS.md](./ASSUMPTIONS.md):

* tests exist to exercise pipeline and invariant correctness, not Signal-quality judgment — the latter is owned by EVALUATION.md
* the system is hybrid; tests must exercise heuristic, learned, and fusion contributions together without depending on model internals ([CONTEXT.md](./CONTEXT.md) §3.2)
* re-derivability is a system-wide invariant ([DATA_MODEL.md](./DATA_MODEL.md)) and is exercised by tests, not only observed
* temporal reasoning is mandatory ([CONTEXT.md](./CONTEXT.md) §11); temporal-correctness tests are first-class
* the low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5) applies: test infrastructure must not dominate engineering cost
* tests must not require external LLM APIs, preserving [CONTEXT.md](./CONTEXT.md) §6.1 even in test paths
* tests must preserve the Replaceability commitment in [ARCHITECTURE.md](./ARCHITECTURE.md): assertions that reach into model internals become liabilities the moment a model is replaced

---

## The Testing / Evaluation Boundary

Tests and evaluation answer different questions. The line between them is load-bearing and is drawn here in the same terms as in [OBSERVABILITY.md](./OBSERVABILITY.md).

* **Testing** asks: did the system execute its pipeline as specified? Did each component do its job? Are the invariants preserved under the inputs tested? This is a judgment about the correctness of execution.
* **Evaluation** asks: are the Signals the system emits useful, meaningful, consistent, and non-obvious? Are they surfaced in a way that reduces cognitive load? This is a judgment about the content of what the system produced.

Tests confirm that the system does what it claims to do. Evaluation asks whether what it claims is worth claiming. The two are complementary and must not collapse into each other.

NLP regression is a specific case worth calling out: tests may detect that a model or heuristic change altered output in measurable ways, but they do not determine whether the new output is better. The latter is EVALUATION.md's concern. This document is responsible for surfacing the change; EVALUATION.md is responsible for judging it.

---

## Testing Layers

Testing is organized into layers that reflect the shape of this system, not a generic inherited hierarchy. Each layer names what it covers and what it explicitly does not.

### Unit

**Covers.** Individual functions and classes in isolation: parsers, rule predicates, feature computations, span utilities, identifier reconciliation helpers, validation predicates.

**Does not cover.** Interactions across components. Stochastic or model-dependent behavior beyond seeded determinism.

**Shape.** Fast, deterministic, run on every change. Frequent and cheap.

### Component

**Covers.** A single [ARCHITECTURE.md](./ARCHITECTURE.md) component exercised end-to-end for its own responsibility, with dependencies stubbed or substituted. For example: Document Processing against a set of representative raw transcripts; Baseline Maintenance against a curated history; the Fusion Engine against curated heuristic and learned candidate evidence.

**Does not cover.** End-to-end data flow across components. Production-like volume.

**Shape.** Moderately fast; determinism enforced at the boundary. Each component is testable in isolation per [ARCHITECTURE.md](./ARCHITECTURE.md)'s Replaceability commitment.

### Contract

**Covers.** The contracts between components — the shapes of what each component emits and what its downstream components accept. The Fusion Engine's upstream contract with Heuristic Analysis and Learned Analysis, and its downstream contract with the Signal Store, are load-bearing for extensibility ([ARCHITECTURE.md](./ARCHITECTURE.md) §8) and are contract-tested in both directions.

**Does not cover.** The semantic correctness of the artifacts exchanged; only the shape and invariants required at the boundary.

**Shape.** A small set of high-value tests per contract. Added to whenever a contract changes.

### Integration (Narrow)

**Covers.** A focused slice of the pipeline — typically a single Document traveling from Ingestion through Signal emission — with real implementations of the involved components and real representative inputs. Integration tests confirm that components compose correctly on a curated example, not that the system handles all inputs.

**Does not cover.** Full production-like traffic or input diversity. Signal-quality judgment.

**Shape.** Slower than component tests; a small, curated corpus. The corpus is part of the system's test assets and is maintained deliberately.

### Temporal Correctness

**Covers.** The system's temporal reasoning — as-of queries, valid-time intervals, emission-time semantics, processing-time monotonicity. The temporal model in [DATA_MODEL.md](./DATA_MODEL.md) is itself a contract, and its invariants are testable.

Representative cases:

* reconstructing NarrativeState as of a past effective time returns exactly the state available then, not the state known now
* a Baseline's valid-time interval is monotone under new observations
* an as-of query over emitted Signals returns the Signals that were in the Surfaced state at that effective time, ignoring later Supersession
* no derived artifact's processing time is earlier than its inputs' observation times

**Does not cover.** Performance of temporal queries.

**Shape.** A dedicated test surface; some cases reuse the curated corpus from integration tests, others are synthetic.

### Re-Derivability

**Covers.** The [DATA_MODEL.md](./DATA_MODEL.md) invariant that derived artifacts can be re-derived from Raw plus DerivationRuns. Representative cases:

* re-deriving a Normalized Document from Raw under its Document Processing DerivationRun produces an artifact structurally equivalent to the stored one
* re-deriving a Baseline from Enriched Documents under a specified DerivationRun is deterministic
* re-deriving a Signal from Analytical inputs under its Fusion Engine DerivationRun produces the same Signal, with the same Basis and Evidence references

Non-determinism in any DerivationRun is itself a test failure per the re-derivability invariant. Where non-determinism cannot be eliminated — for example, certain learned steps — a tolerance specification must be documented, and the test passes only within that tolerance. The tolerance itself is a design artifact owned by MODEL_STRATEGY.md; this layer's job is to enforce it.

**Does not cover.** Whether the re-derived artifact is better than the original — only whether it is equivalent.

**Shape.** Moderately slow; run on a schedule rather than on every change, with results surfaced through [OBSERVABILITY.md](./OBSERVABILITY.md)'s Derivation Traceability plane.

### Signal Lifecycle (State-Machine)

**Covers.** The state machine defined in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md): Candidate, Surfaced, Stale, Superseded, Retired. Every transition is tested as a transformation that produces a new Signal record with Lineage, not a mutation.

Representative cases:

* a Signal moves from Candidate to Surfaced as a new record whose Lineage references the Candidate; the Candidate record is unchanged
* Retirement produces a new Retired record; the original Signal is not deleted
* the Signal Store rejects direct mutation attempts on any existing Signal record
* a Signal whose Basis cannot be resolved, whose Evidence is empty, or whose Commentary is absent is rejected at emission; no such Signal enters any lifecycle state

**Does not cover.** Transition policy — when and why a Signal should transition. Transition policy is deferred to NARRATIVE_ANALYSIS.md and EVALUATION.md. This layer tests that the machine is structurally sound, not that transitions are made for the right substantive reasons.

**Shape.** Focused, contract-like tests at the Signal Store boundary.

### NLP Regression

**Covers.** Changes in system output that result from changes in a model, a heuristic, a preprocessing step, or a configuration. The goal is to detect that the output changed and to characterize the change, without depending on model internals.

Two approaches, operating together:

* **Behavioral tests.** A curated set of inputs with known structural properties (a transcript with a known Omission pattern, a transcript with known hedging density, a transcript with known Speaker turnover). The test asserts that the system's output has the expected structural properties — a Signal of the expected type is emitted, with Basis and Evidence of the expected shape — without asserting specific Strength or Confidence values that may legitimately change across model versions.
* **Golden-set replay.** A frozen set of prior Documents and their prior Signal outputs. After a change, the system is replayed on the set, and the difference between the new and prior outputs is surfaced as a diff: new Signals emitted, prior Signals absent, changes in Basis or Evidence references, changes in Type, changes in lifecycle behavior. The diff is a test artifact; the judgment of whether the diff is good or bad is EVALUATION.md's concern.

Behavioral tests enforce invariants; golden-set replay surfaces change. Neither judges quality. Both are deliberate: they exercise the heuristic / learned / fusion boundary without reaching into model internals.

**Does not cover.** Whether the new output is better than the prior — that is EVALUATION.md.

**Shape.** Behavioral tests are small and fast; golden-set replay is heavier and is scheduled rather than run on every change.

### Production Testing

**Covers.** Tests executed against or alongside the live system. Three modes are considered in scope:

* **Canary emission.** A new DerivationRun is installed for a bounded subset of new Documents — a narrow canary — before being used on the full flow. Canary Signals are observable through the standard [OBSERVABILITY.md](./OBSERVABILITY.md) surfaces and reviewable through the Evaluation Harness. Canary failures are absorbable per [FAILURE_MODES.md](./FAILURE_MODES.md) because they are bounded by the canary's scope.
* **Shadow runs.** A new DerivationRun runs in parallel with the current one; its outputs are stored for comparison but are not emitted to the Signal Store. Shadow runs let the system compare new-versus-prior behavior across the pipeline without exposing users to the candidate run.
* **Replay.** An older Document set is re-processed under the current DerivationRuns to confirm that the system's behavior on known history matches prior expectation; divergence is surfaced through Derivation Traceability.

Production testing is not a substitute for offline testing layers. It is where the system confirms that offline equivalence holds under production-adjacent conditions. The low-capital posture applies: production testing is scoped to bounded samples rather than full-volume parallel execution.

**Does not cover.** Signal-quality judgment about the canary's or shadow run's output. The Evaluation Harness and EVALUATION.md own that judgment.

---

## Testing Across The Hybrid Boundary

The system is hybrid — heuristic, learned, fusion — and tests must exercise the boundary between the three without depending on model internals. The discipline:

* heuristic components are tested with deterministic unit and component tests; rule predicates are independently testable
* learned components are tested through behavioral and contract tests: the shape of their outputs, the invariants they satisfy, and the contract they present to the Fusion Engine. Tests do not assert model weights, learned representations' dimensions, or internal activations
* the Fusion Engine is tested with curated heuristic and learned candidate evidence as inputs. Conflict-resolution behavior is tested against cases where heuristic and learned contributions agree, disagree, and partially disagree. Confidence outputs are tested for structural properties (bounded, lower under Basis Disagreement, lower under thin Baseline) rather than for specific values
* Basis content — which contributions produced which Signal — is tested as a first-class property of Fusion Engine output

Tests do not reach into a model's internals for assertions. A test that does so becomes a liability the moment the model is replaced. This discipline preserves [ARCHITECTURE.md](./ARCHITECTURE.md)'s Replaceability commitment at the cost of testing.

---

## Testing By Invariant

Each system-wide invariant is either tested here, observed in [OBSERVABILITY.md](./OBSERVABILITY.md), or explicitly accepted as unverified with a reason. The list below is the load-bearing check against this document's acceptance criteria.

* **Traceability of every Signal ([CONTEXT.md](./CONTEXT.md) §3.3).** Tested at the Signal Store boundary in the Signal Lifecycle layer; exercised in contract and integration tests. Observed in [OBSERVABILITY.md](./OBSERVABILITY.md) Plane 3 (Derivation Traceability).
* **Re-derivability ([DATA_MODEL.md](./DATA_MODEL.md)).** Tested in the Re-Derivability layer. Observed in [OBSERVABILITY.md](./OBSERVABILITY.md) under the Re-Derivability support section.
* **Immutability of Raw, Signal, and DerivationRun-bound artifacts ([DATA_MODEL.md](./DATA_MODEL.md)).** Tested at the Signal Store and Evidence & Provenance Store boundaries; mutation attempts must be rejected. Observed through Component Health anomalies in [OBSERVABILITY.md](./OBSERVABILITY.md).
* **Signal lifecycle as new records with Lineage ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)).** Tested in the Signal Lifecycle layer.
* **No external LLM API in critical paths ([CONTEXT.md](./CONTEXT.md) §6.1).** Not exercised as an input-output test. Enforced structurally at the component level and observed through the Critical-Path External Dependency Drift audit named in [OBSERVABILITY.md](./OBSERVABILITY.md) and [FAILURE_MODES.md](./FAILURE_MODES.md). A test that exhaustively asserts the absence of network calls is infeasible under the low-capital constraint; this invariant is accepted as structurally-enforced rather than test-enforced.
* **Non-empty Basis, Evidence, and Commentary on every Signal ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)).** Tested at the Signal Store emission boundary in the Signal Lifecycle layer and at contract tests for the Fusion Engine's downstream output.
* **Evidence chain resolvability ([DATA_MODEL.md](./DATA_MODEL.md)).** Tested at the Evidence & Provenance Store contract boundary; exercised in integration tests by following the chain end-to-end on a curated Document.
* **Temporal integrity ([DATA_MODEL.md](./DATA_MODEL.md)).** Tested in the Temporal Correctness layer.
* **Reconciliation confidence is recorded, not silently asserted ([DATA_MODEL.md](./DATA_MODEL.md) Identity Model).** Tested as a component-level property of Entity Resolution.
* **Baseline thinness is exposed as a queryable property ([ARCHITECTURE.md](./ARCHITECTURE.md) §4).** Tested at the Baseline Maintenance contract boundary.
* **Thin-History Policy applied at Signal emission ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)).** Tested at the Fusion Engine's contract boundary as a structural property of emitted Confidence — Confidence is lower under thin Baseline — without asserting specific Confidence values.

Invariants not exercised at this layer are flagged above; they are either observed operationally or structurally enforced by the architecture.

---

## Testing Versus Signal-Quality Evaluation: A Restatement

The distinction above is restated here because it determines what is in scope for this document.

Tests may detect that an output changed, that an invariant was violated, that a contract was broken, or that a behavioral property no longer holds. Tests do not determine whether the new behavior is better, whether a Signal is meaningful, or whether a user would find a ranking helpful. Those are EVALUATION.md questions.

A consequence for NLP regression: a test reporting "the system now emits a different set of Signals than before" is a passing or failing test about change. A test reporting "the new set of Signals is worse than the prior set" is a category error — it has smuggled in a quality judgment. The test layer surfaces the diff; EVALUATION.md judges it.

---

## Cost Posture

Test infrastructure is subject to the same low-capital constraint as the rest of the system. Consequences:

* curated corpora rather than full-volume replay for most layers; full-volume tests are scheduled rather than continuous
* golden-set replay is cheaper than full re-derivation and is preferred where it produces equivalent signal about change
* production testing is bounded-sample rather than full-shadow
* tests that require training infrastructure are bounded by the same hardware constraints as training itself ([ASSUMPTIONS.md](./ASSUMPTIONS.md) H5)
* test retention of artifacts is bounded; test-generated DerivationRuns are distinguishable from production runs and are cleaned up on a schedule

---

## Deferred Decisions

Named with the downstream owner:

* specific test framework selections — downstream developer-workflow work
* CI/CD pipeline and test execution orchestration — downstream infrastructure work
* test-data governance (how curated corpora are maintained, refreshed, and audited) — interacts with DATA_GOVERNANCE.md
* golden-set construction criteria — downstream developer-workflow work, informed by EVALUATION.md
* tolerance specifications for non-deterministic learned components — MODEL_STRATEGY.md
* coverage targets and test-quality metrics — downstream developer-workflow work
* production-testing policy (canary scope, shadow-run cadence, replay schedule) — downstream operations work under the low-capital constraint
* review mechanics for diffs surfaced by golden-set replay — EVALUATION.md

---

## What This Document Is Not

* not an Evaluation methodology document
* not a specific test-framework selection
* not a test catalog
* not a CI/CD specification
* not a coverage-target policy
* not a performance or load-testing specification

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) are authoritative; this document exercises the invariants they define.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary.
* [OBSERVABILITY.md](./OBSERVABILITY.md) draws the observability / evaluation boundary in the same terms used here.
* [FAILURE_MODES.md](./FAILURE_MODES.md) names the failure modes whose testable aspects are covered in the layers above.
* EVALUATION.md owns Signal-quality evaluation, which is explicitly out of scope here.
* MODEL_STRATEGY.md owns model-internal concerns including the non-determinism tolerances the re-derivability layer enforces.
* NARRATIVE_ANALYSIS.md owns Signal transition policy, which this document's Signal Lifecycle layer does not cover.
