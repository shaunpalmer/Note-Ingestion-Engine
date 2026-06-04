# Senior Developer Review: Obsidian Vault Automation Architecture

**Reviewer:** Senior Developer (Kilo)  
**Reviewee:** Junior Developer (Project Owner)  
**Date:** 2026-05-26  
**Project:** Local Automation Stack for Obsidian Vault + Ollama  
**Current Codebase:** 20 scripts, ~2,000 lines, system Python 3.14.4, exFAT external drive

---

## 1. Project Architecture Analysis

### 1.1 The Critical Finding: Automation Scripts Live *Inside* the Vault

**Observation:** The project root is at:
```
/home/mpc/Documents/LinuxBox-Vault/automation-scripts/
```

This means `automation-scripts/` is a subfolder of the Obsidian vault itself. Obsidian's search indexes every Markdown file, text file, and script it can find. Your `.ai.md` sidecars, logs, Python scripts, and CSV registries are all visible to Obsidian's search graph.

**Why this matters:**
- Search results polluted with `register-scripts.py`, `update-storage-table.py`, log files
- Graph view shows automation metadata as "notes" — clutters the knowledge graph
- Dataview queries may accidentally match `script-registry.csv` if you ever import CSVs
- The `.ai.md` sidecars inside `sidecars/` are indexed, which is *intentional* and good
- But the *source* scripts, logs, and state files should never appear in search

### 1.2 Recommended Separation Strategy

**Option A: Move Automation Outside the Vault (Preferred)**
```
~/Projects/automation-stack/          # Scripts, config, runners
    ├── scripts/
    ├── config/
    ├── logs/
    ├── state/
    └── sidecars/                     # Only this folder publishes to vault

~/Documents/LinuxBox-Vault/           # Pure Obsidian territory
    ├── inbox/
    ├── agency/
    ├── programming/
    └── ...
```

**Pros:** Clean separation, no search pollution, vault is purely knowledge  
**Cons:** Requires updating `config/paths.conf`, two locations to back up

**Option B: Keep Inside Vault, Exclude from Search**
Add to Obsidian's **Options → Files and links → Excluded files**:
```
automation-scripts/scripts/
automation-scripts/logs/
automation-scripts/data/
automation-scripts/state/
automation-scripts/config/
```

**Pros:** Single location, simpler backup  
**Cons:** Relies on Obsidian's exclusion (not portable to other tools), easy to misconfigure

**My recommendation:** Start with Option B today (add exclusions), plan migration to Option A within 2 weeks.

### 1.3 How Scripts Should Interact with Vault Data

**Current approach (correct):** Scripts use absolute paths from `config/paths.conf`. They *copy* sidecars into the vault, never *move* originals. This is the right safety model.

**What needs to change:**

1. **Sidecar naming collision:** If you have `invoice.pdf` and `invoice.docx`, both produce `invoice.ai.md`. The second one overwrites the first.
   - **Fix:** Hash-based naming: `invoice-a3f7d2.ai.md` or folder-scoped naming: `docs/invoice.ai.md`

2. **Cross-device copies:** The vault is on your local SSD (`~/Documents/`). The automation workspace is on an external exFAT drive. Every `route_to_vault.py` copy crosses filesystem boundaries.
   - **Fix:** Accept the copy cost. It's safer than symlinks across drives. Log the operation.

3. **Vault folder structure created by automation:** The `agency/`, `marketing/`, `data/` folders were created by a script. If Obsidian's graph already has notes, moving them into these folders changes their graph position.
   - **Fix:** Create the folder structure once, then let the routing script populate it. Don't recreate folders on every run.

---

## 2. Knowledge Gaps and Technical Constraints

### 2.1 Six Critical Questions You Should Be Asking

**Q1: "What happens when two scripts run at the same time?"**

The `processed-files.json` state file is read and written by multiple scripts. There is no file locking. If cron fires `run-daily-ingest.sh` while you're manually running `process_one_file.py`, the state file can corrupt.

**Answer needed:** Implement atomic writes (write to temp file, then `os.replace()`). Better yet, use SQLite for state. JSON on disk is fine for 100 entries, dangerous for 10,000.

**Q2: "What's my recovery plan if the exFAT drive corrupts?"**

Your entire automation project, all sidecars, all logs, and the state file live on an external exFAT drive. exFAT has no journaling. A power loss during a write can corrupt `processed-files.json`, making the pipeline lose track of what's been processed.

