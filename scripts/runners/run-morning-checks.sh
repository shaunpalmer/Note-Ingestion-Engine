#!/usr/bin/env bash
set -euo pipefail

# run-morning-checks.sh
# Purpose: Runner that chains all morning health-check scripts.
# Usage:   ./scripts/runners/run-morning-checks.sh
# Output:  logs/automation.log
# Risk:    read-only (all child scripts are read-only)

PROJECT_ROOT="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts"
source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="run-morning-checks"

log() {
    local level="$1"
    local msg="$2"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[${ts}] [${level}] [${SCRIPT_NAME}] ${msg}"
    echo "${line}"
    mkdir -p "${LOGS_DIR}"
    echo "${line}" >> "${AUTOMATION_LOG}"
}

log INFO "=== Morning Checks Started ==="

# 1. Network status
if [[ -x "${SCRIPTS_DIR}/network/check-network-status.sh" ]]; then
    log INFO "Running network check..."
    "${SCRIPTS_DIR}/network/check-network-status.sh" || log WARN "Network check failed"
else
    log WARN "Network check script not found"
fi

# 2. Ollama status
if [[ -x "${SCRIPTS_DIR}/ollama/check-ollama-status.sh" ]]; then
    log INFO "Running Ollama status check..."
    "${SCRIPTS_DIR}/ollama/check-ollama-status.sh" || log WARN "Ollama check failed"
else
    log WARN "Ollama check script not found"
fi

# 3. Scan Obsidian inbox
if [[ -f "${SCRIPTS_DIR}/obsidian/scan-obsidian-inbox.py" ]]; then
    log INFO "Running Obsidian inbox scan..."
    python3 "${SCRIPTS_DIR}/obsidian/scan-obsidian-inbox.py" || log WARN "Obsidian scan failed"
else
    log WARN "Obsidian scan script not found"
fi

# 4. Update script registry
if [[ -f "${SCRIPTS_DIR}/script-registration/register-scripts.py" ]]; then
    log INFO "Updating script registry..."
    python3 "${SCRIPTS_DIR}/script-registration/register-scripts.py" || log WARN "Registry update failed"
else
    log WARN "Script registry script not found"
fi

# 5. Update storage table (dry-run only from runner; run with --apply separately)
if [[ -f "${SCRIPTS_DIR}/storage-table/update-storage-table.py" ]]; then
    log INFO "Running storage table scan (dry-run)..."
    python3 "${SCRIPTS_DIR}/storage-table/update-storage-table.py" --dry-run || log WARN "Storage scan failed"
else
    log WARN "Storage table script not found"
fi

log INFO "=== Morning Checks Complete ==="
