# SCOPE.md

## Purpose Of This Document

This document defines what the system is in scope to do and what it is not.

It is a scope document, not a design document. It addresses *what* is being built at a capability level. CONTEXT.md addresses *why* and *how the project thinks*.

Where this document and CONTEXT.md overlap, CONTEXT.md is authoritative.

---

## Project Overview

The project is a **financial narrative intelligence system** that detects meaningful changes in meaning, confidence, framing, and consistency across time in financial text, using heuristic structure and learned representations combined through a fusion layer.

The system ingests financial and market-related text sources, analyzes them in temporal and cross-source context, and produces **structured, explainable signals** that identify narrative changes worth human attention.

The system is not intended to function as an autonomous trading system or a generic sentiment analyzer. Instead, the focus is on extracting higher-order signals from changes in language, narrative evolution, omissions, contradictions, confidence shifts, and cross-source inconsistencies.

The core objective is to reduce information overload and improve signal extraction from large volumes of financial text.

---

## Core Problem Space

Financial information is fragmented across multiple sources and distributed over time.

Users are expected to manually process:

* earnings call transcripts
* SEC filings and disclosures
* company press releases
* executive interviews
* macroeconomic announcements
* analyst commentary
* financial news
* online discussion and sentiment platforms

Many of these sources constitute the user's current information problem but are not v1 deliverables. See Scope Boundaries below for what v1 explicitly includes and what is deferred.

Important signals are often subtle and difficult to detect manually, especially when they involve:

* changes in wording over time
* reduced confidence in communication
* narrative inconsistencies
* emerging risk language
* disappearing strategic themes
* contradictions across sources
* shifts in priorities or guidance

The project exists to identify and surface these changes in a structured and explainable manner.

---

## Architectural Commitments

The following commitments are inherited from CONTEXT.md and shape the scope of what the system will build:

* hybrid intelligence (heuristic layer + ML layer + fusion layer)
* ML is a core subsystem, not optional
* models are trained and owned in-house, not consumed as external APIs
* model strategy favors small, specialized, lightweight models
* signals must be traceable to source evidence
* explainability is non-negotiable

These commitments bound the scope of every functional area below.

---

## Primary Goals

### Narrative Change Detection

Detect meaningful changes in language, tone, framing, and strategic emphasis across time.

Examples:

* increased caution in executive language
* weakening confidence statements
* shifts in operational priorities
* reduced mention frequency of previously emphasized initiatives
* sudden introduction of new concerns or risks

This goal aligns with the canonical signal taxonomy defined in CONTEXT §4.

---

### Contextual Financial Signal Extraction

Extract signals that may have relevance to investment analysis.

The canonical signal taxonomy is defined in CONTEXT §4 and expected to be elaborated in SIGNAL_DEFINITIONS.md.

The project prioritizes contextual understanding over simplistic positive/negative sentiment classification.

---

### Temporal Analysis

Track how narratives evolve over time.

The system treats documents not as isolated inputs but as part of an ongoing sequence.

Potential forms of temporal analysis include:

* quarter-over-quarter comparison
* long-term executive communication drift
* recurring themes over time
* trend emergence or disappearance
* narrative persistence tracking

---

### Cross-Source Analysis

Compare narratives across different information sources.

Potential comparisons include:

* earnings calls vs SEC filings
* press releases vs executive interviews
* public statements vs disclosed risks
* media narratives vs company narratives

The goal is to identify contradictions, inconsistencies, or hidden information asymmetries.

---

### Explainable Insight Generation

All surfaced insights must be understandable and traceable.

The system prioritizes explainability over opaque scoring systems.

Outputs must clearly communicate:

* what changed
* why it may matter
* where the signal originated
* how the conclusion was formed

---

## Data Domains

The system is designed to eventually support multiple financial and market-related data domains.

Potential domains include:

* earnings call transcripts
* financial filings
* press releases
* economic reports
* news articles
* analyst reports
* market commentary
* retail sentiment discussions
* executive statements and interviews

### Initial Scope

Initial scope is committed to **earnings call transcripts** (see CONTEXT §8).

This is the only domain the v1 system is required to support. All other domains are deferred until signal quality is validated on the initial domain.

The system is designed with extensibility in mind so that additional domains can be integrated later without restructuring.

---

## Core Functional Areas

### Data Ingestion

The system must support ingesting and organizing financial text data.

Responsibilities include:

* document collection
* document normalization
* metadata association
* source attribution
* historical storage
* version tracking where applicable

---

### Document Understanding

The system must interpret financial text in context.

This includes:

* entity identification
* topic extraction
* relationship identification
* statement segmentation
* semantic interpretation
* contextual understanding of financial terminology

---

### Narrative Tracking

The system must maintain continuity across time.

This includes:

* recurring theme tracking
* historical comparison
* narrative evolution analysis
* strategic priority tracking
* confidence pattern tracking

---

### Signal Detection

The system must identify potentially meaningful signals from textual and contextual patterns.

Signal categories align with CONTEXT §4:

* narrative drift
* confidence shift
* omission event
* contradiction event
* structural anomaly

The canonical set is defined in CONTEXT §4 and SIGNAL_DEFINITIONS.md. New signal types may be added over time.

---

### Comparative Analysis

The system must compare information across:

* time periods
* document types
* companies
* industries
* communication channels
* executive speakers

---

### Insight Presentation

The system must provide outputs in a form that is actionable and understandable.

