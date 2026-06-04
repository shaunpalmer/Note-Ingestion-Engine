# Note Quality Standard — Decision-Surfacing Notes

**Status:** Draft standard for Stage 3 (`Reasoner`)
**Purpose:** Define what a processed Obsidian note must become.
**North star:** Turn forgotten material into trusted, searchable, linked, decision-ready knowledge.

---

## 0. Core Position

Obsidian is not being used here as a document store or a pretty archive.

This vault should answer questions such as:
- What do I know about Super Clean Services?
- What contracts, obligations, prices, or client agreements already exist?
- What marketing ideas have I already had?
- How did I solve this Linux, networking, scripting, or automation problem before?
- What people, projects, jobs, organisations, or business areas does this relate to?
- What useful action can this old material support now?

A good processed note is therefore not merely a summary.

> A good note is a decision-ready abstraction with provenance.

It must be easy to find, quick to re-understand, connected to related ideas, and honest about what is fact, interpretation, uncertainty, and source material.

---

## 1. What Makes a Note Good

A processed Obsidian note is good when it:

1. **Has a clear idea or purpose.** The reader can tell what the note is about in seconds.
2. **Reduces friction to re-understand later.** It explains the value without forcing a reread of the source file.
3. **Supports future decisions.** It says what this material can help with.
4. **Connects to people, projects, business areas, and topics.** Links and properties create retrieval surfaces.
5. **Preserves provenance.** It always points back to the untouched original.
6. **Separates fact from interpretation.** Exact facts must not be blurred with AI inference.
7. **Is scannable in under 10 seconds.** Essence, value, facts, actions, and source must be visible quickly.
8. **Keeps enough raw material to trust the distillation.** A short raw extract/excerpt should be available in the note where useful.

---

## 2. Required Note Shape

Every generated note should follow this default structure unless a note-type template overrides it.

```md
---
title:
source_file:
source_hash:
created_from:
extraction_method:
note_type:
business_area:
project:
people:
organisations:
topics:
tags:
value_score:
scrap_score:
uncertainty:
review_status:
---

# Clear Human Title

## Essence
One strong sentence: what this is and why it matters.

## Summary
Short plain-English summary of what the source contains.

## Why This Matters
- What value does this contain?
- What decision, project, memory, business area, or future work can it support?

## Key Details
- Important facts, dates, people, prices, obligations, technical steps, or ideas.

## Possible Actions
- Practical next uses for this material.

## Answers Future Questions
- Questions this note may help answer later.

## Related Areas
- [[Relevant Business Area]]
- [[Relevant Project]]
- [[Relevant Topic]]

## Trust & Source
- Exact facts preserved from source:
- AI interpretation:
- Uncertainty / needs review:
- Original file:
- Source hash:

## Raw Extract
<details>
<summary>Source excerpt</summary>

Short raw extract or important excerpt from the source.

</details>
```

The `Raw Extract` block should not reproduce huge documents. It should preserve enough source material for trust and quick checking. For long sources, store the full extracted text separately and include only a meaningful excerpt in the composed note.

---

## 3. Required DecisionNote Schema

Stage 3 should produce a `DecisionNote`, not a generic summary.

```yaml
DecisionNote:
  note_type: str
  title: str
  essence: str
  summary: str
  why_it_matters: list[str]
  key_points: list[str]
  keep_facts: list[str]
  business_area: list[str]
  project: list[str]
  people: list[str]
  organisations: list[str]
  topics: list[str]
  proposed_links: list[str]
  tags: list[str]
  possible_actions: list[str]
  answers_future_questions: list[str]
  source_relevance: str
  value_score: float
  scrap_score: float
  uncertainty: float
  uncertainty_reason: str
  fact_interpretation_boundary: str
  discarded_summary: str
  raw_excerpt: str
```

### Field Intent

- `note_type` — drives composition layout. A contract should not look like a tutorial.
- `why_it_matters` — forces utility framing.
- `business_area`, `project`, `people`, `organisations`, `topics` — structured retrieval surfaces.
- `possible_actions` — converts recovered material into usable forward movement.
- `answers_future_questions` — makes retrieval explicit; this is one of the most important fields.
- `source_relevance` — explains why the note deserves to exist.
- `fact_interpretation_boundary` — separates exact source facts from AI interpretation.
- `raw_excerpt` — protects against over-distillation regret.

---

## 4. Note Types and Composition Modes

