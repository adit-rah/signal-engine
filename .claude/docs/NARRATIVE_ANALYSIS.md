# NARRATIVE_ANALYSIS.md

## Purpose Of This Document

NARRATIVE_ANALYSIS.md defines the operational analytical policy by which the Signal Engine produces meaningful Signals in production: how Baselines are constructed and maintained, what thresholds govern Signal emission, how Signals transition through their lifecycle, how Themes are curated, how Signals are ranked, how different Signal types interact, and how promoted Candidate Types are used once they enter the taxonomy.

This document is conceptual. It commits to the shape of each policy but generally does not commit to specific numeric thresholds; numeric values are an empirical concern informed by EVALUATION.md and EXPERIMENTATION.md.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, [CONTEXT.md](./CONTEXT.md) is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## How To Read This Document

* Baselines are addressed first because most Signal types depend on them
* per-type threshold shape is specified; specific numeric values are deferred
* the Signal lifecycle transition policy is stated as operational rules, not as mutations of immutable Signal records
* ranking is specified as within-type ordering, not as a cross-type score
* Theme curation reconciles heuristic, learned, and human-curated provenance under a single identity model
* cross-Signal interaction is represented as co-occurrence and reinforcement, not as type collapse

---

## Guiding Commitments Inherited

Held as invariants throughout:

