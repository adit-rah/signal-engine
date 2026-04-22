# DECISION_LOG.md

## Purpose Of This Document

This document is the durable record of project-level decisions.

A decision log entry captures a resolved ambiguity, a chosen direction, or a settled trade-off — along with the alternatives considered, the reasoning, and the documents touched. It exists so that future contributors can understand *why* the project looks the way it does, and so that the decision trail remains independent of any single contributor's memory.

It is a living artifact. Entries are appended over time. Existing entries are not edited; if a decision is reversed or superseded, a new entry records the reversal and references the prior entry.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative — but CONTEXT.md updates that follow a decision should reference the decision entry here.

---

## How To Use This Document

* Entries are appended chronologically. Each entry is immutable once recorded.
* Every entry has a unique identifier (DL-YYYY-NNN).
* Entries cite the documents they touched so cross-document consistency is auditable.
* If a decision has follow-on dependencies that are not yet resolved, the entry names them as open follow-ons.
* Related open research questions live in RESEARCH_NOTES.md, which may cross-reference decisions here.

---

## Entry Format

Each entry includes:

* **ID** — a stable identifier (DL-YYYY-NNN)
* **Title** — a short declarative statement of the decision
* **Status** — one of: accepted, superseded, reversed
* **Question** — what ambiguity this decision resolves
* **Alternatives considered** — the options that were weighed
* **Decision** — the chosen direction
* **Rationale** — why this direction was chosen
* **Documents affected** — the documents updated or constrained by the decision
* **Follow-ons** — any open concerns this decision produces

---

## Entries

### DL-2026-001 — Hybrid intelligence is the architectural commitment

* **Status:** accepted
* **Question:** Is the project heuristic-only, ML-only, or hybrid?
* **Alternatives considered:** heuristic-only (simpler, more explainable, less semantic reach); ML-only (more generalization, weaker interpretability); hybrid with ML as a core subsystem (semantic reach anchored by structural scaffolding).
* **Decision:** The system is hybrid. The Heuristic Layer, ML Layer, and Fusion Layer are all first-class. ML is a core subsystem; heuristics are structural scaffolding.
* **Rationale:** Sentiment reduction is rejected; temporal narrative intelligence requires semantic reach; explainability requires structural anchoring. No single layer suffices.
* **Documents affected:** CONTEXT §3.2, SCOPE Architectural Commitments, ARCHITECTURE.md, DATA_MODEL.md, SIGNAL_DEFINITIONS.md.
* **Follow-ons:** Fusion Engine mechanics are the designated hard design problem; owned by MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md.

---

### DL-2026-002 — Model ownership posture is in-house, small, specialized

* **Status:** accepted
* **Question:** Does the project depend on external LLM APIs in critical paths?
* **Alternatives considered:** external LLM API for core analysis (lowest time-to-first-signal, high cost, loss of control); single large in-house model (high quality, high training cost, operational burden); stack of small specialized in-house models (per-task scope, low cost, high control).
* **Decision:** A stack of small, specialized, in-house models. External LLM APIs do not appear in critical paths. This posture is also a security property and a structural invariant.
* **Rationale:** Cost sustainability; behavioral control; fit with narrow domain; security surface reduction; consistency with explainability.
* **Documents affected:** CONTEXT §6, SCOPE Non-Goals, ARCHITECTURE.md, MODEL_STRATEGY.md, SECURITY_AND_PRIVACY.md.
* **Follow-ons:** Critical-Path Isolation is structurally enforced and audit-observed, not exhaustively test-enforced; DATA_ACQUISITION.md must enforce licensing compatibility with training use.

---

### DL-2026-003 — Initial scope is committed to earnings call transcripts

