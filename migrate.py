#!/usr/bin/env python3
"""
Evernote to Markdown Migration - Master Runner
Migrates all notes from Evernote to organized Markdown files.

Usage: python migrate.py [--output PATH]

By Begine Fusion (https://beginefusion.com)
"""
import subprocess
import sys
import os
import argparse

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")


def run_step(script_name, description, extra_args=None):
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}\n")

    cmd = [sys.executable, os.path.join(SCRIPT_DIR, script_name)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n  [STOPPED] Step failed: {script_name}")
        print(f"  You can run individual steps from the scripts/ directory.")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate all Evernote notes to organized Markdown files."
    )
    parser.add_argument(
        "--output", "-o",
        default=os.path.expanduser("~/NoteVault"),
        help="Output vault path (default: ~/NoteVault)"
    )
    parser.add_argument(
        "--stacks-config",
        default=None,
        help="Path to stacks.json for folder organization"
    )
    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     EVERNOTE → MARKDOWN MIGRATION TOOLKIT              ║
    ║                                                       ║
    ║     by Begine Fusion (beginefusion.com)               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    print(f"  Output: {args.output}")

    choice = input("\n  Start migration? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Cancelled.")
        return

    steps = [
        ("export_evernote.py", "STEP 1/4: Downloading from Evernote", None),
        ("convert_to_markdown.py", "STEP 2/4: Converting to Markdown",
         ["--output", args.output]),
        ("setup_vault.py", "STEP 3/4: Setting Up Note System",
         ["--vault", args.output]),
    ]

    if args.stacks_config:
        steps.append(
            ("organize_stacks.py", "STEP 4/4: Organizing Stacks",
             ["--vault", args.output, "--config", args.stacks_config])
        )

    for script, desc, extra in steps:
        if not run_step(script, desc, extra):
            return

    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              MIGRATION COMPLETE!                      ║
    ║                                                       ║
    ║  Your notes: {args.output:<40} ║
    ║                                                       ║
    ║  Next: Open in Obsidian (free)                        ║
    ║  https://obsidian.md                                  ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
