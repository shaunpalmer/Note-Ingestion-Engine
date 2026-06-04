# Architectural Debt Map

**Status:** Groundwork map for moving from the legacy filing/tagging pipeline to the transform-first pipeline.  
**Target pipeline:** Extract -> Gate -> Think/Transform -> Compose -> Place/Record.

This document is not a deletion plan. It identifies which existing files can be kept, wrapped, retired as authority, rewritten, migrated, or inspected later.

## Keep

These files contain useful infrastructure or project authority and should be preserved unless a later review finds a specific defect.

| File | Reason |
|---|---|
| `config/paths.conf` | Existing path source; should remain the basis for one config loader. |
| `scripts/ingestion/config.py` | Reusable typed/cached config boundary; candidate canonical loader. |
| `scripts/ingestion/state_manager.py` | Reusable locked/atomic state boundary; candidate canonical state writer. |
| `scripts/ingestion/ollama_client.py` | Useful local LLM client boundary for Stage 3 Reasoner. |
| `scripts/ingestion/circuit_breaker.py` | Useful resilience pattern around local LLM calls. |
| `scripts/ingestion/signals.py` | Useful observer/signal foundation for logs, reports, and metrics. |
| `scripts/ingestion/handlers.py` | Useful observer handler ideas; should not control core pipeline flow. |

## Wrap

These files contain useful code but expose the wrong boundary for the new architecture.

| File | Reason |
|---|---|
| `scripts/ingestion/extract_text.py` | Useful early extraction functions, but current suffix dispatch and bare-string return should be wrapped behind Registry -> Adapter -> parser utility returning `ExtractionResult`. |

## Retire As Authority

These files should not be extended as the source of truth for the new pipeline. Harvest useful snippets, prompts, logging, or resilience ideas only.

| File | Reason |
|---|---|
| `scripts/ingestion/process_one_file.py` | Legacy all-in-one processing flow; combines extraction, LLM metadata, sidecar writing, and state concerns. |
| `scripts/ingestion/process_one_file_v2.py` | Better engineering ideas, but still not the target orchestrator authority. Harvest resilience patterns, then retire. |
| `scripts/ingestion/normalize_confidence.py` | Post-hoc confidence normalization conflicts with independent `value_score`, `scrap_score`, and `uncertainty` contracts. |
| `scripts/ingestion/archive_low_value.py` | Legacy low-value handling belongs in deterministic Gate/review policy, not a post-processing archive script. |

## Rewrite

These files express the old architecture strongly enough that the safer route is replacement after the golden path is proven.

| File | Reason |
|---|---|
| `scripts/ingestion/scan_documents.py` | Should become discovery plus canonical state queueing through one schema and MIME/magic-byte detection. |
| `scripts/ingestion/route_to_vault.py` | Should become Stage 5 Placer with explicit collision and review policies; folders must not drive architecture. |
| `scripts/runners/run-daily-ingest.sh` | Should become a thin runner only. Bash must not own data/state logic. |

## Migrate

| File | Reason |
|---|---|
| `state/processed-files.json` | Must migrate to one canonical `StateEntry` schema keyed by source hash. Current schema drift risks skipped or repeated files. |

## Unknown / Needs Inspection

These areas should be inspected before changing them:

- Existing generated sidecars and reports.
- Any vault-routing assumptions in config files.
- Any scripts outside `scripts/ingestion/` that read or mutate ingestion state.
- Existing imported sample files that could become safe golden path fixtures.

## Old Architecture Conflict Notes

The old pipeline is filing/tagging-first:

```text
scan -> extract text -> ask LLM for shallow metadata -> write sidecar -> normalize confidence -> route/archive by tags/value/confidence
```

The new pipeline is transform-first:

```text
Extract -> Gate -> Think/Transform -> Compose -> Place/Record
```

The conflict is not cosmetic. The old pipeline treats the LLM as a metadata stamper and treats routing as the practical outcome. The new pipeline treats the LLM as a reasoner that produces `DecisionNote` objects, and treats placement as the final cheap step after trust, provenance, retrieval, and note usefulness have been established.

The old files should not be deleted immediately. They should remain available for harvesting useful pieces until the golden path works. Once the golden path proves the new flow, these files can be marked as legacy authority removed and replaced by the transform-first orchestrator and stage components.

## Review Rule

For every future change, ask:

> Does this improve retrieval, trust, provenance, transformation quality, or decision support?

If the answer is only "it processes more files," the change is probably premature.