* **Status:** accepted
* **Question:** Which data domain does v1 support?
* **Alternatives considered:** broad multi-source ingestion from day one; narrow single-domain start (earnings transcripts).
* **Decision:** Earnings call transcripts only. Other domains are deferred until signal quality is validated on the initial domain.
* **Rationale:** Start narrow, preserve signal quality, bound scope. Earnings transcripts offer temporal regularity, structural consistency, and sufficient historical depth.
* **Documents affected:** CONTEXT §8, SCOPE Initial Scope, SCOPE Scope Boundaries, DATA_MODEL.md, DATA_ACQUISITION.md, INGESTION_SPEC.md.
* **Follow-ons:** Validated Quality gate for domain expansion is owned by EVALUATION.md and ROADMAP.md.

---

### DL-2026-004 — Fusion Layer (concept) is distinct from Fusion Engine (component)

* **Status:** accepted
* **Question:** How is the conceptual Fusion Layer from CONTEXT §3.2.C distinguished from the architectural component that realizes it?
* **Alternatives considered:** use "Fusion Layer" for both (creates ambiguity); introduce "Fusion Engine" as the component name (preserves conceptual/component distinction).
* **Decision:** "Fusion Layer" refers to the conceptual sub-layer of hybrid intelligence. "Fusion Engine" refers to the single architectural component in ARCHITECTURE.md that realizes the Fusion Layer concept.
* **Rationale:** Preserves clarity across the document set. Both terms are now load-bearing and distinct.
* **Documents affected:** DOMAIN_GLOSSARY.md, ARCHITECTURE.md, DATA_MODEL.md, SIGNAL_DEFINITIONS.md, MODEL_STRATEGY.md, NARRATIVE_ANALYSIS.md.
* **Follow-ons:** None.

---

### DL-2026-005 — Signal taxonomy is extensible via two paths

* **Status:** accepted
* **Question:** Can new Signal types be added after v1, and if so, how?
* **Alternatives considered:** closed taxonomy (five types only, forever); open taxonomy with ad-hoc additions (risks sprawl); open taxonomy with two explicit paths and a shared review gate.
* **Decision:** The taxonomy is extensible through Research-Driven Extension and Discovery-Driven Extension. Both paths resolve through the same human-review gate. Neither path is privileged.
* **Rationale:** Recognizes that research and unsupervised discovery may both surface meaningful new patterns; prevents premature closure; preserves quality control via the gate.
* **Documents affected:** CONTEXT §4 Taxonomy Status, SIGNAL_DEFINITIONS.md, EVALUATION.md, NARRATIVE_ANALYSIS.md.
* **Follow-ons:** Candidate-Type Pool state machine (SIGNAL_DEFINITIONS.md), promotion workflow (EVALUATION.md), and production-use mechanics (NARRATIVE_ANALYSIS.md) are a three-way ownership split that must be maintained.

---

### DL-2026-006 — V1 is English-first

* **Status:** accepted
* **Question:** What language posture does v1 take?
* **Alternatives considered:** multilingual from day one (larger scope, harder training); English-first with multilingual as a deferred concern.
* **Decision:** V1 is English-first. Multilingual capability is not a v1 requirement.
* **Rationale:** Scope discipline; model-strategy complexity is bounded.
* **Documents affected:** CONTEXT §8 Language Posture, MODEL_STRATEGY.md.
* **Follow-ons:** Extension to other languages is a deferred concern for future model strategy work.

---

### DL-2026-007 — Thin-history posture: reliability over coverage

* **Status:** accepted
* **Question:** How does the system behave for Entities with limited Historical Depth?
* **Alternatives considered:** emit Signals opportunistically (high coverage, high false-positive risk); require a minimum Baseline before emitting any Signals (low coverage, high reliability); a policy that reduces Confidence, holds some Signals at Candidate, and requires minimum recurrence for Omission Events (middle ground).
* **Decision:** Reliability is preferred over coverage for thin-history Entities. Thin-History Policy shape is committed in SIGNAL_DEFINITIONS.md; numeric thresholds are owned by NARRATIVE_ANALYSIS.md.
* **Rationale:** Consistent with the False-Positive Posture; protects trust by not surfacing weak signals for thin-history entities.
* **Documents affected:** CONTEXT §8 Thin-History Posture, SIGNAL_DEFINITIONS.md Thin-History Policy, NARRATIVE_ANALYSIS.md.
* **Follow-ons:** Specific numeric thresholds per Signal type are empirical and owned by NARRATIVE_ANALYSIS.md.

