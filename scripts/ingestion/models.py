"""
models.py
Purpose: Pydantic schemas for the anti-corruption layer.
All validation, typing, and schema enforcement lives here.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# AI Output Schema (Anti-Corruption Layer)
# ---------------------------------------------------------------------------

class MetadataOutput(BaseModel):
    """Validates and sanitizes LLM-generated metadata before it enters the system."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Concise, human-readable title for the note",
    )
    summary: str = Field(
        ...,
        min_length=10,
        max_length=800,
        description="Plain-English summary of the document's content",
    )
    tags: list[str] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Lowercase kebab-case tags for categorization",
    )
    backlinks: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Obsidian-style backlink targets",
    )
    value: Literal["throwaway", "useful", "permanent"] = Field(
        ...,
        description="Value classification for retention decisions",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence (0-1), should not be exactly 1.0",
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_a_sentence(cls, v: str) -> str:
        """Titles are labels, not sentences."""
        words = v.split()
        if len(words) > 12:
            raise ValueError(f"Title too long ({len(words)} words). Must be ≤12 words.")
        return v.strip()

    @field_validator("summary")
    @classmethod
    def summary_must_differ_from_input(cls, v: str) -> str:
        """Prevent the model from echoing the input text."""
        # Heuristic: summary should not start with the exact input text
        # (We can't access the original text here; this is a post-hoc check in the pipeline)
        return v.strip()

    @field_validator("tags")
    @classmethod
    def tags_must_be_kebab_case(cls, v: list[str]) -> list[str]:
        """Enforce lowercase kebab-case for consistency."""
        pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        cleaned = []
        for tag in v:
            tag = tag.strip().lower().replace(" ", "-").replace("_", "-")
            if not pattern.match(tag):
                raise ValueError(f"Tag '{tag}' is not kebab-case")
            cleaned.append(tag)
        # Deduplicate while preserving order
        seen = set()
        return [t for t in cleaned if not (t in seen or seen.add(t))]

    @field_validator("backlinks")
    @classmethod
    def backlinks_must_use_brackets(cls, v: list[str]) -> list[str]:
        """Ensure Obsidian bracket notation."""
        formatted = []
        for bl in v:
            bl = bl.strip()
            if not bl.startswith("[["):
                bl = f"[[{bl}"
            if not bl.endswith("]]"):
                bl = f"{bl}]]"
            formatted.append(bl)
        # Deduplicate
        seen = set()
        return [b for b in formatted if not (b in seen or seen.add(b))]

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_realistic(cls, v: float) -> float:
        """Prevent the model from claiming absolute certainty."""
        if v == 1.0:
            raise ValueError("Confidence must not be exactly 1.0")
        return round(v, 3)


# ---------------------------------------------------------------------------
# Processing Result Schema
# ---------------------------------------------------------------------------

class ProcessingResult(BaseModel):
    """Structured record of a single file's journey through the pipeline."""

    source_path: str
    sha256: str
    source_type: Literal["txt", "md", "pdf", "docx", "doc", "unknown"]
    word_count: int = Field(ge=0)
    model: str
    processed_at: datetime = Field(default_factory=datetime.now)
    processing_time_ms: int = Field(ge=0)
    status: Literal["processed", "failed", "quarantined", "skipped"]
    sidecar_path: str | None = None
    metadata: MetadataOutput | None = None
    error_message: str | None = None

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_extension(cls, v: str) -> str:
        mapping = {".txt": "txt", ".md": "md", ".pdf": "pdf", ".docx": "docx", ".doc": "doc"}
        return mapping.get(v.lower(), v.lower().lstrip("."))


# ---------------------------------------------------------------------------
# State Entry Schema
# ---------------------------------------------------------------------------

class StateEntry(BaseModel):
    """Individual record in the processing state database."""

    source_path: str
    sha256: str
    queued_at: datetime | None = None
    processed_at: datetime | None = None
    model: str | None = None
    sidecar_path: str | None = None
    status: Literal["queued", "processed", "failed", "archived"]
    value: Literal["throwaway", "useful", "permanent"] | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class PipelineState(BaseModel):
    """Top-level state container."""

    schema_version: str = "2.0"
    last_updated: datetime = Field(default_factory=datetime.now)
    entries: dict[str, StateEntry] = Field(default_factory=dict)