* Strength and Confidence are distinct ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Signal Anatomy; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md))
* Signals are immutable once emitted; lifecycle transitions are new records with Lineage ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
* thin-history Entities prefer reliability over coverage ([CONTEXT.md](./CONTEXT.md) §8 Thin-History Posture; [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Thin-History Policy)
* false positives are costlier than false negatives in early development ([CONTEXT.md](./CONTEXT.md) §14; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3)
* explainability is system-wide ([CONTEXT.md](./CONTEXT.md) §3.3); no policy here may be applied without preserving the Basis chain
* temporal reasoning is mandatory ([CONTEXT.md](./CONTEXT.md) §11); every policy in this document is stated against the temporal model in [DATA_MODEL.md](./DATA_MODEL.md)
* ranking methodology is a v1 concern owned here ([SCOPE.md](./SCOPE.md) Open Questions)
* the low-capital posture bounds how much continuous recomputation this document may assume ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5; [ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint)

---

## Baseline Construction And Maintenance

Baselines are the reference state against which most Signals are measured ([DATA_MODEL.md](./DATA_MODEL.md) Baseline; [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md)). Their construction is owned by this document; their storage and validity-interval semantics are owned by [DATA_MODEL.md](./DATA_MODEL.md); their exposure as artifacts is owned by Baseline Maintenance ([ARCHITECTURE.md](./ARCHITECTURE.md) component 4).

### Two Baseline Scopes

A Baseline is maintained per Entity and, where the relevant Signal type warrants it, per Speaker within an Entity. The two scopes exist because different Signal types answer different questions:

* **Entity Baseline** — patterns expected for the Entity's communication at the Entity level, across whichever Speakers it fields. Referenced by Narrative Drift and Structural Anomaly at the Entity scope.
* **Speaker Baseline** — patterns expected for a specific Speaker within an Entity. Referenced by Confidence Shift and by Speaker-scoped instances of Narrative Drift and Structural Anomaly.

Speaker Baselines are scoped within an Entity; the same person, if relevant for multiple Entities, produces separate Speaker Baselines. Cross-Entity Speaker Baselines are out of scope for v1.

### What A Baseline Holds

A Baseline is a composite reference, not a single scalar. At the policy level it holds, at a minimum:

* summary statistics over Baseline-contributing Documents' structural features (for Structural Anomaly)
* summary representations of Theme prominence and framing (for Narrative Drift)
* summary representations of certainty-bearing features (for Confidence Shift, per-Speaker)
* a queryable **Baseline thinness** property indicating sufficiency of the underlying history ([DATA_MODEL.md](./DATA_MODEL.md); [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Baseline Thinness)
* a reference to the DerivationRun that produced the Baseline ([DATA_MODEL.md](./DATA_MODEL.md))

The specific internal representation of each component is owned by MODEL_STRATEGY.md where a learned model contributes, and by DOCUMENT_PROCESSING.md where heuristic features are involved.

### Update Policy

When a new Document arrives for an Entity:

* the current Baseline remains in place and keeps its valid-time interval closed at the new Document's observation time
* a new Baseline is produced whose valid-time begins at or after the new Document's event time, and which incorporates the new Document's contribution
* the new Baseline is a new immutable record; it does not overwrite the prior one ([DATA_MODEL.md](./DATA_MODEL.md) Immutability And History)
* the Signal detection step that considers the new Document compares it against the *prior* Baseline, not the post-update Baseline, so that the comparison is legible

Update cadence is per-Document, not continuous. The system does not maintain a rolling Baseline updated on every minor change; Baselines change step-wise with new Documents.

### Preservation Of Historical Baselines

All prior Baselines are retained. An as-of query at any past Effective Time returns the Baseline in force at that time ([DATA_MODEL.md](./DATA_MODEL.md) Temporal Model; [ARCHITECTURE.md](./ARCHITECTURE.md) Temporal Reasoning).

When the Baseline construction method itself changes (for example, the Structural-Baseline Model is replaced in MODEL_STRATEGY.md), a new DerivationRun produces a new valid-time series. Older Baselines under the prior DerivationRun are retained; the two series coexist. Which series is authoritative for a given Effective Time is determined by which DerivationRun was current at that time, not by recency of the method itself.

### Re-Derivation Posture

Baselines are re-derivable. The system does not require re-derivation to be continuous ([ARCHITECTURE.md](./ARCHITECTURE.md) Low-Capital Constraint). When a Baseline is re-derived — on method change, on correction of an ingested Document, on a re-run of the pipeline — the result is a new record, and the prior record is preserved.

Divergence between a prior Baseline and a re-derived Baseline is itself an operational artifact whose detection is owned by [OBSERVABILITY.md](./OBSERVABILITY.md). This document does not define what constitutes an acceptable divergence; that is a matter for EVALUATION.md and, where appropriate, TESTING_STRATEGY.md.

---

## Thresholds Per Signal Type

Each Signal type's emission is governed by thresholds whose *shape* is committed here and whose *numeric values* are deferred. Numeric values are set empirically through EVALUATION.md's human review and EXPERIMENTATION.md's replay, not in this document.

Per-type threshold shape draws on [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)'s strong-vs-weak criteria.

### Narrative Drift

Thresholds govern:

* **magnitude** — how far the current Document's framing and emphasis deviate from the Baseline
* **sustain** — whether drift is evident in more than one observation period, as a gate on weak single-observation candidates
* **multi-feature consistency** — whether drift is visible in more than one framing feature, to guard against single-feature sensitivity
* **concurrent Basis requirement** — whether both heuristic and learned contributions cross their per-type thresholds before a Signal is promoted beyond Candidate

Emission produces a Signal at Candidate status when at least one analytical side crosses its threshold; promotion to Surfaced follows the Lifecycle Transition Policy below.

### Confidence Shift

Thresholds govern:

* **magnitude** — how far the current Speaker's certainty features deviate from the Speaker Baseline
* **sustain** — whether the shift is evident across more than one observation period for the same Speaker
* **feature consistency** — whether the shift is visible in more than one certainty-bearing feature
* **scope guard** — whether the shift is concentrated in a single topic (in which case a lower-scope Signal may be appropriate) or is pervasive across topics

Because [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) warns against topic-specific hedging being mis-read as a Confidence Shift, the scope guard is non-optional.

### Omission Event

Thresholds govern:

* **prior recurrence depth** — the minimum count of prior Documents in which the Theme appeared as a ThemeInstance; below this depth, the Theme is not considered established enough to have an Omission Event
* **prior consistency** — how regularly the Theme appeared (not merely how many times) across the recurrence window
* **absence sustain** — whether the absence is present in one current Document or across a sequence
* **artefactual guard** — an explicit check that Document scope, Segment structure, and Speaker changes do not independently explain absence ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) Omission Event Common false-positive patterns)
* **learned verification** — agreement from the Omission-Verification Model in MODEL_STRATEGY.md that the Theme is semantically absent, not merely restated tersely

Omission Event is the Signal type most sensitive to thin history; the minimum prior recurrence threshold is the primary Thin-History Policy lever for this type.

### Contradiction Event

Thresholds govern:

