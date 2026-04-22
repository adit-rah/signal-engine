# RESEARCH_NOTES.md

## Purpose Of This Document

RESEARCH_NOTES.md is the living home for open analytical and research questions, working hypotheses, experiment logs, and findings that inform — but are not themselves — architectural or operational decisions.

It is a register and a template, not a treatise. Entries accumulate over time. The document is designed to remain coherent as it grows, without being restructured.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Decisions informed by entries here are recorded in DECISION_LOG.md once that document is created (see Linking Research Notes To Decisions, below).

---

## Status

This document is deliberately a living artifact. It is not a finished research report. It does not attempt to answer its own questions at the time of writing; it structures how those questions are recorded, worked, and eventually resolved or deliberately held open.

An entry that has not been worked is not a defect. An entry whose resolution would close a deliberately open question is a defect; see What Stays Open By Design.

---

## How To Read This Document

* the first section is the template (Anatomy Of A Research Note) — the shape every entry takes
* the second section is the Open Questions Register — the starting set of questions drawn from [CONTEXT.md](./CONTEXT.md) §15, [SCOPE.md](./SCOPE.md) Open Questions, and tensions surfaced elsewhere
* the third section lays out the three entry templates (Hypothesis, Experiment, Finding)
* the fourth section is What Stays Open By Design — questions the project deliberately does not close
* the closing sections describe how entries link to decisions and to neighboring documents
* the document is meant to be skimmed for the entry you need, not read end-to-end

---

## Relationship To Neighboring Documents

RESEARCH_NOTES.md sits among several documents with adjacent concerns. The boundaries matter; overlap causes drift.

* **[CONTEXT.md](./CONTEXT.md) §15** lists open questions at the philosophical and conceptual level. Those questions seed the register here. CONTEXT.md does not host research entries; it hosts the project's posture toward those questions.
* **[SCOPE.md](./SCOPE.md) Open Questions** lists capability-level questions. Those questions seed the register here. SCOPE.md does not resolve them; it records their status.
* **[ASSUMPTIONS.md](./ASSUMPTIONS.md)** names the beliefs the project carries. Research that challenges an assumption should cite the assumption identifier (U1, D4, H4, etc.); if a research entry disconfirms an assumption, the finding updates [ASSUMPTIONS.md](./ASSUMPTIONS.md).
* **EXPERIMENTATION.md** (not yet written) will own experimentation *methodology* — how experiments are designed, run, and validated. This document owns *records of what was asked and found*. The boundary is: methodology in EXPERIMENTATION.md, findings and open threads here.
* **EVALUATION.md** (not yet written) will own evaluation methodology for Signals. Research that concerns evaluation of individual Signal types, reviewer calibration, or the evaluation harness itself may be recorded here and inform EVALUATION.md.
* **NARRATIVE_ANALYSIS.md** (not yet written) will own analytical specifics — Baseline construction, thresholds, ranking. Research that bears on those specifics is recorded here; once decisions are made, they move to NARRATIVE_ANALYSIS.md and DECISION_LOG.md.
* **MODEL_STRATEGY.md** (not yet written) will own model specifics. Research on representation, learned analysis, and fusion mechanics is recorded here; decisions move there.
* **DECISION_LOG.md** (not yet written) is expected to host the project's record of what was decided, why, and which research notes informed the decision. Every research note that eventually resolves into a decision should link to the corresponding entry in DECISION_LOG.md when that entry exists.

The absence of DECISION_LOG.md, EXPERIMENTATION.md, and EVALUATION.md at the time of writing is noted. Entries here may cite them as future owners.

---

## Boundary With EXPERIMENTATION.md

Research-note discipline and experimentation discipline overlap but are not the same.

* an **experiment** — in the sense EXPERIMENTATION.md will own — is a structured procedure with pre-registered design, defined measurements, and a controlled execution. EXPERIMENTATION.md will specify how such experiments are designed and run.
* a **research note** — in the sense this document owns — is a recording artifact. It may describe an experiment, but it may also describe a reading, a thought experiment, a comparative study, a review of prior work, or a conversation that produced a direction.