**Answer needed:** 
- Git-commit state and sidecars daily (they're text, they compress well)
- Keep a secondary state copy on the local SSD
- Consider `rsync --checksum` from exFAT to local SSD as a nightly backup

**Q3: "How does Ollama handle a 50-page PDF with 20,000 words?"**

The prompt builder sends the *entire extracted text* to Ollama. `qwen2.5-coder:7b` has a 32K context window. A 20,000-word document is ~27,000 tokens. This leaves ~5,000 tokens for the prompt and response — tight, but workable.

But what about a 200-page PDF? Or 50 files × 5,000 words each = 250,000 words in a single morning batch?

**Answer needed:**
- Add a `word_count` check before sending to Ollama
- If text > 6,000 words, extract only the first 2,000 + last 1,000 (executive summary pattern)
- Or chunk the document and process sections separately

**Q4: "What encoding are these documents in?"**

The `extract_text.py` fallback uses `utf-8` with `errors="replace"`. But legacy Windows files may be `cp1252`, `latin-1`, or even `big5`. The `replace` error handler silently destroys characters.

**Answer needed:**
- Use `chardet` or `charset-normalizer` to detect encoding before reading
- Log when replacement happens: "WARNING: 47 characters replaced in file X"
- For `.docx`, `python-docx` handles encoding internally — that's fine

**Q5: "What happens when the model returns garbage?"**

The current validator checks: JSON parseable, required fields exist, value in enum, confidence in range. It does NOT check:
- Whether `summary` is actually a summary or just the input text echoed back
- Whether `tags` are meaningful or random words
- Whether `title` is a title or a full sentence

**Answer needed:**
- Add heuristics: title should be < 100 chars, summary should differ from input
- Add a `review/` quarantine for borderline outputs
- Track "model hallucination rate" in the daily report

**Q6: "How do I know the pipeline actually ran this morning?"**

Cron is silent. If `run-daily-ingest.sh` fails at 6:05 AM, you won't know until you check logs.

**Answer needed:**
- Add a "heartbeat" mechanism: the script touches a `last-run.timestamp` file
- If the timestamp is older than 25 hours, the morning check runner should flag it
- Consider a simple desktop notification on Fedora: `notify-send "Automation" "Daily ingest failed"`

### 2.2 File Path Handling: The Long Path Problem

**Current reality:**
```
/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/sidecars/test-note-01.ai.md
```

This is 143 characters. Add a deeply nested document source path and you easily exceed 255 characters for some tools.

**Issues:**
- exFAT technically supports 32,760 character paths, but individual filenames are limited to 255 characters
- Obsidian on Windows (if you ever sync there) has a 260-character path limit unless Long Path Awareness is enabled
- Python's `open()` handles long paths fine, but shell scripts and some Obsidian plugins may not

**Recommendations:**
1. Keep automation paths flat: `sidecars/`, `state/`, `logs/` — no deep nesting
2. For sidecar naming, use truncated hashes rather than full paths: `invoice-a3f7d2.ai.md`
3. Never embed the full source path in a filename — store it in frontmatter instead
4. If paths must be long, use `pathlib.Path` everywhere (you already do this — good)

### 2.3 Python Package Management: The Missing Foundation

**Current state:**
- System Python 3.14.4 (Fedora, very new)
- Packages installed with `pip install --user`: `pypdf`, `python-docx`, `markdownify`
- No `requirements.txt`
- No virtual environment (exFAT doesn't support symlinks)
- No dependency pinning

**The problem:** In six months, you rebuild this machine. You run the scripts. `python-docx` has moved to 2.0 with breaking API changes. Everything breaks. You have no record of what worked.

**The fix (do this now):**

Step 1: Create `requirements.txt`
```bash
cd /run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts
python3 -m pip freeze --user > requirements.txt
```

Step 2: Create a local venv on the internal SSD (not exFAT)
```bash
mkdir -p ~/.local/share/automation-venv
python3 -m venv ~/.local/share/automation-venv
source ~/.local/share/automation-venv/bin/activate
pip install -r requirements.txt
```

Step 3: Update runner scripts to use the venv
```bash
#!/usr/bin/env bash
VENV_PYTHON="/home/mpc/.local/share/automation-venv/bin/python3"
"${VENV_PYTHON}" scripts/ingestion/process_one_file.py "$@"
```

Step 4: Pin versions in `requirements.txt`
```
pypdf==6.12.1
python-docx==1.2.0
markdownify==1.2.2
chardet==5.2.0
```

**Why this matters:** Reproducibility. If your SSD dies and you restore from backup, `pip install -r requirements.txt` gives you the exact same environment.

---

## 3. Refined Automation Strategy

### 3.1 The "Publish, Don't Pollute" Workflow

**Principle:** The automation workspace is a factory. The vault is a storefront. Customers (you) only see finished products.

```
[External Drive: automation-scripts/]
    |
    |-- scripts/          (factory machinery — never in vault)
    |-- logs/             (factory records — never in vault)
    |-- state/            (factory inventory — never in vault)
    |-- sidecars/         (finished products — PUBLISH to vault)
    |-- imported-text-files/  (raw materials)
    |
    v
[Local SSD: Documents/LinuxBox-Vault/]
    |
    |-- inbox/            (new notes from automation)
    |-- agency/           (routed by AI tags)
    |-- programming/      (routed by AI tags)
    |-- ...               (routed by AI tags)
    |-- archive/          (low-value, kept but hidden)
```

**How to keep the factory invisible:**
1. Add automation exclusions to Obsidian's settings (Option B)
2. Or move the factory to `~/Projects/automation-stack/` (Option A)
3. Only `sidecars/*.ai.md` and `reports/*.md` cross the boundary
4. Original `.pdf` and `.docx` files are copied (not moved) into vault categories

### 3.2 Python Environment: Portable and Clean

**The target architecture:**

```
~/Projects/automation-stack/
|-- .venv/                    # Virtual environment on local SSD
|-- requirements.txt          # Pinned dependencies
|-- requirements-dev.txt      # Testing, linting, typing
|-- pyproject.toml            # Modern Python project metadata
|-- scripts/
|-- config/
|-- tests/                    # Unit tests for extractors, validators
```

**Why `pyproject.toml`:**
Modern Python uses `pyproject.toml` (PEP 518) instead of `setup.py`. It declares:
- Build system requirements
- Project metadata (name, version, description)
- Dependencies
- Entry points (CLI commands)

Even for a "script collection," having `pyproject.toml` makes the project installable:
```bash
pip install -e .
# Now you can run:
obsidian-ingest --dry-run
obsidian-warmup
obsidian-report
```

**Immediate action:**
1. Create `requirements.txt` today
2. Create venv on local SSD this week
3. Write `pyproject.toml` next week
4. Add basic tests (pytest) within two weeks

---

## 4. Metadata Schema Review and Improvements

### 4.1 Current Schema (As Implemented)

```json
{
  "source_file": "/original/path/example-file.pdf",
  "source_type": "pdf",
  "processed_at": "2026-05-26T03:37:04.422125",
  "model": "qwen2.5-coder:7b",
  "status": "ai-generated-needs-review",
  "value": "useful",
  "confidence": 0.9,
  "tags": ["backlinks", "local ai", "tagging notes"],
  "backlinks": []
}
```

**Problems with this schema:**

1. **JSON inside YAML frontmatter:** Obsidian expects *YAML* frontmatter, not JSON. Dataview and metadata plugins parse YAML natively. JSON inside `---` blocks is not valid YAML and may break Dataview queries.

2. **No schema version:** When you change the schema in three months, old sidecars become incompatible.

3. **`value` is vague:** Is it a noun? An adjective? `value_tier` or `importance` would be clearer.

4. **No performance metrics:** You don't know if a file took 5 seconds or 5 minutes to process.

5. **No integrity hash:** If the sidecar is edited, you can't verify it matches the original AI output.

6. **No human review tracking:** `status: "ai-generated-needs-review"` is the starting state. There's no field for when it was reviewed or by whom.

### 4.2 Proposed Schema (v2)

```yaml
---
schema_version: "2.0"
ai_metadata:
  model: "qwen2.5-coder:7b"
  prompt_version: "1.0"
  processed_at: "2026-05-26T03:37:04+12:00"
  processing_time_ms: 2847
source:
  file: "/original/path/example-file.pdf"
  type: "pdf"
  size_bytes: 154320
  word_count: 1847
  sha256: "a3f7d2e1..."
output:
  title: "file migration and testing"
  summary: "Moved files from side rig, tested Tailscale..."
  tags:
    - tailscale
    - ai
    - local
  backlinks: []
  value_tier: "useful"
  confidence:
    raw: 0.85
    normalized: 0.91
    method: "sigmoid"
quality:
  status: "ai-generated-needs-review"
  reviewed_at: null
  reviewed_by: null
  review_notes: null
---
```

**Why this structure is better:**

| Change | Benefit |
|--------|---------|
| `schema_version` | Future-proof. Scripts can read v1 and v2 sidecars differently |
| `ai_metadata` block | Separates AI-provenance from content. Makes it clear what the machine did |
| `source.sha256` | Verify the original hasn't changed since processing |
| `source.word_count` | Context size tracking. Helps debug Ollama timeouts |
| `processing_time_ms` | Performance monitoring. Identify slow files |
| `output.confidence.raw` + `.normalized` | Preserves original model output while using the calibrated score |
| `quality` block | Human review workflow. Track who reviewed what and when |
| YAML instead of JSON | Native Obsidian compatibility. Dataview queries work |

### 4.3 Sidecar Template (v2)

```markdown
---
schema_version: "2.0"
ai_metadata:
  model: qwen2.5-coder:7b
  prompt_version: "1.0"
  processed_at: 2026-05-26T03:37:04+12:00
  processing_time_ms: 2847
source:
  file: /original/path/example-file.pdf
  type: pdf
  size_bytes: 154320
  word_count: 1847
  sha256: a3f7d2e1...
output:
  title: file migration and testing
  summary: Moved files from side rig, tested Tailscale...
  tags:
    - tailscale
    - ai
    - local
  backlinks: []
  value_tier: useful
  confidence:
    raw: 0.85
    normalized: 0.91
    method: sigmoid
quality:
  status: ai-generated-needs-review
  reviewed_at:
  reviewed_by:
  review_notes:
---

# file migration and testing

## Summary

Moved files from side rig, tested Tailscale, planning for local AI tag notes and create backlinks

## Why it matters

This note appears useful for active work.

## Source link

[Open original file](file:///original/path/example-file.pdf)

## Review Checklist

- [ ] Tags are accurate and useful
- [ ] Backlinks are meaningful
- [ ] Value tier is appropriate
- [ ] Summary captures the essence
```

**Benefits of the checklist:**
- Makes review a concrete task, not a vague "look at this"
- Each checked box is a commit point (you can stop and resume)
- Unchecked boxes signal to the automation: "don't archive this yet"

---

## 5. Immediate Action Items (Priority Order)

### This Morning (5 minutes)
1. [ ] Add automation exclusions to Obsidian: **Options → Files and links → Excluded files**
   - Pattern: `automation-scripts/scripts/*`, `automation-scripts/logs/*`, `automation-scripts/data/*`

### This Week (1 hour)
2. [ ] Create `requirements.txt` with pinned versions
3. [ ] Create virtual environment on local SSD (`~/.local/share/automation-venv/`)
4. [ ] Update `run-daily-ingest.sh` to activate venv before running Python scripts
5. [ ] Add atomic file writes to `save_state()` (write temp, then `os.replace()`)

### Next Two Weeks (4 hours)
6. [ ] Implement schema v2 in `process_one_file.py`
7. [ ] Add word count guard before sending to Ollama (> 6,000 words → truncate)
8. [ ] Add encoding detection (`chardet`) to `extract_text.py`
9. [ ] Add `last-run.timestamp` heartbeat to runner scripts
10. [ ] Write 3 unit tests: `test_extract_text.py`, `test_validate_metadata.py`, `test_route_to_vault.py`

### This Month (8 hours)
11. [ ] Migrate state from JSON to SQLite (`state.db`)
12. [ ] Add collision-safe sidecar naming (hash suffix or folder scoping)
13. [ ] Implement chunking for large documents (> 8,000 words)
14. [ ] Add desktop notifications for failures (`notify-send`)
15. [ ] Write `pyproject.toml` and make the project pip-installable

---

## 6. Mentorship Closing Thoughts

**What you've done well:**
- Dry-run by default. This is the #1 safety practice for automation.
- Never modify originals. Copy + sidecar is the correct pattern.
- Absolute paths in config. No guessing where things live.
- SHA256 deduplication. Filename-based tracking would have failed on renames.
- Single-responsibility scripts. Each file does one thing. This is maintainable.

**What needs attention:**
- The scripts are inside the vault. Fix the search pollution.
- No tests. You can't refactor safely without tests.
- No dependency tracking. `requirements.txt` is a 30-second task that saves hours later.
- JSON frontmatter. Obsidian speaks YAML. Match the host's language.
- No concurrency protection. State corruption is a matter of time, not if.

**The mindset shift:**

Right now, you're building a "script that processes files." That's fine for week one. By week four, you need to be building a "system that processes files, recovers from errors, reports its own health, and can be understood by someone else six months from now."

That means:
- Tests, not just logs
- Schema versions, not just "it works today"
- Atomic operations, not "probably fine"
- Documentation, not "I'll remember"

The code you wrote is good. The architecture is sound. The gaps are in *discipline*: dependency management, testing, error recovery, and schema evolution. Those are the things that separate a working prototype from a production system.

**One final rule:**

> If the automation breaks and you're not there to fix it, it should fail *noisily* and *safely*.
>
> Noisily: logs, reports, notifications.  
> Safely: no data loss, no overwrites, no deletions.

Your current code fails safely (dry-run default, no deletions). Make it fail noisily too.
