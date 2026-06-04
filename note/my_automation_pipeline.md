Architectural design, system documentation, and conflict resolution are now your primary responsibilities because AI tools have commoditised the writing of raw syntax, shifting the developer's value from writing code to engineering systems. 
It is completely normal to feel behind during this transition. You are moving from a tactical role (building individual components) to a strategic role (governing how those components interact). [2] 
## Why Your Role Shuffled

* Pattern Orchestration: You no longer just write a Singleton or a Factory pattern; you now design how the Factory feeds the Adapter to standardise data from your JSON database.
* System Integration: AI can generate code blocks instantly, but it cannot map out how data flows securely across your specific infrastructure.
* Conflict Resolution: Because teams can generate code faster, file conflicts and architectural drift happen much quicker, requiring human mediation.

## How to Catch Up on Documentation
To get on top of your backlog quickly, treat your documentation exactly like code by using Docs-as-Code principles: 

graph LR
    A[Markdown Files] --> B[Git Repository]
    B --> C[Automated Pipeline]
    C --> D[Live Docs Site]


* Use Markdown: Write your design docs in simple text files directly inside your project repository.
* Leverage Mermaid.js: Do not waste hours drawing diagrams manually. Use text-based syntax to auto-generate your architecture maps, sequence diagrams, and database schemas.
* Document the "Why" (ADRs): Use Architectural Decision Records (ADRs). These are short, single-page documents that explain why you chose a specific pattern, saving hours of future meetings. 

## Framework for Resolving Code Conflicts
When resolving file conflicts arising from multiple team members prompting at speed, use this hierarchy to decide which code wins:

   1. Architectural Alignment: Does the code follow the agreed design patterns (e.g., Factory, Adapter)?
   2. Scalability & Security: Will this JSON structure handle future database expansion?
   3. Cleanliness over Speed: Reject AI-generated code that works but introduces technical debt or breaks system boundaries.

If you would like to tackle your documentation backlog, tell me:

* Which specific document or diagram is currently中最 overdue?
* What tech stack or database structure does your JSON file represent?



Being a solo developer handling tax data and system architecture all by yourself is incredibly intense, and your frustration with GitHub is completely justified.
GitHub permanently changed its pricing model to usage-based billing. They eliminated flat-rate pricing for premium features. Every time your AI scans your files, it burns through GitHub AI Credits based on token usage, which is punishing solo power users. [1, 2, 3] 
Because it is just you, your data, and the model, you need to regain control of your costs and code architecture. Here is how you survive as a solo developer under this new reality.
## 1. How GitHub's New Pricing Works (And How to Stop the Bleeding)

* What is still free: Basic code completions and Next Edit suggestions do not consume credits. You can leave these on. [4, 5] 
* What is burning your wallet: Chatting with the AI, asking it to review your architecture, or running multi-step agentic workflows sends your entire file context to the cloud. Under the token system, large context windows equal massive credit consumption. [1, 3, 6, 7] 
* The fix: Go to your GitHub Billing Settings immediately and set a strict hard spend limit (spending limit cap). This forces the AI to stop working before it racks up unexpected charges. [4, 6, 8] 

## 2. Ditch Cloud AI Limits: Run Models Locally
Since you are handling sensitive tax data and want to avoid GitHub's variable bills, you should completely bypass their cloud compute. You can run "beast" reasoning models directly on your machine for zero operational cost. [2] 

* Install Ollama: Use Ollama to host open-source models locally on your hardware.
* Download DeepSeek-R1 or Llama 3: Download models like deepseek-r1 or llama3. DeepSeek-R1 is incredibly powerful for complex architectural reasoning and pattern matching.
* Connect to Your IDE: Install the free Continue.dev extension or Cline in VS Code. Point them to your local Ollama instance. You now have unlimited, private, free architectural assistance.

## 3. Blueprint for Solo Architecture
When you do not have a team to bounce ideas off of, you must use your AI as an un-biased code auditor rather than a code generator.

