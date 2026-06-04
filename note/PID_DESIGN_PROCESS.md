# PID — Design Process & Project Initiation

**Status:** Draft / thinking layer
**Supersedes the *direction* of:** `note/my_automation_pipeline.md` (kept untouched as raw history)
**Companion files:**
- `note/ARCHITECTURE_v2_transform_first.md` — the new architectural design
- `note/DECISIONS_AND_CHECKLIST.md` — libraries, patterns, open questions
- `config/note_quality.md` — the Stage 3 quality standard

---

## 0. Why this document exists

The existing notes (`my_automation_pipeline.md`) are a transcript of several AI chat sessions stitched together. They contain real ideas, but also: duplicated blocks, billing tangents, sales closers, and **three different architectures that were never reconciled**. That is the "in-between stage" — useful working-through, but not a plan.

A plan only exists once we have:
1. A clear statement of **the problem**.
2. A clear statement of **the goal** (and why the current direction misses it).
3. **Principles** that decide trade-offs for us.
4. A **design process** (the order in which we think, not just code).
5. **Decisions** on libraries and patterns — actually made, not half-mentioned.

This document does 1–4. The companion files do 5 and the architecture.

---

## 1. The problem (stated plainly)

> A decade of scattered, mixed-format personal and work files (PDF, DOCX, legacy DOC/XLS, HTML, TXT, MD, PSD, video) sits in legacy folders. Most of it is noise. Some of it is valuable. Right now it is unusable as *knowledge* because it is opaque, unstructured, and unsorted.

The pain is **not** "the files are in the wrong folders." The pain is **"there is meaning trapped inside thousands of opaque files and I can't think with it."**

---

## 2. The goal — and why the current direction is wrong

### What the project currently does
The built pipeline is a **convert-and-file** system:

```
extract text  →  tag it  →  score it  →  route it into a folder
```

It optimises for **throughput and sorting**: "move 7,000 files into the right category."

### What the project is *supposed* to do
The real goal is a **value-recovery and decision-surfacing** system:

```
raw scrap  →  THINK about it  →  produce trusted, searchable, linked, decision-ready knowledge
```

It should optimise for **recovering usable meaning**: turning an inaccessible source into a note that helps answer future questions, supports decisions, preserves facts, exposes uncertainty, and links back to its source.

### The diagnosis (the answer to "what's the problem with the architecture?")
**The current architecture has lots of plumbing and almost no thinking step.**

- It *files* notes; it does not yet make them decision-ready.
- The LLM is used as a **metadata stamper** (tags + a confidence number), not as a **reasoner** that distils, rewrites, and connects.
- "Value vs scrap" is treated as a *routing decision* (which folder?) instead of a *transformation decision* (is there anything here worth extracting, and if so, extract it).
- Success is measured as "file landed in the right folder," when it should be measured as "the output helps me find, trust, connect, or act on recovered knowledge."

So the project is **close but pointed slightly wrong**: the bones (adapters, sidecars, state, local LLM) are reusable, but the **centre of gravity must move from routing to reasoning.**

---

## 3. Principles (these decide arguments for us)

1. **Decision-surfacing over transportation.** Moving a file is worthless; recovering usable knowledge is the product. Every stage must justify itself against "does this help me find, trust, connect, or act on this later?"
2. **The thinking step is the architecture's heart, not an afterthought.** The LLM reasoning pass is a first-class stage with its own `DecisionNote` contract, not a tag-stamper bolted on at the end.
3. **Lossless source, lossy-on-purpose output.** Never touch originals. The *output note* is allowed — encouraged — to throw away noise. Distillation is the point.
4. **Two questions, kept separate:** "Is there value here?" (gate) and "What is the distilled value?" (transform). Don't collapse them into one confidence number.
5. **Reversibility.** Every output note links back to its source. If the AI distils badly, a human can always find the original. This makes aggressive distillation safe.
6. **One source of truth** for config, state, and contracts. The old design drifted because there were many. (See companion docs.)
7. **Boring, local, private.** Local LLM, no cloud egress for sensitive material, no surprise costs. (This part of the old notes was right.)
8. **Human-in-the-loop by design, not by accident.** Uncertain transformations go to a review queue with the *reasoning* attached, not just a low score.
9. **Trust requires boundaries.** Each note must separate source facts, AI interpretation, uncertain guesses, and raw excerpt/source provenance.
10. **Retrieval is designed around future questions.** A note should say which future questions it can answer.

---

## 4. The design process (the order we think in)

This is the discipline the old notes lacked. Think in this order; do not skip ahead to folders/libraries.

**Step 1 — Define "a good note."**
Before any code: what does a *decision-surfacing* note look like? `config/note_quality.md` now defines the target: title, essence, why it matters, exact facts, actions, future questions, links/properties, source, and trust boundaries. Everything downstream serves this.

**Step 2 — Define the transformation contract.**
Input: raw extracted text + source metadata. Output: a structured `DecisionNote` (not just tags). Write this as a schema. This is the most important artefact in the whole project.

**Step 3 — Define the gate.**
A deterministic, cheap first filter that decides "is it even worth spending LLM thinking on this?" (Keyword/heuristic scrap detection, emptiness/OCR-failure detection.) The gate protects the expensive thinking step.

**Step 4 — Define the thinking step.**
The LLM pass that produces the `DecisionNote` per the Step-2 contract. This is where reasoning lives: identify reusable value, preserve exact facts, propose retrieval surfaces, flag uncertainty, state what was discarded, and list future questions this note can answer.

**Step 5 — Define provenance & reversibility.**
How every output ties back to its source and records what was done to it.

**Step 6 — *Only now* design extraction (adapters) and filing (routing).**
These are the cheap, well-understood ends. They feed and follow the thinking step. They are not the product.

> The old notes started at Step 6 (folders, adapters, libraries) and never really did Steps 1–5. That is why it feels like "not enough thinking."

---

## 5. What we keep from the old work

Reusable bones (don't throw these away):
- **Adapter + Registry + era-aware parser utilities** for extraction — genuinely correct for messy multi-format input.
- **Sidecar/companion model** (original + `.md` + machine-readable sidecar) — good provenance foundation.
- **Local LLM via Ollama** — right call for privacy/cost.
- **Hash-based idempotency** (SHA-256) — correct dedup approach.
- **Two-pass + chunking** for big files — pragmatic for context limits.

What changes: the **purpose of the LLM stage** (DecisionNote reasoner, not stamper) and the **definition of success** (trusted recovered knowledge, not correct folder).

---

## 6. What "done thinking" looks like (exit criteria for the planning phase)

We can stop planning and start building when we can answer, on one page each:
- [x] What does a finished good note contain? (Step 1 — see `config/note_quality.md`)
- [ ] What is the exact `DecisionNote` input→output contract? (Step 2)
- [ ] What deterministic gate decides "worth thinking about"? (Step 3)
- [ ] What does the LLM thinking prompt/contract demand? (Step 4)
- [ ] How does provenance/reversibility work? (Step 5)
- [ ] Which extraction libraries per format, and the routing policy? (Step 6 — see DECISIONS doc)
- [ ] Which single config/state/contract sources of truth? (see DECISIONS doc)

Until those boxes are ticked, we are still in the in-between stage — and that's fine, as long as we know it.