* **comparability** — the strength of the comparability basis from the Contradiction-Alignment Model; candidates whose comparability basis is weak are suppressed at the Candidate stage
* **incompatibility** — the degree to which the two statements are judged incompatible rather than merely different
* **update-versus-contradiction gate** — a check for disclosed correction language, to distinguish updated facts from contradictions
* **scope-match gate** — a check that the two statements apply to comparable scopes (period, segment, unit)
* **rhetorical gate** — a check that neither statement is hypothetical or illustrative rather than committed

Contradiction Event is the one type for which per-Document history is not the primary gate; its thresholds depend on the candidate pair's internal comparability, and it is therefore less affected by Thin-History Policy.

### Structural Anomaly

Thresholds govern:

* **multi-feature deviation** — whether multiple structural features are simultaneously outside Baseline variance, rather than a single outlier
* **sustain-within-Document** — whether the anomaly is present across the Document or concentrated in a brief passage
* **variance adjustment** — correction for Baseline thinness: a thin Baseline's variance is wider, not narrower, and the threshold honors this
* **disclosed-circumstance guard** — an explicit check for disclosed special circumstances (format change, unusual call) that could explain structural deviation

Structural Anomaly is the most sensitive to small-sample Baselines; variance adjustment is the primary mechanism by which Thin-History Policy moderates this type.

---

## Thin-History Policy Thresholds

[SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) commits the shape of the Thin-History Policy. This document specifies its operational thresholds by shape, with numeric values deferred.

The policy has three operational levers:

### 1. Baseline-Thinness-Driven Confidence Adjustment

For Signals that depend on a Baseline (Narrative Drift, Confidence Shift, Structural Anomaly):

* Baseline thinness is a direct input to Confidence ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md); MODEL_STRATEGY.md Fusion Engine: Confidence Computation)
* the shape of the adjustment is monotone — thinner Baselines yield lower Confidence — and is parameterized per type, because the relationship is not uniform
* the adjustment does not affect Strength; Strength remains the magnitude-of-deviation measure

### 2. Candidate-Only Emission Under Severe Thinness

Where Baseline thinness crosses a per-type severity threshold:

* the Signal is emitted at Candidate status only and is not automatically promoted to Surfaced
* promotion from Candidate to Surfaced requires human review through the Evaluation Harness
* the severe-thinness gate is orthogonal to Strength; a strong Signal under a severely thin Baseline is still gated

### 3. Minimum Prior Recurrence For Omission Event

For Omission Event specifically:

* below the minimum recurrence threshold, no Omission Event Signal is emitted — not even as Candidate
* this is a stronger policy than for the other types because an Omission Event with insufficient prior recurrence is structurally meaningless

Specific numeric thresholds for all three levers are deferred. Their empirical determination is an EVALUATION.md and EXPERIMENTATION.md concern.

### Reliability-Over-Coverage As Operational Principle

Across the three levers, the bias runs consistently toward withholding or candidate-gating rather than surfacing. Missing a genuine signal on a thin-history Entity is preferred over surfacing a spurious one ([CONTEXT.md](./CONTEXT.md) §8 Thin-History Posture; [ASSUMPTIONS.md](./ASSUMPTIONS.md) S3). The threshold shapes follow from this posture rather than from a symmetric cost analysis.

---

## Signal Lifecycle Transition Policy

[SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the lifecycle states (Candidate, Surfaced, Stale, Superseded, Retired) and the immutability posture: transitions are expressed as new Signal records with Lineage references, not as mutations of originals. This document specifies the transition policy itself.

### Candidate → Surfaced

A Candidate is promoted to Surfaced when one of the following holds:

* **automatic promotion** — the Signal's Strength crosses its type's automatic-promotion threshold and its Confidence is above the type's Surfaced minimum, and no gating condition applies
* **gated promotion** — a gating condition (severe Baseline thinness, Commentary grounding failure, contested comparability in Contradiction Event) requires human review through the Evaluation Harness; on confirmation, a new Signal record is written with Surfaced status and Lineage referencing the Candidate
* **no promotion** — the Candidate remains in Candidate status indefinitely, visible to the Evaluation Harness but not to user-facing surfaces

Candidate status is not a failure state. It is the explicit "not yet trusted to user-facing surfaces" pool. The proportion of Signals that remain in Candidate over time is itself an evaluation signal (EVALUATION.md).

### Surfaced → Stale

A Surfaced Signal becomes Stale when its observation is no longer current. Staleness is per-type:

* for types that describe a bounded subject time (a Contradiction Event in a specific quarter), Stale is triggered when the subject time has passed the type's freshness window
* for types that describe an ongoing state (a sustained Confidence Shift), Stale is triggered when a subsequent Document's Baseline-relative comparison would restart the analysis and no new Signal has been emitted

Freshness window shapes are per-type; specific values are deferred. The principle is that Stale is about recency of observation, not about correctness.

### Surfaced → Superseded

A Surfaced Signal is superseded when a subsequent Signal concerns the same Entity (or Entity + Speaker), the same type, and an overlapping or subsequent subject time, and the subsequent Signal has been judged to describe the same phenomenon more accurately.

* supersession is expressed as a new Signal record whose Lineage references the prior
* the prior Signal remains available for historical query; it is not deleted ([DATA_MODEL.md](./DATA_MODEL.md) Immutability And History)
* supersession is automatic when a same-subject, same-type emission crosses type-specific supersession thresholds; below those thresholds, both Signals remain Surfaced in their respective time windows

### Surfaced → Retired

A Signal is retired when its Basis or Evidence is found to be invalid:

* a DerivationRun referenced by the Basis has been recalled
* the Evidence Spans point to text that has been corrected or withdrawn
* human review through the Evaluation Harness confirms that the Signal is not meaningful on review

Retirement is expressed as a new record with Lineage. The original Signal is not deleted. Retirement is distinct from Stale: Stale says "no longer current"; Retired says "should not have been surfaced."

Whether review-driven Retirement happens in practice, and how it interacts with reviewer feedback, is specified in EVALUATION.md.

### Candidate → Retired

A Candidate Signal may be retired without ever having been Surfaced when its Basis or Evidence is invalidated. The mechanics match Surfaced → Retired.

### Transitions And Immutability

No transition mutates a Signal record. Every transition produces a new record, whose Type, Subject, Basis, Evidence, Commentary, and emission metadata reflect the post-transition state, and whose Lineage references the prior record. The Signal Store ([ARCHITECTURE.md](./ARCHITECTURE.md) component 9) enforces this structurally; this document specifies when transitions occur.

---

## Ranking And Surfacing Policy

[SCOPE.md](./SCOPE.md) Open Questions flags ranking as owned by this document; [CONTEXT.md](./CONTEXT.md) §9 commits to ranked Signal outputs. This section specifies the ranking policy at the signal layer. The user-facing presentation of ranked Signals remains a [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) concern composed on top of this layer's output.

### Within-Type Ordering

Within a Signal type, Strength is the primary ordering quantity. Strength is bounded and type-relative ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)).

* ties in Strength are broken by Confidence, with higher Confidence ranked above lower
* ties in both are broken by recency of emission
* within-type ranking is stable across queries given the same underlying Signal set

### No Cross-Type Aggregate Score

The policy explicitly excludes a cross-type aggregate ranking score. Strength is type-relative by construction, and collapsing it into a cross-type scalar would violate that structural invariant.

Consumers that need a cross-type surface (for example, "top Signals for Entity E this quarter") compose per-type rankings; the composition rule is a presentation concern for [USER_EXPERIENCE.md](./USER_EXPERIENCE.md), informed by the false-positive posture.

### Confidence As A Gate, Not A Ranker

Confidence gates promotion from Candidate to Surfaced (see Lifecycle Transition Policy) and gates which Signals are shown on user-facing surfaces. It is not used as a primary ranker within a type, because ranking by Confidence within a type would bias the ranking away from strong-but-uncertain Signals toward weak-but-certain Signals — the opposite of the useful surface.

### Stale, Superseded, And Retired

* Stale Signals are not removed from ranking; they are re-ordered to the end of current-state views
* Superseded Signals are not shown on current-state views; they remain available via historical query
* Retired Signals are not shown on current-state views; they remain available via historical query with their retirement state clearly marked

The specific surfaces on which each lifecycle state appears is a [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) concern.

### Thin-History And Ranking

