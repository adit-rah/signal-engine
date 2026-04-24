# ROADMAP.md

## Purpose Of This Document

ROADMAP.md defines the phased evolution of the system from its current pre-development state through subsequent horizons. Each phase is described qualitatively — by character, entry condition, exit condition, and what must hold across it — not by date, resource, or feature list.

This is a roadmap in the sense of direction and readiness, not in the sense of calendar-committed delivery. It is intended to be read alongside [SCOPE.md](./SCOPE.md), which commits what v1 is, and [VISION.md](./VISION.md), which commits what the project is working toward.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). V1 scope is defined by [SCOPE.md](./SCOPE.md) and is not renegotiated here.

---

## Status

The project is presently in the pre-development phase described below as Phase 0. No code or operational infrastructure exists; the Wave 0 and Wave 1 documents constitute the current artifact set.

---

## How To Read This Document

* phases are defined by character — the kind of work that belongs to the phase and the posture the project holds during it
* each phase has entry criteria, exit criteria, and anti-criteria (the pressures that must *not* move the project forward into the next phase)
* no phase has a calendar commitment, a resourcing commitment, or a fixed feature list
* v1 exit criteria are expressed in terms of [SCOPE.md](./SCOPE.md)'s In Scope list; the roadmap does not renegotiate what v1 is
* long-horizon phases remain horizons — they describe direction, not plans
* [VISION.md](./VISION.md) principles are named explicitly at every phase boundary; preservation of those principles is a first-class criterion for advancing phases

---

## Guiding Commitments Across All Phases

These commitments hold across every phase. They are inherited from [CONTEXT.md](./CONTEXT.md) and [VISION.md](./VISION.md) and are invariant with respect to phase progression.

* **Meaning Is Temporal** (CONTEXT §2; VISION.md). The project's primary analytical unit is change in narrative over time.
* **Structure Anchors Learning** (CONTEXT §7; VISION.md). Heuristics are scaffolding for learned components; they are never relegated to fallback logic.
* **Explainability Is A First-Class Property** (CONTEXT §3.3; VISION.md). Every output is traceable; no phase introduces an untraceable output surface.
* **Ownership Over Convenience** (CONTEXT §6; VISION.md). In-house models; external LLM APIs remain excluded from critical paths.
* **Restraint Beats Coverage** (VISION.md). Fewer, higher-quality Signals beat many low-quality Signals. Phase progression does not trade restraint for coverage.
* **Human Judgment Is The Final Authority** (VISION.md). The system augments; the user decides. No phase promotes the system to autonomous action.
* **Epistemic Honesty Over Confidence** (VISION.md). Uncertainty is communicated honestly; Confidence is always distinct from Strength.
* **Low-Capital Posture** ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint; [ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5). Phase progression does not depend on scaling infrastructure beyond what signal quality justifies.

These commitments are the shape of the project across time. A phase that can only be entered by weakening one of them is not a phase of this project.

---

## Phase Structure

Every phase below is described by the same structural fields.

* **Character** — the qualitative nature of the phase; what the project is doing during it
* **What Belongs To This Phase** — the work the phase contains
* **What Holds Across This Phase** — the invariants the phase cannot violate
* **Entry Criteria** — the qualitative conditions under which the phase begins
* **Exit Criteria** — the qualitative conditions under which the phase is considered complete
* **Anti-Criteria** — the pressures that do *not* move the phase forward

The fields are deliberately qualitative. Numeric thresholds, if any are warranted for exit criteria, are deferred to NARRATIVE_ANALYSIS.md, EVALUATION.md, or the relevant downstream document, and are not committed here.

---

## Phase 0: Conceptual Foundation

### Character

Documentation-first. The project establishes its conceptual foundation, scope, vocabulary, assumptions, architecture, data model, and Signal contract before writing production code. This is where the project is at the time of writing.

### What Belongs To This Phase

