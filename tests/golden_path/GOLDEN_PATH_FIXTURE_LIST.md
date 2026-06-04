# Golden Path Fixture List

**Purpose:** Define the trusted sample set that proves the transform-first architecture before broad implementation.  
**Target pipeline:** Extract -> Gate -> Think/Transform -> Compose -> Place/Record.

Do not create fake binary fixtures unless explicitly requested. Markdown and text fixtures may be simple, human-readable examples.

## Fixture Table

| ID | Fixture | Purpose | Pipeline Stages Tested | Pass Condition | Hard Fail Condition |
|---|---|---|---|---|---|
| GP-001 | Simple markdown note | Prove existing Obsidian-style text can be processed without being damaged. | Extract, Gate, Think/Transform, Compose, Place/Record | Clean text extracted, provenance kept, useful `DecisionNote` created, output does not over-transform. | Source structure is damaged, provenance missing, or output becomes shallow metadata only. |
| GP-002 | Plain text scrap | Prove the gate can distinguish meaningful scraps from junk. | Extract, Gate | Meaningful content routes to think/review; obvious junk avoids heavy LLM reasoning. | Empty/noisy text is sent confidently to LLM and becomes polished fake-useful output. |
| GP-003 | Text PDF | Prove normal PDF text extraction works. | Extract, Gate, Think/Transform, Compose | Text extracts as `status=ok`; title, dates, names, and key facts are preserved. | Text PDF is marked `ocr_needed` incorrectly or extraction failure becomes empty text. |
| GP-004 | Scanned/image PDF | Prove OCR-needed documents are detected safely. | Extract, Gate, Place/Record review path | Extraction returns `status=ocr_needed`; item routes to review/ocr queue with source path/hash. | Failed extraction is treated as scrap, empty, or low-value archive. |
| GP-005 | Modern Word `.docx` | Prove modern Word extraction uses the right parser. | Extract, Gate, Think/Transform | `python-docx` path extracts headings/body and preserves important facts. | `.docx` is unsupported without explanation or loses important text silently. |
| GP-006 | Legacy Word `.doc` | Prove legacy Word is not treated as modern Word. | Extract, Gate | `.doc` is detected as legacy/OLE and returns honest `ok`, `unsupported`, `corrupt`, or `metadata_only`. | `.doc` is sent to `python-docx` or silently returns empty text. |
| GP-007 | Modern Excel `.xlsx` | Prove spreadsheet extraction summarises useful structure rather than dumping tables. | Extract, Gate, Think/Transform, Compose | Sheet names, visible tables, and key figures are summarised; type such as invoice/budget/quote is identified when obvious. | Output is unreadable table dump or loses key figures. |
| GP-008 | Legacy Excel `.xls` | Prove legacy Excel is treated separately from modern Excel. | Extract, Gate | `.xls` is detected as legacy spreadsheet and returns honest status with provenance. | `.xls` is sent to `openpyxl` or extraction failure is hidden. |
| GP-009 | Project Studios business file | Prove Project Studios business-area classification and useful retrieval fields. | Extract, Gate, Think/Transform, Compose | `business_area` includes Project Studios; actions/future questions are specific to SEO, PPC, web design, WordPress, lead generation, client work, or strategy. | Business area is missing or actions/questions are generic. |
| GP-010 | Super Clean business file | Prove operational details survive transformation. | Extract, Gate, Think/Transform, Compose | `business_area` includes Super Clean Services; prices, dates, customer names, job details, obligations, invoices, and marketing facts are preserved when present. | Operational record is reduced to vague summary. |
| GP-011 | How-to technical note | Prove procedural knowledge is recognised and preserved. | Extract, Gate, Think/Transform, Compose | `note_type` is how-to; steps, commands, warnings, gotchas, and verification are preserved exactly. | Commands are rewritten incorrectly or procedural steps are lost. |
| GP-012 | Junk/log/export | Prove garbage does not become polished garbage. | Extract, Gate, optional Think/Transform, Place/Record review path | High scrap/low value or review routing; no confident over-summary. | Junk/log/export becomes a polished, confident, fake-useful note. |

## Expected Artefacts Per Fixture

Each fixture should eventually produce:

1. `ExtractionResult` JSON.
2. `GateDecision` JSON.
3. `DecisionNote` JSON when `GateDecision.outcome=think`.
4. Composed Obsidian Markdown note when a note is warranted.
5. State/review record showing where the item went and why.
6. A row in `tests/golden_path/reports/golden-path-review-report.md`.

## Immediate Fixture Priority

Start with simple readable sources before binary formats:

1. GP-001 simple markdown note.
2. GP-002 plain text scrap.
3. GP-009 Project Studios business file.
4. GP-010 Super Clean business file.
5. GP-011 how-to technical note.
6. GP-012 junk/log/export.

Only after those prove useful `DecisionNote` output should PDF, Office, OCR, and spreadsheet breadth become active implementation work.
