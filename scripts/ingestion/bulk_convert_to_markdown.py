#!/usr/bin/env python3
"""
bulk_convert_to_markdown.py
Purpose: Convert .txt, .pdf, .docx files to .md in a staging folder.
         Originals are never modified or moved. A companion .md is created
         beside the original (in the vault or staging area) for AI processing.
Usage:
    python3 scripts/ingestion/bulk_convert_to_markdown.py <source_folder> [--dry-run] [--output-folder <dir>]
Output: .md files in output folder; logs/ingestion.log
Risk: writes-report (creates .md, does not modify originals)
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


def load_config() -> dict:
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


def write_log(log_file: Path, level: str, message: str) -> None:
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] [bulk_convert] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def sanitize_filename(name: str) -> str:
    """Create a clean Markdown filename from a PDF/DOCX name."""
    base = Path(name).stem
    # Replace spaces with dashes, remove weird chars
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"[^A-Za-z0-9._-]", "", base)
    base = base.strip("-._")
    return base + ".md"


def convert_file(source: Path, output_dir: Path, log_file: Path) -> Path | None:
    """Convert a single file to Markdown. Returns output path or None."""
    ext = source.suffix.lower()

    # Import unified extractor inline to avoid coupling
    sys_path = str(Path(__file__).parent)
    if sys_path not in os.sys.path:
        os.sys.path.insert(0, sys_path)
    from extract_text import extract_text

    text = extract_text(source)
    if not text.strip():
        write_log(log_file, "WARN", f"No text extracted: {source}")
        return None

    md_name = sanitize_filename(source.name)
    output_path = output_dir / md_name

    # Build Markdown with source reference
    md_content = f"""---
source_file: "{source}"
source_type: "{ext.lstrip('.')}"
converted_at: "{datetime.now().isoformat()}"
status: "converted-needs-processing"
---

# {Path(source).stem}

## Extracted Content

{text}

## Source Reference

[Open original file](file://{source})
"""

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    write_log(log_file, "INFO", f"Converted: {source.name} -> {md_name}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk convert documents to Markdown")
    parser.add_argument("source_folder", help="Folder containing .txt, .pdf, .docx files")
    parser.add_argument("--output-folder", help="Where to write .md files")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--exts", default=".txt,.pdf,.docx,.doc", help="Comma-separated extensions")
    args = parser.parse_args()

    config = load_config()
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    output_dir = Path(args.output_folder) if args.output_folder else Path(config.get("INGESTION_INCOMING", "/home/mpc/Documents/LinuxBox-Vault/automation-scripts/imported-text-files"))
    source = Path(args.source_folder)

    write_log(log_file, "INFO", f"START Bulk conversion: {source} -> {output_dir}")

    if not source.exists():
        write_log(log_file, "ERROR", f"Source folder not found: {source}")
        return

    extensions = {e.strip().lower() for e in args.exts.split(",")}
    files = [p for p in sorted(source.rglob("*")) if p.is_file() and p.suffix.lower() in extensions]

    write_log(log_file, "INFO", f"Found {len(files)} files to convert")

    converted = 0
    for f in files:
        if args.dry_run:
            md_name = sanitize_filename(f.name)
            print(f"  Would convert: {f} -> {output_dir / md_name}")
            converted += 1
            continue

        result = convert_file(f, output_dir, log_file)
        if result:
            converted += 1

    write_log(log_file, "INFO", f"Converted {converted}/{len(files)} files")
    write_log(log_file, "INFO", "END Bulk conversion complete")


if __name__ == "__main__":
    main()
