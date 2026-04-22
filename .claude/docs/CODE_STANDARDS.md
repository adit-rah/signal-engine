# CODE_STANDARDS.md

## Purpose Of This Document

CODE_STANDARDS.md defines the posture and conventions the project expects of code. It is conceptual: it does not commit to a specific language, framework, linter, or formatter. Those commitments belong to downstream tooling work.

The standards below exist to preserve, at the code level, the invariants committed in [CONTEXT.md](./CONTEXT.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) — chiefly explainability, traceability, replaceability, and in-house model ownership.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## Posture

The project's posture on code:

* readability over cleverness — code is read far more than it is written
* simplicity over premature abstraction — three similar lines are preferable to a generalization introduced before the second concrete use case
* testability follows from bounded responsibilities — components with clean contracts are testable by construction; code without testable surfaces is a design problem, not a test-writing problem
* documentation density is measured in clarity, not volume — dense commentary around opaque code is a smell, not a virtue
* explainability at the code level is continuous with explainability at the system level ([CONTEXT.md](./CONTEXT.md) §3.3); both are first-class

Each of these is a posture, not a metric. Reviewers apply judgment.

---

## Vocabulary

[DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) is canonical. The same vocabulary governs code names, commit messages, and inline documentation.

* code names use glossary terms directly rather than invented near-synonyms. A variable named `sentiment_score` is wrong if what it holds is a Confidence Shift feature
* rejected vocabulary (the glossary's Deliberate Non-Definitions) does not appear in code: no "sentiment", "prediction", "alpha", "recommendation", "AI" as a noun, "black-box"
* new vocabulary enters through [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md), not through the code. A name with no home in the glossary is either an invention that belongs there or a leak that should be renamed
* abbreviations are avoided where glossary terms have canonical forms
* commit-message subject lines use glossary terms; bodies explain *why* when the diff does not; references to document sections (e.g. `SIGNAL_DEFINITIONS.md Thin-History Policy`) are welcome when a constraint is being honored

---

## Traceability In Code

Traceability is a system-wide invariant ([CONTEXT.md](./CONTEXT.md) §3.3; [ARCHITECTURE.md](./ARCHITECTURE.md) Cross-Cutting Concerns). Code preserves it by default; it is not an afterthought applied at the boundary.

* every function that produces a derived artifact takes or produces the DerivationRun that scopes it
* every Signal is emitted with its Basis populated; code paths that cannot populate Basis do not emit Signals ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)
* every Evidence-producing function carries Span references through its return value or its side effects; returning a Strength or Confidence number without its supporting Span is a defect
* intermediate features may be internal, but their provenance is part of the function's contract, not an optional decoration

A code path that discards Basis, Evidence, or DerivationRun references is treated as a design bug, not a style preference.

---

## Component Boundaries And Replaceability

[ARCHITECTURE.md](./ARCHITECTURE.md) commits to replaceability as a cross-cutting concern: each component has a single responsibility and bounded upstream and downstream contracts. Code layout reflects that.

* module structure mirrors component responsibility — Ingestion, Document Processing, Entity Resolution, Baseline Maintenance, Heuristic Analysis, Representation, Learned Analysis, Fusion Engine, Signal Store, Ranking & Surfacing, Evidence & Provenance Store, Evaluation Harness, Query & Retrieval Surface, API Boundary
* code belonging to one component does not reach into the internals of another; interaction occurs through the contract named in [ARCHITECTURE.md](./ARCHITECTURE.md)
* the Fusion Engine's upstream and downstream contracts are load-bearing for extensibility; changes to them are cautious and reviewed
* shared code is kept narrow; shared code that leaks one component's internals into another defeats the replaceability commitment

A module whose responsibility cannot be named in one sentence is suspect.

---

## Immutability

[DATA_MODEL.md](./DATA_MODEL.md) commits the following immutability invariants. Code honors them.