* authoring and stabilizing the Wave 0 and Wave 1 documents — [CONTEXT.md](./CONTEXT.md), [SCOPE.md](./SCOPE.md), [VISION.md](./VISION.md), [ASSUMPTIONS.md](./ASSUMPTIONS.md), [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)
* authoring the strategy-layer documents — [COMPETITIVE_LANDSCAPE.md](./COMPETITIVE_LANDSCAPE.md), [RESEARCH_NOTES.md](./RESEARCH_NOTES.md), and this document
* exploratory reading and prior-art review that feeds [RESEARCH_NOTES.md](./RESEARCH_NOTES.md)
* preliminary sketches of downstream documents (USER_EXPERIENCE.md, EVALUATION.md, MODEL_STRATEGY.md, NARRATIVE_ANALYSIS.md, DECISION_LOG.md, etc.) to mark territory

### What Holds Across This Phase

* no production code
* no commitments to storage technology, deployment topology, or model architecture
* the document set remains internally consistent; contradictions are resolved by reference to CONTEXT.md

### Entry Criteria

The phase is the default starting state. No explicit entry criterion.

### Exit Criteria

* the Wave 0 and Wave 1 documents exist, are mutually consistent, and name downstream owners for every deferred decision
* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are regarded as stable by the contributors who will depend on them
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) is sufficient that downstream documents can be written without redefining core vocabulary
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) establishes the Signal contract at a level of detail that the Fusion Engine and its neighbors can begin to be designed against
* [ARCHITECTURE.md](./ARCHITECTURE.md) and [DATA_MODEL.md](./DATA_MODEL.md) identify every component and entity necessary to implement the SCOPE.md In Scope list
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md)'s Open Questions Register is seeded from CONTEXT §15 and SCOPE Open Questions
* a decision-log discipline (DECISION_LOG.md) is named as a pending artifact, even if not yet authored

### Anti-Criteria

* premature commitment to technology, vendor, or model choices
* skipping the writing of a document because the team "knows what it means" — undocumented consensus does not hold across contributors
* resolving open questions in CONTEXT.md or SIGNAL_DEFINITIONS.md without explicit grounding in [RESEARCH_NOTES.md](./RESEARCH_NOTES.md)
* sprawling the Wave 0 document set into implementation detail it explicitly defers

---

## Phase 1: v1 Earnings-Call Core Build

### Character

The first phase in which production code and operational infrastructure come into existence. The project builds the minimum set of components necessary to ingest earnings call transcripts, produce Signals of the confirmed taxonomy, and surface them with Evidence and Basis. Narrowness is a design commitment, not a concession.

### What Belongs To This Phase

Scoped directly by [SCOPE.md](./SCOPE.md) In Scope (v1):

* ingestion of earnings call transcripts
* Entity identification and temporal document organization
* heuristic and ML-based analysis of the five confirmed Signal types — Narrative Drift, Confidence Shift, Omission Event, Contradiction Event, Structural Anomaly
* a Fusion Engine that combines heuristic and ML outputs into ranked, traceable Signals
* structured, explainable Signal outputs with evidence links
* human-reviewable Signal presentation
* an Evaluation Harness sufficient for early-stage structured human review

Structural concerns that must be in place by the end of the phase:

* the components named in [ARCHITECTURE.md](./ARCHITECTURE.md) exist at a level sufficient for the flow described there
* the conceptual entities in [DATA_MODEL.md](./DATA_MODEL.md) are represented operationally
* the Signal contract from [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) is honored on every emitted Signal
* the Thin-History Policy is in force

### What Holds Across This Phase

* no data domain other than earnings call transcripts is brought into production paths (SCOPE Initial Scope; CONTEXT §8)
* no Signal type outside the confirmed taxonomy is emitted in production, except through the Candidate-Type Pool review path (SIGNAL_DEFINITIONS Extension)
* no external large-language-model API is in the critical path (CONTEXT §6.1)
* every emitted Signal carries Basis and Evidence; no untraceable output is produced (CONTEXT §3.3)
* the low-capital posture is respected; features that multiply infrastructure cost without signal-quality gain are deferred ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint)
* false-positive posture is maintained — Confidence is reduced before Strength is inflated (ASSUMPTIONS S3; SIGNAL_DEFINITIONS Confidence And Uncertainty)

### Entry Criteria

