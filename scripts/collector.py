import json
import logging
import uuid
from pathlib import Path
import fnmatch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def apply_filters(files, filters):
    filtered = []
    for file in files:
        if not filters:
            filtered.append(file)
            continue
        include = False
        for pattern in filters:
            if pattern.startswith("!"):
                if fnmatch.fnmatch(file, pattern[1:]):
                    include = False
                    break
            elif fnmatch.fnmatch(file, pattern):
                include = True
        if include:
            filtered.append(file)
    return filtered

def collect_files(root_dir: Path, filters: list = None):
    files = []
    for path in root_dir.rglob("*"):
        if path.is_file():
            rel_path = str(path.relative_to(root_dir))
            files.append(rel_path)
    return apply_filters(files, filters or [])

def generate_struct(root_dir: str, output: str = "struct.json"):
    root_path = Path(root_dir)
    struct = {
        "metadata": {
            "project_name": "llmstruct",
            "version": "0.2.0",
            "authors": [{"name": "@kpblcaoo", "github": "kpblcaoo", "email": "kpblcaoo@example.com"}],
            "stats": {"modules_count": 0, "functions_count": 0},
            "artifact_id": str(uuid.uuid4()),
            "summary": "LLMstruct project structure",
            "tags": ["struct"]
        },
        "toc": [],
        "modules": [],
        "folder_structure": [],
        "filters": ["src/*", "!tests/*", "!venv/*", "!build/*"]
    }
    
    output_path = Path(output)
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
            struct["filters"] = existing.get("filters", struct["filters"])
    
    files = collect_files(root_path, struct["filters"])
    
    for file in files:
        struct["folder_structure"].append({
            "path": file,
            "type": "file",
            "artifact_id": str(uuid.uuid4()),
            "metadata": {}
        })
    
    struct["modules"] = [
        {"name": "cli", "path": "src/cli", "artifact_id": str(uuid.uuid4()), "functions": []},
        {"name": "collector", "path": "src/collector", "artifact_id": str(uuid.uuid4()), "functions": []}
    ]
    struct["toc"] = files
    struct["metadata"]["stats"]["modules_count"] = len(struct["modules"])
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(struct, f, indent=2)
    logger.info(f"Generated {output}")

def main():
    generate_struct(".", "struct.json")

if __name__ == "__main__":
    main()
