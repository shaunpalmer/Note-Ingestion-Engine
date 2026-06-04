# Decisions & Checklist

**Status:** Working decisions + open questions
**Reads with:** `PID_DESIGN_PROCESS.md`, `ARCHITECTURE_v2_transform_first.md`

This is the "sort out the libraries, sort out the patterns" doc the old notes never finished. Two parts: (A) decisions made, (B) what should happen here — the checklist + open questions that need *you*.

---

## A. Decisions made

### Patterns (final)
- **Adapter** per vendor (thin router). ✅
- **Registry** (ext + magic-bytes → adapter). This is the factory; **no separate Factory pattern.** ✅
- **Strategy** = era-aware parser utilities (legacy-binary vs modern-XML) behind each adapter. ✅
- **Anti-Corruption Layer** = pydantic schemas (`ExtractionResult`, `DecisionNote`) at extraction and LLM boundaries. ✅
- **Circuit Breaker + retry** around the LLM client. ✅
- **Observer** (signals) for reporting/logging/metrics — decoupled from the loop. ✅
- **Dropped:** "Factory" and "Singleton" as named patterns (buzzwords, no fit). ❌

### Detection
- Primary: **magic bytes** (`python-magic` / libmagic). Fallback: extension. *(Old design used extension only — a landmine at scale.)*

### Libraries per format (extraction)
| Format | Library | Note |
|---|---|---|
| Modern Word `.docx` | `python-docx` | XML-based |
| Legacy Word `.doc` | `textract` / `olefile` / `striprtf` | binary; `python-docx` crashes on these |
| Modern Excel `.xlsx` | `openpyxl` or `pandas` | |
| Legacy Excel `.xls` | `xlrd` (1.2.0 era) or modern equivalent | `openpyxl` can't read `.xls` |
| PDF (text) | `pdfplumber` or `pymupdf` | better than `pypdf` for layout |
| PDF (scanned) | `pytesseract` + `pdf2image` (OCR) | **the missing path — now required** |
| HTML | `beautifulsoup4` | strip tags |
| PSD | `psd-tools` / metadata only | extract metadata, not pixels |
| Video | `whisper` / local transcription | <10 min full transcript; >10 min first 3 min + chunked summary |

### Infra
- **Language:** Python 3.11+ for all logic. Bash only sequences stages (warm Ollama → call orchestrator). No data logic in bash.
- **LLM:** local via Ollama; `qwen2.5-coder:7b` primary, fallback model configured.
- **Validation:** pydantic at boundaries.
- **State:** one file, one schema, keyed by SHA-256, atomic writes (`filelock`).
- **Config:** one `config.py` reading one `paths.conf`. Delete all other `load_config()` copies.

### Scoring
- **Sigmoid, independent axes** (`value_score`, `scrap_score`) — NOT softmax. A note can be high-scrap *and* high-value.
- **Deterministic Gate** decides whether to spend LLM thinking. LLM self-confidence is **advisory metadata only**, never the gate.

### Note target
- Stage 3 produces a **DecisionNote**, not a generic summary and not a metadata label. ✅
- The system exists to create **trusted, searchable, linked, decision-ready knowledge**. ✅
- `config/note_quality.md` is now the human quality standard Stage 3 must hit. ✅

### Linking phases
1. **Tags and properties first** (`business_area`, `project`, `people`, `organisations`, `topics`, `note_type`). ✅
2. **String-based link suggestions** once note titles/aliases exist. ✅
3. **Embedding-based linking later** when there are roughly 300-500+ quality notes. ✅

---

## B. What should happen here — checklist & open questions

### Must-decide-before-building (PID exit criteria)
- [x] **Define "a good note."** `config/note_quality.md` now defines a Decision-Surfacing Note standard.
- [ ] **Lock the `DecisionNote` schema** (Architecture §3b + `config/note_quality.md`). This is the transformation contract — the heart.
- [ ] **Lock the `ExtractionResult` schema** with the `status` enum.
- [ ] **Write the gate heuristics** (`scrap_heuristics.json`): empty/corrupt, min meaningful token count, entropy threshold, duplicate similarity, machine exports, OCR-needed.
- [ ] **Write the Reasoner prompt** that demands the `DecisionNote` schema — distil, link, flag uncertainty, separate fact from interpretation, list future questions, say what was discarded.

### Open questions for YOU (these can't be guessed)
1. **Scrap tolerance:** Auto-bin obvious scrap, or send everything to `/review` until trust is calibrated? (Recommend: review-first, then automate once calibrated.)
2. **Business areas / controlled vocabulary:** What are the canonical values for `business_area`? Examples: Super Clean Services, Project Studios, AYS, LinuxBox, personal admin, theology.
3. **Note types:** Which `note_type` values should be allowed on day one? Proposed: reference, how-to, idea, decision, archive, meeting, contract, invoice, media, log, scrap.
4. **Migration:** rebuild clean in the new `knowledge-pipeline/` layout, or refactor the existing scripts in place? (Recommend: rebuild the orchestrator + Stage 3 fresh, reuse extraction code as adapters.)
5. **Review threshold:** What values of `uncertainty`, `scrap_score`, and `value_score` route to `/review` vs `/archive`?

### First three ADRs to write (`docs/adr/`)
- **ADR-001:** Purpose is transformation, not filing. (Records the direction change.)
- **ADR-002:** One pipeline, one state schema, one config. (Kills the V1/V2 drift.)
- **ADR-003:** LLM is a Reasoner producing `DecisionNote`, not a tag-stamper.
- **ADR-004:** Vault retrieval starts with tags/properties, then string links, then embeddings later.
- **ADR-005:** Trust requires separating fact, interpretation, guess, and source excerpt.

### Sequencing (lowest-risk build order)
1. Lock the two schemas using `config/note_quality.md` as the standard. *(thinking, no code)*
2. Stand up `config.py` (one) + `StateManager` (one schema).
3. Build Stage 3 (Reasoner + prompt) against a handful of *already-extracted* text files — prove the transformation is good before touching extraction plumbing.
4. Wrap existing extraction as adapters behind a Registry.
5. Add Gate, Composer, Placer, review queue.
6. Add OCR + video.
7. Wire observers (report/log). Thin bash runner last.

> Note the order: **prove the thinking step works on real content first.** If Stage 3 doesn't produce notes that are genuinely better than the input, none of the plumbing matters — and we'll have caught the "wrong direction" before building it again.
