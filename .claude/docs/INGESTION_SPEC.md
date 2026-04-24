# INGESTION_SPEC.md

## Purpose Of This Document

INGESTION_SPEC.md specifies how an acquired artifact, once it has crossed the boundary into the system, is landed as a Raw artifact and attributed well enough to feed [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md). It defines Document-identity establishment, the three mandatory Document timestamps, deduplication and update semantics, Source identity reconciliation, failure handling under immutability, and the provenance emitted along the way.

This document is conceptual. It does not select parsers, file formats, libraries, or storage layouts. It defines the rules ingestion must satisfy so that Raw artifacts enter the data model cleanly and derived artifacts downstream can depend on them.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). The data model ingestion produces is defined in [DATA_MODEL.md](./DATA_MODEL.md). The Ingestion component's responsibilities are defined in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## How To Read This Document

* ingestion is described as a set of invariants and stages, not as a pipeline diagram
* every rule below is a constraint on what Ingestion produces, not on how it does so
* the boundary with [DATA_ACQUISITION.md](./DATA_ACQUISITION.md) is stated identically here and there
* the boundary with [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md) is stated explicitly at the end

---

## Guiding Invariants

Held for every ingested artifact:

* Raw is immutable (DATA_MODEL.md §Immutability And History)
* every Raw artifact carries its Source, its Source-native identifier (when one exists), its Observation Time, and its acquisition DerivationRun reference
* every Raw artifact's provenance is resolvable from the Evidence & Provenance Store without reading the artifact itself
* no derived artifact downstream of ingestion references Raw content whose existence and provenance cannot be reconstructed from the Evidence & Provenance Store alone
* ingestion never silently drops an arrival; every arrival is represented somewhere in the system, even if it is a duplicate or a failure

---

## Boundary Against DATA_ACQUISITION.md

The boundary between acquisition and ingestion is the moment an acquired artifact first exists as a Raw artifact within the system, attributed to its Source and assigned an Observation Time.

Anything upstream of that moment — where the artifact came from, through what channel, under what licensing terms, and with what quality properties — is [DATA_ACQUISITION.md](./DATA_ACQUISITION.md)'s concern.

Anything downstream of it — how the artifact is parsed, how its Document identity is established, how it is normalized into canonical text and structure, and how it is landed into the Raw and Normalized layers — is INGESTION_SPEC.md's concern.

This boundary statement is held identically in [DATA_ACQUISITION.md](./DATA_ACQUISITION.md).

---

## What Ingestion Consumes

At the boundary, ingestion receives:

* the artifact as a byte sequence or equivalent
* the Source's canonical identifier
* the Source-native identifier for the artifact (if the Source provides one)
* the retrieval channel and the acquisition timestamp
* the acquisition DerivationRun reference
* the Source's licensing posture

Nothing else is assumed. In particular, Entity identity is not yet attached; Speaker identity is not yet reconciled; the three Document timestamps are not yet definitively established.

---

## Stages

Ingestion is described as an ordered set of stages. Each stage has a clear output. The stage names are conceptual; implementation may combine or split them.

### 1. Raw Landing

The received byte sequence is landed as an immutable Raw artifact in the data model's Raw layer. The Raw artifact is identified by a project-owned canonical Document identifier and carries a reference to its Source, its Source-native identifier, and its Observation Time.

Raw Landing commits the artifact to the system. Subsequent stages never mutate it.

### 2. Minimal Structural Extraction

Enough structure is extracted to support Document-identity establishment, the three Document timestamps, and deduplication. This is strictly the minimum — typically Source-declared metadata and header-level features — not full parsing. Full parsing is [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md)'s concern.

Minimal Structural Extraction produces a lightweight descriptor associated with the Raw artifact. It does not rewrite the Raw artifact and does not land in the Normalized layer.

### 3. Three-Time Establishment

The three mandatory Document timestamps (Event Time, Document Time, Observation Time; DATA_MODEL.md §Document) are established for the Raw artifact. Observation Time was recorded at Raw Landing. Document Time is established from Source-declared metadata. Event Time is established from Source-declared metadata and, where the Source permits, from structural cues within the artifact.

If any of the three cannot be established with acceptable confidence, the Document is quarantined (see Failure Handling).

### 4. Source Identity Reconciliation

The Source is resolved to its canonical identifier (DATA_MODEL.md §Source). Source reconciliation is typically a fast lookup because the Source was identified at acquisition; this stage exists to close the loop in case the acquirer passed a native Source alias rather than the canonical identifier.

### 5. Deduplication And Update Reconciliation

The arrival is reconciled against prior ingests from the same Source (see Deduplication, below). The outcome of this stage is one of: a new Document (the arrival is novel), an update to a prior Document (the arrival is a revision), or a duplicate of a prior ingest (the arrival repeats an earlier one).

In all cases, a new record is created. No prior Raw artifact is mutated.

### 6. Document Commit

A Document record (DATA_MODEL.md §Document) is committed. The Document references the Raw artifact, the Source, the three timestamps, the Source-native identifier, the ingestion DerivationRun, and — where applicable — a relationship to a prior Document (for updates and duplicates).

