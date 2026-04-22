# SECURITY_AND_PRIVACY.md

## Purpose Of This Document

SECURITY_AND_PRIVACY.md defines the pragmatic security and privacy posture for the Signal Engine: who and what the system has to defend against, how it handles the data it touches, how it respects the sources it reads from, and what security properties its outward contract must hold.

This is an engineering and product-integrity document. It is not a compliance audit, a legal disclaimer, or a penetration-test plan. It is written for engineers who will build and operate the system and for anyone reviewing it for operational security.

Where this document and [CONTEXT.md](./CONTEXT.md) disagree, CONTEXT.md is authoritative. Vocabulary used here is defined in [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md).

---

## Scope And Non-Scope

### In scope

* the threat model the system operates under, at a conceptual level
* the posture for handling source text, derived artifacts, and user queries
* the posture for secrets: acquisition credentials, model weights, internal service credentials
* the posture for respecting source terms, attribution, and licensing constraints
* the security properties required of the API Boundary
* provenance as a first-class security property

### Out of scope

* specific tools, vendors, or key-management products
* specific vulnerability-scanning strategies or schedules
* incident response procedures (shape owned by downstream operations and FAILURE_MODES.md; observability hooks owned by OBSERVABILITY.md)
* retention, deletion, and governance rules (owned by DATA_GOVERNANCE.md)
* data acquisition strategy (owned by DATA_ACQUISITION.md)
* compliance frameworks and their checklists
* threat-model exercises that depend on deployment topology (deferred to downstream infrastructure work)

---

## Guiding Posture

The project commits to a small number of operating beliefs about security and privacy. Everything below is a consequence of these.

* The system informs a human; it does not act. Its attack surface is therefore about information, not about actions taken in the world ([SCOPE.md](./SCOPE.md) Non-Goals; [CONTEXT.md](./CONTEXT.md) §10).
* Models are trained and operated in-house (CONTEXT §6.1). Critical paths do not depend on external large-language-model APIs. This is a security property as much as a cost and control property.
* Explainability is required end-to-end (CONTEXT §3.3). Provenance is both a product feature and a security substrate.
* Source text is the core asset. Losing it, corrupting it, or misrepresenting it undermines every Signal the system emits.
* The system is built for depth over speed ([ASSUMPTIONS.md](./ASSUMPTIONS.md) U2, U6). Operational posture can favor careful handling over low-latency optimization.

---

## Threat Model

The system's threat model is framed in three questions: who would attack it, what would they be after, and which surfaces let them try.

### Who

* **Opportunistic actors** scanning for exposed credentials, unpatched services, or misconfigured storage. The most common category and the least targeted.
* **Source-adversarial actors** attempting to poison ingested text so that a downstream Signal reflects their narrative rather than an observed one. This category is domain-specific and credible given the subject matter.
* **Curious insiders or collaborators** with legitimate access who should not see everything the system stores. Insider risk is proportional to how much raw and derived material the system holds.
* **Competing products or replicators** attempting to exfiltrate curated artifacts — reconciled Entity mappings, Baselines, Speaker profiles, trained model weights — that would reduce the cost of imitating the system.
* **Inbound abuse of the API Boundary** — unauthenticated or authenticated callers attempting denial-of-service, prompt injection through free-text inputs, or oracle-style probing to reconstruct private data.

### What

* **Source text and its lineage** — raw artifacts, the provenance chain that anchors them, and the reconciled identity state that binds them to Entities and Speakers.
* **Derived analytical state** — Baselines, ThemeInstances, Behavioral Communication Profiles, emitted Signals, and the DerivationRun records that make them re-derivable.
* **Model weights and training corpora** — representation models, specialized models, and the datasets used to produce them. Trained weights are valuable; training corpora may carry licensing constraints (ASSUMPTIONS D6).
* **Credentials** — source-acquisition credentials, storage credentials, inter-component service credentials, deployment credentials.
* **User queries and query history** — what a user asked, which Signals they inspected, how their access pattern reveals their interest profile.

### Through

The exposed surfaces are:

