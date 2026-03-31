"""
Step 4: Set up your Evernote replacement system on OneDrive.
Creates the folder structure, search index, and daily note templates.

Run: python "4_setup_note_system.py"

This creates a complete Obsidian-compatible vault that:
- Syncs via OneDrive (2TB, already mounted)
- Works with any Markdown editor
- Is perfect as data for your AI Architecture
- Has full-text search via index
- Supports tags, links, and attachments
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

VAULT_PATH = os.environ.get("VAULT_PATH", os.path.join(os.path.expanduser("~"), "NoteVault"))

def setup_vault():
    """Set up the complete note vault system."""

    print("=" * 60)
    print("  EVERNOTE REPLACEMENT - Setting Up Your Note System")
    print("=" * 60)

    # Create core structure
    folders = [
        "",                          # Vault root
        "_templates",                # Note templates
        "_archive",                  # Archived notes
        "Inbox",                     # Quick capture (like Evernote inbox)
        "Daily Notes",               # Daily journal/log
        "Projects",                  # Active projects
        "Reference",                 # Reference materials
        "Ideas",                     # Ideas and brainstorms
    ]

    for folder in folders:
        path = os.path.join(VAULT_PATH, folder)
        os.makedirs(path, exist_ok=True)
        print(f"  [OK] {folder or 'Vault root'}")

    # Create Obsidian config (if user wants to use Obsidian)
    create_obsidian_config()

    # Create templates
    create_templates()

    # Create quick-capture script
    create_quick_capture()

    # Create search/index tool
    create_search_tool()

    # Create AI data export tool
    create_ai_export_tool()

    # Generate tag index from migrated notes
    generate_tag_index()

    print("\n" + "=" * 60)
    print("  YOUR EVERNOTE REPLACEMENT IS READY!")
    print("=" * 60)
    print(f"""
  Vault Location: {VAULT_PATH}
  Synced via:     OneDrive (automatic)

  WHAT YOU GET:
  - All {count_notes()} migrated notes in organized folders
  - Full-text search (run: python search_notes.py "query")
  - Quick note capture (run: python quick_note.py "title")
  - Tag index for browsing by topic
  - AI-ready export for your architecture
  - Templates for new notes

  RECOMMENDED: Install Obsidian (free)
  - Download: https://obsidian.md
  - Open vault: File > Open Vault > {VAULT_PATH}
  - All your notes will be browsable with full search,
    graph view, tags, and backlinks
  - Obsidian is 100% local (no cloud lock-in)
  - OneDrive handles the sync

  YOU SAVE: CA$325.49/year (Evernote subscription)
  YOU GAIN: Full ownership of your data as .md files
""")


def count_notes():
    """Count total .md files in vault."""
    count = 0
    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith('.md'):
                count += 1
    return count


def create_obsidian_config():
    """Create Obsidian configuration for optimal setup."""
    obsidian_dir = os.path.join(VAULT_PATH, ".obsidian")
    os.makedirs(obsidian_dir, exist_ok=True)

    # App config
    app_config = {
        "attachmentFolderPath": "_attachments",
        "newFileLocation": "folder",
        "newFileFolderPath": "Inbox",
        "showLineNumber": True,
        "strictLineBreaks": False,
        "readableLineLength": True,
        "defaultViewMode": "source",
        "alwaysUpdateLinks": True,
    }
    with open(os.path.join(obsidian_dir, "app.json"), 'w') as f:
        json.dump(app_config, f, indent=2)

    # Appearance
    appearance = {
        "accentColor": "#7c3aed",
        "theme": "obsidian"
    }
    with open(os.path.join(obsidian_dir, "appearance.json"), 'w') as f:
        json.dump(appearance, f, indent=2)

    # Daily notes config
    daily_notes = {
        "folder": "Daily Notes",
        "format": "YYYY-MM-DD",
        "template": "_templates/daily-note"
    }

    # Core plugins
    core_plugins = [
        "file-explorer", "global-search", "switcher", "graph",
        "backlink", "tag-pane", "page-preview", "templates",
        "daily-notes", "note-composer", "command-palette",
        "editor-status", "outline", "word-count", "file-recovery"
    ]
    with open(os.path.join(obsidian_dir, "core-plugins.json"), 'w') as f:
        json.dump(core_plugins, f, indent=2)

    print("  [OK] Obsidian configuration")


def create_templates():
    """Create note templates."""
    templates_dir = os.path.join(VAULT_PATH, "_templates")

    # Daily note template
    daily = """---
