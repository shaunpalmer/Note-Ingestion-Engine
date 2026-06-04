Pasted text.txt
Document
Oh, look at that. We're starting to get somewhere.
Thought for 21s

👸🏻: Good call — I’ve added a next-few-days goals section and a plain-English explanation of cron jobs on Fedora into the canvas.

📌: The roadmap is now:

Day 1:
one test note → Ollama → JSON → .ai.md sidecar

Day 2:
add JSON validation + logging

Day 3:
process a small inbox folder

Day 4:
test cron automation

📖: Cron jobs are still available on Fedora. They are basically scheduled commands, similar in purpose to Windows Task Scheduler.

Example:

*/30 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py >> /srv/shared/obsidian-ai/logs/cron.log 2>&1

That means:

Every 30 minutes, run the Python script and write output/errors to the log file.

Fedora also has systemd timers, which are more modern and powerful, but for this project I’d start with cron because it is simpler and perfect for early testing.

🛠️: Immediate next command for the machine:

mkdir -p /srv/shared/obsidian-ai/{inbox,processed,failed,logs,prompts}

👸🏻: After that, create one test note in the inbox, and then we build the first Python script.

I've already got a folder called it incoming files or incoming inboxes. Something like that. I'll tell the actual details, but for now I'm just trying to workout what needs to happen. You might split it up to two different actual functions. Because one brings it out of the folder. You might run a small script for changing the file. Perhaps, to mark down, if you look in the resource fold it in this project, you'll see how originally did that and then you might move it again into an actual folder.That's doing the heavy lifting
Ollama-model-testing-rules-and-prompts
Ollama Model Testing Rules, Prompt, and Automation Outline
Goal

Compare local Ollama models for an Obsidian / SEDAM note-intelligence workflow.

The model should help with:

clean titles
useful summaries
lowercase kebab-case tags
Obsidian-style backlinks
note value classification
confidence scoring
automation-ready JSON
Current Best Practical Setup
Default metadata model:
qwen2.5-coder:7b


Fallback/general summary model:
mistral


Retest/alternative:
qwen2.5:7b


Not useful for this task:
llama3.1:8b
Model Output Rules

The model must follow these rules:

Return a single raw JSON object only.
Do not wrap the answer in Markdown code fences.
Do not include explanation before or after the JSON.
Use lowercase kebab-case tags.
Use Obsidian backlinks in [[Double Brackets]].
If no strong backlink exists, return an empty array.
Set value as one of:
throwaway
useful
permanent
Use confidence between 0 and 1.
Do not use confidence 1 unless the classification is extremely obvious.
Prefer useful for working project notes unless the note is clearly disposable or foundational.
Test 1: Strict JSON Metadata Test

Use this first against qwen2.5-coder:7b and mistral.

ollama run qwen2.5-coder:7b 'You are an Obsidian metadata assistant. Return one raw JSON object only. No Markdown. No code fence. No explanation. Use lowercase kebab-case tags. Use Obsidian backlinks in [[Double Brackets]]. If no strong backlink exists, return an empty backlinks array. Set value as one of: throwaway, useful, permanent. Use confidence between 0 and 1. Do not use confidence 1 unless extremely certain. Text: "I moved files from the side rig, tested Tailscale, and want a local AI to tag notes and create backlinks." Return exactly this schema: {"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'

Fallback test:

ollama run mistral 'You are an Obsidian metadata assistant. Return one raw JSON object only. No Markdown. No code fence. No explanation. Use lowercase kebab-case tags. Use Obsidian backlinks in [[Double Brackets]]. If no strong backlink exists, return an empty backlinks array. Set value as one of: throwaway, useful, permanent. Use confidence between 0 and 1. Do not use confidence 1 unless extremely certain. Text: "I moved files from the side rig, tested Tailscale, and want a local AI to tag notes and create backlinks." Return exactly this schema: {"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'
Test 2: Messy Spoken Note Cleanup Test

This tests whether the model can handle rough dictated notes.

ollama run qwen2.5-coder:7b 'You are an Obsidian metadata assistant. Return one raw JSON object only. No Markdown. No code fence. No explanation. Fix obvious dictation errors silently. Use lowercase kebab-case tags. Use Obsidian backlinks in [[Double Brackets]]. Set value as one of: throwaway, useful, permanent. Text: "phone mic keeps getting words wrong but i want local ai to clean up notes and make them useful for obsidian tags backlinks and summaries maybe the side rig can process them later" Return exactly this schema: {"title":"","cleaned_note":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'
Test 3: Sidecar File Description Test

