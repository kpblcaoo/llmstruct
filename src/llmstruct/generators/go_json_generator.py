import datetime
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from ..parsers.go_parser import analyze_module

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_go_folder_structure(
    root_dir: str,
    gitignore_patterns: Optional[List[str]],
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
    exclude_dirs: Optional[List[str]],
) -> List[Dict[str, Any]]:
    """Capture directory and file structure for Go projects with artifact_id, respecting .gitignore and patterns."""
    structure = []
    root_path = Path(root_dir).resolve()
    default_exclude_dirs = {
        "vendor", ".git", ".github", "bin", "dist", "build", ".idea", ".vscode"
    }
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs

    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [
        p.rstrip("/") + "/*" if p.endswith("/") else p for p in gitignore_patterns
    ]

    for dir_path, dirnames, filenames in os.walk(root_dir):
        rel_dir = str(Path(dir_path).relative_to(root_path))
        if rel_dir == ".":
            rel_dir = ""

        if any(Path(dir_path).match(p) for p in normalized_gitignore) or any(
            d in exclude_dirs_set for d in Path(dir_path).parts
        ):
            dirnames[:] = []
            continue

        dirnames[:] = [
            d
            for d in dirnames
            if d not in exclude_dirs_set
            and not any(
                Path(dir_path).joinpath(d).match(p)
                for p in normalized_gitignore + (exclude_patterns or [])
            )
        ]

        structure.append(
            {
                "path": rel_dir or ".",
                "type": "directory",
                "artifact_id": str(uuid.uuid4()),
                "metadata": {},
            }
        )
        for fname in sorted(filenames):
            file_path = Path(dir_path) / fname
            # Include Go files, mod files, and other relevant files
            go_patterns = include_patterns or ["*.go", "go.mod", "go.sum", "*.md", "Dockerfile", "*.yaml", "*.yml"]
            if any(
                file_path.match(p)
                for p in go_patterns
                if not any(
                    file_path.match(ep)
                    for ep in (exclude_patterns or []) + normalized_gitignore
                )
            ):
                structure.append(
                    {
                        "path": str(file_path.relative_to(root_path)),
                        "type": "file",
                        "artifact_id": str(uuid.uuid4()),
                        "metadata": {},
                    }
                )

    return sorted(structure, key=lambda x: x["path"])


def build_go_toc_and_modules(
    root_dir: str,
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
    gitignore_patterns: Optional[List[str]],
    include_ranges: bool,
    include_hashes: bool,
    exclude_dirs: Optional[List[str]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build TOC and modules for Go projects with artifact_id and robust filtering."""
    toc = []
    modules = []
    default_exclude_dirs = {
        "vendor", ".git", ".github", "bin", "dist", "build", ".idea", ".vscode"
    }
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs

    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [
        p.rstrip("/") + "/*" if p.endswith("/") else p for p in gitignore_patterns
    ]

    # Find all Go files
    files = [
        f
        for f in Path(root_dir).rglob("*.go")
        if not any(f.match(p) for p in (exclude_patterns or []) + normalized_gitignore)
        and not any(d in exclude_dirs_set for d in f.parts)
        and not f.name.endswith("_test.go")  # Exclude test files from main analysis
    ]

    for file_path in files:
        module = analyze_module(
            str(file_path), root_dir, include_ranges, include_hashes
        )
        if module:
            module["artifact_id"] = str(uuid.uuid4())
            modules.append(module)
            toc.append(
                {
                    "module_id": module["module_id"],
                    "path": module["path"],
                    "category": module["category"],
                    "package": module.get("package", "unknown"),
                    "functions": len(module["functions"]),
                    "structs": len(module["classes"]),  # Go structs mapped to classes
                    "summary": (
                        module["module_doc"].split("\n")[0]
                        if module["module_doc"]
                        else ""
                    ),
                    "artifact_id": module["artifact_id"],
                }
            )

    return toc, modules


def extract_go_mod_info(root_dir: str) -> Dict[str, Any]:
    """Extract information from go.mod file."""
    go_mod_path = Path(root_dir) / "go.mod"
    if not go_mod_path.exists():
        return {}
    
    try:
        with open(go_mod_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.strip().split("\n")
        module_name = ""
        go_version = ""
        dependencies = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("module "):
                module_name = line.split("module ")[1]
            elif line.startswith("go "):
                go_version = line.split("go ")[1]
            elif line and not line.startswith("//") and not line.startswith("(") and not line.startswith(")"):
                # Dependency line
                parts = line.split()
                if len(parts) >= 2 and not line.startswith("require"):
                    dep_name = parts[0]
                    dep_version = parts[1]
                    dependencies.append({"name": dep_name, "version": dep_version})
        
        return {
            "module_name": module_name,
            "go_version": go_version,
            "dependencies": dependencies
        }
    except Exception as e:
        logging.error(f"Failed to parse go.mod: {e}")
        return {}


def generate_go_json(
    root_dir: str,
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
    gitignore_patterns: Optional[List[str]],
    include_ranges: bool,
    include_hashes: bool,
    goals: Optional[List[str]],
    exclude_dirs: Optional[List[str]],
) -> Dict[str, Any]:
    """Generate JSON structure for Go project with artifact_id, summary, and tags."""
    Path(root_dir).resolve()
    toc, modules = build_go_toc_and_modules(
        root_dir,
        include_patterns,
        exclude_patterns,
        gitignore_patterns,
        include_ranges,
        include_hashes,
        exclude_dirs,
    )

    go_mod_info = extract_go_mod_info(root_dir)
    
    stats = {
        "modules_count": len(modules),
        "functions_count": sum(len(m["functions"]) for m in modules),
        "structs_count": sum(len(m["classes"]) for m in modules),  # Go structs
        "packages_count": len(set(m.get("package", "unknown") for m in modules)),
        "call_edges_count": sum(
            len(set(sum((list(v) for v in m["callgraph"].values()), [])))
            for m in modules
        ),
    }

    project_name = go_mod_info.get("module_name", "go-project")
    
    return {
        "metadata": {
            "project_name": project_name,
            "description": f"Go project analysis for {project_name}",
            "version": datetime.datetime.utcnow().isoformat() + "Z",
            "language": "go",
            "go_version": go_mod_info.get("go_version", "unknown"),
            "authors": [
                {
                    "name": "Go Project Author",
                    "tool": "llmstruct-go-parser",
                }
            ],
            "instructions": [
                "Follow Go best practices and conventions",
                "Preserve functionality, ensure idempotency",
                "Use attached struct.json for context and navigation",
                "Request missing packages or functions if needed",
                "Regenerate JSON for significant changes, track via Git and artifacts",
                "Use internal comments for descriptions, append brief summary",
            ],
            "goals": goals or [],
            "stats": stats,
            "go_mod_info": go_mod_info,
            "artifact_id": str(uuid.uuid4()),
            "summary": f"Structured JSON for Go project {project_name}",
            "tags": ["codebase", "golang", "automation"],
            "folder_structure": get_go_folder_structure(
                root_dir,
                gitignore_patterns,
                include_patterns,
                exclude_patterns,
                exclude_dirs,
            ),
        },
        "toc": toc,
        "modules": modules,
    } 