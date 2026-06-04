#!/usr/bin/env bash
set -euo pipefail

# write-log.sh
# Purpose: Append a structured log entry to the automation log.
# Usage:   ./scripts/log/write-log.sh <LEVEL> <SCRIPT_NAME> <MESSAGE>
# Example: ./scripts/log/write-log.sh INFO check-network "Wi-Fi route found"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

LOGS_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOGS_DIR}/automation.log"

# Ensure log directory exists
mkdir -p "${LOGS_DIR}"

# Validate arguments
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <LEVEL> <SCRIPT_NAME> <MESSAGE>" >&2
    exit 1
fi

LEVEL="$1"
SCRIPT_NAME="$2"
shift 2
MESSAGE="$*"

TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

# Write to log file
printf '[%s] [%s] [%s] %s\n' "${TIMESTAMP}" "${LEVEL}" "${SCRIPT_NAME}" "${MESSAGE}" >> "${LOG_FILE}"

# Also echo to stdout so the caller can see it
printf '[%s] [%s] [%s] %s\n' "${TIMESTAMP}" "${LEVEL}" "${SCRIPT_NAME}" "${MESSAGE}"
