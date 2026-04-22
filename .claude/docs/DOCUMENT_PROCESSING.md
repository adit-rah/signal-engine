# DOCUMENT_PROCESSING.md

## Purpose Of This Document

DOCUMENT_PROCESSING.md specifies how a Raw artifact becomes a Normalized Document, a sequence of Segments, and a sequence of Utterances in [DATA_MODEL.md](./DATA_MODEL.md) terms. It covers the conceptual transformations that take Raw text into a canonical form, how Segments are identified for v1 Transcripts, how Speaker attribution is performed within a Document, how normalization is versioned under DerivationRuns, and how Span precision is preserved through the transformation.

This document is conceptual. It does not select tokenizers, regular-expression libraries, or segmentation algorithms. It defines the contract Document Processing must satisfy so that downstream analytical components — Heuristic Analysis, Representation, Learned Analysis, Baseline Maintenance, and ultimately the Fusion Engine — can depend on the Normalized form.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). The Document Processing component's responsibilities are defined in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## How To Read This Document

* transformations are described by what they produce, not by how
* every transformation is versioned under a DerivationRun; re-derivation is a first-class operation
* Span precision is an invariant through normalization; every requirement below is a consequence
* the boundary with [INGESTION_SPEC.md](./INGESTION_SPEC.md) is upstream; the boundary with downstream analysis is stated at the end

---

## Guiding Invariants

Held for every Normalized artifact:

* Raw is immutable; normalization does not mutate Raw (DATA_MODEL.md §Immutability And History)
* re-normalization under new logic produces a new Normalized artifact under a new DerivationRun; prior Normalized artifacts are retained (DATA_MODEL.md §Immutability And History)
* every Normalized artifact carries a reference to the Raw artifact it was derived from and to the Document Processing DerivationRun that produced it
* every Span derived from Normalized text is resolvable back to its locus in Raw text, and forward to its locus in any subsequent Normalized version derived from the same Raw
* Document Processing does not make semantic claims about content; those are analytical-layer concerns (CONTEXT §3.2.A, §3.2.B)

---

## Boundary Against INGESTION_SPEC.md

Document Processing begins at a committed Document record with its Raw artifact attached, its three timestamps established, and its Source identity reconciled. Nothing upstream of that commit is Document Processing's concern.

Document Processing therefore does not re-establish Document timestamps, re-reconcile Source identity, or perform deduplication against prior ingests. Those are [INGESTION_SPEC.md](./INGESTION_SPEC.md)'s concerns.

---

## Boundary Against Analytical Components

Document Processing produces Normalized text, Segments, Utterances, and within-Document Speaker attribution. Everything downstream of that output is the concern of analytical components:

* Entity Resolution reconciles the Document to a canonical Entity and reconciles within-Document Speaker names to canonical Speakers across Documents
* Heuristic Analysis produces rule-based features and candidate evidence
* Representation computes learned representations
* Learned Analysis produces learned-layer candidate evidence
* Theme assignment (ThemeInstances) is an analytical operation shared across Heuristic and Learned layers

This document is explicit about what it does *not* produce: no Entity identity, no cross-Document Speaker identity, no ThemeInstances, no Baselines, no Signals.

---

## Transformations From Raw To Normalized

The Raw → Normalized transformation is conceptually a sequence of sub-transformations. Each is versioned independently under a DerivationRun; the collection of sub-transformation versions forms the Document Processing DerivationRun for the Document.

### Text Recovery

The Raw artifact's textual content is recovered from whatever format it arrived in. This is where format-specific decoding happens — extracting text from marked-up bytes, from structured feeds, or from plain text.

Text Recovery produces a character sequence and a locus map: for each character in the recovered text, a reference back into the Raw artifact sufficient to re-resolve the character's original position. The locus map is the primitive that preserves Span precision through downstream normalization.

Specific format handling is deferred to downstream implementation.

### Canonical Text Production

