#!/usr/bin/env bash
set -euo pipefail

# run-daily-ingest.sh
# Purpose: Full daily document ingestion pipeline.
# Usage:   ./scripts/runners/run-daily-ingest.sh [--apply]
# Stages:
#   1. Warm Ollama
#   2. Scan for candidates
#   3. Process batch (up to 50 files)
#   4. Normalize confidence scores
#   5. Route approved sidecars to vault
#   6. Archive low-value files
#   7. Write daily report
# Output:  logs/ingestion.log + reports/YYYY-MM-DD-ingestion-report.md
# Risk:    writes-report + moves-files (copies to vault, does not delete originals)

PROJECT_ROOT="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts"
source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="run-daily-ingest"

log() {
    local level="$1"
    local msg="$2"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[${ts}] [${level}] [${SCRIPT_NAME}] ${msg}"
    echo "${line}"
    mkdir -p "${LOGS_DIR}"
    echo "${line}" >> "${LOGS_DIR}/ingestion.log"
}

APPLY_FLAG=""
if [[ "${1:-}" == "--apply" ]]; then
    APPLY_FLAG="--apply"
fi

DRY_RUN_FLAG=""
if [[ -z "${APPLY_FLAG}" ]]; then
    DRY_RUN_FLAG="--dry-run"
fi

log INFO "=== Daily Ingest Started ==="

# 1. Warm up Ollama
if [[ -x "${SCRIPTS_DIR}/ollama/warm-ollama-model.sh" ]]; then
    log INFO "Stage 1: Warming Ollama..."
    "${SCRIPTS_DIR}/ollama/warm-ollama-model.sh" || { log ERROR "Ollama warm-up failed"; exit 1; }
else
    log WARN "Ollama warm-up script not found"
fi

# 2. Scan for candidates (queue them in state)
if [[ -f "${SCRIPTS_DIR}/ingestion/scan_documents.py" ]]; then
    log INFO "Stage 2: Scanning incoming documents..."
    python3 "${SCRIPTS_DIR}/ingestion/scan_documents.py" ${APPLY_FLAG} --limit 50 || log WARN "Document scan failed"
else
    log WARN "Document scanner not found"
fi

# 3. Process queued files
#    We re-read state and process any files marked "queued"
if [[ -f "${SCRIPTS_DIR}/ingestion/process_one_file.py" ]]; then
    log INFO "Stage 3: Processing queued files..."
    # Extract queued file paths from state
    QUEUED_FILES=$(python3 -c "
import json, sys
state_path = '${STATE_DIR}/processed-files.json'
try:
    with open(state_path) as f:
        state = json.load(f)
    for h, entry in state.get('by_hash', {}).items():
        if entry.get('status') == 'queued':
            print(entry.get('source_path', ''))
except Exception:
    pass
" 2>/dev/null)

    if [[ -n "${QUEUED_FILES}" ]]; then
        while IFS= read -r file_path; do
            [[ -z "$file_path" ]] && continue
            if [[ -n "${DRY_RUN_FLAG}" ]]; then
                log INFO "Dry-run: would process $file_path"
            else
                python3 "${SCRIPTS_DIR}/ingestion/process_one_file.py" "$file_path" || log WARN "Failed: $file_path"
            fi
        done <<< "${QUEUED_FILES}"
    else
        log INFO "No queued files to process"
    fi
else
    log WARN "process_one_file.py not found"
fi

# 4. Normalize confidence
if [[ -f "${SCRIPTS_DIR}/ingestion/normalize_confidence.py" ]]; then
    log INFO "Stage 4: Normalizing confidence scores..."
    python3 "${SCRIPTS_DIR}/ingestion/normalize_confidence.py" ${DRY_RUN_FLAG} --method sigmoid || log WARN "Normalization failed"
else
    log WARN "normalize_confidence.py not found"
fi

# 5. Route to vault
if [[ -f "${SCRIPTS_DIR}/ingestion/route_to_vault.py" ]]; then
    log INFO "Stage 5: Routing sidecars to vault..."
    for sidecar in "${INGESTION_SIDECARS}"/*.ai.md; do
        [[ -e "$sidecar" ]] || continue
        if [[ -n "${DRY_RUN_FLAG}" ]]; then
            log INFO "Dry-run: would route $sidecar"
        else
            python3 "${SCRIPTS_DIR}/ingestion/route_to_vault.py" "$sidecar" ${DRY_RUN_FLAG} || log WARN "Routing failed: $sidecar"
        fi
    done
else
    log WARN "route_to_vault.py not found"
fi

# 6. Archive low-value
if [[ -f "${SCRIPTS_DIR}/ingestion/archive_low_value.py" ]]; then
    log INFO "Stage 6: Archiving low-value sidecars..."
    python3 "${SCRIPTS_DIR}/ingestion/archive_low_value.py" ${DRY_RUN_FLAG} || log WARN "Archive failed"
else
    log WARN "archive_low_value.py not found"
fi

# 7. Write daily report
if [[ -f "${SCRIPTS_DIR}/ingestion/write_daily_report.py" ]]; then
    log INFO "Stage 7: Writing daily report..."
    python3 "${SCRIPTS_DIR}/ingestion/write_daily_report.py" || log WARN "Report generation failed"
else
    log WARN "write_daily_report.py not found"
fi

log INFO "=== Daily Ingest Complete ==="