A single experiment is typically represented here by a Hypothesis entry, one or more Experiment entries that reference it, and one or more Finding entries that reference the experiments. The methodology governing how each experiment was constructed lives in EXPERIMENTATION.md; the record of what was asked and learned lives here.

If an entry in this document would only be meaningful if the reader also consulted the methodology — for example, a finding whose interpretation depends on how the sample was drawn — the entry must cite the relevant EXPERIMENTATION.md section explicitly.

---

## Anatomy Of A Research Note

Every entry, regardless of kind, has the fields below. Kinds differ in which fields are load-bearing; all fields are present.

### Identifier

A stable, human-readable label. Recommended form: `RN-<kind>-<area>-<short-slug>`, where `<kind>` is `H` (Hypothesis), `E` (Experiment), `F` (Finding), or `Q` (Open Question). Example: `RN-H-fusion-basis-disagreement-signal`.

Identifiers do not need to be dense; they need to be stable and unique.

### Status

One of:

* **open** — entered, not yet worked in a load-bearing way
* **in progress** — being worked; no conclusion yet
* **resolved** — a finding has been recorded; entry is closed to further work under its current identifier
* **superseded** — a subsequent entry replaces this one; carries a lineage reference to the replacement
* **held open** — deliberately not resolved; see What Stays Open By Design

A resolved entry is not deleted. Its resolution is recorded as a Finding entry that references the original.

### Kind

One of: Hypothesis, Experiment, Finding, Open Question.

Open Questions are recorded without being worked; they are the register's starting posture. Hypotheses are proposals to be tested. Experiments record structured attempts. Findings record what was learned.

### Question Or Claim

The question (for Open Questions), the claim (for Hypotheses), the procedure summary (for Experiments), or the conclusion (for Findings), stated in one or two sentences.

### Motivation

Why the entry exists. What would change if it were resolved. Which CONTEXT, SCOPE, VISION, ASSUMPTIONS, SIGNAL_DEFINITIONS, ARCHITECTURE, or DATA_MODEL reference it is grounded in.

### Inputs And Dependencies

Assumption identifiers the entry depends on (U1, D4, H4, etc.). Referenced Signal types, components, or data-model elements. Upstream research notes by identifier.

### Approach Sketch

How the question might be approached. For Hypotheses: what would count as confirmation or disconfirmation. For Experiments: the procedure (deferring methodological detail to EXPERIMENTATION.md if written). For Findings: how the finding was arrived at.

This is not a methodology specification. It is enough detail for a future contributor to pick up the thread.

### Observations And Findings To Date

What has been learned, if anything. Partial observations are encouraged; absence of observation is recorded as such.

### Linked Decisions

References to DECISION_LOG.md entries, once that document exists. Entries may name a *pending* decision (for example, "pending fusion-layer conflict-resolution decision") before DECISION_LOG.md exists, with a note that the linkage will formalize later.

### Updates To Upstream Documents

If the entry, when resolved, should update CONTEXT.md, SCOPE.md, ASSUMPTIONS.md, VISION.md, a glossary term, or a downstream document, that update is named here. A resolved entry whose upstream update has not been propagated is incomplete.

### Deferrals

Aspects of the entry that are deliberately not addressed. Each deferral names its downstream owner.

### Notes

Free-form. Additional context, conversations, pointers to external reading, analyst disagreements. Not load-bearing for the entry's resolution but useful for future readers.

---

## The Open Questions Register

The register below is the starting set of open questions carried into the project. Entries are structured as Open Question entries in the kind sense above. Each cites the document and section that hosts the original formulation.

The register is not exhaustive. Contributors add entries as new questions surface. An Open Question entry that becomes the object of a Hypothesis is referenced from the Hypothesis rather than being deleted.

Entries are grouped by analytical area. Grouping is descriptive and may grow over time.

---

### Area: Signal Semantics

**RN-Q-signals-meaningful-change**
What is the operational definition of a meaningful signal, as distinct from detectable change that is not meaningful?
Source: CONTEXT §15; restated in SCOPE Open Questions under "signal ranking and prioritization methodology".
Bearing: every Signal type's strong-vs-weak criteria in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) depend on a shared notion of meaningfulness. Thresholds are deferred to NARRATIVE_ANALYSIS.md, but the question of what "meaningful" means conceptually sits here.

