# ETHICS_AND_LIMITATIONS.md

## Purpose Of This Document

ETHICS_AND_LIMITATIONS.md establishes the Signal Engine's epistemic honesty posture: what the system can and cannot claim, how its limitations are communicated, how false-positive and false-negative modes are named, how it avoids drifting into predictive-oracle framing, and what language it will not use.

This is a product-quality document. It is not a terms-of-service document, not a liability disclaimer, and not marketing. The content here is a constraint on future user-facing materials and on the system's surfaces — not a disclaimer appended to them after the fact.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## Scope And Non-Scope

### In scope

* the epistemic limits of the system and how they are communicated
* the posture on hallucination risk, given the in-house model commitment and the Basis requirement
* how the false-positive posture translates into user-facing implications
* how correlation is distinguished from causation in what the system says
* how Strength and Confidence are communicated and what they do not mean
* language the system does not use, and why
* known biases the project acknowledges
* things a user should never expect from the system
* the drift modes the project must stay vigilant against

### Out of scope

* specific user-facing wording (deferred to USER_EXPERIENCE.md; this document is a source of constraints for that wording)
* specific visual, interaction, or layout design (USER_EXPERIENCE.md)
* legal disclaimers, terms of service, or warranty language
* regulatory or compliance positioning
* marketing copy, positioning, or messaging

---

## Guiding Commitments

The project commits to a small set of epistemic commitments. Everything below is a consequence of these.

* The system informs a human; it does not predict, recommend, or act ([CONTEXT.md](./CONTEXT.md) §10; [SCOPE.md](./SCOPE.md) Non-Goals).
* Outputs describe observed change in narrative, not future state ([VISION.md](./VISION.md) §Failure Modes → Drift Toward Prediction; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) §Deliberate Non-Definitions).
* Structured Skepticism is a design discipline, not a disclaimer afterthought ([CONTEXT.md](./CONTEXT.md) §3.4).
* Every Signal is traceable to source text, contributing rules, and model outputs ([CONTEXT.md](./CONTEXT.md) §3.3; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy).
* False positives in early development are costlier to user trust than false negatives ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3).
* Restraint beats coverage ([VISION.md](./VISION.md) §Principles Across Time).

---

## Epistemic Limits: What The System Does Not Claim

The system's outputs are Signals in the specific sense defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). A Signal is a meaningful, explainable deviation or pattern in financial narrative structure over time. It is not any of the following, and the system must not imply otherwise:

* **not a prediction of future state.** A Narrative Drift Signal describes an observed drift. It does not claim the drift will continue, will stop, will reverse, or will be resolved favorably.
* **not a recommendation.** A Signal is not an instruction to buy, sell, hold, watch, flag, or act. The system surfaces information; the user decides what, if anything, to do with it.
* **not financial advice.** A Signal is an observation about communication, not a position on an underlying security, asset, or decision.
* **not a sentiment score.** The project rejects sentiment reduction by construction (CONTEXT §3.4, §10; DOMAIN_GLOSSARY Deliberate Non-Definitions → Sentiment / Sentiment Score).
* **not a causal claim.** A Confidence Shift observed alongside a later operational event is not a claim that the shift caused, revealed, or reliably preceded the event. Correlation is not causation and the system does not frame it as such.
* **not an alpha, trading, or buy-sell signal.** The word "Signal" in this project is a term of art (DOMAIN_GLOSSARY). It is not interchangeable with trading-signal terminology. Downstream documents and user-facing surfaces must not let the shared word drift into the trading sense.
* **not a claim of completeness.** The system's coverage of narrative change is bounded by its data domain (v1 earnings call transcripts, CONTEXT §8), its language (English-first, CONTEXT §8), its Entity set, and its historical depth. Absence of a Signal is not absence of narrative change; it is absence of a Signal the system detected and chose to surface.

These refusals are not cautionary footnotes. They are product constraints. A feature, surface, or piece of Commentary that implies any of them must not ship.

---

## Hallucination Posture

Hallucination — the generation of plausible text that is not grounded in source material — is a risk wherever learned components produce language. The project's posture reduces, but does not eliminate, this risk.