Document Commit is the stage whose completion signals Document Processing that the Document is ready for Raw → Normalized transformation.

### 7. Provenance Emission

The ingestion DerivationRun, its outputs, and their relationships are written to the Evidence & Provenance Store (ARCHITECTURE §Evidence & Provenance Store). Every artifact ingestion produces — the Raw record, the Document record, the quarantine or duplicate relationships — is recorded there rather than passed forward as pipeline payload.

---

## Document Identity Establishment

A Document is identified by a project-owned canonical identifier. The identifier is assigned at Raw Landing and is stable for the lifetime of the Document.

The canonical Document identifier is not derived from any Source-native identifier. A Source-native identifier is preserved alongside the canonical identifier on the Document record, for reconciliation and human traceability.

A Raw artifact is always associated with exactly one Document at Document Commit. Multiple Raw artifacts may be associated with a single Document over time — for example, when an update of the same transcript arrives from the same Source; each update produces a new Raw with a new canonical Document identifier and an explicit relationship to the prior Document.

This is a deliberate choice: "same artifact, newer version" is represented as two Documents with an update relationship, not as one Document with two Raws. This preserves the Raw immutability invariant and keeps the Document record a stable anchor for derived artifacts.

---

## Three Mandatory Document Timestamps

Every Document carries three timestamps (DATA_MODEL.md §Document):

### Event Time

When the phenomenon being described occurred. For a Transcript, the call time. Event Time is established from Source-declared metadata preferentially; where the Source declares only a date, the time component may be left coarse and that coarseness is recorded.

### Document Time

When the Document was published or finalized by the Source. Typically close to but distinct from Event Time. Established from Source-declared metadata.

### Observation Time

When the system ingested the Document — specifically, when the Raw artifact was committed at Raw Landing. This is a system-owned timestamp that Ingestion is the sole writer of.

Each timestamp carries a precision indicator. A coarse Event Time (only a date) is a different state from an absent Event Time. Coarseness is not treated as failure; absence is.

---

## Deduplication And Update Reconciliation

Deduplication is non-silent. The system never drops an arrival as a duplicate without creating a record of the arrival.

### Matching

An arrival is reconciled against prior ingests by:

* Source identifier plus Source-native identifier, when the Source provides a native identifier that it commits to reusing for updates
* content fingerprint, as a secondary match signal — a Content Fingerprint is a conceptual summary of the artifact's content sufficient to recognize byte-level identity without reading the artifact itself
* temporal proximity in Event Time and Document Time, as a context signal when Source-native identifiers or fingerprints are unavailable or unstable

Specific fingerprint scheme, tolerance for fuzzy matches, and priority ordering are deferred to downstream implementation.

### Outcomes

Matching produces exactly one of the following outcomes, each of which is recorded:

* **novel** — no match; a new Document is committed
* **identical duplicate** — content fingerprint matches a prior Raw from the same Source; no new Document record is necessary, but a duplicate-arrival record is written to the Evidence & Provenance Store so the arrival is not silently lost
* **update** — Source-native identifier or close-match fingerprint with newer Document Time; a new Document is committed, with an update relationship to the prior Document; the prior Document is marked as superseded but not deleted or mutated
* **ambiguous** — match signals conflict; the arrival is quarantined (see Failure Handling) rather than assumed to belong to any of the above outcomes

Update relationships are first-class references on the Document, not annotations. Every Document knows whether it supersedes a prior one and whether it has itself been superseded.

### Legitimate Updates Never Silently Lost

A legitimate update — a corrected transcript, a retracted-and-reissued filing, a provider republication — must produce a new Document, not a drop. Downstream components subscribe to Document arrivals, not to Source-native identifiers; the update is a new Document they will observe, with a lineage reference to the prior one.

---

## Source Identity Reconciliation

Source reconciliation runs during ingestion even though acquisition already identified the Source, because:

* the acquirer may pass a native Source alias, not a canonical identifier
* an acquirer may itself aggregate multiple sub-Sources; the true Source for an artifact may differ from the acquirer
* Source identity is relied on by cross-source analysis (CONTEXT §11); reconciliation at ingestion is the last opportunity to catch an incorrect attribution

Reconciliation produces either a canonical Source reference or, if no Source can be canonically reconciled, a quarantined Document.

Reconciliation confidence is recorded on the Document, as the data model requires (DATA_MODEL.md §Identity Model — reconciliation confidence is recorded where imperfect). A low-confidence Source reconciliation is surfaced, not hidden.

---

## Ingestion Failure Handling

Ingestion failures must not violate the Raw immutability invariant. The system handles failures by creating new records, not by deleting or mutating prior ones.

### Quarantine

A quarantined Document is one for which ingestion could not complete one of the required stages — typically a missing timestamp, a missing or ambiguous Source, or an ambiguous deduplication outcome.

A quarantined Document is still committed to the data model, with an explicit quarantined state, a reason code, and a reference to the problematic condition. Its Raw artifact is preserved. Downstream components (Document Processing and beyond) do not act on quarantined Documents.

Quarantine is a Document-level state, not an artifact-level one. The Raw artifact is always landed; the Document that references it may be quarantined.