* the **API Boundary** — the single intended external contract (ARCHITECTURE.md §14)
* the **Ingestion** pathway — the system's upstream interface to the outside world (ARCHITECTURE.md §1), including any acquisition tooling, however minimal (DATA_ACQUISITION.md owns specifics)
* the **Evaluation Harness** — not user-facing, but a pathway through which reviewers touch Signals and Candidate Signals (ARCHITECTURE.md §12)
* any **operator-facing surface** used to run, monitor, and re-derive — its specifics are deferred to downstream infrastructure but its existence is accepted
* **stored artifacts at rest** — raw, normalized, analytical, and Signal layers

The threat model does not include surfaces the system does not have. It has no trading surface, no recommendation surface, no autonomous action surface ([CONTEXT.md](./CONTEXT.md) §10; [SCOPE.md](./SCOPE.md) Non-Goals).

---

## The In-House Model Posture As A Threat-Model Lever

CONTEXT §6 commits the system to in-house models with no external LLM API in critical paths. This is usually read as a cost-and-control choice. It is also a security property.

### What this posture removes

* **Third-party prompt-injection surface in critical paths.** No critical-path component sends text to an external model whose behavior could be shifted by prompt-injection content embedded in ingested financial text. The Fusion Engine, Heuristic Analysis, Learned Analysis, and Representation are internal.
* **Third-party behavioral drift** in the interpretive layer. External models can change behavior between versions in ways the project cannot audit. In-house models change under DerivationRuns the project owns.
* **Outbound exfiltration of source text** to third-party model providers during analysis. Whatever leaves the system is deliberate.

### What this posture does not remove

* Ingested text can still be adversarially shaped (see Source-Adversarial Threats below). Model ownership defends against third-party injection, not against adversarial inputs written into source text itself.
* In-house models trained on poisoned corpora are still poisoned. Training-corpus hygiene is a concern for DATA_ACQUISITION.md and MODEL_STRATEGY.md; it is flagged here because it is the largest remaining model-centric risk.
* Optional local small-footprint language models (CONTEXT §6.2), if used, still operate on text — their use must be in-process or on-infrastructure, and their output still needs to be traceable.
* Non-critical-path uses of external models (offline research, evaluation tooling) are not forbidden by the architecture but are explicitly out of critical paths (ARCHITECTURE.md §Model Ownership Posture). Any such use must not become a silent dependency.

The operative principle is that no externally reachable service can rewrite the system's interpretive behavior in-place.

---

## Source-Adversarial Threats

The subject matter — financial communication — invites adversarial framing by construction. A speaker who wants a favorable narrative has incentive to shape what appears in a transcript.

The project treats source-adversarial framing as a feature of the domain, not a security incident. The system's response is:

* **Treat every input as untrusted text.** Ingested content flows through Document Processing and Entity Resolution before any analysis can attach claims to it. Attribution is a deliberate step, not an assumption.
* **Preserve raw text unmodified.** The Raw derivation layer (DATA_MODEL.md) is immutable. Analysis operates on Normalized artifacts, but the Raw artifact remains authoritative for disputes about what was actually said.
* **Require Basis and Evidence for every Signal** (CONTEXT §3.3, SIGNAL_DEFINITIONS.md Signal Anatomy). A Signal that cannot be traced to Spans is not emitted. This bounds the blast radius of manipulated text: the Spans are visible, and a human reviewing a Signal sees the material the system relied on.
* **Reserve judgment about incompatibility.** A Contradiction Event requires that two statements be judged incompatible rather than merely different (SIGNAL_DEFINITIONS.md §Contradiction Event). The system does not accept a claim of incompatibility just because the language differs.

Specific hardening of parsing paths against malformed or adversarial document structure is deferred to INGESTION_SPEC.md and DOCUMENT_PROCESSING.md.

---

## Data Handling Posture

### Sensitivity classes

The system handles four broad classes of data. Sensitivity is relative to what would happen if the class leaked, not to a regulatory category.