Not every source deserves the same treatment. Stage 3 must choose a `note_type` and composition mode.

### 4.1 Reference Mode

For contracts, invoices, legal-ish documents, client records, supplier documents, receipts worth keeping.

Goal: preserve accuracy and retrieval.

Use:
- summary
- exact facts
- dates
- people/organisations
- obligations
- amounts/prices
- source link
- review status

Do not over-compress exact obligations, prices, dates, or names.

### 4.2 How-To Mode

For tutorials, technical notes, setup instructions, commands, scripts, configuration notes.

Goal: make the knowledge repeatable.

Use:
- purpose
- prerequisites
- steps
- commands
- gotchas
- verification
- related systems/projects

### 4.3 Idea Mode

For marketing ideas, business concepts, strategy notes, theological reflections, creative plans, product/service ideas.

Goal: extract reusable thinking.

Use:
- core idea
- why it matters
- possible use
- related business/project/topic
- next action
- future questions it could answer

### 4.4 Decision Mode

For past decisions, trade-offs, architecture choices, business choices, client/project choices.

Goal: preserve context and reasoning.

Use:
- decision made
- options considered
- reason
- consequences
- related projects
- future review trigger

### 4.5 Archive Mode

For low-value but not-trash material.

Goal: make it findable without spending much reasoning effort.

Use:
- short summary
- minimal facts
- tags/properties
- source link
- low value score

Archive Mode should not waste Stage 3 effort producing a polished note.

---

## 5. Distillation Rules

The system should be neither a faithful archive nor a hallucinated rewrite.

Use **two-layer distillation**:

1. **Decision abstraction:** essence, why it matters, key details, actions, future questions.
2. **Trust anchor:** exact source link, source hash, exact facts, raw excerpt, uncertainty reason.

Rules:
- Remove redundancy and boilerplate.
- Preserve exact names, dates, amounts, obligations, commands, and technical instructions.
- Mark uncertainty explicitly rather than smoothing it away.
- Do not invent relationships to vault notes.
- Prefer short, direct, specific language over generic AI phrasing.
- If the value is unclear, route to review rather than pretending certainty.

---

## 6. Retrieval Layers

A useful Obsidian vault uses three retrieval layers.

### 6.1 Search
Raw text, extracted content, titles, summaries, and preserved facts.

### 6.2 Tags and Properties
Structured filtering.

Examples:
```yaml
tags:
  - area/superclean
  - area/project-studios
  - type/contract
  - type/how-to
  - status/review
business_area:
  - Super Clean Services
project:
  - Weekend Cleaning Job
note_type: contract
people:
  - Sophie
```

### 6.3 Links
Meaning and relationships.

Examples:
```md
Related:
- [[Super Clean Services]]
- [[Project Studios]]
- [[Lead Generation]]
- [[End of Tenancy Cleaning]]
- [[Obsidian Knowledge Pipeline]]
```

Do not over-link. Early phases should prefer tags/properties first, then string-matched link suggestions, then embedding-based links only when the corpus is large enough to justify it.

---

## 7. Trust Rules

Each processed note must make trust visible.

Separate:
- **Fact:** directly present in the source.
- **Interpretation:** AI's understanding of what the source means.
- **Decision:** a conclusion or recommendation.
- **Guess:** uncertain inference that needs review.

A useful note should make the reader think:

> I know where this came from, what was preserved, what was inferred, and whether I need to review it.

If the system cannot provide that, route the item to review.

---

## 8. Stage 3 Prompt Requirements

The Reasoner prompt must not ask: "Summarise this."

It must ask:

> What reusable value is inside this, what does it relate to, what future question could it answer, and how should it be trusted or used later?

The model must answer:
1. What is this document or fragment?
2. What useful value does it contain?
3. What business area, project, person, organisation, or topic does it relate to?
4. Is it a reference, how-to, idea, decision, archive, media, log, invoice, contract, or scrap?
5. What facts must be preserved exactly?
6. What is interpretation rather than fact?
7. What can be safely discarded?
8. What should this link to or be grouped with?
9. What future question could this answer?
10. What action, if any, could this support?

---

## 9. Quality Check

A generated note passes quality review if a human can answer these in under 10 seconds:

- What is this?
- Why might I care?
- What exact facts should I trust?
- What is uncertain or needs review?
- What project/person/business/topic does it relate to?
- What could I use it for?
- Where is the original?

If not, the note is not good enough.
