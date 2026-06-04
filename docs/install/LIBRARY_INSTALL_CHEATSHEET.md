# Library Install Cheatsheet

This project should install dependencies in layers. Do not install every heavy OCR/media dependency on day one.

## Phase 1: Core Now

Use `requirements-core.txt` for the immediate contracts-first work:

- `pydantic` for `ExtractionResult`, `GateDecision`, `DecisionNote`, and `StateEntry` contracts.
- `filelock` for safe canonical state writes.
- `python-frontmatter` and `PyYAML` for Obsidian Markdown frontmatter.
- `requests` for local Ollama HTTP calls.
- `tenacity` for retry boundaries.
- `python-magic` for MIME/magic-byte detection.
- `charset-normalizer` for messy text encodings.
- `pytest` for golden path and contract tests.

Install only when needed, for example:

```bash
python -m pip install -r requirements-core.txt
```

## Phase 2: Document Extraction Later

Use `requirements-documents.txt` after the core contracts and golden path fixture tests exist:

- `python-docx` for modern `.docx`.
- `olefile` for legacy OLE detection in `.doc`, `.xls`, and `.ppt`.
- `striprtf` for `.rtf`.
- `openpyxl` for modern `.xlsx` / `.xlsm`.
- `xlrd` for legacy `.xls`.
- `python-pptx` for modern `.pptx`.
- `pymupdf` and `pdfplumber` for PDF text/layout extraction.
- `beautifulsoup4` and `lxml` for HTML/XML.
- `pandas` for tabular previews and spreadsheet summaries.

## Phase 3: OCR / Media Later

Use `requirements-ocr-media.txt` only after the transform-first golden path is proven:

- `pytesseract`, `pdf2image`, and `Pillow` for OCR/image work.
- `faster-whisper` and `ffmpeg-python` for local transcription/media handling.
- `psd-tools` for PSD metadata/layer inspection.

These are intentionally blocked for now as broad feature work.

## Fedora System Dependencies

Likely system packages:

```bash
sudo dnf install file file-libs
```

OCR later:

```bash
sudo dnf install tesseract tesseract-langpack-eng poppler-utils
```

Media later:

```bash
sudo dnf install ffmpeg
```

Optional metadata tools:

```bash
sudo dnf install perl-Image-ExifTool
```

Optional Office conversion fallback:

```bash
sudo dnf install libreoffice
```

## Rule

Do not install anything automatically from scripts. Dependency installation should remain a deliberate human action until the golden path is proven.
