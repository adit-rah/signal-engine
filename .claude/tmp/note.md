# Prompt Engineering Notes — Signal Engine Doc Agents

Working notes for the head architect (Claude) to recall when drafting Wave
prompts for the doc-writing agents.

---

## Core Principle

Prompts must **fully inform** the agent without **pre-architecting** the
system on their behalf.

The agent is the one making structural decisions. The head architect's job is
to ensure they have:

- every piece of relevant context
- every relevant constraint
- every relevant principle
- every non-goal
- the correct voice and style reference
- explicit acceptance criteria
- awareness of what other documents exist and how theirs fits in

The head architect's job is **not** to give the agent a skeleton of the
answer.

---

## Mistakes Made in First Prompt Draft (do not repeat)

In the Wave 1 prompt, the following were pre-specified and should have been
left to the agent:

- Listed "Recommended initial components" for `ARCHITECTURE.md` (Ingestion
  Layer, Document Processing Layer, Entity & Temporal Store, etc.)
- Listed "Recommended initial entities" for `DATA_MODEL.md` (Company,
  Executive, Industry, Theme, Document, Statement, etc.)
- Listed "Recommended initial signal types" for `SIGNAL_DEFINITIONS.md`
  beyond what `CONTEXT.md` already defines

These are structural calls the agent should make based on the constraints
and principles provided. Listing them turns the prompt into a rubber-stamp
request.

---

## Do This Instead

For each deliverable, specify:

1. **Purpose** of the document (what question it answers)
2. **Audience** (who will read it and why)
3. **Inputs** (which files to read, with paths)
4. **Constraints** (what the document must respect)
5. **Non-goals** (what it must not do)
6. **Voice** (reference CONTEXT.md as exemplar)
7. **Required structural properties** (must be extensible, must be
   traceable, must not contradict X) — not required section headings
8. **Deferred decisions** (explicit list of things the agent must defer to
   named downstream documents)
9. **Acceptance criteria** (self-check list)

Do **not** specify:

- Which components exist
- Which entities exist
- Which signal types exist beyond those defined in `DOMAIN_GLOSSARY.md` or
  `CONTEXT.md`
- The structure of the document's answer
- Section headings that imply structural decisions (e.g. "Major Components"
  is fine because every architecture doc has components; "Recommended:
  Ingestion Layer, Processing Layer..." is not fine)

---

## Section Headings — Subtle Rule

Section headings that describe **categories of content** (e.g. "Purpose",
"Audience", "Open Questions", "Deferred Decisions") are fine — they are
about the shape of the document.

Section headings that describe **specific structural answers** (e.g. "The
Ingestion Layer", "The Fusion Layer") are not fine — they are the agent's
job to decide.

When in doubt: if swapping in a different correct answer would require
changing the heading, the heading is too prescriptive.

---

## When Structural Hints Are Okay

If `CONTEXT.md` or another confirmed input already commits to a structural
decision (e.g. CONTEXT.md names "Structural Layer", "Semantic Layer",
"Signal Layer"), the agent should honor it. The prompt may reference these
*as coming from the inputs*, not as the head architect's recommendation.

Example phrasing that is okay:

> "`CONTEXT.md` §11 names three conceptual layers. The architecture
> document should respect this framing or, if it diverges, surface the
> divergence explicitly for human review."

Example phrasing that is not okay:

> "Recommended components: Structural Layer, Semantic Layer, Signal
> Layer..."

The first cites a source. The second invents prescription.