### Why the risk is structurally constrained

* **No external LLM API in critical paths** ([CONTEXT.md](./CONTEXT.md) §6.1). The most common source of free-floating generated claims — a general-purpose model invoked on arbitrary prompts — is absent from the system's critical paths by design.
* **Every Signal requires Basis and Evidence** ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy). A Signal whose contributing rules and model outputs cannot be resolved is not emitted. A Signal without Spans in source text is not emitted.
* **The Fusion Engine integrates; it does not invent.** The Fusion Engine combines heuristic and learned candidate evidence into a Signal whose Basis references both ([ARCHITECTURE.md](./ARCHITECTURE.md) §8). Its output is constrained by its inputs.
* **Small, specialized models** (CONTEXT §6.2) are scoped to narrow tasks. A contradiction-detection model does not have generative latitude to summarize a narrative; a representation model does not produce free text at all.

### Where the risk remains

* **Commentary.** Every Signal has a non-empty, human-readable Commentary field ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) §Commentary; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy). Commentary is generated text. It is the most plausible hallucination surface in the system.
* **Optional local language models** for structured-extraction tasks (CONTEXT §6.2). These are permitted; their outputs are subject to the same Basis and Evidence requirements as any other contributing component.
* **Theme names and summaries.** Where Themes are discovered or labeled with generated language, the label itself is not evidence for the Theme's presence; the ThemeInstance Spans are.

### The posture

* **Generated text is bound to its Basis.** Commentary is bound to the Signal it accompanies ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy). If the Basis is withdrawn, the Commentary does not stand alone.
* **Commentary does not extend the claim.** Commentary describes what the Signal observes and why it may be meaningful. It does not add claims beyond what the Signal, its Strength, its Confidence, and its Evidence support. This is a constraint on Commentary generation, owned in content by MODEL_STRATEGY.md and in surfacing by USER_EXPERIENCE.md.
* **Hallucinated Commentary is a defect, not a limitation.** When Commentary drifts from the Signal's Basis, the posture is to treat the drift as a bug and fix it, not to hedge its way into acceptability.
* **Structured outputs are preferred to prose where both work.** Where a claim can be expressed as structured data referencing Spans, it should be — prose is the last resort, not the default.

---

## False-Positive Posture And Its User-Facing Implications

[CONTEXT.md](./CONTEXT.md) §14 and user confirmation establish that false positives carry greater cost to user trust than false negatives in early development. [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) operationalizes this by lowering Confidence rather than withholding Signals silently.

This posture has two user-facing implications that must be communicated honestly. Neither is a disclaimer — each is a product truth that shapes how the system can be read.

### Absence of a Signal is not absence of risk

The system surfaces Signals it detects and chooses to surface. It does not surface every meaningful change in a narrative, every possible concern, or every risk. Reasons a meaningful change may not produce a surfaced Signal include:

* the change is real but weak relative to the noise floor for its Type
* the change depends on a Baseline that is too thin to support a high-Confidence Signal; Thin-History Policy (SIGNAL_DEFINITIONS.md) holds such Signals at Candidate or reduces their Confidence
* the change is outside the confirmed initial taxonomy and has not yet entered the Candidate-Type Pool
* the change occurred in a data domain not yet in scope (earnings call transcripts only in v1, CONTEXT §8)
* the Entity is not yet covered, or the historical depth needed for comparison is not yet present
* the Entity's communication is in a language the system does not yet support (English-first, CONTEXT §8)

A user treating the absence of a Signal as evidence that nothing is happening has misread the system. User-facing surfaces must not suggest comprehensive coverage.

### Presence of a low-Confidence Signal is not confirmation

Signals carry Confidence distinct from Strength ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Confidence; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) §Signal Confidence). A high-Strength Signal with low Confidence is coherent: a large observed deviation about which the system is not sure.

A user-facing surface must not collapse the two. In particular:

* a low-Confidence Signal is not evidence that the phenomenon it describes is occurring; it is evidence that the system observed something and is reporting honestly about its own uncertainty
* a low-Confidence Signal is not "probably wrong"; it is "the system's epistemic footing here is weaker than usual, and that footing is exposed rather than hidden"
* Strength and Confidence are always surfaced together; showing one without the other is misleading by construction

