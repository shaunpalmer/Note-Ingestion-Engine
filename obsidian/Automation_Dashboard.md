## Today’s Network Status
## Notes Processed
## New Sidecar Files
## Storage Rig Status
## Tailscale Status
## Errors To Review
## Next Safe Action


👸🏻: Recommended save: create a note called Automation Roadmap — Obsidian, Ollama, Network, Side Rigs and paste this in as the first strategy document. Next step: build the first tiny Python script for one test note → Ollama → validated JSON → sidecar Markdown, yeah?


failover-monitor.sh
File
Here was one of the first scripts I ever did coming to Linux. It has been a game changer because I had flaky Wi-Fi with 200 people on that free Wi-Fi. Sometimes it's good and sometimes it's not. So, and then I had a paid one which I used less frequently, but still great for a backup. Yeah, so here's the automation, the very first one I did.
MACHINE_IDENTITIES.md
File
NETWORK_TEST_LOG.md
File
README.md
File
setup-shared-folders.sh
File
setup-share-user.sh
File
test-share-access.sh
File
This is the updated version because I, you know, I had to start somewhere, right? So these are the ones that identified the network, there were tests, and it works. It doesn't flip-flop. Yeah, read the code, you will see what I'm talking about. And this was the next bit that I did.
bulk-rename-txt-to-md-canvas.md
File
Here's another useful script that I built the other day. I should have got you in on it earlier, but this is a project that's still in the making. Hey, what do you think of this idea? I'm pretty sure we can expand this one too. You might want to add this to your memories.
Updated memory
Thought for a few seconds

👸🏻: Yes, Shaun — this is a very useful idea, and I’ve added the core pattern to memory.

👨🏻: What you built is a bulk file-conversion automation for cleaning up old notes before bringing them into Obsidian. The command targets a nested folder structure, finds every .txt file recursively, and renames it to .md, including inside dated subfolders. The key command uses find with a quoted path so Linux handles the space in GPT -save properly.

📖: The reason this is worth expanding is simple: it sits right before your Obsidian/Ollama workflow.

Your pipeline becomes:

old GPT .txt notes
→ bulk rename to .md
→ Obsidian-readable notes
→ Ollama metadata pass
→ sidecar .ai.md files
→ reviewed knowledge vault

👨🏻: I like the idea because it is practical, low-risk, and very “Automate the Boring Stuff” in spirit. The automation cheat sheet you uploaded also points in this same direction: Python’s pathlib is specifically useful for file/folder work like listing folders, checking files, renaming files, reading suffixes, and creating directories.

🛠️: How I’d expand this next:

v1: raw find command
v2: dry-run mode
v3: write a log file
v4: skip files that already have matching .md names
v5: create backup list before renaming
v6: Python pathlib version
v7: Obsidian cleanup script
v8: Ollama metadata sidecar generator

📌: The biggest improvement is dry-run first. Before renaming anything, the script should show:

Found 342 .txt files
Would rename:
old-note.txt → old-note.md
folder/example.txt → folder/example.md
No files changed yet

Then you run it again with something like:

--apply

That keeps it safe. No “oops, I renamed half the universe” moment. 😄

👸🏻: My recommendation: this becomes your next official module:

Module: Bulk TXT to Markdown Converter
Risk level: Medium
Purpose: Prepare old text notes for Obsidian
Current status: Proven command pattern
Next version: Python script with dry-run + logging

👨🏻: Next step: we turn this into a proper Python script using pathlib, with --dry-run as the default and --apply required before it touches files.

Worked for 49 seconds

👸🏻: It makes sense to let scripts and AI do the heavy lifting rather than you wading through 30 000 files on your own. A daily “ingestion script” could crawl your documents folder, convert a handful of files to Markdown, send the text through your Llama model to judge relevance, extract key points and tags, add any back‑links and Obsidian‑style front‑matter, and then copy both the original and the processed note into your vault. Over time, that daily trickle turns into a complete archive, and the script can alert you when it finishes its queue. The book we discussed earlier already covers practical tasks like copying, moving, renaming, compressing files, scraping information from documents, and sending emails, plus it introduces modules such as pathlib for filesystem work and EZGmail for interacting with Gmail. Those chapters will be useful when we start coding your automation.

📖: On the Gmail side, you could set up a separate script that reads a spreadsheet or database of your contacts, filters them by age (e.g., anything older than five years gets re‑engagement messages), and sends templated “we miss you” or “haven’t heard from you” emails through the Gmail API. The book’s updated edition includes a section on the EZGmail module, which simplifies sending emails directly from Python and would dovetail nicely with your lead‑generation plans. To avoid spamming people or burning your domains, we can schedule those messages, randomise send times, and track responses to refine future campaigns.