* Phase 0 exit criteria are met
* the Fusion Engine's upstream and downstream contracts are specified clearly enough to begin implementation, even if internal conflict-resolution mechanics remain open ([ARCHITECTURE.md](./ARCHITECTURE.md) Fusion Engine)
* a provisional approach to Baseline construction exists — numeric thresholds may still be deferred to NARRATIVE_ANALYSIS.md, but the shape of the approach is articulated
* a provisional model-strategy sketch exists for the representation model and the task-specific models, scoped to the low-capital posture

### Exit Criteria

The phase exits when v1 exists, not when it is polished. "V1 exists" means:

* the SCOPE.md In Scope list is operationally realized, end to end
* earnings call transcripts can be ingested and Signals can be emitted, surfaced, and reviewed for at least one non-trivial set of Entities with Historical Depth sufficient to support the Baseline-dependent Signal types
* every emitted Signal honors the Signal contract — Basis, Evidence, Strength, Confidence, Lifecycle State, Commentary (SIGNAL_DEFINITIONS Anatomy)
* the Evaluation Harness is capable of sampling Signals for human review and recording reviewer feedback
* the system runs under the low-capital posture — it is feasible for the project's operating budget without external-dependency workarounds
* the system remains functional if external model providers are unavailable (ARCHITECTURE.md Model Ownership Posture)

Phase exit does not require that signal quality be validated — that is Phase 2's concern. Phase 1 exit is the existence of the system at a level sufficient for quality validation to begin.

### Anti-Criteria

* expanding into additional Data Domains because the earnings-call domain feels narrow — narrowness is the design (SCOPE Initial Scope)
* adding Signal types to meet user requests before the confirmed taxonomy is operating well
* introducing external LLM APIs into critical paths for convenience (CONTEXT §6.1)
* trading explainability for polish — no output surface skips Basis or Evidence
* premature user exposure that biases the project toward cosmetic improvement over structural correctness

---

## Phase 2: v1 Signal Quality Validation

### Character

Not a build phase. A validation phase. The project's disposition shifts from "does it work" to "is what it produces meaningful". This is the phase the SCOPE E1 assumption ([ASSUMPTIONS.md](./ASSUMPTIONS.md)) explicitly requires: signal quality on earnings call transcripts is validated before domain expansion is considered.

### What Belongs To This Phase

* structured human review of surfaced Signals across Entities with varying Historical Depth (CONTEXT §14; SIGNAL_DEFINITIONS Thin-History Policy)
* internal dogfooding on known historical narratives (CONTEXT §14)
* retrospective study of past narrative changes with known outcomes, under the discipline that observing a correlation is not predicting a future (CONTEXT §10; [SCOPE.md](./SCOPE.md) Intelligence Concepts — Market-Relevant Signal Correlation remains exploratory)
* reviewer calibration work — if persistent disagreement arises, it is treated as a first-class concern, not a dismissable inconvenience (ASSUMPTIONS X5; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Flagged For Downstream Ownership)
* maturation of the Evaluation Harness itself; it remains an evolving artifact (ASSUMPTIONS T4)
* working open [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) entries that bear on quality — Baseline construction, fusion mechanics, Confidence representation, Thin-History thresholds
* surfacing findings to NARRATIVE_ANALYSIS.md, MODEL_STRATEGY.md, and DECISION_LOG.md where applicable

### What Holds Across This Phase

* the SCOPE.md In Scope boundary holds — this is a quality phase, not a scope phase
* the false-positive posture holds (ASSUMPTIONS S3); phases do not drift toward coverage under quality pressure
* human judgment remains the authoritative evaluation mode; any quantitative metric is a supplement, not a replacement (CONTEXT §14)
* evaluation does not dress up subjective judgment as objective measurement (VISION.md: Drift Toward Ground-Truth Theater)
* absent ground truth is acknowledged rather than papered over (CONTEXT §13.3)

### Entry Criteria

* Phase 1 exit criteria are met
* the system has operated for long enough on a non-trivial Entity set to generate a reviewable corpus of emitted Signals
* the Evaluation Harness is in place and capable of structured sampling

### Exit Criteria

Phase 2 does not exit by meeting a single bar. Several qualitative conditions, held together, constitute exit:

* experienced financial readers consistently report that the system surfaces changes they would have missed or found slowly (VISION.md Qualitative Success)
* surfaced Signals are traceable to source Evidence without manual effort (VISION.md Qualitative Success)
* reviewers can articulate, in their own language, why a surfaced Signal is meaningful, and their articulations converge rather than diverge over time
* the system's failures are legible — explainable even when wrong (VISION.md Qualitative Success)
* the signal quality validation supports — rather than strains — the case for extending to a second Data Domain
* the residual weaknesses are known and named; the project is not exiting Phase 2 by pretending to see no issues

Phase 2 exit is a judgment, exercised by the contributors who must then commit to Phase 3's domain extension. It is not a checkbox.

### Anti-Criteria

* declaring quality validated because a user, an investor, or a benchmark asks for domain expansion
* declaring quality validated because a proxy metric clears a proxy threshold
* declaring quality validated because reviewer disagreement has been averaged into a single number
* declaring quality validated because the project feels ready to move on
* treating the absence of a complaint as the presence of quality

---

## Phase 3: First Data Domain Extension

### Character

The first phase in which the project broadens beyond earnings call transcripts. Extension is an architectural stress test; the system's extensibility posture (ARCHITECTURE.md Extensibility; DATA_MODEL.md Extensibility) is exercised for real for the first time.

Phase 3 is a validation that the Wave 0 documents were correct that additional domains could be added without restructuring. If they were not, the phase exposes the flaw.

### What Belongs To This Phase

* selecting a single additional Data Domain — chosen by readiness signals, not by this document
* adding a Document subtype and an ingestion path for the new domain (ARCHITECTURE.md Extensibility — new Document types; DATA_MODEL.md Extensibility)
* extending Entity Resolution, Baseline Maintenance, Heuristic Analysis, Representation, and Learned Analysis to the new domain without altering the Fusion Engine's contract
* adapting Signal emission and Evidence semantics to the new domain's Span precision ([DATA_MODEL.md](./DATA_MODEL.md) Span)
* exercising cross-source analysis in at least its single-domain-plus-one form — intra-Entity Contradiction Events across domains, Narrative Drift observed jointly across domains ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Contradiction Event; [SCOPE.md](./SCOPE.md) Cross-Source Analysis)

### What Holds Across This Phase

* earnings-call signal quality does not regress in pursuit of the extension
* the Fusion Engine's contract does not change shape; extensions attach as new feature contributors (ARCHITECTURE.md Extensibility)
* the Signal contract does not relax for the new domain (SIGNAL_DEFINITIONS Anatomy)
* the Thin-History Policy governs the new domain where applicable
* the low-capital posture holds — a second domain does not justify lifting the capital ceiling

### Entry Criteria

* Phase 2 exit criteria are met; signal quality on earnings call transcripts is validated
* the open questions most directly implicated by domain extension have been advanced in [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) — in particular, RN-Q-cross-source-contradiction-deferred-design is no longer purely theoretical
* the project has the operational capacity to integrate a second domain without starving the first

### Exit Criteria

* the additional domain is in production on the same contract terms as earnings call transcripts
* cross-domain analysis produces at least one Signal type whose quality meets the bar set in Phase 2
* the extensibility posture has been demonstrated — not claimed — for domain addition
* no component has required a contract-level change to accommodate the new domain; extensions are additive (DATA_MODEL.md Extensibility)

### Anti-Criteria

* picking a domain because it is trendy, not because the Phase 2 findings indicate readiness
* adding a second domain in parallel with the first because "more is better" — parallel addition fails the stress test the phase is designed to be
* letting the additional domain's specifics leak into the Fusion Engine's contract
* relaxing Evidence or Basis requirements for the new domain because the data model's representation is less mature there

---

## Phase 4: Analytical Deepening

### Character

A maturation phase rather than an expansion phase. With more than one Data Domain stably in production, the project deepens its analytical work. Cross-signal interactions, fusion-layer sophistication, and the Candidate-Type Pool's discovery-driven extensions all become first-order concerns.

This phase does not necessarily follow Phase 3 chronologically. It may interleave or run concurrently once Phase 3's extensibility stress test has concluded.

### What Belongs To This Phase

