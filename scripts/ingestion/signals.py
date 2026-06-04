"""
signals.py
Purpose: Centralized blinker signal definitions for the observer pattern.
All pipeline events are emitted as signals; handlers subscribe independently.
"""

from __future__ import annotations

from blinker import Signal

# ---------------------------------------------------------------------------
# Pipeline Lifecycle Signals
# ---------------------------------------------------------------------------

# Emitted when a file is discovered and queued for processing
file_queued = Signal("file-queued")

# Emitted when a file completes full processing (success or failure)
file_processed = Signal("file-processed")

# Emitted when a sidecar file is written to disk
sidecar_written = Signal("sidecar-written")

# Emitted when a file is routed to a vault category
file_routed = Signal("file-routed")

# Emitted when a file is quarantined for human review
file_quarantined = Signal("file-quarantined")

# Emitted when a file is archived as low-value
file_archived = Signal("file-archived")

# Emitted when Ollama returns a response (valid or not)
ollama_responded = Signal("ollama-responded")

# Emitted when Ollama fails after all retries
ollama_failed = Signal("ollama-failed")

# Emitted when metadata validation fails (corrupted LLM output)
metadata_invalid = Signal("metadata-invalid")

# Emitted daily when the report is generated
daily_report_generated = Signal("daily-report-generated")

# Emitted when confidence scores are normalized across a batch
confidence_normalized = Signal("confidence-normalized")

# Emitted when the circuit breaker trips (Ollama unhealthy)
circuit_breaker_opened = Signal("circuit-breaker-opened")

# Emitted when the circuit breaker resets (Ollama recovered)
circuit_breaker_closed = Signal("circuit-breaker-closed")
