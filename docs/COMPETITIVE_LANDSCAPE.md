# COMPETITIVE_LANDSCAPE.md

## Purpose Of This Document

COMPETITIVE_LANDSCAPE.md describes the landscape of existing financial-text tooling at a categorical level, names the posture-level gaps those categories leave unoccupied, and explains what is structurally distinctive about this project relative to that landscape.

It is a landscape document, not a competitive deck. It names categories of tools, not products. It is not a vendor evaluation, a pricing analysis, or a positioning exercise.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). The project's orientation is grounded in [VISION.md](./VISION.md).

---

## How To Read This Document

* the landscape is described as categories of capability and posture, not as a list of named products
* each category is named operationally, so that a reader can recognize an instance without the document having to name one
* the project's distinctive posture is grounded in [CONTEXT.md](./CONTEXT.md) and [VISION.md](./VISION.md) rather than in contrasts with any specific alternative
* the document closes with competitive-drift risks — the directions the project must *not* drift in — and the architectural protections already in place against them

---

## Orientation

The project is, per [VISION.md](./VISION.md), a temporal narrative intelligence engine for financial text. Its subject is the Financial Narrative of an Entity over time. Its outputs are structured, explainable Signals in the sense defined by [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md): meaningful, explainable deviations or patterns in narrative structure over time, with Basis and Evidence.

The landscape described below is surveyed against this orientation. A tool that does something different well is not diminished by its placement here; it is simply solving a different problem.

---

## The Landscape, Conceptually

The following categories are recognizable in the field of tooling that touches financial text. Categories are described by the kind of work they optimize for and the assumptions that shape them.

The same product may occupy more than one category. The categories are analytical lenses, not mutually exclusive buckets.

---

### Sentiment-Oriented Tools

Tools whose central output is a polarity score — positive, negative, neutral, or a variation — applied to financial text.

The operational assumption is that financial meaning can be reduced to a direction and a magnitude on a single axis. Outputs are typically numeric and aggregable.

Appropriate for: first-order triage of large volumes of text, downstream consumption by systems that want a single numeric feature, applications where aggregate mood rather than narrative structure is the unit of interest.

---

### General-Purpose Large-Language-Model Assistants

Generalist conversational systems queried ad hoc against financial text. The user asks; the system responds; each query is broadly independent.

The operational assumption is that a general-purpose model can be steered into financial analysis by prompt. Responses are fluent, free-form, and typically not accompanied by system-level provenance.

Appropriate for: exploratory reading, single-document summarization, ad hoc question answering, tasks where the user is present and can verify the answer inline.

---

### Institutional-Grade Natural-Language-Processing Platforms

Enterprise platforms that ingest broad financial corpora, emit structured features, and integrate into institutional data pipelines. Typically built for sell-side, buy-side, or corporate-data consumers.

The operational assumption is that scale, breadth, and integration with existing workflows are the primary value. The features tend to be designed for aggregation into quantitative models rather than for direct human reading.

Appropriate for: systematic strategies that want text-derived features at scale, data-science teams who will compose derived features downstream, institutions whose cost base absorbs the integration expense.

---

### Retail Analyst Aggregators And Market Commentary

Platforms that aggregate community commentary, crowd-sourced analysis, news, or a mixture of these, and surface them to retail investors.

The operational assumption is that velocity, breadth of opinion, and recency are the primary value. Curation, when present, is social rather than structural.

Appropriate for: retail readers seeking a continuous feed of perspective, contexts where recency dominates depth, aggregation of heterogeneous sources into a single stream.

---

### Academic Research Tools

Research artifacts — papers, corpora, experimental pipelines — that study financial text from a scholarly perspective. Often specialized, often one-off, often not productized.

The operational assumption is that a specific research question drives the construction, and that reproducibility within the study matters more than continuous operation.

Appropriate for: the study that motivated the tool; as prior art for productized systems; as a source of methods that may eventually harden into production.

---

### Alerting And News-Aggregation Tools

