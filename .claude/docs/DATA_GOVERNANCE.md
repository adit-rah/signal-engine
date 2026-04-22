# DATA_GOVERNANCE.md

## Purpose Of This Document

DATA_GOVERNANCE.md defines the stewardship of data the system holds: what provenance is recorded per artifact and per derivation layer, how retention policy is shaped per layer, how deletion is handled under the immutability and re-derivability invariants, how data quality is monitored at the source level, how source licensing terms are enforced technically, and how the seven temporal-model times are carried through the system for audit.

This document is conceptual. It does not select retention periods, deletion implementations, quality dashboards, or compliance systems. It defines the policies any realization must honor so that governance is coherent with the data model and the rest of the cluster.

This document is explicitly not a legal or compliance document. It does not authorize, interpret, or substitute for legal review. It defines the system-level posture from which compliance-conscious decisions are made.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary is drawn from [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md). Security-threat handling is owned by SECURITY_AND_PRIVACY.md; this document covers stewardship, not threat response.

---

## How To Read This Document

* governance is described as policy shapes, not as numeric thresholds
* every policy here honors the immutability and re-derivability invariants of [DATA_MODEL.md](./DATA_MODEL.md)
* the boundary with SECURITY_AND_PRIVACY.md is explicit and held
* retention numbers, deletion implementations, and compliance-specific detail are deferred

---

## Guiding Commitments

Inherited and held as invariants:

* Raw is immutable (DATA_MODEL.md §Immutability And History)
* derived artifacts are re-derivable from Raw plus their DerivationRun (DATA_MODEL.md §Derivation Layers)
* every derived artifact carries provenance to the source Spans that support it (CONTEXT §3.3; DATA_MODEL.md §Evidence Provenance And Traceability)
* temporal reasoning is first-class (CONTEXT §11, §3; DATA_MODEL.md §Temporal Model)
* the in-house model ownership posture (CONTEXT §6) constrains what may be used for training, which depends on Source licensing posture ([DATA_ACQUISITION.md](./DATA_ACQUISITION.md))
* low-capital posture ([ASSUMPTIONS.md](./ASSUMPTIONS.md) T3, H5) bounds the governance surface; governance mechanisms must not demand disproportionate continuously-running infrastructure

---

## Boundary Against SECURITY_AND_PRIVACY.md

DATA_GOVERNANCE.md owns stewardship — provenance, retention, deletion, quality tracking, licensing enforcement, and temporal carrying. It assumes a non-adversarial operating environment for the purposes of policy design.

SECURITY_AND_PRIVACY.md (deferred) owns the threat model, adversarial risk, access control, authentication, authorization, data-in-transit and at-rest protection, and incident response. Where governance and security overlap — for example, a deletion request that originates in a compliance obligation and must be verified before execution — this document commits the stewardship-side rule, and SECURITY_AND_PRIVACY.md commits the verification discipline around it.

Practically, overlaps include:

* deletion mechanics (this document's conceptual posture; SECURITY_AND_PRIVACY.md's enforcement against unauthorized deletion)
* access to Raw artifacts (this document's retention rules; SECURITY_AND_PRIVACY.md's access control)
* licensing posture enforcement (this document's technical enforcement; SECURITY_AND_PRIVACY.md's audit discipline)

This boundary is held identically with SECURITY_AND_PRIVACY.md as a cross-document invariant.

---

## Provenance Per Artifact And Per Layer

Every artifact the system holds carries provenance. The provenance is layered: an artifact inherits the provenance of the artifacts it was derived from.

### Raw

Raw artifact provenance records:

* the Source canonical identifier
* the Source-native identifier (if provided)
* the retrieval channel
* the acquisition DerivationRun
* the ingestion DerivationRun that landed the artifact
* the Observation Time with its precision
* the Source's licensing posture at ingestion time
* the Content Fingerprint (if computed)

Raw provenance is the ground floor of traceability; every downstream artifact's trace terminates here.

### Normalized

Normalized artifact provenance inherits Raw provenance and adds:

* the Raw artifact identifier it was derived from
* the Document Processing DerivationRun (with its sub-transformation versions)
* the Pipeline Version under which it was produced
* the Segmentation and Utterance-identification outcomes (Segment and Utterance records, with their ordinals and loci)
* the locus map between Raw and Normalized