🛠️: My suggestion is to tackle this in phases: (1) build the Obsidian ingestion script with daily scheduling and progress tracking; (2) add Llama‑powered relevance scoring, tagging, and back‑link insertion; (3) design the Gmail outreach workflow with age‑based segmentation, personalised templates, and API integration; and (4) use a simple job scheduler (like cron) to run each piece at appropriate intervals. Shall we start drafting the first phase—the daily note‑ingestion script—and identify the exact metadata fields and tag logic you’d like to use?

automate the boring stuff with python automate the boring stuff with python ( PDFDrive ).pdf
PDF
Well, first of all, we're going to write a description and a PR and things that'll need to be done. Do you know enough of the kinds of scripts? And the other thing you could probably do is, somewhere on my machine, I've got, hang on, somewhere I've got, I've actually got this already on my machine, the PDF.Look, I even managed to track down the copy of the book, so uh feel free to browse and come up with some plans. Anyway, we definitely need to make a plan for automating through my documents, but if we just did the documents first and then perhaps we can do the video library later on. Um but Obsidian, I thought we need to make a file, so you can describe the video and then you include the link to where it is in the folder or something. I'm not sure, but so you can just go straight to it after you've searched the document, a link, a backlink, and we talked about what sort of format this should be in. So yeah, there's plenty of scope and plenty of growth for this kind of script. Everything I've tried so far, it eventually worked out.
Thought for 8s

👸🏻: Yes, Shaun — I know enough now to write the first project description, PR description, and task list for this automation work.

The big idea is clear:

Build a safe, slow, accumulative automation system that processes your document library into Obsidian over time, using Python scripts plus local Ollama models. It starts with documents only. Videos come later as a second phase.

The Automate the Boring Stuff with Python book fits this perfectly. Its automation section covers reading/writing files, organising files, regex, PDFs and Word documents, CSV/JSON, scheduling tasks, email/text messages, and GUI automation — basically the exact family of scripts you’re now building around Obsidian and local AI.

Your local setup is also already pointing in the right direction. Ollama is installed on Fedora, with models like mistral, qwen2.5:7b, qwen2.5-coder:7b, and llama3.1:8b, and the stated goal is note summaries, tags, backlinks, file descriptions, sidecar Markdown notes, and cron-style automation.

📖: I’d write the first PR like this:

PR Title
Add roadmap for Obsidian document ingestion automation
PR Description

This PR defines the first safe build phase for the local Obsidian automation system.

The goal is to process a large document library gradually, without damaging or moving original files. The first version will scan selected document folders, process a small number of files per run, create Markdown sidecar notes, and use a local Ollama model to generate summaries, tags, backlinks, usefulness scores, and review metadata.

This project follows the same safe automation pattern already proven in the local Linux scripts:

observe first
log clearly
process slowly
do not modify originals
write sidecar output
review before scaling

The first phase focuses on documents only. Video library automation will be added later, once the document workflow is proven.

Why this matters

Shaun has a large archive of documents and notes that would take too long to sort manually. Processing a few files per day creates compound progress. Over time, the archive becomes searchable, tagged, linked, and usable inside Obsidian.

This is not a one-off file conversion script. It is the beginning of a local knowledge-ingestion pipeline.

First Build Scope

The first version should:

scan one source folder
select a small batch of files
copy or convert supported files to Markdown
send extracted text to Ollama
validate the AI response
write a .ai.md sidecar note
record progress in a local state file
log every action
avoid moving or deleting originals

The first supported file types should be simple:

.txt
.md
.pdf
.docx later

PDF and Word support can be added carefully after the text/Markdown flow is stable. The book’s table of contents confirms PDF and Word automation is a natural later chapter-level expansion.

Suggested Sidecar Format

For a document called:

example-file.pdf

The script should create something like:

example-file.ai.md

Suggested content:

---
source_file: "/original/path/example-file.pdf"
source_type: "pdf"
processed_at: "2026-05-25T00:00:00+12:00"
model: "qwen2.5-coder:7b"
status: "processed"
value: "useful"
confidence: 0.82
tags:
  - python
  - automation
  - obsidian
backlinks:
  - "[[Python Automation]]"
  - "[[Obsidian Vault]]"
---

# Example File

## Summary

Short plain-English summary here.

## Why it matters

Reason this file is useful, permanent, or throwaway.