This tests whether the model can generate metadata for future file automation.

ollama run qwen2.5-coder:7b 'You are helping organise files for a local archive. Return one raw JSON object only. No Markdown. No code fence. No explanation. Suggest a clean filename, short description, tags, destination folder, and whether the file should be reviewed before moving. Use lowercase kebab-case tags. Text: "VID_00382.mp4 appears to show a Fedora machine testing Ollama, pulling Mistral and Qwen models, and preparing local AI for Obsidian notes." Return exactly this schema: {"suggested_filename":"","description":"","tags":[],"destination_folder":"","review_required":true,"confidence":0}'
How To Judge The Output

Score each model from 1 to 5 for:

Criterion	Meaning
JSON validity	Can a script parse it?
Instruction following	Did it avoid Markdown and explanations?
Tag quality	Are tags reusable and not too vague?
Backlink quality	Are backlinks useful and in [[Double Brackets]]?
Classification	Is throwaway/useful/permanent sensible?
Confidence	Is confidence realistic rather than inflated?
Practical usefulness	Would this help the actual vault workflow?
Latest Strict Prompt Test

A stricter prompt was tested against the current top two models: qwen2.5-coder:7b and mistral.

Prompt rules included:

raw JSON only
no Markdown code fence
no explanation
lowercase kebab-case tags
Obsidian backlinks in [[Double Brackets]]
value must be throwaway, useful, or permanent
confidence between 0 and 1
avoid confidence 1 unless extremely certain
Qwen 2.5 Coder 7B Result
{
  "title":"moving files testing tailscale ai tagging backlinks",
  "summary":"Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.",
  "tags":["files","tailscale","ai","tagging","backlinks"],
  "backlinks":[],
  "value":"useful",
  "confidence":0.8
}

Judgment:

valid JSON
no Markdown wrapper
followed the requested schema
value classification is sensible
confidence is realistic
tags are usable, though slightly generic
title is understandable but could be cleaner
no backlinks suggested, but that is acceptable because the prompt allowed an empty array if no strong backlink exists

Verdict: best result in the strict test.

Mistral Result
{
  "title":"i-moved-files-from-the-side-rig-tested-tailscale-and-want-a-local-ai-to-tag-notes-and-create-backlinks",
  "summary":"User moved files from the side rig, tested Tailscale, and wants a local AI to tag notes and create backlinks.",
  "tags":[],
  "backlinks":["i-moved-files-from-the-side-rig","tested-tailscale"]
}

Judgment:

returned JSON-like output
did not include all required schema fields
missing value
missing confidence
tags array is empty
backlinks are not in [[Double Brackets]]
title is too long and basically repeats the full sentence

Verdict: failed the strict metadata automation test.

Current Working Assumption

Use:

qwen2.5-coder:7b

as the default model for the first SEDAM / Obsidian metadata workflow.

Use:

mistral

as a fallback for looser summaries and general note work, but not as the first choice for automation-ready metadata.

Retest:

qwen2.5:7b

only when structured output is not mission-critical or when there is a validation layer.

Avoid:

llama3.1:8b

for this specific metadata workflow unless later prompts improve its behaviour.

Short Report: Current Winner
Winner
qwen2.5-coder:7b
Why It Wins

qwen2.5-coder:7b is currently the best model for the Obsidian / SEDAM metadata workflow because it followed the strict prompt better than the others.

It returned:

raw JSON only
no Markdown code fence
all required schema fields
a sensible value of useful
a realistic confidence score of 0.8
usable tags
a clear enough summary

It was not perfect. The title could be cleaner and the tags could be more specific. However, for automation, reliability matters more than elegance. A slightly plain but valid JSON response is better than a pretty response that breaks the script.

Why Mistral Loses The Strict Test

Mistral is still useful for general summaries, but it failed the stricter automation test.

Problems:

missing value
missing confidence
empty tags
backlinks were not in [[Double Brackets]]
title was too long

Mistral can stay as the fallback/general summary model, but it should not be the first choice for automation-ready metadata.

Final Default Setup
Default metadata model:
qwen2.5-coder:7b


