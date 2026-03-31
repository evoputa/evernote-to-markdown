"""
Step 3: Convert all exported .enex files to organized Markdown (.md) files.
Preserves notebook structure, tags, metadata, and attachments.

Run: python "3_convert_to_markdown.py"

Input:  .enex files from Step 2 (or manually exported)
Output: Organized .md files in your OneDrive vault
"""
import os
import re
import sys
import json
import base64
import hashlib

# Fix Windows console encoding for emoji/unicode in note titles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='replace', buffering=1)
import mimetypes
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not installed
    def tqdm(iterable, **kwargs):
        desc = kwargs.get('desc', '')
        total = kwargs.get('total', None)
        for i, item in enumerate(iterable):
            if total:
                print(f"\r  {desc}: {i+1}/{total}", end='', flush=True)
            yield item
        print()

try:
    import markdownify
    HAS_MARKDOWNIFY = True
except ImportError:
    HAS_MARKDOWNIFY = False

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False

from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# ============================================================
# CONFIGURATION - Adjust these paths as needed
# ============================================================

SOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))

# Where your .enex files are (from Step 2)
ENEX_INPUT_DIR = os.environ.get("ENEX_INPUT_DIR", os.path.join(SOLUTION_DIR, "..", "enex_export"))

# Where the markdown vault will be created
# Override with: --output flag or VAULT_PATH environment variable
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.join(os.path.expanduser("~"), "NoteVault"))

# Attachments subfolder inside each notebook folder
ATTACHMENTS_DIR = "_attachments"

# Maximum filename length (Windows limit is 255, but paths have limits too)
MAX_FILENAME_LENGTH = 100

# ============================================================
# HELPERS
# ============================================================

def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    if not name:
        return "Untitled"
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.strip('.')
    if len(name) > MAX_FILENAME_LENGTH:
        name = name[:MAX_FILENAME_LENGTH].strip()
    if not name:
        return "Untitled"
    return name


