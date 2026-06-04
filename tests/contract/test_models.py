from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.core.models import (
    DecisionNote,
    ExtractionResult,
    ExtractionStatus,
    GateDecision,
    GateOutcome,
    NoteStatus,
    NoteType,
    PipelineStage,
    StateEntry,
)


HASH = "a" * 64
NOW = datetime(2026, 6, 4, tzinfo=timezone.utc)


def test_extraction_result_accepts_honest_success():
    result = ExtractionResult(
        source_path="fixtures/GP-001-simple-markdown-note.md",
        source_hash=HASH,
        original_extension=".md",
        detected_mime="text/markdown",
        file_size_bytes=128,
        modified_at=NOW,
        adapter_used="PlainTextAdapter",
        parser_used="md_extract",
        status=ExtractionStatus.OK,
        text="# Useful note\n\nA real note.",
    )

    assert result.status == ExtractionStatus.OK
    assert result.source_hash == HASH


def test_extraction_result_rejects_silent_empty_success():
    with pytest.raises(ValidationError, match="status=ok requires meaningful extracted text"):
        ExtractionResult(
            source_path="fixtures/empty.md",
            source_hash=HASH,
            original_extension=".md",
            file_size_bytes=0,
            adapter_used="PlainTextAdapter",
            parser_used="md_extract",
            status=ExtractionStatus.OK,
            text="",
        )


def test_extraction_result_requires_failure_reason_for_unreadable_status():
    with pytest.raises(ValidationError, match="requires warnings or error_message"):
        ExtractionResult(
            source_path="fixtures/GP-004-scanned-pdf.pdf",
            source_hash=HASH,
            original_extension=".pdf",
            file_size_bytes=2048,
            adapter_used="PdfAdapter",
            parser_used="pdf_classifier",
            status=ExtractionStatus.OCR_NEEDED,
        )


def test_gate_decision_allows_only_think_to_call_llm():
    decision = GateDecision(
        source_hash=HASH,
        outcome=GateOutcome.THINK,
        should_call_llm=True,
        reason="Meaningful text with possible reusable knowledge.",
        signals={"token_count": 120},
        value_hint=0.7,
        scrap_hint=0.2,
        provenance={"source_path": "fixtures/GP-001-simple-markdown-note.md"},
    )

    assert decision.should_call_llm is True


def test_gate_decision_rejects_llm_call_for_review_outcome():
    with pytest.raises(ValidationError, match="should_call_llm must be true only"):
        GateDecision(
            source_hash=HASH,
            outcome=GateOutcome.REVIEW,
            should_call_llm=True,
            reason="Unclear source quality.",
            review_reason="Needs human inspection.",
        )


def test_gate_decision_requires_review_reason_for_ocr_needed():
    with pytest.raises(ValidationError, match="requires review_reason"):
        GateDecision(
            source_hash=HASH,
            outcome=GateOutcome.OCR_NEEDED,
            should_call_llm=False,
            reason="PDF appears image-only.",
        )


def test_decision_note_accepts_source_backed_high_value_note():
    note = DecisionNote(
        source_hash=HASH,
        note_type=NoteType.HOW_TO,
        title="Restore Network DNS Resolution",
        essence="A technical note explaining how DNS was restored on a Linux machine.",
        summary="The source records commands and checks used to fix DNS resolution.",
        why_it_matters=["Preserves a repeatable fix for a Linux networking problem."],
        key_points=["Check resolver config before changing network services."],
        keep_facts=["Command preserved: resolvectl status"],
        business_area=["LinuxBox"],
        topics=["linux", "dns", "networking"],
        tags=["linux", "how-to"],
        possible_actions=["Reuse the checks during future DNS failures."],
        answers_future_questions=["How did I check DNS resolution on Linux before?"],
        source_relevance="Contains exact troubleshooting steps and commands.",
        value_score=0.9,
        scrap_score=0.1,
        uncertainty=0.1,
        fact_interpretation_boundary="Commands are source facts; usefulness is AI interpretation.",
        discarded_summary="Removed repeated terminal noise.",
        raw_excerpt="resolvectl status",
    )

    assert note.note_type == NoteType.HOW_TO
    assert note.value_score == 0.9


def test_decision_note_rejects_high_value_without_raw_excerpt():
    with pytest.raises(ValidationError, match="high-value DecisionNote requires raw_excerpt"):
        DecisionNote(
            source_hash=HASH,
            note_type=NoteType.REFERENCE,
            title="Client Quote",
            essence="A source-backed client quote.",
            summary="A quote with useful operational details.",
            why_it_matters=["Could support future pricing decisions."],
            key_points=["Includes a price and customer name."],
            keep_facts=["Price: 120"],
            answers_future_questions=["What did this client quote include?"],
            source_relevance="Contains pricing information.",
            value_score=0.8,
            scrap_score=0.1,
            uncertainty=0.1,
            fact_interpretation_boundary="Price is source fact; action is interpretation.",
            discarded_summary="Removed boilerplate.",
        )


def test_decision_note_rejects_unexplained_uncertainty():
    with pytest.raises(ValidationError, match="requires uncertainty_reason"):
        DecisionNote(
            source_hash=HASH,
            note_type=NoteType.IDEA,
            title="Marketing Idea",
            essence="A possible marketing idea.",
            summary="The source may describe a campaign concept.",
            why_it_matters=["Could support later campaign planning."],
            key_points=["Mentions lead generation."],
            answers_future_questions=["What marketing ideas mentioned lead generation?"],
            source_relevance="Contains possible strategy material.",
            value_score=0.5,
            scrap_score=0.3,
            uncertainty=0.6,
            fact_interpretation_boundary="Topic is source fact; campaign value is interpretation.",
            discarded_summary="Removed unclear fragments.",
        )


def test_state_entry_accepts_consistent_created_note_state():
    entry = StateEntry(
        source_hash=HASH,
        source_path="fixtures/GP-001-simple-markdown-note.md",
        current_stage=PipelineStage.COMPOSED,
        extraction_status=ExtractionStatus.OK,
        gate_outcome=GateOutcome.THINK,
        note_status=NoteStatus.CREATED,
        composed_note_path="out/GP-001-simple-markdown-note.md",
        schema_version="1",
        created_at=NOW,
        updated_at=NOW,
        run_id="contract-test-run",
    )

    assert entry.note_status == NoteStatus.CREATED


def test_state_entry_rejects_review_without_queue():
    with pytest.raises(ValidationError, match="current_stage=review requires review_queue"):
        StateEntry(
            source_hash=HASH,
            source_path="fixtures/GP-004-scanned-pdf.pdf",
            current_stage=PipelineStage.REVIEW,
            extraction_status=ExtractionStatus.OCR_NEEDED,
            note_status=NoteStatus.REVIEW_NEEDED,
            created_at=NOW,
            updated_at=NOW,
            run_id="contract-test-run",
        )


def test_contracts_reject_unknown_fields():
    with pytest.raises(ValidationError):
        GateDecision(
            source_hash=HASH,
            outcome=GateOutcome.THINK,
            should_call_llm=True,
            reason="Meaningful source.",
            llm_confidence=0.99,
        )