* cross-signal interaction modeling (ASSUMPTIONS S7; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Deferred Decisions; RN-Q-cross-signal-interaction-modeling)
* fusion-layer sophistication — the Fusion Engine's conflict-resolution, Confidence construction, and Basis Disagreement handling mature (VISION.md Likely Maturation; CONTEXT §3.2.C)
* exercising the Candidate-Type Pool for discovery-driven taxonomy extensions ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension); the first promoted discovery-driven types may emerge here, subject to Evaluation Harness review
* behavioral communication profiling at Entity and Speaker levels at higher fidelity (CONTEXT §5.3; [SCOPE.md](./SCOPE.md) Behavioral Communication Profiling)
* growth of a quantitative evaluation layer that supplements human judgment without displacing it (VISION.md Likely Maturation)
* deeper work on Baseline construction where Phase 2 surfaced limitations

### What Holds Across This Phase

* the confirmed initial taxonomy remains the backbone; new types are added through the extension pattern, not by dilution
* every emitted Signal still honors the Signal contract, including discovery-driven types once promoted
* evaluation's quantitative layer does not displace human judgment as the authoritative mode (CONTEXT §14; VISION.md)
* structured skepticism continues to shape every output (CONTEXT §3.4)
* in-house model ownership continues (CONTEXT §6)

### Entry Criteria

* the Fusion Engine's contract has proven stable across at least one domain extension
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) has accumulated findings that bear on cross-signal interactions and fusion sophistication
* the Evaluation Harness is mature enough to review discovery-driven candidate types without being overwhelmed

### Exit Criteria

Phase 4 is a maturation phase; it exits into steady-state operation rather than into a distinct subsequent phase.

* cross-signal interaction modeling exists and demonstrably improves signal quality in at least one area, without displacing single-Signal Basis
* the fusion layer's sophistication exceeds the provisional Phase 1 implementation in ways reviewers can articulate
* at least one discovery-driven Signal type has been promoted through the Candidate-Type Pool with full review, or the pool has been exercised enough to produce confidence that the review mechanics work
* the system's sense of itself is more opinionated as experience accumulates (VISION.md Likely Maturation); this opinion flows back into CONTEXT.md, SCOPE.md, and the glossary where appropriate

### Anti-Criteria

* deepening analytics in a way that creates untraceable outputs — sophistication that sacrifices interpretability is not an acceptable trade (CONTEXT §6.4; VISION.md)
* promoting discovery-driven types without human review (VISION.md Failure Modes; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension)
* collapsing multiple Signal types into one aggregate "super-signal" in pursuit of a cross-type ranking; Strength remains type-relative ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Anatomy)
* treating the quantitative evaluation layer as a replacement for human judgment

---

## Phase N: Long-Horizon Possibilities

### Character

A horizon, not a phase. The project sees possibilities it does not commit to. [SCOPE.md](./SCOPE.md) Long-Term Expansion Possibilities enumerates the areas; VISION.md's Likely Maturation frames their posture.

The project does not pre-commit to any of the possibilities below. Their inclusion here is to prevent them from being absent (and so forgotten) while also preventing them from being planned (and so falsely implied).

### What Might Eventually Belong Here

From [SCOPE.md](./SCOPE.md) Long-Term Expansion Possibilities and Deferred sections, any of the following may eventually be undertaken, subject to the phase-gating principles above:

* additional Data Domains beyond the second — filings, news, press releases, interviews, macro commentary, analyst commentary
* real-time or streaming analysis (currently deferred)
* multi-modal inputs (currently deferred)
* personalized or portfolio-aware workflows (currently deferred)
* collaborative / multi-user research tooling (currently deferred)
* industry-wide narrative tracking (currently horizon)
* macroeconomic narrative monitoring (currently horizon)
* event-driven analysis systems (currently horizon)

Any of these, if undertaken, passes through the same phase-gating shape: entry conditions grounded in validated signal quality, exit conditions that preserve VISION.md principles, anti-criteria that guard against scope sprawl and drift.

### What Holds Across This Horizon

* every commitment in the Guiding Commitments Across All Phases section, without exception
* [SCOPE.md](./SCOPE.md) Non-Goals remain Non-Goals until SCOPE.md itself is revised with explicit justification
* CONTEXT §10 Explicit Non-Goals — no price prediction, no financial advice, no autonomous trading agent, no sentiment reductionism, no black-box prediction — continue to hold indefinitely

