"""
Step 5: Organize NoteVault into Evernote-style Stacks.

Stack = a group of folders (like Evernote's notebook stacks)
Folder = a group of notes (like Evernote's notebooks)

This script moves related folders into parent "Stack" folders.

Usage:
  python organize_stacks.py --vault ~/NoteVault --config stacks.json
  python organize_stacks.py --vault ~/NoteVault
"""
import os
import sys
import json
import shutil

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='replace', buffering=1)

VAULT_PATH = os.environ.get("VAULT_PATH", os.path.join(os.path.expanduser("~"), "NoteVault"))

# ============================================================
# STACK DEFINITIONS
# Load from stacks.json config file (recommended) or use the
# example inline dict below as a starting point.
# Edit stacks.json to match your Evernote notebook organization.
# ============================================================

# Example stacks — replace with your own or use --config stacks.json
DEFAULT_STACKS = {
    "Business": [
        "Meeting Notes",
        "Client Projects",
        "Proposals",
        "Invoices",
    ],
    "Learning": [
        "Courses",
        "Certifications",
        "Book Notes",
        "Research",
    ],
    "Personal": [
        "Journal",
        "Recipes",
        "Travel",
        "Health",
    ],
    "Projects": [
        "Project Alpha",
        "Project Beta",
        "Archive",
    ],
}

# Folders to leave at root (system folders)
ROOT_FOLDERS = {
    "_templates", "_archive", "Inbox", "Daily Notes",
    "Projects", "Reference", "Ideas", ".obsidian",
}


def load_stacks(config_path=None):
    """Load stack definitions from a JSON config file, or fall back to defaults."""
    if config_path and os.path.exists(config_path):
        print(f"  Loading stacks from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Strip the optional _comment key
        return {k: v for k, v in data.items() if not k.startswith('_')}
    return DEFAULT_STACKS


def organize_stacks(stacks=None):
    print("=" * 60)
    print("  ORGANIZE VAULT INTO STACKS")
    print("=" * 60)

    if stacks is None:
        stacks = DEFAULT_STACKS

    moved = 0
    skipped = 0
    errors = []

    for stack_name, folders in stacks.items():
        stack_path = os.path.join(VAULT_PATH, stack_name)
        os.makedirs(stack_path, exist_ok=True)

        for folder_name in folders:
            src = os.path.join(VAULT_PATH, folder_name)
            dst = os.path.join(stack_path, folder_name)

            if not os.path.exists(src):
                skipped += 1
                continue

            if os.path.exists(dst):
                # Already moved
                skipped += 1
                continue

            try:
                shutil.move(src, dst)
                moved += 1
                print(f"  [MOVED] {folder_name} -> {stack_name}/")
            except Exception as e:
                errors.append(f"{folder_name}: {e}")
                print(f"  [ERROR] {folder_name}: {e}")

    # Create index files for each stack
    print("\n  Creating stack index files...")
    for stack_name in stacks:
        create_stack_index(stack_name)

    print(f"\n{'=' * 60}")
    print(f"  REORGANIZATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Folders moved:   {moved}")
    print(f"  Skipped:         {skipped}")
    print(f"  Errors:          {len(errors)}")
    print(f"  Stacks created:  {len(stacks)}")
    print(f"{'=' * 60}")

    if errors:
        print("\n  Errors:")
        for err in errors:
            print(f"    - {err}")

    # Count remaining ungrouped folders
    remaining = []
    for item in os.listdir(VAULT_PATH):
        item_path = os.path.join(VAULT_PATH, item)
        if os.path.isdir(item_path) and item not in ROOT_FOLDERS and item not in stacks:
            if not item.startswith('.') and not item.startswith('_'):
                remaining.append(item)

    if remaining:
        print(f"\n  {len(remaining)} folders remain at root (ungrouped):")
        for r in sorted(remaining):
            print(f"    - {r}")
        print("\n  You can drag these into stacks in Obsidian's sidebar.")


def create_stack_index(stack_name):
    """Create an index/folder note for a stack with Dataview snippet view."""
    stack_path = os.path.join(VAULT_PATH, stack_name)
    if not os.path.exists(stack_path):
        return

    # Count notes in each subfolder
    subfolders = []
    total_notes = 0
    for item in sorted(os.listdir(stack_path)):
        item_path = os.path.join(stack_path, item)
        if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('_'):
            note_count = len([f for f in os.listdir(item_path)
                              if f.endswith('.md') and f != '_index.md'])
            subfolders.append((item, note_count))
            total_notes += note_count

    index_content = f'''---
title: "{stack_name}"
type: "stack"
cssclasses:
  - snippet-view
tags: ["stack"]
---

# {stack_name}

> **{len(subfolders)} notebooks** | **{total_notes} notes**

---

## Notebooks

'''

    for folder_name, count in subfolders:
        index_content += f'- **[[{stack_name}/{folder_name}|{folder_name}]]** ({count} notes)\n'

    index_content += '''

---

> [!tip] Dataview Snippet View
> Install the **Dataview** community plugin, then uncomment the query below
> to see an Evernote-style snippet view of all notes in this stack.

<!--
```dataview
TABLE WITHOUT ID
  file.link AS "Title",
  truncate(file.frontmatter.title, 80) AS "Preview",
  file.frontmatter.updated AS "Updated"
FROM "{stack_name}"
SORT file.mtime DESC
LIMIT 50
```
-->
'''.replace('{stack_name}', stack_name)

    with open(os.path.join(stack_path, f"_index.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"    [OK] {stack_name}/_index.md")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Organize vault folders into Evernote-style stacks.")
    parser.add_argument("--vault", "-v", default=VAULT_PATH, help="Vault path (default: ~/NoteVault)")
    parser.add_argument("--config", "-c", default=None, help="Path to stacks.json config file")
    args = parser.parse_args()
    VAULT_PATH = args.vault
    stacks = load_stacks(args.config)
    organize_stacks(stacks)