### Re-Attempts

Re-attempts at ingestion — after a Source publishes missing metadata, after a Source classification is updated, after ambiguous matching is resolved — are new ingestion operations that produce new Document records, linked to the prior quarantined Document by a succeeds relationship.

A quarantined Document is never "unquarantined" in place. Its record remains; a successor Document is committed. This preserves the re-derivability invariant (DATA_MODEL.md §Derivation Layers): historical Signals that were not produced because of quarantine remain explicable from the preserved record, even after the quarantine is resolved.

### Partial Failures

A partial failure — for example, Raw Landing succeeds but Minimal Structural Extraction fails — is represented as a Raw artifact plus a failed ingestion DerivationRun and no Document record. Downstream components see no Document, which is the intended behavior. The Evidence & Provenance Store records the failed DerivationRun so operators can investigate.

### Licensing-Posture Blocks

A Document whose Source is in an Incompatible Or Ambiguous licensing posture at ingestion time is quarantined and not committed as an active Document. This is not a rejection; the Raw artifact is preserved. If the Source's posture is later reclassified to Training-Compatible or Analytical-Only, a new ingestion operation may commit a successor Document under the updated posture.

Licensing enforcement mechanics are owned by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md); this document only commits the ingestion-time check.

---

## Provenance Emitted By Ingestion

Every ingestion operation emits the following provenance to the Evidence & Provenance Store:

* the ingestion DerivationRun (its identifier, its logical name, its version)
* the acquisition DerivationRun it descended from
* the Raw artifact it landed
* the Document record (if one was committed) and its three timestamps with their precisions
* the deduplication outcome and the prior-Document reference if the outcome was update or identical duplicate
* the Source canonical identifier and the Source reconciliation confidence
* the licensing posture carried in from acquisition

Downstream components read provenance from the Evidence & Provenance Store; ingestion does not embed it in the Document payload beyond the references the Document itself requires.

---

## What Ingestion Produces For Downstream

At the boundary with [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md), ingestion has produced:

* a committed Document record with the three timestamps established
* a committed Raw artifact associated with that Document, immutable
* canonical Source identity attached to the Document
* a deduplication outcome and, where relevant, prior-Document lineage
* the ingestion DerivationRun recorded in the Evidence & Provenance Store
* the Source's licensing posture carried on the Document for downstream enforcement

Entity identity is not yet attached (that is Entity Resolution's concern; [ARCHITECTURE.md](./ARCHITECTURE.md) §Entity Resolution). Speaker identity is not yet reconciled. The text is not yet normalized. No Segments or Utterances exist yet.

---

## Boundary Against DOCUMENT_PROCESSING.md

Ingestion stops at the point where the Document record has been committed and its provenance has been emitted. Raw → Normalized transformation, Segment and Utterance tagging, and within-Document Speaker attribution are [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md)'s concern.

Ingestion is explicitly not responsible for:

* producing Normalized text
* identifying Segments (prepared remarks, Q&A)
* tagging Utterances
* attributing Speakers within the Document
* reconciling the Document to its Entity
* any semantic interpretation of the artifact

Those are downstream of ingestion, not part of it.

---

## What This Document Is Not

* not an acquisition specification (owned by [DATA_ACQUISITION.md](./DATA_ACQUISITION.md))
* not a normalization specification (owned by [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md))
* not a parser-library selection
* not a file-format specification
* not a storage specification
* not a governance specification (owned by [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md))

---

## Deferred Decisions

* specific parser libraries and tooling — downstream implementation work
* file-format handling (HTML, PDF, plain text, structured feeds) — downstream implementation work
* Content Fingerprint scheme and match-confidence thresholds — downstream implementation work
* physical storage layout of Raw artifacts — downstream infrastructure work
* retry policy and backoff for transient ingestion failures — downstream infrastructure work
* Source-reconciliation confidence thresholds — downstream implementation work, coordinated with [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md)'s quality monitoring
* detailed quarantine triage workflow — [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) and downstream operational work

---

## Open Questions

* How is Observation Time preserved when ingestion replays historical artifacts that were captured before the system existed? Flagged: the Observation Time in that case is the system's ingestion time, not the original acquisition time, and both are recorded.
* How is partial supersession handled — when an update revises only part of a prior Document? The update relationship committed here is Document-level; intra-Document partial supersession is deferred and likely belongs in [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md)'s normalization versioning.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the Raw layer, the Document record, and the three-timestamp model; this document specifies how ingestion produces instances of those structures.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the Ingestion component; this document specifies the rules that component's outputs must satisfy.
* [DATA_ACQUISITION.md](./DATA_ACQUISITION.md) is the immediate upstream document; the boundary is held identically in both.
* [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md) is the immediate downstream document; the boundary is stated above.
* [DATA_GOVERNANCE.md](./DATA_GOVERNANCE.md) owns retention, deletion, and licensing enforcement for the artifacts this document commits.
* [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) owns how Document Commit is observed by downstream components.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms introduced here (Content Fingerprint, Quarantine, Ingestion DerivationRun) are flagged for extension in the cluster's closing summary.
