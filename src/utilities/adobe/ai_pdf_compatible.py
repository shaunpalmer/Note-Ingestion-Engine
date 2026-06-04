"""
Utility: Adobe Illustrator PDF-compatible extraction.

Purpose:
Inspect Illustrator files that contain PDF-compatible data and extract metadata or embedded readable text when available.

Expected library:
pymupdf/pdfplumber for PDF-compatible content; optional ExifTool for metadata.

Pipeline role:
Used by AdobeAdapter during Stage 1 Extract for .ai sources after core document flows are proven.

Status:
Placeholder only. Not wired into the orchestrator yet.
"""
