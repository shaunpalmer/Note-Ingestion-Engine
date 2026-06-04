# ARCHITECTURE NOTE:
# This file belongs to the legacy filing/tagging-first pipeline.
# Do not extend this as the authority for the new transform-first pipeline.
# See docs/debt/ARCHITECTURAL_DEBT_MAP.md.
"""
process_one_file_v2.py
Purpose: Refactored single-file processor using external libraries for all heavy lifting.

Libraries used:
- pydantic    → Anti-corruption layer (schema validation)
- filelock    → Thread-safe state access
- tenacity    → Retry logic + circuit breaker
- blinker     → Observer pattern (signals)
- structlog   → Structured logging

Usage:
    python3 -m scripts.ingestion.process_one_file_v2 <file_path> [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

# Local imports (all library-based modules)
from .circuit_breaker import OllamaUnavailableError, ollama_circuit_breaker
from .config import (
    CONFIDENCE_THRESHOLD,
    MAX_WORDS_FOR_LLM,
    get_logs_dir,
    get_sidecars_dir,
    get_state_dir,
)
from .handlers import (  # noqa: F401 — side effects: registers signal handlers
    archive_low_value,
    log_file_processed,
    log_ollama_failure,
    log_ollama_metrics,
    move_to_review,
    route_sidecar_to_vault,
)
from .models import MetadataOutput, ProcessingResult, StateEntry
from .ollama_client import OllamaClient
from .signals import (
    file_processed,
    file_quarantined,
    metadata_invalid,
    ollama_failed,
    sidecar_written,
)
from .state_manager import StateManager

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Text Extraction
# ---------------------------------------------------------------------------

def extract_text(path: Path) -> str:
    """Delegate to unified extractor for .txt, .md, .pdf, .docx support."""
    extractor = Path(__file__).with_name("extract_text.py")
    if extractor.exists():
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(extractor), str(path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            pass
    # Fallback: plain text only
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def count_words(text: str) -> int:
    return len(text.split())


def truncate_for_llm(text: str, max_words: int = MAX_WORDS_FOR_LLM) -> str:
    """Executive summary truncation: first 60% + last 20%."""
    words = text.split()
    if len(words) <= max_words:
        return text
    first = int(max_words * 0.6)
    last = int(max_words * 0.2)
    return (
        " ".join(words[:first])
        + "\n\n...[truncated: middle section omitted]...\n\n"
        + " ".join(words[-last:])
    )


# ---------------------------------------------------------------------------
# Prompt Building
# ---------------------------------------------------------------------------

def build_prompt(text: str) -> str:
    return (
        "You are an Obsidian metadata assistant. "
        "Return one raw JSON object only. No Markdown. No code fence. No explanation. "
        "Use lowercase kebab-case tags. "
        "Use Obsidian backlinks in [[Double Brackets]]. "
        "If no strong backlink exists, return an empty backlinks array. "
        "Set value as one of: throwaway, useful, permanent. "
        "Use confidence between 0 and 1. Do not use confidence 1 unless extremely certain. "
        "Prefer useful for working project notes unless clearly disposable or foundational.\n\n"
        f'Text: "{text}"\n\n'
        'Return exactly this schema: '
        '{"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'
    )


# ---------------------------------------------------------------------------
# JSON Sanitization
# ---------------------------------------------------------------------------

def sanitize_llm_output(raw: str) -> str:
    """Strip accidental Markdown fences and whitespace."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# File Hashing
# ---------------------------------------------------------------------------

def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Sidecar Generation
# ---------------------------------------------------------------------------

def write_sidecar(
    original: Path,
    metadata: MetadataOutput,
    sidecar_dir: Path,
    model: str,
    processing_time_ms: int,
) -> Path:
    sidecar_name = original.stem + ".ai.md"
    sidecar_path = sidecar_dir / sidecar_name

    # Build YAML frontmatter (native YAML, not JSON-in-YAML)
    frontmatter_lines = [
        "---",
        f"schema_version: '2.0'",
        "ai_metadata:",
        f"  model: {model}",
        "  prompt_version: '1.0'",
        f"  processed_at: {datetime.now().isoformat()}",
        f"  processing_time_ms: {processing_time_ms}",
        "source:",
        f"  file: {original}",
        f"  type: {original.suffix.lower().lstrip('.')}",
        "output:",
        f"  title: {metadata.title}",
        f"  summary: {metadata.summary}",
        "  tags:",
    ]
    for tag in metadata.tags:
        frontmatter_lines.append(f"    - {tag}")

    frontmatter_lines.append("  backlinks:")
    for bl in metadata.backlinks:
        frontmatter_lines.append(f"    - {bl}")

    frontmatter_lines.extend([
        f"  value_tier: {metadata.value}",
        "  confidence:",
        f"    raw: {metadata.confidence}",
        "quality:",
        "  status: ai-generated-needs-review",
        "  reviewed_at:",
        "  reviewed_by:",
        "  review_notes:",
        "---",
        "",
        f"# {metadata.title}",
        "",
        "## Summary",
        "",
        metadata.summary,
        "",
        "## Why it matters",
        "",
    ])

    if metadata.value == "throwaway":
        frontmatter_lines.append("This note appears disposable. Review before keeping.")
    elif metadata.value == "permanent":
        frontmatter_lines.append("This note appears foundational or reference-worthy.")
    else:
        frontmatter_lines.append("This note appears useful for active work.")

    frontmatter_lines.extend([
        "",
        "## Source link",
        "",
        f"[Open original file](file://{original})",
        "",
        "## Review Checklist",
        "",
        "- [ ] Tags are accurate and useful",
        "- [ ] Backlinks are meaningful",
        "- [ ] Value tier is appropriate",
        "- [ ] Summary captures the essence",
    ])

    sidecar_dir.mkdir(parents=True, exist_ok=True)
    with open(sidecar_path, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter_lines) + "\n")

    return sidecar_path