---

## Correlation Is Not Causation

Narrative change may coincide with market or operational events. The system observes narrative change. It does not claim that narrative change causes, predicts, or reliably precedes those events.

* the system does not issue Signals that assert causal links between narrative change and external outcomes
* Commentary does not assert causation where only co-occurrence is supported by evidence
* market-relevant signal correlation remains exploratory ([SCOPE.md](./SCOPE.md) Intelligence Concepts) and is not a v1 deliverable; if and when it enters scope, its framing must preserve this distinction
* user-facing materials describing example Signals must not narrate them as having caused or predicted subsequent events, even where such framing is tempting in retrospect

The project treats this distinction as a load-bearing commitment. A single example presented as "the Signal predicted the event" would undermine the posture regardless of how heavily hedged the surrounding text.

---

## Confidence And Strength: What They Communicate And What They Do Not

The system exposes two epistemic properties on every Signal: Strength and Confidence ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)).

### What they communicate

* **Strength** is a type-relative statement about how far the observed phenomenon rises above the noise floor for its Type. It is bounded. It is not a probability.
* **Confidence** is a representation of the system's epistemic certainty in the Signal itself. It reflects Baseline thinness, Basis disagreement, and Evidence span precision and quantity. It is not a probability of correctness.

### What they do not communicate

* **Strength is not cross-type.** A high-Strength Narrative Drift and a high-Strength Confidence Shift are not on a shared scale; they describe type-internal intensity, not comparative magnitude across types ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Signal Anatomy → Strength).
* **Strength is not a probability of anything external.** It is not a probability of price movement, of operational event, or of any outcome in the world ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Strength invariants).
* **Confidence is not a probability of correctness.** Claiming otherwise would violate structured skepticism (CONTEXT §3.4).
* **Neither is a confidence interval on a prediction.** The system makes no prediction to hold an interval around.

### Constraints on presentation

* Strength and Confidence must be presented together. A single number without disambiguation — or a collapsed "score" — would erase the distinction the project paid for.
* Presentations that invite reading either as a probability must be avoided. Language like "95% likely", "high accuracy", and "certain" is not a faithful rendering of either property.
* The specific representation (scalar, banded, categorical) is deferred to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; surfacing to users is deferred to USER_EXPERIENCE.md. Whatever is chosen must honor the constraints above.

---

## Language Hygiene

[DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) §Deliberate Non-Definitions names specific vocabulary the project will not use. That list is authoritative. This document restates it as a user-surface constraint and adds enforcement responsibility.

### Terms that must not appear in user-facing materials

* **Sentiment / sentiment score** — prefer Confidence Shift, Narrative Drift, or the specific Signal type
* **Prediction / forecast** — prefer Signal; the system describes observed change, not future state
* **Alpha / alpha signal** — "Signal" in this project is not a trading term
* **Recommendation** — the system does not recommend; it surfaces information for a human to interpret
* **Trading signal / buy-sell signal** — out of scope; a Signal here is a narrative Signal
* **AI / AI-powered** — marketing-adjacent language; name the specific component (Heuristic Analysis, Learned Analysis, Fusion Engine) instead
* **Black-box model** — excluded by construction; explainability is required end-to-end
* **Autonomous agent** — not in scope; the system informs, it does not act
* **Accuracy** (as the primary evaluation term) — CONTEXT §14 explicitly rejects prediction accuracy as the measure of success

### Enforcement

* the API Boundary (ARCHITECTURE.md §14) must not surface response fields named in the forbidden vocabulary, even incidentally
* Commentary generation (MODEL_STRATEGY.md) must not produce text that uses the forbidden vocabulary; this is a constraint on that document's eventual design
* USER_EXPERIENCE.md is bound by this hygiene in any label, caption, tooltip, or prose surface it produces
* published materials about the system — documentation, examples, demonstrations — are bound by the same hygiene

### Language the project does use