**RN-Q-signals-importance-ranking**
How should Signal importance be ranked across types and across Entities?
Source: CONTEXT §15; SCOPE Open Questions.
Bearing: [ARCHITECTURE.md](./ARCHITECTURE.md)'s Ranking & Surfacing component owns the implementation; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) states that Strength is type-relative and explicitly not a cross-type ranking value. A cross-type ranking method must bridge that gap.

**RN-Q-signals-uncertainty-communication**
How should uncertainty in a Signal be communicated to users honestly without devaluing strong Signals?
Source: CONTEXT §15.
Bearing: [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) separates Strength from Confidence at the data level; USER_EXPERIENCE.md will own the surface; the research question is how each Confidence representation reads to a human in practice.

---

### Area: Fusion Layer

**RN-Q-fusion-heuristic-ml-reconciliation**
How should the Fusion Engine reconcile conflicting heuristic and learned outputs for a given candidate Signal?
Source: CONTEXT §15; framed as a hard design problem in CONTEXT §3.2.C and [ARCHITECTURE.md](./ARCHITECTURE.md).
Bearing: the Fusion Engine's conflict-resolution mechanics are deferred to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; the research note records the question and the constraints it must satisfy (preserve Basis, honor structured skepticism, remain traceable).

**RN-Q-fusion-balance-per-signal-type**
What is the right balance between heuristic rigor and ML generalization per Signal type?
Source: CONTEXT §15.
Bearing: the five confirmed types ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) differ in how amenable they are to heuristic description. A per-type balance may differ. The register holds the question; resolution will arrive type by type.

**RN-Q-fusion-basis-disagreement-representation**
How should Basis Disagreement be detected, represented, and resolved?
Source: [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) marks this deferred to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) names it as an input to Confidence.
Bearing: Confidence's construction depends on a decision about representation. The research note holds the question and its downstream implications.

---

### Area: Baselines And Thin History

**RN-Q-baselines-construction-method**
By what method are Baselines constructed, such that the resulting Baseline supports Narrative Drift, Confidence Shift, and Structural Anomaly detection at the quality level this project intends?
Source: [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) defers this to NARRATIVE_ANALYSIS.md and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); [ARCHITECTURE.md](./ARCHITECTURE.md)'s Baseline Maintenance owns it structurally.
Bearing: a significant portion of Signal quality flows from Baseline construction. The question is open at the analytical level.