The recovered text is canonicalized into a form suitable for stable downstream consumption. Canonicalization applies deterministic, reversible-in-provenance transformations — normalization of whitespace, Unicode form, character-level encoding artifacts, and similar structural conventions. Canonical Text Production does not edit content; it edits only representation.

Every canonicalization step produces an update to the locus map, so the character-level relationship between Raw and Normalized text remains resolvable.

Where a canonicalization step would be content-altering (for example, expanding contractions, correcting punctuation, or rewriting for style), it is not performed here. Those are analytical-layer concerns and are deferred.

### Segmentation

The canonical text is segmented into Segments (DATA_MODEL.md §Segment). For v1 Transcripts, the Segments are typically prepared remarks, Q&A, and any sub-segments the Source's structure exposes. Segmentation uses structural cues — headers, speaker-role markers, conventional delimiters, Source-declared section markers — not content interpretation.

Segmentation is structural, not semantic. A prepared-remarks Segment is identified by its structural position in the Document, not by deciding that its content is "preparatory."

### Utterance Identification

Within each Segment, the canonical text is segmented into Utterances (DATA_MODEL.md §Utterance). An Utterance is a single speaker turn; its boundaries are typically structural — a speaker-change marker, an interlocutor shift in Q&A, or a Source-declared turn delimiter.

Each Utterance is assigned a Document-scoped ordinal and a reference to the Segment it belongs to.

### Within-Document Speaker Attribution

Each Utterance is attributed to a within-Document Speaker handle — a label that uniquely identifies the Speaker within the scope of the Document (for example, "CEO, John Smith" or "Analyst, Acme Capital"). The handle is not yet a canonical Speaker identifier; that reconciliation is Entity Resolution's concern.

Within-Document Speaker attribution uses structural cues declared by the Source — speaker-role markers, header lines preceding turns, or Source-provided speaker tags — and, where necessary, conventional heuristics (the last-seen speaker, speaker roster declared in a header).

Where within-Document Speaker attribution is ambiguous, the Utterance is tagged as speaker-ambiguous rather than attributed by guess. Ambiguity is a recorded state, not an absence.

---

## Segment Boundaries For V1 Transcripts

For v1 Transcripts specifically, Segments are identified by the following conceptual cues, in priority order:

* Source-declared section markers (explicit metadata or section headers from the Source)
* conventional transcript headings — "Prepared Remarks", "Questions and Answers", or close variants
* structural shifts in speaker-role pattern — a sustained shift from a single-Speaker pattern (prepared remarks) to an interlocutor pattern (Q&A)
* fallback to a single-Segment Document when no structural cue supports a split

The cue set is expected to generalize across the majority of Transcripts given the Source-landscape commitments in [DATA_ACQUISITION.md](./DATA_ACQUISITION.md). Edge cases — calls with unusual formats, mid-call agenda items, or disclosed special-situation calls — may produce richer Segment structure where the Source's cues support it, or a coarser Segment structure where they do not.

Structural Anomaly Signals ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md)) depend on Segment structure being recovered consistently across Documents for the same Entity. Segmentation stability across time is therefore a quality property tracked by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md), not hidden inside Document Processing.

---

## Ambiguous Speaker Attribution

Speaker attribution ambiguity arises in several common shapes:

* a Source omits a speaker tag for an Utterance that a structural heuristic cannot unambiguously attribute
* two Speakers share a role title (for example, two Analysts without full-name disambiguation)
* a Speaker is introduced only by role in a header and later Utterances do not re-state the full handle
* a transcript convention changes mid-Document (for example, a shift from full-name tags to first-name tags)

In each case, Document Processing records the ambiguity as an explicit state on the affected Utterances. The within-Document Speaker handle is set to a placeholder that encodes the ambiguity (for example, "unknown speaker in Q&A segment 3"), and the Utterance carries a flag that makes the ambiguity queryable.

