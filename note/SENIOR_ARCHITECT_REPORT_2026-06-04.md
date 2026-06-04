# Senior Architecture Report — Local Knowledge Ingestion Pipeline

**Prepared by:** Senior Architect (review engagement)
**Date:** 2026-06-04
**Repository:** `automation-scripts`
**Review type:** Point-in-time architectural assessment against the transform-first direction
**Disposition:** Proceed to a controlled rebuild of the orchestration layer; freeze further extension of the legacy flow.

---

## Why — Purpose of This Report

This report exists to give a clear, evidence-based answer to a single question:

> Does the system, as currently built, do what the project now needs it to do?

The project's intent has changed. The goal is no longer to sort and file documents. The goal is to recover value from a large, mixed, decade-old body of files and turn it into trusted, searchable, linked, decision-ready Obsidian knowledge.

A change of intent of this size demands an architectural audit before any further code is written. Continuing to build on a foundation that encodes the old intent would compound cost and risk. This report establishes the current position, names the structural risks, and defines what must be decided and done before further implementation.

This is a design report. It contains no implementation code.

---

## What — Scope and Method

The assessment was performed by reading the live repository: the ingestion scripts, the orchestration runner, the configuration and state files, the data contracts, and the existing architecture notes. Evidence is cited by file and line.

The system was measured against the target architecture recorded in the project's own notes:

- `config/note_quality.md` — the definition of a good output note.
- `note/ARCHITECTURE_v2_transform_first.md` — the five-stage transform-first pipeline.
- `note/PID_DESIGN_PROCESS.md` and `note/DECISIONS_AND_CHECKLIST.md` — purpose, principles, and decisions.

The target pipeline is:

```text
1. Extract  →  2. Gate  →  3. Think / Transform  →  4. Compose  →  5. Place & record
```

The system was not judged on whether it runs. It was judged on whether its structure serves the stated outcome.

---

## Executive Summary

The project is at a healthy and well-timed inflection point. The design thinking is now sound; the implementation has not yet followed it.

**Overall assessment:** the codebase is a competent **document-tagging-and-filing pipeline** with several high-quality infrastructure components. It is **not yet** a knowledge-transformation pipeline. The gap between the two is structural, not cosmetic.

There are, in effect, two codebases sharing one repository:

- **A legacy procedural pipeline** (`process_one_file.py`, `scan_documents.py`, `route_to_vault.py`, `normalize_confidence.py`, `archive_low_value.py`) — this is what the daily runner actually executes.
- **A more modern component set** (`config.py`, `models.py`, `state_manager.py`, `ollama_client.py`, `circuit_breaker.py`, `signals.py`, `handlers.py`, `process_one_file_v2.py`) — better engineered, but **not wired into the running pipeline** and flagged for deletion in `CODE_EVALUATION.md`.

These two halves disagree on the most safety-critical contract in the system — the state file schema — which is a live defect, not a future risk.

**The three findings that matter most:**

1. **Purpose mismatch.** The LLM is used as a metadata stamper returning `{title, summary, tags, backlinks, value, confidence}` (`scripts/ingestion/process_one_file.py:116`). The target requires a reasoner producing a rich `DecisionNote` (`config/note_quality.md:114`). This is the central conflict; everything else is secondary.

2. **State schema split (active defect).** The running runner and scanner read and write `by_hash`/`by_path` (`scripts/runners/run-daily-ingest.sh:73`, `scripts/ingestion/scan_documents.py:77,147`), while the persisted state file and the validated model use `entries` (`state/processed-files.json:4`, `scripts/ingestion/models.py:163`). The pipeline can silently fail to detect queued or already-processed files.

3. **Extraction is extension-shallow and format-naive.** Detection is by file suffix only, and `.doc` is routed to the modern `.docx` parser (`scripts/ingestion/extract_text.py:54-61`). For a decade of legacy and mixed formats this will fail at scale and silently discard real value.

**Recommendation:** keep the strong infrastructure components, retire the legacy flow as the authority, define two contracts (`ExtractionResult`, `DecisionNote`), and rebuild a thin Python orchestrator around the five-stage model. Validate the thinking step on real content before investing in extraction breadth.