title: "{{date:YYYY-MM-DD}} - Daily Note"
created: "{{date:YYYY-MM-DD HH:mm:ss}}"
type: "daily"
tags: ["daily"]
---

# {{date:YYYY-MM-DD dddd}}

## Tasks
- [ ]

## Notes


## Ideas


## End of Day Review

"""
    with open(os.path.join(templates_dir, "daily-note.md"), 'w') as f:
        f.write(daily)

    # Meeting note template
    meeting = """---
title: "Meeting - {{title}}"
created: "{{date:YYYY-MM-DD HH:mm:ss}}"
type: "meeting"
tags: ["meeting"]
attendees: []
---

# Meeting: {{title}}

**Date:** {{date:YYYY-MM-DD}}
**Attendees:**

## Agenda


## Notes


## Action Items
- [ ]

## Follow-up

"""
    with open(os.path.join(templates_dir, "meeting-note.md"), 'w') as f:
        f.write(meeting)

    # Project note template
    project = """---
title: "{{title}}"
created: "{{date:YYYY-MM-DD HH:mm:ss}}"
type: "project"
tags: ["project"]
status: "active"
---

# {{title}}

## Overview


## Goals


## Tasks
- [ ]

## Resources


## Notes

"""
    with open(os.path.join(templates_dir, "project-note.md"), 'w') as f:
        f.write(project)

    # Quick capture template
    quick = """---
title: "{{title}}"
created: "{{date:YYYY-MM-DD HH:mm:ss}}"
type: "note"
tags: []
---

# {{title}}

"""
    with open(os.path.join(templates_dir, "quick-note.md"), 'w') as f:
        f.write(quick)

    print("  [OK] Note templates (daily, meeting, project, quick)")


def create_quick_capture():
    """Create a quick note capture script."""
    script = '''"""
Quick Note Capture - Replaces Evernote's quick note feature.
Usage: python quick_note.py "Note Title" ["notebook"]

Examples:
  python quick_note.py "Meeting with client"
  python quick_note.py "New idea" "Ideas"
  python quick_note.py "Research findings" "Projects"
"""
import os
import sys
from datetime import datetime

VAULT_PATH = r"{vault_path}"

def quick_note(title=None, notebook="Inbox"):
    if not title:
        title = input("Note title: ").strip()
        if not title:
            title = datetime.now().strftime("Quick Note %Y-%m-%d %H%M")

    # Sanitize
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
    notebook_path = os.path.join(VAULT_PATH, notebook)
    os.makedirs(notebook_path, exist_ok=True)

    filepath = os.path.join(notebook_path, f"{{safe_title}}.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""---
title: "{{title}}"
created: "{{now}}"
type: "note"
tags: []
notebook: "{{notebook}}"
---

# {{title}}

"""

    # Check if note already exists
    if os.path.exists(filepath):
        print(f"Note already exists: {{filepath}}")
        return filepath

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created: {{filepath}}")
    return filepath

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else None
    notebook = sys.argv[2] if len(sys.argv) > 2 else "Inbox"
    quick_note(title, notebook)
'''.replace("{vault_path}", VAULT_PATH)

    with open(os.path.join(VAULT_PATH, "quick_note.py"), 'w') as f:
        f.write(script)

    print("  [OK] Quick capture tool")


def create_search_tool():
    """Create a full-text search tool for the vault."""
    script = '''"""
Full-Text Search for your NoteVault.
Replaces Evernote's search functionality.

Usage:
  python search_notes.py "search query"
  python search_notes.py "query" --tag "meeting"
  python search_notes.py "query" --notebook "Projects"
"""
import os
import sys
import re
from pathlib import Path

