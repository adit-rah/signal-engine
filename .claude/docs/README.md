# Signal Engine

A financial narrative intelligence system that detects meaningful changes in meaning, confidence, framing, and consistency across time in financial text, using heuristic structure and learned representations combined through a fusion layer.

Not a sentiment analyzer. Not a trading prediction system. Not a black-box oracle.

This document is the index. The authoritative framing lives in [CONTEXT.md](./CONTEXT.md).

---

## State Of The Project

The architectural and design documentation is complete and internally coherent. Implementation has not yet begun.

The v1 scope is committed to earnings call transcripts; see [SCOPE.md](./SCOPE.md). The model-ownership posture is in-house, small, specialized; see [CONTEXT.md §6](./CONTEXT.md).

Every load-bearing decision made so far is recorded in [DECISION_LOG.md](./DECISION_LOG.md).

---

## The Document Set

Thirty documents, grouped by purpose.

### Ground Truth

These define the project's identity and are the input to every other document.

* [CONTEXT.md](./CONTEXT.md) — conceptual foundation, system philosophy, architectural intent. Authoritative.
* [SCOPE.md](./SCOPE.md) — what v1 is and is not in scope to do.
* [VISION.md](./VISION.md) — forward-looking north star.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) — explicit baseline beliefs about users, data, signals, team, and scope.

### Canonical References

Living artifacts that every other document cites.

* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) — authoritative vocabulary. ~150 terms across 11 sections.
* [DECISION_LOG.md](./DECISION_LOG.md) — durable record of project-level decisions.
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) — open analytical questions and experiment register.

### Structural Spine

The system's shape.

* [ARCHITECTURE.md](./ARCHITECTURE.md) — 14 conceptual components, data flow, cross-cutting concerns.
* [DATA_MODEL.md](./DATA_MODEL.md) — 15 core entities, 3-kind identity, 7-kind temporal model, 5-layer derivation.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) — Signal anatomy, five canonical types, extension paths, lifecycle.

### Data Pipeline

End-to-end data lifecycle.

* [DATA_ACQUISITION.md](./DATA_ACQUISITION.md) — where documents come from, under what licensing posture.
* [INGESTION_SPEC.md](./INGESTION_SPEC.md) — once a document arrives, how it is landed.
* [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md) — Raw to Normalized transformations.
* [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) — orchestration, Pipeline Version, re-derivation.
* [SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md) — internal query surface and as-of semantics.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) — provenance, retention, tombstoning, source quality.

### Intelligence Core

The analytical engine.

* [MODEL_STRATEGY.md](./MODEL_STRATEGY.md) — model families, Fusion Engine mechanics, Strength and Confidence computation.
* [NARRATIVE_ANALYSIS.md](./NARRATIVE_ANALYSIS.md) — Baseline construction, thresholds, lifecycle transitions, ranking, Theme curation.
* [EVALUATION.md](./EVALUATION.md) — human review, Candidate-Type Pool promotion, Review Rubric.
* [EXPERIMENTATION.md](./EXPERIMENTATION.md) — experiment specification, Historical Replay, Graduation Review.

### Platform And Reliability

How we know the system is working.

* [OBSERVABILITY.md](./OBSERVABILITY.md) — Document Journey, Component Health, Derivation Traceability.
* [FAILURE_MODES.md](./FAILURE_MODES.md) — per-component failure modes with detection and recovery.
* [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) — nine testing layers including temporal correctness and NLP regression.

### Product Surface

How humans and clients consume the system.

* [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) — Entity Narrative Timeline, progressive disclosure, Evidence presentation.
* [API_SPEC.md](./API_SPEC.md) — protocol-agnostic contract, three projection depths, as-of queries.

### Trust And Safety

Product-integrity concerns framed as engineering, not legal cover.

* [SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md) — threat model, secrets posture, source-terms enforcement.
* [ETHICS_AND_LIMITATIONS.md](./ETHICS_AND_LIMITATIONS.md) — epistemic honesty, Hallucination Surface, Drift Watch.

### Strategy And Planning

Where the project sits and where it is going.

* [COMPETITIVE_LANDSCAPE.md](./COMPETITIVE_LANDSCAPE.md) — category-level distinctness from existing tooling.
* [ROADMAP.md](./ROADMAP.md) — five phases with qualitative entry and exit criteria.