---

## Current-State Architecture

### What the system does today

The daily runner `scripts/runners/run-daily-ingest.sh` executes seven stages: warm Ollama, scan, process, normalize confidence, route to vault, archive low-value, write report. In architectural terms this is:

```text
scan (extension filter)
  → extract text (suffix dispatch)
    → LLM metadata generation
      → sidecar (.ai.md)
        → confidence normalization
          → route to folder (tags/value/confidence)
            → archive low-value
              → daily report
```

The deliverable of this pipeline is a **filed, tagged document with a metadata sidecar**. The deliverable the project now wants is a **decision-ready note that recovers and surfaces the value inside the source**. The pipeline is optimised for placement; the goal is comprehension.

### Component inventory and grading

| Component | File | Role | Grade |
|---|---|---|---|
| Path config | `config/paths.conf` | Single path source | Keep |
| Config loader (modern) | `scripts/ingestion/config.py:18` | Cached typed accessors | Keep; make canonical |
| Config loader (legacy) | 7× duplicated `load_config()` | Per-script copies | Retire |
| Validation models | `scripts/ingestion/models.py:20` | Pydantic ACL | Keep foundation; replace schema |
| State manager | `scripts/ingestion/state_manager.py:24` | Locking + atomic writes | Keep; make canonical |
| LLM client | `scripts/ingestion/ollama_client.py` | Ollama + fallback | Keep |
| Circuit breaker | `scripts/ingestion/circuit_breaker.py` | Resilience | Keep |
| Signals/handlers | `scripts/ingestion/signals.py`, `handlers.py` | Observer events | Keep; rewire after composer exists |
| Text extractor | `scripts/ingestion/extract_text.py:54` | Suffix dispatch | Reuse functions; retire as boundary |
| Legacy processor | `scripts/ingestion/process_one_file.py` | Active metadata flow | Retire as authority |
| V2 processor | `scripts/ingestion/process_one_file_v2.py` | Orphaned modern flow | Harvest, then retire |
| Scanner | `scripts/ingestion/scan_documents.py` | Queueing, old state | Rewrite |
| Router | `scripts/ingestion/route_to_vault.py` | Tag→folder | Demote/rewrite |
| Confidence normalizer | `scripts/ingestion/normalize_confidence.py` | Post-hoc scoring | Retire |
| Daily runner | `scripts/runners/run-daily-ingest.sh` | Orchestration + data logic in bash | Replace with thin wrapper |

---

## Gap Analysis

### Gap 1 — The thinking step is missing (highest severity)

The system has no Stage 3 in the intended sense. The LLM prompt asks for shallow metadata (`scripts/ingestion/process_one_file.py:103-117`; duplicated in `process_one_file_v2.py:111-124`), and the validated output schema `MetadataOutput` contains only `title, summary, tags, backlinks, value, confidence` (`scripts/ingestion/models.py:20-55`).

The target `DecisionNote` (`config/note_quality.md:114-144`) additionally requires `note_type`, `essence`, `why_it_matters`, `key_points`, `keep_facts`, `business_area`, `project`, `people`, `organisations`, `topics`, `possible_actions`, `answers_future_questions`, `source_relevance`, independent `value_score` and `scrap_score`, `uncertainty` with reason, `fact_interpretation_boundary`, `discarded_summary`, and `raw_excerpt`.

This is the difference between metadata about a document and recovered, trustworthy knowledge. It is the project's reason for existing, and it is absent.

### Gap 2 — No deterministic gate

There is no Stage 2. Files are filtered only by extension at scan time (`scripts/ingestion/scan_documents.py:73`) and by emptiness after extraction (`scripts/ingestion/process_one_file.py:256`). Retention decisions depend on the LLM's self-reported `value`/`confidence` after the model has already run (`scripts/ingestion/archive_low_value.py:89`, `scripts/ingestion/route_to_vault.py:92`).

The intended design uses a cheap, deterministic gate *before* the LLM to decide "is this worth thinking about?" — detecting empties, corrupt files, OCR-needed scans, logs, receipts, boilerplate, near-duplicates, and metadata-only files. Using the LLM's own confidence as the gate is architecturally backwards and wastes the most expensive resource in the pipeline.