* Raw artifacts are not edited in place
* Normalized, Enriched, Analytical, and Signal-layer artifacts are immutable given their DerivationRun; re-derivation produces new records with a new DerivationRun, not mutated records
* Signals are immutable once emitted; lifecycle transitions (Stale, Superseded, Retired) are expressed as new Signal records with Lineage references
* Baselines are immutable per valid-time interval; updates produce new valid-time intervals
* Commentary is bound to its Signal and immutable

Functions that receive these artifacts do not mutate them. Constructs that encourage mutation — in-place setters on what the data model treats as immutable, for example — are not introduced.

---

## Dependencies

The project's model-ownership posture ([CONTEXT.md](./CONTEXT.md) §6; [ASSUMPTIONS.md](./ASSUMPTIONS.md) H6) and low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5) shape dependency choice.

* no external large-language-model API appears in a critical path ([CONTEXT.md](./CONTEXT.md) §6.1; [ARCHITECTURE.md](./ARCHITECTURE.md) Model Ownership Posture). Optional local small-footprint language models are permitted; they run in-process or on owned infrastructure, not remotely
* dependencies that require expensive infrastructure to run are out of scope
* narrow, single-purpose libraries are preferred over large frameworks; a library whose purpose can be stated in one sentence is easier to reason about and easier to replace
* every new dependency is a commitment. Its presence should survive a review that asks: what concrete problem is it solving that a small amount of owned code could not?
* non-critical-path uses of external services (for example, offline research tooling) are permitted but are clearly out of the critical path; they are not invoked from code that ingests, derives, or emits in the production flow

---

## Inline Documentation Scope

Code documentation answers *why*, not *what*. The code itself states what.

* hidden constraints, non-obvious invariants, and workarounds for specific problems belong in code, next to the lines they concern
* design discussion, architectural rationale, and taxonomy motivation belong in `docs/`, not in source files
* comments that narrate the implementation line by line are noise
* docstrings describe contracts and preserved invariants, not implementation mechanics
* a comment that would go stale the next time the surrounding code changes is a sign the comment is describing implementation rather than intent

---

## Explicitly Avoided Practices

The following are not matters of taste. They violate commitments elsewhere in the document set.

* **over-abstraction** — premature generalization before a second concrete use case exists; reaching for configurability at the cost of legibility
* **premature optimization** — micro-optimizations without measured evidence of need, especially where they reduce readability
* **silent mutation of immutable artifacts** — in-place edits of Signals, Baselines, or lower derivation-layer artifacts ([DATA_MODEL.md](./DATA_MODEL.md) Immutability And History)
* **black-box model wrappers** — model invocations whose inputs, outputs, and intermediate scores cannot be traced. Excluded by construction ([CONTEXT.md](./CONTEXT.md) §3.3, §6.4; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions)
* **swallowed failures** — caught exceptions without explicit signalling, null-returning on error, suppression of traceback information in logs
* **opaque numeric returns** — returning a Strength or Confidence number without the Basis or Evidence reference that supports it
* **critical-path calls to external large-language-model providers** — violates [CONTEXT.md](./CONTEXT.md) §6.1 and [ARCHITECTURE.md](./ARCHITECTURE.md) Model Ownership Posture
* **taxonomy collapse** — merging distinct Signal types (Narrative Drift, Confidence Shift, Omission Event, Contradiction Event, Structural Anomaly) into a single catch-all at the code level. Cross-type interactions are modeled at the Fusion Engine, not collapsed at the type boundary

---

## Deferred Decisions

The following are deliberately not decided here.

* language selection — deferred; this document remains language-agnostic until that decision is made
* linter, formatter, and static-analysis configuration — deferred to downstream tooling work
* testing strategy — deferred to [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
* continuous-integration posture — deferred to downstream tooling work
* deployment and packaging conventions — deferred to downstream infrastructure work

This document is extended when those decisions are made; it is not rewritten.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the component boundaries the Component Boundaries section honors.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the immutability invariants the Immutability section enforces.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the Signal anatomy the Traceability section honors.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) is the vocabulary source.
* [CONTRIBUTING.md](./CONTRIBUTING.md) companions this document; it governs how changes move through review rather than how code itself is written.
