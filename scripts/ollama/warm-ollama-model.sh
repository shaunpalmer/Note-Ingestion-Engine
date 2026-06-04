#!/usr/bin/env bash
set -euo pipefail

# warm-ollama-model.sh
# Purpose: Start Ollama service if needed, warm up the chosen model, verify it responds.
# Usage:   ./scripts/ollama/warm-ollama-model.sh
# Output:  logs/ollama.log
# Risk:    modifies-system (starts service, loads model into memory)

SCRIPT_DIR="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/scripts/ollama"
PROJECT_ROOT="/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts"
source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="warm-ollama-model"
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

log INFO "START Ollama warm-up"

# Check if ollama binary exists
if ! command -v ollama &>/dev/null; then
    log ERROR "ollama binary not found in PATH. Is Ollama installed?"
    exit 1
fi

# Check if ollama serve is running (API reachable)
if ! curl -sf "${OLLAMA_HOST}" &>/dev/null; then
    log WARN "Ollama API not reachable at ${OLLAMA_HOST}. Attempting to start ollama serve..."

    # Try systemd user service first
    if systemctl --user is-active ollama.service &>/dev/null; then
        log INFO "ollama.service is already active (systemd user)"
    elif systemctl is-active ollama.service &>/dev/null; then
        log INFO "ollama.service is already active (systemd system)"
    else
        log INFO "Starting ollama serve in background..."
        nohup ollama serve > "${LOGS_DIR}/ollama-serve.log" 2>&1 &
        sleep 3
    fi

    # Wait up to 30 seconds for API
    for i in {1..30}; do
        if curl -sf "${OLLAMA_HOST}" &>/dev/null; then
            log INFO "Ollama API is now reachable"
            break
        fi
        sleep 1
    done

    if ! curl -sf "${OLLAMA_HOST}" &>/dev/null; then
        log ERROR "Ollama API still not reachable after 30s. Check logs: ${LOGS_DIR}/ollama-serve.log"
        exit 1
    fi
else
    log INFO "Ollama API already reachable at ${OLLAMA_HOST}"
fi

# Warm up the model with a tiny prompt and keep_alive
log INFO "Warming model ${OLLAMA_MODEL} with keep_alive=${OLLAMA_KEEP_ALIVE}..."

RESPONSE=$(curl -sf "${OLLAMA_HOST}/api/generate" \
    -d "{
        \"model\": \"${OLLAMA_MODEL}\",
        \"prompt\": \"Reply with: LOCAL_AI_READY\",
        \"stream\": false,
        \"keep_alive\": \"${OLLAMA_KEEP_ALIVE}\"
    }" 2>/dev/null)

if [[ -z "${RESPONSE}" ]]; then
    log WARN "No response from model ${OLLAMA_MODEL}. Trying fallback ${OLLAMA_FALLBACK_MODEL}..."
    RESPONSE=$(curl -sf "${OLLAMA_HOST}/api/generate" \
        -d "{
            \"model\": \"${OLLAMA_FALLBACK_MODEL}\",
            \"prompt\": \"Reply with: LOCAL_AI_READY\",
            \"stream\": false,
            \"keep_alive\": \"${OLLAMA_KEEP_ALIVE}\"
        }" 2>/dev/null)
    if [[ -n "${RESPONSE}" ]]; then
        log INFO "Fallback model ${OLLAMA_FALLBACK_MODEL} responded successfully"
    else
        log ERROR "Neither primary nor fallback model responded. Check Ollama model list: ollama list"
        exit 1
    fi
else
    log INFO "Model ${OLLAMA_MODEL} warmed and responding"
fi

log INFO "END Ollama warm-up completed successfully"