Ambiguous Utterances remain part of the Document. Downstream Entity Resolution may resolve the ambiguity using cross-Document signal (a Speaker's voice pattern, prior-Document attribution, Entity roster); if not, the Utterance remains speaker-ambiguous, and analytical components treat it accordingly (for example, Confidence Shift excludes speaker-ambiguous Utterances from Speaker-scoped Baselines).

Paraphrase reconciliation, content-level Speaker disambiguation, and cross-Document Speaker identification are explicitly deferred from Document Processing to downstream fusion and learned work — see Deferred Analytical Reconciliation below.

---

## Normalization Versioning

Normalization is versioned so that re-normalization produces a new Normalized artifact without losing history.

### DerivationRun Per Normalization

Every Normalized artifact references a Document Processing DerivationRun. The DerivationRun pins the version of every sub-transformation — Text Recovery, Canonical Text Production, Segmentation, Utterance Identification, within-Document Speaker Attribution — used to produce it.

A change to any sub-transformation produces a new DerivationRun version. Re-normalizing a Raw artifact under the new DerivationRun produces a new Normalized artifact; the prior Normalized artifact is not replaced.

### Multiple Normalized Artifacts Per Raw

A single Raw artifact may therefore have several Normalized artifacts associated with it over time, each under its own DerivationRun. Consumers — heuristic features, learned features, Baselines, Signals — reference a specific Normalized artifact by identifier, so the choice of which Normalized artifact they depend on is explicit and recorded.

### Default Normalized Artifact

At any time, a single Normalized artifact per Document is designated the current default. The default is the one downstream components use by convention unless they explicitly request an older version. Promotion of a new default is a deliberate operation coordinated with [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)'s re-derivation semantics.

The default is a pointer, not a mutation. The prior default remains queryable by identifier; the default pointer moves.

### Re-Normalization Does Not Invalidate Downstream

Downstream artifacts that referenced a prior Normalized version are not invalidated when a new Normalized version is produced. They continue to reference the prior version. Re-derivation of downstream artifacts against the new Normalized version is a separate, scheduled operation (owned by [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)); Document Processing does not cascade changes downstream.

---

## Span Precision Through Normalization

Spans (DATA_MODEL.md §Span) must remain resolvable as the text passes through normalization. The mechanism is the locus map produced at Text Recovery and extended at each canonicalization step.

### Bidirectional Locus Resolution

For any Span in a Normalized artifact, the locus map supports:

* resolving backward to the corresponding locus in the Raw artifact
* resolving forward to the corresponding locus in any subsequent Normalized version derived from the same Raw, where the subsequent normalization's locus map preserves a correspondence

The second direction is best-effort: if a subsequent normalization meaningfully changes canonical-text structure, some Spans may not resolve forward. Spans that cannot resolve forward are recorded as such, and downstream analysis treats them as stale against the new Normalized version.

### Utterance-Bounded Default

Per DATA_MODEL.md §Span, Span precision for Transcripts is at least Utterance-bounded. Document Processing ensures every Utterance is itself a valid Span with a stable locus. Finer-grained Spans (character offsets within an Utterance) are supported and their locus maps preserved; the coarser guarantee is what the model relies on.

### Evidence Integrity

Every Evidence record that cites a Span in a Transcript cites at least an Utterance boundary (DATA_MODEL.md §Span). Document Processing's role is to make Utterance boundaries reproducible across re-normalizations under the same DerivationRun, so a Signal's Evidence does not become ambiguous over time.

---

## Deferred Analytical Reconciliation

Several kinds of reconciliation are explicitly *not* performed here and are deferred to analytical or fusion-layer work:

* **paraphrase reconciliation** — noticing that two Utterances say substantively the same thing in different words is a learned-layer concern, not a normalization concern
* **content-level Speaker disambiguation** — deciding that an ambiguous Utterance belongs to Speaker A rather than Speaker B based on content is fusion-layer work
* **cross-Document Speaker identity** — reconciling a within-Document Speaker handle to the canonical Speaker across Documents is Entity Resolution's concern
* **semantic Segmentation** — identifying conceptual segments beyond structural ones (for example, grouping Q&A exchanges by topic) is a learned-layer concern
* **Theme assignment** — identifying the Themes a Document instantiates (ThemeInstances) is an analytical operation, jointly heuristic and learned
* **contradiction, omission, drift detection** — Signal detection generally

Document Processing is intentionally shallow. Depth is earned in the Enriched and Analytical layers, under separate versioned DerivationRuns, and is expected to remain compatible with the Normalized contract this document defines.

---

## Output Of Document Processing

At the boundary with analytical components, Document Processing has produced, for each Document:

* a Normalized artifact with a canonical text, a reference to its Raw, and a reference to the Document Processing DerivationRun that produced it
* a sequence of Segments associated with the Normalized artifact, each with a type label, an ordinal, and a locus within the Normalized text
* a sequence of Utterances, each associated with a Segment, each with a within-Document Speaker handle (possibly ambiguous), and each itself a valid Span
* a locus map preserving Span resolution between Raw and Normalized
* provenance (the DerivationRun and its sub-transformation versions) written to the Evidence & Provenance Store

Entity identity is still not attached; that is Entity Resolution's output. Cross-Document Speaker reconciliation has not happened; that is Entity Resolution's output. No Themes, no features, no Baselines, no Signals.

---

## What This Document Is Not

* not an ingestion document (owned by [INGESTION_SPEC.md](./INGESTION_SPEC.md))
* not an analytical component specification (heuristic, learned, fusion work lives elsewhere)
* not a tokenizer or preprocessor selection
* not a storage or indexing specification
* not a retention or deletion specification (owned by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md))