## Source link

[Open original file](file:///original/path/example-file.pdf)
Acceptance Criteria

This PR is complete when:

roadmap document exists
initial folder structure is defined
metadata schema is documented
sidecar format is documented
first script boundaries are clear
risk rules are written down
video automation is explicitly deferred
Out of Scope For This PR
bulk processing all 30,000 documents
renaming original files
moving original files
deleting files
email automation
video transcription
automatic customer outreach
Risk Rules

The first script must not rename, move, delete, or overwrite originals.

The first script should process only one file, or a tiny batch, until the output is trusted.

The first script should default to dry-run mode.

The first script should write logs.

The first script should keep a state file so it knows what has already been processed.

👨🏻: The task list I’d put under this PR is:

1. Create project folder
2. Create README.md
3. Create ROADMAP.md
4. Create SCHEMA.md
5. Create sample sidecar .ai.md file
6. Create first dry-run scanner script
7. Add local config file
8. Add processing log
9. Add state file
10. Test with one document only

Suggested folder structure:

obsidian-automation/
  README.md
  ROADMAP.md
  SCHEMA.md
  examples/
    sample-source-note.md
    sample-source-note.ai.md
  scripts/
    scan_documents.py
    process_one_file.py
  config/
    config.example.json
  logs/
    .gitkeep
  state/
    .gitkeep

🛠️: My recommendation for the first actual script is not the Ollama one yet.

First script should be:

scan_documents.py

Its job:

look through a folder
find candidate files
skip files already processed
print the next 5 files it would process
write nothing unless --apply is used

Then the second script becomes:

process_one_file.py

Its job:

read one file
extract text
send to Ollama
validate JSON
write .ai.md sidecar
log result

That keeps the beast on a leash. No “30,000 file stampede through the vault” on day one. 😄

For the later video phase, yes: I’d make a Markdown file per video. It would describe the video, store the original file path, maybe include duration/size/date, and later include transcript or AI summary. Something like:

video-name.video.md

With:

---
source_file: "/srv/shared/media/videos/example.mp4"
media_type: "video"
status: "not-transcribed"
tags:
  - video-library
  - training
---

# Video Name

## Description

Short description here.

## Source

[Open video](file:///srv/shared/media/videos/example.mp4)

👸🏻: Reasoned next step: save this as ROADMAP.md or PR-001-document-ingestion-roadmap.md, then we write the first dry-run scanner script.

Well, I was thinking something like 50 a day. Perhaps we do all the, all the text files first, and then perhaps we get on to other files like, like docs files. If then they had 50 a day, um, you might run out of files one a week. I'm not sure. But it depends how fast you want to run it. If, if you start running into problems, and I, 50 is not that bad um to run, you know, I'm pretty sure a script and a large language model will handle 50, and within a short period of time, you'll probably get through all the text files. Time you run the standard texts and, uh, what do they call them, like, uh, like the summary.{
  "title":"moving files testing tailscale ai tagging backlinks",
  "summary":"Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.",
  "tags":["files","tailscale","ai","tagging","backlinks"],
  "backlinks":[],
  "value":"useful",
  "confidence":0.8
}
Thought for a few seconds

👸🏻: Yes — 50 a day is a sensible first production target, especially if we start with plain text and Markdown files.

👨🏻: I’d treat it like this:

Start with:

.txt
.md

Then later add:

.pdf
.docx
.odt
.html
.csv

That matches the boring-but-powerful automation path from Automate the Boring Stuff: reading/writing files, organising files, regex, CSV/JSON, PDFs/Word, scheduling tasks, and later email/text automation.

Your JSON example is exactly the right shape for the first metadata model:

{
  "title": "moving files testing tailscale ai tagging backlinks",
  "summary": "Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.",
  "tags": ["files", "tailscale", "ai", "tagging", "backlinks"],
  "backlinks": [],
  "value": "useful",
  "confidence": 0.8
}

That should become the required schema for the first Obsidian ingestion script.

📖: I’d update the roadmap like this:

Processing strategy

First phase:

Process 50 text/markdown files per day.
Do not move originals.
Do not delete originals.
Do not overwrite existing sidecars.
Log every processed file.
Keep a state database or JSON file.
Resume where it left off.

The daily run should create sidecar notes like:

original-file.ai.md

Or, if we decide to copy cleaned files into Obsidian:

original-file.md
original-file.ai.md
Daily batch logic

The script should:

1. Scan source folders.
2. Find unprocessed .txt and .md files.
3. Select the next 50.
4. Read each file safely.
5. Send content to qwen2.5-coder:7b or qwen2.5:7b.
6. Validate JSON.
7. Write sidecar Markdown.
8. Mark file as processed.
9. Write a daily report.

Your Ollama notes already show this is the intended local AI direction: note summaries, tags, backlinks, file descriptions, sidecar Markdown notes, and cron-style automation.

State tracking

I would not rely on filename alone. I’d use a state file like:

state/processed-files.json

Each entry should store:

{
  "source_path": "/home/mpc/Documents/example.txt",
  "sha256": "file-hash-here",
  "processed_at": "2026-05-25T04:00:00+12:00",
  "model": "qwen2.5-coder:7b",
  "sidecar_path": "/home/mpc/Documents/example.ai.md",
  "status": "processed"
}

That way, if a file moves later, we still have a fingerprint.

Daily report

Each run should create:

logs/2026-05-25-ingestion-report.md

With:

# Daily Ingestion Report — 2026-05-25

Processed: 50
Successful: 48
Failed: 2
Skipped: 0
Model: qwen2.5-coder:7b

## Useful
- [[moving files testing tailscale ai tagging backlinks]]

## Failed
- broken-file.txt — JSON validation failed
- weird-encoding.txt — could not read file

This gives you an Obsidian-readable audit trail. Very important. Otherwise six weeks later you’ll be staring at the vault going, “Who touched this? Was it me? Was it the robot? Was it Tuesday?” 😄

👨🏻: My recommendation for the first PR task list becomes:

PR-001: Document ingestion roadmap
PR-002: Dry-run scanner for .txt and .md files
PR-003: Process one file through Ollama
PR-004: Batch process 50 files per day
PR-005: Add cron/systemd timer
PR-006: Add PDF/docx support
PR-007: Add video sidecar metadata

For the first actual script, I’d call it:

obsidian_daily_ingest.py

But internally split it into functions:

scan_candidates()
load_state()
pick_batch(limit=50)
extract_text()
run_ollama()
validate_json()
write_sidecar()
update_state()
write_daily_report()

📌: The key decision I’d lock in now:

Daily limit: 50 files
First file types: .txt and .md
Model: qwen2.5-coder:7b
Output: .ai.md sidecar
Originals: untouched
Default mode: dry-run
Apply mode: explicit --apply

👸🏻: Recommended save: add this as PR-002 — Daily Text File Ingestion Plan, then next we can write the first obsidian_daily_ingest.py skeleton with --dry-run, --limit 50, and schema validation.

failover-monitor.sh
File
Here was one of the first scripts I ever did coming to Linux. It has been a game changer because I had flaky Wi-Fi with 200 people on that free Wi-Fi. Sometimes it's good and sometimes it's not. So, and then I had a paid one which I used less frequently, but still great for a backup. Yeah, so here's the automation, the very first one I did.
MACHINE_IDENTITIES.md
File
NETWORK_TEST_LOG.md
File
README.md
File
setup-shared-folders.sh
File
setup-share-user.sh
File
test-share-access.sh
File
This is the updated version because I, you know, I had to start somewhere, right? So these are the ones that identified the network, there were tests, and it works. It doesn't flip-flop. Yeah, read the code, you will see what I'm talking about. And this was the next bit that I did.
bulk-rename-txt-to-md-canvas.md
File
Here's another useful script that I built the other day. I should have got you in on it earlier, but this is a project that's still in the making. Hey, what do you think of this idea? I'm pretty sure we can expand this one too. You might want to add this to your memories.
Updated memory
Thought for a few seconds

👸🏻: Yes, Shaun — this is a very useful idea, and I’ve added the core pattern to memory.

👨🏻: What you built is a bulk file-conversion automation for cleaning up old notes before bringing them into Obsidian. The command targets a nested folder structure, finds every .txt file recursively, and renames it to .md, including inside dated subfolders. The key command uses find with a quoted path so Linux handles the space in GPT -save properly.

📖: The reason this is worth expanding is simple: it sits right before your Obsidian/Ollama workflow.

Your pipeline becomes:

old GPT .txt notes
→ bulk rename to .md
→ Obsidian-readable notes
→ Ollama metadata pass
→ sidecar .ai.md files
→ reviewed knowledge vault

👨🏻: I like the idea because it is practical, low-risk, and very “Automate the Boring Stuff” in spirit. The automation cheat sheet you uploaded also points in this same direction: Python’s pathlib is specifically useful for file/folder work like listing folders, checking files, renaming files, reading suffixes, and creating directories.

🛠️: How I’d expand this next:

v1: raw find command
v2: dry-run mode
v3: write a log file
v4: skip files that already have matching .md names
v5: create backup list before renaming
v6: Python pathlib version
v7: Obsidian cleanup script
v8: Ollama metadata sidecar generator

📌: The biggest improvement is dry-run first. Before renaming anything, the script should show:

Found 342 .txt files
Would rename:
old-note.txt → old-note.md
folder/example.txt → folder/example.md
No files changed yet

Then you run it again with something like:

--apply

That keeps it safe. No “oops, I renamed half the universe” moment. 😄

👸🏻: My recommendation: this becomes your next official module:

Module: Bulk TXT to Markdown Converter
Risk level: Medium
Purpose: Prepare old text notes for Obsidian
Current status: Proven command pattern
Next version: Python script with dry-run + logging

👨🏻: Next step: we turn this into a proper Python script using pathlib, with --dry-run as the default and --apply required before it touches files.

Worked for 49 seconds

👸🏻: It makes sense to let scripts and AI do the heavy lifting rather than you wading through 30 000 files on your own. A daily “ingestion script” could crawl your documents folder, convert a handful of files to Markdown, send the text through your Llama model to judge relevance, extract key points and tags, add any back‑links and Obsidian‑style front‑matter, and then copy both the original and the processed note into your vault. Over time, that daily trickle turns into a complete archive, and the script can alert you when it finishes its queue. The book we discussed earlier already covers practical tasks like copying, moving, renaming, compressing files, scraping information from documents, and sending emails, plus it introduces modules such as pathlib for filesystem work and EZGmail for interacting with Gmail. Those chapters will be useful when we start coding your automation.

📖: On the Gmail side, you could set up a separate script that reads a spreadsheet or database of your contacts, filters them by age (e.g., anything older than five years gets re‑engagement messages), and sends templated “we miss you” or “haven’t heard from you” emails through the Gmail API. The book’s updated edition includes a section on the EZGmail module, which simplifies sending emails directly from Python and would dovetail nicely with your lead‑generation plans. To avoid spamming people or burning your domains, we can schedule those messages, randomise send times, and track responses to refine future campaigns.

🛠️: My suggestion is to tackle this in phases: (1) build the Obsidian ingestion script with daily scheduling and progress tracking; (2) add Llama‑powered relevance scoring, tagging, and back‑link insertion; (3) design the Gmail outreach workflow with age‑based segmentation, personalised templates, and API integration; and (4) use a simple job scheduler (like cron) to run each piece at appropriate intervals. Shall we start drafting the first phase—the daily note‑ingestion script—and identify the exact metadata fields and tag logic you’d like to use?

automate the boring stuff with python automate the boring stuff with python ( PDFDrive ).pdf
PDF
Well, first of all, we're going to write a description and a PR and things that'll need to be done. Do you know enough of the kinds of scripts? And the other thing you could probably do is, somewhere on my machine, I've got, hang on, somewhere I've got, I've actually got this already on my machine, the PDF.Look, I even managed to track down the copy of the book, so uh feel free to browse and come up with some plans. Anyway, we definitely need to make a plan for automating through my documents, but if we just did the documents first and then perhaps we can do the video library later on. Um but Obsidian, I thought we need to make a file, so you can describe the video and then you include the link to where it is in the folder or something. I'm not sure, but so you can just go straight to it after you've searched the document, a link, a backlink, and we talked about what sort of format this should be in. So yeah, there's plenty of scope and plenty of growth for this kind of script. Everything I've tried so far, it eventually worked out.
Thought for 8s

👸🏻: Yes, Shaun — I know enough now to write the first project description, PR description, and task list for this automation work.

The big idea is clear:

Build a safe, slow, accumulative automation system that processes your document library into Obsidian over time, using Python scripts plus local Ollama models. It starts with documents only. Videos come later as a second phase.

The Automate the Boring Stuff with Python book fits this perfectly. Its automation section covers reading/writing files, organising files, regex, PDFs and Word documents, CSV/JSON, scheduling tasks, email/text messages, and GUI automation — basically the exact family of scripts you’re now building around Obsidian and local AI.

Your local setup is also already pointing in the right direction. Ollama is installed on Fedora, with models like mistral, qwen2.5:7b, qwen2.5-coder:7b, and llama3.1:8b, and the stated goal is note summaries, tags, backlinks, file descriptions, sidecar Markdown notes, and cron-style automation.

📖: I’d write the first PR like this:

PR Title
Add roadmap for Obsidian document ingestion automation
PR Description

This PR defines the first safe build phase for the local Obsidian automation system.

The goal is to process a large document library gradually, without damaging or moving original files. The first version will scan selected document folders, process a small number of files per run, create Markdown sidecar notes, and use a local Ollama model to generate summaries, tags, backlinks, usefulness scores, and review metadata.

This project follows the same safe automation pattern already proven in the local Linux scripts:

observe first
log clearly
process slowly
do not modify originals
write sidecar output
review before scaling

The first phase focuses on documents only. Video library automation will be added later, once the document workflow is proven.

Why this matters

Shaun has a large archive of documents and notes that would take too long to sort manually. Processing a few files per day creates compound progress. Over time, the archive becomes searchable, tagged, linked, and usable inside Obsidian.

This is not a one-off file conversion script. It is the beginning of a local knowledge-ingestion pipeline.

First Build Scope

The first version should:

scan one source folder
select a small batch of files
copy or convert supported files to Markdown
send extracted text to Ollama
validate the AI response
write a .ai.md sidecar note
record progress in a local state file
log every action
avoid moving or deleting originals

The first supported file types should be simple:

.txt
.md
.pdf
.docx later

PDF and Word support can be added carefully after the text/Markdown flow is stable. The book’s table of contents confirms PDF and Word automation is a natural later chapter-level expansion.

Suggested Sidecar Format

For a document called:

example-file.pdf

The script should create something like:

example-file.ai.md

Suggested content:

---
source_file: "/original/path/example-file.pdf"
source_type: "pdf"
processed_at: "2026-05-25T00:00:00+12:00"
model: "qwen2.5-coder:7b"
status: "processed"
value: "useful"
confidence: 0.82
tags:
  - python
  - automation
  - obsidian
backlinks:
  - "[[Python Automation]]"
  - "[[Obsidian Vault]]"
---

# Example File

## Summary

Short plain-English summary here.

## Why it matters

Reason this file is useful, permanent, or throwaway.

## Source link

[Open original file](file:///original/path/example-file.pdf)
Acceptance Criteria

This PR is complete when:

roadmap document exists
initial folder structure is defined
metadata schema is documented
sidecar format is documented
first script boundaries are clear
risk rules are written down
video automation is explicitly deferred
Out of Scope For This PR
bulk processing all 30,000 documents
renaming original files
moving original files
deleting files
email automation
video transcription
automatic customer outreach
Risk Rules

The first script must not rename, move, delete, or overwrite originals.

The first script should process only one file, or a tiny batch, until the output is trusted.

The first script should default to dry-run mode.

The first script should write logs.

The first script should keep a state file so it knows what has already been processed.

👨🏻: The task list I’d put under this PR is:

1. Create project folder
2. Create README.md
3. Create ROADMAP.md
4. Create SCHEMA.md
5. Create sample sidecar .ai.md file
6. Create first dry-run scanner script
7. Add local config file
8. Add processing log
9. Add state file
10. Test with one document only

Suggested folder structure:

obsidian-automation/
  README.md
  ROADMAP.md
  SCHEMA.md
  examples/
    sample-source-note.md
    sample-source-note.ai.md
  scripts/
    scan_documents.py
    process_one_file.py
  config/
    config.example.json
  logs/
    .gitkeep
  state/
    .gitkeep

🛠️: My recommendation for the first actual script is not the Ollama one yet.

First script should be:

scan_documents.py

Its job:

look through a folder
find candidate files
skip files already processed
print the next 5 files it would process
write nothing unless --apply is used

Then the second script becomes:

process_one_file.py

Its job:

read one file
extract text
send to Ollama
validate JSON
write .ai.md sidecar
log result

That keeps the beast on a leash. No “30,000 file stampede through the vault” on day one. 😄

For the later video phase, yes: I’d make a Markdown file per video. It would describe the video, store the original file path, maybe include duration/size/date, and later include transcript or AI summary. Something like:

video-name.video.md

With:

---
source_file: "/srv/shared/media/videos/example.mp4"
media_type: "video"
status: "not-transcribed"
tags:
  - video-library
  - training
---

# Video Name

## Description

Short description here.

## Source

[Open video](file:///srv/shared/media/videos/example.mp4)

👸🏻: Reasoned next step: save this as ROADMAP.md or PR-001-document-ingestion-roadmap.md, then we write the first dry-run scanner script.

Well, I was thinking something like 50 a day. Perhaps we do all the, all the text files first, and then perhaps we get on to other files like, like docs files. If then they had 50 a day, um, you might run out of files one a week. I'm not sure. But it depends how fast you want to run it. If, if you start running into problems, and I, 50 is not that bad um to run, you know, I'm pretty sure a script and a large language model will handle 50, and within a short period of time, you'll probably get through all the text files. Time you run the standard texts and, uh, what do they call them, like, uh, like the summary.{
  "title":"moving files testing tailscale ai tagging backlinks",
  "summary":"Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.",
  "tags":["files","tailscale","ai","tagging","backlinks"],
  "backlinks":[],
  "value":"useful",
  "confidence":0.8
}
Thought for a few seconds

👸🏻: Yes — 50 a day is a sensible first production target, especially if we start with plain text and Markdown files.

👨🏻: I’d treat it like this:

Start with:

.txt
.md

Then later add:

.pdf
.docx
.odt
.html
.csv

That matches the boring-but-powerful automation path from Automate the Boring Stuff: reading/writing files, organising files, regex, CSV/JSON, PDFs/Word, scheduling tasks, and later email/text automation.

Your JSON example is exactly the right shape for the first metadata model:

{
  "title": "moving files testing tailscale ai tagging backlinks",
  "summary": "Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.",
  "tags": ["files", "tailscale", "ai", "tagging", "backlinks"],
  "backlinks": [],
  "value": "useful",
  "confidence": 0.8
}

That should become the required schema for the first Obsidian ingestion script.

📖: I’d update the roadmap like this:

Processing strategy

First phase:

Process 50 text/markdown files per day.
Do not move originals.
Do not delete originals.
Do not overwrite existing sidecars.
Log every processed file.
Keep a state database or JSON file.
Resume where it left off.

The daily run should create sidecar notes like:

original-file.ai.md

Or, if we decide to copy cleaned files into Obsidian:

original-file.md
original-file.ai.md
Daily batch logic

The script should:

1. Scan source folders.
2. Find unprocessed .txt and .md files.
3. Select the next 50.
4. Read each file safely.
5. Send content to qwen2.5-coder:7b or qwen2.5:7b.
6. Validate JSON.
7. Write sidecar Markdown.
8. Mark file as processed.
9. Write a daily report.

Your Ollama notes already show this is the intended local AI direction: note summaries, tags, backlinks, file descriptions, sidecar Markdown notes, and cron-style automation.

State tracking

I would not rely on filename alone. I’d use a state file like:

state/processed-files.json

Each entry should store:

{
  "source_path": "/home/mpc/Documents/example.txt",
  "sha256": "file-hash-here",
  "processed_at": "2026-05-25T04:00:00+12:00",
  "model": "qwen2.5-coder:7b",
  "sidecar_path": "/home/mpc/Documents/example.ai.md",
  "status": "processed"
}

That way, if a file moves later, we still have a fingerprint.

Daily report

Each run should create:

logs/2026-05-25-ingestion-report.md

With:

# Daily Ingestion Report — 2026-05-25

Processed: 50
Successful: 48
Failed: 2
Skipped: 0
Model: qwen2.5-coder:7b

## Useful
- [[moving files testing tailscale ai tagging backlinks]]

## Failed
- broken-file.txt — JSON validation failed
- weird-encoding.txt — could not read file

This gives you an Obsidian-readable audit trail. Very important. Otherwise six weeks later you’ll be staring at the vault going, “Who touched this? Was it me? Was it the robot? Was it Tuesday?” 😄

👨🏻: My recommendation for the first PR task list becomes:

PR-001: Document ingestion roadmap
PR-002: Dry-run scanner for .txt and .md files
PR-003: Process one file through Ollama
PR-004: Batch process 50 files per day
PR-005: Add cron/systemd timer
PR-006: Add PDF/docx support
PR-007: Add video sidecar metadata

For the first actual script, I’d call it:

obsidian_daily_ingest.py

But internally split it into functions:

scan_candidates()
load_state()
pick_batch(limit=50)
extract_text()
run_ollama()
validate_json()
write_sidecar()
update_state()
write_daily_report()

📌: The key decision I’d lock in now:

Daily limit: 50 files
First file types: .txt and .md
Model: qwen2.5-coder:7b
Output: .ai.md sidecar
Originals: untouched
Default mode: dry-run
Apply mode: explicit --apply

👸🏻: Recommended save: add this as PR-002 — Daily Text File Ingestion Plan, then next we can write the first obsidian_daily_ingest.py skeleton with --dry-run, --limit 50, and schema validation.

The specialized tools below connect Python, Obsidian, and QMD (Quarto Markdown) workflows seamlessly on Fedora Linux.
## 🐍 Python Packages for Obsidian Automation
These Python libraries handle batch manipulation, data science analytics, and programmatic edits across your local vault markdown files. [1, 2] 
------------------------------
py-obsidianmd


A specialized framework used to modify note frontmatter and metadata in batch. It seamlessly converts standard inline properties into Dataview-style notations automatically.

pip install py-obsidianmd
```

------------------------------
obsidiantools


An analytics-focused tool built directly on top of the Pandas and NetworkX libraries. It maps out the structural text connections inside your vault to perform graph network analytics on your notes.
%%MAGIT_PARSER_PROTECT%%bash pip install obsidiantools %%MAGIT_PARSER_PROTECT%%
------------------------------
python-frontmatter


The standard, essential package required to load, read, edit, and write YAML metadata sections safely without breaking your Obsidian markdown text content.
%%MAGIT_PARSER_PROTECT%%bash pip install python-frontmatter %%MAGIT_PARSER_PROTECT%% [1, 2] 
## 📄 QMD (Quarto Markdown) Obsidian Plugins [3, 4] 
If you are using .qmd files for data science, executing embedded code blocks, or publishing academic documents, use these plugins to avoid needing external applications like VS Code. [4] 
------------------------------
qmd as md


Enables seamless native editing, live previewing, and rendering of .qmd files directly within your Obsidian vault panels. It interfaces natively with your local Linux Quarto installation to spin up local HTML preview servers or export compiled PDFs on the fly.
------------------------------
Quarto Exporter


Converts internal Obsidian-specific structural link syntax into clean, standard academic-compliant .qmd files. It safely migrates note tags and tracks creation/modification timestamps into the final Quarto document YAML block.
------------------------------
Ridian


An academic-focused plugin designed to execute R and Quarto style data processing chunks cleanly inside your notes. It is optimal for processing research workflows and compiling scientific charts. [4, 5, 6, 7, 8] 
## 🔍 QMD Search Engines & Local AI Add-ons
"QMD" can also refer to Query Markup Documents, a local, privacy-first vector search framework built explicitly to run local AI processes directly against your markdown notes. [9, 10] 
------------------------------
QMD Semantic Search


An AI-powered local vector search engine running completely on-device without cloud API access. It provides immediate keyword and conceptual context matching across all notes by deploying localized GGUF embeddings. [9, 10] 
------------------------------
## 💻 Fast Fedora Environment Config
To make sure Obsidian can communicate properly with your system's Quarto and Python setups, run these configuration commands in your terminal:
%%MAGIT_PARSER_PROTECT%%```bash
## Ensure Quarto CLI and Python development tools are active system-wide
sudo dnf install python3-pip git -y
## Note: Download the Fedora Quarto .rpm from the official quarto.org site and install it:
sudo dnf localinstall quarto-linux-amd64.rpm
## CRITICAL FIX: If you installed Obsidian using Flatpak, run this command## so Obsidian plugins are allowed to launch Quarto/Python binaries on your host:
flatpak override --user --talk-name=org.freedesktop.Flatpak md.obsidian.Obsidian
%%MAGIT_PARSER_PROTECT%%```
Are you looking to generate academic reports using Quarto (.qmd), or are you trying to build a local AI semantic search engine with Python? Let me know so I can help you configure the exact templates!

[1] [https://www.reddit.com](https://www.reddit.com/r/ObsidianMD/comments/z9vvov/pyobsidianmd_a_python_library_to_modify_your/)
[2] [https://forum.obsidian.md](https://forum.obsidian.md/t/obsidiantools-python-package-for-doing-advanced-analytics-of-your-vault/24122)
[3] [https://forum.obsidian.md](https://forum.obsidian.md/t/obsidian-quarto-setup-current-status-and-questions/75003)
[4] [https://www.obsidianstats.com](https://www.obsidianstats.com/plugins/qmd-as-md-obsidian)
[5] [https://www.youtube.com](https://www.youtube.com/watch?v=kPMW4u_K3L4&t=82)
[6] [https://github.com](https://github.com/danieltomasz/qmd-as-md-obsidian)
[7] [https://www.obsidianstats.com](https://www.obsidianstats.com/plugins/quarto-exporter)
[8] [https://github.com](https://github.com/AndreasThinks/obsidian-to-quarto-exporter)
[9] [https://github.com](https://github.com/achekulaev/obsidian-qmd)
[10] [https://github.com](https://github.com/tobi/qmd)
