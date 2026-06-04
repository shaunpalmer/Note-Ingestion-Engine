# Architecture v2 — Transform-First Note Pipeline

**Status:** Proposed design (replaces the *direction* of the old pipeline)
**Reads after:** `note/PID_DESIGN_PROCESS.md`
**Old design (kept for history, not the plan):** `note/my_automation_pipeline.md`

---

## 0. The one-sentence shift

**Old direction:** `extract → tag → score → file in a folder` (a sorting machine).
**New direction:** `extract → GATE → THINK → compose a decision-ready note → file, with provenance` (a thinking machine that happens to also file).

The folder routing still exists — but it is now the *last, cheapest* step, not the point.

The refined north star is now captured in `config/note_quality.md`:

> Turn forgotten material into trusted, searchable, linked, decision-ready knowledge.

---

## 1. The pipeline (new shape)

```
[ Legacy files: pdf/docx/doc/xls/html/txt/md/psd/video ]
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 1 — EXTRACT  (cheap, well-understood)                │
│   Registry → Adapter → era-aware parser utility            │
│   Output: ExtractionResult{ text, source_meta, status }    │
│   status ∈ {ok, empty, ocr_needed, corrupt}                │
└───────────────────────────────┬───────────────────────────┘
                                 ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 2 — GATE  (deterministic, no LLM, protects thinking) │
│   • drop empty/corrupt → quarantine                        │
│   • detect duplicates, exports, logs, boilerplate          │
│   • "is this worth thinking about?" YES → think  NO → bin  │
└───────────────────────────────┬───────────────────────────┘
                          YES    ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 3 — THINK  ★ THE HEART ★  (local LLM as reasoner)    │
│   Input:  chunked text + source_meta                       │
│   Output: DecisionNote (schema, see §3) — NOT just tags    │
│     • essence + why it matters  • distilled key points     │
│     • facts/figures worth keeping  • future questions      │
│     • business/project/person/org/topic retrieval fields   │
│     • value axis + scrap axis (independent)                │
│     • uncertainty + reason  • fact vs interpretation line  │
└───────────────────────────────┬───────────────────────────┘
                                 ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 4 — COMPOSE  (build the actual note artefact)        │
│   • write human note (.md): decision surface + raw excerpt │
│   • write machine sidecar (.ai.md / .meta.json): scores,   │
│     provenance, source hash, model, discarded-summary      │
│   • ALWAYS backlink to the untouched original              │
└───────────────────────────────┬───────────────────────────┘
                                 ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 5 — PLACE & RECORD  (the old "routing", demoted)     │
│   • route by note's own tags → vault category folder       │
│   • collision policy {skip|version|force}                  │
│   • uncertain → /review  (with reasoning attached)         │
│   • update single state file (idempotency by source hash)  │
└───────────────────────────────────────────────────────────┘
                                 ▼
              Observers (decoupled): log, daily report, metrics
```

The critical change vs the old design: **Stage 3 produces a DecisionNote, not metadata.** The old pipeline's LLM call only returned `{category, status, type, confidence}` — a label. The new one returns a trusted decision surface: what this source is, what value it contains, what future questions it can answer, and how much of the result is fact vs interpretation.

---

## 2. Why each stage exists (so nothing is cargo-culted)

| Stage | Why it earns its place |
|---|---|
| Extract | Get clean text out of opaque containers. Cheap, deterministic, format-specific. |
| Gate | Thinking is the expensive resource. Never spend it on empty/corrupt/duplicates/obvious-scrap. Deterministic so it's debuggable. |
| **Think** | **The product.** Turns raw material into trusted, linked, decision-ready knowledge. |
| Compose | Turns the LLM's structured reasoning into actual files a human and a RAG system can use. |
| Place | Filing. Genuinely the least important step. Must not pretend to be the point. |

---

## 3. The two contracts that matter most

Everything hinges on two schemas. Define these *first* (PID Steps 2 & 4).