### Entry Criteria

No single entry criterion is named. Horizons are entered phase by phase, through the same gating discipline as Phase 3 and Phase 4, once the preceding phases have given the project the signal-quality ground to stand on.

### Exit Criteria

Not applicable. This is a horizon, not a phase with a destination.

### Anti-Criteria

* treating the possibilities enumerated here as commitments
* sequencing possibilities by market demand rather than by signal-quality readiness
* interpreting [VISION.md](./VISION.md)'s Likely Maturation as a plan rather than a trajectory
* permitting long-horizon possibilities to retroactively alter Phase 1 or Phase 2 scope

---

## V1 Exit Criteria (Explicit Alignment With SCOPE.md)

V1 exit criteria map 1:1 onto [SCOPE.md](./SCOPE.md)'s In Scope (v1) list. This section restates the correspondence so a reader evaluating whether the project is ready to exit Phase 1 can check against SCOPE.md directly.

| SCOPE.md In Scope (v1) | Phase 1 Exit Condition |
| --- | --- |
| ingestion of earnings call transcripts | Ingestion component ingests earnings call transcripts; raw artifacts are immutable; source metadata attached |
| entity identification and temporal document organization | Entity Resolution produces canonical Entity and Speaker identity; Document temporal metadata is recorded (event/document/observation time) |
| heuristic and ML-based analysis of the five confirmed Signal types | Heuristic Analysis and Learned Analysis produce candidate evidence for each of Narrative Drift, Confidence Shift, Omission Event, Contradiction Event, Structural Anomaly |
| a Fusion Engine that combines heuristic and ML outputs into ranked, traceable Signals | Fusion Engine integrates candidate evidence; Basis is preserved on every Signal; Confidence is distinct from Strength |
| structured, explainable Signal outputs with evidence links | every Signal carries Evidence with Spans; Commentary is non-empty; the Signal → Basis → Evidence → Spans chain is resolvable |
| human-reviewable Signal presentation | Signals are surfaceable in a form consumable by a human reviewer, pending detailed presentation design from USER_EXPERIENCE.md |
| an Evaluation Harness sufficient for early-stage structured human review | Evaluation Harness samples Signals, records reviewer feedback, and can host Candidate-Type Pool review once exercised |

Phase 1 exit is met when every row in this table is met. Phase 2 — signal quality validation — then begins against the operational system produced in Phase 1.

---

## Signals That Indicate Readiness To Advance

Advancement from one phase to the next is a judgment exercised by contributors, informed by qualitative signals rather than calendar milestones.

### Product Signals

* reviewers converge on articulations of why Signals are meaningful, rather than diverging
* surfaced Signals are traceable to source without manual effort
* Candidate and Surfaced lifecycle transitions behave as designed; Retired Signals are rare and traceable when they occur

### Research Signals

* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) entries relevant to the next phase's questions have accumulated Findings, not only Hypotheses
* findings have propagated into CONTEXT.md, SCOPE.md, ASSUMPTIONS.md, or the glossary where they update the project's understanding
* questions held open by design remain open; questions that can close have closed with explicit Basis

### Operational Signals

* the system operates within the low-capital posture; phase progression does not require abandoning that posture
* the system remains functional if external model providers are unavailable (ARCHITECTURE.md Model Ownership Posture)
* DerivationRuns are reproducible; re-derivation under new logic behaves as designed

---

## Signals That Do Not Move Phases Forward

These pressures, singly or in combination, are not grounds for advancing phases. They are named so that a contributor under pressure can recognize the pattern and respond accordingly.