---

### DL-2026-008 — False-positive posture: false positives are costlier than false negatives in early development

* **Status:** accepted
* **Question:** How should the system tune the tradeoff between false positives and false negatives?
* **Alternatives considered:** equal weighting (implicit-default, ignores trust dynamics); false-negative intolerance (high coverage, low precision); false-positive intolerance in early development (reduced coverage, higher precision).
* **Decision:** In early development, false positives carry greater cost to user trust than false negatives. The posture may evolve as the system matures.
* **Rationale:** User trust is the project's most valuable asset; a low-quality signal destroys trust faster than an absent signal. Absence of a Signal is not absence of risk (stated in ETHICS_AND_LIMITATIONS.md).
* **Documents affected:** CONTEXT §14 False-Positive Posture, SIGNAL_DEFINITIONS.md, NARRATIVE_ANALYSIS.md, EVALUATION.md, USER_EXPERIENCE.md, ETHICS_AND_LIMITATIONS.md.
* **Follow-ons:** EVALUATION.md operationalizes this across three surfaces (emission, surfacing, presentation).

---

### DL-2026-009 — Data acquisition is an independent workstream with its own document

* **Status:** accepted
* **Question:** Does the project treat data acquisition as part of ingestion, or as its own concern?
* **Alternatives considered:** fold acquisition into INGESTION_SPEC.md (simpler, but conflates sourcing with parsing and couples licensing with technical handling); separate DATA_ACQUISITION.md owning sourcing, licensing, and historical-depth posture.
* **Decision:** DATA_ACQUISITION.md is a dedicated document. Boundary: DATA_ACQUISITION.md owns where documents come from; INGESTION_SPEC.md owns what happens once a document has arrived.
* **Rationale:** Acquisition is on the v1 critical path, interacts with Licensing Posture compatibility (which binds model training), and is non-trivial enough to warrant a named owner. Folding it into ingestion would couple licensing-sensitive decisions with parsing details.
* **Documents affected:** DATA_ACQUISITION.md, INGESTION_SPEC.md, DATA_GOVERNANCE.md, MODEL_STRATEGY.md, CONTEXT §8, ARCHITECTURE.md.
* **Follow-ons:** Licensing Posture classification and Posture Carrying become load-bearing across the data pipeline.

---

### DL-2026-010 — Operating posture is deliberate / batch / on-demand, not real-time streaming

* **Status:** accepted
* **Question:** Does the system operate as a real-time stream, a scheduled batch, an on-demand service, or some combination?
* **Alternatives considered:** real-time streaming (low-latency, high-infrastructure-cost, mismatched with analytical deliberation); deliberate/batch/on-demand (lower cost, compatible with low-capital posture, matches the analytical-depth positioning).
* **Decision:** V1 operates in a deliberate / batch / on-demand posture. Real-time streaming is explicitly out of v1.
* **Rationale:** Consistent with the low-capital posture and with the depth-oriented user experience. Real-time behavior implies alerting and dashboard-style aggregation, both deferred.
* **Documents affected:** ARCHITECTURE.md Operating Posture, SCOPE Scope Boundaries, SCOPE Non-Goals, EVENTS_AND_PIPELINES.md, USER_EXPERIENCE.md.
* **Follow-ons:** None.

---

### DL-2026-011 — Pipeline Version is the named mechanism for re-derivability