def evernote_date_to_iso(date_str):
    """Convert Evernote date format (20231215T143022Z) to ISO."""
    if not date_str:
        return None
    try:
        # Evernote format: YYYYMMDDTHHmmssZ
        dt = datetime.strptime(date_str.strip(), "%Y%m%dT%H%M%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            dt = dateparser.parse(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else date_str
        except Exception:
            return date_str


def html_to_markdown(html_content):
    """Convert Evernote HTML content to clean Markdown."""
    if not html_content:
        return ""

    # Pre-process Evernote-specific elements
    # Remove en-note wrapper
    html_content = re.sub(r'</?en-note[^>]*>', '', html_content)

    # Convert en-todo checkboxes
    html_content = re.sub(
        r'<en-todo\s+checked="true"\s*/?>', '- [x] ', html_content
    )
    html_content = re.sub(
        r'<en-todo\s+checked="false"\s*/?>', '- [ ] ', html_content
    )
    html_content = re.sub(r'<en-todo\s*/?>', '- [ ] ', html_content)

    # Handle en-media (attachments) - replace with placeholder
    html_content = re.sub(
        r'<en-media[^>]*hash="([^"]*)"[^>]*type="([^"]*)"[^>]*/?>',
        r'![attachment-\1](\2)',
        html_content
    )

    # Convert using markdownify (preferred) or html2text
    if HAS_MARKDOWNIFY:
        md = markdownify.markdownify(
            html_content,
            heading_style="ATX",
            bullets="-",
            strip=['style', 'script'],
        )
    elif HAS_HTML2TEXT:
        converter = html2text.HTML2Text()
        converter.body_width = 0  # No line wrapping
        converter.protect_links = True
        converter.unicode_snob = True
        md = converter.handle(html_content)
    else:
        # Last resort: BeautifulSoup text extraction
        soup = BeautifulSoup(html_content, 'html.parser')
        md = soup.get_text(separator='\n')

    # Clean up excessive whitespace
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    md = md.strip()

    return md


def get_text(element, tag, default=""):
    """Safely get text from an XML element."""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default


# ============================================================
# ENEX PARSER
# ============================================================

def parse_enex_file(enex_path):
    """Parse an .enex file and yield note dictionaries."""
    print(f"\n  Parsing: {os.path.basename(enex_path)}")

    try:
        # Parse with iterparse for memory efficiency on large files
        context = ET.iterparse(enex_path, events=('end',))
        note_count = 0

        for event, elem in context:
            if elem.tag == 'note':
                note = extract_note(elem)
                if note:
                    note_count += 1
                    yield note
                # Free memory
                elem.clear()

        print(f"    Found {note_count} notes")

    except ET.ParseError as e:
        print(f"  [WARNING] XML parse error in {enex_path}: {e}")
        # Try recovery parsing
        yield from parse_enex_recovery(enex_path)


def parse_enex_recovery(enex_path):
    """Recovery parser for malformed .enex files."""
    print("    Attempting recovery parse...")
    try:
        with open(enex_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find all <note>...</note> blocks
        note_pattern = re.compile(r'<note>(.*?)</note>', re.DOTALL)
        matches = note_pattern.findall(content)

        for match in matches:
            try:
                note_xml = f'<note>{match}</note>'
                elem = ET.fromstring(note_xml)
                note = extract_note(elem)
                if note:
                    yield note
            except ET.ParseError:
                continue

        print(f"    Recovery found {len(matches)} notes")
    except Exception as e:
        print(f"    Recovery failed: {e}")


def extract_note(elem):
    """Extract note data from an XML element."""
    note = {
        'title': get_text(elem, 'title', 'Untitled'),
        'content': get_text(elem, 'content'),
        'created': get_text(elem, 'created'),
        'updated': get_text(elem, 'updated'),
        'tags': [],
        'attributes': {},
        'resources': []
    }

    # Extract tags
    for tag_elem in elem.findall('tag'):
        if tag_elem.text:
            note['tags'].append(tag_elem.text.strip())

    # Extract note attributes
    attrs = elem.find('note-attributes')
    if attrs is not None:
        for attr in attrs:
            if attr.text:
                note['attributes'][attr.tag] = attr.text.strip()

    # Extract resources (attachments)
    for res in elem.findall('resource'):
        resource = extract_resource(res)
        if resource:
            note['resources'].append(resource)

    return note


def extract_resource(res_elem):
    """Extract a resource (attachment) from an XML element."""
    resource = {
        'data': None,
        'mime': get_text(res_elem, 'mime', 'application/octet-stream'),
        'filename': None,
        'hash': None,
        'width': None,
        'height': None,
    }

    # Get the binary data
    data_elem = res_elem.find('data')
    if data_elem is not None and data_elem.text:
        encoding = data_elem.get('encoding', 'base64')
        try:
            if encoding == 'base64':
                # Clean up whitespace in base64 data
                clean_data = re.sub(r'\s+', '', data_elem.text)
                resource['data'] = base64.b64decode(clean_data)
            else:
                resource['data'] = data_elem.text.encode('utf-8')
        except Exception:
            resource['data'] = None

    # Compute hash for matching with en-media tags
    if resource['data']:
        resource['hash'] = hashlib.md5(resource['data']).hexdigest()

    # Get filename from resource attributes
    res_attrs = res_elem.find('resource-attributes')
    if res_attrs is not None:
        resource['filename'] = get_text(res_attrs, 'file-name')
        resource['width'] = get_text(res_attrs, 'width')
        resource['height'] = get_text(res_attrs, 'height')

    # Generate filename if missing
    if not resource['filename'] and resource['hash']:
        ext = mimetypes.guess_extension(resource['mime']) or '.bin'
        resource['filename'] = f"attachment_{resource['hash'][:8]}{ext}"

    return resource


# ============================================================
# MARKDOWN WRITER
# ============================================================

def note_to_markdown(note, notebook_name, attachments_dir):
    """Convert a parsed note to a Markdown string with YAML frontmatter."""

    # Build YAML frontmatter
    frontmatter_fields = []
    safe_title = note['title'].replace('"', "'")
    frontmatter_fields.append(f'title: "{safe_title}"')

    if note['created']:
        frontmatter_fields.append(f"created: \"{evernote_date_to_iso(note['created'])}\"")
    if note['updated']:
        frontmatter_fields.append(f"updated: \"{evernote_date_to_iso(note['updated'])}\"")

    frontmatter_fields.append(f"notebook: \"{notebook_name}\"")
    frontmatter_fields.append(f"source: \"evernote\"")

    if note['tags']:
        tags_yaml = ", ".join(f'"{t}"' for t in note['tags'])
        frontmatter_fields.append(f"tags: [{tags_yaml}]")

    if note['attributes'].get('source-url'):
        frontmatter_fields.append(f"source_url: \"{note['attributes']['source-url']}\"")

    if note['attributes'].get('author'):
        frontmatter_fields.append(f"author: \"{note['attributes']['author']}\"")

    frontmatter = "---\n" + "\n".join(frontmatter_fields) + "\n---\n\n"

    # Convert HTML content to Markdown
    content_md = html_to_markdown(note['content'])

    # Fix attachment references
    resource_map = {}
    for res in note['resources']:
        if res['hash'] and res['filename']:
            resource_map[res['hash']] = res['filename']

    # Replace attachment placeholders with proper links
    for hash_val, filename in resource_map.items():
        rel_path = f"{ATTACHMENTS_DIR}/{filename}"
        # Image types get embedded, others get linked
        if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']):
            content_md = content_md.replace(
                f'![attachment-{hash_val}]',
                f'![{filename}]({rel_path})'
            )
        else:
            content_md = content_md.replace(
                f'![attachment-{hash_val}]',
                f'[{filename}]({rel_path})'
            )

    # Clean up any remaining attachment placeholders
    content_md = re.sub(
        r'!\[attachment-[a-f0-9]+\]\([^)]+\)',
        '[attachment]',
        content_md
    )

    return frontmatter + content_md


def save_attachments(note, attachments_path):
    """Save note attachments to disk."""
    saved = []
    for res in note['resources']:
        if res['data'] and res['filename']:
            filepath = os.path.join(attachments_path, sanitize_filename(res['filename']))
            # Handle duplicate filenames
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filepath)
                counter = 1
                while os.path.exists(f"{name}_{counter}{ext}"):
                    counter += 1
                filepath = f"{name}_{counter}{ext}"

            try:
                with open(filepath, 'wb') as f:
                    f.write(res['data'])
                saved.append(filepath)
            except Exception as e:
                print(f"      [WARN] Could not save attachment {res['filename']}: {e}")

    return saved


# ============================================================
# MAIN CONVERSION
# ============================================================

def find_enex_files(input_dir):
    """Find all .enex files recursively."""
    enex_files = []
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith('.enex'):
                enex_files.append(os.path.join(root, f))
    return enex_files


def determine_notebook_name(enex_path, input_dir):
    """Determine the notebook name from the .enex file path."""
    # evernote-backup creates: output/Notebook Name/Notebook Name.enex
    # or sometimes: output/Notebook Name.enex
    rel_path = os.path.relpath(enex_path, input_dir)
    parts = Path(rel_path).parts

    if len(parts) > 1:
        # In a subdirectory = notebook name is the directory
        return parts[0]
    else:
        # Just a file = notebook name is the filename without extension
        return Path(enex_path).stem


def convert_all():
    """Main conversion function."""

    print("=" * 60)
    print("  EVERNOTE MIGRATION - Step 3: Convert to Markdown")
    print("=" * 60)

    # Check for alternative input locations
    if not os.path.exists(ENEX_INPUT_DIR):
        os.makedirs(ENEX_INPUT_DIR, exist_ok=True)

    # Find all .enex files
    enex_files = find_enex_files(ENEX_INPUT_DIR)

    if not enex_files:
        # Also check the solution directory root
        enex_files = find_enex_files(SOLUTION_DIR)

    if not enex_files:
        print(f"\n  [ERROR] No .enex files found!")
        print(f"  Expected location: {ENEX_INPUT_DIR}")
        print(f"  Please run Step 2 first, or manually place .enex files there.")
        print(f"\n  You can also place them anywhere in: {SOLUTION_DIR}")
        return

    print(f"\n  Found {len(enex_files)} .enex file(s)")
    print(f"  Output vault: {VAULT_PATH}")

    # Create vault structure
    os.makedirs(VAULT_PATH, exist_ok=True)

    # Stats
    total_notes = 0
    total_attachments = 0
    notebooks_created = set()
    errors = []
    title_counts = {}  # Track duplicate titles per notebook

    # Process each .enex file
    for enex_path in enex_files:
        notebook_name = determine_notebook_name(enex_path, ENEX_INPUT_DIR)
        safe_notebook = sanitize_filename(notebook_name)
        notebook_dir = os.path.join(VAULT_PATH, safe_notebook)
        attachments_dir = os.path.join(notebook_dir, ATTACHMENTS_DIR)

        os.makedirs(notebook_dir, exist_ok=True)
        os.makedirs(attachments_dir, exist_ok=True)
        notebooks_created.add(safe_notebook)

        # Track titles in this notebook for dedup
        if safe_notebook not in title_counts:
            title_counts[safe_notebook] = {}

        # Parse and convert each note
        for note in parse_enex_file(enex_path):
            try:
                # Generate filename from title
                safe_title = sanitize_filename(note['title'])

                # Handle duplicate titles in same notebook
                if safe_title in title_counts[safe_notebook]:
                    title_counts[safe_notebook][safe_title] += 1
                    safe_title = f"{safe_title}_{title_counts[safe_notebook][safe_title]}"
                else:
                    title_counts[safe_notebook][safe_title] = 0

                filename = f"{safe_title}.md"
                filepath = os.path.join(notebook_dir, filename)

                # Convert to markdown
                md_content = note_to_markdown(note, notebook_name, attachments_dir)

                # Write the markdown file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                # Save attachments
                if note['resources']:
                    saved = save_attachments(note, attachments_dir)
                    total_attachments += len(saved)

                total_notes += 1

            except Exception as e:
                errors.append(f"{notebook_name}/{note.get('title', 'Unknown')}: {e}")
                continue

    # Clean up empty attachment directories
    for root, dirs, files in os.walk(VAULT_PATH):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if d == ATTACHMENTS_DIR and not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except (PermissionError, OSError):
                pass  # OneDrive may be syncing, skip

    # Generate vault index
    generate_vault_index(VAULT_PATH, notebooks_created, total_notes)

    # Report
    print("\n" + "=" * 60)
    print("  CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"  Notes converted:    {total_notes}")
    print(f"  Notebooks created:  {len(notebooks_created)}")
    print(f"  Attachments saved:  {total_attachments}")
    print(f"  Errors:             {len(errors)}")
    print(f"  Vault location:     {VAULT_PATH}")
    print("=" * 60)

    if errors:
        error_log = os.path.join(SOLUTION_DIR, "conversion_errors.log")
        with open(error_log, 'w', encoding='utf-8') as f:
            for err in errors:
                f.write(f"{err}\n")
        print(f"\n  Error log saved to: {error_log}")

    print(f"\n  Next step: Run python \"4_setup_note_system.py\"")
    print(f"  to set up your Evernote replacement system.")


def generate_vault_index(vault_path, notebooks, total_notes):
    """Create an index file for the vault."""

    index_content = f"""---
title: "NoteVault Index"
created: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
source: "evernote-migration"
type: "index"
---

# NoteVault - Migrated from Evernote

**Migration Date:** {datetime.now().strftime('%Y-%m-%d')}
**Total Notes:** {total_notes}
**Total Notebooks:** {len(notebooks)}

## Notebooks

"""
    for nb in sorted(notebooks):
        # Count notes in this notebook
        nb_path = os.path.join(vault_path, nb)
        note_count = len([f for f in os.listdir(nb_path)
                          if f.endswith('.md') and f != '_index.md'])
        index_content += f"- [[{nb}]] ({note_count} notes)\n"

    index_content += """
## About This Vault

This vault was migrated from Evernote using an automated conversion tool.
All notes are in Markdown format with YAML frontmatter containing metadata.

### Structure
- Each Evernote notebook = a folder
- Each note = a .md file with frontmatter (title, created, updated, tags, notebook)
- Attachments are in `_attachments/` subfolders
- Tags are preserved in frontmatter for search/filtering

### Recommended Tools
- **Obsidian** (free) - Best for browsing, linking, and searching
- **VS Code** - For bulk editing and scripting
- **Any Markdown editor** - All files are standard .md
"""

    with open(os.path.join(vault_path, "_INDEX.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert Evernote .enex files to Markdown.")
    parser.add_argument("--input", "-i", default=ENEX_INPUT_DIR, help="Directory containing .enex files")
    parser.add_argument("--output", "-o", default=VAULT_PATH, help="Output vault path (default: ~/NoteVault)")
    args = parser.parse_args()
    ENEX_INPUT_DIR = args.input
    VAULT_PATH = args.output
    convert_all()