Potential output forms include:

* structured summaries
* change reports
* narrative drift reports
* supporting evidence excerpts
* confidence indicators

Alerting, push notifications, and dashboard-style aggregated views are deferred; v1 is a **pull-based, depth-oriented** surface. Detailed presentation design is deferred to USER_EXPERIENCE.md.

---

## Intelligence Concepts

The following conceptual areas underpin the system's analytical work.

The canonical signal taxonomy lives in CONTEXT §4; the entries below describe the conceptual *capabilities* the system must support.

### Narrative Drift

Detect gradual changes in strategic communication or executive messaging.

### Confidence Analysis

Identify changes in certainty, conviction, or hedging behavior.

### Omission Detection

Identify important topics or themes that disappear over time.

### Contradiction Analysis

Detect inconsistencies between:

* past and current statements
* separate communication channels
* stated goals and disclosed risks

### Behavioral Communication Profiling

Understand baseline communication behavior for specific executives or organizations.

The system may later identify deviations from established communication patterns.

### Market-Relevant Signal Correlation

Explore relationships between narrative patterns and future market behavior.

This area is treated as **exploratory** and is not a v1 deliverable. It is retained here to preserve awareness of the direction, not as a commitment.

---

## User Experience Goals

The system should help users:

* process large information volumes efficiently
* identify non-obvious narrative changes
* understand evolving company behavior
* reduce manual comparison work
* surface potentially overlooked risks or shifts
* improve research workflows

The system should avoid overwhelming users with raw data or low-quality signals.

Detailed user experience design is deferred to USER_EXPERIENCE.md.

---

## Design Principles

### Context Over Raw Sentiment

The project prioritizes contextual understanding rather than simplistic sentiment scoring.

### Temporal Awareness

Meaning often emerges through change over time rather than isolated statements.

### Explainability

Insights are inspectable and supported by evidence.

### Extensibility

The architecture must allow future expansion into additional data sources, signal types, and analytical capabilities.

### Human-Centered Analysis

The system augments human analysis rather than replacing human judgment.

### Model Ownership

The system is built on models the project trains and operates itself, not on external LLM APIs in critical paths.

---

## Scope Boundaries

### In Scope (v1)

* ingestion of earnings call transcripts
* entity identification and temporal document organization
* heuristic and ML-based analysis of the five canonical signal types (narrative drift, confidence shift, omission event, contradiction event, structural anomaly)
* a fusion engine that combines heuristic and ML outputs into ranked, traceable signals
* structured, explainable signal outputs with evidence links
* human-reviewable signal presentation (pull-based, entity-centric, single-user)
* an evaluation harness sufficient for early-stage structured human review
* a Signal lifecycle transition policy (Candidate, Surfaced, Stale, Superseded, Retired)
* as-of reconstruction of historical narrative state, exposed both internally and externally

### Deferred (v2+)

* additional data domains (filings, news, press releases, interviews, macro, analyst commentary, public discourse)
* real-time or streaming analysis
* multi-modal inputs
* portfolio-aware or personalized workflows
* market-correlation studies
* predictive signal experimentation
* collaborative / multi-user research tooling
* alerting, push notifications, and dashboard-style aggregated views

### Deferred vs. Long-Term Expansion

"Deferred" items are out of v1 but are **available for phase-gated entry** in subsequent versions once v1 signal quality is validated (see ROADMAP.md).

"Long-Term Expansion Possibilities" (below) are **horizon-level** possibilities that are not yet on any phase gate.

If an item appears in both lists, the Deferred entry is authoritative for phase-gating purposes.

---

## Non-Goals

The project is not intended to:

* guarantee profitable trading outcomes
* function as a fully autonomous trading agent
* provide financial advice
* operate as a simplistic sentiment classifier
* generate unsupported predictions without evidence
* depend on external LLM APIs in critical paths
* produce entity-level aggregate scores (Signal Strength is type-relative; no cross-type or cross-entity aggregate is emitted)
* claim completeness of coverage (absence of a Signal is never a claim of absence of risk)
* provide alerting or dashboard-style aggregated views in v1

---

## Open Questions

The following areas remain intentionally undefined at this stage and are expected to be resolved during downstream architecture and research work:

* specific training-data requirements to fine-tune the in-house representation model (tracked in RESEARCH_NOTES.md)
* storage and deployment strategy (downstream infrastructure work)

### Questions Now Owned

The following were open in earlier drafts and are now assigned to owner documents. They are listed here as pointers, not as open items.

* signal ranking and prioritization methodology → NARRATIVE_ANALYSIS.md and EVALUATION.md
* scoring methodologies within the fusion engine → MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md
* user interaction model → USER_EXPERIENCE.md
* data acquisition specifics for earnings call transcripts → DATA_ACQUISITION.md
* specific model architecture selection → MODEL_STRATEGY.md (posture is in CONTEXT §6)
* evaluation methodology beyond human review → EVALUATION.md
* real-time vs. batch processing decisions → resolved to **deliberate / batch / on-demand** in ARCHITECTURE.md Operating Posture

---

## Long-Term Expansion Possibilities

Potential future expansion areas may include:

* personalized research workflows
* portfolio-aware analysis
* industry-wide narrative tracking
* macroeconomic narrative monitoring
* event-driven analysis systems
* real-time monitoring and alerting
* multi-modal financial intelligence
* collaborative research tooling
* predictive signal experimentation

These are future possibilities rather than immediate project requirements.