* **Hype pressure** — the broader ecosystem attending to a topic the project is adjacent to does not imply readiness. The project advances on signal quality, not on attention (VISION.md: Drift Toward Scope Sprawl, Drift Toward Noise).
* **Investor or funder expectations** — external commitments that predate the project's readiness do not reshape readiness (ASSUMPTIONS T2). The roadmap does not commit to funder-facing milestones.
* **User feature requests** — user pressure is a research input, not a phase driver. Taxonomy extensions arrive from the research-driven or discovery-driven paths, not from feature requests (ASSUMPTIONS E2; CONTEXT §4; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Extension).
* **Benchmark chasing** — a number clearing a threshold is not the same as a human reader finding the signals useful (CONTEXT §14; VISION.md: Drift Toward Ground-Truth Theater).
* **Competitive pressure** — the landscape moving does not change the project's problem (see [COMPETITIVE_LANDSCAPE.md](./COMPETITIVE_LANDSCAPE.md)). A competitor shipping sentiment scores does not oblige this project to emit sentiment scores.
* **Calendar pressure** — the roadmap is qualitative; the passing of time is not, by itself, a reason to advance.

A phase that advances on any of these pressures without a grounded readiness signal is, by this document's construction, not advancing.

---

## Preservation Of VISION.md Principles Across Phases

[VISION.md](./VISION.md) names seven Principles Across Time. Their preservation is a first-class criterion for every phase; it is not a side concern.

* **Meaning Is Temporal** — no phase relegates temporal analysis to secondary status. All five confirmed Signal types depend on temporal comparison; subsequent taxonomy extensions must also respect this grounding.
* **Structure Anchors Learning** — no phase promotes the ML layer to sole arbiter of Signal emission. Heuristics remain structural scaffolding.
* **Explainability Is A First-Class Property** — no phase introduces an output surface that skips Basis or Evidence.
* **Ownership Over Convenience** — no phase introduces external LLM APIs into critical paths. Optional non-critical-path uses are permitted, but the project's core remains self-sufficient.
* **Restraint Beats Coverage** — phases add coverage only when restraint permits. Premature coverage under phase pressure is a failure mode, not a feature.
* **Human Judgment Is The Final Authority** — no phase automates away the user's role. Evaluation's quantitative layer, when it arrives, supplements human judgment rather than replacing it.
* **Epistemic Honesty Over Confidence** — Confidence remains distinct from Strength at every phase; no phase collapses the two.

A phase transition that requires weakening any of the above is not a phase transition of this project. It is a different project.

---

## Cross-Reference With SCOPE.md's Boundary Posture

[SCOPE.md](./SCOPE.md) names In Scope (v1), Deferred (v2+), and Non-Goals. Each of those categories interacts with this roadmap differently.

* **In Scope (v1)** is operationalized by Phase 1. Phase 1 does not exit until the In Scope list is realized.
* **Deferred (v2+)** is not in Phase 1. Specific deferred items may enter Phase 3 (first additional domain) or Phase 4 (analytical deepening) or the horizon beyond, each subject to phase-gating criteria.
* **Non-Goals** are not phased in. They remain Non-Goals indefinitely. A Non-Goal becoming in-scope requires a revision to SCOPE.md and CONTEXT.md, not a roadmap entry.

This triad holds across the document. The roadmap does not walk back Non-Goals under any phase name.

---

## What This Document Does Not Decide

* dates, quarters, or release cadences of any kind
* resourcing, staffing, or team composition
* specific features at a finer grain than the SCOPE.md In Scope list for v1
* specific tools, frameworks, languages, or deployment environments
* specific evaluation metrics or thresholds
* the exact shape of USER_EXPERIENCE.md or its phase of introduction
* go-to-market, pricing, or distribution strategy

If a roadmap decision would require one of the above to be made, it is out of scope for this document and belongs to the appropriate downstream document.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document honors their commitments and does not renegotiate them.
* [VISION.md](./VISION.md) supplies the principles every phase must preserve.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies the beliefs about readiness and posture that the phase gates operationalize.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) supplies the vocabulary.
* [ARCHITECTURE.md](./ARCHITECTURE.md), [DATA_MODEL.md](./DATA_MODEL.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) supply the structural, data, and Signal contracts that Phase 1 must realize and subsequent phases must preserve.
* [COMPETITIVE_LANDSCAPE.md](./COMPETITIVE_LANDSCAPE.md) supplies the account of the project's distinctness that the roadmap must remain consistent with.
* [RESEARCH_NOTES.md](./RESEARCH_NOTES.md) supplies the open questions whose resolution or deliberate hold-open informs phase progression.
* DECISION_LOG.md (future) is expected to record the phase-transition decisions themselves, with references back to the research notes that supported them.