VAULT_PATH = r"{vault_path}"

def search(query, tag_filter=None, notebook_filter=None, max_results=50):
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()

    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, VAULT_PATH)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                continue

            content_lower = content.lower()

            # Apply filters
            if notebook_filter:
                if not rel_path.startswith(notebook_filter):
                    continue

            if tag_filter:
                if f'"{tag_filter}"' not in content_lower and tag_filter.lower() not in content_lower:
                    continue

            # Score: how many query words appear
            score = sum(1 for w in query_words if w in content_lower)
            if score == 0:
                continue

            # Bonus for title match
            if query_lower in filename.lower():
                score += 5

            # Get context snippet
            idx = content_lower.find(query_words[0])
            if idx >= 0:
                start = max(0, idx - 50)
                end = min(len(content), idx + 100)
                snippet = content[start:end].replace('\\n', ' ').strip()
                snippet = re.sub(r'\\s+', ' ', snippet)
            else:
                snippet = content[:150].replace('\\n', ' ').strip()

            results.append((score, rel_path, snippet))

    # Sort by score (best first)
    results.sort(key=lambda x: -x[0])

    # Display results
    if not results:
        print(f"  No results found for: {{query}}")
        return

    print(f"\\n  Found {{len(results)}} results for: {{query}}\\n")

    for i, (score, path, snippet) in enumerate(results[:max_results]):
        print(f"  {{i+1}}. [{{score}}] {{path}}")
        print(f"     {{snippet[:120]}}...")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_notes.py \\"search query\\"")
        sys.exit(1)

    query = sys.argv[1]
    tag = None
    notebook = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--tag" and i + 1 < len(sys.argv):
            tag = sys.argv[i + 1]
        if arg == "--notebook" and i + 1 < len(sys.argv):
            notebook = sys.argv[i + 1]

    search(query, tag, notebook)
'''.replace("{vault_path}", VAULT_PATH)

    with open(os.path.join(VAULT_PATH, "search_notes.py"), 'w') as f:
        f.write(script)

    print("  [OK] Full-text search tool")


def create_ai_export_tool():
    """Create a tool to export notes for AI Architecture consumption."""
    script = '''"""
AI Data Export Tool - Export your NoteVault for AI Architecture use.
Creates structured JSON/JSONL files optimized for AI ingestion.

Usage:
  python ai_export.py                     # Export all notes
  python ai_export.py --notebook "Projects"  # Export specific notebook
  python ai_export.py --tag "meeting"     # Export by tag
  python ai_export.py --format jsonl      # Export as JSONL (for embeddings)
"""
import os
import sys
import json
import re
from datetime import datetime