# ---------------------------------------------------------------------------
# Main Processing Logic
# ---------------------------------------------------------------------------

def process_file(file_path: Path, dry_run: bool = False) -> ProcessingResult:
    """Process a single file through the full pipeline with library-based resilience."""
    start_time = time.time()
    sha = file_hash(file_path)
    state_mgr = StateManager()

    # Check if already processed
    if state_mgr.sha_exists(sha):
        logger.info("file.already_processed", source_path=str(file_path), sha=sha)
        return ProcessingResult(
            source_path=str(file_path),
            sha256=sha,
            source_type=file_path.suffix,
            word_count=0,
            model="",
            processing_time_ms=0,
            status="skipped",
            error_message="Already processed",
        )

    # Extract text
    text = extract_text(file_path)
    word_count = count_words(text)
    logger.info("file.extracted", source_path=str(file_path), words=word_count)

    if not text.strip():
        return ProcessingResult(
            source_path=str(file_path),
            sha256=sha,
            source_type=file_path.suffix,
            word_count=word_count,
            model="",
            processing_time_ms=0,
            status="failed",
            error_message="Empty or unreadable file",
        )

    # Truncate if needed
    if word_count > MAX_WORDS_FOR_LLM:
        text = truncate_for_llm(text)
        logger.info("file.truncated", source_path=str(file_path), original_words=word_count)

    # Build prompt
    prompt = build_prompt(text)

    # Call Ollama (with circuit breaker + retry + fallback)
    client = OllamaClient()
    ollama_start = time.time()

    try:
        raw_response = client.generate_with_fallback(prompt)
    except OllamaUnavailableError as e:
        logger.error("ollama.unavailable", error=str(e))
        ollama_failed.send(None, primary=client.model, fallback=client.fallback_model)
        return ProcessingResult(
            source_path=str(file_path),
            sha256=sha,
            source_type=file_path.suffix,
            word_count=word_count,
            model=client.model,
            processing_time_ms=int((time.time() - start_time) * 1000),
            status="failed",
            error_message=f"Ollama unavailable: {e}",
        )

    ollama_elapsed_ms = int((time.time() - ollama_start) * 1000)

    # Sanitize and validate
    cleaned = sanitize_llm_output(raw_response)

    try:
        metadata = MetadataOutput.model_validate_json(cleaned)
    except Exception as e:
        logger.warning("validation.failed", error=str(e), response=cleaned[:200])
        metadata_invalid.send(None, source_path=str(file_path), error=str(e))

        # Quarantine for human review
        if not dry_run:
            quarantine_path = get_sidecars_dir() / (file_path.stem + ".ai.md.invalid")
            with open(quarantine_path, "w") as f:
                f.write(f"# INVALID RESPONSE\n\n```json\n{cleaned}\n```\n\nError: {e}\n")
            file_quarantined.send(None, sidecar_path=quarantine_path, reason="validation_failed")

        return ProcessingResult(
            source_path=str(file_path),
            sha256=sha,
            source_type=file_path.suffix,
            word_count=word_count,
            model=client.model,
            processing_time_ms=int((time.time() - start_time) * 1000),
            status="quarantined",
            error_message=f"Validation failed: {e}",
        )

    # Dry-run: stop before writing
    if dry_run:
        logger.info("dry_run.complete", source_path=str(file_path), metadata=metadata.model_dump())
        return ProcessingResult(
            source_path=str(file_path),
            sha256=sha,
            source_type=file_path.suffix,
            word_count=word_count,
            model=client.model,
            processing_time_ms=ollama_elapsed_ms,
            status="processed",
            metadata=metadata,
        )

    # Write sidecar
    sidecar_path = write_sidecar(
        file_path,
        metadata,
        get_sidecars_dir(),
        client.model,
        ollama_elapsed_ms,
    )
    sidecar_written.send(None, sidecar_path=sidecar_path, metadata=metadata)
    logger.info("sidecar.written", path=str(sidecar_path))

    # Update state
    state_mgr.upsert_entry(StateEntry(
        source_path=str(file_path),
        sha256=sha,
        processed_at=datetime.now(),
        model=client.model,
        sidecar_path=str(sidecar_path),
        status="processed",
        value=metadata.value,
        confidence=metadata.confidence,
    ))

    # Archive low-value files
    if metadata.value == "throwaway" or metadata.confidence < CONFIDENCE_THRESHOLD:
        file_quarantined.send(None, sidecar_path=sidecar_path, reason="low_value_or_confidence")

    total_elapsed_ms = int((time.time() - start_time) * 1000)
    result = ProcessingResult(
        source_path=str(file_path),
        sha256=sha,
        source_type=file_path.suffix,
        word_count=word_count,
        model=client.model,
        processing_time_ms=total_elapsed_ms,
        status="processed",
        sidecar_path=str(sidecar_path),
        metadata=metadata,
    )

    file_processed.send(None, result=result)
    return result


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Process one file through Ollama (v2)")
    parser.add_argument("file_path", help="Absolute path to the file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    args = parser.parse_args()

    path = Path(args.file_path)
    if not path.exists():
        logger.error("file.not_found", path=str(path))
        sys.exit(1)

    result = process_file(path, dry_run=args.dry_run)
    print(f"\nStatus: {result.status}")
    if result.metadata:
        print(f"Title: {result.metadata.title}")
        print(f"Value: {result.metadata.value}")
        print(f"Confidence: {result.metadata.confidence}")
    if result.error_message:
        print(f"Error: {result.error_message}")


if __name__ == "__main__":
    main()