Fallback/general summary model:
mistral


Retest/alternative:
qwen2.5:7b


Not useful for this task:
llama3.1:8b
Production Prompt Format

Use this prompt shape for the first automated version.

You are an Obsidian metadata assistant.
Return one raw JSON object only.
No Markdown.
No code fence.
No explanation.
Use lowercase kebab-case tags.
Use Obsidian backlinks in [[Double Brackets]].
If no strong backlink exists, return an empty backlinks array.
Set value as one of: throwaway, useful, permanent.
Use confidence between 0 and 1.
Do not use confidence 1 unless extremely certain.
Prefer useful for working project notes unless the note is clearly disposable or foundational.


Text:
"{NOTE_TEXT}"


Return exactly this schema:
{
  "title":"",
  "summary":"",
  "tags":[],
  "backlinks":[],
  "value":"",
  "confidence":0
}
Terminal Test Command
ollama run qwen2.5-coder:7b 'You are an Obsidian metadata assistant. Return one raw JSON object only. No Markdown. No code fence. No explanation. Use lowercase kebab-case tags. Use Obsidian backlinks in [[Double Brackets]]. If no strong backlink exists, return an empty backlinks array. Set value as one of: throwaway, useful, permanent. Use confidence between 0 and 1. Do not use confidence 1 unless extremely certain. Prefer useful for working project notes unless the note is clearly disposable or foundational. Text: "I moved files from the side rig, tested Tailscale, and want a local AI to tag notes and create backlinks." Return exactly this schema: {"title":"","summary":"","tags":[],"backlinks":[],"value":"","confidence":0}'
Required Output Format

The output must be a single JSON object like this:

{
  "title": "example-note-title",
  "summary": "Short plain-English summary of the note.",
  "tags": ["obsidian", "local-ai", "side-rig"],
  "backlinks": ["[[Obsidian Vault]]", "[[Local AI]]"],
  "value": "useful",
  "confidence": 0.8
}
Automation Script Outline
Script Goal

Create a small script that takes a Markdown note or text file, sends the content to Ollama using qwen2.5-coder:7b, validates the JSON response, and writes metadata back into a sidecar Markdown file or frontmatter block.

Suggested Script Name
sedam-note-metadata.py
First Version Workflow
1. Read note file from an inbox folder
2. Extract plain text
3. Build strict prompt
4. Send prompt to Ollama using qwen2.5-coder:7b
5. Capture model response
6. Strip accidental whitespace
7. Validate JSON
8. Check required fields exist:
   - title
   - summary
   - tags
   - backlinks
   - value
   - confidence
9. If JSON is valid:
   - create/update sidecar .md note
   - or write frontmatter into the original note
10. If JSON is invalid:
   - save response to an error log
   - do not modify the original file
Safety Rules For Automation

The first automated version should be conservative.

Rules:

do not rename files automatically yet
do not delete files
do not overwrite original notes without a backup
do not trust model output without JSON validation
keep a log of every processed note
keep failed outputs for review
only process files from a test inbox first
Suggested Folder Layout
/srv/shared/obsidian-ai/
  inbox/
  processed/
  failed/
  logs/
  prompts/
Example Output Sidecar

For a file called:

network-note.md

The script could create:

network-note.ai.md

With content:

---
title: moving-files-testing-tailscale-ai-tagging-backlinks
summary: Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.
tags:
  - files
  - tailscale
  - ai
  - tagging
  - backlinks
backlinks: []
value: useful
confidence: 0.8
model: qwen2.5-coder:7b
status: ai-generated-needs-review
---


## AI Summary
Moved files from side rig, tested Tailscale, and need local AI for note tagging and creating backlinks.
Next Build Step

Build a tiny Python script that processes one file only.

Do not start with folder-wide automation. First prove the loop:

one note → Ollama → JSON → validation → sidecar Markdown

Once that works, expand to batch processing and cron jobs.

Goals For The Next Few Days
Main Goal

Build the first working SEDAM / Obsidian local AI workflow.

The first version should be small, safe, and boring:

one test note → local model → JSON metadata → sidecar Markdown note

No bulk file moving yet. No automatic renaming yet. No deleting. No clever chaos goblin mode.

Day 1: Prove The One-File Loop
Goal

Create a script that processes one test note and creates an .ai.md sidecar file.

