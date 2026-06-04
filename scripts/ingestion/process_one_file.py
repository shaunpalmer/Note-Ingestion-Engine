#!/usr/bin/env python3
"""
process_one_file.py
Purpose: Process a single file through Ollama and create a .ai.md sidecar.
Usage:
    python3 scripts/ingestion/process_one_file.py <file_path> [--dry-run]
Output: .ai.md sidecar, logs/ingestion.log
Risk:   writes-report (creates sidecar, does not modify original)

ARCHITECTURAL NOTE: This file violates the transform-first architecture in several ways:
1. VIOLATES Single Responsibility Principle - handles extraction, LLM calls, validation, sidecar writing, and state updates
2. NEEDS REFACTORING: Should be split into separate components following the 5-stage pipeline:
   - Extract: File → ExtractionResult (with status)
   - Gate: ExtractionResult → GateDecision (deterministic, no LLM)
   - Think: Clean text + metadata → DecisionNote (LLM as reasoner)
   - Compose: DecisionNote → Markdown note + sidecar
   - Place: Composed note → Vault location + state update
3. SHOULD USE shared library functions instead of duplicated code (load_config, file_hash, write_log, save_state)
4. MISSING DETERMINISTIC GATE: Should check if file is worth LLM processing before calling Ollama
5. OUTPUT FORMAT INADEQUATE: Produces shallow metadata instead of DecisionNote per config/note_quality.md
6. STATE SCHEMA ISSUE: Uses by_hash/by_path instead of unified entries schema (causing live defect)
7. EXTRACTION LIMITED: Only returns text, no extraction status (ok/empty/ocr_needed/corrupt/unsupported/metadata_only)
8. FILE DETECTION NAIVE: Relies on extract_text.py which uses extension-only detection (should use magic bytes/MIME first)
"""

import argparse
import json
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_config() -> dict:
    """
    ARCHITECTURAL ISSUE: Duplicated code - this exact function exists in 6+ other scripts.
    PER REFACTORING PLAN: Should import from shared library (scripts/lib/common.py or src/config.py)
    that provides centralized, typed configuration access as the single source of truth.
    """
    config = {}
    config_path = Path("/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/config/paths.conf")
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"')
                    val = os.path.expandvars(val)
                    config[key.strip()] = val
        for _ in range(10):
            changed = False
            for key, val in list(config.items()):
                for k, v in config.items():
                    placeholder = f"${{{k}}}"
                    if placeholder in val:
                        val = val.replace(placeholder, v)
                        changed = True
                config[key] = val
            if not changed:
                break
    return config


def load_state(state_path: Path) -> dict:
    """
    ARCHITECTURAL ISSUE: Duplicated code - exists in scan_documents.py and others.
    PER REFACTORING PLAN: Should import atomic save/load functions from shared library.
    FURTHER ISSUE: This function doesn't use file locking, making it unsafe for concurrent access.
    The StateManager from state_manager.py provides proper locking and atomic operations.
    """
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}


def save_state(state: dict, state_path: Path) -> None:
    """
    ARCHITECTURAL ISSUE: Duplicated code and unsafe implementation.
    PER REFACTORING PLAN: Should use StateManager.atomic_save() from state_manager.py
    which provides file locking and atomic writes via os.replace().
    CURRENT ISSUE: No file locking (concurrent access unsafe) and not atomic 
    (can corrupt state on crash during write).
    """
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def file_hash(path: Path) -> str:
    """
    ARCHITECTURAL ISSUE: Duplicated code - exists in scan_documents.py and others.
    PER REFACTORING PLAN: Should import from shared library.
    NOTE: This is actually a good utility function that could be shared.
    """
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def write_log(log_file: Path, level: str, message: str) -> None:
    """
    ARCHITECTURAL ISSUE: Duplicated code - exists in 6+ other scripts.
    PER REFACTORING PLAN: Should import from shared library.
    NOTE: This follows the reusable logging pattern mentioned in README.md.
    """
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] [process_one_file] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def extract_text(path: Path) -> str:
    """
    ARCHITECTURAL NOTE: Delegates to unified extractor but this creates a subprocess.
    PER ARCHITECTURE V2: Should use Registry → Adapter → parser-utility boundary 
    returning ExtractionResult{ text, source_meta, status }.
    CURRENT LIMITATIONS: 
    - Only returns text, no extraction status (can't distinguish ok/empty/ocr_needed/corrupt/etc.)
    - Relies on extract_text.py which uses extension-only detection (should use magic bytes/MIME first)
    - Creates subprocess overhead instead of direct library calls
    SENIOR ARCHITECT REPORT: "Detection is by file suffix only, and .doc is routed to the modern 
    .docx parser. For a decade of legacy and mixed formats this will fail at scale and silently 
    discard real value. Against the documented target set (legacy and modern Office, RTF, Google 
    exports, PDF text vs scanned, PSD/AI/INDD metadata, HTML, CSV/JSON/XML, logs, images, audio, 
    video), this is a narrow slice. Critically, routing .doc (legacy binary OLE) to the modern 
    XML parser will fail on real files, and every failure currently collapses to an empty string 
    — indistinguishable from a genuinely empty document."
    """
    """Delegate to unified extractor supporting .txt, .md, .pdf, .docx."""
    import subprocess
    extractor = Path(__file__).with_name("extract_text.py")
    if extractor.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(extractor), str(path)],
                capture_output=True, text=True, timeout=60,
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


