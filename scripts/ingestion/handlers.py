"""
handlers.py
Purpose: Signal handlers for the observer pattern.
Each handler subscribes to pipeline events and performs one action.
New behaviors are added by defining new functions here — no core changes needed.
"""

from __future__ import annotations

from pathlib import Path

import structlog

from .config import get_logs_dir, get_sidecars_dir, get_vault_path
from .models import MetadataOutput, ProcessingResult
from .signals import (
    circuit_breaker_opened,
    daily_report_generated,
    file_archived,
    file_processed,
    file_quarantined,
    file_queued,
    file_routed,
    metadata_invalid,
    ollama_failed,
    ollama_responded,
    sidecar_written,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Logging Handlers
# ---------------------------------------------------------------------------

@file_queued.connect
def log_file_queued(sender, **kwargs) -> None:
    logger.info("pipeline.file_queued", source_path=kwargs.get("source_path"))


@file_processed.connect
def log_file_processed(sender, **kwargs) -> None:
    result: ProcessingResult = kwargs["result"]
    logger.info(
        "pipeline.file_processed",
        source_path=result.source_path,
        status=result.status,
        elapsed_ms=result.processing_time_ms,
    )


@ollama_responded.connect
def log_ollama_metrics(sender, **kwargs) -> None:
    logger.info(
        "ollama.metrics",
        model=kwargs.get("model"),
        elapsed_ms=kwargs.get("elapsed_ms"),
        response_length=kwargs.get("response_length"),
    )


@ollama_failed.connect
def log_ollama_failure(sender, **kwargs) -> None:
    logger.error(
        "ollama.failure",
        primary=kwargs.get("primary"),
        fallback=kwargs.get("fallback"),
    )


@metadata_invalid.connect
def log_metadata_failure(sender, **kwargs) -> None:
    logger.warning(
        "validation.failed",
        source_path=kwargs.get("source_path"),
        error=kwargs.get("error"),
    )


@circuit_breaker_opened.connect
def log_circuit_opened(sender, **kwargs) -> None:
    logger.error(
        "circuit_breaker.opened",
        failure_count=kwargs.get("failure_count"),
        last_failure=kwargs.get("last_failure_time"),
    )


# ---------------------------------------------------------------------------
# Routing Handlers
# ---------------------------------------------------------------------------

@sidecar_written.connect
def route_sidecar_to_vault(sender, **kwargs) -> None:
    """Automatically route approved sidecars to vault categories."""
    sidecar_path: Path = kwargs["sidecar_path"]
    metadata: MetadataOutput = kwargs["metadata"]

    # Simple routing based on value tier
    vault_base = get_vault_path()
    category = _determine_category(metadata)
    target_dir = vault_base / category
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy sidecar (original stays in sidecars/)
    import shutil
    target_path = target_dir / sidecar_path.name
    shutil.copy2(sidecar_path, target_path)

    file_routed.send(
        sender,
        sidecar_path=sidecar_path,
        target_path=target_path,
        category=category,
    )
    logger.info("vault.routed", sidecar=sidecar_path.name, category=category)


def _determine_category(metadata: MetadataOutput) -> str:
    """Map metadata to vault folder."""
    tags = set(metadata.tags)
    if tags & {"agency", "client", "project", "contract", "invoice"}:
        return "agency"
    if tags & {"marketing", "seo", "campaign", "lead", "branding"}:
        return "marketing"
    if tags & {"data", "database", "csv", "analysis", "report"}:
        return "data"
    if tags & {"python", "script", "code", "automation", "linux", "programming"}:
        return "programming"
    if tags & {"personal", "family", "health", "finance"}:
        return "personal"
    if metadata.value == "permanent":
        return "reference"
    if metadata.value == "throwaway" or metadata.confidence < 0.4:
        return "archive"
    return "inbox"


# ---------------------------------------------------------------------------
# Quarantine Handler
# ---------------------------------------------------------------------------

@file_quarantined.connect
def move_to_review(sender, **kwargs) -> None:
    """Move low-confidence or failed files to review folder."""
    sidecar_path: Path = kwargs["sidecar_path"]
    reason: str = kwargs.get("reason", "unknown")

    review_dir = get_sidecars_dir().parent / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    target = review_dir / sidecar_path.name
    shutil.copy2(sidecar_path, target)

    logger.warning("vault.quarantined", sidecar=sidecar_path.name, reason=reason)


# ---------------------------------------------------------------------------
# Archive Handler
# ---------------------------------------------------------------------------

@file_archived.connect
def archive_low_value(sender, **kwargs) -> None:
    """Copy low-value sidecars to archive folder."""
    sidecar_path: Path = kwargs["sidecar_path"]
    archive_dir = get_sidecars_dir().parent / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    target = archive_dir / sidecar_path.name
    shutil.copy2(sidecar_path, target)

    logger.info("vault.archived", sidecar=sidecar_path.name)