* **Source text** — typically public (earnings call transcripts, CONTEXT §8) but not necessarily free to redistribute. Treat as *publicly-observed, privately-held within the system*: widely available in principle, but the system's copy is an operational asset that respects source terms.
* **Derived analytical state** — Baselines, ThemeInstances, Behavioral Communication Profiles, Signals, Commentary. This is the system's intellectual output. Leakage would erode the project's position and may expose user query patterns (below).
* **Model weights and training corpora** — weights are a project asset. Training corpora may carry licensing constraints the project must respect (ASSUMPTIONS D6).
* **User-side state** — queries, access patterns, retrieval history. These reveal interest profiles and must be treated as private to the user.

### Source text and PII

Earnings call transcripts contain named executives speaking in their professional capacity. Speaker names and roles are public. The project treats Speaker identity as operational metadata, not as PII in the consumer sense. Personal addresses, contact information, or identifiers of private individuals do not normally appear.

If PII does appear — incidentally in an answer to a question, in a transcript provider's header metadata, or in a future domain beyond earnings calls — the posture is:

* the Raw artifact is preserved as received; the system does not silently rewrite source text
* PII-bearing spans are not surfaced independently of the Signal they support; the system does not build indexes that promote PII to a first-class queryable surface
* PII is not propagated into Commentary generation (Commentary generation method is owned by MODEL_STRATEGY.md; the constraint here is a constraint for that document)
* future Document subtypes expected to contain higher PII density (interviews, analyst commentary mentioning private individuals) must treat PII-handling as an entry condition, not as a post-hoc cleanup

### Speaker Baselines and Behavioral Profiles

Per-Speaker Baselines (DATA_MODEL.md) and Behavioral Communication Profiles (CONTEXT §5.3) model how a specific named executive communicates. This is not PII in the conventional sense, but it is a privacy-adjacent artifact: a profile of how an individual speaks.

* profiles are limited to Speakers acting in a public, attributed capacity within Source artifacts
* profile storage inherits the sensitivity of derived analytical state (above)
* the system does not build Speaker profiles for speakers outside the attributed speaking contexts of the domain
* downstream surfacing of Speaker profiles is a USER_EXPERIENCE.md concern and must not promote them into profile-browsing primitives

### User queries and retrieval history

A user's pattern of Signals examined, Entities watched, and queries posed is sensitive. It reveals an interest profile that may itself be material.

* user-side state is treated as private to the user
* aggregation of user behavior for evaluation (e.g. reviewer-attributed feedback in the Evaluation Harness) is permitted but must not leak individual-user query patterns into surfaces beyond their purpose
* specific retention and access policies are deferred to DATA_GOVERNANCE.md

### Retention, deletion, and re-derivation

Retention, deletion, and governance policy are owned by DATA_GOVERNANCE.md. This document notes only:

* the data model commits to immutability of Raw artifacts and to re-derivability of downstream layers (DATA_MODEL.md §Immutability And History)
* any deletion mechanism that does not respect immutability must be justified as a governance decision, not introduced as an engineering convenience
* governance policy for each sensitivity class above belongs in DATA_GOVERNANCE.md

---

## Secrets Posture

Secrets are handled at a conceptual level here. Specific key-management products and vault choices are deferred to downstream infrastructure.

### Three classes of secrets

* **Acquisition credentials.** Credentials that authorize the system to obtain Source artifacts (provider API keys, authenticated endpoints, crawl credentials where applicable). These grant access to external services and, if leaked, implicate the project's relationship with those services. Rotation, scoping, and attribution belong to acquisition tooling.
* **Model weights and training-state artifacts.** Not secrets in the cryptographic sense, but project assets whose distribution control matters. Weights are distributed to the components that perform inference; they are not distributed to surfaces that do not need them.
* **Inter-component and deployment credentials.** Service-to-service credentials, storage credentials, deployment credentials. Scoped to the component that needs them, not shared broadly.

### Posture commitments

* no secret appears in source repositories, artifacts, logs, Commentary, Evidence, Signal payloads, or API responses
* no secret crosses the API Boundary in either direction
* secrets are scoped to the component that needs them; a secret usable by one component is not implicitly usable by another
* rotation is a property of the system, not a one-time configuration; specific rotation policy is an infrastructure concern
* compromise of a single secret is expected to be survivable without system-wide compromise

