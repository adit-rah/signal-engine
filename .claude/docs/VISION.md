# VISION.md

## Purpose Of This Document

VISION.md extends CONTEXT.md and SCOPE.md with a forward-looking orientation. CONTEXT.md defines why the project exists and how the project thinks. SCOPE.md defines the capability boundary. This document defines where the project is going and what makes it worth building across time.

It is intended for every contributor to the project: engineers, researchers, designers, product thinkers, and any eventual external stakeholders.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative.

---

## The North Star

The project aims to become:

> a durable temporal narrative intelligence engine for financial text, built to surface meaning that emerges through change, explained in a way humans can trust.

This sentence is intentionally narrow.

The project is not chasing generality. It is aiming at a specific, durable problem and intends to remain the best available answer to that problem.

---

## What The System Is

The system is:

* a reader of financial narratives over time
* an explainer of how those narratives have changed
* a structured surface for human analysts to interrogate change
* a system of record for narrative evolution, not a single-query answer engine
* a hybrid of structural reasoning and learned representation, reconciled through the fusion layer (CONTEXT §3.2)

---

## What The System Is Not

The system is not:

* a sentiment analyzer
* a prediction engine or trading system
* a recommendation engine
* a general-purpose financial assistant
* an autonomous agent that acts in markets
* a replacement for human judgment

These non-goals are inherited from CONTEXT §10 and the Non-Goals section of SCOPE.md. They are restated here because drift away from them is the most common failure mode in this product category.

---

## Strategic Edge

The project's edge is not a single model, dataset, or interface. It is the compounded effect of several commitments held simultaneously:

* disciplined temporal and comparative orientation (CONTEXT §2)
* refusal to treat financial text as a stream of isolated documents
* heuristics as structural scaffolding rather than as fallback logic (CONTEXT §7)
* explainability as a required property of every output, not a layer added after the fact (CONTEXT §3.3)
* ownership of the models that power signal extraction (CONTEXT §6)

Each of these, taken alone, is imitable. Taken together, they likely compound into a coherence that is difficult to copy without commitment to the same philosophy.

A competitor that optimizes for generality, speed, or prediction is solving a different problem. The system's defensibility rests on holding its narrow orientation when the surrounding market pulls toward broader, shallower systems.

---

## What Changes For A User When The System Works Well

The user is the decision-maker. The system reduces the cost of noticing.

When the system works well:

* work that previously required tracing a company through many documents becomes a focused review of structured narrative changes
* subtle shifts in framing, confidence, or emphasis surface without requiring the user to notice them manually
* themes that have fallen away — previously emphasized, now absent — become visible rather than invisible
* contradictions across time or sources surface with their supporting excerpts attached
* time spent on detecting change decreases; time spent on judging its significance increases

Detailed user experience design is deferred to USER_EXPERIENCE.md. Nothing in this section prejudges that design.

---

## How The System's Identity Likely Evolves

Evolution is described in terms of character, not roadmap.

### Early Identity

* narrow focus on earnings call transcripts (CONTEXT §8; SCOPE Initial Scope)
* deliberately slow, deliberately careful
* evaluation heavy on human judgment (CONTEXT §14)
* signal taxonomy bounded to the confirmed initial set (CONTEXT §4)
* a small team accepting the burden of in-house model ownership (CONTEXT §13.5)

### Likely Maturation

* additional data domains enter as signal quality stabilizes, following the path already implied by SCOPE's Deferred section
* the signal taxonomy may extend; any extension is expected to flow through the pattern owned by SIGNAL_DEFINITIONS.md
* evaluation likely grows a quantitative layer over time, without displacing human judgment as the authoritative mode during early development
* fusion-layer sophistication likely deepens as understanding of signal interaction matures
* the system's sense of itself likely becomes more opinionated as experience accumulates

No specific version cadence, date, or feature is committed to here. The evolution described is a trajectory, not a schedule.

---

## Qualitative Success

Success is not a number. Success is a set of observable conditions.

The project is succeeding when:

* experienced financial readers consistently report that the system surfaces changes they would have missed, or would have found slowly
* surfaced signals are traceable to source evidence without manual effort
* users can articulate, in their own language, why a signal is meaningful
* the system's failures are legible — explainable even when wrong
* downstream work can rely on CONTEXT.md, SCOPE.md, and this document set as a stable foundation
* the team's understanding of the problem deepens over time rather than narrowing into a fixed product shape