Surfaced Signals for thin-history Entities carry the Confidence reduction introduced by the Thin-History Policy. This affects which Signals meet the Surfaced minimum but does not affect within-type ordering among Surfaced Signals, because Strength remains the primary ordering quantity.

### Ranking Is Observable

The ranking produced for a given query, at a given time, is itself an operational artifact. Whether it was produced under a given DerivationRun, and whether re-ranking under a different DerivationRun produces a different ordering, is observable under [OBSERVABILITY.md](./OBSERVABILITY.md). Whether a given ranking is *good* — reflective of importance as a human reader would judge it — is an EVALUATION.md concern.

---

## Theme Curation

Themes are the unit that supports Narrative Drift and Omission Event analysis ([DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) Theme; [DATA_MODEL.md](./DATA_MODEL.md) Theme). Theme curation is owned by this document.

### Three Theme Provenances, One Identity Model

Themes may be produced through three mechanisms:

* **heuristic themes** — proposed by rule-based analysis over domain text
* **learned themes** — proposed by the Theme-Discovery Model in MODEL_STRATEGY.md
* **human-curated themes** — introduced by analysts or researchers, typically to anchor a specific analytical concern

All three produce Themes under the same identity model. A Theme's provenance is recorded on the Theme record as a first-class field but does not alter how the Theme is referenced downstream. ThemeInstances reference a Theme by canonical identifier; they do not care how the Theme was originated.

### Theme Lifecycle

Themes are proposed, reviewed, and either promoted, merged, or retired.

* a **proposed** Theme is visible to Theme curation workflows but is not yet considered canonical; ThemeInstances may be drafted but not counted toward Baselines
* a **promoted** Theme is canonical; its ThemeInstances contribute to Theme prominence measurements and Baseline construction
* a **merged** Theme has been determined to duplicate an existing Theme; its prior ThemeInstances are reconciled to the surviving Theme; a merged Theme's identifier is retained and maps to the surviving one
* a **retired** Theme has been withdrawn as no longer meaningful; its prior ThemeInstances are preserved with the retired Theme identifier, but the Theme no longer accepts new instances and no longer contributes to new Baselines

Theme lifecycle transitions are expressed as new Theme records or merge records rather than as in-place edits, consistent with the immutability posture in [DATA_MODEL.md](./DATA_MODEL.md).

### Promotion Workflow

Promotion from proposed to canonical is a review workflow. The review mechanics are owned by EVALUATION.md; this document commits the shape:

* a proposal carries a draft name, a description, representative ThemeInstances, and (where relevant) the originating DerivationRun
* review criteria include whether the Theme is semantically distinct from existing Themes, whether it is stable across Documents, and whether it is useful for tracking over time
* promotion produces a Theme record at canonical status; rejection preserves the proposal but does not promote

Theme promotion is distinct from Signal-type promotion through the Candidate-Type Pool. They share a spirit but are separate workflows.

### Human-Curated Themes And Operational Coexistence

Human-curated Themes coexist with heuristic and learned Themes. The system does not privilege one provenance over another, but the operational policy is:

* a human-curated Theme that conflicts with an automatically proposed Theme is reconciled through the Theme merge mechanism
* human-curated Themes may be introduced for analytical purposes that no automatic mechanism has yet discovered; this is a legitimate use and must not be obstructed by automation
* automatic mechanisms must not silently retire a human-curated Theme; retirement of a human-curated Theme requires human review

---

## Cross-Signal Interaction

Signals of different types may relate to one another. [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) names this concern explicitly and defers interaction modeling to this document.

### The Policy: Represent, Do Not Collapse

Cross-signal interactions are represented as explicit relationships on Signal records, not by collapsing interacting Signals into a single composite type. Strength remains type-relative; interactions do not produce a cross-type score.

### Kinds Of Interaction Modeled In V1

Three kinds of interaction are modeled. Each is a relationship attached to Signals, not a new Signal type.

* **co-occurrence** — two Signals of different types concerning the same Entity (and, where relevant, Speaker) with overlapping subject time. Example: an Omission Event co-occurring with a Confidence Shift concerning the same Speaker. The co-occurrence relationship is recorded but does not cause either Signal's Strength or Confidence to change.
* **reinforcing evidence** — two Signals share Evidence Spans or overlapping Basis contributions. The reinforcement is recorded on both Signals as a relationship; it does not merge the Signals.
* **contradiction between Signals** — two Signals concerning the same Entity and overlapping subject time assert observations that are incompatible (for example, a Contradiction Event contests a narrative the Narrative Drift Signal describes). The contradiction is recorded as a relationship and is a first-class input to the lifecycle transition policy: the conflicting Signals remain Surfaced but may be held for review through the Evaluation Harness.