These are posture commitments. The mechanics of enforcement — vaults, sealed environments, audit trails — belong to downstream infrastructure.

---

## Source Terms Posture

The system reads from sources that publish under terms. Respecting those terms is both a legal prudence and an engineering property: the system is not architected to disguise its access patterns.

### Commitments

* **Rate limits and cadence.** Acquisition tooling is expected to respect each source's rate limits. The low-capital operating posture (ARCHITECTURE.md §Low-Capital Constraint; ASSUMPTIONS T3, H5) is compatible with respectful cadence by construction.
* **Attribution.** Source identity is preserved on every Document and propagates to every derived artifact via the provenance chain (DATA_MODEL.md §Evidence Provenance And Traceability). A user examining a Signal can resolve which Source the supporting text came from.
* **Licensing posture.** The in-house model commitment (CONTEXT §6.1) depends on the ability to train on acquired text (ASSUMPTIONS D6). Training use must be compatible with the terms of each source. Where a source's terms prohibit training use, that source is not usable for training regardless of its availability for analysis.
* **No source misrepresentation.** The system does not remove, rewrite, or obscure Source attribution on stored artifacts. The Normalized artifact is a Normalization of the Raw artifact, not a replacement of it (DATA_MODEL.md).

### Deferred

* which specific sources are used, under what agreements, and with what cost profile → DATA_ACQUISITION.md
* the training-corpus composition decision (which sources contribute to which models) → MODEL_STRATEGY.md, informed by DATA_ACQUISITION.md
* formal license audit or provider-agreement review → outside this document; flagged as a precondition to training runs by the owner of MODEL_STRATEGY.md

This document commits the posture; DATA_ACQUISITION.md commits the practice.

---

## API Boundary Security Properties

The API Boundary (ARCHITECTURE.md §14) is the system's only intended external contract. Its specific shape is owned by API_SPEC.md; its security properties are committed here.

### Required properties

* **Authenticated by default.** No unauthenticated caller reaches Signal data, Evidence, Baselines, or historical query state. Any anonymous surface (for example, a health check) is explicitly and narrowly scoped.
* **Input validation at the boundary.** Free-text inputs from callers are validated and never concatenated into model prompts or analytical paths without passing through the same traceability discipline as ingested source text. Inputs that reach internal components are structured, not opaque strings.
* **Response shape discipline.** Responses return Signals, Evidence references, and query results against the data model. They do not include secrets, credentials, internal DerivationRun payloads beyond what Basis requires for Explainability, or raw infrastructure metadata.
* **No action surface.** The API does not expose an action-taking surface. It reads, it serves derived outputs, and it accepts feedback where the Evaluation Harness contract allows. It does not trade, transfer, or act in external systems ([SCOPE.md](./SCOPE.md) Non-Goals).
* **Rate limiting and abuse resistance.** The boundary is expected to withstand simple abuse patterns without leaking timing or existence information about private artifacts. Specific rate-limit mechanics are deferred; the property is asserted here.
* **Authorization respects data sensitivity.** Access controls align with the sensitivity classes defined above: user-side state is private to the user; derived analytical state follows the project's access model; credentials and weights never traverse the boundary.

### Explainability does not override authorization

Every Signal carries Basis and Evidence (CONTEXT §3.3). The Basis chain and the Spans it references are surfaced only to callers authorized for those Signals. Explainability is a property of what is shown, not a bypass for what is hidden. If a caller is not authorized for a Signal, it is not authorized for that Signal's explanation.

---

## Provenance As A Security Property

The Evidence & Provenance Store (ARCHITECTURE.md §11) and the DerivationRun abstraction (DATA_MODEL.md §Derivation Layers) exist to support explainability. They also function as a security substrate.