### Gap 3 — Extraction is format-naive

Detection is suffix-only and the format coverage is `.txt, .md, .pdf, .docx` plus a mis-mapped `.doc` (`scripts/ingestion/extract_text.py:54-66`). `requirements.txt` confirms only `pypdf` and `python-docx` are present — no magic/MIME detection, no OCR, no legacy Office, no spreadsheet, no media libraries.

Against the documented target set (legacy and modern Office, RTF, Google exports, PDF text vs scanned, PSD/AI/INDD metadata, HTML, CSV/JSON/XML, logs, images, audio, video), this is a narrow slice. Critically, routing `.doc` (legacy binary OLE) to the modern XML parser will fail on real files, and every failure currently collapses to an empty string — indistinguishable from a genuinely empty document.

### Gap 4 — No extraction-status contract

Extraction returns a bare string (`scripts/ingestion/extract_text.py:54`). There is no way to distinguish `ok`, `empty`, `ocr_needed`, `corrupt`, `unsupported`, and `metadata_only`. This collapses six different operational realities into one, which makes the gate, the review queue, and trust-handling impossible to build correctly. The target `ExtractionResult{ text, source_meta, status }` (`note/ARCHITECTURE_v2_transform_first.md:88-99`) is the missing contract.

### Gap 5 — No adapter/registry boundary

There is no Registry, no adapter interface, and no vendor/era separation. Extraction is a suffix-keyed dictionary inside one module. Adding a format means editing the central extractor (closed for extension, open for modification — the inverse of OCP). The orchestrator is coupled to concrete extraction rather than to an abstraction.

### Gap 6 — Output note quality is below standard

The generated sidecar contains a title, summary, a generic "Why it matters" line, and a source link (`scripts/ingestion/process_one_file.py:200-225`; the V2 variant at `:170-233` is better formatted but equally shallow). It does not preserve exact facts, list future questions, separate fact from interpretation, expose uncertainty, or carry structured retrieval properties. Measured against `config/note_quality.md`, the output does not yet qualify as a decision-surfacing note.

### Gap 7 — Tagging carries too much architectural weight

Tags drive folder placement directly (`scripts/ingestion/route_to_vault.py:70-95`, `scripts/ingestion/handlers.py:120-137`) against a hardcoded category set. The target requires three retrieval layers — search, structured properties (business_area/project/people/organisations/topics/note_type/status), and meaningful links — with tags as one layer, not the organising principle.

### Gap 8 — State and configuration integrity (active defect)

- **Schema split:** runner and scanner use `by_hash`/`by_path` (`scripts/runners/run-daily-ingest.sh:73`, `scripts/ingestion/scan_documents.py:77,147,157`); persisted state and models use `entries` (`state/processed-files.json:4`, `scripts/ingestion/models.py:163`). These are incompatible and both write paths are live.
- **Duplication:** `load_config()` is reimplemented in seven scripts; the canonical loader exists at `scripts/ingestion/config.py:18` but is not used by them.
- **Locking:** `StateManager` provides filelock + atomic writes (`scripts/ingestion/state_manager.py:24-61`), but the legacy scripts write state without it (`scripts/ingestion/scan_documents.py:161`, `scripts/ingestion/process_one_file.py:312`).
- **Bash owns data logic:** the runner parses state JSON via inline Python (`scripts/runners/run-daily-ingest.sh:67-78`), violating the principle that bash sequences and Python owns data.

### Gap 9 — Provenance and reversibility are partial

Originals are preserved and copied, not deleted (`scripts/ingestion/route_to_vault.py:135-140`) — good. But there is no raw excerpt embedded for trust, no fact/interpretation boundary, no source hash surfaced in the note body, and the vault write has no collision policy (same-named files overwrite). Aggressive distillation is only safe when reversibility is guaranteed; today it is only partially guaranteed.

---

## Risk Assessment