Additional interaction kinds are deferred. Adding a kind is an extension to this document, not to [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md).

### Use Of Interaction In Ranking And Surfacing

Interactions may influence surfacing policy but do not alter within-type ranking.

* a Signal with a reinforcing-evidence relationship to another Surfaced Signal may be surfaced preferentially within its type when the presenting view wishes to highlight reinforcement; this is a composition concern for [USER_EXPERIENCE.md](./USER_EXPERIENCE.md)
* a Signal in a contradiction-between-Signals relationship is not automatically suppressed; both remain available with their relationship recorded

### Use Of Interaction In Confidence

Interactions may modestly inform Confidence.

* reinforcing-evidence relationships slightly raise Confidence, because agreement across types is epistemic support
* contradiction-between-Signals relationships slightly lower Confidence for both Signals, because disagreement across types is epistemic weakness

The effect is bounded and is secondary to the primary Confidence inputs in MODEL_STRATEGY.md. Its specific magnitude is deferred and informed by EVALUATION.md.

---

## Use Of Promoted Candidate Types

The Candidate-Type Pool ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) owns the state machine. EVALUATION.md owns the promotion workflow. This document owns what happens once a type is promoted.

### Integration Of A Promoted Type

On promotion of a new Signal type into the taxonomy:

* the Fusion Engine begins emitting the new type under the same contract as existing types — Basis mandatory, Evidence mandatory, Strength and Confidence present and distinct, Commentary generated ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))
* this document extends its Thresholds Per Signal Type section with the new type's threshold shape, drawn from the proposal artifact EVALUATION.md produced
* Baseline construction for the new type is introduced as an extension to the Baseline Construction And Maintenance section; the new type's Baseline components are either added to the Entity Baseline or to the Speaker Baseline, as the proposal specifies
* the new type enters the lifecycle transition policy under the same rules as existing types; if it has type-specific transition shapes, they are added to Signal Lifecycle Transition Policy

### Relationship Of A Promoted Type To Existing Types

The promotion review (EVALUATION.md) is required to establish that the new type is distinct from existing types. Once promoted, relationships between the new type and existing types are modeled through Cross-Signal Interaction:

* co-occurrence with existing types is recorded where overlapping
* reinforcing-evidence relationships with existing types are recorded where the new type shares Evidence or Basis contributions
* contradiction-between-Signals relationships are recorded where incompatible

The new type does not retrospectively re-classify existing Signals. Historical Signals of existing types remain as they were; the new type applies prospectively, subject to re-derivation on demand for historical analysis.

### Theme-Discovery Proposals Distinguished From Candidate-Type Proposals

The Theme-Discovery Model in MODEL_STRATEGY.md produces two kinds of output: Theme proposals and Signal-type proposals. Theme proposals enter the Theme curation workflow above. Signal-type proposals enter the Candidate-Type Pool ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) and are reviewed under EVALUATION.md. The two workflows do not short-circuit one another.

---

## Operationalizing Reliability Over Coverage For Thin-History Entities

[CONTEXT.md](./CONTEXT.md) §8 commits thin-history Entities to reliability over coverage. Across the policies above, this manifests as:

* Confidence is reduced on any Signal referring to a thin Baseline (Thin-History Policy Thresholds lever 1)
* severe thinness gates emission at Candidate status pending human review (lever 2)
* Omission Event is suppressed entirely below the minimum prior recurrence threshold (lever 3)
* thin Baselines produce wider variance estimates for Structural Anomaly, not narrower, so that normal variability is not mistaken for anomaly
* within-type ranking among Surfaced Signals is unchanged for thin-history Entities; they are ranked on Strength as elsewhere, but fewer of their Signals reach Surfaced in the first place

The cumulative effect is a system that emits less for thin-history Entities than it does for historically deep ones, with the outputs it does emit held to a higher epistemic bar. This is the operational manifestation of the posture.

---

## What This Document Does Not Specify

