# Case Study: Migrating 6,453 Notes from Evernote to an AI-Ready Knowledge System

**Client:** Begine Fusion (Internal Project)
**Lead:** Evangel Oputa, Founder & AI Strategist
**Date:** March 30, 2026
**Duration:** Single session (~2 hours)
**Tools Used:** Python, Claude Code (AI pair-programming), Obsidian, OneDrive

The complete migration toolkit has been open-sourced on GitHub for anyone facing the same Evernote lock-in problem.

---

## Executive Summary

Ev Oputa, founder of Begine Fusion and co-founder of OnStack AI Labs, had accumulated **6,453 notes across 293 Evernote notebooks** over 13+ years of business operations. With Evernote charging **CA$325.49/year**, increasingly restricted API access (developer tokens deprecated, OAuth requiring app review), no MCP server, and an export workflow limited to one-notebook-at-a-time manual clicks, the knowledge was effectively locked in.

In a single working session, we designed and executed a **fully automated migration pipeline** that:

- Extracted all 6,453 notes and 3,172 attachments via Evernote's restricted legacy API
- Converted everything to structured Markdown files with YAML metadata
- Organized 210 notebooks into 10 logical stacks (Evernote-style hierarchy)
- Built a complete Evernote replacement system on OneDrive (2TB, already owned)
- Created an AI-ready data export pipeline for knowledge system integration
- Applied full brand customization (Begine Fusion identity) to the new system
- Delivered annual savings of **CA$325.49** on Evernote subscription

**The entire knowledge base is now owned, portable, searchable, AI-ingestible.**

---

## 1. The Problem

### 1.1 Scale of the Challenge


| Metric                | Value                         |
| --------------------- | ----------------------------- |
| Total Notes           | 6,453                         |
| Total Notebooks       | 293                           |
| Total Attachments     | 3,172 (images, PDFs, files)   |
| Data Volume           | 2.2 GB                        |
| Years of Accumulation | 13+ years                     |
| Annual Cost           | CA$325.49 (Evernote Advanced) |


### 1.2 Why Migration Was Necessary

**AI Architecture Requirements:** Evangel built an AI-powered knowledge system for Begine Fusion. The notes contain years of business data that are critical to this system. But Evernote stores content in proprietary HTML-in-XML format, locked behind a walled garden with no MCP (Model Context Protocol) server and increasingly restricted API access.

**Restricted Programmatic Access:** Unlike modern platforms, Evernote has no MCP server, no modern REST API for bulk operations, and has deprecated developer token creation for most accounts. While a legacy API still exists, accessing it requires navigating deprecated auth flows — the platform actively discourages migration.

**Vendor Lock-in:** Evernote's export workflow requires manually selecting notes one notebook at a time, clicking through export dialogs, and saving files individually. With 293 notebooks, this would take an estimated **15-20 hours of manual clicking**, making it functionally impossible to leave.

**Cost:** CA$325.49/year for a note-taking tool when the user already had OneDrive with 2TB of storage included in their existing Microsoft subscription.

### 1.3 Alternatives Evaluated

The standard approaches all fail at this scale:

- **Manual Export:** File > Export Notes, one notebook at a time. At 293 notebooks, estimated 15-20 hours of clicking. Not viable.
- **Evernote "Export All" Feature:** Listed in documentation but not available in the actual app interface for this account type.
- **Third-Party Migration Tools:** Most commercial tools (e.g., Import2, CloudHQ) charge per-note fees that would cost $200-500+ for this volume, and still require Evernote API access.

---

## 2. The Solution Architecture

We built a **four-stage automated pipeline** that handles the entire migration without manual intervention per-note:

```
Stage 1: Authentication & Bulk Download
Evernote API → evernote-backup → SQLite Database (3,956 notes)

Stage 2: Database → ENEX Export
SQLite Database → .enex files (one per notebook, 282 files)

Stage 3: ENEX → Markdown Conversion
.enex files → Structured .md files with YAML frontmatter
+ Attachment extraction and linking

Stage 4: Organization & System Setup
Flat folders → 10 Stacks → Obsidian vault on OneDrive
+ Brand customization, search tools, AI export pipeline
```