### Enriched

Enriched artifact provenance inherits Normalized provenance and adds:

* the Entity Resolution DerivationRun and its reconciliation confidence
* the canonical Speaker reconciliation DerivationRun and its confidence per Speaker
* the ThemeInstance DerivationRuns (heuristic and learned contributions)

### Analytical

Analytical artifact provenance inherits Enriched provenance and adds:

* the Heuristic Analysis DerivationRun (for heuristic features)
* the Representation DerivationRun (for embeddings)
* the Learned Analysis DerivationRun (for learned features and candidate evidence)
* the Baseline DerivationRun (for Baselines)
* any dependency references to prior analytical artifacts used as inputs (for example, prior Baselines against which a new Baseline was derived)

### Signal

Signal provenance inherits Analytical provenance and adds:

* the Fusion Engine DerivationRun
* the Basis chain ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) §Basis) — which heuristic rules contributed, which learned outputs contributed
* the Evidence chain — references to Evidence records and through them to Spans
* the Signal lifecycle state and any lineage references
* the Pipeline Version under which the Signal was emitted

Signal provenance is the complete chain from Signal down to the Raw Spans that support it. A Signal whose provenance chain cannot be resolved is not a valid Signal and is not retained as an active artifact.

### Provenance Locality

All provenance is stored in the Evidence & Provenance Store ([ARCHITECTURE.md](./ARCHITECTURE.md) §11), not embedded in artifact payloads. This keeps artifacts small and keeps provenance queryable independently. Retrieval of provenance is handled through the Query & Retrieval Surface ([SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md)).

---

## Retention Policy Per Layer

Retention policy applies per derivation layer. Specific numeric retention periods are deferred. The policy shape for each layer is committed here.

### Raw

Raw artifacts are retained indefinitely by default, subject to licensing-posture constraints. Raw is the ground truth from which derived artifacts are re-derivable; retiring Raw forecloses re-derivation for the artifacts Raw supports.

Exceptions to indefinite retention:

