#!/usr/bin/env bash
set -euo pipefail

# unload-ollama-model.sh
# Purpose: Unload the chosen model after the morning automation window.
# Usage:   ./scripts/ollama/unload-ollama-model.sh
# Output:  logs/ollama.log
# Risk:    modifies-system (frees model from memory)

PROJECT_ROOT="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts"
source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="unload-ollama-model"
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

log INFO "START Unloading Ollama models"

if ! curl -sf "${OLLAMA_HOST}" &>/dev/null; then
    log WARN "Ollama API not reachable. Nothing to unload."
    log INFO "END Unload complete (Ollama was already down)"
    exit 0
fi

# Unload by setting keep_alive to 0m for the target model
curl -sf "${OLLAMA_HOST}/api/generate" \
    -d "{
        \"model\": \"${OLLAMA_MODEL}\",
        \"prompt\": \"unload\",
        \"stream\": false,
        \"keep_alive\": \"0m\"
    }" >/dev/null 2>&1 || true

log INFO "Model ${OLLAMA_MODEL} unload signal sent (keep_alive=0m)"

# Also try fallback model
curl -sf "${OLLAMA_HOST}/api/generate" \
    -d "{
        \"model\": \"${OLLAMA_FALLBACK_MODEL}\",
        \"prompt\": \"unload\",
        \"stream\": false,
        \"keep_alive\": \"0m\"
    }" >/dev/null 2>&1 || true

log INFO "Fallback model ${OLLAMA_FALLBACK_MODEL} unload signal sent"
log INFO "END Unload complete"
