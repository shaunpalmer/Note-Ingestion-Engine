# Code Evaluation: Existing Scripts vs New Scripts

## Methodology
Every script was read and scored on:
- **Single Responsibility** — does it do one thing?
- **DRY** — is code duplicated elsewhere?
- **Resilience** — does it handle failure gracefully?
- **Observability** — can you tell what happened from logs?
- **Safety** — is dry-run supported? Are originals protected?

---

## YOUR Original Scripts (Evaluation)

### 1. `scripts/log/write-log.sh` — Score: A
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Appends one log line |
| DRY | ✅ Used by other scripts, not duplicated |
| Resilience | ✅ Validates args, fails gracefully |
| Observability | ✅ Is the logging system itself |
| Safety | ✅ Append-only, never deletes |

**Verdict:** Keep as-is. This is your best script. Clean, focused, reliable.

### 2. `scripts/log/test-log.sh` — Score: A
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Tests the logger |
| DRY | ✅ Reuses write-log.sh |
| Resilience | ✅ Checks executable before running |
| Observability | ✅ Prints inspection command |
| Safety | ✅ Writes to log only |

**Verdict:** Keep as-is. Good smoke test pattern.

### 3. `scripts/network/check-network-status.sh` — Score: A-
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Read-only network checks |
| DRY | ✅ Has its own log_info/log_warn (acceptable for bash) |
| Resilience | ✅ Graceful when nmcli/ip missing |
| Observability | ✅ Comprehensive logging |
| Safety | ✅ Read-only, no changes |

**Minor issue:** Duplicates log formatting pattern from write-log.sh. Acceptable in bash.
**Verdict:** Keep as-is. Good read-only script pattern.

### 4. `scripts/obsidian/scan-obsidian-inbox.py` — Score: B+
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Scans inbox, reports types |
| DRY | ❌ `load_config()` and `write_log()` are copy-pasted from other scripts |
| Resilience | ✅ Handles missing inbox gracefully |
| Observability | ✅ Logs file counts and types |
| Safety | ✅ Read-only, --dry-run supported |

**Verdict:** Keep. Extract shared functions later.

### 5. `scripts/script-registration/register-scripts.py` — Score: B
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Scans scripts, writes CSV |
| DRY | ❌ `load_config()` and `get_project_root()` duplicated |
| Resilience | ✅ Handles missing dirs gracefully |
| Observability | ✅ Prints count |
| Safety | ✅ Read-only |

**Issue:** `purpose` field is always empty. The script tracks scripts but doesn't document them.
**Verdict:** Keep. Add purpose extraction from docstrings later.

### 6. `scripts/storage-table/update-storage-table.py` — Score: B+
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Scans folders, writes CSV |
| DRY | ❌ `load_config()` duplicated |
| Resilience | ✅ Handles missing paths gracefully |
| Observability | ✅ Dry-run shows sample records |
| Safety | ✅ --dry-run by default |

**Verdict:** Keep. Good CSV writer pattern.

### 7. `scripts/ingestion/extract_text.py` — Score: A
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Extracts text from files |
| DRY | ✅ No duplication |
| Resilience | ✅ Graceful on import failures, encoding issues |
| Observability | ✅ Silent on failure (returns "", appropriate for pipe) |
| Safety | ✅ Read-only |

**Verdict:** Keep as-is. This is your cleanest Python script.

---

## YOUR Scripts That Need Work

### 8. `scripts/ingestion/scan_documents.py` — Score: C+
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Scans for candidates |
| DRY | ❌ `load_config()`, `file_hash()`, `write_log()` all duplicated |
| Resilience | ⚠️ No file locking on state write |
| Observability | ✅ Good logging |
| Safety | ✅ --dry-run default, SHA256 dedup |

**Issues:**
- 25-line `load_config()` copy-pasted from 5 other files
- 10-line `file_hash()` also in `process_one_file.py`
- State write is not atomic (corrupts on crash)
- No file locking (concurrent access unsafe)

