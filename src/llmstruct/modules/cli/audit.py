import os
from pathlib import Path

def audit(args):
    """Audit project structure and generate reports."""
    print("🔍 Auditing project structure...")
    root_dir = os.path.abspath(args.root_dir)
    print(f"📁 Project root: {root_dir}")
    key_files = ["struct.json", "llmstruct.toml", ".gitignore"]
    for file in key_files:
        file_path = Path(root_dir) / file
        status = "✅" if file_path.exists() else "❌"
        print(f"  {status} {file}")
    if hasattr(args, 'include_duplicates') and args.include_duplicates:
        print("\n" + "="*50)
        from llmstruct.cli import analyze_duplicates
        analyze_duplicates(args) 