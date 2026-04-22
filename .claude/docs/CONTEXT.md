# CONTEXT.md

## Purpose Of This Document

This document defines the conceptual foundation, system philosophy, and architectural intent for a financial narrative intelligence system.

It is intended for architecture-level agents responsible for designing downstream system components (e.g. ARCHITECTURE.md, DATA_MODEL.md, SIGNAL_DEFINITIONS.md).

This document prioritizes conceptual clarity over implementation detail.

Where this document and any downstream document disagree, this document is authoritative.

---

# 1. Project Identity

## Working Definition

The system is a **financial narrative intelligence system** that detects meaningful changes in meaning, confidence, framing, and consistency across time in financial text.

It achieves this through **heuristic structure and learned representations combined through a fusion layer**.

It is not a sentiment analyzer or a trading prediction system.

Instead, it focuses on:

* narrative evolution over time
* contextual meaning shifts
* communication consistency and contradiction
* omission and emergence of themes
* latent structure in financial language

---

# 2. Core Thesis

Financial meaning is not primarily contained in isolated statements.

> Meaning emerges through *change over time* across narratives.

The system assumes that informational value is derived from:

* temporal drift
* comparative analysis
* structural inconsistency
* repeated narrative reinforcement or decay
* disappearance of prior emphasis

This temporal and comparative view is foundational.

---

# 3. System Philosophy

## 3.1 Context Over Isolation

No document is interpreted independently. Every statement exists within a historical and cross-source context.

---

## 3.2 Hybrid Intelligence Model

The system is explicitly **hybrid**, combining:

### A. Structural / Heuristic Layer

Defines what matters and ensures interpretability:

* entity extraction
* document segmentation
* time alignment
* rule-based comparisons
* omission tracking logic
* contradiction detection scaffolding

### B. Machine Learning Layer

Provides semantic richness and generalization:

* embedding-based representation learning
* narrative similarity and drift detection
* probabilistic signal scoring
* latent feature extraction from financial text
* unsupervised pattern discovery

### C. Fusion Layer

Combines both to produce final signals:

* integrates heuristic + ML outputs
* resolves conflicts between structure and learned signals
* ensures explainability and traceability

The fusion layer is architecturally the most significant and deliberately the least specified component of the system.

It is where structural rigor and learned nuance reconcile, and where signal quality ultimately emerges.

It is expected to be treated as a hard design problem during downstream architecture work, not resolved by default.

ML is a **core subsystem**, not optional, but it does not replace structural reasoning.

---

## 3.3 Explainability Requirement

All outputs must be traceable to:

* source text
* structural rules (if applied)
* ML-derived scores (if used)

Black-box outputs without traceability are discouraged.

---

## 3.4 Structured Skepticism

The system must avoid:

* overconfident inference
* causal claims from weak correlations
* sentiment reductionism

Financial language is inherently noisy.

---

# 4. Core Signal Philosophy

A "signal" is not raw sentiment or prediction.

A signal is:

> a meaningful, explainable deviation or pattern in financial narrative structure over time

## Signal types include:

### Narrative Drift

Gradual change in framing, emphasis, or strategic communication.

### Confidence Shift

Changes in certainty, hedging, or assertiveness.

### Omission Event

Disappearance of previously recurring themes or priorities.

### Contradiction Event

Inconsistency across time or sources.

### Structural Anomaly

Unusual deviation from established communication patterns.

## Taxonomy Status

The signal types defined above constitute the **confirmed initial taxonomy** for the system.

They are not assumed to be exhaustive.

New signal types may be introduced over time through either of two paths:

* **research-driven proposal** — a new type is proposed from analytical or research work
* **discovery-driven proposal** — a new type is proposed by the ML layer under §5.4 via unsupervised pattern discovery

Both paths resolve through the same human-review gate. Neither path is privileged over the other.

The extension pattern for adding new signal types is expected to be defined in downstream signal definition work (SIGNAL_DEFINITIONS.md).

---

# 5. ML Role Definition

Machine learning is used to amplify signal detection, not define system truth.

## ML Responsibilities:

### 5.1 Representation Learning

* semantic embeddings of financial text
* cross-document similarity
* narrative clustering

### 5.2 Signal Enhancement

* drift detection beyond heuristic thresholds
* uncertainty modeling
* latent structure detection

### 5.3 Behavioral Modeling

* communication pattern profiling
* deviation detection from baseline behavior

### 5.4 Optional Extensions

* unsupervised discovery of emerging narrative themes

## ML Constraints:

* must remain explainable at signal level
* must not act as sole decision-maker
* must be grounded in structured inputs

---

# 6. Model Ownership Posture

## 6.1 Posture Summary

The system relies on models the project trains, owns, and operates in-house.