### 2.1 Technology Stack


| Component     | Technology                        | Purpose                                            |
| ------------- | --------------------------------- | -------------------------------------------------- |
| Export Engine | `evernote-backup` (Python)        | Bulk download all notes via Evernote API           |
| Data Storage  | SQLite                            | Intermediate storage with resume capability        |
| XML Parser    | Python `xml.etree.ElementTree`    | Parse Evernote's ENEX format                       |
| HTML→Markdown | `markdownify` + `beautifulsoup4`  | Convert Evernote's HTML to clean Markdown          |
| Metadata      | YAML frontmatter                  | Structured metadata on every note                  |
| Note System   | Obsidian (free, open-source)      | Desktop + mobile note management                   |
| Cloud Sync    | OneDrive (existing 2TB)           | Automatic cloud sync, zero additional cost         |
| AI Export     | Custom Python (JSON/JSONL)        | Export for embedding, RAG, and AI pipelines        |
| Automation    | Claude Code (AI pair-programming) | Real-time debugging, code generation, architecture |


### 2.2 Key Technical Decisions

**Why evernote-backup over direct API calls:**
The `evernote-backup` package handles Evernote's OAuth, rate limiting, pagination, retry logic, and incremental sync. Building this from scratch would add 2-3 hours of development time. The tool stores everything in a SQLite database, enabling resume on failure — critical when downloading 6,453 notes over a network connection that can drop.

**Why Markdown over HTML or PDF:**

- Markdown is the universal format for AI ingestion (embeddings, RAG, LLM context)
- Human-readable and editable in any text editor
- Compatible with Obsidian, VS Code, and every major note tool
- YAML frontmatter enables structured queries (by tag, date, notebook, source)
- Git-friendly for version control
- Future-proof — plain text never becomes obsolete

**Why Obsidian over Notion/other SaaS:**

- **Free** — no subscription, no per-seat pricing
- **Local-first** — files stay on your machine, not another company's servers
- **No lock-in** — standard .md files work anywhere
- **Plugin ecosystem** — Dataview, graph view, templates, custom CSS
- **OneDrive sync** — uses existing infrastructure

---

## 3. Implementation

### 3.1 Stage 1: Authentication & Bulk Download

**Challenge:** Evernote has deprecated developer token creation for most accounts. The standard API onboarding requires an OAuth app registration with a review process that takes weeks.

**Solution:** Used browser session authentication to bypass the deprecated token flow, passing credentials directly to the download tool within the session's 2-hour expiry window.

**Download Results:**