def build_prompt(text: str) -> str:
    """
    ARCHITECTURAL ISSUE: This prompt asks for shallow metadata instead of DecisionNote.
    PER NOTE QUALITY STANDARD: Should prompt for a DecisionNote with essence, why_it_matters, 
    key_points, keep_facts, business_area, project, people, organisations, topics, 
    possible_actions, answers_future_questions, source_relevance, value_score, scrap_score, 
    uncertainty, uncertainty_reason, fact_interpretation_boundary, discarded_summary, raw_excerpt.
    CURRENT PROMPT ONLY RETURNS: title, summary, tags, backlinks, value, confidence
    This is the central conflict identified in the Senior Architect Report - LLM used as 
    metadata stamper instead of reasoner.
    """
    """Build the strict Ollama prompt from the known-good template."""
    return (
        "You are an Obsidian metadata assistant. "
        "Return one raw JSON object only. No Markdown. No code fence. No explanation. "
        "Use lowercase kebab-case tags. "
        "Use Obsidian backlinks in [[Double Brackets]]. "
        "If no strong backlink exists, return an empty backlinks array. "
        "Set value as one of: throwaway, useful, permanent. "
        "Use confidence between 0 and 1. Do not use confidence 1 unless extremely certain. "
        "Prefer useful for working project notes unless the note is clearly disposable or foundational.\n\n"
        f'Text: "{text}"\n\n'
        'Return exactly this schema: '
        '{"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'
    )


