import json
from pathlib import Path
import gitignore_parser
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_gitignore():
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        return gitignore_parser.parse_gitignore(gitignore_path)
    return lambda x: False

def is_text_file(file_path):
    """Check if file is likely a text file based on extension."""
    text_extensions = {'.py', '.md', '.txt', '.json', '.toml', '.yml', '.yaml', '.gitignore'}
    return file_path.suffix.lower() in text_extensions

def collect_project():
    root_dir = Path(".")
    ignore_dirs = ["src", "tests", "venv", "tmp", "build", "examples"]
    gitignore = load_gitignore()
    output_json = "project_context.json"

    doc_files = {}
    for file_path in root_dir.rglob("*"):
        if file_path.is_file() and not any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
            if not gitignore(file_path) or file_path.name == output_json or file_path.name == ".gitignore":
                if is_text_file(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            doc_files[str(file_path)] = f.read()
                    except UnicodeDecodeError as e:
                        logger.warning(f"Skipping {file_path}: not a valid UTF-8 file ({e})")
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
                else:
                    logger.warning(f"Skipping {file_path}: not a text file")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"files": [{"path": k, "content": v} for k, v in doc_files.items()]}, f, ensure_ascii=False)
        logger.info(f"Generated {output_json} with {len(doc_files)} files")

if __name__ == "__main__":
    collect_project()