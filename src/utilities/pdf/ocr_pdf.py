"""
Utility: OCR PDF extraction.

Purpose:
Extract text from scanned/image-only PDFs after the system explicitly identifies OCR is needed.

Expected library:
pytesseract, pdf2image, and Pillow

Pipeline role:
Used by PdfAdapter during Stage 1 Extract for OCR-specific sources after the golden path supports OCR.

Status:
Placeholder only. Not wired into the orchestrator yet.
"""