* **Status:** accepted
* **Question:** Re-derivability is committed as an invariant in DATA_MODEL.md, but what is the *named* mechanism by which historical replay is reproducible?
* **Alternatives considered:** leave the mechanism implicit (vulnerable to drift); commit to per-artifact DerivationRun provenance alone (insufficient for collection-level reproducibility); introduce Pipeline Version as a pin across DerivationRuns.
* **Decision:** Pipeline Version is the canonical mechanism. A Pipeline Version pins a set of DerivationRuns; given a Pipeline Version and Raw inputs, the system can reproduce the derived state.
* **Rationale:** Makes re-derivability operationally concrete; supports Historical Replay (EXPERIMENTATION.md) and As-Of Views (USER_EXPERIENCE.md, API_SPEC.md).
* **Documents affected:** CONTEXT §11, EVENTS_AND_PIPELINES.md, DATA_MODEL.md, EXPERIMENTATION.md, DATA_GOVERNANCE.md.
* **Follow-ons:** Pipeline Version promotion workflow mechanics are owned by EVENTS_AND_PIPELINES.md (pipeline side) and DATA_GOVERNANCE.md (governance side).

---

### DL-2026-012 — V1 user surface is single-user, entity-centric, pull-based

* **Status:** accepted
* **Question:** What are the user-surface shape commitments for v1?
* **Alternatives considered:** multi-user collaborative workspace (out of scope for v1 capacity); single-user, entity-centric, depth-oriented surface; alerting-dashboard posture (conflicts with deliberation).
* **Decision:** V1 is single-user, entity-centric, and pull-based. Alerting, push notifications, and dashboard-style aggregated views are deferred. No entity-level aggregate scores are emitted.
* **Rationale:** Matches the audience baseline (depth-oriented analysts), the low-capital posture, and the structural skepticism commitment.
* **Documents affected:** CONTEXT §17, SCOPE Non-Goals, SCOPE Insight Presentation, USER_EXPERIENCE.md, API_SPEC.md.
* **Follow-ons:** Collaborative, multi-user, and portfolio-aware surfaces are long-term expansion possibilities.

---

## Pending Cross-Document Coordination

The following are tensions flagged across Wave 2 clusters that affect multiple documents. They are not yet resolved as decisions but are tracked so they do not get lost.

* **Non-determinism in learned DerivationRuns versus the re-derivability invariant.** MODEL_STRATEGY.md owns tolerance specifications; TESTING_STRATEGY.md enforces the invariant up to those tolerances.
* **Evidence & Provenance Store atomic-write contracts** when the underlying storage is not transactionally homogeneous. Inherited by downstream infrastructure work.
* **Signal Evidence tombstoning vs. the mandatory-Evidence rule** in SIGNAL_DEFINITIONS.md. A Signal whose Evidence access is tombstoned remains a record; its lifecycle transition is a joint SIGNAL_DEFINITIONS.md / NARRATIVE_ANALYSIS.md concern.
* **Historical embeddings under deprecated Representation DerivationRuns.** Retention vs. re-embedding on demand; SEARCH_AND_RETRIEVAL.md and DATA_GOVERNANCE.md co-own resolution.
* **Reviewer capacity contention** between production evaluation and experimentation. Arbitration mechanism is deferred to downstream operational work.
* **Narrow Graduation and Entity-scoped DerivationRuns.** Whether the Fusion Engine's DerivationRun set may vary by Entity is a downstream ARCHITECTURE.md concern if pressure emerges.
* **Probationary promotion for Candidate Types.** Open question in NARRATIVE_ANALYSIS.md and EVALUATION.md about whether a probationary state belongs between Candidate-Type-Pool "hold" and full promotion.
* **Persistent Degraded Mode and promotion.** Whether persistent Degraded Mode should gate Candidate→Surfaced promotion is an open NARRATIVE_ANALYSIS.md question.
* **External-LLM commoditization of Basis-and-Evidence provenance.** If competitive landscape shifts such that external LLM assistants offer comparable provenance, the distinctness account in COMPETITIVE_LANDSCAPE.md will need sharpening.

---

## Relationship To Other Documents

* CONTEXT.md, SCOPE.md, VISION.md, ASSUMPTIONS.md, DOMAIN_GLOSSARY.md — these documents are often the ones updated in response to a decision here.
* RESEARCH_NOTES.md — tracks open research questions, some of which become decisions recorded here.
* ROADMAP.md — its phase gates may be informed by decisions here.
* All Wave 2 documents — decisions here constrain their design space.