Success is not quarterly revenue, user count, or a single model benchmark. Those may become useful proxies later; they are not the definition.

---

## Failure Modes To Avoid

Success has a shape. Failure has a shape too. The project must remain vigilant against drift in the following directions.

### Drift Toward Sentiment

Every financial text tool is under pressure to collapse into a "positive or negative" score. This collapse is the most common failure of the category. The project rejects it by construction (CONTEXT §3.4, §10).

### Drift Toward Prediction

Surfaced signals describe observed change, not future state. Framing signals as predictions would undermine explainability and invite overconfidence (CONTEXT §13.2).

### Drift Toward Opacity

Any move toward outputs that cannot be traced to source text, rules, or scores violates CONTEXT §3.3. Sophistication that sacrifices interpretability is not an acceptable trade (CONTEXT §6.4).

### Drift Toward External Dependency

Relying on external large-language-model APIs in critical paths violates CONTEXT §6.1 and introduces cost, control, and behavioral-drift risks the project has chosen not to accept.

### Drift Toward Autonomous Action

The system informs humans. It does not trade, recommend, or act (SCOPE Non-Goals).

### Drift Toward Scope Sprawl

Premature expansion into additional data domains, real-time processing, or multi-user workflows risks diluting signal quality on the initial domain. These remain available for future work but are deferred (SCOPE Deferred).

### Drift Toward Noise

Signals that are technically correct but not meaningful erode user trust faster than they build it. Signal quality includes restraint; coverage without quality is a regression.

### Drift Toward Ground-Truth Theater

Evaluation that reports clean numerical accuracy against proxy labels risks dressing up subjective judgment as objective measurement. CONTEXT §13.3 acknowledges the absence of clean ground truth; the project must not paper over it.

---

## Principles Across Time

Principles do not commit to what the system does. They commit to how the project thinks as it does it.

### Meaning Is Temporal

What something says matters less than how what-is-said has changed. This commitment is inherited from CONTEXT §2 and is not negotiable.

### Structure Anchors Learning

Heuristics are not fallback. They are the scaffold that makes learned components interpretable. The machine-learning layer does not displace structural reasoning; it extends it (CONTEXT §7).

### Explainability Is A First-Class Property

An output that cannot be explained is not a product of this system. Explainability applies to every stage of the pipeline, not only to final outputs (CONTEXT §3.3).

### Ownership Over Convenience

The project accepts the cost of training, operating, and maintaining its own models in exchange for control, explainability, and cost sustainability (CONTEXT §6).

### Restraint Beats Coverage

Fewer, higher-quality signals beat many low-quality signals. Restraint is a design commitment, not a limitation. Cognitive-load reduction is a stated evaluation dimension (CONTEXT §14); noisy output is counter-productive to that goal.

### Human Judgment Is The Final Authority

The system augments. The user decides. This holds at the individual-signal level and at the direction-of-the-project level (SCOPE's Human-Centered Analysis principle).

### Epistemic Honesty Over Confidence

The system communicates uncertainty honestly. Overclaiming is worse than underclaiming, because a false confident signal costs more downstream than a hedged one.

---

## Relationship To Other Documents

* CONTEXT.md defines the conceptual foundation and philosophy this document extends.
* SCOPE.md defines what is in and out of scope; this document does not alter those boundaries.
* ASSUMPTIONS.md makes explicit the beliefs about the world this vision depends on.
* DOMAIN_GLOSSARY.md defines the vocabulary used here.
* USER_EXPERIENCE.md remains deliberately deferred; nothing in this document pre-decides experience.
* Other downstream documents (ARCHITECTURE.md, DATA_MODEL.md, SIGNAL_DEFINITIONS.md, MODEL_STRATEGY.md, and their kin) inherit from this vision but are not pre-structured by it.

---

## What This Document Does Not Decide

* architecture, infrastructure, storage, or implementation
* tooling, vendor, framework, or language choices
* specific model architectures (deferred to MODEL_STRATEGY.md)
* signal ranking, scoring, or fusion-layer resolution (deferred to SIGNAL_DEFINITIONS.md and ARCHITECTURE.md)
* user interface or interaction design (deferred to USER_EXPERIENCE.md)
* evaluation harness design (deferred to future evaluation work)
* data acquisition, licensing, or storage choices

These are not open questions this document takes on. They are simply not this document's to decide.