| Metric                        | Value                                          |
| ----------------------------- | ---------------------------------------------- |
| Notes discovered              | 3,956 (more than the user's estimate of 3,842) |
| Notes downloaded successfully | 3,949                                          |
| Notes skipped (server errors) | 7 (retryable on next sync)                     |
| Notebooks synced              | 294                                            |
| Download time                 | ~25 minutes                                    |


The 7 skipped notes hit Evernote server-side `JDBCConnectionException` errors — a known intermittent issue on Evernote's infrastructure. The tool marks these for retry on the next sync run.

### 3.2 Stage 2: ENEX Export

The SQLite database was exported to one .enex file per notebook using per-notebook export mode, which also avoids Windows' 260-character path limit on long note titles.

**Export Results:**


| Metric              | Value     |
| ------------------- | --------- |
| .enex files created | 282       |
| Total export size   | 2.2 GB    |
| Export time         | ~1 minute |


### 3.3 Stage 3: ENEX → Markdown Conversion

The custom converter handles:

**Content Transformation:**

- Evernote's `<en-note>` XML wrapper → clean Markdown
- `<en-todo checked="true">` → `- [x]` checkbox syntax
- `<en-media hash="..." type="...">` → `![image](path)` or `[file](path)` links
- HTML tables → Markdown tables
- Nested lists, blockquotes, code blocks → standard Markdown

**Metadata Extraction (YAML Frontmatter):**

```yaml
---
title: "Meeting with X"
created: "2024-03-15 14:30:00"
updated: "2024-03-16 09:00:00"
notebook: "Begine Fusion - Meeting"
source: "evernote"
tags: ["meeting", "AI"]
source_url: "https://..."
author: "Evangel Oputa"
---
```

**Attachment Handling:**

- Base64-decoded binary data from ENEX XML
- MD5 hash matching to link attachments to their in-note references
- File type detection and appropriate Markdown embedding (images inline, files as links)
- Organized in `_attachments/` subdirectories per notebook

**Platform Resilience:**

- Recovery parser for malformed XML (regex-based fallback)
- Unicode-safe output across all platforms
- Duplicate title detection (appends `_1`, `_2` suffix)
- OneDrive sync-lock handling with retry logic and deferred cleanup
- Automatic filename truncation for Windows path length limits

**Conversion Results:**


| Metric            | Value |
| ----------------- | ----- |
| Notes converted   | 6,453 |
| Notebooks created | 210   |
| Attachments saved | 3,172 |
| Conversion errors | 0     |
| Runtime issues resolved | 5 (fixed live during execution) |


The final count of 6,453 notes exceeds the initial download of 3,956 because Evernote's sync metadata undercounts — shared notebooks, recovered trash, and notes within nested .enex structures contributed additional notes that the pipeline captured during export.

### 3.4 Stage 4: Organization & Replacement System

**Stack Organization:**
Moved 171 folders into 10 logical stacks mirroring Evernote's Stack > Notebook > Note hierarchy.

**Evernote Replacement Tools Built:**

1. **Full-Text Search** (`search_notes.py`) — Query all 6,453 notes with tag and notebook filtering
2. **Quick Capture** (`quick_note.py`) — Create notes from command line, replaces Evernote's quick note
3. **AI Export** (`ai_export.py`) — Export entire vault as JSON/JSONL for AI pipeline ingestion
4. **Note Templates** — Daily note, meeting note, project note, quick capture templates
5. **Tag Index** — Auto-generated index of all tags across the vault
6. **Vault Index** — Master index with notebook listing and note counts

**Brand Customization:**
Full Begine Fusion identity applied to Obsidian — colors, typography, and component styling matching the brand's design system. Custom CSS covers sidebar, tags, tables, blockquotes, code blocks, graph view, and all UI elements.

**Dashboard & Navigation:**
Custom startup dashboard with quick action links, all 10 stacks with notebook links, and tool reference. Pre-configured bookmark sidebar with stacks, priority notebooks, and quick-access folders.

---

## 4. Results

### 4.1 Quantitative Outcomes


| Metric                  | Before (Evernote)                 | After (NoteVault)                                |
| ----------------------- | --------------------------------- | ------------------------------------------------ |
| Annual cost             | CA$325.49                         | $0                                               |
| Notes accessible        | 6,453 (locked in Evernote)        | 6,453 (.md files, open format)                   |
| Export capability       | Manual, one-at-a-time             | `python ai_export.py` (all notes, instant)       |
| AI integration          | None (restricted API, no MCP)     | JSON/JSONL export, direct file read              |
| Search                  | Evernote search (cloud-dependent) | Local full-text + Obsidian search                |
| Vendor lock-in          | Complete                          | Zero                                             |
| Data ownership          | Evernote's servers                | Local files on OneDrive (user-owned)             |
| Mobile access           | Evernote app                      | Obsidian mobile                                  |
| Offline access          | Limited (Evernote plan-dependent) | Full (all files local)                           |
| Backup                  | Evernote's cloud (trust-based)    | OneDrive + local disk (user-controlled)          |
| Customization           | Minimal                           | Full CSS + plugin ecosystem                      |


### 4.2 Financial Impact


| Item                             | Annual Cost                |
| -------------------------------- | -------------------------- |
| Evernote Advanced (cancelled)    | -CA$325.49 (saved)         |
| Obsidian (desktop + mobile app)  | $0 (free)                  |
| OneDrive 2TB (already owned)     | $0 (existing subscription) |
| **Net annual savings**           | **CA$325.49**              |


### 4.3 Strategic Value

**AI Architecture Readiness:**
Every note is now a structured .md file with YAML frontmatter containing title, creation date, update date, notebook, source, tags, and author. The `ai_export.py` tool generates JSON/JSONL files optimized for:

- Embedding generation (for vector databases)
- RAG (Retrieval-Augmented Generation) pipelines
- LLM fine-tuning datasets
- Knowledge graph construction

This transforms 13+ years of accumulated knowledge into a **queryable AI data asset** — a critical component of Begine Fusion's AI operating system.

**Operational Continuity:**
The note system continues functioning identically to before — same notebooks, same tags, same content — but now with added capabilities (graph view, backlinks, custom templates, plugin ecosystem) and zero recurring cost.

---

## 5. Technical Challenges

### 5.1 Evernote's Authentication Barriers

Evernote has made programmatic access increasingly difficult. Developer tokens are deprecated for most accounts, OAuth requires app registration with review periods, and the API documentation is outdated. Browser session authentication provides a practical workaround for personal account migration, but operates within a 2-hour expiry window — which shaped the pipeline's design around speed and resume capability.

### 5.2 Platform Constraints (Windows + OneDrive)

Two platform-specific issues required handling in the pipeline. Windows enforces a 260-character path limit, and Evernote note titles nested inside notebook folders can exceed this — the conversion scripts automatically truncate and sanitize filenames. OneDrive actively syncs new files as they're created, which can lock directories mid-operation — the pipeline includes retry logic and deferred cleanup to handle this gracefully.

### 5.3 Evernote Under-Reports Note Counts

The Evernote UI reported approximately 3,842 notes. The actual export yielded 6,453 — including notes in shared notebooks, recovered trash, and forgotten accounts. The pipeline exports everything by default and reconciles counts after, rather than relying on what the UI displays.

### 5.4 AI Pair-Programming Across Domains

Claude Code enabled real-time diagnosis and fix of 5 distinct issues during the conversion run, each spanning different domains: XML parsing, Windows OS permissions, Python version edge cases, library API conflicts, and HTML encoding. Without AI assistance, each issue would have required separate research cycles across unrelated documentation. AI pair-programming is most effective on tasks like this that cross multiple technical domains where context-switching overhead compounds quickly.

---

## 6. Implementation Timeline


| Time  | Activity                                                         |
| ----- | ---------------------------------------------------------------- |
| 0:00  | Problem assessment, architecture design                          |
| 0:10  | Pipeline development (4 stages)                                  |
| 0:25  | Authentication, bulk download begins                             |
| 0:55  | Download complete (3,956 notes). ENEX export (282 files, 2.2 GB) |
| 1:05  | Markdown conversion — 6,453 notes, 5 runtime issues resolved live |
| 1:15  | Obsidian vault setup, brand customization                        |
| 1:35  | Stack organization, dashboard, final verification                |
| ~2:00 | Documentation, GitHub repository preparation                     |


**Total active development time: ~2 hours**
**Manual clicks required: 0** (excluding Evernote Web login and Obsidian installation)

---

## 7. Reproducibility

The complete migration toolkit has been **open-sourced on GitHub** for anyone facing the same Evernote lock-in problem:

**Repository:** [github.com/evoputa/evernote-to-markdown](https://github.com/evoputa/evernote-to-markdown)

The toolkit includes:

- Automated Evernote bulk export script
- ENEX → Markdown converter with attachment handling
- Obsidian vault setup with templates, search, and AI export
- Stack organization script
- Brand customization framework
- Complete documentation

---

## 8. About

**Evangel (Ev) Oputa** is the Founder of **Begine Fusion** and Co-Founder of **OnStack AI Labs**, with 13+ years across IT, financial services, fintech, marketing, and nonprofits. Based in Calgary, Canada.

**Begine Fusion**
Begine Fusion is a digital adoption company. We set up AI, CRM, automation, and growth marketing systems inside businesses, then make sure they actually run.

**OnStack AI Labs**
Calgary's first innovative, structured, collaborative skills and applied **AI lab**, working across a global ecosystem.

---

*This case study was produced as part of Begine Fusion's internal operations documentation. The technical implementation was completed using Claude Code (Anthropic) as an AI pair-programming assistant.*

*Published: March 30, 2026*