* a licensing-posture constraint requires retirement or deletion after a defined period (for example, a Source's terms limit retention duration)
* a deletion request (see Deletion, below) removes or tombstones a specific Raw

Specific retention period numbers are a function of licensing posture and operational cost and are deferred to downstream decisions.

### Normalized

Normalized artifacts are retained while their Raw is retained and while their DerivationRun remains relevant — either as a current default or as a historically-referenced artifact. Retirement of an old Normalized artifact whose Raw and DerivationRun are retained is permissible but not required; the Normalized layer is re-derivable by definition.

In practice, multiple Normalized artifacts per Raw are likely to accumulate under re-normalization ([DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md)). Governance supports retaining all of them or retiring older ones according to a policy whose shape is committed here:

* Normalized artifacts currently referenced by Analytical or Signal artifacts are retained
* Normalized artifacts no longer referenced and whose DerivationRun is superseded may be retired, with retirement recorded as a governance operation (not a silent deletion)

### Enriched

Enriched artifacts follow the same policy shape as Normalized: retained while referenced; retireable when superseded by a newer Enrichment DerivationRun and no downstream artifact depends on them. Retirement is explicit.

### Analytical

Analytical artifacts — heuristic features, learned features, Baselines, comparisons — are re-derivable from Enriched plus their DerivationRuns. Retention follows the same shape:

* Analytical artifacts referenced by Signals are retained
* Analytical artifacts superseded by a newer DerivationRun version and no longer referenced may be retired
* Baselines are a special case: Baselines are versioned by valid-time (DATA_MODEL.md §Baseline), and historical Baselines support as-of queries; retirement of Baselines is therefore more conservative than retirement of other Analytical artifacts

### Signal

Signals are retained indefinitely by default. Signal retention is load-bearing for the system's temporal claim (CONTEXT §2): meaning emerges through change over time, and historical Signals are part of the system's memory.

Exceptions:

* a licensing-posture change that renders a Signal's Evidence unretainable may force the Signal to be retired and its Evidence access tombstoned; the Signal record itself remains
* a deletion request may tombstone a specific Signal's access without removing its record

### Pipeline Versions And DerivationRuns

Pipeline Version records and DerivationRun records are retained indefinitely. They are the substrate for historical replay and for understanding the history of the system's decisions; retiring them forecloses replay.

---

## Deletion Under Immutability

A deletion request — originating in licensing-posture changes, compliance obligations, or operator intent — must be handled without violating immutability or re-derivability.

### Tombstoning

The mechanism is a tombstone, not an in-place erase. A Tombstone is a governance record attached to an artifact; it marks the artifact's content as no longer accessible to the system's readers, while the artifact's existence and provenance remain queryable.

A Tombstone is itself an immutable record: it names the artifact, the governance reason for the action, the DerivationRun that produced the tombstone, and the time of its issuance. A tombstone is not reversed by mutation; a re-availability decision produces a new governance record superseding the tombstone.

### Redaction Records

For cases where partial content must be made inaccessible — for example, a specific Span's text is unretainable but the surrounding Document is — a Redaction Record marks the specific locus as redacted. Evidence that cites a redacted Span resolves to the record of the redaction rather than to the original text.

Redaction Records and Tombstones are distinct in scope but share the shape: governance operations expressed as new immutable records, not as mutations of prior records.

### Propagation

Deletion propagates as queryable state, not as cascading mutation.

* Raw tombstone: the Raw artifact's content becomes inaccessible; Normalized, Enriched, Analytical, and Signal artifacts that depended on it remain as records but become non-re-derivable. Their as-of queryability is unaffected for historical Effective Times; their re-derivation against a newer Pipeline Version fails explicitly and the failure is recorded.
* Normalized tombstone: the specific Normalized artifact's content becomes inaccessible. The Raw remains; re-normalization can produce a new Normalized artifact if permitted by the reason for the tombstone.
* Analytical tombstone: the specific Analytical artifact's content becomes inaccessible; consumers see the tombstone rather than the artifact.
* Signal tombstone: the specific Signal's Evidence access is blocked. The Signal record remains in the Signal Store; its lifecycle is unaffected by the tombstone as a lifecycle transition, but any access to its content yields the tombstone.

### Re-Derivation Against Tombstoned Sources

Re-derivation scheduling ([EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)) observes tombstones. An attempt to re-derive a downstream artifact from a tombstoned upstream artifact produces an explicit failure — not a silent skip — and the failure is recorded in the Evidence & Provenance Store as a failed DerivationRun referencing the tombstone.

### Hard Deletion

Hard deletion — the actual destruction of bytes, irrecoverable — is a compliance-driven capability, not a default. It is outside the scope of normal governance and requires explicit invocation under a policy that is not defined here. The conceptual commitment is that hard deletion is supported and, when it occurs, is recorded as an immutable governance record even though the underlying content is gone.

Specific hard-deletion mechanics, authorization, and verification discipline are deferred to SECURITY_AND_PRIVACY.md.

---

## Data Quality Monitoring

This document governs the monitoring of upstream data quality — Source quality and ingestion quality — not Signal quality. Signal quality is owned by EVALUATION.md.

### Source Quality

Source Quality is the aggregate of the criteria defined in [DATA_ACQUISITION.md](./DATA_ACQUISITION.md):

* Speaker attribution coverage
* punctuation fidelity
* completeness
* structural regularity
* normalization stability
* provenance transparency

Source Quality is tracked per Source over time. The tracking is periodic, not continuous, reflecting the low-capital posture. Each Source has a Source Quality history — a sequence of samples, each an assessment of the criteria above against a representative set of artifacts from that Source in a window.

Source Quality drift — a degradation in one or more criteria — is a governance observation, not a Signal. Its consequences may be:

* a decision to downgrade the Source's acceptance for new coverage
* a decision to re-normalize prior artifacts from the Source under a revised DerivationRun that accounts for the drift
* a decision to tombstone an unusable subset of prior artifacts
* a decision to deprecate the Source

Specific criteria measurement, sample sizes, and thresholds are deferred to downstream implementation.

### Ingestion Quality

Ingestion Quality is tracked at the ingestion layer:

* quarantine rates per Source
* deduplication ambiguity rates per Source
* Source reconciliation confidence distribution
* failed DerivationRun rates

These metrics feed the same governance consequences as Source Quality: Source deprecation, re-normalization, tombstoning.

### Cross-Layer Quality

Some quality concerns span derivation layers. For example, a Source whose Source Quality is acceptable may produce artifacts whose normalization is unstable under a specific DerivationRun — a Segmentation-stability regression noted in [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md).

Cross-layer quality is tracked as a joint property; the governance response is typically a re-normalization under a revised DerivationRun or, if the cause is upstream, a Source Quality action.

### Distinction From Signal Quality

Source Quality and Ingestion Quality are about the data entering the system. Signal Quality is about the outputs of the system's analysis, owned by EVALUATION.md. Governance observes the upstream conditions; evaluation observes the downstream outputs. The two are expected to interact — degraded Source Quality typically reduces Signal Quality — but the accountability is separated.

---

## Licensing Posture Enforcement

Licensing posture, established at acquisition ([DATA_ACQUISITION.md](./DATA_ACQUISITION.md)), must be enforced technically. The enforcement is a system property, not a legal process.

### Posture Carrying

Every Raw artifact carries its Source's licensing posture at ingestion time. The posture travels with the artifact through the derivation layers; every derived artifact inherits the posture of the most restrictive artifact it depends on.

For example: a Signal whose Evidence cites Spans from a Training-Compatible Source and from an Analytical-Only Source inherits the Analytical-Only posture — the more restrictive of the two.

### Enforcement Points

Enforcement happens at the points where posture matters:

* **training** — training datasets are constructed by querying for artifacts whose inherited licensing posture is Training-Compatible. Artifacts whose posture is Analytical-Only are excluded from training sets; artifacts whose posture is Incompatible Or Ambiguous are excluded by construction (they are never committed as active artifacts; [INGESTION_SPEC.md](./INGESTION_SPEC.md) quarantines them)
* **Signal emission** — a Signal whose Evidence would depend on Incompatible Or Ambiguous material is not emitted; this case should not arise because such material does not exist as an active artifact, but the check is performed as a defense against ingestion-layer misclassification
* **artifact retrieval** — the Query & Retrieval Surface honors posture when returning artifacts to callers whose authorization does not cover the posture; posture is one dimension the surface may filter on, alongside access control (owned by SECURITY_AND_PRIVACY.md)

### Posture Reclassification

A Source's licensing posture may change over time — a provider's terms update, a reclassification after legal review, a reclassification after a quality determination. Reclassification is a governance operation that:

* produces a new Source-posture record with valid-time
* propagates to artifacts at re-derivation time (re-derivation under the new posture may require re-tagging downstream artifacts)
* may trigger tombstoning of artifacts that can no longer be retained under the new posture

Reclassification does not retroactively alter prior artifacts' recorded posture. The historical record shows the posture that applied at each time.

### Enforcement Limitations

Technical enforcement prevents accidental misuse under a correctly classified posture. It does not substitute for legal review of terms, and it does not guarantee compliance with all obligations a Source's terms impose. Substantive compliance is outside this document's scope.

---

## Carrying The Seven Temporal-Model Times For Audit

The Temporal Model (DATA_MODEL.md §Temporal Model) names seven kinds of time. Governance's job is to ensure every one relevant to an artifact is recorded and queryable for audit. The table below states which times each artifact class carries.

### Raw

* Observation Time — recorded at Raw Landing
* Acquisition timestamp (upstream of Observation Time) — recorded in acquisition provenance

### Document

* Event Time — established at ingestion, with precision indicator
* Document Time — established at ingestion, with precision indicator
* Observation Time — inherited from Raw

### Normalized, Enriched, Analytical

* Processing Time — when the artifact was produced under its DerivationRun
* inherit Event Time, Document Time, Observation Time from the Document(s) they depend on
* Valid Time — for Baselines specifically, the interval over which the Baseline applies

### Signal

* Emission Time — when the Signal was produced
* Subject Time — the time or interval the Signal describes (distinct from Emission Time)
* Processing Time — when the Fusion Engine's DerivationRun produced the Signal
* inherit temporal information from upstream artifacts via Basis and Evidence

### Queries

* Effective Time — the caller-specified time for as-of queries; recorded on the query but not an artifact property

All seven times are carried through either directly on the artifact or by reference to upstream artifacts via provenance. Audit queries reconstruct the complete temporal context of any artifact by following those references.

---

## Governance Records

Governance produces immutable records:

* Source Quality samples
* Ingestion Quality samples
* Source-posture reclassifications with valid-time
* Tombstones (Raw, Normalized, Enriched, Analytical, Signal)
* Redaction Records at Span scope
* Deletion records for hard deletion events
* Pipeline Version promotions ([EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md))

Each governance record is itself a derivation of the governance process, recorded in the Evidence & Provenance Store and queryable through the Query & Retrieval Surface.

Governance records are retained indefinitely by default. They are the substrate for auditing the system's governance history.

---

## What This Document Is Not

* not a legal or compliance document
* not a security-threat specification (owned by SECURITY_AND_PRIVACY.md)
* not a storage specification
* not a retention-period specification (specific periods deferred)
* not a deletion-implementation specification
* not a Signal-quality specification (owned by EVALUATION.md)
* not an access-control specification (owned by SECURITY_AND_PRIVACY.md)

---

## Deferred Decisions

* specific retention periods per layer — downstream decisions, constrained by licensing posture and operational cost
* hard-deletion mechanics and authorization discipline — SECURITY_AND_PRIVACY.md
* access-control and authorization over governance operations — SECURITY_AND_PRIVACY.md
* Source Quality sample-size and measurement specifics — downstream implementation work
* Ingestion Quality thresholds for Source deprecation — downstream implementation work
* Pipeline Version promotion workflow mechanics — downstream operational work, coordinated with [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md)
* Tombstone and Redaction Record serialization and representation — downstream implementation work
* legal review process for licensing posture classification — outside scope
* compliance-regime-specific policies (jurisdiction-specific data-protection rules) — outside scope; when committed, they compose onto this document's policy shapes rather than replace them

---

## Open Questions

* How is a posture change propagated to embeddings that were produced under a prior Representation DerivationRun? If Training-Compatible becomes Analytical-Only for a Source, the embeddings derived from that Source are governance-tombstoned for training purposes but may remain for retrieval purposes; the double-life of that state is flagged as operational complexity.
* How is a Signal's Evidence tombstoning reconciled with the requirement that every Signal carries Evidence ([SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md))? A Signal whose Evidence access is tombstoned remains a record but becomes non-reviewable at Evidence level; whether it remains Surfaced, moves to Stale, or moves to Retired is a lifecycle-transition question that belongs jointly to [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) and NARRATIVE_ANALYSIS.md.
* How is quality monitoring itself resource-bounded under the low-capital posture? Periodic sampling is committed here; specific schedules are deferred but flagged as an ongoing operational cost that must be sized deliberately.
* How are governance records themselves retained if the low-capital posture becomes tighter? Flagged: governance-record retention is load-bearing for audit, and its reduction is a non-trivial decision.

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the derivation layers, immutability, and temporal model this document stewards.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the Evidence & Provenance Store that holds governance records.
* [DATA_ACQUISITION.md](./DATA_ACQUISITION.md) originates licensing postures and Source Quality criteria that this document enforces and monitors.
* [INGESTION_SPEC.md](./INGESTION_SPEC.md) produces the Raw provenance this document tracks.
* [DOCUMENT_PROCESSING.md](./DOCUMENT_PROCESSING.md) produces the Normalized provenance and Segmentation-stability signal this document monitors.
* [EVENTS_AND_PIPELINES.md](./EVENTS_AND_PIPELINES.md) defines Pipeline Versions and DerivationRuns whose governance (promotion, retirement) this document owns.
* [SEARCH_AND_RETRIEVAL.md](./SEARCH_AND_RETRIEVAL.md) exposes governance records and provenance to internal callers.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines Signal anatomy; this document governs Signal retention, tombstoning, and licensing-posture enforcement.
* SECURITY_AND_PRIVACY.md (deferred) owns the threat model and access discipline; boundary held identically.
* EVALUATION.md (deferred) owns Signal quality; the boundary with Source Quality and Ingestion Quality is held here.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary; new terms introduced here (Tombstone, Redaction Record, Source Quality, Ingestion Quality, Governance Record, Posture Carrying) are flagged for extension in the cluster's closing summary.