### 3a. ExtractionResult (Stage 1 output)
```
ExtractionResult:
  text:        str            # extracted markdown/plain text
  source_meta: dict           # path, vendor, original ext, created/modified, hash
  status:      enum           # ok | empty | ocr_needed | corrupt
```
The `status` field is the fix for the old "empty extraction silently looks like scrap" bug.

### 3b. DecisionNote (Stage 3 output — the heart)
```
DecisionNote:
  note_type:      str           # concept | meeting | reference | decision | research | log | media | invoice | tutorial
  title:          str           # clear human title
  essence:        str           # one sentence: what is this, really?
  summary:        str           # short plain-English summary
  why_it_matters: list[str]     # decision/project/memory/business value
  key_points:     list[str]     # distilled signal, noise removed
  keep_facts:     list[str]     # specific facts/figures/dates/obligations worth preserving
  business_area:  list[str]     # Super Clean, Project Studios, LinuxBox, etc.
  project:        list[str]
  people:         list[str]
  organisations: list[str]
  topics:         list[str]
  proposed_links: list[str]     # candidate links/topics, not invented certainties
  tags:           list[str]
  possible_actions: list[str]   # what this recovered material can support
  answers_future_questions: list[str]  # future retrieval hooks
  source_relevance: str         # why this note deserves to exist
  value_score:    float 0..1    # independent: how worth keeping?
  scrap_score:    float 0..1    # independent: how much is noise?
  uncertainty:    float 0..1    # model's honesty flag
  uncertainty_reason: str       # WHY it's unsure (for the review queue)
  fact_interpretation_boundary: str  # what is source fact vs AI interpretation
  discarded_summary: str        # what it threw away & why (reversibility)
  raw_excerpt:    str           # compact trust anchor, not full source dump
```
`value_score` and `scrap_score` are **independent axes** (sigmoid, not softmax) — exactly as the old notes correctly intuited but never built. A note can be mostly noise yet contain one crucial fact: high scrap *and* high value.

The schema intentionally asks: **what future question could this answer?** That field is not decoration. It aligns the generated note with actual tired-human retrieval later.

---

## 4. Components & relationships (what the main loop imports)

The orchestrator depends **only on abstractions**:

```
Orchestrator
  ├─ Registry          (ext/magic-bytes → Adapter)        # Stage 1
  ├─ Gate              (is this worth thinking about?)      # Stage 2
  ├─ Reasoner          (LLM thinking → DecisionNote)        # Stage 3
│     └─ LLMClient   (Ollama + retry + circuit breaker + fallback model)
  ├─ Composer          (DecisionNote → .md + sidecar)       # Stage 4
  ├─ Placer            (route + collision + review queue)  # Stage 5
  ├─ StateManager      (single schema, atomic, hash-keyed)
  └─ events (signals)  (observers: report/log/metrics)
```

The orchestrator must **not** import individual adapters, vendor parsers, or know folder names. It asks the Registry for an adapter and the Placer where things go.

### Patterns, finalised (no buzzwords)
- **Adapter** — one per vendor; thin router. *(kept)*
- **Registry** — ext/magic-bytes → adapter; this *is* the factory, no separate Factory. *(kept; drop "Factory"/"Singleton" language)*
- **Strategy** — era-specific parser utilities behind each adapter (legacy-binary vs modern-XML). *(kept — strongest idea in the old notes)*
- **Anti-Corruption Layer** — validated schemas (`ExtractionResult`, `DecisionNote`) at the extraction and LLM boundaries. *(new emphasis)*
- **Circuit Breaker + retry** — around the LLM client. *(reuse from old V2)*
- **Observer** — decoupled reporting/logging/metrics. *(reuse from old V2, now actually wired in)*

---

## 5. Directory layout (transform-first)

