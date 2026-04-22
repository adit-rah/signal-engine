# ASSUMPTIONS.md

## Purpose Of This Document

ASSUMPTIONS.md surfaces the beliefs about the world that CONTEXT.md and SCOPE.md leave implicit. Downstream architects will make decisions that silently depend on these beliefs; naming them now prevents contradictory decisions later.

Each entry below is a claim about the world the project operates in, not a design preference. Where an entry reads more like a design decision than a belief, it is flagged and deferred to the document that will own it.

Where this document and CONTEXT.md disagree, CONTEXT.md is authoritative.

---

## How To Read This Document

Each assumption is formatted as:

* a crisp statement of the claim
* a short justification referencing CONTEXT.md or SCOPE.md where possible
* a one-line risk note where the assumption carries meaningful consequence if wrong

Assumption identifiers (e.g. U1, D4, H5) are stable. Downstream documents may cite them when explaining which beliefs a decision relies on.

---

## Assumptions About Users

### U1. Users have financial literacy sufficient to interpret narrative signals.

The audience described in CONTEXT §17 is composed of individuals who already engage deeply with financial text. Signals are expressed in the grammar of financial narrative; they are not translated for a general audience.

Risk: if the actual user base is broader, signal presentation may require an interpretive layer the project has not planned.

### U2. Users value depth and explainability over speed.

CONTEXT §17 and SCOPE's User Experience Goals both frame the user as a depth-seeker. Latency is an acceptable trade for quality and traceability.

Risk: if future users demand real-time responsiveness, deferred work in SCOPE (real-time and streaming) becomes load-bearing sooner than planned.

### U3. Users already consume financial text; the system does not source their information diet.

SCOPE's Core Problem Space describes information the user is already processing manually. The system reduces the cost of processing, not the burden of access.

Risk: if users cannot reliably access the underlying text, the system's value is upstream-capped.

### U4. Users want signals in the context of an entity's own history, not relative to a portfolio.

CONTEXT §8 commits to temporal analysis of an entity over time. Personalized and portfolio-aware workflows are deferred (SCOPE Deferred).

Risk: users may expect portfolio-level aggregation from the outset; the initial presentation may feel incomplete.

### U5. Users engage the system individually rather than collaboratively in the initial period.

Multi-user collaboration is deferred (SCOPE Deferred). The initial system models a single reader at a time.

Risk: early adopters inside small research teams may expect shared workspaces; this is not a v1 capability.

### U6. Users tolerate latency in the tens-of-seconds to minutes range for depth of analysis.

Implicit in CONTEXT's §14 evaluation framing (human review, dogfooding, retrospective study) and the absence of real-time commitments in SCOPE. The system is positioned as deliberate, not immediate.

Risk: if users expect instantaneous results, the operational posture of v1 will feel heavy.

---

## Assumptions About Data

### D1. Earnings call transcripts are acquirable with sufficient historical depth for comparative analysis.

CONTEXT §8 cites "sufficient historical depth for comparative analysis" as a reason for choosing this domain. Acquisition is treated as feasible in principle but not solved in detail.

Risk: acquisition gaps, paywalls, or licensing limits could meaningfully constrain which comparisons the system can perform. SCOPE Open Questions already flags this as unresolved.

*Specific acquisition strategy is deferred to downstream data-sourcing work.*

### D2. Earnings call transcripts are structurally regular enough to support heuristic segmentation.

The quarterly cadence, prepared-remarks / Q&A structure, and consistent speaker roles implied in CONTEXT §8 make heuristic segmentation tractable.

Risk: structural variability across companies, industries, or eras may be larger than expected, weakening heuristic coverage.

### D3. Transcripts can be reliably attributed to individual speakers.

