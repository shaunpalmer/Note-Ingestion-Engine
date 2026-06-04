# Concise Project Report: Automation Stack Status & Architecture

**Date:** 2026-05-26  
**Reporter:** Kilo (Senior Developer Review)  
**Project:** local-automation-stack  
**Environment:** Fedora Linux, Python 3.14.4, Ollama local LLM

---

## 1. Capacity and Performance Analysis

### Current Baseline: 50 Files/Day

The project targets **50 files per day** for document ingestion. Let's reality-check this against actual measured performance.

**Measured timings from today's tests:**

| Operation | Time | Notes |
|-----------|------|-------|
| Ollama warm-up (cold start) | ~5s | One-time per batch |
| Single .txt file (106 bytes) | ~12s | Full pipeline: extract → Ollama → sidecar |
| Scanner (7,600 files) | ~15s | Dry-run, SHA256 hashing every file |
| Network check | ~3s | nmcli + ping + DNS |
| Confidence normalization | ~0.5s | Sigmoid across batch |

**Extrapolated throughput:**

If a 106-byte text file takes 12 seconds, and assuming linear scaling (it isn't, but for estimation):

| Scenario | Time | Hourly Rate | Daily Rate (8h) |
|----------|------|-------------|-----------------|
| 100-byte text file | 12s | 300/hr | 2,400 |
| 1,000-word document | ~25s | 144/hr | 1,152 |
| 5,000-word document | ~60s | 60/hr | 480 |
| 20,000-word document | ~180s | 20/hr | 160 |

**Verdict: 50 files/day is conservative.**

For typical text/markdown files under 2,000 words, the system can realistically process **200–400 files per day** on a single machine. The 50-file target was appropriate for a *cautious first phase* but should be revised upward once the pipeline is trusted.

**However**, the real bottleneck is not speed — it is **review bandwidth**. The AI generates sidecars that need human review. If you process 400 files/day but can only review 20, you have a queue management problem, not a throughput problem.

**Recommendation:**
- Keep the 50-file *automated processing* target for now
- Add a separate **review queue** limit (e.g., max 20 files pending review)
- When the review queue is full, pause new processing
- This is a **backpressure** mechanism — the pipeline slows down when the human can't keep up

---

## 2. Document Processing & Testing

### PDF Length Constraints: The Hidden Problem

**Current behavior:** `extract_text.py` reads the entire PDF into memory, then sends the full text to Ollama. No length checks exist.

**The `qwen2.5-coder:7b` context window:** 32,768 tokens. At ~0.75 words/token, that's roughly **24,500 words** of input capacity. The prompt itself consumes ~200 tokens. The expected JSON response consumes ~150 tokens. So safe input is approximately **24,000 words**.

**Testing methodology I recommend:**

```python
# Add to extract_text.py
MAX_WORDS_FOR_LLM = 6000  # Conservative: well under the limit

def test_document_length(path: Path) -> dict:
    """Return word count and truncation recommendation."""
    text = extract_text(path)
    words = len(text.split())
    return {
        "word_count": words,
        "safe_for_llm": words <= MAX_WORDS_FOR_LLLM,
        "recommendation": "truncate" if words > MAX_WORDS_FOR_LLM else "process",
        "truncated_text": truncate_for_llm(text, MAX_WORDS_FOR_LLM) if words > MAX_WORDS_FOR_LLM else text,
    }

def truncate_for_llm(text: str, max_words: int) -> str:
    """Executive summary pattern: first 60% + last 20% + ellipsis."""
    words = text.split()
    if len(words) <= max_words:
        return text
    first_part = int(max_words * 0.6)
    last_part = int(max_words * 0.2)
    return " ".join(words[:first_part]) + "\n\n...[truncated: middle section omitted]...\n\n" + " ".join(words[-last_part:])
```

**Are PDF expectations realistic?**

| PDF Type | Typical Word Count | LLM Feasible? | Strategy |
|----------|-------------------|---------------|----------|
| 1-page invoice | 100–300 | Yes | Full text |
| 5-page report | 2,000–3,000 | Yes | Full text |
| 20-page research paper | 8,000–12,000 | Borderline | Truncate or chunk |
| 100-page manual | 40,000–80,000 | No | Extract TOC, process sections |
| 500-page book | 200,000+ | No | Chapter-by-chapter, or skip |

**Recommendation:**
- Add a `word_count` check to the pipeline
- Documents under 6,000 words: process in full
- Documents 6,000–15,000 words: executive summary truncation
- Documents over 15,000 words: chunk into sections, process each separately, merge sidecars

---

## 3. Project Specifics: The exFAT/FAT32 Issue

**Observation:** The automation workspace lives on an external drive mounted at `/run/media/mpc/Expansion/`. The filesystem is **exFAT**.

**Why this matters:**

| Feature | ext4 (Linux native) | exFAT |
|---------|---------------------|-------|
| Symlinks | Yes | No |
| Journaling | Yes (metadata) | No |
| File permissions | Full POSIX | Single read-only bit |
| Max filename | 255 bytes | 255 characters |
| Max path | No practical limit | 32,760 characters |
| Case sensitivity | Yes | No |
| `os.replace()` atomicity | Yes | Partial (no journaling) |

**Impact on this project:**

1. **Cannot create virtual environments on exFAT** — venv requires symlinks. This is why I recommended creating the venv on the local SSD.
2. **No file locking primitives** — exFAT doesn't support `flock()` or `lockf()` reliably across all kernel versions.
3. **Atomic writes are not guaranteed** — `os.replace()` works, but a power loss during the write can leave a corrupt file.
4. **Case-insensitive filenames** — `Report.md` and `report.md` are the same file. This could cause issues if AI-generated titles produce collisions.

**The FAT32 confusion:** You mentioned "FAT 232" — there is no such filesystem. You may be thinking of:
- **FAT32**: Older Windows filesystem, 4GB file size limit, 255-character filenames
- **exFAT**: Modern replacement for FAT32, no 4GB limit, but still no journaling
- **NTFS**: Windows native, journaling, permissions, but Linux write support is slower
- **ext4**: Linux native, journaling, best performance and reliability

**Recommendation:**
- Accept exFAT for the project workspace (it works, and the drive is external)
- Keep state files (`processed-files.json`) backed up to the local SSD
- Git-commit the project daily (state, config, sidecars)
- Consider reformatting the external drive to ext4 if it will be permanently attached to Linux

---

## 4. Development Timelines: Lessons from AI Integration

### Original Estimates vs. Reality

| Task | Original Estimate | Actual Time | Factor |
|------|-------------------|-------------|--------|
| Basic logging script | 1 hour | 1 hour | 1× |
| Ollama status check | 30 min | 30 min | 1× |
| Document scanner | 2 hours | 2 hours | 1× |
| Single-file processor | 4 hours | 6 hours | 1.5× |
| JSON validation | 1 hour | 3 hours | 3× |
| Sidecar generation | 2 hours | 4 hours | 2× |
| Confidence normalization | 1 hour | 2 hours | 2× |
| Vault routing | 2 hours | 3 hours | 1.5× |
| Daily report generator | 1 hour | 1.5 hours | 1.5× |
| **Total** | **14.5 hours** | **24 hours** | **1.65×** |

### Why AI Integration Takes More Iterations

The 1.65× factor is entirely due to **model behavior unpredictability**:

1. **Prompt engineering is empirical, not deductive** — You can't reason your way to the right prompt. You have to test, observe, adjust, test again.
2. **Temperature and sampling** — Even identical prompts produce slightly different outputs. "Confidence: 0.8" on run 1 might be "confidence: 0.75" on run 2.
3. **Context window limits** — You only discover truncation issues when you test with a real 10,000-word PDF.
4. **JSON edge cases** — The model might wrap JSON in Markdown fences, add trailing commas, or omit required fields. Each case needs a specific validator fix.
5. **Rate limiting and timeouts** — Ollama on CPU can take 30+ seconds for a complex prompt. Timeouts need tuning.
6. **Fallback model behavior** — `mistral` and `qwen2.5-coder:7b` interpret the same prompt differently. The fallback logic needs separate validation rules.

### Revised Estimation Rule

For any task involving LLM integration, apply:

> **Time = Base_Complexity × 2.0**

And for any task involving prompt engineering:

> **Time = Base_Complexity × 3.0**

This is not pessimism — it is realism. The "six passes instead of two weeks" pattern you observed is normal. Each pass discovers a new edge case in model behavior.

---

## 5. Efficiency & Optimization: Quick Wins

### Immediate Wins (Today, < 30 minutes each)

1. **Add word count guard to pipeline** — Prevents Ollama context overflow. One `if len(text.split()) > 6000:` check.
2. **Create `requirements.txt`** — `pip freeze --user > requirements.txt`. 30 seconds. Saves hours later.
3. **Add `--quiet` flag to network check** — For cron use, suppresses verbose nmcli output. One argument parser addition.
4. **Add `last-run.timestamp` heartbeat** — `touch state/last-run.timestamp` at end of runner. Monitor with `find state/last-run.timestamp -mtime +1`.
5. **Truncate long titles** — AI sometimes returns 100+ character titles. Cap at 80 chars in `write_sidecar()`.

### This Week (1–2 hours each)

6. **Implement atomic state writes** — Write to `processed-files.json.tmp`, then `os.replace()`. Prevents corruption.
7. **Add file locking with `filelock`** — `pip install filelock`, wrap state access in `with FileLock("state.lock"):`.
8. **Add retry with exponential backoff** — Use `tenacity` library for Ollama API calls. Handles transient failures.
9. **Implement schema v2 (YAML frontmatter)** — Obsidian-native, Dataview-compatible.
10. **Add encoding detection (`chardet`)** — Prevents silent character loss in legacy documents.

### This Month (4–8 hours each)

11. **Migrate state to SQLite** — Replaces JSON with ACID transactions. Scales to 100,000+ entries.
12. **Add circuit breaker for Ollama** — If Ollama fails 3 times in a row, pause the pipeline for 10 minutes. Prevents hammering a dead service.
13. **Implement observer pattern for pipeline events** — Use `blinker` signals. Separate logging, routing, and notification from the core processing logic.
14. **Add chunking for large documents** — Split 20,000-word PDFs into 5,000-word chunks, process each, merge sidecars.
15. **Write unit tests with pytest** — Start with `test_extract_text.py`, `test_validate_metadata.py`, `test_route_to_vault.py`.

---

## 6. Technical Hurdles: Pip Packages & Dependencies

### Current State

**Installed packages (user site):**
- `pypdf==6.12.1` — PDF text extraction
- `python-docx==1.2.0` — Word document extraction
- `markdownify==1.2.2` — HTML to Markdown conversion
- `filelock==3.29.0` — File locking (just installed)
- `tenacity==9.1.4` — Retry/circuit breaker patterns (just installed)
- `pydantic==2.13.4` — Schema validation (just installed)
- `blinker==1.9.0` — Observer pattern / signals (just installed)
- `structlog==25.5.0` — Structured logging (just installed)

### The exFAT Problem (Revisited)

Cannot create virtual environments on exFAT because venv requires symlinks. Solution:

```bash
# Create venv on local SSD (ext4)
mkdir -p ~/.local/share/automation-venv
python3 -m venv ~/.local/share/automation-venv

# Activate and install
source ~/.local/share/automation-venv/bin/activate
pip install -r requirements.txt

# Update runner scripts
VENV_PYTHON="/home/mpc/.local/share/automation-venv/bin/python3"
"${VENV_PYTHON}" scripts/ingestion/process_one_file.py "$@"
```

### Dependency Version Pinning

The current `pip install --user` approach installs the *latest* version of each package. When `pypdf` releases version 7.0 with breaking API changes, the pipeline breaks.

**Fix (already recommended, not yet implemented):**

```bash
# Create requirements.txt with pinned versions
pip freeze --user > requirements.txt

# Result looks like:
# pypdf==6.12.1
# python-docx==1.2.0
# markdownify==1.2.2
# filelock==3.29.0
# tenacity==9.1.4
# pydantic==2.13.4
# blinker==1.9.0
# structlog==25.5.0
```

This makes the environment reproducible. Any Fedora machine with Python 3.14 can run:

```bash
python3 -m venv ~/.local/share/automation-venv
source ~/.local/share/automation-venv/bin/activate
pip install -r requirements.txt
```

And get the exact same environment.

---

## 7. Risk Assessment: Additional Concerns

### High-Risk Issues

1. **State file corruption on concurrent access**
   - Probability: High (cron + manual runs)
   - Impact: Pipeline loses track of processed files, reprocesses or skips
   - Mitigation: File locking + atomic writes + SQLite migration

2. **Ollama context overflow on large documents**
   - Probability: Medium (depends on document mix)
   - Impact: Silent truncation or model error
   - Mitigation: Word count guard + truncation + chunking

3. **exFAT drive failure or corruption**
   - Probability: Medium (no journaling, external drive)
   - Impact: Loss of state, sidecars, and logs
   - Mitigation: Git commits + SSD backup + daily rsync

### Medium-Risk Issues

4. **Obsidian search pollution**
   - Probability: Certain (scripts are inside vault)
   - Impact: Cluttered search, graph noise
   - Mitigation: Add exclusions immediately; plan migration out of vault

5. **Model output quality degradation over time**
   - Probability: Medium (temperature, prompt drift)
   - Impact: Inconsistent tagging, unreliable routing
   - Mitigation: Prompt version tracking + output quality metrics + periodic re-testing

6. **Dependency rot**
   - Probability: High over 6+ months
   - Impact: Scripts break on new Python versions or package updates
   - Mitigation: Pinned requirements + venv + unit tests

### Low-Risk Issues

7. **File naming collisions**
   - `invoice.pdf` and `invoice.docx` both produce `invoice.ai.md`
   - Mitigation: Hash-based naming or folder-scoped naming

8. **Encoding issues in legacy files**
   - Windows-1252, Latin-1, Big5 files produce garbled text
   - Mitigation: `chardet` encoding detection

---

## 8. Action Plan: Prioritized To-Do List

### P0 — Critical (Do Today)

1. **Add Obsidian exclusions for automation folders**
   - Path: Options → Files and links → Excluded files
   - Patterns: `automation-scripts/scripts/*`, `automation-scripts/logs/*`, `automation-scripts/data/*`, `automation-scripts/state/*`
   - Time: 5 minutes

2. **Create `requirements.txt` with pinned versions**
   - Command: `pip freeze --user > requirements.txt`
   - Time: 30 seconds

3. **Add word count guard to `process_one_file.py`**
   - `MAX_WORDS = 6000`, truncate if exceeded
   - Time: 15 minutes

4. **Implement atomic state file writes**
   - Write to `processed-files.json.tmp`, then `os.replace()`
   - Time: 15 minutes

### P1 — High Priority (This Week)

5. **Add file locking with `filelock`**
   - Wrap `load_state()` and `save_state()` in `with FileLock("state.lock"):`
   - Time: 30 minutes

6. **Add retry logic with `tenacity`**
   - Wrap Ollama API calls: `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))`
   - Time: 30 minutes

7. **Create virtual environment on local SSD**
   - `python3 -m venv ~/.local/share/automation-venv`
   - Install pinned dependencies
   - Update runner scripts to use venv Python
   - Time: 30 minutes

8. **Implement schema v2 (YAML frontmatter)**
   - Replace JSON-in-frontmatter with native YAML
   - Add `schema_version`, `ai_metadata`, `source.sha256`, `quality` blocks
   - Time: 2 hours

9. **Add `last-run.timestamp` heartbeat**
   - Touch file at end of each runner script
   - Check age in morning health check
   - Time: 15 minutes

### P2 — Medium Priority (Next Two Weeks)

10. **Add circuit breaker for Ollama**
    - Use `tenacity` or custom decorator: if 3 failures in 60s, pause 10 minutes
    - Prevents hammering a dead or overloaded service
    - Time: 2 hours

11. **Implement observer pattern with `blinker`**
    - Signals: `file_processed`, `sidecar_written`, `ollama_failed`, `low_confidence`
    - Separate handlers: logger, router, notifier, archiver
    - Time: 3 hours

12. **Add anti-corruption layer for LLM output**
    - `Pydantic` model for validation: `class MetadataOutput(BaseModel)`
    - Strict type checking, min/max constraints, regex patterns for tags
    - Time: 2 hours

13. **Add encoding detection with `chardet`**
    - Detect encoding before reading text files
    - Log when replacement characters are used
    - Time: 1 hour

14. **Implement chunking for large documents**
    - Split > 15,000-word documents into sections
    - Process each section, merge sidecars
    - Time: 4 hours

### P3 — Longer Term (This Month)

15. **Migrate state from JSON to SQLite**
    - `state.db` with tables: `files`, `processing_runs`, `errors`
    - ACID transactions, concurrent access safe
    - Time: 4 hours

16. **Write unit tests with pytest**
    - `test_extract_text.py`: Test .txt, .pdf, .docx extraction
    - `test_validate_metadata.py`: Test JSON schema validation
    - `test_route_to_vault.py`: Test category routing logic
    - Time: 4 hours

17. **Add desktop notifications for failures**
    - `notify-send "Automation Failed" "Daily ingest encountered 3 errors"`
    - Time: 30 minutes

18. **Implement collision-safe sidecar naming**
    - Use truncated hash: `invoice-a3f7d2.ai.md`
    - Time: 1 hour

---

## 9. Architectural Patterns: Circuit Breaker, Observer, Anti-Corruption

You specifically asked about incorporating these patterns. Here's how they fit:

### Circuit Breaker for Ollama

**Problem:** If Ollama crashes or the model is unloaded, the pipeline retries indefinitely, wasting time and generating errors.

**Solution:** Use `tenacity` to implement a circuit breaker.

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class OllamaUnavailableError(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(OllamaUnavailableError),
    reraise=True,
)
def call_ollama(prompt: str, model: str) -> str:
    response = requests.post(f"{OLLAMA_HOST}/api/generate", json={...})
    if response.status_code == 503:
        raise OllamaUnavailableError("Ollama service unavailable")
    return response.json()["response"]
```

**Extension:** After 3 consecutive failures, write a `circuit-open` flag to state. The pipeline checks this flag before attempting Ollama calls. A separate health check script resets the flag when Ollama recovers.

### Observer Pattern with `blinker`

**Problem:** The current pipeline mixes logging, routing, archiving, and reporting logic inside `process_one_file.py`. Changing one behavior requires editing the core processor.

**Solution:** Use `blinker` signals to decouple.

```python
from blinker import signal

# Define signals
file_queued = signal("file-queued")
file_processed = signal("file-processed")
sidecar_written = signal("sidecar-written")
low_confidence_detected = signal("low-confidence-detected")
ollama_failed = signal("ollama-failed")

# In process_one_file.py, emit signals instead of calling directly
file_processed.send(self, source_path=path, metadata=metadata)
sidecar_written.send(self, sidecar_path=sidecar_path, metadata=metadata)

# In separate modules, connect handlers
@file_processed.connect
def log_processing(sender, **kwargs):
    write_log(f"Processed: {kwargs['source_path']}")

@sidecar_written.connect
def route_to_vault_handler(sender, **kwargs):
    route_to_vault(kwargs['sidecar_path'])

@low_confidence_detected.connect
def quarantine_for_review(sender, **kwargs):
    move_to_review(kwargs['sidecar_path'])
```

**Benefits:**
- Add new behaviors (e.g., desktop notifications) without touching `process_one_file.py`
- Remove behaviors by disconnecting handlers
- Test handlers independently

### Anti-Corruption Layer for LLM Output

**Problem:** The model returns JSON that may be malformed, have wrong types, or contain nonsense values. The current validator checks field existence but not *quality*.

**Solution:** Use `pydantic` for strict schema validation + heuristics for quality.

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class MetadataOutput(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    summary: str = Field(..., min_length=10, max_length=500)
    tags: list[str] = Field(..., min_items=1, max_items=10)
    backlinks: list[str] = Field(default_factory=list)
    value: Literal["throwaway", "useful", "permanent"]
    confidence: float = Field(..., ge=0.0, le=1.0)

    @validator("title")
    def title_not_a_sentence(cls, v):
        if len(v.split()) > 15:
            raise ValueError("Title must not be a full sentence")
        return v

    @validator("summary")
    def summary_differs_from_input(cls, v, values):
        # Heuristic: summary should not just echo the input
        if v == values.get("_original_text", "")[:len(v)]:
            raise ValueError("Summary appears to echo input text")
        return v

    @validator("tags")
    def tags_lowercase_kebab(cls, v):
        for tag in v:
            if not re.match(r"^[a-z0-9-]+$", tag):
                raise ValueError(f"Tag must be kebab-case: {tag}")
        return v
```

**Benefits:**
- Type safety at runtime
- Clear error messages when validation fails
- Easy to extend with new rules
- Self-documenting schema

### Putting It Together: The Resilient Pipeline

```
Incoming File
    |
    v
[file_queued signal] --> Logger, Queue Monitor
    |
    v
extract_text()
    |
    v
[if word_count > 6000] --> truncate_for_llm()
    |
    v
[Circuit Breaker: Is Ollama healthy?]
    |-- NO --> [ollama_failed signal] --> Log, Notify, Pause pipeline
    |-- YES --> call_ollama()
    |
    v
[Pydantic Validator: Anti-Corruption Layer]
    |-- INVALID --> [ollama_failed signal] --> Quarantine for review
    |-- VALID --> MetadataOutput object
    |
    v
write_sidecar()
    |
    v
[sidecar_written signal] --> Router, Archiver, Reporter
    |
    v
[normalize_confidence] --> Sigmoid/Softmax
    |
    v
[low_confidence_detected signal] --> Quarantine to review/
    |
    v
[file_processed signal] --> Update state, Write log
```

This architecture is:
- **Resilient:** Circuit breaker prevents cascading failures
- **Observable:** Every event is a signal; you can attach monitors
- **Clean:** LLM output is sanitized before it touches your vault
- **Extensible:** New behaviors are new signal handlers, not core changes

---

## 10. Summary

| Metric | Current State | Target State | Timeline |
|--------|--------------|--------------|----------|
| Daily throughput | 50 files (conservative) | 200–400 files | After review queue tuning |
| PDF handling | No length checks | Word count guards + chunking | This week |
| State storage | JSON file (corruptible) | SQLite (ACID) | This month |
| Concurrency | None | File locking + atomic writes | This week |
| LLM resilience | Basic retry | Circuit breaker + observer | Next two weeks |
| Schema | JSON-in-YAML (v1) | Native YAML (v2) + Pydantic | This week |
| Environment | System Python + `--user` | Venv on SSD + pinned deps | This week |
| Testing | None | pytest unit tests | This month |

**The single most important action:** Install the `filelock` and `tenacity` libraries (done today), add file locking to state access, and create `requirements.txt`. These three tasks take 30 minutes and eliminate the two highest-risk failure modes.