```
knowledge-pipeline/
├── config/
│   ├── paths.conf              # SINGLE source of truth
│   ├── note_quality.md         # "what a good note is" (PID Step 1) — human spec
│   ├── scrap_heuristics.json   # gate rules
│   └── categories.json
├── src/
│   ├── orchestrator.py         # the 5-stage loop; abstractions only
│   ├── config.py               # the ONLY config loader
│   ├── models.py               # ExtractionResult, DecisionNote, StateEntry
│   ├── registry.py
│   ├── adapters/{base,microsoft,adobe,google,video}.py
│   ├── utilities/              # era-aware parsers (Strategy)
│   │   ├── microsoft/{doc_legacy,docx_modern,xls_legacy,xlsx_modern}.py
│   │   ├── pdf/{text_pdf, ocr_pdf}.py        # OCR path = the missing hole, now filled
│   │   └── html/, video/
│   ├── gate/{scrap_filter.py, emptiness.py}  # Stage 2
│   ├── reason/{reasoner.py, prompts.py}      # Stage 3 — the heart
│   ├── llm/{client.py, circuit_breaker.py}
│   ├── compose/{note_writer.py, sidecar_writer.py}
│   ├── place/{router.py, review_queue.py}
│   ├── state/manager.py        # ONE schema
│   └── events/{signals.py, handlers.py}
├── runners/run-ingest.sh       # thin: warm Ollama → call orchestrator. NO data logic in bash.
├── docs/adr/                   # decisions recorded
└── tests/                      # contract tests + golden-file extraction tests
```

---

## 6. What this fixes vs the old pipeline

| Old problem | Fix here |
|---|---|
| LLM used as tag-stamper | LLM is the Reasoner producing a DecisionNote (Stage 3) |
| "Value" = which folder | "Value" = independent score gating a *transformation* |
| Empty extraction looks like scrap | `status` enum + Gate separate "couldn't read" from "not worth keeping" |
| No OCR | `utilities/pdf/ocr_pdf.py` + `ocr_needed` status |
| Two parallel codebases sharing one state file (`by_hash` vs `entries`) | One StateManager, one schema |
| 6 copies of `load_config()` | One `config.py` |
| Data logic inside bash heredoc | Orchestrator is Python; bash only sequences |
| Routing collisions overwrite files | Explicit collision policy + review queue |
| `route_to_vault.py` uses `sys` without importing it | Removed in rewrite; covered by contract tests |
| Self-reported LLM confidence used as the gate | Deterministic Gate is the gate; LLM scores are advisory metadata |
| Generic AI summaries that erode trust | DecisionNote separates fact, interpretation, uncertainty, and raw excerpt |

---

## 7. Gate refinements

The Gate must not ask "is this valuable?" That is too semantic and belongs later.

It asks: **is this worth thinking about?**

Required gate signals:
- `min_meaningful_token_count` — prevents empty/near-empty extraction from looking like scrap.
- `entropy_threshold` — catches pure formatting noise and repetitive machine output.
- `duplicate_similarity_threshold` — catches near duplicates beyond exact SHA-256 matches.
- `machine_export_detector` — flags Slack dumps, log exports, app backups, and generated boilerplate.
- `ocr_needed` — routes image-only PDFs to OCR/review instead of binning them.

Gate outcomes:
- `think` — send to Stage 3.
- `archive_minimal` — create an Archive Mode note with minimal processing.
- `quarantine` — corrupt, unreadable, or suspicious.
- `ocr_needed` — send to OCR path before scoring.

---

## 8. Linking phases

Do not start with embedding-based linking. It creates wrong backlinks, graph noise, and trust erosion too early.

Phases:
1. **Tags and properties first** — cheap, predictable retrieval: `business_area`, `project`, `people`, `organisations`, `topics`, `note_type`.
2. **String-based link suggestions** — match `proposed_links` to existing note titles and aliases.
3. **Embedding-based linking** — only once the vault has enough quality notes (roughly 300-500+) to justify semantic retrieval.

Links should mean something. Over-linking is just another form of clutter.

---

## 9. Success metric (the real one)

Not "how many files were sorted."
**"For a sample of processed items, does the output help me find, trust, connect, or act on something I had forgotten?"**

If a human reviewing 20 random outputs says "yes, this gives me decision-ready recovered knowledge," the architecture is doing its job. If they say "this is just an AI summary" or "this just moved my files around," it isn't — and we're back to the wrong direction.
