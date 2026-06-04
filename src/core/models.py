"""Pydantic contracts for the transform-first knowledge pipeline.

These models define stage boundaries only. They are not wired into the legacy
filing/tagging pipeline and contain no extraction, orchestration, routing, or
LLM implementation logic.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SourceHash = str


class StrictContractModel(BaseModel):
    """Base settings for explicit stage-boundary contracts."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ExtractionStatus(StrEnum):
    """Honest Stage 1 extraction outcomes."""

    OK = "ok"
    EMPTY = "empty"
    OCR_NEEDED = "ocr_needed"
    CORRUPT = "corrupt"
    UNSUPPORTED = "unsupported"
    METADATA_ONLY = "metadata_only"


class GateOutcome(StrEnum):
    """Deterministic Stage 2 outcomes before any LLM call."""

    THINK = "think"
    ARCHIVE_MINIMAL = "archive_minimal"
    REVIEW = "review"
    OCR_NEEDED = "ocr_needed"
    UNSUPPORTED = "unsupported"
    QUARANTINE = "quarantine"
    SKIP_DUPLICATE = "skip_duplicate"


class NoteType(StrEnum):
    """Initial allowed note types for DecisionNote outputs."""

    REFERENCE = "reference"
    HOW_TO = "how-to"
    IDEA = "idea"
    DECISION = "decision"
    ARCHIVE = "archive"
    MEETING = "meeting"
    CONTRACT = "contract"
    INVOICE = "invoice"
    CLIENT_RECORD = "client-record"
    MEDIA = "media"
    LOG = "log"
    SCRAP = "scrap"


class PipelineStage(StrEnum):
    """Canonical state stages for the transform-first pipeline."""

    DISCOVERED = "discovered"
    EXTRACTED = "extracted"
    GATED = "gated"
    TRANSFORMED = "transformed"
    COMPOSED = "composed"
    PLACED = "placed"
    REVIEW = "review"
    FAILED = "failed"


class NoteStatus(StrEnum):
    """Canonical state of the note artefact for a source file."""

    NOT_CREATED = "not_created"
    CREATED = "created"
    REVIEW_NEEDED = "review_needed"
    ARCHIVE_MINIMAL = "archive_minimal"
    FAILED = "failed"


class ExtractionResult(StrictContractModel):
    """Stage 1 output: extraction must report what happened, not just text."""

    source_path: str = Field(min_length=1)
    source_hash: SourceHash = Field(pattern=r"^[a-fA-F0-9]{64}$")
    original_extension: str = Field(min_length=1)
    detected_mime: str | None = None
    file_size_bytes: int = Field(ge=0)
    modified_at: datetime | None = None
    adapter_used: str = Field(min_length=1)
    parser_used: str = Field(min_length=1)
    status: ExtractionStatus
    text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_status_truthfulness(self) -> "ExtractionResult":
        if self.status == ExtractionStatus.OK and not self.text.strip():
            raise ValueError("status=ok requires meaningful extracted text")
        if self.status in {
            ExtractionStatus.CORRUPT,
            ExtractionStatus.UNSUPPORTED,
            ExtractionStatus.OCR_NEEDED,
        } and not (self.error_message or self.warnings):
            raise ValueError(f"status={self.status} requires warnings or error_message")
        return self


class GateDecision(StrictContractModel):
    """Stage 2 output: deterministic pre-LLM routing decision."""

    source_hash: SourceHash = Field(pattern=r"^[a-fA-F0-9]{64}$")
    outcome: GateOutcome
    should_call_llm: bool
    reason: str = Field(min_length=1)
    signals: dict[str, Any] = Field(default_factory=dict)
    value_hint: float | None = Field(default=None, ge=0.0, le=1.0)
    scrap_hint: float | None = Field(default=None, ge=0.0, le=1.0)
    review_reason: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_llm_boundary(self) -> "GateDecision":
        expected_llm = self.outcome == GateOutcome.THINK
        if self.should_call_llm is not expected_llm:
            raise ValueError("should_call_llm must be true only when outcome=think")
        if self.outcome in {
            GateOutcome.REVIEW,
            GateOutcome.OCR_NEEDED,
            GateOutcome.UNSUPPORTED,
            GateOutcome.QUARANTINE,
        } and not self.review_reason:
            raise ValueError(f"outcome={self.outcome} requires review_reason")
        return self


class DecisionNote(StrictContractModel):
    """Stage 3 output: decision-ready knowledge with provenance and trust."""

    source_hash: SourceHash = Field(pattern=r"^[a-fA-F0-9]{64}$")
    note_type: NoteType
    title: str = Field(min_length=1)
    essence: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    why_it_matters: list[str] = Field(min_length=1)
    key_points: list[str] = Field(min_length=1)
    keep_facts: list[str] = Field(default_factory=list)
    business_area: list[str] = Field(default_factory=list)
    project: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    organisations: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    proposed_links: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    possible_actions: list[str] = Field(default_factory=list)
    answers_future_questions: list[str] = Field(min_length=1)
    source_relevance: str = Field(min_length=1)
    value_score: float = Field(ge=0.0, le=1.0)
    scrap_score: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    uncertainty_reason: str = ""
    fact_interpretation_boundary: str = Field(min_length=1)
    discarded_summary: str = Field(min_length=1)
    raw_excerpt: str = ""

    @model_validator(mode="after")
    def validate_decision_note_quality(self) -> "DecisionNote":
        if self.uncertainty > 0.2 and not self.uncertainty_reason.strip():
            raise ValueError("uncertainty above 0.2 requires uncertainty_reason")
        if self.value_score >= 0.7 and not self.raw_excerpt.strip():
            raise ValueError("high-value DecisionNote requires raw_excerpt")
        if self.note_type == NoteType.HOW_TO and not self.keep_facts:
            raise ValueError("how-to DecisionNote requires preserved steps/commands in keep_facts")
        return self


class StateEntry(StrictContractModel):
    """Canonical state record for one source hash."""

    source_hash: SourceHash = Field(pattern=r"^[a-fA-F0-9]{64}$")
    source_path: str = Field(min_length=1)
    current_stage: PipelineStage
    extraction_status: ExtractionStatus | None = None
    gate_outcome: GateOutcome | None = None
    note_status: NoteStatus = NoteStatus.NOT_CREATED
    composed_note_path: str | None = None
    sidecar_path: str | None = None
    review_queue: str | None = None
    error_message: str | None = None
    schema_version: Literal["1"] = "1"
    created_at: datetime
    updated_at: datetime
    run_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_state_consistency(self) -> "StateEntry":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")
        if self.current_stage == PipelineStage.REVIEW and not self.review_queue:
            raise ValueError("current_stage=review requires review_queue")
        if self.current_stage == PipelineStage.FAILED and not self.error_message:
            raise ValueError("current_stage=failed requires error_message")
        if self.note_status == NoteStatus.CREATED and not self.composed_note_path:
            raise ValueError("note_status=created requires composed_note_path")
        return self
