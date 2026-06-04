"""
Utility: PDF classifier.

Purpose:
Classify PDFs as text-bearing, scanned/image-only, corrupt, unsupported, or metadata-only before extraction.

Expected library:
pymupdf and/or pdfplumber for inspection; OCR libraries later only when needed.

Pipeline role:
Used by PdfAdapter during Stage 1 Extract to prevent silent empty extraction and route OCR-needed files honestly.

Status:
Placeholder only. Not wired into the orchestrator yet.
"""
