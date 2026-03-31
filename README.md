# Evernote to Markdown Migration Toolkit

**Migrate thousands of Evernote notes to organized Markdown files in minutes, not hours.**

Built by [Evangel Oputa](https://github.com/evoputa) at [Begine Fusion](https://beginefusion.com) & [OnStack AI Labs](https://github.com/OnStack-AI-Labs) after migrating 6,453 notes from 293 Evernote notebooks in a single session.

---

## The Problem

Evernote makes it nearly impossible to leave:
- No bulk export (manual, one-notebook-at-a-time clicking)
- No MCP server for AI integration
- Deprecated developer tokens
- Proprietary format (HTML-in-XML)
- CA$325/year for something your existing cloud storage can do

If you have hundreds of notebooks and thousands of notes, manual migration would take 15-20 hours of clicking. This toolkit does it in **under 30 minutes**.

## What This Toolkit Does

```
Evernote Account
      |
      v
[1. Bulk Download] --> SQLite DB (all notes via API)
      |
      v
[2. ENEX Export] --> .enex files (one per notebook)
      |
      v
[3. Convert to Markdown] --> Organized .md files with YAML frontmatter
      |
      v
[4. Set Up Vault] --> Obsidian-ready system with search, templates, AI export
      |
      v
[5. Organize Stacks] --> Evernote-style Stack > Notebook > Note hierarchy
```

## What You Get

- **Every note** as a clean `.md` file with YAML metadata (title, created, updated, tags, notebook)
- **Every attachment** extracted and linked (images, PDFs, files)
- **Notebook structure** preserved as folders
- **Stack organization** (group folders into stacks, just like Evernote)
- **Full-text search** tool (replaces Evernote search)
- **Quick note capture** tool (replaces Evernote quick note)
- **AI export** tool (JSON/JSONL for embeddings, RAG, LLM pipelines)
- **Obsidian configuration** (templates, bookmarks, daily notes)
- **Works with any Markdown editor** (Obsidian, VS Code, Typora, etc.)

## Requirements

- **Python 3.10+** (tested on 3.11)
- **Evernote account** (any plan)
- **~10 minutes** for download + conversion

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/beginefusion/evernote-to-markdown.git
cd evernote-to-markdown
pip install -r requirements.txt
```

### 2. Get Your Evernote Auth Token

**Option A: Developer Token (if available)**
1. Go to https://www.evernote.com/api/DeveloperToken.action
2. Sign in and create a token
3. Copy the token string

**Option B: Browser Cookie (works for all accounts)**
1. Open https://www.evernote.com/client/ in your browser
2. Sign in to your account
3. Open DevTools (F12) > Application tab > Cookies
4. Find the cookie with a value starting with `S=s###:U=...`
5. Copy that value

### 3. Run the Migration

```bash
# Step 1: Download all notes from Evernote
python scripts/export_evernote.py

# Step 2: Convert to Markdown
python scripts/convert_to_markdown.py --input ./enex_export --output ~/NoteVault

# Step 3: Set up your note system
python scripts/setup_vault.py --vault ~/NoteVault

# Step 4 (optional): Organize into stacks
python scripts/organize_stacks.py --vault ~/NoteVault --config stacks.json
```

Or run everything at once:

```bash
python migrate.py
```

### 4. Open in Obsidian

1. Download [Obsidian](https://obsidian.md) (free)
2. Open vault > select your NoteVault folder
3. Done. All your notes are there.

## Configuration

### Custom Stack Organization

Edit `stacks.json` to define how your notebooks group into stacks:

```json
{
  "Business": [
    "Meeting Notes",
    "Client Projects",
    "Proposals"
  ],
  "Learning": [
    "Courses",
    "Certifications",
    "Book Notes"
  ],
  "Personal": [
    "Journal",
    "Recipes",
    "Travel"
  ]
}
```

### Custom Output Path

```bash
# Output to a cloud-synced folder
python scripts/convert_to_markdown.py --output "C:\Users\you\OneDrive\NoteVault"
python scripts/convert_to_markdown.py --output ~/Dropbox/NoteVault
python scripts/convert_to_markdown.py --output ~/Google\ Drive/NoteVault
```

### AI Export

```bash
# Export all notes as JSON (for RAG, embeddings, knowledge graphs)
python scripts/ai_export.py --vault ~/NoteVault --format json

# Export as JSONL (one note per line, for streaming/batch processing)
python scripts/ai_export.py --vault ~/NoteVault --format jsonl

# Export specific notebook or tag
python scripts/ai_export.py --vault ~/NoteVault --notebook "Meeting Notes"
python scripts/ai_export.py --vault ~/NoteVault --tag "AI"
```

## Output Format

Every note becomes a `.md` file with structured frontmatter:

```markdown
---
title: "Meeting with Client X"
created: "2024-03-15 14:30:00"
updated: "2024-03-16 09:00:00"
notebook: "Client Meetings"
source: "evernote"
tags: ["meeting", "client", "Q1"]
source_url: "https://..."
---

# Meeting with Client X

The actual note content in clean Markdown...

- [x] Action item completed
- [ ] Action item pending

![photo.jpg](_attachments/photo.jpg)
```

## Folder Structure After Migration

```
NoteVault/
  Dashboard.md                  # Homepage with links to all stacks
  _INDEX.md                     # Master index
  _TAG_INDEX.md                 # Browse by tag
  _templates/                   # Note templates
    daily-note.md
    meeting-note.md
    project-note.md
    quick-note.md
  Inbox/                        # Quick capture destination
  Business Stack/               # Stack (group of notebooks)
    Client Projects/            # Notebook (group of notes)
      Meeting Note 1.md         # Note
      Meeting Note 2.md
      _attachments/
        screenshot.png
    Proposals/
      ...
  Personal Stack/
    Journal/
      ...
  search_notes.py               # Full-text search tool
  quick_note.py                 # Quick capture tool
  ai_export.py                  # AI data export tool
```

## Tested Scale

| Metric | Our Migration |
|---|---|
| Notes | 6,453 |
| Notebooks | 293 |
| Attachments | 3,172 |
| Data volume | 2.2 GB |
| Download time | ~25 minutes |
| Conversion time | ~5 minutes |
| Total time | ~30 minutes |
| Errors | 0 |

## Troubleshooting

### Token Error: "Invalid token format"
Make sure you paste the token without surrounding quotes. The token should start with `S=s` not `"S=s`.

### Windows Path Too Long
Some Evernote note titles are very long. The converter automatically truncates filenames to 100 characters. If you still get path errors, try a shorter output path (e.g., `C:\NV` instead of `C:\Users\...\NoteVault`).

### Unicode/Emoji in Note Titles
The converter handles emoji and special characters in note titles. If you see encoding errors on Windows, the converter automatically switches to UTF-8 output.

### OneDrive/Dropbox Lock Errors
Cloud sync services may lock newly created files. The converter gracefully skips cleanup operations that fail due to locks. This doesn't affect your notes.

### Evernote Server Errors During Download
Some notes may fail with `JDBCConnectionException`. These are Evernote server-side issues. Re-run the sync command to retry:
```bash
python -m evernote_backup sync -d evernote_backup.db
```

## Why Not [Alternative]?

| Tool | Issue |
|---|---|
| Evernote's built-in export | Manual, one notebook at a time. 293 notebooks = 15+ hours of clicking. |
| Import2 / CloudHQ | Per-note pricing ($200-500 for large accounts). Still needs API access. |
| Notion import | Imports to another SaaS with its own lock-in. |
| Google Keep | No bulk import. Different use case (sticky notes vs. documents). |
| Copy-paste | Not serious for 6,000+ notes. |

## Contributing

Issues and pull requests welcome. Key areas for contribution:

- [ ] Linux/macOS testing and path handling
- [ ] Additional export formats (HTML, PDF)
- [ ] Notion/Obsidian/Logseq-specific optimizations
- [ ] Web UI for non-technical users
- [ ] Progress bars and ETA display
- [ ] Incremental sync (only convert new/changed notes)

## License

MIT License. Use it, modify it, share it.

## Credits

Built by **Evangel (Ev) Oputa**, Founder of **[Begine Fusion](https://beginefusion.com)** and Co-Founder of **[OnStack AI Labs](https://OnStacklabs.ai)**.

**Begine Fusion** is a digital adoption company. We set up AI, CRM, automation, and growth marketing systems inside businesses, then make sure they actually run.

**OnStack AI Labs** — Calgary's first innovative, structured, collaborative skills and applied AI lab, working across a global ecosystem.

Technical implementation assisted by **Claude Code** (Anthropic).

---

*If this tool saved you from Evernote jail, give it a star and share it with others stuck in the same situation.*