VAULT_PATH = r"{vault_path}"
EXPORT_DIR = os.path.join(VAULT_PATH, "_ai_exports")

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    metadata = {{}}
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm = content[3:end].strip()
            for line in fm.split('\\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    val = val.strip().strip('"').strip("'")
                    if val.startswith('[') and val.endswith(']'):
                        val = [v.strip().strip('"').strip("'")
                               for v in val[1:-1].split(',') if v.strip()]
                    metadata[key.strip()] = val
            body = content[end+3:].strip()
        else:
            body = content
    else:
        body = content
    return metadata, body

def export_for_ai(notebook_filter=None, tag_filter=None, fmt="json"):
    os.makedirs(EXPORT_DIR, exist_ok=True)

    notes = []
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '_ai_exports']
        for filename in files:
            if not filename.endswith('.md') or filename.startswith('_'):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, VAULT_PATH)

            if notebook_filter and not rel_path.startswith(notebook_filter):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                continue

            metadata, body = parse_frontmatter(content)

            if tag_filter:
                tags = metadata.get('tags', [])
                if isinstance(tags, str):
                    tags = [tags]
                if tag_filter not in tags:
                    continue

            note = {{
                "id": rel_path.replace(os.sep, '/'),
                "title": metadata.get('title', filename[:-3]),
                "content": body,
                "metadata": metadata,
                "notebook": metadata.get('notebook', os.path.dirname(rel_path)),
                "tags": metadata.get('tags', []),
                "created": metadata.get('created', ''),
                "updated": metadata.get('updated', ''),
                "char_count": len(body),
                "word_count": len(body.split()),
            }}
            notes.append(note)

    # Export
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if fmt == "jsonl":
        output_file = os.path.join(EXPORT_DIR, f"notes_{{timestamp}}.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            for note in notes:
                f.write(json.dumps(note, ensure_ascii=False) + '\\n')
    else:
        output_file = os.path.join(EXPORT_DIR, f"notes_{{timestamp}}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({{
                "export_date": datetime.now().isoformat(),
                "total_notes": len(notes),
                "notes": notes
            }}, f, ensure_ascii=False, indent=2)

    print(f"\\n  Exported {{len(notes)}} notes to: {{output_file}}")
    print(f"  Format: {{fmt.upper()}}")

    # Stats
    total_words = sum(n['word_count'] for n in notes)
    total_chars = sum(n['char_count'] for n in notes)
    print(f"  Total words: {{total_words:,}}")
    print(f"  Total characters: {{total_chars:,}}")
    print(f"  Ready for AI ingestion!")

if __name__ == "__main__":
    notebook = None
    tag = None
    fmt = "json"

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--notebook" and i + 1 <= len(sys.argv) - 1:
            notebook = sys.argv[i + 1]
        elif arg == "--tag" and i + 1 <= len(sys.argv) - 1:
            tag = sys.argv[i + 1]
        elif arg == "--format" and i + 1 <= len(sys.argv) - 1:
            fmt = sys.argv[i + 1]

    export_for_ai(notebook, tag, fmt)
'''.replace("{vault_path}", VAULT_PATH)

    with open(os.path.join(VAULT_PATH, "ai_export.py"), 'w') as f:
        f.write(script)

    print("  [OK] AI Architecture export tool")


def generate_tag_index():
    """Scan all migrated notes and build a tag index."""
    tag_map = {}  # tag -> list of note paths

    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, VAULT_PATH)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    # Read just the frontmatter
                    content = f.read(2000)
            except Exception:
                continue

            # Extract tags from frontmatter
            if 'tags:' in content:
                tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
                if tags_match:
                    tags_str = tags_match.group(1)
                    tags = [t.strip().strip('"').strip("'")
                            for t in tags_str.split(',') if t.strip()]
                    for tag in tags:
                        if tag not in tag_map:
                            tag_map[tag] = []
                        tag_map[tag].append(rel_path)

    if not tag_map:
        print("  [OK] Tag index (no tags found yet - will populate after migration)")
        return

    # Write tag index
    index_content = f"""---
title: "Tag Index"
created: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
type: "index"
---

# Tag Index

Total unique tags: {len(tag_map)}

"""
    for tag in sorted(tag_map.keys()):
        notes = tag_map[tag]
        index_content += f"\n## #{tag} ({len(notes)} notes)\n\n"
        for note_path in sorted(notes)[:20]:  # Show first 20
            note_name = Path(note_path).stem
            index_content += f"- [[{note_path.replace(os.sep, '/')}|{note_name}]]\n"
        if len(notes) > 20:
            index_content += f"- ... and {len(notes) - 20} more\n"

    with open(os.path.join(VAULT_PATH, "_TAG_INDEX.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"  [OK] Tag index ({len(tag_map)} unique tags)")


# Import re at top level
import re

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Set up Obsidian-ready note vault.")
    parser.add_argument("--vault", "-v", default=VAULT_PATH, help="Vault path (default: ~/NoteVault)")
    args = parser.parse_args()
    VAULT_PATH = args.vault
    setup_vault()