Where a downstream surface is tempted to reach for forbidden vocabulary, the alternatives are concrete: the Signal types named in [CONTEXT.md](./CONTEXT.md) §4, the Signal properties named in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md), and the evaluation dimensions named in [CONTEXT.md](./CONTEXT.md) §14 (usefulness, clarity, consistency over time, cognitive-load reduction, surfacing of non-obvious change).

---

## Known Biases

The system is shaped by the data it reads, the language it reads it in, the companies it covers, and the structure of the domain. These biases are acknowledged, not hidden.

### Domain bias

* **Earnings call transcripts are performative.** Executives prepare for them. Framing is strategically chosen. A Confidence Shift observed in earnings call language is a shift in how the Entity chooses to communicate on its quarterly stage, not necessarily a shift in underlying state.
* **Quarterly cadence is a temporal filter.** Meaningful narrative change on sub-quarterly timescales is not visible in v1 ([ASSUMPTIONS.md](./ASSUMPTIONS.md) D4). Signals are bounded by the sampling rate of the domain.
* **The Q&A segment is analyst-shaped.** Which questions are asked, and by whom, shapes what gets said. A Signal derived from Q&A inherits the questions' framing.

### Language bias

* **English-first** ([CONTEXT.md](./CONTEXT.md) §8). The system is tuned to English financial discourse. Entities operating primarily in other languages are underserved in v1 and may be underserved for longer if model strategy does not cross the language boundary.

### Sample bias

* **Entity coverage is not uniform.** The set of Entities the system covers reflects data availability, acquisition terms, and historical depth. It does not reflect a balanced statistical sample of markets, industries, or geographies.
* **Historical depth varies by Entity.** Signals depending on Baselines are more reliable for Entities with long history. Thin-History Policy (SIGNAL_DEFINITIONS.md) addresses this at the Signal level; at the product level, the user should understand that coverage is uneven.

### Structural bias

* **Transcripts reflect what was said, not what was meant.** A Speaker who hedges for legal reasons is indistinguishable from a Speaker who hedges because of genuine uncertainty. The system observes the hedging; it does not attribute motive.
* **Provider artefacts shape what the system sees.** Transcript segmentation, punctuation, and speaker attribution are products of the transcript provider ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Common false-positive patterns throughout). Provider changes can look like narrative changes.

### Model bias

* **Learned components reflect their training corpora.** A representation model adapted to financial text (CONTEXT §6.2) encodes the norms of the text it was trained on. Where those norms are themselves biased (industry over-representation, historical-era register), the bias is inherited. Training-corpus composition is owned by MODEL_STRATEGY.md and is where this bias is managed.

These biases are not failures of the project. They are facts about the domain and the commitments the project has made. The product posture is to acknowledge them and to let users read Signals with them in mind.

---

## What A User Should Never Expect From The System

These are claims the system will not make about itself, even when users ask or when it would be convenient.

* an answer to "what will this stock do"
* an answer to "should I buy, sell, or hold"
* a probability that a Signal is correct, or that its phenomenon is occurring, or that it predicts an outcome
* a score that collapses Strength and Confidence into a single number
* a claim that a narrative change caused a subsequent market or operational event
* a claim of completeness — that it has surfaced every meaningful change, for every covered Entity, across every Signal type
* a claim that absence of a surfaced Signal means no meaningful change has occurred
* a guarantee that a Signal will remain Surfaced, or that its Confidence will not change on re-derivation
* a sentiment polarity
* a trading recommendation of any kind
* an autonomously taken action in any external system ([SCOPE.md](./SCOPE.md) Non-Goals)

A user who wants any of the above is reading the system for a purpose it was not built to serve.

---

## Drift Watch

[VISION.md](./VISION.md) §Failure Modes names the drift modes the project must stay vigilant against. This section inherits those drift modes from VISION.md and names their ethics-and-limitations consequences.

