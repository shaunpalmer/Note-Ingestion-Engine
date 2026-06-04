#!/usr/bin/env bash
set -euo pipefail

# check-ollama-status.sh
# Purpose: Quick read-only check of Ollama API and loaded models.
# Usage:   ./scripts/ollama/check-ollama-status.sh
# Output:  stdout + logs/ollama.log
# Risk:    read-only

PROJECT_ROOT="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts"
source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="check-ollama-status"
LOG_FILE="${LOGS_DIR}/ollama.log"

log() {
    local level="$1"
    local msg="$2"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[${ts}] [${level}] [${SCRIPT_NAME}] ${msg}"
    echo "${line}"
    mkdir -p "${LOGS_DIR}"
    echo "${line}" >> "${LOG_FILE}"
}

log INFO "START Checking Ollama status"

if ! curl -sf "${OLLAMA_HOST}" &>/dev/null; then
    log WARN "Ollama API not reachable at ${OLLAMA_HOST}"
    log INFO "END Status check complete — Ollama is down or not serving"
    exit 0
fi

log INFO "Ollama API reachable at ${OLLAMA_HOST}"

# List running models
PS_JSON=$(curl -sf "${OLLAMA_HOST}/api/ps" 2>/dev/null || echo '{}')
MODELS=$(echo "${PS_JSON}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(m.get('name','?') for m in d.get('models',[])))" 2>/dev/null || echo "unknown")

log INFO "Currently loaded models: ${MODELS}"
log INFO "END Status check complete"
