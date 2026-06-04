# Automation Architecture Summary

Date: 2026-05-26
Status: Foundation complete, ready for bulk operation

---

## What We Built

A local Linux automation system that turns scattered documents (`.txt`, `.md`, `.pdf`, `.docx`) into structured, AI-tagged Obsidian knowledge — without touching originals.

---

## Why Markdown Is the Core Format

LLMs and RAG systems reason best over plain text with structure. Markdown is that structure. PDFs and Word files are opaque containers — the AI can't navigate headings, links, or tables inside them without extraction.

The pipeline therefore:
1. **Preserves** the original PDF/DOCX exactly where it is (as the canonical reference)
2. **Extracts** the text into a companion `.md` file
3. **Processes** the `.md` through Ollama for metadata
4. **Creates** an `.ai.md` sidecar with tags, backlinks, value score
5. **Routes** all three files (original + markdown + sidecar) into the vault's category folders

You keep the beautiful Word formatting for humans. The AI gets clean Markdown to reason about.

---

## Confidence Scoring

The model returns a self-reported confidence (0–1). This is unreliable in isolation. We apply post-processing:

| Method | Purpose | When to Use |
|--------|---------|-------------|
| **Sigmoid** | Stretch mid-range scores to make subtle differences visible | Single-file processing, making clearer cut-offs |
| **Soft-max** | Convert raw scores to relative probabilities across a batch | Batch ranking, "which of these 50 files matters most?" |

The sigmoid is the default because it handles single-document judgments cleanly. Soft-max becomes useful when you want to prioritize a daily queue.

---

## Vault Category Structure

```
~/Documents/LinuxBox-Vault/
|-- inbox/              # New files waiting for first review
|-- agency/             # Client work, contracts, proposals
|-- marketing/          # SEO, campaigns, branding, leads
|-- data/               # Databases, cleaning, analysis, reports
|-- programming/        # Scripts, automation, APIs, Linux
|-- personal/           # Family, health, finance, house
|-- reference/          # Permanent, foundational knowledge
|-- archive/            # Low-confidence, throwaway, outdated
|-- review/             # AI flagged as uncertain — needs human eye
```

The `route_to_vault.py` script reads the AI-generated tags and value score, then chooses the folder automatically. You can override manually anytime.

---

## Multi-Business Context

You mentioned running three streams: personal, agency, and data/programming. The tagging system already accounts for this:

- **Agency files** get tags like `client`, `project`, `contract`, `invoice` → routed to `agency/`
- **Marketing files** get tags like `seo`, `campaign`, `lead` → routed to `marketing/`
- **Data/Programming** get tags like `python`, `script`, `csv`, `automation` → routed to `data/` or `programming/`
- **Personal** gets tags like `family`, `health`, `finance` → routed to `personal/`

The AI doesn't need to know your business structure explicitly. It reads the *content* and the tags emerge naturally.

---

## Full Pipeline (One Command)

```bash
# Dry-run first — see what would happen
./scripts/runners/run-daily-ingest.sh

# Apply for real — warm Ollama, process up to 50 files, route, archive, report
./scripts/runners/run-daily-ingest.sh --apply
```

Stages:
1. Warm Ollama (`qwen2.5-coder:7b`) and keep alive for 3 hours
2. Scan `imported-text-files/` for unprocessed candidates
3. Extract text (`.txt`, `.md`, `.pdf`, `.docx`)
4. Send to Ollama with strict JSON prompt
5. Validate JSON schema (title, summary, tags, backlinks, value, confidence)
6. Write `.ai.md` sidecar with YAML frontmatter
7. Normalize confidence scores (sigmoid)
8. Route sidecars to vault category folders
9. Archive low-value files (`throwaway` or confidence < 0.4)
10. Write daily report: `reports/YYYY-MM-DD-ingestion-report.md`

---

## What Exists Now (19 Scripts)

| Script | Status |
|--------|--------|
| Logging infrastructure | ✅ Working |
| Network status check | ✅ Working |
| Ollama warm-up / unload / status | ✅ Working |
| Obsidian inbox scanner | ✅ Working |
| Script registry | ✅ Working (19 scripts) |
| Storage table | ✅ Working (7,614 files indexed) |
| Document ingestion scanner | ✅ Working (dry-run by default) |
| Single-file processor (`txt/md/pdf/docx` → Ollama → sidecar) | ✅ Working |
| Unified text extractor | ✅ Working |
| Bulk converter (`txt/pdf/docx` → `.md`) | ✅ Working |
| Vault router (AI tags → category folders) | ✅ Working |
| Confidence normalizer (sigmoid / soft-max) | ✅ Working |
| Archive low-value files | ✅ Working |
| Daily report generator | ✅ Working |
| Morning checks runner | ✅ Working |
| Daily ingest runner | ✅ Working |
| Share setup scripts | ✅ Existing (setup + test) |

---

## What's Missing / Next

1. **PDF extraction quality testing** — `pypdf` extracts text but formatting is lost. For complex PDFs, `pdfplumber` or `pymupdf` may be better.
2. **Vault publication with collision handling** — if a file already exists in the target folder, the router needs a `--force` or `--skip` policy.
3. **Cron integration** — `run-daily-ingest.sh` is ready for `crontab` once you're confident in the output quality.
4. **Real file volume testing** — one test file works. 50 real files is the next milestone.
5. **Confidence thresholds tuning** — the 0.4 cutoff for archiving is a starting guess. You'll want to adjust based on actual output quality.

---

## Recommended Next Action

1. Drop 5–10 real `.txt` or `.md` files into `imported-text-files/`
2. Run `./scripts/runners/run-daily-ingest.sh` (dry-run)
3. Inspect the proposed routing and sidecar content
4. Run with `--apply` if it looks correct
5. Review `sidecars/*.ai.md` and `reports/2026-05-26-ingestion-report.md`
6. Adjust tag routing rules in `route_to_vault.py` if files are landing in wrong categories