**Verdict:** Keep the logic. Extract shared functions.

### 9. `scripts/ingestion/process_one_file.py` — Score: C
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ❌ 319 lines: extracts text, calls Ollama, validates JSON, writes sidecar, updates state |
| DRY | ❌ `load_config()`, `file_hash()`, `write_log()`, `save_state()` all duplicated |
| Resilience | ❌ No retry, no circuit breaker, no timeout handling |
| Observability | ✅ Logs each step |
| Safety | ✅ --dry-run, doesn't modify originals |

**Issues:**
- Too many responsibilities in one file
- No retry on Ollama failure (single failure kills the batch)
- No circuit breaker (hammers Ollama if it's down)
- JSON-in-YAML frontmatter (not native YAML, Dataview can't parse)
- Sidecar naming collision: `invoice.pdf` and `invoice.docx` both become `invoice.ai.md`
- MAX_CHARS = 8000 is wrong metric (should be word count, not character count)

**Verdict:** This is your most important script and the one that needs the most work. Refactor, don't replace.

### 10. `scripts/ingestion/route_to_vault.py` — Score: C+
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Routes files based on tags |
| DRY | ❌ `load_config()`, `write_log()` duplicated |
| Resilience | ✅ Handles missing source files gracefully |
| Observability | ✅ Logs routing decisions |
| Safety | ✅ --dry-run, copies don't move |

**Issue:** `parse_frontmatter()` expects JSON inside `---` blocks. Your `process_one_file.py` writes JSON-in-YAML, so this is consistent. But it's not real YAML.

**Verdict:** Keep. Update if frontmatter format changes.

### 11. `scripts/ingestion/archive_low_value.py` — Score: C+
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Archives low-confidence files |
| DRY | ❌ `load_config()`, `write_log()`, `parse_frontmatter()` duplicated |
| Resilience | ✅ Handles missing files gracefully |
| Observability | ✅ Logs archive count |
| Safety | ✅ Copies, doesn't delete |

**Verdict:** Keep. Extract shared functions.

### 12. `scripts/ingestion/bulk_convert_to_markdown.py` — Score: B-
| Criterion | Verdict |
|-----------|---------|
| Single responsibility | ✅ Converts files to .md |
| DRY | ❌ `load_config()`, `write_log()` duplicated; `extract_text()` imported inline |
| Resilience | ✅ Handles extraction failures |
| Observability | ✅ Logs conversion count |
| Safety | ✅ --dry-run, doesn't modify originals |

**Issue:** `sys.path.insert(0, ...)` to import `extract_text` is a hack. Should use proper import.

**Verdict:** Keep. Fix the import hack.

---

## MY New Scripts (Evaluation — Brutal Honesty)

### 13–20. The v2 Modules (`models.py`, `signals.py`, `config.py`, `circuit_breaker.py`, `state_manager.py`, `ollama_client.py`, `handlers.py`, `process_one_file_v2.py`)

| Script | Good Parts | Bad Parts | Verdict |
|--------|-----------|-----------|---------|
| `models.py` | Pydantic schemas are robust | Over-engineered for current needs | **Archive** — extract the `MetadataOutput` validator, merge into `process_one_file.py` |
| `signals.py` | Observer pattern is clean | 12 signals for a 6-script project is overkill | **Delete** — premature abstraction |
| `config.py` | Centralizes `load_config()` | Introduces a module for a 25-line function | **Partially keep** — extract shared `load_config()` into a `lib/` module |
| `circuit_breaker.py` | Correct pattern | Custom class when `tenacity` handles this | **Archive** — use `@retry` decorator inline instead |
| `state_manager.py` | File locking + atomic writes | Introduces a class for what should be 3 functions | **Partially keep** — extract `atomic_save()` and `FileLock` into `lib/` |
| `ollama_client.py` | Separates API logic | Adds a class when a function would do | **Partially keep** — extract `call_ollama()` function |
| `handlers.py` | Decouples routing from processing | 140 lines of signal plumbing for 3 operations | **Delete** — call routing directly in `process_one_file.py` |
| `process_one_file_v2.py` | Uses all libraries | 300+ lines, parallel to existing file | **Delete** — refactor the original instead |

**My honest assessment of my own work:**

I created **8 new files** to solve problems that could have been solved by adding **~30 lines** to your existing scripts. The `filelock` and `tenacity` libraries are useful, but they don't need their own wrapper modules. A `@retry` decorator on `run_ollama()` and a `with FileLock(...)` around `save_state()` would have been sufficient.

The `pydantic` schema validation is genuinely better than your hand-rolled `validate_metadata()` — stricter, clearer errors, type-safe. That should be incorporated.

The YAML frontmatter in v2 is better than JSON-in-YAML. That should be incorporated.

Everything else — signals, handlers, separate client class — is architectural astronautics for a project that's still in the "make it work" phase.

---

## Consolidation Plan: The Honest List

### What to Keep (Your Best Work)
1. `write-log.sh` — as-is
2. `test-log.sh` — as-is
3. `check-network-status.sh` — as-is
4. `extract_text.py` — as-is
5. `scan-obsidian-inbox.py` — as-is (extract shared functions later)
6. `register-scripts.py` — as-is (add purpose extraction later)
7. `update-storage-table.py` — as-is (extract shared functions later)
8. `scan_documents.py` — keep logic (extract shared functions)
9. `route_to_vault.py` — keep logic (extract shared functions)
10. `archive_low_value.py` — keep logic (extract shared functions)
11. `bulk_convert_to_markdown.py` — keep logic (fix import)

### What to Refactor (Your Script That Needs Work)
12. `process_one_file.py` — This is the critical one. 319 lines, too many responsibilities.

### What to Incorporate (From My v2 Work)
- Pydantic `MetadataOutput` validation → replace `validate_metadata()` in `process_one_file.py`
- Native YAML frontmatter → replace JSON-in-YAML in `write_sidecar()`
- `tenacity @retry` → wrap `run_ollama()` in `process_one_file.py`
- `filelock` → wrap state save in `process_one_file.py` and `scan_documents.py`
- Atomic `os.replace()` → replace direct `json.dump()` in `save_state()`

### What to Delete (My Over-Engineering)
- `models.py` (extract the one `MetadataOutput` class, delete the rest)
- `signals.py`
- `circuit_breaker.py` (use `tenacity` directly)
- `handlers.py`
- `ollama_client.py` (extract the `call_ollama` function, delete the class)
- `process_one_file_v2.py`

### What to Create (One Shared Library)
- `scripts/lib/common.py` — `load_config()`, `write_log()`, `file_hash()`, `atomic_save()`

This is **one new file** to eliminate duplication across **7 existing files**.

---

## The Refactoring Checklist

Phase 1: Extract shared code (1 hour)
- [ ] Create `scripts/lib/common.py` with `load_config()`, `write_log()`, `file_hash()`, `atomic_save()`
- [ ] Update `scan_documents.py` to import from `common`
- [ ] Update `process_one_file.py` to import from `common`
- [ ] Update `route_to_vault.py` to import from `common`
- [ ] Update `archive_low_value.py` to import from `common`
- [ ] Update `bulk_convert_to_markdown.py` to import from `common`

Phase 2: Harden `process_one_file.py` (2 hours)
- [ ] Add `tenacity` retry to `run_ollama()`
- [ ] Add `filelock` to `save_state()`
- [ ] Replace `validate_metadata()` with Pydantic `MetadataOutput`
- [ ] Replace JSON-in-YAML with native YAML frontmatter
- [ ] Fix MAX_CHARS → word count truncation
- [ ] Add collision-safe sidecar naming (hash suffix)

Phase 3: Clean up (30 minutes)
- [ ] Delete v2 sprawl files
- [ ] Update `register-scripts.py` with actual purpose fields
- [ ] Update `requirements.txt`

**Total: 3.5 hours of focused refactoring. No new parallel files. Your existing scripts get better.**
