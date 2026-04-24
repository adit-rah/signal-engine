# CONTRIBUTING.md

## Purpose Of This Document

CONTRIBUTING.md defines how contributors propose, review, and integrate changes. It is intended to be usable by a new contributor on day one.

This document does not reinvent extension patterns that live elsewhere. For new Signal types, see [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension. For new Document types, see [DATA_MODEL.md](./DATA_MODEL.md) Extensibility. Both patterns are referenced below, not duplicated.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Code-level conventions are in [CODE_STANDARDS.md](./CODE_STANDARDS.md).

---

## How Changes Are Proposed

Changes fall into two bands.

### Narrow Changes

Bug fixes, small corrections, narrow improvements, and documentation updates need no prior proposal. They move directly through review. Reviewers check against [CODE_STANDARDS.md](./CODE_STANDARDS.md) and the expectations below.

### Structural Changes

Changes that touch component boundaries, the Fusion Engine's contract, the data model, the Signal taxonomy, or [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) require a short proposal before implementation.

A proposal is a paragraph, not a form. It names:

* what the change is
* which document section it honors, extends, or modifies
* which traceability, Basis, or Evidence invariants it interacts with
* which assumption identifiers ([ASSUMPTIONS.md](./ASSUMPTIONS.md), e.g. `H5`, `E1`) it depends on

Proposals are discussed before code is written. The resolution is recorded in [DECISION_LOG.md](./DECISION_LOG.md).

---

## Review Expectations

Reviewers hold the following, in approximately this order. The list is a posture, not a checklist generator.

* **Respects component boundaries.** Does the change stay within the component it belongs to per [ARCHITECTURE.md](./ARCHITECTURE.md)? Cross-component reach is either justified explicitly or refactored.
* **Preserves traceability.** Is Basis populated on any emitted Signal? Is Evidence tied to Spans? Are DerivationRun references carried through derived artifacts ([CONTEXT.md](./CONTEXT.md) §3.3; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)?
* **Uses glossary vocabulary.** Names, commit messages, and surfaced strings use [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) terms rather than invented near-synonyms or rejected vocabulary.
* **Honors immutability.** No silent mutation of Signals, Baselines, or lower derivation-layer artifacts ([DATA_MODEL.md](./DATA_MODEL.md) Immutability And History).
* **Honors the model posture.** No external large-language-model API call on a critical path ([CONTEXT.md](./CONTEXT.md) §6.1).
* **Justifies new dependencies.** Every new dependency is a commitment; its presence should survive a "why not owned code" question ([CODE_STANDARDS.md](./CODE_STANDARDS.md) Dependencies).
* **Captures decisions.** Non-trivial design decisions are recorded in [DECISION_LOG.md](./DECISION_LOG.md) before the change lands.

The reviewer's job is not to generate a checklist; it is to hold the above invariants without letting a technically correct change violate them.

---

## Adding A New Signal Type

The extension pattern is owned by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension and is not reinvented here. Two paths exist; both resolve through the same human-review gate, and neither is privileged over the other ([CONTEXT.md](./CONTEXT.md) §4).

### Research-Driven Extension

A contributor proposes a new Signal type from analytical or research work. The proposal includes the four sections required of every Signal type: operational definition, required evidence pattern, strong-vs-weak criteria, common false-positive patterns.

Once accepted, the type is added to [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). The Fusion Engine begins emitting the type through its existing contract; no new contract is introduced.

### Discovery-Driven Extension

Per [CONTEXT.md](./CONTEXT.md) §5.4, the Learned Analysis component may propose candidate Signal *types* — not only new instances of existing types. Candidate types enter the Candidate-Type Pool ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)). Representative candidate instances are held there for human review through the Evaluation Harness ([ARCHITECTURE.md](./ARCHITECTURE.md)).

A proposed type is promoted only after human review confirms that it is meaningful, distinct from existing types, and not a rediscovery of an existing type under a new name.

Contributors bringing a type through either path commit to documenting it in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) once promoted.

---

## Adding A New Document Type

The extension pattern is owned by [DATA_MODEL.md](./DATA_MODEL.md) Extensibility and is not reinvented here.

* new subtypes attach to the base Document without altering its identity or temporal model
* Span precision for the new subtype is specified when the subtype is added ([DATA_MODEL.md](./DATA_MODEL.md) Span)
* Document Processing ([ARCHITECTURE.md](./ARCHITECTURE.md)) gains a parser and a normalization path; downstream components (Entity Resolution, Heuristic Analysis, Representation, Learned Analysis, Fusion Engine) are not altered
* Evidence-to-Span precision is preserved across the new type; a subtype whose Spans cannot be re-resolved unambiguously is not accepted

A new Source may accompany a new Document type. Source identity reconciliation follows [DATA_MODEL.md](./DATA_MODEL.md) Source.

---

## Recording Decisions

Non-trivial design decisions are recorded in [DECISION_LOG.md](./DECISION_LOG.md). The log remains skeletal at this stage; contributors extend it as decisions accumulate.

A decision entry names:

* the question
* the alternatives considered
* the resolution
* the documents affected

Vocabulary decisions enter [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) rather than the decision log. Decisions that change an [ARCHITECTURE.md](./ARCHITECTURE.md) commitment are logged and then reflected in the architecture document. Decisions that extend the Signal taxonomy are logged and then reflected in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

---

## Recording Research

Experimental results, investigative reading, and exploratory analysis are recorded in [RESEARCH_NOTES.md](./RESEARCH_NOTES.md).

Research notes are not review gates. They record what was learned so that future contributors do not re-walk the same ground. A research note becomes a decision only when it is promoted to [DECISION_LOG.md](./DECISION_LOG.md) through the structural-change path above.

---

## Out Of Scope

The following are explicitly not acceptable contributions, regardless of their technical quality. They violate commitments elsewhere in the document set.

* adding external large-language-model API calls to critical paths ([CONTEXT.md](./CONTEXT.md) §6.1; [ARCHITECTURE.md](./ARCHITECTURE.md) Model Ownership Posture). Non-critical research tooling is separately scoped
* changes that violate the in-house model posture ([CONTEXT.md](./CONTEXT.md) §6)
* bypassing the Basis or Evidence requirement on any Signal ([CONTEXT.md](./CONTEXT.md) §3.3; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy)
* silent mutation of immutable artifacts ([DATA_MODEL.md](./DATA_MODEL.md) Immutability And History)
* black-box components on the critical path ([CONTEXT.md](./CONTEXT.md) §6.4; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions)
* re-framing a Signal as a prediction, recommendation, or trading instruction ([CONTEXT.md](./CONTEXT.md) §10; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions)
* collapsing Signal types into a single catch-all rather than routing cross-type interaction through the Fusion Engine

A change that falls here is not resolved by revision; it is the wrong change.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the component boundaries this document's review expectations honor.
* [DATA_MODEL.md](./DATA_MODEL.md) owns the Document-type extension pattern referenced above.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) owns the Signal-type extension pattern and the Candidate-Type Pool.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) is the vocabulary source.
* [CODE_STANDARDS.md](./CODE_STANDARDS.md) companions this document; it governs how code is written rather than how changes move.
* [DECISION_LOG.md](./DECISION_LOG.md) is where resolved proposals are recorded; it remains skeletal at this stage.
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) is where research notes accumulate.