Tasks
create a test folder
create one messy Markdown note
write a Python script to read that note
send the note text to Ollama using qwen2.5-coder:7b
capture the JSON response
validate the JSON
create a sidecar Markdown file
Example Flow
example-note.md
  ↓
qwen2.5-coder:7b
  ↓
example-note.ai.md
Day 2: Add Validation And Logging
Goal

Make the script safer and easier to debug.

Tasks
add JSON validation
check required fields exist
reject bad model output
write failed responses to a failed/ folder
write successful processing events to a log file
include the model name and processing date in the sidecar file
Required Fields
{
  "title": "",
  "summary": "",
  "tags": [],
  "backlinks": [],
  "value": "",
  "confidence": 0
}
Day 3: Add Folder Processing
Goal

Process a small test inbox folder, not the real vault yet.

Tasks
scan /inbox/ for .md or .txt files
process only files without an existing .ai.md sidecar
move successful files to /processed/
move failed attempts to /failed/
keep a log of every file touched
Safe Test Folder
/srv/shared/obsidian-ai/
  inbox/
  processed/
  failed/
  logs/
  prompts/
Day 4: Add Cron Job Testing
Goal

Run the script automatically on a schedule.

Start with a harmless schedule, such as every 30 minutes or once per hour.

Important Rule

Cron should only run the safe test workflow first.

Do not point cron at the real Obsidian vault until the script has proven itself.

Cron Jobs On Fedora
Are Cron Jobs Available On Fedora?

Yes. Cron jobs are still available on Fedora.

Fedora also uses systemd timers, which are the more modern Linux-native way to schedule tasks. But traditional cron is still commonly used and perfectly fine for simple scheduled scripts.

Cron Compared With Windows

On Windows, the closest equivalent is usually:

Task Scheduler

On Fedora/Linux, you commonly use:

cron
systemd timers

For this project, cron is a good starting point because it is simple and script-friendly.

What Is A Cron Job?

A cron job is a scheduled command.

It is not a different programming language. It is basically Linux saying:

Run this command at this time, on this schedule.

For example:

0 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py

That means:

Run this Python script at minute 0 of every hour.
Cron Format

Cron uses five timing fields:

minute hour day-of-month month day-of-week command

Example:

*/30 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py

Meaning:

Run every 30 minutes.
Useful Cron Examples

Run every hour:

0 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py

Run every 30 minutes:

*/30 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py

Run every day at 2:00 AM:

0 2 * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py

Run every 10 minutes while testing:

*/10 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py
Editing User Cron Jobs

Open the user's cron file:

crontab -e

List current cron jobs:

crontab -l

Remove all cron jobs for the current user:

crontab -r

Be careful with crontab -r because it removes the whole user crontab.

Safer Cron Command With Logging

A better test cron command should log output:

*/30 * * * * /usr/bin/python3 /srv/shared/obsidian-ai/sedam-note-metadata.py >> /srv/shared/obsidian-ai/logs/cron.log 2>&1

This sends normal output and errors to:

/srv/shared/obsidian-ai/logs/cron.log
Cron Safety Rules For SEDAM

Use these rules before automating anything:

cron should only run scripts that have already been tested manually
always use full paths
log all output
never delete files in early versions
never rename files automatically in early versions
never point cron at the full vault first
test on a small inbox folder
keep backups of anything important
Cron vs Systemd Timers
Cron

Best for:

simple scheduled scripts
quick automation
easy testing
small personal workflows
Systemd Timers

Best for:

more robust services
dependency-aware jobs
better logging through journalctl
production-style Linux automation
Recommendation For This Project

Start with cron.

Later, when the workflow is stable, convert important jobs to systemd timers if needed.

The first cron goal should be simple:

Every 30 minutes, process new notes from /srv/shared/obsidian-ai/inbox/ and create .ai.md sidecar files.
Immediate Next Step

Do not force a new folder name yet. Shaun already has an existing incoming folder, possibly named something like incoming files or incoming inboxes.

Once the exact path is confirmed, use that existing folder rather than creating duplicate inboxes.

Split The Workflow Into Separate Functions

The workflow should be split into small stages instead of one giant script.

This keeps the system safer, easier to debug, and easier to expand.

Core Principle

Each script/function should do one job well.

