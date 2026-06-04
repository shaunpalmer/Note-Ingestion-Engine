# Golden Path Test Guardrails

**Status:** Architecture confidence harness  
**Purpose:** Prove the pipeline direction before scaling extraction, OCR, media handling, or routing complexity.  
**North star:** Real mixed-format source files become useful, trusted, searchable, linked Obsidian notes.

## Architect Position

The golden path is not ordinary unit testing. It is the antidote to correct lines in the wrong architecture.

A script can run, a parser can return text, and an LLM can produce tags while the system still fails the actual project. This project fails if it produces polished summaries that do not help Shaun recover value, make decisions, preserve facts, or trust the source.

The golden path exists to force the system to prove direction before it produces more plumbing.

## The Crisis It Prevents

The current risk is not lack of code. The current risk is architectural drift:

- Extraction can silently fail and look like empty content.
- The LLM can be used as a tag stamper instead of a reasoner.
- Tags and folders can become the architecture.
- Low-value junk can become polished fake-useful notes.
- Legacy and modern formats can be blurred together.
- State can be written through multiple schemas.
- Passing local scripts can create false confidence.

The right response is not a broad rewrite. The right response is a small, trusted harness that proves the pipeline shape.

## Golden Path Rule

Before adding more formats, OCR, media, or routing complexity, the system must pass the golden path test set.

Passing means the system produces decision-ready knowledge with provenance.

Failing means the architecture is still wrong, even if the code runs.

## Pipeline Under Test

```text
Extract -> Gate -> Think / Transform -> Compose -> Place and Record
```

Each stage must earn its place:

| Stage | Must prove |
|---|---|
| 1. Extract | Every file returns an `ExtractionResult` with status, source hash, provenance, and honest failure state. |
| 2. Gate | The deterministic gate runs before the LLM and can stop junk, route uncertainty, and preserve provenance. |
| 3. Think / Transform | The LLM returns a `DecisionNote`, not just title, summary, tags, and confidence. |
| 4. Compose | The system writes a readable Obsidian Markdown note with frontmatter, source, retrieval fields, and trust boundaries. |
| 5. Place and Record | Placement happens last, uses collision policy, and updates one canonical state manager. |

## Confidence Types

Every golden path review should check four kinds of confidence:

| Confidence type | Question |
|---|---|
| Extraction confidence | Did we correctly read or classify the source file? |
| Architecture confidence | Did the file move through the proper stages without shortcuts? |
| Knowledge confidence | Did the output note recover useful value? |
| Trust confidence | Can Shaun see where the information came from and what is uncertain? |

## Golden Test Set

| Test ID | File Type | Main Risk | Must Prove | Pass/Fail |
|---|---|---|---|---|
| GP-001 | Markdown | Over-processing | Useful note without damaging source |  |
| GP-002 | TXT scrap | Junk promotion | Gate handles scraps |  |
| GP-003 | Text PDF | Weak extraction | Text extracted correctly |  |
| GP-004 | Scanned PDF | Silent empty failure | Marked OCR-needed |  |
| GP-005 | DOCX | Basic Office parsing | Modern Word works |  |
| GP-006 | DOC | Legacy format confusion | Not treated as DOCX |  |
| GP-007 | XLSX | Table dump noise | Key figures summarised |  |
| GP-008 | XLS | Legacy spreadsheet confusion | Not treated as XLSX |  |
| GP-009 | Project Studios | Business retrieval | Correct business area/actions |  |
| GP-010 | Super Clean | Operational detail loss | Facts/prices/jobs preserved |  |
| GP-011 | How-to | Command loss | Steps/commands preserved |  |
| GP-012 | Junk/log | Polished rubbish | High scrap/low value/review |  |

## Required Output Per Fixture

Each golden fixture should produce or explicitly skip these artefacts:

1. `ExtractionResult` JSON.
2. `GateDecision` JSON.
3. `DecisionNote` JSON when the gate outcome is `think`.
4. Composed Obsidian Markdown note when a note is warranted.
5. Placement/state record or review queue record.
6. Review report entry explaining pass/fail and uncertainty.

A skipped LLM call can be a pass if the gate made the correct deterministic decision.

## Hard Fail Rules

Hard fail if any of these occur:

- Any file is silently treated as empty after failed extraction.
- `.doc` is processed as if it were `.docx`.
- `.xls` is processed as if it were `.xlsx`.
- The LLM is called before the deterministic gate.
- The output is only title, summary, tags, and confidence.
- The note lacks source provenance.
- The system writes state using more than one schema.
- Bash mutates state or performs data logic.
- A low-value file becomes a polished fake-useful note.
- Existing vault files can be overwritten without collision policy.

## Soft Fail Rules

Soft fail if any of these occur:

- Tags are vague or inconsistent.
- Future questions are generic.
- Possible actions are generic.
- Business area is missing when obvious.
- People or organisations are missed.
- Raw excerpt is missing for high-value source material.
- Uncertainty is present but unexplained.

## How To Exercise The Project

Do not start with the full vault. Do not start by adding libraries for every format.

Exercise the system in this order:

1. Build the golden path fixtures.
2. Run Stage 1 extraction only and review `ExtractionResult` status quality.
3. Run Stage 2 gate only and confirm no LLM calls happen before gate decisions.
4. Run Stage 3 on already-extracted useful text and confirm `DecisionNote` quality.
5. Run Stage 4 composition and inspect the actual Markdown note in Obsidian terms.
6. Run Stage 5 placement only after collision and review policies are explicit.
7. Update one golden path review report.

If a stage cannot produce the required contract, stop and fix the contract before adding breadth.

## Opinionated Next Three Steps

1. Lock `ExtractionResult`, `GateDecision`, and `DecisionNote` in the model layer.
2. Convert the golden path from documentation into executable contract tests with fixtures and expected outputs.
3. Prove Stage 3 on markdown/text fixtures before investing in PDF/OCR/Office breadth.

## What Copilot Must Do

When Copilot or another AI agent works on this project, it must first answer:

- Which golden path test does this change improve?
- Which pipeline stage does this change touch?
- Which contract does this change preserve or clarify?
- Could this accidentally strengthen the old filing-first pipeline?
- Does this improve trust, provenance, retrieval, transformation quality, or decision support?

If the answer is only "it processes more files," the change is probably premature.

## Reference Files

- `copilot-instructions.md`
- `config/note_quality.md`
- `docs/note/ARCHITECTURE_v2_transform_first.md`
- `docs/note/PID_DESIGN_PROCESS.md`
- `docs/note/DECISIONS_AND_CHECKLIST.md`
- `docs/design/AI_ARCHITECTURE_GUARDRAILS.json`
- `docs/Testing/GOLDEN_PATH_TEST_GUARDRAILS.json`
- `docs/Testing/Pass-Fail-rules.json`
- `docs/Testing/Golden-Path-Folder-Structure`