* **Tamper-visibility.** Every derived artifact names the DerivationRun that produced it. A quiet change to analytical output is visible as a change in DerivationRun, not as an invisible mutation.
* **Blast-radius containment.** Because the data model supports re-derivation, a discovered bad DerivationRun — whether from a model regression, a data-quality incident, or a security event — can be invalidated and its downstream artifacts re-derived rather than patched in place.
* **Signal retirement without deletion.** Signals found to be incorrect are expressed as Retired records with Lineage (SIGNAL_DEFINITIONS.md §Lifecycle State), not silently removed. Destructive correction is not an option the system reaches for.
* **Auditability.** The chain Signal → Basis → Evidence → Span → Document → Raw (DATA_MODEL.md §Evidence Provenance And Traceability) is a functional audit trail for any output the system emits.

These properties are consequences of the data-model choices already committed. This document names them as security properties so that downstream work does not treat them as optional.

---

## What This Document Does Not Commit

* specific key-management tools, secrets managers, or credential vaults
* specific deployment topology, network boundaries, or ingress/egress rules
* vulnerability scanning, dependency hygiene processes, or CI/CD controls
* specific authentication protocols, identity providers, or session models
* incident response procedures, runbooks, or on-call rotation
* specific retention durations, deletion policies, or purge mechanisms
* specific license terms for sources — those belong to DATA_ACQUISITION.md
* acceptable-use policy for users of the API — belongs to a future product-policy document
* regulatory or compliance frameworks — not adopted by this document as structure

Anything above left to "downstream" or "deferred" is intentionally not decided here so that it can be decided well elsewhere.

---

## Deferred Decisions

With named owners where identified:

* specific security tooling, vaults, and credential management — downstream infrastructure work
* vulnerability scanning and dependency-hygiene processes — downstream infrastructure work
* incident response and operational playbooks — downstream operations; observability hooks in OBSERVABILITY.md; failure-mode shape in FAILURE_MODES.md
* retention, deletion, and governance policy — DATA_GOVERNANCE.md
* data acquisition specifics including source-terms agreements — DATA_ACQUISITION.md
* training-corpus licensing composition — MODEL_STRATEGY.md, informed by DATA_ACQUISITION.md
* specific API authentication and authorization mechanics — API_SPEC.md
* parsing hardening for malformed or adversarial documents — INGESTION_SPEC.md and DOCUMENT_PROCESSING.md
* auditable review of Evaluation Harness reviewer access — EVALUATION.md

---

## Glossary Additions Recommended

Terms introduced or used in a committing way here that warrant [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) entries:

* **Source Terms Posture** — the project's commitment to respecting each source's rate limits, attribution requirements, and licensing terms
* **Sensitivity Class** — the four operational classes named above (source text, derived analytical state, model weights and training corpora, user-side state)
* **Behavioral Communication Profile** as a privacy-adjacent artifact — already defined in DOMAIN_GLOSSARY.md; recommend noting the privacy framing inline

---

## Relationship To Other Documents

* [CONTEXT.md](./CONTEXT.md) and [SCOPE.md](./SCOPE.md) are authoritative.
* [VISION.md](./VISION.md) establishes the posture this document operationalizes on the security side.
* [ASSUMPTIONS.md](./ASSUMPTIONS.md) supplies beliefs (notably D6 on licensing, T3 and H5 on low-capital posture, U2 and U6 on user latency tolerance) that shape the threat model.
* [DOMAIN_GLOSSARY.md](./DOMAIN_GLOSSARY.md) owns vocabulary.
* [ARCHITECTURE.md](./ARCHITECTURE.md) defines the components whose security properties are asserted here; §Model Ownership Posture is closely paired with this document's Model-Posture section.
* [DATA_MODEL.md](./DATA_MODEL.md) defines the immutability and provenance invariants this document relies on as a security substrate.
* [SIGNAL_DEFINITIONS.md](./SIGNAL_DEFINITIONS.md) defines the Basis and Evidence requirements that anchor explainability and blast-radius containment.
* [ETHICS_AND_LIMITATIONS.md](./ETHICS_AND_LIMITATIONS.md) is the companion document; where this one defines trust about data, that one defines trust about claims.
* DATA_ACQUISITION.md, DATA_GOVERNANCE.md, MODEL_STRATEGY.md, API_SPEC.md, INGESTION_SPEC.md, DOCUMENT_PROCESSING.md, OBSERVABILITY.md, FAILURE_MODES.md, and EVALUATION.md own the deferrals listed above.
