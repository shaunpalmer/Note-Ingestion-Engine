# Project Status Report — Architecture & Transform-First Direction

**Date:** 2026-06-04
**Status:** Design direction clarified; implementation not yet aligned
**Scope:** Current automation pipeline, architecture notes, extraction/tagging/state/config structure, and the new transform-first Obsidian goal.

---

## 1. Executive Summary

The project has reached an important architectural turning point.

The existing automation system is close in plumbing but not yet correct in purpose. It currently behaves like a **document ingestion and filing system**: scan files, extract text, ask the LLM for metadata, tag the result, score confidence, route it to folders, and archive low-value items.

The new architecture changes the target.

The system should become a **value-recovery and decision-surfacing pipeline**:

> Turn old files, scraps, documents, notes, and media into searchable, linked, trusted, decision-ready Obsidian knowledge.

This means filing and tagging are still useful, but they are no longer the main product. The product is the generated Obsidian note: something that helps a human later understand, trust, connect, and act on recovered material.

The current codebase contains useful parts, but the active pipeline still reflects the old architecture. The next stage should be careful design consolidation before more implementation.

---

## 2. The Three Whys

### Why 1 — Why does this project exist?

The project exists because years of scattered files contain hidden value that is currently hard to find, trust, or reuse.

The raw files include documents, notes, contracts, technical material, business ideas, marketing scraps, PDFs, Word files, logs, exports, media, and other mixed formats. Some are rubbish. Some are valuable. Some may contain one useful fact buried inside a large amount of noise.

The point is not merely to store these files in Obsidian. The point is to recover usable knowledge from them.

### Why 2 — Why is the current architecture not enough?

The current architecture mostly answers:

> Where should this file go?

But the new goal requires answering:

> What reusable value is inside this file, how can I trust it, and what future question could it help answer?

The current system does extraction, tagging, scoring, and routing. That is useful, but it does not yet perform the deeper thinking step needed to create decision-ready notes.

### Why 3 — Why does the transform-first design matter?

Obsidian is not just a folder system. It is a thinking surface.

A useful Obsidian note should let a tired future human quickly answer:

- What is this?
- Why does it matter?
- What exact facts should be preserved?
- What project, person, organisation, business area, or topic does it relate to?
- What could I use it for?
- What future question could this answer?
- What was discarded?
- Where is the original source?

The transform-first architecture matters because it changes the centre of gravity from **filing files** to **recovering decision-ready knowledge**.

---

## 3. The Three Whats

### What exists now?

The project currently has:

- A working local automation structure.
- `config/paths.conf` for shared paths.
- Ingestion scripts under `scripts/ingestion/`.
- A daily runner at `scripts/runners/run-daily-ingest.sh`.
- Basic text extraction for `.txt`, `.md`, `.pdf`, `.docx`, and incorrectly `.doc` through the `.docx` path.
- Ollama-based metadata generation.
- Sidecar `.ai.md` files.
- Confidence normalization.
- Tag/value/confidence-based routing.
- Archive logic for low-confidence or throwaway material.
- A newer V2 set of useful components: Pydantic models, state manager, circuit breaker, Ollama client, and signals.
- New design notes that define the transform-first direction.
- `config/note_quality.md`, which now defines what a good generated Obsidian note should become.

### What is wrong with the current direction?

The current direction is too filing-first.

It treats the LLM mainly as a metadata assistant. The prompt asks for:

```json
{"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}
```

That is too shallow for the new goal.

The system should instead produce a `DecisionNote` with fields such as:

- `note_type`
- `essence`
- `why_it_matters`
- `key_points`
- `keep_facts`
- `business_area`
- `project`
- `people`
- `organisations`
- `topics`
- `possible_actions`
- `answers_future_questions`
- `source_relevance`
- `value_score`
- `scrap_score`
- `uncertainty`
- `uncertainty_reason`
- `discarded_summary`
- `raw_excerpt`

The current pipeline produces metadata. The target pipeline should produce useful recovered knowledge.

### What should the project become?

The project should become a five-stage transform-first pipeline:

```text
1. Extract
2. Gate
3. Think / Transform
4. Compose Obsidian note
5. Place and record state
```

Each stage should have a clear purpose:

- **Extract:** Get content and metadata out of real file formats.
- **Gate:** Decide whether the material is worth spending thinking effort on.
- **Think / Transform:** Turn the material into a decision-ready `DecisionNote`.
- **Compose:** Write a human-useful Obsidian note with provenance and trust boundaries.
- **Place and record:** File it last, record state, and route uncertain items to review.

---

## 4. The Three Hows

### How should extraction work?

Extraction should be based on real file type detection, not only file extensions.

Preferred design:

```text
magic bytes / MIME detection
    → Registry
        → Adapter
            → parser utility
                → ExtractionResult
```

The `ExtractionResult` should include:

```yaml
ExtractionResult:
  text: str
  source_meta: dict
  status: ok | empty | ocr_needed | corrupt | unsupported | metadata_only
```

