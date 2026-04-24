# USER_EXPERIENCE.md

## Purpose Of This Document

USER_EXPERIENCE.md defines how users interact with the Signals the system produces: how Signals are surfaced, how Evidence is presented alongside them, how Strength and Confidence are communicated, how information density is managed, and how explainability is realized at the user-facing surface.

This document is conceptual. It does not commit to visual design, component libraries, interaction paradigms, or front-end technology. It defines the experience model within which those choices are later made.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Signal anatomy referred to here is specified in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). The backend-to-surface boundary is defined in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## How To Read This Document

* the document describes user-facing surfaces by purpose and content, not by visual treatment
* Signal anatomy fields (from [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) are each accounted for
* where a decision depends on visual design or interaction paradigm, it is deferred
* where a new term is useful, it is flagged for glossary extension rather than defined inline
* example Signal presentations are illustrative, not prescriptive copy

---

## Audience Baseline

Inherited from [CONTEXT.md](./CONTEXT.md) §17 and [ASSUMPTIONS.md](./ASSUMPTIONS.md) U1–U6. The system is built for individuals who already engage deeply with financial text and who value depth over speed:

* independent analysts
* researchers
* investors working on individual-entity analysis
* information-heavy decision makers

The user is assumed to possess the financial literacy required to interpret narrative Signals without translation. The user is assumed to consume financial text independent of the system — the system reduces the cost of noticing change, not the burden of access (ASSUMPTIONS U3).

The user is modeled as a single reader, not a team member (ASSUMPTIONS U5). Collaborative workflows are deferred ([SCOPE.md](./SCOPE.md) Deferred).

The user is modeled as entity-centric, not portfolio-centric (ASSUMPTIONS U4). The initial experience centers on a chosen Entity at a time; cross-Entity exploration exists as a secondary mode.

The user is assumed to tolerate latency in the tens-of-seconds to minutes range for depth of analysis (ASSUMPTIONS U6). The UX is not optimized for an instantaneous-response posture.

Refined persona work is expected to follow dogfooding experience; the baseline above is sufficient for this document.

---

## Guiding UX Commitments

Inherited from [CONTEXT.md](./CONTEXT.md), [VISION.md](./VISION.md), and [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md), and held as UX-level invariants:

* every Signal surfaced must be traceable to source text via its Basis and Evidence chain (CONTEXT §3.3)
* Confidence is never communicated as a probability of correctness (CONTEXT §3.4; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Signal Confidence)
* Strength and Confidence are distinct and must not be collapsed into a single display value
* Commentary is carried on every Signal and is immutable per Signal record
* the full Signal anatomy is accessible from the user-facing surface — some fields default to summary, none are hidden
* the UX reinforces structured skepticism rather than undermining it
* the UX does not introduce framings excluded by the Deliberate Non-Definitions ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)): no "sentiment", no "prediction", no "recommendation", no "buy/sell signal", no "alpha"
* the UX does not invent analytical value it has not received from the backend; ranking, Confidence, and Strength are upstream concerns surfaced faithfully

---

## Default Surface

The default surface when a user engages with the system is **the Entity Narrative Timeline for a selected Entity**.

If no Entity has been selected, the entry surface is **Entity discovery** — a search or browse affordance that resolves to a canonical Entity. Entity discovery is a necessary access point; it is not the analytical surface.

Once an Entity is selected, the Timeline becomes the primary surface. It is the view from which every other UX flow is reachable:

* Signal Detail (per-Signal drill-down)
* Basis Inspector (per-Signal reconstruction of how it was produced)
* Evidence View (per-Signal source-text excerpts with locus)
* NarrativeState As-Of (historical reconstruction for this Entity)
* cross-Entity exploration (from a Signal's Type or Theme, outward)

Cross-Entity browsing exists — for example, "Signals of Type Contradiction Event across covered Entities in the last quarter" — but it is a discovery mode, not the default. The system is oriented around depth on one Entity rather than breadth across many (ASSUMPTIONS U4).

---

## Primary Surfaces

Each surface below is described by purpose and content. Visual treatment is deferred.

### Entity Narrative Timeline

The default analytical surface for a selected Entity.

Purpose:

* present the Entity's Signals as a temporally ordered sequence
* make visible what has changed over time in the Entity's narrative
* provide a reading path from high-level change to specific Evidence

Content:

* the Entity's Signals over a selected time window, in temporal order
* each Signal presented as a headline comprising its Type, Subject (including Speaker where relevant), a Strength indication, a Confidence indication, and a Commentary excerpt
* markers for lifecycle state (Candidate, Surfaced, Stale, Superseded, Retired) visible but not emphasized equally
* a visible As-Of indicator showing the Effective Time the Timeline is reconstructed at
* filters by Signal Type, Speaker, Theme, Strength floor, Confidence floor, and lifecycle state

The Timeline is entity-scoped. Cross-Entity aggregation is not its purpose.

### Signal Detail

A per-Signal surface reached by drill-down from the Timeline or any list view.

Purpose:

* expose the full Signal anatomy for one Signal
* provide the reading path to Basis, Evidence, and Lineage

Content:

* Identity (stable identifier), Type, Subject, Temporal Scope (including subject time, emission time, and, where applicable, Baseline valid-time)
* Strength and Confidence, separately presented
* Commentary in full
* a link to Basis Inspector
* a link to Evidence View
* Lineage references — the Signal this record supersedes (if any) and the Signal that supersedes it (if any)
* lifecycle state with a plain-language explanation of what that state means

### Basis Inspector

A per-Signal surface that reconstructs how the Signal was produced.

Purpose:

* honor CONTEXT §3.3 explainability at the user-facing level
* allow the user to see which heuristic rules contributed, which learned analyses contributed, and where the Fusion Engine reconciled them
* expose Basis Disagreement honestly when it occurred

Content:

* heuristic contributions, each with a short plain-language description
* learned contributions, each with a short plain-language description — naming the analysis, not the model internals
* the fusion step, described as a reconciliation rather than a black-box aggregation
* Basis Disagreement, when present, shown as a first-class property rather than hidden
* references to the DerivationRuns involved, so a sophisticated user can trace re-derivation across versions
* a link back to Evidence View — Basis and Evidence together are the full explanation

Basis Inspector does not expose model internals, weights, or probabilities claimed to be correctness probabilities. It exposes *what contributed* and *what was reconciled*.

### Evidence View

A per-Signal surface that shows the Spans supporting the Signal.

Purpose:

* anchor the Signal in source text
* allow the user to read the supporting material in its original context
* honor CONTEXT §3.3 traceability at the user-facing level

Content:

* each Evidence record, with the referenced Spans resolved to source text excerpts
* for each Span: the Document, the Segment, the Speaker (where applicable), the event time of the Document, and the excerpt itself
* navigation to the full Document view for any excerpt, so the user can read the surrounding context
* where an Evidence record comprises Spans from multiple Documents (typical for Narrative Drift, Confidence Shift, Contradiction Event), all are shown with clear temporal ordering
* where the Signal is an Omission Event, the rendering is adapted — see Evidence Presentation below

### NarrativeState As-Of

A surface that reconstructs the Entity's narrative state as of a chosen Effective Time.

Purpose:

* support the core temporal reasoning the system is built for (CONTEXT §2, §11)
* allow the user to ask "what did this narrative look like then"
* ensure that historical reasoning is not silently reshaped by later data

Content:

* the Entity's Surfaced Signals as they existed at the chosen Effective Time
* Baselines applicable at the chosen time, including Baseline thinness as it was at that time
* Themes and recent Documents relevant to the Entity at that time
* a clear indicator that the view is historical, not current

The NarrativeState As-Of view reads from immutable history. It does not present hindsight — it presents what the system believed, with the Basis it had, at the chosen time. Lineage makes visible how a Signal at that time has since been superseded or retired.

### Candidate Signal Review

A surface exposing Candidate Signals for the selected Entity or across Entities.

Purpose:

* make the Candidate pool visible without elevating it to the primary surface
* allow curious users, researchers, and Evaluation Harness reviewers to engage with pre-surfaced material
* distinguish lifecycle state from quality judgment — a Candidate Signal is not a "bad" Signal; it is a lifecycle-positioned one

Content:

* the Entity's Candidate Signals with the same anatomy presentation as Surfaced Signals
* an explicit indicator that these are Candidates and are not included in the default Timeline
* the reason a Candidate has not been promoted — threshold not met, thin-history gate, pending human review, or other — where the system can articulate it
* clear labeling that engagement with this surface is a different mode than the default analytical flow

Candidate Signals are not treated as drafts or as reduced-quality Signals. They are Signals at a specific lifecycle state. Presentation reinforces that framing.

### Cross-Entity Exploration

A secondary discovery surface for queries that are not Entity-scoped.

Purpose:

* support queries such as "Contradiction Events across covered Entities in the last quarter" or "Omission Events concerning Theme X"
* provide a path outward from a Signal on the Timeline to related Signals elsewhere
* support analyst workflows that explore patterns rather than single Entities

Content:

* a list of Signals matching the cross-Entity query, with Entity as a first-class column
* anatomy summary per Signal (Type, Subject including Entity, Strength, Confidence, lifecycle state, Commentary excerpt)
* filters equivalent to those on the Timeline
* a return path — selecting any Signal opens its Signal Detail, from which the user can descend into that Entity's Timeline

The surface is built to serve exploration; it is not a dashboard or a metric view.

---

## Signal Presentation

Every Signal surfaced carries the full anatomy described in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). The UX presents that anatomy under a progressive-disclosure discipline:

* **Headline (always visible)**: Type, Subject (Entity and Speaker where relevant), a qualitative Strength indicator, a qualitative Confidence indicator, a short Commentary excerpt, lifecycle state if other than Surfaced.
* **Summary (one step of drill-down)**: Temporal Scope, full Commentary, link to Basis Inspector, link to Evidence View, Lineage references.
* **Full reconstruction (deeper drill-down)**: full Basis chain, all Evidence Spans resolved to source excerpts, references to DerivationRuns, Baseline thinness where applicable.

No anatomy field is hidden; the surface defaults to summary presentation and expands on request. This structure honors ASSUMPTIONS X2 — explainability does not require surfacing every internal step by default.

### Ranking

Signals are presented in a ranked order determined upstream (owned by Ranking & Surfacing; methodology deferred to NARRATIVE_ANALYSIS.md and EVALUATION.md). The UX does not alter rank; it exposes it.

The UX does provide:

* a visible ordering indicator, so the user knows ranking has been applied
* filters and sort options that re-scope the presented set — for example, ordering by subject time instead of rank — without claiming those secondary orderings are ranked importance
* a way to surface low-Confidence or low-Strength Signals explicitly when the user asks, so the default restraint does not become invisibility

No user affordance allows overriding the system's ranking methodology. The user can re-scope, not re-rank.

### Filtering

Filter dimensions available on Signal lists (Timeline, cross-Entity, Candidate pool):

* Signal Type
* Subject (Speaker where applicable)
* Theme
* Strength floor
* Confidence floor
* lifecycle state
* time range, by subject time or emission time (the UX must make which is in use unambiguous)
* Baseline thinness (affected / not affected)
* Basis Disagreement (present / absent)

Filters do not create rankings. They scope the set.

### Information Density

The default density is *headline-level*, with drill-down available on every Signal. This accommodates the depth-seeking audience (ASSUMPTIONS U2) without degrading to a wall of text at the entry surface.

Density discipline:

* no more than the anatomy fields needed for triage appear on the Timeline entry for a Signal
* Commentary is truncated with a clear affordance to expand; it is not silently cut
* Evidence is not inlined at headline level; it appears in Evidence View

The surface is designed to reduce the cost of noticing change, per [VISION.md](./VISION.md). Reducing cost means reducing visual noise, not reducing analytical content. The difference matters.

---

## Evidence Presentation

Evidence is surfaced as source-text excerpts resolved from the Span references carried by each Signal's Evidence records.

### Standard Case

For types where Evidence is a positive quotation (Narrative Drift, Confidence Shift, Contradiction Event, Structural Anomaly):

* each Span resolves to an excerpt rendered with Document, Segment, Speaker (where applicable), and event time
* excerpts are presented in a temporal ordering that honors the Signal's comparison structure — for Drift and Shift, prior Spans precede current Spans; for Contradiction, the paired statements are visually adjacent
* the user can open the originating Document at the locus of the excerpt
* where Span precision is finer than Utterance (for example, a character-offset sub-range), the finer locus is visible but framed within the enclosing Utterance

### Omission Event

Omission Events are a structurally distinct case. The Evidence is an absence: the current Document does not contain the expected ThemeInstances. The Spans carried on the Signal are drawn from prior Documents citing the now-absent Theme.

UX presentation of an Omission Event:

* the prior Spans are shown as "prior ThemeInstances" with full Document context
* the current Document's scope is shown, with an **Absence Marker** explicitly communicating that the Theme is not present here
* the Commentary must explain why the absence is considered meaningful — for example, "this Theme was present in each of the last four transcripts" — because the absence itself cannot be quoted
* the common false-positive patterns listed in [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) (Document scope change, compression, Speaker change, disclosed retirement) are surfaced where the system has flagged them, so the user can assess whether the absence is likely meaningful

"Absence Marker" is flagged for glossary extension.

### Evidence Density

By default, the Evidence View shows all Spans referenced by the Signal. Evidence is not truncated silently. For Signals with many Spans — for example, a sustained Narrative Drift citing framing evidence across several quarters — the view organizes Spans by Document and time but does not hide any.

---

## Communicating Strength

Strength is presented as a qualitative, type-relative indicator. The specific representation — whether discrete bands, tiers, or a constrained scalar — is not decided here ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defers this to MODEL_STRATEGY.md and NARRATIVE_ANALYSIS.md). Whatever the chosen representation, the UX applies the following invariants:

* Strength is shown as a property of the Signal, not as a cross-type comparable number
* Strength is not labeled as a probability, a percentage likelihood, or a forecast magnitude
* Strength is never displayed together with language implying external prediction (no "x% chance", no "likely to move")
* Strength is labeled with a term that communicates magnitude of deviation relative to the type — for example, "how large the observed shift is" — not absolute importance

The label for Strength in the UX should be plain ("Strength", "Magnitude of Shift") and consistent across types. Specific labels are deferred to copywriting work.

---

## Communicating Confidence

Confidence is presented separately from Strength and is the vehicle for structured skepticism in the UX.

Invariants, inherited from [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and CONTEXT §3.4:

* Confidence is not a probability of correctness and is not displayed as one
* Confidence is not rendered as a percentage
* Confidence is not rendered in units that imply statistical calibration unless such calibration has been established (it has not, for v1)
* Confidence is distinct from Strength visually and labelled distinctly
* a Signal with high Strength and low Confidence is a coherent combination; the UX must render it as such rather than surfacing only one of the two values

Confidence communication is paired with a human-readable reason. At least one of the following factors, where applicable, is surfaced alongside the Confidence indicator:

* Baseline thinness (for Signals that depend on a Baseline)
* Basis Disagreement (when heuristic and learned contributions diverged)
* narrow or sparse Evidence (few Spans, or Spans of limited locus precision)

Examples of Confidence language (illustrative, not prescriptive):

* "Confidence is lower because the Entity's history does not yet establish a stable Baseline."
* "Confidence is lower because the heuristic and learned analyses reached different conclusions about the magnitude of the shift."
* "Confidence is typical; Basis and Evidence are consistent with other Signals of this Type."

Language such as "80% confidence" or "probably accurate" is excluded. Those framings imply a calibration the project does not claim.

---

## Commentary Presentation

Commentary is bound to the Signal at emission time and is immutable ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)). The UX honors this:

* Commentary is shown in full on Signal Detail; excerpted on headline surfaces
* Commentary is never edited in-place; if the system has changed its reading of a narrative, the change is expressed as a new Signal that supersedes the prior one, with its own Commentary
* a Signal's Lineage is navigable from its Commentary panel — the user can follow the supersession chain and see how the Commentary evolved across Signal records
* Commentary is not marketing copy; example and house copy must avoid claims of prediction, recommendation, or sentiment (see Deliberate Non-Definitions)

For a superseded Signal, the UX makes visible:

* the original Commentary, unmodified
* a link forward to the Signal that supersedes it, with its (distinct, immutable) Commentary
* the temporal context — when each reading was emitted

This pattern honors the immutability commitment while ensuring the user can always find the most current reading.

---

## Navigating To Basis

From any Signal, the user reaches Basis Inspector in one step. The path is consistent across surfaces:

* Signal headline → Signal Detail → Basis Inspector
* Signal headline → Basis Inspector directly (where the surface supports shortcut affordances)

Basis Inspector does not require a separate query; the Basis chain is carried with the Signal in the backend contract (see [API_SPEC.md](./API_SPEC.md)). The UX may choose to defer rendering of the Basis chain until the user opens the Inspector, but does not defer availability.

Basis is not optional. A Signal without a resolvable Basis is not emitted ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)); the UX relies on this invariant rather than handling a "missing Basis" case.

---

## Historical Reconstruction And As-Of

As-of queries are a first-class UX concern ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) As-of Query; CONTEXT §2, §11).

Surface posture:

* an **As-Of View** control is visible on the Timeline, Signal Detail, NarrativeState, and cross-Entity surfaces
* the default As-Of is "now"; changing it recomputes the view against immutable history
* when As-Of is not "now", the surface carries a persistent indicator that the view is historical
* historical views show Signals in the lifecycle state they held at the Effective Time, not their current state — Lineage still renders, but transitions that occurred after the Effective Time are marked as future to the view

"As-Of View" is flagged for glossary extension.

The user must not be able to confuse a historical view with a current view. The indicator is persistent and the As-Of value is always legible.

---

## Lifecycle Legibility

Signals move through Candidate, Surfaced, Stale, Superseded, and Retired states ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Lifecycle). The UX makes each state legible without obscuring what the state means.

* **Candidate**: surfaced only in the Candidate Signal Review surface, or as an optional filter on the Timeline; never mixed into the default Timeline without an explicit opt-in; labeled as a lifecycle state, not a quality judgment.
* **Surfaced**: the default state for Timeline presence; no special indicator needed.
* **Stale**: shown in the Timeline when the time window is inclusive of Stale Signals; marked with an indicator that this observation is no longer current; not emphasized in current-state surfaces.
* **Superseded**: shown with a visible link to the Signal that supersedes it; the superseding Signal is the default object of engagement.
* **Retired**: shown only on historical surfaces and on the Lineage chain; the reason for retirement (invalidated Basis, corrected Evidence, other) is surfaced where available.

Lineage is rendered as a chain the user can walk, not as metadata. A user reading a Superseded Signal can always reach its successor; a user reading a Surfaced Signal can always reach its predecessors.

---

## Thin-History In The UX

The Thin-History Policy ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) is a first-class UX concern. It is made visible, not implicit.

Surface posture for Signals emitted under thin-history conditions:

* the Signal carries a visible **Thin-History indicator**, attached to the Confidence representation
* the Commentary explains, in plain language, what the thinness is about — usually Baseline thinness for a short-lived Entity or a newly-observed Speaker
* the Entity Timeline exposes Baseline thinness as a property of the Entity when the user is browsing, so it is not a surprise at the Signal level
* where the Policy has held a Signal at Candidate status, the Candidate Signal Review surface carries the explicit reason

The Thin-History indicator is a marker of the system's epistemic state, not a warning about the Entity. The UX copy must not suggest the Entity is "risky" — only that the system has less history to compare against.

---

## Structured Skepticism In The UX

Structured Skepticism (CONTEXT §3.4) is a design discipline at the UX level, not a label on the surface.

The UX reinforces skepticism through:

* separating Strength and Confidence everywhere (never a single composite display)
* avoiding probability language that the system does not earn
* surfacing Basis Disagreement honestly, as a structural feature of the Fusion Engine rather than a bug
* surfacing Baseline thinness as a structural property rather than an error state
* refusing to aggregate across Signal types into a single "score" for an Entity
* refusing to infer Entity-level or Speaker-level verdicts that the Signal taxonomy does not support
* surfacing Candidate and Stale states rather than hiding them
* allowing the user to read Evidence in source context, so the user's judgment is not mediated entirely by Commentary

The surface should make it easy to say, "this Signal has high Strength, low Confidence, and the following supporting text — I will judge its meaningfulness myself." That is the intended user experience.

---

## Example Signal Presentations

Illustrative only. Copy is not prescriptive. Each example shows the minimum anatomy rendered at the Signal headline level.

### Example 1: Narrative Drift, Surfaced, Typical Confidence

> **Narrative Drift — Entity: ACME Corp**
> Strength: moderate. Confidence: typical.
> Subject time: Q3 transcript; Baseline covers the prior four quarters.
> Commentary: "Emphasis on margin discipline has moved toward language about reinvestment. The shift appears across prepared remarks and Q&A and is consistent with prior-period comparisons."

### Example 2: Confidence Shift, Surfaced, Thin-History

> **Confidence Shift — Entity: ACME Corp, Speaker: CFO**
> Strength: large. Confidence: lower than typical. Thin-History: yes.
> Subject time: Q3 transcript; Speaker Baseline covers the prior two quarters.
> Commentary: "Hedging language has increased meaningfully in the CFO's Q&A responses. Confidence is lower than typical because this Speaker's Baseline is still thin."

### Example 3: Omission Event, Surfaced

> **Omission Event — Entity: ACME Corp, Theme: International Expansion**
> Strength: moderate. Confidence: typical.
> Subject time: Q3 transcript; Theme present in the prior six transcripts.
> Commentary: "The International Expansion Theme, present and discussed in each of the last six earnings calls, is absent in this transcript. Scope and segmentation appear consistent with prior calls."

### Example 4: Contradiction Event, Candidate, Basis Disagreement

> **Contradiction Event — Entity: ACME Corp — Candidate**
> Strength: large. Confidence: lower than typical. Basis Disagreement: present.
> Subject time: Q3 transcript vs. prior quarterly filing.
> Commentary: "A statement in the Q3 call is in apparent tension with a prior-quarter filing's disclosed commitment. The heuristic and learned analyses reached different conclusions about whether the statements are incompatible."

These examples use the anatomy fields required by [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md). None of them imply prediction, recommendation, or sentiment.

---

## What The UX Deliberately Excludes