Systems whose central output is a stream of recent items, possibly filtered or tagged, delivered on a low-latency cadence.

The operational assumption is that the marginal value is being first to know. Ranking, when present, tends to be recency-weighted.

Appropriate for: readers who already know what they are looking for and want to be notified when it arrives, contexts where decisions are timing-sensitive rather than interpretation-sensitive.

---

### Predictive And Alpha-Generation Systems

Tools that emit predictions about future market outcomes — price, volatility, earnings surprise, event risk — derived in whole or in part from text.

The operational assumption is that text can be converted into a forward-looking quantitative prediction useful to a trading process. The output is typically consumed by a model, not read by a human.

Appropriate for: trading strategies, quantitative research that treats text as one of many feature sources, pipelines that value numeric output over narrative explanation.

---

## Posture-Level Failure Modes With Respect To Temporal Narrative Intelligence

Each category above solves a real problem well. Each leaves a particular gap when measured against the specific problem this project pursues — reading financial narrative *through change across time*, with Evidence and Basis carried through every output, under the structural commitments described in [CONTEXT.md](./CONTEXT.md) §3.

The failure modes below are of posture, not of product quality.

### Against Sentiment-Oriented Tools

Sentiment collapses narrative onto a scalar axis. Narrative Drift, Confidence Shift, Omission Event, Contradiction Event, and Structural Anomaly — the confirmed taxonomy in CONTEXT §4 — cannot be expressed as polarity. A Confidence Shift is orthogonal to sentiment; an Omission Event is the *absence* of material, not a signed value; a Contradiction Event is a relational claim between two statements, not a property of one.

Structured skepticism (CONTEXT §3.4) also rejects sentiment reduction as a posture. A tool whose core output is polarity cannot host this project's Signal contract without changing what it is.

### Against General-Purpose Large-Language-Model Assistants

General-purpose assistants are optimized for single-query fluency. They do not, as a class, maintain a Baseline of an Entity's communication over time, do not track NarrativeState across Documents, and do not preserve Basis and Evidence chains at the system level. An answer is produced; the trace that would support CONTEXT §3.3 explainability is not a first-class artifact.

Per CONTEXT §6.1, relying on an external large-language-model API in any critical path is a failure mode by construction. A system whose primary output mechanism is an external general-purpose model cannot satisfy the ownership posture this project has committed to.

### Against Institutional-Grade Natural-Language-Processing Platforms

Institutional platforms emit features optimized for downstream quantitative consumption. They are not, as a class, oriented toward a human analyst reading Surfaced Signals with attached Evidence. Their features are typically not explainable at the Signal level in the sense CONTEXT §3.3 requires; their cost base assumes an institutional integration project that this project explicitly cannot absorb ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint).

The failure mode is not quality. It is posture: breadth-and-integration versus depth-and-explanation.

### Against Retail Analyst Aggregators And Market Commentary

Aggregators optimize for recency and perspective volume. They do not, as a class, produce Baselines, track Theme recurrence, surface Omission Events, or maintain traceable Basis chains. Their value is horizontal breadth; this project's value is vertical depth on a specific Entity's narrative over time.

The failure mode is categorical. A stream of current commentary is not a record of narrative evolution, even when both contain similar raw material.

### Against Academic Research Tools

Research tools are, by posture, research tools. They are not, as a class, oriented toward continuous operation, Signal lifecycle management, or the discipline of emitting only what can be explained to a reader who was not in the study. The project draws on research results and methods; it does not organize itself as a study.

The failure mode is not a criticism of research — it is the statement that a productized temporal narrative intelligence engine is a distinct artifact.

### Against Alerting And News-Aggregation Tools

Alerting systems optimize for time-to-notification. This project explicitly accepts latency in exchange for depth ([ASSUMPTIONS.md](./ASSUMPTIONS.md) U2, U6); Signals here are observations about change in narrative, not notifications about a newly arrived Document. The unit of output is different, and so is the disposition toward the reader.