**RN-Q-baselines-thinness-thresholds**
What threshold on Baseline thinness should trigger Confidence reduction, candidate-only emission, or non-emission?
Source: [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Thin-History Policy commits the shape; thresholds are deferred to NARRATIVE_ANALYSIS.md.
Bearing: a policy without thresholds is directional. The thresholds themselves are research-driven.

**RN-Q-baselines-versioning-across-method-change**
How are Baselines versioned when the Baseline construction method itself changes, such that historical comparisons remain interpretable?
Source: [ARCHITECTURE.md](./ARCHITECTURE.md) Open Structural Questions.
Bearing: re-derivation under new logic produces new DerivationRuns. The question is how Baseline valid-time series interact with Baseline-method valid-time.

---

### Area: Signal Taxonomy Extension

**RN-Q-taxonomy-distinctness-criterion**
What criterion establishes that a candidate new Signal type (whether research-driven or discovery-driven) is distinct from the existing taxonomy and is not a rediscovery under a new name?
Source: [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension names the Candidate-Type Pool and defers promotion workflow to EVALUATION.md. The distinctness criterion is a research concern.
Bearing: a taxonomy that admits redundancy erodes the clarity of each type's operational definition.

**RN-Q-taxonomy-discovery-driven-review-criteria**
What review criteria should govern promotion of a discovery-driven candidate type (CONTEXT §5.4)?
Source: CONTEXT §4 Taxonomy Status; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Discovery-Driven Extension.
Bearing: discovery-driven proposals arrive with less theoretical grounding than research-driven proposals. Review must be rigorous enough to prevent false types without being so strict that real types are rejected.

---

### Area: Cross-Signal Interactions

**RN-Q-cross-signal-interaction-modeling**
To what extent, and how, should cross-signal interactions — for example, a Confidence Shift co-occurring with an Omission Event — be modeled beyond the Fusion Engine's per-Signal scope?
Source: [ASSUMPTIONS.md](./ASSUMPTIONS.md) S7; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Deferred Decisions ("cross-signal interaction modeling — NARRATIVE_ANALYSIS.md").
Bearing: the Fusion Engine integrates heuristic and learned evidence into a single Signal; it does not, by current contract, reason across Signals. Whether a higher-order analytical layer is warranted is open.

---

### Area: Evaluation

**RN-Q-evaluation-ground-truth-strategy**
In the absence of clean ground truth for many Signal types (CONTEXT §13.3), what evaluation strategy beyond human review meaningfully advances the project's confidence in Signal quality?
Source: CONTEXT §14; SCOPE Open Questions.
Bearing: evaluation harness evolution (ASSUMPTIONS T4) depends on resolving this question without falling into ground-truth theater (VISION.md Failure Modes).

**RN-Q-evaluation-reviewer-calibration**
If expert human reviewers disagree systematically on what counts as a strong Signal, how is reviewer calibration performed?
Source: [ASSUMPTIONS.md](./ASSUMPTIONS.md) S4, X5; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Flagged For Downstream Ownership names reviewer calibration as a concern for the evaluation owner downstream.
Bearing: reliance on human evaluation requires a procedure for handling disagreement that is not itself a source of false comfort.

**RN-Q-evaluation-training-data-requirements**
What data is required to train or fine-tune the in-house representation model to acceptable signal quality?
Source: CONTEXT §15.
Bearing: [ASSUMPTIONS.md](./ASSUMPTIONS.md) H2, H3, H5 all rest on this being feasible at the chosen scale. Research on the dependency is load-bearing for model strategy.

---

### Area: Data Acquisition

**RN-Q-acquisition-historical-depth-feasibility**
To what degree is earnings call transcript data acquirable with sufficient historical depth, coverage, and licensing for training and comparative analysis?
Source: [SCOPE.md](./SCOPE.md) Open Questions; [ASSUMPTIONS.md](./ASSUMPTIONS.md) D1, D6, T5.
Bearing: a large negative finding on acquisition feasibility would reshape the project's operating plan. The question is open.

---

### Area: Operating Mode

**RN-Q-operating-mode-re-derivation-scheduling**
How is re-derivation scheduled and throttled under the low-capital constraint, without violating the re-derivability invariant?
Source: [ARCHITECTURE.md](./ARCHITECTURE.md) Open Structural Questions.
Bearing: the data model treats derived artifacts as re-derivable; operational scheduling of re-derivation interacts with cost.

---

### Area: Cross-Source Contradiction (Deferred Domain)

**RN-Q-cross-source-contradiction-deferred-design**
When a second Data Domain is introduced (v2+), how does cross-source Contradiction Event detection interact with the single-domain Baselines established for earnings call transcripts?
Source: [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Contradiction Event operational definition; SCOPE Deferred.
Bearing: a deferred-but-anticipated question; recorded here so it is not a surprise at the point of domain expansion.

---

## Hypothesis Entry Template

A Hypothesis is a claim the project proposes to test. Entries use the Research Note anatomy above with the following emphases.

```
Identifier:    RN-H-<area>-<slug>
Status:        open | in progress | resolved | superseded | held open
Kind:          Hypothesis
Claim:         <one or two sentences: the claim being tested>
Motivation:    <why it matters; which upstream document raised it>
Inputs And Dependencies:
  - Assumption identifiers (e.g. ASSUMPTIONS D4, H3)
  - Signal types, components, or data-model elements referenced
  - Upstream research notes by identifier
Approach Sketch:
  <how the claim might be tested; what would count as confirmation
   or disconfirmation; deferral notes to EXPERIMENTATION.md where
   methodology belongs there>
Observations And Findings To Date:
  <partial observations; null observations; absence recorded>
Linked Decisions:
  <pending or actual DECISION_LOG.md entries>
Updates To Upstream Documents:
  <CONTEXT, SCOPE, ASSUMPTIONS, VISION, or glossary updates that
   would follow from confirmation/disconfirmation>
Deferrals:
  <aspects not addressed; downstream owner named>
Notes:
  <free-form>
```

A Hypothesis entry without a clear disconfirmation condition is incomplete. If no observation would refute the claim, the entry is a preference or a principle; it belongs elsewhere.

---

## Experiment Entry Template

An Experiment entry records a structured attempt to advance a Hypothesis or characterize a phenomenon. Methodology specifics live in EXPERIMENTATION.md (future); this entry captures what was done and what was observed.

```
Identifier:    RN-E-<area>-<slug>
Status:        open | in progress | resolved | superseded | held open
Kind:          Experiment
Procedure Summary:
  <one paragraph describing the attempt>
Hypothesis Reference:
  <RN-H-... entry this experiment bears on, if any>
Methodology Reference:
  <EXPERIMENTATION.md section, when that document exists>
Inputs And Dependencies:
  - data used (Documents, Entities, historical depth)
  - components invoked
  - DerivationRuns referenced
Observations:
  <what was observed; null results recorded>
Interpretation:
  <how the observations bear on the Hypothesis; limits of
   interpretation; confounds>
Linked Decisions:
  <pending or actual DECISION_LOG.md entries>
Updates To Upstream Documents:
  <document updates to propagate, if any>
Deferrals:
  <aspects not addressed>
Notes:
  <free-form>
```

An Experiment entry that draws a conclusion stronger than its procedure supports is a defect. Experiments are honest about confounds and limits; findings that require more work are labeled as such.

---

## Finding Entry Template

A Finding entry records a conclusion drawn from one or more experiments, a reading of prior work, a conceptual analysis, or a synthesis of observations accumulated over time.

```
Identifier:    RN-F-<area>-<slug>
Status:        resolved | superseded | held open
Kind:          Finding
Claim:         <the finding, stated as conservatively as the evidence
                supports>
Basis:         <the entries (RN-H, RN-E, prior RN-F) and reasoning
                that support the claim>
Confidence Of The Finding:
  <the entry's own estimate of how certain the finding is;
   analogous in spirit to Signal Confidence but applied to the
   research note>
Scope Of Applicability:
  <where the finding holds; where it is known not to hold>
Counter-Evidence:
  <known observations that complicate the finding>
Linked Decisions:
  <DECISION_LOG.md entries the finding informed, or is expected to>
Updates To Upstream Documents:
  <document updates to propagate, if any; whether propagated yet>
Deferrals:
  <aspects not addressed>
Notes:
  <free-form>
```

A Finding entry claiming more than its Basis supports is retired and replaced. Retiring a Finding is expressed as a new entry that references the original, analogous to the Signal retirement posture in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

---

## What Stays Open By Design

Some questions are deliberately held open. Closing them prematurely would either sacrifice honesty or pre-commit the project to a position it does not yet have grounds to take. These are recorded here so a contributor cannot unintentionally resolve them.

* **The absence of clean ground truth for many Signal types** — CONTEXT §13.3 treats this as a central challenge. Entries that propose to "solve" the ground-truth problem by proxy labels, synthetic comparisons, or narrow benchmarks must be marked held open unless they genuinely advance the problem rather than merely dress it up.
* **The final shape of "meaningful"** — a working definition per Signal type is expected; a global, definitive answer is not. Attempts to collapse meaning into a single metric violate structured skepticism (CONTEXT §3.4).
* **The fusion layer's final conflict-resolution strategy** — CONTEXT §3.2.C marks the fusion layer as deliberately under-specified and treats it as a hard design problem. Research entries may sharpen the question; they should not attempt a total resolution without architectural grounding.
* **The evaluation harness's final form** — CONTEXT §14 explicitly frames evaluation as an evolving artifact; freezing it prematurely is a failure mode (VISION.md: Drift Toward Ground-Truth Theater).
* **The relationship between Signals and market behavior** — market-correlation study is exploratory and deferred ([SCOPE.md](./SCOPE.md) Intelligence Concepts; Non-Goals). Research entries on this topic must not drift toward prediction framing ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions).
* **The signal taxonomy's eventual final shape** — CONTEXT §4 treats the taxonomy as extensible; [ASSUMPTIONS.md](./ASSUMPTIONS.md) N4 makes the non-assumption explicit. Research entries may propose extensions; they should not claim the taxonomy is complete.

When an entry touches one of these areas, its Status field begins at `held open` by default, and any transition to `resolved` requires explicit justification in the Finding.

---

## Linking Research Notes To Decisions

Every research note that materially informs a decision should link to the corresponding entry in DECISION_LOG.md once that document exists. Until then, the Linked Decisions field carries a plain-language description of the pending decision and the downstream document that will host it.

Recommended practice, once DECISION_LOG.md is in place:

* every decision recorded in DECISION_LOG.md cites the research note identifiers that informed it
* every resolved research note cites the decision that followed from it
* decisions that contradict a prior research note cite the reason and trigger a note supersession

The bidirectional linkage is the mechanism by which a reader can trace any architectural or analytical decision back to the research that supported it, and vice versa. This is the research-layer analogue of the Basis chain required at the Signal level by CONTEXT §3.3.

Creating DECISION_LOG.md is flagged as a pending project need. This document does not create it; it assumes it will arrive and specifies how the two documents will interact.

---

## Areas Likely To Accumulate Entries

Based on the register above and the deferred decisions named in the Wave 0 and Wave 1 documents, the following areas are expected to generate sustained research activity. The list is descriptive — a contributor is welcome to open an entry in an area not listed.

* Baseline construction methodology and thin-history thresholds
* Fusion Engine conflict-resolution strategies and Confidence construction
* Training data requirements and representation-model quality
* Cross-signal interaction modeling
* Candidate-Type Pool review criteria for discovery-driven extensions
* Evaluation harness evolution and reviewer calibration
* Data acquisition feasibility and licensing posture
* Commentary generation grounded in Basis and Evidence without sacrificing traceability
* Re-derivation scheduling under the low-capital constraint

---

## Extensibility Of This Document

The document is extensible without restructuring. New entries are appended to the relevant area of the Open Questions Register or, once worked, live as Hypothesis, Experiment, or Finding entries indexed by identifier.

New areas are added when an entry does not fit an existing area and a new grouping is warranted. Area additions are a low-friction operation; they do not require document-level revision.

If the register grows large enough that the document becomes unreadable as a single file, splitting by area is expected. Each split file inherits the template and the discipline of this document; the document as a whole remains the authoritative template.

---

## What This Document Is Not

* it is not a finished research paper
* it is not a methodology specification (that is EXPERIMENTATION.md)
* it is not a record of decisions (that is DECISION_LOG.md)
* it is not an evaluation report (that is EVALUATION.md)
* it is not an architectural specification
* it is not a user-facing document; entries may be technical, partial, or unresolved

The discipline of the document is that it remains honest about what is known, what is tried, and what is held open. Losing that honesty is the failure mode most relevant to this document's integrity.

---

## Deferred To Other Documents

* specific experiment methodology — EXPERIMENTATION.md
* specific evaluation methodology — EVALUATION.md
* specific Baseline construction methods and thresholds — NARRATIVE_ANALYSIS.md
* specific model architectures, training data, fusion mechanics — MODEL_STRATEGY.md
* specific ranking algorithms — NARRATIVE_ANALYSIS.md and EVALUATION.md
* specific user-facing presentation of research results — out of scope entirely unless and until a user-facing research surface is contemplated

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; their open-questions sections seed this register.
* [VISION.md](./VISION.md) supplies the principles under which research is pursued — especially Restraint Beats Coverage, Epistemic Honesty Over Confidence, and Structure Anchors Learning.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies the identifiers (U, D, S, H, T, E, X, N) that research entries cite.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) supplies the vocabulary; the Flagged For Downstream Ownership section names many of the questions recorded here.
* [ARCHITECTURE.md](./ARCHITECTURE.md) supplies the Open Structural Questions that map onto research areas here.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) supplies the Deferred Decisions that map onto research areas here.
* DECISION_LOG.md (future) is expected to be the bidirectional linkage partner for this document; every load-bearing resolution here should surface there.
