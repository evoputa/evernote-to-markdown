"""
Step 2: Export ALL Evernote notes using evernote-backup.
This downloads every notebook and note from your Evernote account via the API.
No manual clicking required.

Run: python "2_export_evernote.py"

You'll need your Evernote auth token. The script will guide you.
"""
import subprocess
import sys
import os
import webbrowser

SOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DB = os.path.join(SOLUTION_DIR, "evernote_backup.db")
ENEX_OUTPUT = os.path.join(SOLUTION_DIR, "enex_export")

def get_token_instructions():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           HOW TO GET YOUR EVERNOTE AUTH TOKEN                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Option A: Developer Token (Fastest)                             ║
║  1. Go to: https://www.evernote.com/api/DeveloperToken.action    ║
║  2. Sign in with your Evernote account                           ║
║  3. Click "Create a developer token"                             ║
║  4. Copy the token string                                        ║
║                                                                  ║
║  Option B: If developer tokens are disabled                      ║
║  1. Open Evernote Web: https://www.evernote.com/client/           ║
║  2. Sign in to your account                                      ║
║  3. Open browser DevTools (F12)                                  ║
║  4. Go to Application tab > Cookies                              ║
║  5. Find the cookie named "auth" or look for a long               ║
║     S=s###:U=######:E=...... string                              ║
║  6. Copy that value                                              ║
║                                                                  ║
║  Option C: OAuth via evernote-backup                             ║
║  The tool can do OAuth automatically (may open a browser)        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

def export_via_evernote_backup():
    """Use evernote-backup tool to download everything."""

    print("=" * 60)
    print("  EVERNOTE MIGRATION - Step 2: Bulk Export")
    print("  This will download ALL notebooks and notes from your account")
    print("=" * 60)

    # Check if we already have a backup database
    if os.path.exists(BACKUP_DB):
        print(f"\n[INFO] Found existing backup at: {BACKUP_DB}")
        choice = input("Resume previous backup? (y/n): ").strip().lower()
        if choice == 'y':
            sync_and_export()
            return

    # First time setup - need authentication
    get_token_instructions()

    print("\nChoose authentication method:")
    print("  1. I have a developer token")
    print("  2. I have the auth cookie from browser")
    print("  3. Try OAuth (opens browser)")

    method = input("\nEnter choice (1/2/3): ").strip()

    if method in ('1', '2'):
        token = input("\nPaste your token: ").strip().strip('"').strip("'")
        if not token:
            print("[ERROR] No token provided. Exiting.")
            return

        # Initialize the backup with token
        print("\n[STEP 1/3] Initializing backup database...")
        cmd = [
            sys.executable, "-m", "evernote_backup",
            "init-db",
            "--backend", "evernote",
            "--token", token,
            "--database", BACKUP_DB
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Init failed: {result.stderr}")
            # Try with network store URL for some accounts
            print("\n[RETRY] Trying with explicit note store URL...")
            note_store_url = input("Enter your NoteStore URL (or press Enter to skip): ").strip()
            if note_store_url:
                cmd.extend(["--note-store-url", note_store_url])
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"[ERROR] Still failing: {result.stderr}")
                    print("\nFalling back to alternative export method...")
                    fallback_export()
                    return
            else:
                print("\nFalling back to alternative export method...")
                fallback_export()
                return

        print("[OK] Database initialized!")

    elif method == '3':
        print("\n[STEP 1/3] Starting OAuth flow (browser will open)...")
        cmd = [
            sys.executable, "-m", "evernote_backup",
            "init-db",
            "--backend", "evernote",
            "--oauth",
            "--database", BACKUP_DB
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] OAuth failed: {result.stderr}")
            fallback_export()
            return

    sync_and_export()

def sync_and_export():
    """Sync all notes and export to .enex files."""

    # Sync all notes
    print("\n[STEP 2/3] Downloading ALL notebooks and notes...")
    print("  This may take 10-30 minutes for 3842 notes. Please wait...\n")

    cmd = [
        sys.executable, "-m", "evernote_backup",
        "sync",
        "--database", BACKUP_DB
    ]
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print("[ERROR] Sync failed. You can re-run this script to resume.")
        return

    print("\n[OK] All notes downloaded!")

    # Export to .enex files (one per notebook)
    print(f"\n[STEP 3/3] Exporting to .enex files in: {ENEX_OUTPUT}")
    os.makedirs(ENEX_OUTPUT, exist_ok=True)

    cmd = [
        sys.executable, "-m", "evernote_backup",
        "export",
        "--database", BACKUP_DB,
        "--output", ENEX_OUTPUT
    ]
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print("[ERROR] Export failed.")
        return

    # Count what we got
    enex_count = 0
    for root, dirs, files in os.walk(ENEX_OUTPUT):
        for f in files:
            if f.endswith('.enex'):
                enex_count += 1

    print("\n" + "=" * 60)
    print(f"  Export complete!")
    print(f"  Exported {enex_count} .enex files to: {ENEX_OUTPUT}")
    print(f"  Next step: Run python \"3_convert_to_markdown.py\"")
    print("=" * 60)

def fallback_export():
    """Alternative: Guide user through Evernote desktop bulk export with PowerShell automation."""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║          ALTERNATIVE: Semi-Automated Desktop Export              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Since the API method didn't work, here's the fastest            ║
║  alternative using your Evernote desktop app:                    ║
║                                                                  ║
║  1. Open Evernote desktop                                        ║
║  2. Click on "Notebooks" in the left sidebar                     ║
║  3. For the FASTEST approach:                                    ║
║     - Click "All Notes" (shows all 3842 notes)                   ║
║     - Press Ctrl+A to select ALL notes                           ║
║     - Right-click > "Export notes..."                            ║
║     - Choose "ENEX (.enex)" format                               ║
║     - Save to: {output_dir}                                      ║
║     - This exports EVERYTHING in one file!                       ║
║                                                                  ║
║  4. Alternatively, export notebook by notebook                   ║
║     (the converter handles both single and multi-file exports)   ║
║                                                                  ║
║  After export, run: python "3_convert_to_markdown.py"            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""".format(output_dir=ENEX_OUTPUT))

    os.makedirs(ENEX_OUTPUT, exist_ok=True)

    print(f"[INFO] Created output directory: {ENEX_OUTPUT}")
    print(f"[INFO] Save your .enex file(s) there, then run step 3.")

if __name__ == "__main__":
    export_via_evernote_backup()