An alert answers the question *did something new arrive*. A Signal in this project answers the question *did something meaningful change in the narrative over time, and why*.

### Against Predictive And Alpha-Generation Systems

Predictive systems emit forward-looking claims. This project rejects prediction framing by construction (CONTEXT §10; [SCOPE.md](./SCOPE.md) Non-Goals; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions). A Signal in this project describes observed change, not future state; Strength is not a probability of anything external ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Anatomy).

A system whose commercial claim is forward prediction is solving a different problem with different evaluation criteria, different failure modes, and a different relationship to uncertainty.

---

## What Is Structurally Distinctive About This Project

The project's distinctness is not located in any single capability. It is located in the conjunction of several commitments held simultaneously. Each is individually imitable; the conjunction is what produces a coherent temporal narrative intelligence engine rather than a tool in one of the categories above.

### Temporal-First Orientation

The core thesis of CONTEXT §2 is that meaning emerges through change across narratives. Documents are not primary; the Financial Narrative an Entity generates over time is primary. Baselines, NarrativeState, Subject Time distinct from Emission Time, and the as-of query mechanism are all expressions of this commitment.

Most tooling in the landscape treats documents as independent inputs and treats recency as a proxy for relevance. This project treats recency as a temporal coordinate and treats change as the unit of meaning.

### Hybrid Intelligence As Architecture

CONTEXT §3.2 commits to a Heuristic Layer, an ML Layer, and a Fusion Layer that combines them. The Fusion Engine is a first-class component and a designated hard design problem (CONTEXT §3.2.C; [ARCHITECTURE.md](./ARCHITECTURE.md)).

Heuristics are not fallback logic; they are structural scaffolding (CONTEXT §7). The ML layer is not optional; it is a core subsystem (CONTEXT §16). The combination is the architecture, not an aspiration.

Most tooling leans hard in one direction. Pure-heuristic systems are brittle on nuance; pure-ML systems are opaque under financial scrutiny. A hybrid with a dedicated fusion step treats reconciliation as a first-class concern rather than a residual.

### Explainability As A System-Wide Property

CONTEXT §3.3 requires traceability to source text, structural rules, and model-derived scores for every surfaced output. [ARCHITECTURE.md](./ARCHITECTURE.md) realizes this as the Evidence & Provenance Store and the Basis chain carried by every Signal. [DATA_MODEL.md](./DATA_MODEL.md) realizes it as the Signal → Basis → Candidate Evidence → Features → Evidence → Spans → Document → Raw chain, with no artifact emitted unless its position in the chain is resolvable.

Most tooling treats explanation as a presentation layer added after the analysis is done. This project treats explainability as an invariant of the pipeline, preserved at every stage.

### In-House Model Ownership

CONTEXT §6.1 commits the system to models the project trains, owns, and operates; external large-language-model APIs are excluded from critical paths. CONTEXT §6.2 commits to a stack of small, specialized models rather than a single large model. This is a cost, control, and explainability posture; it is accepted deliberately (CONTEXT §13.5).

Most tooling, including many recent entrants, relies on external general-purpose model APIs at the critical path. This project has chosen the opposite trade: more operational burden, less control dependence, and a better fit with the narrow domain shape.

### Structured Skepticism And Restraint