Confidence shift, behavioral communication profiling, and cross-speaker contradiction analysis depend on speaker attribution (CONTEXT §4, §5.3; SCOPE's Behavioral Communication Profiling).

Risk: if speaker attribution is inconsistent or absent, several signal types lose fidelity.

### D4. Quarterly cadence is adequate temporal resolution for v1.

CONTEXT §8 cites quarterly cadence as a virtue. Drift, omission, and confidence shifts are assumed to be legible across quarterly intervals.

Risk: some meaningful narrative changes may occur on sub-quarterly timescales and be missed in v1. These remain addressable in future domain expansion (SCOPE Deferred).

### D5. Transcript text is primarily in English during the initial period.

Neither CONTEXT.md nor SCOPE.md specifies a language posture. A domain-adapted representation model (CONTEXT §6.2) implicitly assumes a target language. English is the default downstream work should assume unless MODEL_STRATEGY.md explicitly commits otherwise.

Risk: multilingual requirements would meaningfully widen the scope of model strategy. This is a gap in CONTEXT.md that may warrant a later note.

### D6. Licensing posture permits training on acquired text.

In-house model ownership (CONTEXT §6.1) depends on the ability to train on domain-specific text. The licensing posture for acquired transcripts must permit this use.

Risk: if licensing restricts training, the model strategy in CONTEXT §6 becomes operationally harder and may require adaptation.

### D7. Data volume in v1 is bounded by the earnings-call domain and the company set chosen to cover.

SCOPE's In Scope list commits to earnings call transcripts and no other sources. V1 data volume is therefore the product of earnings calls, companies covered, and historical depth retained.

Risk: underestimating the covered company set or historical depth affects storage and training feasibility but does not change architectural shape.

### D8. Transcript text is primarily machine-readable as text rather than as audio or scanned image.

CONTEXT §1 and CONTEXT §8 treat the domain as text. Audio-to-text and image-to-text preprocessing are not part of the stated scope. Multi-modal inputs are explicitly deferred (SCOPE Deferred).

Risk: if reliable machine-readable transcripts are unavailable for some companies, acquisition gaps appear that only multi-modal processing could fill — outside v1 scope.

---

## Assumptions About Signals

### S1. Meaningful signals exist in narrative change and are non-trivially detectable.

The core thesis (CONTEXT §2) asserts that meaning emerges through change. The project presumes this change is detectable via the hybrid intelligence described in CONTEXT §3.2.

Risk: if most narrative change is noise rather than signal, the ratio of valuable to total output will be lower than hoped, and evaluation in CONTEXT §14 will be correspondingly harder.

### S2. The five confirmed signal types (CONTEXT §4) are the right initial decomposition.

Narrative drift, confidence shift, omission event, contradiction event, and structural anomaly are assumed to cover the early useful signal space.

Risk: a type may prove redundant or indistinguishable in practice, or a major signal category may be absent. The taxonomy is extensible (CONTEXT §4) but the cost of revision grows with integration depth.

### S3. False positives are costlier to user trust than false negatives in the early period.

CONTEXT §13.2 warns against overconfidence. A system that surfaces too many weak signals is likely to erode user trust faster than one that occasionally misses a meaningful signal.

Risk: excessive caution may reduce apparent usefulness in early demonstrations; this trade is accepted. The posture may shift as users mature, but the starting position leans toward restraint (see the Restraint principle in VISION.md).

### S4. Signal quality is recognizable by humans before it is measurable by automated metrics.

CONTEXT §14 defers to human judgment during early evaluation. This presumes a human reviewer can recognize a good signal when shown one, given sufficient context.

Risk: if expert human reviewers disagree systematically, evaluation becomes harder — not just slower.

### S5. The meaning of "meaningful change" is partially definable by rule and partially contextual.

Some portion of signal quality can be pinned down through structured rules (CONTEXT §3.2.A). The remainder is inherently contextual and is where the ML layer contributes generalization (CONTEXT §3.2.B).

Risk: the balance between structural definition and learned generalization is itself an open question (CONTEXT §15). A wrong balance per signal type weakens that signal.

### S6. Signal importance ranking is possible and useful.

CONTEXT §9 commits to ranked signal outputs. The confirmation implies ranking is feasible at some level of quality.

*Ranking methodology is a design decision, not a world-belief. Deferred to SIGNAL_DEFINITIONS.md and ARCHITECTURE.md. SCOPE Open Questions already flags it.*

### S7. Cross-signal interactions exist and are worth modeling eventually.

Implicit in CONTEXT §3.2.C's framing of the fusion layer as "where signal quality ultimately emerges". A system that treats each signal type independently would not need a fusion layer at all.

Risk: if cross-signal interactions are weak or mostly redundant in practice, the fusion layer's complexity is under-justified.

---

## Assumptions About Heuristics, ML, And Fusion

### H1. Heuristic structure is tractable enough to meaningfully anchor the ML layer.

CONTEXT §7 treats heuristics as structural scaffolding. This presumes financial narrative has sufficient recurring structure to encode in rules without excessive brittleness.

Risk: if heuristic coverage is thinner than expected, the ML layer bears more interpretive weight and explainability degrades.

### H2. The ML layer contributes real generalization beyond what heuristics can capture.

CONTEXT §5 claims ML provides semantic richness and generalization. The project's value depends on this being true at the scale the in-house posture supports.

Risk: if learned representations are not substantially better than lexical heuristics on financial text at the chosen scale, the cost of in-house model ownership is poorly repaid.

### H3. Small, specialized models can reach acceptable quality per signal type.

CONTEXT §6.2 commits to a stack of small, specialized models rather than a single large model.

Risk: if quality on specific signal types requires scale the in-house posture cannot absorb, model strategy must adapt — either narrower scope, fewer specializations, or reduced ambition per type.

### H4. The fusion layer is a solvable design problem, not an unresolvable philosophical one.

CONTEXT §3.2.C describes the fusion layer as "the most significant and deliberately the least specified" component. This presumes it can be built, even if the specific resolution strategy is deferred.

Risk: if heuristic and ML outputs are systematically in tension rather than complementary, fusion becomes a persistent source of friction rather than a design decision.

*Specific fusion mechanics are deferred to ARCHITECTURE.md and related downstream work.*

### H5. In-house training is feasible on modest hardware budgets.

CONTEXT §6.3 states this directly. The project accepts the associated operational cost (CONTEXT §13.5).

Risk: if the representation model strand requires more compute than is affordable, the model strategy must adapt. This is a tight constraint on ambition.

### H6. External large-language-model APIs are not required for any critical path.

CONTEXT §6.1 commits to this posture. Optional local small-footprint language models are permitted (CONTEXT §6.2); external APIs are excluded from critical paths.

Risk: if a task emerges that only a large external model can handle, the project must choose between accepting the scope loss and revisiting the posture. The latter is a meaningful change to CONTEXT.md.

### H7. Explainability can be preserved as model complexity increases.

CONTEXT §6.4 states that complexity is justified only when it produces measurably better signals than simpler alternatives. This presumes traceability can be maintained as model sophistication grows.

Risk: some classes of learned component (e.g. deeply entangled representations) may defeat traceability. If so, they are excluded on that ground.

---

## Assumptions About Team, Timeline, And Operations

### T1. The team has or can develop the ML capability required for in-house model ownership.

CONTEXT §13.5 names this burden explicitly. Accepting it presumes the capacity to discharge it.

Risk: if specialized ML expertise is not sustainably available, in-house ownership becomes a liability rather than a strength.

### T2. The project is long-horizon rather than short-deadline driven.

CONTEXT §14's evaluation philosophy and §6's model posture both presume time for iteration, human evaluation, and model development. The project is not optimized for speed to a product launch.

Risk: external pressure to ship quickly could force premature decisions in the fusion layer or evaluation harness. Those are precisely the places premature decisions cost the most.

### T3. Operational infrastructure is modest in the initial period.

Implied by CONTEXT §6.3 and the absence of real-time requirements in SCOPE. Batch and on-demand processing are the assumed operating mode in v1.

*Specific operating mode is deferred to ARCHITECTURE.md.*

### T4. The evaluation harness evolves alongside the system rather than preceding it.

CONTEXT §14 explicitly frames evaluation as an evolving artifact.

Risk: without discipline, a perpetually-evolving harness can defer accountability indefinitely. This risk is acknowledged in CONTEXT §13.3 and must be managed by whoever owns evaluation downstream.

### T5. The project can operate without a dedicated data-acquisition function in the earliest period.

Implicit in the quiet treatment of data sourcing in CONTEXT §8 and SCOPE. Acquisition is treated as feasible, not as a large distinct workstream.

Risk: acquisition may in fact be a non-trivial engineering workstream. If so, expect it to surface as a dedicated concern rather than a background task.

---

## Assumptions About Scope Evolution

### E1. Signal quality validation on earnings call transcripts precedes domain expansion.

SCOPE Deferred and CONTEXT §8 both position v1 around earnings calls, with other domains unlocked by validated quality.

Risk: without an explicit definition of "validated quality", domain expansion may happen under pressure rather than by readiness. The evaluation owner downstream should pin this down.

### E2. Additional signal types emerge from research, not from feature requests.

CONTEXT §4 makes the taxonomy extensible through the pattern owned by SIGNAL_DEFINITIONS.md. New types are expected from surfaced research rather than from user wishlists.

Risk: user pressure for specific signal types may distort the taxonomy's conceptual coherence if not disciplined through the extension pattern.

### E3. Multi-modal inputs, real-time processing, and collaborative tooling remain deferred.

Explicitly deferred in SCOPE Deferred.

Risk: market or user demand may push these forward; the project accepts the risk of deferring.

### E4. Market-correlation study remains exploratory, not promoted to v1.

SCOPE's Market-Relevant Signal Correlation is framed as exploratory and not a v1 deliverable. The project assumes this framing holds through v1.

Risk: if market-correlation work is promoted prematurely, the Non-Goal of avoiding prediction (CONTEXT §10) is strained.

---

## Assumptions About Trust, Explainability, And Uncertainty

### X1. Users can productively engage with uncertainty if it is communicated honestly.

CONTEXT §13.2 and §14 both position uncertainty as a first-class concern. The project presumes users prefer honest uncertainty to false confidence.

Risk: some users may interpret hedged outputs as low-quality outputs. User-facing uncertainty presentation is deferred to USER_EXPERIENCE.md.

### X2. Explainability does not require exposing every internal step to the user.

CONTEXT §3.3 requires traceability to source text, rules, and model-derived scores. Traceability is a system property; how much of it surfaces at the user interface is a separate concern.

*How much of the explanation is surfaced to users is deferred to USER_EXPERIENCE.md.*

### X3. Evidence excerpts are sufficient grounding for most surfaced signals.

SCOPE's Insight Presentation and CONTEXT §9 both treat source-evidence linkage as core. The project presumes a reader, given the signal and its supporting excerpts, can evaluate it.

Risk: if signals routinely require more context than a short excerpt to evaluate, presentation costs grow, and evaluation per signal becomes heavier.

### X4. Users tolerate that some signals are inherently subjective.

CONTEXT §13.3 acknowledges that many signals lack clean ground truth. The project presumes users accept this rather than demand objective proof for every claim.

Risk: users may expect binary verdicts; presentation design (deferred to USER_EXPERIENCE.md) must navigate this.

### X5. The project's definition of "meaningful" is shared enough across reviewers to be evaluable.

Implicit in CONTEXT §14's reliance on human review. If reviewers operate from incompatible notions of meaning, human evaluation produces noise rather than signal about signal quality.

Risk: reviewer calibration may itself need to become a downstream concern if disagreement is persistent.

---

## Deliberate Non-Assumptions

The project deliberately does not assume the following, either because the opposite is believed or because committing either way would prematurely constrain downstream work.

### N1. The project does not assume that its outputs are predictive of market behavior.

SCOPE Non-Goals and CONTEXT §10 explicitly reject prediction framing. Market-relevant signal correlation is treated as exploratory (SCOPE's Intelligence Concepts).

### N2. The project does not assume that a single large model would match a stack of specialized models under the cost and control constraints accepted.

CONTEXT §6.2 commits to the opposite posture deliberately.

### N3. The project does not assume that automatic metrics can replace human evaluation during early development.

CONTEXT §14 explicitly rejects this substitution for now.

### N4. The project does not assume its signal taxonomy is final.

CONTEXT §4 treats the taxonomy as extensible.

### N5. The project does not assume a specific user interaction model.

CONTEXT §17, SCOPE, and USER_EXPERIENCE.md all defer this. No assumption in this document should be read as pre-deciding interaction design.

### N6. The project does not assume that every signal has a clean ground truth.

CONTEXT §13.3 treats the absence of ground truth as a central challenge, not an implementation inconvenience.

---

## Deferred Decisions Flagged In This Document

The following items appeared in this document in places where an assumption-shaped statement would overstep. They are not assumptions; they are design decisions that will be made elsewhere.

* Specific data acquisition strategy for earnings call transcripts — deferred to downstream data-sourcing work; flagged in SCOPE Open Questions.
* Signal ranking and prioritization methodology — deferred to SIGNAL_DEFINITIONS.md and ARCHITECTURE.md.
* Fusion-layer resolution mechanics — deferred to ARCHITECTURE.md and related work.
* Specific operating mode (batch, on-demand, or other) — deferred to ARCHITECTURE.md.
* Exact surface of explanation presented to users — deferred to USER_EXPERIENCE.md.
* Reviewer calibration procedure if expert disagreement is persistent — deferred to the evaluation owner downstream.

---

## Relationship To Other Documents

* CONTEXT.md and SCOPE.md are authoritative where they speak; this document extends them rather than revising them.
* VISION.md establishes the forward-looking orientation this document anchors in reality.
* DOMAIN_GLOSSARY.md defines the vocabulary used here.
* Downstream documents may cite an assumption by its identifier (e.g. D4, H4) to signal which belief a decision relies on. If a downstream decision requires a belief not listed here, it should add the belief before proceeding.