* **Drift toward sentiment** — any collapse of Signals into polarity violates CONTEXT §3.4, §10 and the Language Hygiene section above.
* **Drift toward prediction** — any framing of Signals as predictions violates CONTEXT §10 and the Epistemic Limits section above; particularly tempting when retrospective examples line up with later events.
* **Drift toward opacity** — any output not traceable to source text, rules, or scores violates CONTEXT §3.3 and hollows the Hallucination Posture's main defense.
* **Drift toward external dependency** — any movement of critical-path analysis to external models violates CONTEXT §6.1 and reintroduces the third-party hallucination and injection surfaces the in-house posture closed.
* **Drift toward autonomous action** — any action-taking surface violates SCOPE Non-Goals and the API Boundary's no-action property ([SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md)).
* **Drift toward ground-truth theater** — any evaluation that reports clean numerical accuracy against proxy labels violates CONTEXT §13.3 and would turn epistemic honesty into a performance rather than a practice.
* **Drift toward noise** — Signals that are technically correct but not meaningful erode trust faster than they build it ([VISION.md](./VISION.md) §Failure Modes). Ethics-side consequence: volume without restraint is a failure of product quality, not a feature of thoroughness.

The drift watch is a standing responsibility of the project. A feature request, a demo framing, or a piece of Commentary that nudges any of these directions is a signal to pause, not to proceed.

---

## What This Document Does Not Decide

* specific user-facing wording, labels, tooltips, or prose on any surface (owned by USER_EXPERIENCE.md; bound by the constraints here)
* specific representation of Strength and Confidence (scalar, banded, categorical) (owned by MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; surfacing by USER_EXPERIENCE.md)
* specific Commentary generation method (owned by MODEL_STRATEGY.md; surfacing by USER_EXPERIENCE.md)
* specific evaluation methodology, including how reviewer calibration handles disagreement (owned by EVALUATION.md; bound by CONTEXT §14's rejection of accuracy as primary metric)
* specific thresholds for when a Signal is surfaced, held at Candidate, or suppressed (owned by NARRATIVE_ANALYSIS.md, informed by the posture here)
* legal, regulatory, or compliance positioning

---

## Deferred Decisions

With named owners:

* exact user-facing wording and visual rendering → USER_EXPERIENCE.md (this document is a constraints source)
* Strength and Confidence representation → MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md; surfacing to users → USER_EXPERIENCE.md
* Commentary generation method → MODEL_STRATEGY.md; surfacing → USER_EXPERIENCE.md
* ranking and prioritization policy → NARRATIVE_ANALYSIS.md and EVALUATION.md
* evaluation methodology including reviewer calibration → EVALUATION.md
* specific thresholds for meaningfulness, Confidence cut-offs, Thin-History Policy numeric thresholds → NARRATIVE_ANALYSIS.md
* training-corpus composition decisions that bear on model bias → MODEL_STRATEGY.md, informed by DATA_ACQUISITION.md
* legal disclaimers, terms of service, acceptable-use policy → outside this document set

---

## Glossary Additions Recommended

Terms used in a committing way here that warrant [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) entries, or sharpened definitions:

* **Drift Watch** — the standing list of drift modes the project stays vigilant against, inherited from VISION.md §Failure Modes and named as a product-quality concern here
* **Epistemic Surface** — the set of properties a Signal exposes about its own certainty (Strength, Confidence, Basis disagreement, Baseline thinness); useful as a single handle for user-facing constraints
* **Hallucination Surface** — the set of generative surfaces in the system (principally Commentary) where generated text risks departing from Basis; named here to make the posture legible

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document inherits their non-goals without extending them.
* [VISION.md](./VISION.md) establishes the orientation this document operationalizes; the Drift Watch section is paired with VISION.md §Failure Modes.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies the beliefs this document relies on (notably S3 on false positives, X1 through X5 on user tolerance for uncertainty, D5 on language posture).
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; §Deliberate Non-Definitions is the authoritative list the Language Hygiene section enforces.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines Strength, Confidence, Basis, and Evidence — the epistemic surface this document protects.
* [SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md) is the companion document; where this one defines trust about claims, that one defines trust about data.
* [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) will surface this document's constraints to users; it owns wording, this document owns the wording's bounds.
* MODEL_STRATEGY.md, NARRATIVE_ANALYSIS.md, and EVALUATION.md own the deferrals listed above.