CONTEXT §3.4 requires avoiding overconfident inference, causal claims from weak correlations, and sentiment reductionism. [VISION.md](./VISION.md) states the principle directly — restraint beats coverage — and classifies noise as a regression. [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3 accepts false negatives as less costly than false positives in the early period. [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) operationalizes this via the separation of Strength from Confidence and via the Thin-History Policy.

Most tooling is under commercial pressure to report more. This project is under construction-level pressure to report less and better.

### Narrow Scope By Design

[VISION.md](./VISION.md)'s North Star is deliberately narrow. [SCOPE.md](./SCOPE.md) commits v1 to earnings call transcripts and defers additional data domains until signal quality is validated (SCOPE Deferred; ASSUMPTIONS E1). Long-term expansion possibilities remain possibilities, not plans (SCOPE Long-Term Expansion Possibilities).

Most tooling seeks generality. This project seeks durability in a narrow problem — a posture more common in research than in product, and one that depends on holding its shape under pressure.

### Entity-Centric Orientation

[DATA_MODEL.md](./DATA_MODEL.md) centers analytical state on the Entity. Baselines, NarrativeStates, and Signals all anchor to an Entity (and, where relevant, a Speaker within that Entity). Cross-Entity analysis is available as an extension but not as the anchoring frame (DATA_MODEL Entity-Centric Orientation).

Most tooling aggregates across Entities as the primary mode. This project analyses within an Entity's narrative as the primary mode, with cross-Entity analysis deferred to v2+.

---

## Where The Project Explicitly Does Not Compete

Several areas that a competitive reading might place the project into are, on examination, out of scope. Naming them here prevents mistaken comparison.

* **Prediction and alpha generation** — not in scope (CONTEXT §10; SCOPE Non-Goals; SIGNAL_DEFINITIONS What A Signal Is Not). The project does not compete with predictive or alpha-generation systems; it does not claim their outcomes.
* **Trading automation and recommendation** — not in scope (CONTEXT §10; SCOPE Non-Goals). The system informs a human; it does not act.
* **Real-time or streaming delivery** — deferred to v2+ (SCOPE Deferred). The project does not compete with alerting or news-aggregation tools on latency.
* **Breadth across data domains** — deferred (SCOPE Initial Scope; ASSUMPTIONS E1). The project does not compete with aggregator platforms on breadth; the initial domain is earnings call transcripts.
* **Multi-user collaboration, portfolio workflows, personalization** — deferred to v2+ (SCOPE Deferred; ASSUMPTIONS U4, U5). The project does not compete with collaborative research platforms in early phases.
* **General-purpose financial assistance** — not a goal (VISION What The System Is Not). The project does not compete with generalist conversational systems.
* **Simplistic sentiment classification** — rejected by construction (CONTEXT §3.4, §10; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions). The project does not compete with sentiment tools on polarity scoring.

A reader evaluating whether this project is redundant with an existing tool should first check whether the evaluation is against the project's actual subject — temporal narrative intelligence over financial text — or against one of the areas above. Comparisons across the boundary are not productive.

---

## Competitive Drift Risks

The most likely way this project would come to resemble tools in the landscape it does not intend to compete with is not through choice but through drift. [VISION.md](./VISION.md) names the drift directions; they are restated here and annotated with the landscape category that each drift would pull the project into.

* **Drift toward sentiment** — would pull the project into the sentiment-oriented-tools category. Protected by CONTEXT §3.4 and §10, by SIGNAL_DEFINITIONS What A Signal Is Not, and by the [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definition of sentiment.
* **Drift toward prediction** — would pull the project into the predictive-and-alpha-generation category. Protected by CONTEXT §10, SCOPE Non-Goals, SIGNAL_DEFINITIONS What A Signal Is Not, and the Strength-is-not-a-probability invariant.
* **Drift toward opacity** — would reduce the project to a general-purpose assistant or a black-box platform. Protected by CONTEXT §3.3, by [ARCHITECTURE.md](./ARCHITECTURE.md)'s Evidence & Provenance Store and Basis chain requirements, and by [DATA_MODEL.md](./DATA_MODEL.md)'s no-artifact-without-provenance invariant.
* **Drift toward external dependency** — would pull the project into the general-purpose-assistant category and surrender the ownership posture. Protected by CONTEXT §6.1 and [ARCHITECTURE.md](./ARCHITECTURE.md)'s Model Ownership Posture.
* **Drift toward autonomous action** — would place the project in a category it has excluded by name (CONTEXT §10; SCOPE Non-Goals; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions, Autonomous Agent).
* **Drift toward scope sprawl** — would dilute the project into an institutional platform or aggregator before the initial domain's signal quality is validated. Protected by SCOPE Deferred, ASSUMPTIONS E1, and the Low-Capital Constraint in [ARCHITECTURE.md](./ARCHITECTURE.md).
* **Drift toward noise** — would erode the trust that restraint buys. Protected by the false-positive posture (ASSUMPTIONS S3), by the separation of Strength from Confidence in SIGNAL_DEFINITIONS, and by the Thin-History Policy.
* **Drift toward ground-truth theater** — would produce an evaluation regime that flatters the system rather than stressing it. Protected by CONTEXT §14 and §13.3, which treat the absence of clean ground truth as a central challenge rather than a solved problem.

---

## Architectural Protections Already In Place

Several structural choices in the Wave 1 documents specifically resist the drifts above. They are summarized here because they are the load-bearing mechanism by which the project's posture holds over time.

* the Signal contract — Basis and Evidence are required on every Signal; no artifact may be emitted without a resolvable chain to source Spans ([DATA_MODEL.md](./DATA_MODEL.md); [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Anatomy)
* the separation of Strength and Confidence — a system that could only report a single number would be unable to honor structured skepticism; reporting both keeps epistemic honesty at the Signal level
* the Thin-History Policy — an Entity with insufficient historical depth is treated as a queryable state rather than a silent inference, preventing overreach into thin-Baseline territory
* the Fusion Engine contract — extensions attach as new feature contributors; the contract itself is load-bearing for extensibility and changes are expected to be cautious ([ARCHITECTURE.md](./ARCHITECTURE.md) Extensibility)
* the lifecycle model — Signals are immutable once emitted; lifecycle transitions are expressed as new records with lineage, not as mutations; a Signal that turns out to be wrong is retired with a trace rather than deleted
* the Candidate-Type Pool — discovery-driven taxonomy extensions flow through a human-review gate rather than appearing silently (CONTEXT §4; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension)
* the Low-Capital Constraint — features that multiply infrastructure cost without corresponding signal-quality gains are out of scope ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint)

These are not competitive talking points. They are structural commitments that, held consistently, keep the project in the category it intends to occupy.

---

## What This Document Does Not Claim

* no claim is made that any specific product or platform is deficient — categories are analytical lenses, not judgments of instances
* no claim is made that the project's distinctness is a market advantage — distinctness is the precondition for doing a specific kind of work, not a commercial position
* no claim is made about relative accuracy against any named alternative — [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions explicitly avoids accuracy as a primary evaluation term
* no claim is made that drift risks are bounded by the enumeration here — the list is the current set, not an ontology of all possible drifts
* no ranking is given of the project relative to the categories above — the document is about posture, not about comparative ranking

---

## Deferred To Other Documents

* specific product or vendor comparisons — not in scope here and not recommended elsewhere without a clear purpose
* pricing or positioning — out of scope for this document set
* evaluation methodology against any external benchmark — deferred to EVALUATION.md (see also CONTEXT §14 on the evaluation philosophy that frames any such benchmark)
* data acquisition and licensing posture relative to data vendors — deferred to a future data-acquisition document (flagged in [ARCHITECTURE.md](./ARCHITECTURE.md) Open Structural Questions and [SCOPE.md](./SCOPE.md) Open Questions)

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) is authoritative; this document depends on §1–§6, §10, §14 for its grounding.
* [VISION.md](./VISION.md) supplies the North Star, Strategic Edge, and Failure Modes used here.
* [SCOPE.md](./SCOPE.md) supplies the Scope Boundaries, Non-Goals, and Deferred list used to locate the project in the landscape.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) supplies the vocabulary; its Deliberate Non-Definitions are load-bearing for the drifts enumerated above.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies U-, D-, S-, and E-series assumptions used to justify posture choices.
* [ARCHITECTURE.md](./ARCHITECTURE.md) supplies the structural protections cited in the final sections.
* [ROADMAP.md](./ROADMAP.md) shares this document's orientation and must remain consistent with its account of what the project is and is not.