---

## Deferred Decisions

* specific tokenizer, segmenter, or locus-mapping libraries — downstream implementation work
* specific rules for Canonical Text Production (which Unicode forms, which whitespace conventions) — downstream implementation work
* specific heuristics for Segment detection beyond the priority cues above — downstream implementation work
* specific fallback strategies when Source-declared speaker tags are absent — downstream implementation work, coordinated with [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)'s Source-quality tracking
* cross-Document Speaker reconciliation — Entity Resolution, upstream of analytical components
* Theme detection and ThemeInstance production — NARRATIVE_ANALYSIS.md and MODEL_STRATEGY.md
* re-normalization scheduling and throttling — [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)

---

## Open Questions

* How is the default Normalized artifact for a Document chosen when multiple exist? The mechanism is deferred but coordinated with [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)'s Pipeline Version concept.
* How are structural cues treated when a Source's conventions drift mid-history? A Document whose Segmentation differs from prior Documents' under the same Source raises a quality concern; tracking lives in [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md).
* How is intra-Document partial supersession ([INGESTION_SPEC.md](./INGESTION_SPEC.md) Open Questions) expressed in the Normalized layer? Flagged: likely as a per-Segment or per-Utterance update relationship under the update-Document relationship model, but not committed here.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [DATA_MODEL.md](./DATA_MODEL.md) defines Document, Segment, Utterance, Span, and the immutability/re-derivability posture; this document specifies how Document Processing produces instances of those structures under versioned DerivationRuns.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the Document Processing component; this document specifies the rules that component's outputs must satisfy.
* [INGESTION_SPEC.md](./INGESTION_SPEC.md) is the immediate upstream document.
* [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) owns how Document Processing is triggered, how re-normalization is scheduled, and how downstream components observe newly produced Normalized artifacts.
* [SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md) owns how consumers query specific Normalized artifacts, including by DerivationRun version.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) owns retention and quality monitoring of Normalized artifacts, including Segmentation-stability tracking.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) consumes Segments, Utterances, and Spans as the locus of Evidence; this document ensures those loci are stable.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms introduced here (Locus Map, Default Normalized Artifact, Within-Document Speaker Handle, Normalization DerivationRun) are flagged for extension in the cluster's closing summary.