### Developer Workflow

How changes are made.

* [CODE_STANDARDS.md](./CODE_STANDARDS.md) — posture, not prescription. Language-agnostic.
* [CONTRIBUTING.md](./CONTRIBUTING.md) — how to propose changes, add Signal types, record decisions.

---

## Reading Paths

### If you are joining the engineering team

1. [VISION.md](./VISION.md) — 10 minutes
2. [CONTEXT.md](./CONTEXT.md) — 20 minutes
3. [ARCHITECTURE.md](./ARCHITECTURE.md) — 20 minutes
4. The cluster documents most relevant to your area
5. [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) — as a reference throughout

### If you are reviewing the project at a strategic level

1. [VISION.md](./VISION.md) and [SCOPE.md](./SCOPE.md)
2. [CONTEXT.md](./CONTEXT.md)
3. [DECISION_LOG.md](./DECISION_LOG.md) — twelve decisions with full reasoning
4. [COMPETITIVE_LANDSCAPE.md](./COMPETITIVE_LANDSCAPE.md) and [ROADMAP.md](./ROADMAP.md)

### If you are a researcher or ML contributor

1. [CONTEXT.md](./CONTEXT.md) and [VISION.md](./VISION.md)
2. [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
3. [MODEL_STRATEGY.md](./MODEL_STRATEGY.md)
4. [EVALUATION.md](./EVALUATION.md) and [EXPERIMENTATION.md](./EXPERIMENTATION.md)
5. [RESEARCH_NOTES.md](./RESEARCH_NOTES.md)

### If you are designing the product surface

1. [VISION.md](./VISION.md)
2. [USER_EXPERIENCE.md](./USER_EXPERIENCE.md)
3. [API_SPEC.md](./API_SPEC.md)
4. [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) — the anatomy you are surfacing
5. [ETHICS_AND_LIMITATIONS.md](./ETHICS_AND_LIMITATIONS.md) — what the surface must never claim

### If you are working on data

1. [DATA_MODEL.md](./DATA_MODEL.md)
2. [DATA_ACQUISITION.md](./DATA_ACQUISITION.md) through [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)
3. [ARCHITECTURE.md](./ARCHITECTURE.md) — component boundaries for the data cluster

### If you want to contribute a change

1. [CONTRIBUTING.md](./CONTRIBUTING.md)
2. [CODE_STANDARDS.md](./CODE_STANDARDS.md)
3. [DECISION_LOG.md](./DECISION_LOG.md) — for the entry format if your change records a decision

---

## Document Conventions

All documents in this repository share a common voice and discipline.

* Hedged language. "Likely", "may", "should" rather than absolute claims. Financial systems are noisy; the tone reflects this.
* Short paragraphs, often a single sentence. Bulleted lists over dense prose.
* Horizontal rules between major sections.
* No emojis anywhere. No marketing language.
* No first-person voice. The system, the project, this document.
* Authoritative vocabulary lives in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Terms are cited, not redefined.
* Where two documents disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Where a downstream document and its owned scope disagree, the owner's commitment wins.

---

## Authority Chain

A single upstream reference hierarchy governs the document set.

```
CONTEXT.md
    ├── SCOPE.md  (what, bounded by CONTEXT's why)
    ├── VISION.md  (where, extending CONTEXT's why)
    ├── ASSUMPTIONS.md  (beliefs implied by CONTEXT + SCOPE)
    └── DOMAIN_GLOSSARY.md  (vocabulary used everywhere)
        │
        ├── ARCHITECTURE.md, DATA_MODEL.md, SIGNAL_DEFINITIONS.md
        │   (structural spine)
        │
        └── All Wave 2 documents
            (cluster-specific elaboration)

DECISION_LOG.md runs alongside — decisions update upstream documents
and are recorded here for traceability.

RESEARCH_NOTES.md runs alongside — open questions across the set.
```

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [CODE_STANDARDS.md](./CODE_STANDARDS.md).

Before proposing a change that would touch [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), or the structural spine, draft a [DECISION_LOG.md](./DECISION_LOG.md) entry describing the question and alternatives.

---

## Relationship To Other Documents

This document is an index. It is the only document in the set whose job is to help a reader navigate the others. Every authoritative claim lives in one of the documents it links to.