The following are excluded by design, inherited from [CONTEXT.md](./CONTEXT.md) §10, [SCOPE.md](./SCOPE.md) Non-Goals, and [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Deliberate Non-Definitions:

* no "sentiment" score, polarity indicator, or positive/negative framing on any Signal or any Entity
* no "prediction" or "forecast" language; the UX does not tell the user what will happen
* no "recommendation"; the UX does not advise action, including no buy/sell/hold language, no "you should watch this", no prescriptive framing
* no "alpha" or trading-signal language
* no Entity-level aggregate "score" combining Signals across types
* no UI affordance for acting in markets
* no "AI" or "AI-powered" framing; the surface names the analytical components ("heuristic analysis", "learned analysis", "Fusion Engine") when it names anything
* no override of ranking or Confidence by the user — those are upstream concerns
* no user-editable Signal content; Signals are system outputs, not documents
* no hiding of Candidate, Stale, or Retired Signals — each lifecycle state is accessible, even if not default-visible

These are exclusions of concept, not only of copy. The UX must not re-introduce excluded concepts through visual shorthand, color semantics, or iconography.

---

## What This Document Is Not

* not a visual design document
* not a frontend implementation specification
* not a copywriting style guide (example copy is illustrative)
* not an authentication or account experience document (deferred to SECURITY_AND_PRIVACY.md)
* not a specification of specific interaction paradigms (click, drag, keyboard shortcut conventions, etc.)
* not a performance or latency specification
* not an accessibility specification (a clear gap; see Deferred Decisions)

---

## Deferred Decisions

* visual design, component library, layout, color semantics, iconography, typography — deferred to implementation
* specific interaction paradigms — deferred to implementation
* authentication and account UX — deferred to SECURITY_AND_PRIVACY.md and implementation
* accessibility posture — deferred; should be named as an owner in a future document
* mobile and small-screen experience — deferred
* alert or notification experience, if any — deferred; the v1 surface is pull-based
* personalization (followed Entities, saved views, alerts) — deferred; aligned with [SCOPE.md](./SCOPE.md) Deferred
* multi-user and collaborative experience — deferred ([SCOPE.md](./SCOPE.md) Deferred)
* reviewer-facing UX for the Evaluation Harness — separate concern, owned by EVALUATION.md and downstream implementation
* specific copy for Strength and Confidence labels — deferred to copywriting
* specific rendering of Basis Disagreement — deferred; this document commits only that it is surfaced honestly
* specific density at which Evidence groups are summarized for very long Evidence sets — deferred to implementation

---

## Glossary Additions Recommended

The following terms are introduced in this document and should be promoted into [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **As-Of View** — the user-facing reconstruction of a surface at a specified Effective Time; the UX realization of an As-of Query.
* **Absence Marker** — the explicit rendering of a Theme's absence on an Omission Event, given that absence cannot be quoted.
* **Thin-History Indicator** — the visible marker that a Signal was emitted under thin-history conditions and carries reduced Confidence accordingly.
* **Signal Headline** — the minimum anatomy projection surfaced at list-level before drill-down (Type, Subject, Strength indicator, Confidence indicator, Commentary excerpt, lifecycle state if non-Surfaced).

The first three are project-specific UX concepts worth canonicalizing. The fourth is primarily a UX term but mirrors a serialization shape named in [API_SPEC.md](./API_SPEC.md) (Signal Digest); either term may become the glossary canonical, with the other as a synonym.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes their user-facing commitments.
* [VISION.md](./VISION.md) establishes the orientation — reducing the cost of noticing change — that the default surface is built around.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) U1–U6 bound the audience assumptions this document works from.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; this document recommends additions listed above.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) is the contract for Signal anatomy; this document presents every anatomy field.
* [DATA_MODEL.md](./DATA_MODEL.md) supplies the underlying entities the UX reads from.
* [ARCHITECTURE.md](./ARCHITECTURE.md) owns the boundary between backend output and user-facing surface; this document consumes that boundary, it does not alter it.
* [API_SPEC.md](./API_SPEC.md) defines the contract this surface pulls against; anatomy rendered here corresponds field-for-field to serialization defined there.
* NARRATIVE_ANALYSIS.md and EVALUATION.md own ranking and lifecycle transition policy; this document does not alter those.
* MODEL_STRATEGY.md owns Commentary generation mechanics; this document commits only to Commentary's presentation posture.
* SEARCH_AND_RETRIEVAL.md owns internal query mechanics; this document does not duplicate them.