Do not begin with one monster script that scans, converts, renames, summarises, tags, moves, and archives everything in one hit.

That would be automation soup.

Stage 1: Intake Scanner
Job

Look inside the incoming folder and list files that need processing.

Responsibilities
scan the incoming folder
detect file types
ignore hidden/system files
skip files that already have a matching .ai.md sidecar
produce a list of candidate files
Possible function name
def scan_incoming_folder(incoming_path):
    pass
Stage 2: File Normaliser
Job

Prepare files into a format that can be processed.

This includes simple conversions such as .txt to .md.

Shaun has already proven a useful Linux pattern for bulk converting .txt files to .md using find, for example:

find "$HOME/Documents/LinuxBox-Vault/linuxBox/GPT -save" -type f -name "*.txt" -exec bash -c 'mv "$1" "${1%.txt}.md"' _ {} \;

For SEDAM, this should become a safer version with:

dry-run mode
logging
collision checks
backup option
recursive option
Possible function name
def normalise_file_to_markdown(file_path):
    pass
Stage 3: Text Extractor
Job

Extract usable text from the file.

File handling ideas
.md  → read directly
.txt → convert or read directly
.pdf → later stage, not first version
.mp4 → do not process video content yet; use filename/sidecar metadata only
Possible function name
def extract_text_for_ai(file_path):
    pass
Stage 4: Metadata Generator
Job

Send the extracted text to Ollama using the winning model.

Current default model
qwen2.5-coder:7b
Possible function name
def generate_metadata_with_ollama(text, model="qwen2.5-coder:7b"):
    pass
Stage 5: JSON Validator
Job

Make sure the model response is safe to use.

Checks
response is valid JSON
required fields exist
tags is a list
backlinks is a list
value is one of throwaway, useful, permanent
confidence is between 0 and 1
Possible function name
def validate_metadata_json(metadata):
    pass
Stage 6: Sidecar Writer
Job

Create an .ai.md file beside the original note or in a processing folder.

Example
original:
network-note.md


sidecar:
network-note.ai.md
Possible function name
def write_sidecar_note(original_file, metadata):
    pass
Stage 7: Mover / Router
Job

Move files only after successful processing.

This is the heavier-lifting stage and should come later.

Possible destinations
processed/
failed/
needs-review/
archive/
Possible function name
def route_processed_file(file_path, metadata):
    pass
Recommended Early Pipeline

Start with this:

incoming folder
  ↓
scan file
  ↓
normalise txt/md if needed
  ↓
extract text
  ↓
send to qwen2.5-coder:7b
  ↓
validate JSON
  ↓
write .ai.md sidecar
  ↓
leave original file where it is

Later pipeline:

incoming folder
  ↓
scan + normalise + extract
  ↓
AI metadata
  ↓
validation
  ↓
sidecar note
  ↓
move to correct project/media/business folder
  ↓
log action
Important Design Decision

The first version should create metadata before moving files.

Why?

Because metadata helps decide where the file should go.

AI description + tags + value
  ↓
better routing decision

Moving first and understanding later is more likely to create folder chaos.

Safety Rules
scan first
dry-run before moving
convert only simple file types first
create sidecars before changing originals
log everything
never delete in early versions
avoid auto-renaming until confidence is proven
keep failed files separate
do not point the script at the full vault first
Revised Next Build Step

Once the real incoming folder path is known, build the first script around that folder.

First target:

scan one incoming folder
find one .md or .txt file
create one .ai.md sidecar
leave the original untouched

After that works, add:

.txt → .md conversion

Then add:

processed / failed routing

Only after those are proven should cron be added.

Thought for 24s

👸🏻: Yes — that is exactly the right instinct. I updated the canvas so the workflow is split into separate stages/functions, rather than one big “do everything” script.

🛠️: The better architecture is:

incoming folder
  ↓
scan files
  ↓
normalise file type
  ↓
extract text
  ↓
send to qwen2.5-coder:7b
  ↓
validate JSON
  ↓
write .ai.md sidecar
  ↓
later: move/route file

📖: The important bit is this: metadata should probably happen before moving the file.

Reason: the AI description, tags, and value rating help decide where the file belongs. Moving first and understanding later is how you end up with folders called:

sorted-maybe-final-final-actually-use-this-one

Tiny goblin behaviour. Avoid. 😄

For the first version, I’d split it into these functions:

scan_incoming_folder()
normalise_file_to_markdown()
extract_text_for_ai()
generate_metadata_with_ollama()
validate_metadata_json()
write_sidecar_note()
route_processed_file()

And yes, your previous .txt → .md pattern fits perfectly as the normaliser stage. The proven command pattern was basically:

find "$HOME/Documents/LinuxBox-Vault/linuxBox/GPT -save" -type f -name "*.txt" -exec bash -c 'mv "$1" "${1%.txt}.md"' _ {} \;

But in the proper script version, we add:

dry-run mode
collision checks
logging
backup option
recursive option

👸🏻: So the next build target is not “sort everything.” It is much safer:

find one .md or .txt file
normalise if needed
send content to Ollama
create one .ai.md sidecar
leave the original untouched

Next step: when you give me the real incoming folder path, we can build the first one-file script around that exact location.

Macarthur thing album, when I when I get back to my d'artagnan, i've gone to be that's 5:26 in the morning.Yeah and I norm i think i'm not gonna build this in.vs-Code first i set up some folded names. What sort of folded name? Can I have for this? And then I'll put some names to file us and get into it after that. Well, we'll get into building the scripts, and we have to decide, we're going to put these scripts on the machine, probably somewhere in Admin. It's probably going to be deep in the valve system. Somewhere?So it's out of the way it runs somewhere.There's plenty of notes.It points the right direction in paths. And quietly runs in the background
Thought for 8s

👸🏻: You’re at 5:26 in the morning, Shaun — so I’d keep this planning clean and not start building in VS Code yet. This is a “name the folders, choose the paths, don’t summon the automation goblin before coffee” moment. ☕

📖: Cleaned-up version of what you said:

“When I get back to my desktop, I’m probably not going to build this in VS Code straight away. First, I want to set up the folder names. What folder names should I use for this? Then I’ll add some file names and we can start building the scripts. We also need to decide where the scripts should live on the machine. Probably somewhere under Admin, deep enough in the filesystem that they’re out of the way, but still easy to find. The scripts should point to the right paths and quietly run in the background.”

🛠️: My recommended folder structure:

~/Admin/SEDAM/
  scripts/
  config/
  prompts/
  logs/
  test-data/
  docs/

Then for the working file area, use your existing incoming folder when you confirm the real path. But conceptually:

/srv/shared/obsidian-ai/
  incoming/
  processed/
  failed/
  needs-review/
  sidecars/
  logs/

📌: I’d separate script home from data home:

~/Admin/SEDAM/
→ where your scripts, prompts, config, and project notes live

/srv/shared/obsidian-ai/
→ where files are processed, logged, and moved

Reason: /srv/shared is already part of your storage/network world, while ~/Admin/SEDAM is your control room. Your existing notes already show /srv/shared patterns working for shared storage, and your current Ollama notes confirm the local AI goal includes sidecar Markdown notes, summaries, tags, backlinks, and cron jobs.

📂: Folder names I’d use:

mkdir -p ~/Admin/SEDAM/{scripts,config,prompts,logs,docs,test-data}

Later, once you confirm the real incoming path:

mkdir -p /srv/shared/obsidian-ai/{processed,failed,needs-review,sidecars,logs}

📄: First script names:

sedam_scan_incoming.py
sedam_note_metadata.py
sedam_validate_json.py
sedam_write_sidecar.py
sedam_route_file.py

But for the first build, only create this one:

sedam_note_metadata.py

That keeps us focused on the first proven loop:

one note → Ollama → JSON → .ai.md sidecar

🐍: This direction matches your automation resources too. Your uploaded Python automation material specifically points toward file/folder manipulation with pathlib, including creating directories, joining paths, renaming files, and checking if files exist. The Automate the Boring Stuff material also directly covers reading/writing files, organising files, moving/renaming files, JSON data, and scheduling tasks.

👸🏻: My recommendation for tonight/morning: create only the admin project shell, then stop before coding.

mkdir -p ~/Admin/SEDAM/{scripts,config,prompts,logs,docs,test-data}
cd ~/Admin/SEDAM

Then later we add the real incoming path into a config file, probably:

~/Admin/SEDAM/config/sedam_paths.json

Next step: when you’re back at the desktop, run the mkdir -p command and then tell me the real path of your existing incoming folder.