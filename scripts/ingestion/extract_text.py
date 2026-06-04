#!/usr/bin/env python3
# ARCHITECTURE NOTE:
# This file belongs to the legacy filing/tagging-first pipeline.
# Do not extend this as the authority for the new transform-first pipeline.
# See docs/debt/ARCHITECTURAL_DEBT_MAP.md.
"""
extract_text.py
Purpose: Unified text extractor for .txt, .md, .pdf, .docx files.
Usage:
    python3 scripts/ingestion/extract_text.py <file_path>
    # Returns plain text on stdout, empty string on failure
Risk: read-only
"""

import sys
from pathlib import Path


def extract_from_txt(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def extract_from_md(path: Path) -> str:
    return extract_from_txt(path)


def extract_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n\n".join(parts)
    except Exception:
        return ""


def extract_from_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(str(path))
        parts = []
        for para in doc.paragraphs:
            if para.text:
                parts.append(para.text)
        return "\n".join(parts)
    except Exception:
        return ""


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    extractors = {
        ".txt": extract_from_txt,
        ".md": extract_from_md,
        ".pdf": extract_from_pdf,
        ".docx": extract_from_docx,
        ".doc": extract_from_docx,
    }
    fn = extractors.get(ext)
    if fn is None:
        return ""
    return fn(path)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: extract_text.py <file_path>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    text = extract_text(path)
    print(text)


if __name__ == "__main__":
    main()
