import datetime
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from ..parsers.python_parser import analyze_module

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_folder_structure(root_dir: str, gitignore_patterns: Optional[List[str]], include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], exclude_dirs: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Capture directory and file structure with artifact_id, respecting .gitignore and patterns."""
    structure = []
    root_path = Path(root_dir).resolve()
    default_exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs
    
    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [p.rstrip('/') + '/*' if p.endswith('/') else p for p in gitignore_patterns]
    
    for dir_path, dirnames, filenames in os.walk(root_dir):
        rel_dir = str(Path(dir_path).relative_to(root_path))
        if rel_dir == '.':
            rel_dir = ''
        
        if any(Path(dir_path).match(p) for p in normalized_gitignore) or any(d in exclude_dirs_set for d in Path(dir_path).parts):
            dirnames[:] = []
            continue
        
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs_set and not any(Path(dir_path).joinpath(d).match(p) for p in normalized_gitignore + (exclude_patterns or []))]
        
        structure.append({
            "path": rel_dir or ".",
            "type": "directory",
            "artifact_id": str(uuid.uuid4()),
            "metadata": {}
        })
        for fname in sorted(filenames):
            file_path = Path(dir_path) / fname
            if any(file_path.match(p) for p in (include_patterns or ['*.py']) if not any(file_path.match(ep) for ep in (exclude_patterns or []) + normalized_gitignore)):
                structure.append({
                    "path": str(file_path.relative_to(root_path)),
                    "type": "file",
                    "artifact_id": str(uuid.uuid4()),
                    "metadata": {}
                })
    
    return sorted(structure, key=lambda x: x['path'])

def build_toc_and_modules(root_dir: str, include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], gitignore_patterns: Optional[List[str]], include_ranges: bool, include_hashes: bool, exclude_dirs: Optional[List[str]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build TOC and modules with artifact_id and robust filtering."""
    toc = []
    modules = []
    default_exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs
    
    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [p.rstrip('/') + '/*' if p.endswith('/') else p for p in gitignore_patterns]
    
    files = [
        f for f in Path(root_dir).rglob('*.py')
        if not any(f.match(p) for p in (exclude_patterns or []) + normalized_gitignore)
        and not any(d in exclude_dirs_set for d in f.parts)
    ]
    
    for file_path in files:
        module = analyze_module(str(file_path), root_dir, include_ranges, include_hashes)
        if module:
            module['artifact_id'] = str(uuid.uuid4())
            modules.append(module)
            toc.append({
                "module_id": module['module_id'],
                "path": module['path'],
                "category": module['category'],
                "functions": len(module['functions']),
                "classes": len(module['classes']),
                "summary": module['module_doc'].split('\n')[0] if module['module_doc'] else '',
                "artifact_id": module['artifact_id']
            })
    
    return toc, modules

def generate_json(root_dir: str, include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], gitignore_patterns: Optional[List[str]], include_ranges: bool, include_hashes: bool, goals: Optional[List[str]], exclude_dirs: Optional[List[str]]) -> Dict[str, Any]:
    """Generate JSON structure for project with artifact_id, summary, and tags."""
    root_path = Path(root_dir).resolve()
    toc, modules = build_toc_and_modules(root_dir, include_patterns, exclude_patterns, gitignore_patterns, include_ranges, include_hashes, exclude_dirs)
    
    stats = {
        "modules_count": len(modules),
        "functions_count": sum(len(m['functions']) for m in modules),
        "classes_count": sum(len(m['classes']) for m in modules),
        "call_edges_count": sum(len(set(sum((list(v) for v in m['callgraph'].values()), []))) for m in modules)
    }
    
    return {
        "metadata": {
            "project_name": "llmstruct",
            "description": "Utility for generating structured JSON for codebases",
            "version": datetime.datetime.utcnow().isoformat() + 'Z',
            "authors": [
                {
                    "name": "Mikhail Stepanov",
                    "github": "kpblcaoo",
                    "email": "kpblcaoo@gmail.com"
                }
            ],
            "instructions": [
                "Follow best practices, warn if instructions conflict with them",
                "Preserve functionality, ensure idempotency",
                "Use attached struct.json for context and navigation",
                "Request missing modules or functions if needed",
                "Regenerate JSON for significant changes, track via Git and artifacts",
                "Use internal comments for descriptions, append brief summary"
            ],
            "goals": goals or [],
            "stats": stats,
            "artifact_id": str(uuid.uuid4()),
            "summary": "Structured JSON for llmstruct codebase",
            "tags": ["codebase", "automation"],
            "folder_structure": get_folder_structure(root_dir, gitignore_patterns, include_patterns, exclude_patterns, exclude_dirs)
        },
        "toc": toc,
        "modules": modules
    }