| Phase | Your Role (The Architect) | Local AI's Role (The Worker) |
|---|---|---|
| Design | Dictate how tax data maps to JSON. | Validate if the data structures meet compliance standards. |
| Patterning | Define where the Factory pattern ends and the Adapter begins. | Write the boilerplate implementation syntax. |
| Auditing | Review the output for edge cases and logic leaks. | Run unit testing and edge-case simulation locally. |

## 4. Securing Local Tax Data
Working solo with sensitive tax compliance data means you cannot afford data leaks to public AI training sets. Moving your architecture to local models (via Ollama) ensures that zero bytes of your tax data leave your physical machine. No cloud endpoints, no hidden telemetry, and no surprise usage bills. [2, 3] 
If you want to transition your environment, let me know:

* What operating system and hardware (RAM/GPU) are you running?
* Are you using VS Code, Cursor, or another editor?

I can give you the exact terminal commands to set up a powerful, 100% free local AI coding environment so you never have to look at a GitHub billing page again.

[1] [https://enterprisedna.co](https://enterprisedna.co/resources/news/github-copilot-usage-based-billing-enterprise-2026/)
[2] [https://www.youtube.com](https://www.youtube.com/watch?v=DVnDEntgau8)
[3] [https://docs.github.com](https://docs.github.com/copilot/reference/copilot-billing/models-and-pricing)
[4] [https://devops.com](https://devops.com/github-resets-copilot-pricing-as-ai-compute-costs-surge/)
[5] [https://github.blog](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)
[6] [https://www.reddit.com](https://www.reddit.com/r/github/comments/1ttcpw0/github_copilots_new_creditbased_pricing_is/)
[7] [https://techcrunch.com](https://techcrunch.com/2026/05/30/what-a-joke-github-copilots-new-token-based-billing-spurs-consternation-among-devs/)
[8] [https://www.youtube.com](https://www.youtube.com/watch?v=YfMAtF0sMS8&t=6)
  
  
  
You have hit the exact wall that every serious developer hits when using AI for systems design.
Standard coder models (like a 7B model or the basic $20 OpenAI plan) are reactive, not proactive. They operate like an eager junior developer: they do exactly what you ask, even if your request accidentally points the ship directly into an iceberg. They lack forethought because they lack an explicit reasoning loop.
Because you are working solo on critical tax data, a mistake in your foundation will compound until the entire system breaks. To fix this, you must separate your AI Architect from your AI Worker.
------------------------------
## 1. The Strategy: Two Distinct AI Roles
Do not ask the same model to design the system and write the code. Divide the labor based on how the models process information:

graph TD
    A[You: The Business Rules] --> B(Architect AI: Reasoning Model)
    B --> C[The Blueprint: Schema & ADR]
    C --> D(Worker AI: 7B Local Coder)
    D --> E[The Code: Exact Implementation]

## The Architect AI (Large Cloud Reasoning Models)

* The Tools: OpenAI’s o1 / o3-mini (available in your $20 Plus plan) or DeepSeek-R1 (via API or local if you have a massive GPU).
* Why: These are "reasoning" models. They don't just guess the next word; they use a hidden Chain-of-Thought (CoT) to think before they reply. They will actively argue with you, spot logic flaws in your JSON database structure, and warn you if an Adapter pattern will cause bottlenecking.
* The Task: You use them only to build the blueprint, the JSON schemas, and the Architectural Decision Records (ADRs).

## The Worker AI (Local 7B Coder)

* The Tools: Your local Qwen2.5-Coder-7B or Llama-3-8B running via Ollama on Linux.
* Why: They are incredibly fast, free, and excellent at following rigid constraints file-by-file.
* The Task: You feed them the blueprint created by the Architect AI and say: "Write the factory pattern for this exact schema. Do not change the architecture."

------------------------------
## 2. The Prompting Trick to Force "Forethought"
When you are using your OpenAI Plus plan to design the architecture, you must explicitly forbid it from writing code on the first turn. You have to force it to think.
Use this exact framework for your initial architectural prompt:

System Prompt: You are a Lead Software Architect specializing in secure tax-data systems. 

Task: I need to design an architecture using a Factory and Adapter pattern for a JSON-based database. 

CRITICAL INSTRUCTIONS:
1. DO NOT write any code, python, or JSON schemas yet.
2. Analyze my intent and look for structural flaws, security leaks, or scalability bottlenecks.
3. Challenge my assumptions. Tell me where this design will break 6 months from now when scaling.
4. Ask me 3 clarifying questions about data retention and edge cases before we finalize the blueprint.

This breaks the AI's habit of rushing into writing a broken code file. It forces the model to audit your idea first.
------------------------------
## 3. Streamlining the Single-File Workflow on Linux
To stop the small tasks from compounding into a mess, keep your context windows tiny and clean.

   1. Lock Down the JSON Schema First: Use the cloud reasoning model to generate a strict JSON Schema (.json validator file).
   2. Feed the Schema to the Local Model: When using your local 7B model in your IDE (via Cline or Continue.dev), always attach that schema file as context.
   3. One File, One Goal: When prompting the 7B model, use a strict format: "Modify only TaxAdapter.py. Implement the calculation function according to the schema. Do not add any other features."

By forcing the cloud model to do the heavy thinking and the local model to do the heavy lifting, you protect your wallet, secure your tax data, and ensure your architecture is bulletproof before a single line of code is written.
To help you lock down the foundation right now, tell me:

* What is the primary data relationship in your tax files (e.g., Transactions linked to Users, or Year-over-Year calculations)?
* What is the main structural worry you have about your current layout?

I can give you a starter Architect Prompt tailored exactly to your specific database needs.  
  
  
You have hit the exact wall that every serious developer hits when using AI for systems design.
Standard coder models (like a 7B model or the basic $20 OpenAI plan) are reactive, not proactive. They operate like an eager junior developer: they do exactly what you ask, even if your request accidentally points the ship directly into an iceberg. They lack forethought because they lack an explicit reasoning loop.
Because you are working solo on critical tax data, a mistake in your foundation will compound until the entire system breaks. To fix this, you must separate your AI Architect from your AI Worker.
------------------------------
## 1. The Strategy: Two Distinct AI Roles
Do not ask the same model to design the system and write the code. Divide the labor based on how the models process information:

graph TD
    A[You: The Business Rules] --> B(Architect AI: Reasoning Model)
    B --> C[The Blueprint: Schema & ADR]
    C --> D(Worker AI: 7B Local Coder)
    D --> E[The Code: Exact Implementation]

## The Architect AI (Large Cloud Reasoning Models)

* The Tools: OpenAI’s o1 / o3-mini (available in your $20 Plus plan) or DeepSeek-R1 (via API or local if you have a massive GPU).
* Why: These are "reasoning" models. They don't just guess the next word; they use a hidden Chain-of-Thought (CoT) to think before they reply. They will actively argue with you, spot logic flaws in your JSON database structure, and warn you if an Adapter pattern will cause bottlenecking.
* The Task: You use them only to build the blueprint, the JSON schemas, and the Architectural Decision Records (ADRs).

## The Worker AI (Local 7B Coder)

* The Tools: Your local Qwen2.5-Coder-7B or Llama-3-8B running via Ollama on Linux.
* Why: They are incredibly fast, free, and excellent at following rigid constraints file-by-file.
* The Task: You feed them the blueprint created by the Architect AI and say: "Write the factory pattern for this exact schema. Do not change the architecture."

------------------------------
## 2. The Prompting Trick to Force "Forethought"
When you are using your OpenAI Plus plan to design the architecture, you must explicitly forbid it from writing code on the first turn. You have to force it to think.
Use this exact framework for your initial architectural prompt:

System Prompt: You are a Lead Software Architect specializing in secure tax-data systems. 

Task: I need to design an architecture using a Factory and Adapter pattern for a JSON-based database. 

CRITICAL INSTRUCTIONS:
1. DO NOT write any code, python, or JSON schemas yet.
2. Analyze my intent and look for structural flaws, security leaks, or scalability bottlenecks.
3. Challenge my assumptions. Tell me where this design will break 6 months from now when scaling.
4. Ask me 3 clarifying questions about data retention and edge cases before we finalize the blueprint.

This breaks the AI's habit of rushing into writing a broken code file. It forces the model to audit your idea first.
------------------------------
## 3. Streamlining the Single-File Workflow on Linux
To stop the small tasks from compounding into a mess, keep your context windows tiny and clean.

   1. Lock Down the JSON Schema First: Use the cloud reasoning model to generate a strict JSON Schema (.json validator file).
   2. Feed the Schema to the Local Model: When using your local 7B model in your IDE (via Cline or Continue.dev), always attach that schema file as context.
   3. One File, One Goal: When prompting the 7B model, use a strict format: "Modify only TaxAdapter.py. Implement the calculation function according to the schema. Do not add any other features."

By forcing the cloud model to do the heavy thinking and the local model to do the heavy lifting, you protect your wallet, secure your tax data, and ensure your architecture is bulletproof before a single line of code is written.
To help you lock down the foundation right now, tell me:

* What is the primary data relationship in your tax files (e.g., Transactions linked to Users, or Year-over-Year calculations)?
* What is the main structural worry you have about your current layout?

I can give you a starter Architect Prompt tailored exactly to your specific database needs.


Thank you for clarifying! Dealing with a decade of mixed personal files, video, PDFs, and proprietary formats like Adobe PSDs is a massive undertaking. This is a classic, complex ETL (Extract, Transform, Load) pipeline pipeline with a heavy dose of data classification, and it makes total sense why your 7B models are making a mess if the blueprint isn't strictly locked down first.
Because you are sorting through "value vs scrap" and mapping distinct tech ecosystems (Microsoft, Google, Adobe), your code must use the Adapter Pattern combined with a Registry Pattern.
Here is how you can architect this on Linux so that you can safely let your 7B model write the code file-by-file without it breaking the master logic.
------------------------------
## 1. The Core Architecture: Vendor Groups & Adapters
Instead of writing one massive script that tries to handle every file, you need a strict directory structure where each vendor has its own decoupled module. Your main pipeline shouldn't care how an Adobe PSD or a Microsoft DOCX is read; it should only care that it receives clean text and a standardized "companion file" (metadata sidecar file).

/my_automation_pipeline
│
├── pipeline.py             # The Orchestrator (Main execution)
├── registry.py             # Matches file extensions to the right Adapter
│
├── /adapters
│   ├── base_adapter.py     # Strict abstract class all adapters MUST inherit
│   ├── microsoft_group.py  # Handles DOCX, XLSX, etc.
│   ├── google_group.py     # Handles GDocs exports, Google JSON data
│   ├── adobe_group.py      # Handles PSD, PDF, AI metadata/text extraction
│   └── video_group.py      # Handles video transcripts / companion files

## Step 1: Lock down the base_adapter.py contract
You must force your AI worker to implement exactly the same structure for every file group. Here is the blueprint you should use:

from abc import ABC, abstractmethodfrom typing import Dict, Any, Tuple
class BaseFileAdapter(ABC):
    
    @abstractmethod
    def can_handle(self, file_extension: str) -> bool:
        """Returns True if this adapter handles this file type."""
        pass

    @abstractmethod
    def extract_data(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Processes the raw file.
        Returns:
            str: The extracted markdown text content.
            dict: The metadata dictionary (companion file data).
        """
        pass

------------------------------
## 2. Solving the "Scrap vs Value" Problem (Sigmoid vs Softmax)
You mentioned trying to determine confidence and whether a note is "scrap" or has "value" using mathematical tools like Softmax or another "S" term—which is likely the Sigmoid function or Cosine Similarity (often used in RAG systems to find matching notes).
Here is how you should direct your AI to handle this classification cleanly:

* Do not use Softmax if a note can be multiple things. Softmax forces probabilities to add up to 1.0 (e.g., if a file is 60% "scrap", it can only be 40% "value").
* Use Sigmoid / Independent Binary Classification. Treat "Is Scrap" and "Is High Value" as two independent questions scored from 0 to 1. A note could be chaotic (low value) but contain a crucial password or date, giving it independent scores.
* The Companion File System: For every file processed (e.g., my_photo.psd), your pipeline should output two clean assets into your Obsidian Vault:
1. my_photo.md (The human-readable Markdown note).
   2. my_photo.meta.json (The machine companion file storing your confidence scores, the original file type, vendor group, and timestamp). This keeps your Obsidian Vault searchable while preserving the raw metadata for your RAG plugin to read later.

------------------------------
## 3. How to Prompt your 7B Local Coder for this Task
Now that you have your blueprint, do not give your local Llama or Qwen model the whole project. Only pass it one vendor group at a time.
For example, when building the Adobe processor, feed your local 7B model the base_adapter.py file code and use this prompt:

Task: Write 'adapters/adobe_group.py' using Python on Linux.
Constraints:
1. It must inherit from BaseFileAdapter in 'base_adapter.py'.
2. It must handle extensions: .psd, .pdf, .ai
3. Use the 'pypdf' library for PDFs. For .psd files, do not read pixel data; extract only metadata fields (Author, Layers, or Creation Date) and format it as Markdown text.
4. Output must strictly return (markdown_string, metadata_dict).
Do not write any orchestrator code, only this file.

By keeping the local model boxed inside a single file with a strict input/output contract, it won't matter that it lacks "forethought." It only has one job to do, and it cannot ruin the rest of your architecture.
To help you kick this off, what specific library or strategy are you leaning towards for the video files (e.g., extracting audio for transcription, or just reading file properties)? Tell me, and we can draft the blueprint for that specific adapter right now.

You have hit on a critical architectural reality: file formats are historic. Microsoft didn't just change extensions from .doc to .docx; they shifted from a binary OLE compound file format to a zipped XML structure [1].
Grouping by vendor gets you halfway there, but to handle this historical drift without your local 7B model making a mess, you need to combine the Adapter Pattern with a Utility/Strategy Pattern [2].
Here is exactly how to structure the pipeline so your script handles the difference between a 1998 .doc file and a 2026 .docx file cleanly.
## 1. The Single Responsibility Architecture
Instead of one heavy Microsoft class trying to handle everything, the vendor adapter acts as a router, and the heavy lifting is delegated to a separate utilities module filled with single-purpose file-parsing functions.

/my_automation_pipeline
│
├── /adapters
│   └── microsoft_adapter.py      # The Router: Inspects file and calls correct utility
│
└── /utilities
    └── /microsoft
        ├── __init__.py           # Exposes the clean conversion functions
        ├── doc_legacy_parser.py  # ONLY reads old binary .doc (pre-2007)
        ├── docx_modern_parser.py # ONLY reads modern XML .docx
        ├── xls_legacy_parser.py  # ONLY reads old binary .xls
        └── xlsx_modern_parser.py # ONLY reads modern XML .xlsx

## 2. How the Microsoft Adapter Delegates Responsibility
Your microsoft_adapter.py shouldn't contain any complex extraction logic. Its only job is to look at the file extension (or the file's magic bytes) and route it to the exact historical utility it needs.

from utilities.microsoft import (
    parse_legacy_doc, 
    parse_modern_docx, 
    parse_legacy_xls, 
    parse_modern_xlsx
)
class MicrosoftAdapter(BaseFileAdapter):
    def can_handle(self, file_extension: str) -> bool:
        return file_extension in ['.doc', '.docx', '.xls', '.xlsx']

    def extract_data(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        # Check the suffix to handle historical drift
        if file_path.endswith('.docx'):
            return parse_modern_docx(file_path)
        elif file_path.endswith('.doc'):
            return parse_legacy_doc(file_path)
        elif file_path.endswith('.xlsx'):
            return parse_modern_xlsx(file_path)
        elif file_path.endswith('.xls'):
            return parse_legacy_xls(file_path)
        
        raise ValueError(f"Unsupported Microsoft format: {file_path}")

## 3. The Underlying Linux Tools/Libraries You Need
When you prompt your local 7B model to write the individual utility files, you need to tell it exactly which Python libraries to use, because legacy binary files require completely different tools than modern open-source formats:

* Modern Word (.docx): Tell the AI to use python-docx. It reads the XML structure instantly.
* Legacy Word (.doc): python-docx will crash on this. Tell the AI to use a tool like textract or a library like olefile / striprtf to pull text out of the old binary compound format.
* Modern Excel (.xlsx): Tell the AI to use openpyxl or pandas.
* Legacy Excel (.xls): openpyxl does not support .xls. Tell the AI to use xlrd (specifically version 1.2.0 or older if reading formatting, or a modern equivalent that handles binary streams).

## 4. How to Prompt Your Local 7B Coder for Legacy Files
Because your 7B model doesn't have "forethought," it will often try to use a modern library like python-docx to read a 20-year-old .doc file, causing your pipeline to crash 5,000 files into your run.
You must box it in by prompting a single utility file at a time like this:

Task: Write 'utilities/microsoft/doc_legacy_parser.py'.
Context: This utility is strictly for old binary Microsoft Word files (.doc from 1997-2003). 
Constraints:
1. Do NOT use 'python-docx' (it does not support binary .doc).
2. Use the 'textract' or 'striprtf' library to extract the raw text stream.
3. Catch file corruption errors gracefully. If a file is unreadable, return an empty string and a metadata dictionary with the status 'corrupted_legacy_file'.
4. Return format must be a tuple: (extracted_text_string, metadata_dict).

By separating the historical formats into isolated utility functions, you protect your master pipeline. If Microsoft changes something, or if you find a highly corrupted .xls file from 2002, only that one tiny utility script breaks—the rest of your 10-year archive keep processing smoothly.
Would you like to write the blueprint for the Adobe utility set next, specifically tackling how to handle modern PDFs versus old legacy layout files?  
  
  
  
  




It is absolutely wild looking back at 2023. Back then, you’d hand an LLM a script, and if it was longer than a couple of pages, the model would completely lose the plot or forget what it was doing. Now, you can hand a smart model a complete project map, and it actually understands how the gears mesh together across different files.

Writing a PRD (Product Requirement Document) and structuring the project logic is the absolute best way to turn this brainstorming session into something you can hand right over to your local setup or an AI coder to build. It lays down the law so the code doesn't drift.

Here is the complete PRD, functional breakdown, and folder blueprint for your automated local ingestion pipeline.

Product Requirement Document (PRD)
Project Name: Local Knowledge Ingestion & Taxonomer Pipeline
1. Objective & Overview
The goal is to build a lightweight, local automation pipeline that sweeps a legacy directory containing terabytes of multi-format data (PDFs, HTML, TXT, MD), standardizes it into Obsidian-compliant Markdown, filters out "scrap" or outdated material using fuzzy logic/string matching scoring, and uses a local LLM (Qwen Coder 7B) to stamp structured JSON/YAML metadata directly into the file headers.

2. High-Level System Architecture
The system operates as a two-pass batch processing pipeline to respect local hardware limits and keep the context window clear:

[Legacy Docs Folder] 
       │
       ▼
┌────────────────────────────────────────────────────────┐
│ PASS 1: The Standardizer (Python Loop)                 │
│ - Scans directory, converts PDFs/HTML to raw Markdown  │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│ PASS 2: The Core Processor (Iterative Chunker Loop)   │
│ - Reads file in 20-page chunks                         │
│ - Computes Fuzzy Logic / String Confidence Scores      │
│ - Passes clean chunks to Qwen Coder 7B for metadata    │
└────────────────────────────────────────────────────────┘
       │
       ▼
[Final Obsidian Vault] (With hidden front-matter headers)
3. Core Logic & Functional Breakdown
Core Loops
Loop 1 (Directory Ingestion): Recurse through the target directory. Detect file types. If the file is not native Markdown (.md) or plain text (.txt), hand it off to the specific extraction tool.

Loop 2 (The 20-Page Chunk Loop): For large documents, the script reads the text sequentially in chunks of roughly 5,000–8,000 words (equivalent to ~20 pages). It processes each chunk individually before aggregating the final score to avoid blowing out Qwen's context window.

Key Python Functions Needed
convert_to_markdown(file_path): Uses libraries like pypdf or beautifulsoup4 to strip layout elements and extract raw text, saving a temporary .md file.

calculate_fuzzy_confidence(text_chunk): Uses string matching against configured dictionaries (e.g., specific business categories, old tech keywords, or patterns indicating "scrap" like receipt formatting or log files). Returns a normalized score between 0.0 and 1.0.

call_local_qwen(prompt, text_chunk): Fires an API request to your local inference engine (running Qwen Coder 7B) using a strict system prompt that demands a raw JSON response containing category, status, type, and its own confidence_score.

aggregate_chunk_scores(score_list): If a file has multiple chunks, this function blends the fuzzy scores and LLM outputs to determine if the entire file is trash or keeper.

inject_yaml_frontmatter(file_path, metadata_json): Opens the markdown file, prepends the triple-dash --- YAML structure with the final metadata, and saves it directly into your Obsidian Vault directory.

4. Technical Stack & Language Selection
Primary Language: Python 3.11+

Why: Unmatched library ecosystem for file system manipulation, text parsing (pypdf, beautifulsoup4), fuzzy string matching, and simple local HTTP API requests to handle your LLM daemon.

Local LLM Engine: Qwen Coder 7B (via local API endpoint like LM Studio or Ollama on port 1234 / 11434).

Why: Incredible instruction-following discipline; outputs pure JSON reliably without conversational fluff.

5. Ideal Project Folder Structure
Modern LLMs can read this exact tree and immediately understand where utility code ends and the execution logic begins.

Plaintext
knowledge-pipeline/
│
├── config/
│   ├── categories.json         # Defines your taxonomies (Marketing, Systems, etc.)
│   └── scrap_keywords.json     # Low-value target words for fuzzy string matching
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main orchestrator (runs the core loops)
│   │
│   ├── extractors/             # Pass 1: Standardizing files
│   │   ├── __init__.py
│   │   ├── pdf_handler.py      # Extracts raw text from PDFs
│   │   └── html_handler.py     # Strips tags from HTML files
│   │
│   ├── processors/             # Pass 2: Analysis
│   │   ├── __init__.py
│   │   ├── fuzzy_matcher.py    # String matching & confidence score algorithms
│   │   └── llm_client.py       # Handles payloads and strict prompts to Qwen 7B
│   │
│   └── utils/
│       ├── __init__.py
│       └── file_io.py          # Handles writing YAML front-matter to files
│
├── requirements.txt            # Python dependencies (pypdf, requests, etc.)
└── README.md                   # System documentation for you and the AI
This layout keeps things highly modular. If your PDF extraction library changes, you only touch pdf_handler.py. If you want to experiment with a different fuzzy string algorithm, you only touch fuzzy_matcher.py. The orchestrator (main.py) just manages the flow of data through the loops.

Does this match the vision you had in your head, or should we tweak how the data passes through the loops before you feed it to the code machine?