This matters because `.doc`, `.docx`, and `.rtf` are different problems. A legacy Word binary file should not be treated like a modern XML Word file.

### How should the thinking step work?

The LLM should not be prompted as a tag stamper.

It should be prompted as a reasoner:

> What reusable value is inside this source, what does it relate to, what future question could it answer, what exact facts must be preserved, what can be discarded, and what uncertainty remains?

The output should be a validated `DecisionNote`, not loose prose and not only metadata.

### How should Obsidian retrieval work?

The system should use three retrieval layers:

1. **Search** — raw text, summaries, facts, excerpts.
2. **Tags / properties** — structured filtering by area, type, status, project, people, organisations.
3. **Links** — meaningful relationships between notes.

Tags are useful, but they are not the whole architecture. They should support retrieval, not drive the entire system.

---

## 5. Current Architectural Gaps

### 5.1 Extraction gaps

Current extraction is too narrow.

It supports only a small set of formats and handles some incorrectly.

Major gaps:

- `.doc` is routed through the `.docx` extractor.
- No `.rtf` support.
- No `.xls` / `.xlsx` support.
- No `.ppt` / `.pptx` support.
- No HTML extraction layer in the main extractor.
- No CSV / JSON / XML strategy.
- No OCR for scanned PDFs or images.
- No video/audio transcription strategy.
- No PSD / AI / INDD metadata-only strategy.
- No `unsupported`, `corrupt`, `ocr_needed`, or `metadata_only` extraction statuses.

### 5.2 Detection gaps

The current extractor relies on file extensions.

That is risky because old archives often contain misnamed files, exported files, or files with missing/incorrect extensions.

The preferred design is:

```text
Primary: magic bytes / MIME detection
Fallback: file extension
```

### 5.3 Adapter / Registry gaps

The current project does not yet have a clean boundary like:

```text
Registry → Adapter → parser utility → ExtractionResult
```

The orchestrator and extractor still work with direct extension dispatch.

This makes it harder to add support for old Microsoft formats, Adobe formats, OCR, media, and metadata-only files without creating a large fragile script.

### 5.4 Gate gaps

There is no real deterministic Gate yet.

The Gate should decide:

> Is this worth thinking about?

It should detect:

- empty files
- corrupt files
- OCR-needed files
- receipts
- logs
- boilerplate
- duplicate and near-duplicate material
- very low-content scraps
- metadata-only files
- unsupported formats

The current system relies too much on LLM value/confidence after the LLM call. That is backwards. The Gate should protect the LLM step before it happens.

### 5.5 Reasoner gaps

The current LLM prompt asks for metadata.

It does not ask for:

- decision usefulness
- exact preserved facts
- future questions
- possible actions
- business/project/person/organisation relationships
- fact vs interpretation separation
- discarded material
- uncertainty reasoning

This is the biggest conceptual gap.

### 5.6 Composer gaps

The current sidecar output is not yet a proper Obsidian decision note.

It lacks:

- strong essence
- why this matters
- key details
- possible actions
- future questions
- trust and source section
- raw excerpt
- structured properties for business/project/people/organisations/topics

`config/note_quality.md` now defines the target, but the code has not implemented it.

### 5.7 State and config gaps

There are multiple config loaders and multiple state schemas.

Risks:

- several scripts duplicate `load_config()`
- old scripts use `by_hash` and `by_path`
- newer V2 state uses `entries`
- the actual state file currently uses `entries`
- the daily runner still expects `by_hash`
- some scripts write state without locking
- the newer `StateManager` uses locking and atomic writes but is not used everywhere
- Bash currently performs JSON/state logic inside `run-daily-ingest.sh`

This must be resolved before more ingestion runs.

---

## 6. What Currently Matches the New Architecture

The project already has some strong foundations.

Reusable pieces:

- `config/paths.conf` — useful central path configuration.
- `config/note_quality.md` — correct quality standard for generated notes.
- `scripts/ingestion/config.py` — good start for a single config loader.
- `scripts/ingestion/state_manager.py` — good file-locking and atomic-write state manager.
- `scripts/ingestion/ollama_client.py` — useful LLM client boundary.
- `scripts/ingestion/circuit_breaker.py` — useful resilience around Ollama.
- `scripts/ingestion/models.py` — useful Pydantic validation foundation.
- `scripts/ingestion/signals.py` — useful observer/event pattern.
- `scripts/ingestion/handlers.py` — useful starting point for review/report/routing events, though routing needs redesign.
- SHA-256 file hashing — correct idempotency basis.
- Basic extraction functions — reusable as parser utilities behind adapters.
- Sidecar/provenance idea — correct, but needs richer note composition.

The project is not a failure. It has the right materials. The issue is that the active flow still expresses the old goal.

---

## 7. What Conflicts With the New Architecture

Conflicting parts:

- `process_one_file.py` is old procedural metadata-stamping logic.
- The active daily runner still calls `process_one_file.py` instead of a transform-first orchestrator.
- `extract_text.py` is extension-dispatch, not Registry/Adapter based.
- `scan_documents.py` defaults to `.txt,.md` and writes old state format.
- `route_to_vault.py` treats folder placement as a central goal.
- `archive_low_value.py` archives based on LLM value/confidence.
- `normalize_confidence.py` reinforces the old single-confidence model.
- Current `MetadataOutput` is too shallow.
- Current state formats are split.
- Bash runner contains data logic.

These should not guide future architecture.

---

## 8. Recommendations

### Recommendation 1 — Freeze the old architecture as transitional

Do not keep extending the old ingestion pipeline as if it were the final system.

It can remain as a reference and source of reusable parts, but the target architecture should be the transform-first pipeline.

### Recommendation 2 — Lock the two core schemas before coding

Define final schemas for:

```text
ExtractionResult
DecisionNote
```

These schemas should become the contracts that all stages obey.

### Recommendation 3 — Build Stage 3 first on already-extracted text

Before building adapters, OCR, and media support, test whether the Reasoner can produce good `DecisionNote` outputs from plain text inputs.

If the Reasoner cannot produce useful decision-ready notes, more extraction plumbing will not solve the main problem.

### Recommendation 4 — Replace metadata prompting with DecisionNote prompting

The LLM prompt should stop asking for only title, summary, tags, value, and confidence.

It should ask for recovered value, facts, relationships, actions, uncertainty, discarded material, and future questions.

### Recommendation 5 — Introduce the Gate before the LLM

The Gate should be deterministic and cheap.

It should decide whether the file deserves thinking effort before the LLM is called.

### Recommendation 6 — Rebuild orchestration around the five-stage flow

The runner should become thin.

The main pipeline should live in Python and should follow:

```text
Extract → Gate → Think / Transform → Compose → Place and record
```

### Recommendation 7 — Wrap extraction as adapters

Do not keep adding format logic into one extractor script.

Create proper adapters for:

- Microsoft formats
- Google exports
- Adobe/design/document formats
- plain text/scrap formats
- media formats

Each adapter should delegate to specific parser utilities.

### Recommendation 8 — Make routing the last step

Routing should happen after a high-quality note exists.

Placement should use structured properties, review status, note type, and business area — not only tags and confidence.

### Recommendation 9 — Unify state and config now

Before running more ingestion, decide:

- one config loader
- one state schema
- one state writer
- one locking strategy

This is a stability prerequisite.

---

## 9. Missing Decisions

Shaun still needs to decide:

1. **Canonical business areas**
   - Super Clean Services
   - Project Studios
   - AYS
   - LinuxBox
   - Obsidian
   - personal admin
   - theology
   - marketing
   - data/programming

2. **Allowed note types**
   - reference
   - how-to
   - idea
   - decision
   - archive
   - meeting
   - contract
   - invoice
   - client-record
   - media
   - log
   - scrap

3. **Gate strictness**
   - auto-archive obvious scraps?
   - route uncertain items to review?
   - never delete automatically?

4. **OCR policy**
   - automatic OCR?
   - review queue first?
   - batch OCR only?

5. **Video/audio policy**
   - full transcription under 10 minutes?
   - sampled/chunked transcription over 10 minutes?
   - skip metadata-only media?

6. **Raw excerpt policy**
   - how much raw content should appear inside the generated note?

7. **Linking strategy**
   - tags/properties first?
   - string-matched links second?
   - embeddings later?

8. **Migration strategy**
   - rebuild transform-first orchestrator fresh?
   - or refactor old scripts in place?

Recommended answers:

- review-first until trust is built
- tags/properties first, links second, embeddings later
- rebuild orchestrator fresh
- reuse extraction functions, config, state manager, LLM client, and validation layer

---

## 10. Recommended Next Steps

### Step 1 — Write final schema definitions

Define `ExtractionResult` and `DecisionNote` as the canonical contracts.

No implementation should proceed until these are stable enough to guide the pipeline.

### Step 2 — Test the Reasoner on existing text

Use 5–10 existing `.txt` or `.md` examples and manually check whether the generated `DecisionNote` outputs satisfy `config/note_quality.md`.

This validates the heart of the system before building more plumbing.

### Step 3 — Resolve state and config drift

Choose one state schema and one config loader before running the pipeline again.

The current split between `entries` and `by_hash/by_path` is too risky to ignore.

---

## 11. Final Status

The project is in a **pre-implementation architecture correction phase**.

It should not yet be judged by whether the current scripts run. It should be judged by whether the architecture is now pointing toward the right human outcome.

Current status:

```text
Design direction:        clarified
Quality target:          defined in config/note_quality.md
Old pipeline:            working but filing-first
Transform-first code:    not yet implemented
Main architectural risk: continuing to extend the old flow
Best next move:          validate DecisionNote output before more plumbing
```

The correct north star is now:

> Build a trusted recovery system that turns forgotten material into searchable, linked, decision-ready Obsidian knowledge.
