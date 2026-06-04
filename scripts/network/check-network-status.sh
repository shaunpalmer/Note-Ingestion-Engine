#!/usr/bin/env bash
set -euo pipefail

# check-network-status.sh
# Purpose: Read-only network status check.
# Usage: ./scripts/network/check-network-status.sh
# Output: logs/network.log
# Risk level: read-only

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

source "${PROJECT_ROOT}/config/paths.conf"

SCRIPT_NAME="check-network-status"
LOG_FILE="${LOGS_DIR}/network.log"

log_info() {
    local msg="$1"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[${ts}] [INFO] [${SCRIPT_NAME}] ${msg}"
    echo "${line}"
    echo "${line}" >> "${LOG_FILE}"
}

log_warn() {
    local msg="$1"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[${ts}] [WARN] [${SCRIPT_NAME}] ${msg}"
    echo "${line}"
    echo "${line}" >> "${LOG_FILE}"
}

mkdir -p "${LOGS_DIR}"

log_info "START Checking network status"

# Check nmcli device status
if command -v nmcli &>/dev/null; then
    log_info "nmcli available"
    nmcli device status 2>/dev/null | while read -r line; do
        log_info "nmcli: ${line}"
    done || true
else
    log_warn "nmcli not found"
fi

# Check IP routes
if command -v ip &>/dev/null; then
    log_info "Checking IP routes..."
    ip route 2>/dev/null | while read -r line; do
        log_info "ip route: ${line}"
    done || true
else
    log_warn "ip command not found"
fi

# Check internet reachability
if ping -c 2 -W 3 8.8.8.8 &>/dev/null; then
    log_info "OK Internet reachable (8.8.8.8)"
else
    log_warn "FAIL No internet reachability (8.8.8.8)"
fi

# Check DNS resolution
if ping -c 2 -W 3 google.com &>/dev/null; then
    log_info "OK DNS resolution working (google.com)"
else
    log_warn "FAIL DNS resolution not working (google.com)"
fi

log_info "END Completed successfully"
