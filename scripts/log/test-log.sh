#!/usr/bin/env bash
set -euo pipefail

# test-log.sh
# Purpose: Verify the logging system works end-to-end.
# Usage:   ./scripts/log/test-log.sh
# Risk:    writes-log

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

LOG_WRITER="${PROJECT_ROOT}/scripts/log/write-log.sh"

if [[ ! -x "${LOG_WRITER}" ]]; then
    echo "ERROR: Log writer not found or not executable: ${LOG_WRITER}" >&2
    exit 1
fi

SCRIPT_NAME="test-log"

echo "=== Log Test Started ==="

"${LOG_WRITER}" INFO "${SCRIPT_NAME}" "This is an informational message"
"${LOG_WRITER}" WARN "${SCRIPT_NAME}" "This is a warning"
"${LOG_WRITER}" ERROR "${SCRIPT_NAME}" "This is an error (simulated)"
"${LOG_WRITER}" DEBUG "${SCRIPT_NAME}" "This is a debug message"

echo "=== Log Test Finished ==="
echo "Inspect the log with:"
echo "  tail -n 4 ${PROJECT_ROOT}/logs/automation.log"