* specific numeric thresholds for any lever above — empirically determined through EVALUATION.md and EXPERIMENTATION.md
* the internal representation of Strength and Confidence (scalar, band, tier) beyond the distinction — deferred between this document and MODEL_STRATEGY.md; the empirical choice is informed by EVALUATION.md
* how Signals are presented to users — [USER_EXPERIENCE.md](./USER_EXPERIENCE.md)
* model architectures — MODEL_STRATEGY.md
* human-review mechanics for Candidate-Type Pool promotion — EVALUATION.md
* how Themes and Signal types are proposed by learned models — MODEL_STRATEGY.md
* observability of Baselines, lifecycle transitions, and rankings — [OBSERVABILITY.md](./OBSERVABILITY.md)
* retention of historical Baselines beyond general immutability — DATA_GOVERNANCE.md

---

## Deferred Decisions

* numeric threshold values per Signal type — empirical, EVALUATION.md and EXPERIMENTATION.md
* numeric Thin-History Policy thresholds per type — empirical
* freshness window sizes per type for Stale transitions — empirical
* specific supersession thresholds per type — empirical
* Confidence magnitudes attached to cross-signal interaction — empirical
* cadence of the Theme-Discovery Model (run rate for Theme and Candidate-Type proposals) — bounded by the low-capital constraint; specific cadence deferred
* policy for reconciliation of Speaker identity across Entities where the same person moves between them — deferred; out of v1 scope for Speaker Baselines

---

## Open Questions

* how aggressively to restart the Narrative Drift analysis when Speaker turnover is observed — a trade between missing drift and mistaking Speaker change for drift; informed by review outcomes in EVALUATION.md
* how to represent a partial-promotion outcome for a Candidate Type that is promoted on a probationary basis — flagged for EVALUATION.md; this document's Use Of Promoted Candidate Types section currently assumes a binary promoted/not state and will extend if EVALUATION.md commits a probationary state
* how to treat Signals whose Basis comes entirely from one analytical side due to persistent Degraded Mode — this document currently treats Degraded Mode as reducing Confidence and recording the missing side on Basis; whether extended Degraded Mode should also gate promotion to Surfaced is flagged for review
* whether Theme-prominence measurements themselves become a first-class surfaced artifact (not a Signal, a Theme trend report) — an extension flagged but not committed here

---

## Recommended Glossary Extensions

Flagged for addition to [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md):

* **Entity Baseline** — a Baseline scoped to an Entity's Document-level patterns, used by Narrative Drift and Entity-scoped Structural Anomaly
* **Speaker Baseline** — a Baseline scoped to a Speaker within an Entity's communications, used by Confidence Shift and Speaker-scoped Signals
* **Freshness Window** — a type-specific duration after which a Surfaced Signal is eligible for transition to Stale
* **Signal Interaction Record** — the relationship record attaching co-occurrence, reinforcing-evidence, and contradiction-between-Signals links across Signals

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative; this document realizes their analytical commitments operationally
* [VISION.md](./VISION.md) and [ASSUMPTIONS.md](./ASSUMPTIONS.md) bound the posture
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms are flagged above
* [DATA_MODEL.md](./DATA_MODEL.md) owns Baseline, Theme, Signal, and DerivationRun as data-model artifacts; this document owns how they are produced and used analytically
* [ARCHITECTURE.md](./ARCHITECTURE.md) names the components (Baseline Maintenance, Fusion Engine, Ranking & Surfacing) whose policy this document supplies
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) owns Signal Anatomy, Candidate-Type Pool state machine, and Thin-History Policy shape; this document supplies operational thresholds and lifecycle policy
* MODEL_STRATEGY.md owns Fusion Engine mechanics at the model level, model versioning, and Degraded Mode behavior; this document owns the operational policy that the mechanics execute
* EVALUATION.md owns human review, Candidate-Type Pool promotion workflow, and empirical determination of thresholds
* EXPERIMENTATION.md owns replay-based evaluation of threshold and policy changes, graduating validated changes to this document
* [OBSERVABILITY.md](./OBSERVABILITY.md) owns the operational view of lifecycle transitions and ranking; this document owns the policies those views observe
* [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) composes the ranked and surfaced Signals into user-facing views; this document does not pre-decide presentation