External large-language-model APIs are **not** assumed as a dependency in critical paths.

This posture exists for three reasons:

* cost sustainability (no assumed per-call inference budget)
* control over model behavior, versioning, and explainability
* fit with the narrow, domain-specific nature of financial narrative

The posture is also a **security property**: minimizing third-party inference surface reduces the attack surface, supply-chain exposure, and potential for uncontrolled data egress.

The "no external LLM API in critical paths" commitment is a system-wide **invariant** (labeled *Critical-Path Isolation* in downstream documents). Exhaustive test enforcement is infeasible under the low-capital constraint; the invariant is therefore **structurally enforced and audit-observed** rather than asserted by automated tests.

---

## 6.2 Model Strategy Shape

The system does not rely on a single large general-purpose model.

It relies on a stack of **small, specialized models**, each scoped to a narrow task.

This stack may conceptually include:

* a domain-adapted representation model for financial text
* task-specific lightweight models for particular signal types (e.g. confidence analysis, contradiction detection)
* optional local small-footprint language models for structured extraction tasks that exceed heuristic capability
* optional local small-footprint language models for **bounded, grounded generation tasks** (e.g. Signal Commentary under a grounding check that anchors output to Basis and Evidence)

Adaptation of open-source weights for any of the above is considered inside the in-house posture, provided the model is operated on project infrastructure and not served by an external provider.

Specific model architectures, training data strategies, and model selection are deferred to downstream model strategy work (MODEL_STRATEGY.md).

---

## 6.3 Implications

* training must be feasible on modest hardware budgets
* models must be replaceable without restructuring the system
* inference must be runnable locally or on inexpensive infrastructure
* external API dependencies must not appear in critical paths
* model versioning and traceability are first-class concerns

---

## 6.4 Constraint

Models exist in service of explainable signal extraction.

Model sophistication must not come at the cost of traceability or interpretability.

Complexity is justified only when it produces measurably better signals than simpler alternatives.

---

# 7. Heuristic Role Definition

Heuristics define system structure and constraints.

They are responsible for:

* defining what counts as a signal
* enforcing consistency across time
* anchoring ML outputs
* providing baseline interpretability

Heuristics are not secondary; they are **structural scaffolding** for ML.

---

# 8. Data Domains

The system may process:

* earnings call transcripts
* SEC filings
* press releases
* financial news
* executive interviews
* macroeconomic reports
* analyst commentary
* public market discourse (optional future extension)

## Initial Scope

Initial scope is committed to **earnings call transcripts**.

This domain is chosen because it offers:

* high temporal regularity (quarterly cadence)
* consistent structural format
* rich narrative content per document
* strong entity-to-document association
* sufficient historical depth for comparative analysis

Other domains remain in scope for future expansion but are deferred until signal quality is validated on the initial domain.

## Licensing Posture

Acquisition is not only a matter of availability. **Licensing-posture compatibility is a first-class concern**: sources whose terms restrict training use constrain what the in-house model stack can learn from.

Source terms are classified by their operational compatibility — training-compatible, analytical-only, or incompatible-or-ambiguous — and this classification is carried with artifacts through the derivation layers. Detailed strategy is owned by DATA_ACQUISITION.md.

## Language Posture

V1 is **English-first**.

Multilingual capability is not a v1 requirement. Extension to other languages is a deferred concern for future model strategy work.

## Thin-History Posture

For entities with limited historical depth, the system prefers **reliability over coverage**.

Signals that depend on a baseline are subject to reliability thresholds rather than emitted opportunistically. Specific thresholds are deferred to downstream analytical work.

---

# 9. Intended Outputs

The system produces **structured, explainable insights**, not raw predictions.

Outputs may include:

* ranked signals
* narrative change reports
* contradiction summaries
* omission alerts
* confidence shift analysis
* evidence-linked explanations

## Output Format Philosophy

Outputs must include:

* what changed
* where it changed
* why it is considered meaningful
* supporting evidence references

## Output Type Assumption (CONFIRMED)

The system uses a **hybrid output model**:

* structured signals (ranked)
* explanatory context
* supporting excerpts

---

# 10. System Boundaries

## Explicit Non-Goals

The system is not intended to:

* predict stock prices directly
* provide financial advice
* function as an autonomous trading agent
* reduce analysis to sentiment scoring
* operate as a black-box prediction engine

---

# 11. Key Design Constraints

* temporal reasoning is mandatory
* cross-document comparison is core
* explainability is required
* signals must be traceable
* ML must augment, not obscure reasoning
* heuristics must provide structural grounding
* models must be ownable and operable without external API dependency
* re-derivability is an invariant (a DerivationRun + its inputs must reproduce the original artifact); the named mechanism for reproducible historical replay is the **Pipeline Version**, defined in downstream pipeline work
* **as-of reconstruction** is a first-class capability exposed both internally (Query & Retrieval Surface) and externally (API)