| # | Risk | Likelihood | Impact | Notes |
|---|---|---|---|---|
| R1 | State schema split corrupts dedup/queue | High | High | Live now; silent failure mode |
| R2 | `.doc` and legacy formats fail silently as "empty" | High | High | Real value discarded as scrap |
| R3 | Building more on the legacy flow increases rework | High | Medium | Compounding architectural debt |
| R4 | LLM confidence used as retention gate | High | Medium | Unreliable signal; wrong files archived |
| R5 | No collision policy on vault write | Medium | Medium | Overwrites in target folders |
| R6 | Two parallel codebases drift further | Medium | Medium | Maintenance and trust cost |

---

## Recommendations

### Keep (reuse with confidence)

- `config/paths.conf` and the cached loader `scripts/ingestion/config.py` — promote to the single configuration source.
- `scripts/ingestion/state_manager.py` — adopt as the only state access path.
- `scripts/ingestion/ollama_client.py` and `circuit_breaker.py` — the LLM resilience boundary.
- `scripts/ingestion/models.py` — keep as the validation layer; replace the schema it carries.
- `scripts/ingestion/signals.py` / `handlers.py` — retain the observer mechanism for logging, reporting, and review events.
- SHA-256 hashing and the original-preserving copy approach.
- `config/note_quality.md` and the `note/` design set — the correct north star.

### Rewrite

- The orchestrator: replace the bash-driven, data-bearing runner with a thin runner plus a Python orchestrator implementing the five stages.
- The scanner: detect by magic bytes with extension fallback; write the single canonical state schema.
- Extraction: re-expose existing parser functions behind a Registry → Adapter → parser-utility boundary, returning `ExtractionResult`.
- The router: demote to a final placement stage driven by structured properties and a defined collision policy.

### Retire

- `scripts/ingestion/process_one_file.py` as the authority (harvest, then remove).
- `scripts/ingestion/normalize_confidence.py` — superseded by independent `value_score`/`scrap_score`/`uncertainty`.
- The inline state-parsing logic in the runner.
- The duplicated `load_config()` copies.
- `process_one_file_v2.py` once its resilience patterns are folded into the new orchestrator.

### Clarify (decisions required before coding)

1. Canonical `business_area` vocabulary (e.g. Super Clean Services, Project Studios, AYS, LinuxBox, Obsidian, personal admin, theology, marketing, data/programming).
2. Allowed `note_type` set (reference, how-to, idea, decision, archive, meeting, contract, invoice, client-record, media, log, scrap).
3. Gate strictness and the review-vs-archive policy (recommended: review-first until calibrated; never auto-delete).
4. OCR policy (recommended: flag `ocr_needed`, batch later).
5. Media policy (recommended: transcribe short media; sample long media).
6. Raw-excerpt policy in the composed note.
7. Linking phase (recommended: properties/tags first, string-matched links second, embeddings later).
8. State migration decision for the existing `entries` file before the next run.

---

## Next Steps (before further coding)

1. **Stabilise state and config.** Choose one state schema (`entries` is already on disk and validated) and route all reads/writes through `StateManager`; make `config.py` the only loader. This closes the live R1 defect.
2. **Lock the two contracts.** Finalise `ExtractionResult` and `DecisionNote` as Pydantic models derived from `config/note_quality.md`. These become the interfaces every stage obeys.
3. **Prove the thinking step on real content.** Build only the reasoner prompt + `DecisionNote` validation, and run it against 5–10 existing text/markdown files. Confirm the output meets the note-quality standard before any investment in extraction breadth or OCR.
4. **Then** introduce the gate, the registry/adapters, the composer, and the placer in that order, wiring observers for reporting last.

---

## Closing Assessment

This is not a failing project; it is a project that has correctly outgrown its first design. The infrastructure quality (validation, locking, resilience, signalling) is above average for a solo effort, and the design notes now articulate the right goal with unusual clarity.

The single most important architectural action is to stop treating the legacy filing pipeline as the system of record and to make the **thinking step** real — because that step is the entire point of the project. The state-schema split should be fixed immediately as a correctness matter; everything else should follow the contracts-first, prove-the-core-first sequence above.

> North star: build a trusted recovery system that turns forgotten material into searchable, linked, decision-ready Obsidian knowledge — and let filing be the quiet last step, not the purpose.