def run_ollama(prompt: str, model: str, host: str) -> str:
    """
    ARCHITECTURAL NOTE: This function lacks resilience patterns.
    PER REFACTORING PLAN: Should use OllamaClient from ollama_client.py 
    which provides retry logic, circuit breaker, and structured logging.
    CURRENT ISSUES: 
    - No retry on Ollama failure (single failure kills the batch)
    - No circuit breaker (hammers Ollama if it's down)
    - No timeout handling beyond the subprocess timeout
    """
    """Send prompt to Ollama API and return raw response text."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    })
    try:
        result = subprocess.run(
            ["curl", "-sf", f"{host}/api/generate", "-d", payload],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return ""
        data = json.loads(result.stdout)
        return data.get("response", "")
    except Exception:
        return ""


def validate_metadata(raw: str) -> dict[str, Any] | None:
    """
    ARCHITECTURAL NOTE: This validation is for shallow metadata output.
    PER ARCHITECTURE V2 AND NOTE QUALITY STANDARD: Should validate against 
    DecisionNote schema instead of MetadataOutput.
    PER REFACTORING PLAN: Should use Pydantic models from models.py 
    (specifically DecisionNote) for stricter validation, clearer errors, 
    and type safety instead of hand-rolled validation.
    CURRENT VALIDATION ONLY CHECKS FOR: title, summary, tags, backlinks, value, confidence
    MISSING FIELDS FROM DECISIONNOTE: note_type, essence, why_it_matters, key_points, 
    keep_facts, business_area, project, people, organisations, topics, proposed_links, 
    possible_actions, answers_future_questions, source_relevance, value_score, scrap_score, 
    uncertainty, uncertainty_reason, fact_interpretation_boundary, discarded_summary, raw_excerpt
    """
    """Validate and clean the Ollama JSON response."""
    # Strip accidental Markdown fences and whitespace
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    required = ["title", "summary", "tags", "backlinks", "value", "confidence"]
    for field in required:
        if field not in data:
            return None

    if data["value"] not in {"throwaway", "useful", "permanent"}:
        return None

    try:
        conf = float(data["confidence"])
        if not (0 <= conf <= 1):
            return None
        data["confidence"] = conf
    except (TypeError, ValueError):
        return None

    if not isinstance(data["tags"], list):
        data["tags"] = []
    if not isinstance(data["backlinks"], list):
        data["backlinks"] = []

    return data


def write_sidecar(original: Path, metadata: dict[str, Any], sidecar_dir: Path, model: str) -> Path:
    """
    ARCHITECTURAL ISSUE: This creates shallow sidecar content instead of DecisionNote-based note.
    PER NOTE QUALITY STANDARD: Should compose a proper Obsidian note with:
    - YAML frontmatter containing structured properties (business_area, project, people, etc.)
    - Essence, summary, why_it_matters, key_points sections
    - Fact/interpretation boundary separation
    - Raw excerpt for trust
    - Proper note_type-based composition
    CURRENT ISSUES:
    - Creates JSON-style frontmatter (not native YAML, Dataview can't parse well)
    - Sidecar naming collision: invoice.pdf and invoice.docx both become invoice.ai.md
    - Only includes basic metadata, missing all DecisionNote fields
    - Does not separate fact from interpretation
    - No raw excerpt for trust anchor
    PER REFACTORING PLAN: Should use native YAML frontmatter and include all DecisionNote fields.
    """
    """Write the .ai.md sidecar file with YAML frontmatter."""
    sidecar_name = original.stem + ".ai.md"
    sidecar_path = sidecar_dir / sidecar_name

    # Deduplicate tags and backlinks
    tags = sorted(set(str(t) for t in metadata.get("tags", []) if t))
    backlinks = sorted(set(str(b) for b in metadata.get("backlinks", []) if b))

    # Ensure backlinks use Obsidian [[Double Brackets]]
    formatted_backlinks = []
    for bl in backlinks:
        if not bl.startswith("[["):
            bl = f"[[{bl}]]"
        if not bl.endswith("]]"):
            bl = bl + "]]"
        formatted_backlinks.append(bl)

    frontmatter = {
        "source_file": str(original),
        "source_type": original.suffix.lower().lstrip("."),
        "processed_at": datetime.now().isoformat(),
        "model": model,
        "status": "ai-generated-needs-review",
        "value": metadata.get("value", "unknown"),
        "confidence": metadata.get("confidence", 0.0),
        "tags": tags,
        "backlinks": formatted_backlinks,
    }

    yaml_lines = json.dumps(frontmatter, indent=2)
    # Convert JSON-style arrays to YAML list format for readability
    content = f"---\n{yaml_lines}\n---\n\n"
    content += f"# {metadata.get('title', original.stem)}\n\n"
    content += f"## Summary\n\n{metadata.get('summary', '')}\n\n"
    content += "## Why it matters\n\n"
    value = metadata.get("value", "unknown")
    if value == "throwaway":
        content += "This note appears disposable. Review before keeping.\n"
    elif value == "permanent":
        content += "This note appears foundational or reference-worthy.\n"
    else:
        content += "This note appears useful for active work.\n"
    content += f"\n## Source link\n\n[Open original file](file://{original})\n"

    sidecar_dir.mkdir(parents=True, exist_ok=True)
    with open(sidecar_path, "w", encoding="utf-8") as f:
        f.write(content)

    return sidecar_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Process one file through Ollama")
    parser.add_argument("file_path", help="Absolute path to the file to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    args = parser.parse_args()

    config = load_config()
    file_path = Path(args.file_path)
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    state_path = Path(config.get("STATE_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/state")) / "processed-files.json"
    sidecar_dir = Path(config.get("INGESTION_SIDECARS", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/sidecars"))
    model = config.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
    host = config.get("OLLAMA_HOST", "http://127.0.0.1:11434")

    write_log(log_file, "INFO", f"START Processing {file_path}")

    if not file_path.exists():
        write_log(log_file, "ERROR", f"File not found: {file_path}")
        sys.exit(1)

    # ARCHITECTURAL ISSUE: Lack of extraction status reporting
    # PER ARCHITECTURE V2: Extraction should return ExtractionResult{ text, source_meta, status }
    # where status ∈ {ok, empty, ocr_needed, corrupt, unsupported, metadata_only}
    # CURRENT ISSUE: extract_text() returns bare string, making it impossible to distinguish
    #               ok, empty, ocr_needed, corrupt, unsupported, and metadata_only
    #               This collapses six different operational realities into one, which makes
    #               the gate, the review queue, and trust-handling impossible to build correctly.
    # SENIOR ARCHITECT REPORT: "No extraction-status contract [...] This collapses six different 
    # operational realities into one, which makes the gate, the review queue, and trust-handling 
    # impossible to build correctly."
    # Extract text
    text = extract_text(file_path)
    if not text.strip():
        write_log(log_file, "WARN", f"Empty or unreadable file: {file_path}")
        sys.exit(0)

    # Truncate very long inputs (Ollama context limits)
    MAX_CHARS = 8000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n...[truncated]"
        write_log(log_file, "INFO", f"Text truncated to {MAX_CHARS} chars")

    # Build prompt
    prompt = build_prompt(text)

    # ARCHITECTURAL ISSUE: Missing deterministic gate before LLM processing
    # PER TRANSFORM-FIRST DESIGN: Should implement Stage 2 - Gate to determine if file is worth LLM processing
    # CURRENT FLOW: Extract text -> Immediately send to LLM (expensive operation)
    # REQUIRED FLOW: Extract text -> Gate (deterministic checks: empty, corrupt, OCR-needed, obvious scrap) -> 
    #              Only send to LLM if gate says "think"
    # SENIOR ARCHITECT REPORT: "Using the LLM's own confidence as the gate is architecturally backwards"
    # GATE SHOULD CHECK: min_meaningful_token_count, entropy_threshold, duplicate_similarity_threshold,
    #                   machine_export_detector, ocr_needed flag
    # Send to Ollama
    write_log(log_file, "INFO", f"Sending to model {model}...")
    raw_response = run_ollama(prompt, model, host)

    if not raw_response:
        write_log(log_file, "ERROR", "No response from Ollama")
        sys.exit(1)

    # Validate JSON
    metadata = validate_metadata(raw_response)
    if metadata is None:
        write_log(log_file, "ERROR", f"Invalid JSON response: {raw_response[:200]}...")
        sys.exit(1)

    write_log(log_file, "INFO", f"Valid metadata: title={metadata.get('title')}, value={metadata.get('value')}, confidence={metadata.get('confidence')}")

    if args.dry_run:
        write_log(log_file, "INFO", "Dry-run mode — sidecar not written")
        print(f"\nDry-run would create sidecar with:\n{json.dumps(metadata, indent=2)}")
        write_log(log_file, "INFO", "END Processing complete (dry-run)")
        return

    # Write sidecar
    sidecar_path = write_sidecar(file_path, metadata, sidecar_dir, model)
    write_log(log_file, "INFO", f"Sidecar written: {sidecar_path}")

    # ARCHITECTURAL ISSUE: State schema mismatch (LIVE DEFECT)
    # PER SENIOR ARCHITECT REPORT: "State schema split (active defect). The running runner and scanner 
    # read and write by_hash/by_path (scripts/runners/run-daily-ingest.sh:73, scripts/ingestion/scan_documents.py:77,147), 
    # while the persisted state file and the validated model use entries (state/processed-files.json:4, 
    # scripts/ingestion/models.py:163). The pipeline can silently fail to detect queued or already-processed files."
    # PER ARCHITECTURE V2: Should use single canonical state schema with entries structure
    # PER REFACTORING PLAN: Should use StateManager from state_manager.py as the only state access path
    # Update state
    state = load_state(state_path)
    state.setdefault("by_hash", {})
    state.setdefault("by_path", {})
    sha = file_hash(file_path)
    entry = {
        "source_path": str(file_path),
        "sha256": sha,
        "processed_at": datetime.now().isoformat(),
        "model": model,
        "sidecar_path": str(sidecar_path),
        "status": "processed",
        "value": metadata.get("value"),
        "confidence": metadata.get("confidence"),
    }
    state["by_hash"][sha] = entry
    state["by_path"][str(file_path)] = sha
    save_state(state, state_path)
    write_log(log_file, "INFO", "State updated")

    write_log(log_file, "INFO", "END Processing complete")


if __name__ == "__main__":
    main()