---

# 12. Conceptual Architecture Direction

The system will likely evolve around three layers:

## 12.1 Structural Layer

Defines and organizes financial text data.

## 12.2 Semantic Layer (ML)

Learns representations and latent patterns.

## 12.3 Signal Layer

Produces interpretable financial narrative signals.

---

# 13. Key Risks

## 13.1 Overfitting to Noise

Financial language is highly noisy; ML may detect patterns that are not meaningful.

## 13.2 Overconfidence in Signals

The system must avoid implying certainty where none exists.

## 13.3 Model Drift Without Ground Truth

Many signals are inherently subjective; evaluation is difficult.

## 13.4 Loss of Interpretability

ML must not eliminate traceability of outputs.

## 13.5 Model Ownership Burden

Training and maintaining in-house models carries operational cost and expertise requirements; this burden is accepted deliberately in exchange for control and explainability.

---

# 14. Evaluation Philosophy

Success is not measured by prediction accuracy alone.

Instead:

* usefulness of detected signals
* clarity of explanations
* consistency over time
* reduction of human cognitive load
* ability to surface non-obvious narrative changes

## Evaluation Approach

Evaluation methodology is itself a research concern.

Early-stage evaluation is expected to rely on:

* structured human review of surfaced signals
* qualitative analyst feedback
* internal dogfooding on known historical narratives
* retrospective study of past narrative changes with known outcomes

Automatic metrics are not expected to substitute for human judgment during early development.

The absence of clean ground truth (§13.3) is acknowledged as a central evaluation challenge rather than a solved problem.

The evaluation harness itself is an evolving artifact and is expected to mature alongside the system. The structured instruments used inside it — notably the Review Rubric and the Reviewer Cohort — are also expected to evolve.

Evolution must not become a mechanism for perpetual deferral. If the harness is always "about to mature", evaluation has failed. Milestones for harness maturation are tracked in EVALUATION.md and RESEARCH_NOTES.md.

## False-Positive Posture

In early development, **false positives carry greater cost to user trust than false negatives**.

The project accepts reduced coverage in exchange for higher surfaced-signal reliability.

This posture may evolve as the system matures. It is stated here so that downstream tuning, ranking, and evaluation work defaults to the same priority.

---

# 15. Open Questions

* What is the optimal definition of a "meaningful signal"?
* How should signal importance be ranked?
* How should uncertainty be communicated to users?
* How should multi-source contradictions be resolved?
* What is the right balance between heuristic rigor and ML generalization per signal type?
* How should the fusion layer reconcile conflicting heuristic and ML outputs?
* What data is required to train or fine-tune the in-house representation model with acceptable signal quality?

---

# 16. Confirmed Assumptions

* ML is a core subsystem, not optional
* system is hybrid (heuristics + ML + fusion layer)
* outputs are structured + explainable
* sentiment analysis is insufficient as a primary model
* temporal comparison is fundamental
* system is exploratory, not purely predictive
* models are trained and owned in-house, not consumed as external APIs
* model strategy favors small, specialized, lightweight models over large general-purpose models
* initial scope is committed to earnings call transcripts
* the signal taxonomy is the confirmed initial set and is extensible through research-driven and discovery-driven paths
* evaluation depends on human judgment during early development
* v1 is English-first
* for thin-history entities, reliability is preferred over coverage
* in early development, false positives are costlier to user trust than false negatives

---

# 17. Audience and User Modeling

Detailed modeling of users, their workflows, and their information needs is deliberately deferred to downstream documents.

User experience, personas, and interaction design are expected to be developed in dedicated documents (USER_EXPERIENCE.md and related artifacts).

The system is broadly intended to support individuals who engage deeply with financial text: independent analysts, researchers, investors, and information-heavy decision makers who value depth over speed and explainability over opacity.

V1 is **single-user** and **entity-centric** at the user-facing surface. Multi-user collaboration, portfolio-aware workflows, and cross-entity aggregated surfaces are deferred.

Further refinement of the audience model is expected as the product takes shape.

---

# 18. Decision Traceability

Project-level decisions — including those that emerge through consolidation passes across document clusters — are tracked in DECISION_LOG.md.

DECISION_LOG.md is a living artifact. Downstream documents may reference a decision record by ID; the glossary, assumptions, and scope documents may be updated to reflect a resolved decision, and the decision record notes which documents were touched.

If a contradiction arises between a downstream document and this document, it should be surfaced as a decision in DECISION_LOG.md rather than silently resolved.

---

# 19. Final Strategic Principle

The system is best understood as:

> a temporal narrative intelligence engine for financial text

not a sentiment tool and not a trading bot.
