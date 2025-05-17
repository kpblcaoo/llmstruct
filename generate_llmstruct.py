#!/usr/bin/env python3
"""
Generate JSON for workspace based on user instructions template.

Creates structure:
- metadata with description, instructions, and version
- toc with module summaries and categories
- modules with detailed function/class info, comments, call graphs, and categories
"""

import os
import ast
import json
import fnmatch
import logging
import datetime
import tokenize
import hashlib
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", filename="llmstruct.log")

EXCLUDE_DIRS = {'venv', '__pycache__', '.pytest_cache', '.git', 'tests', 'test'}

# Static instructions
INSTRUCTIONS = [
    "Follow best practices, warn if instructions conflict with them",
    "Preserve functionality, ensure idempotency",
    "Use attached struct.json for context and navigation",
    "Request missing modules or functions if needed",
    "Regenerate JSON for significant changes, track via Git and artifacts",
    "Use internal comments for descriptions, append brief summary"
]

# Default goals (fallback)
DEFAULT_GOALS = [
    "Create a universal JSON format for codebases",
    "Support extensible parsing for multiple languages",
    "Develop modular parser plugins",
    "Provide open, RFC-style documentation",
    "Integrate with LLMs for automation"
]

def load_gitignore(root_dir: str) -> List[str]:
    """Load and normalize patterns from .gitignore, logging loaded patterns."""
    gitignore_path = os.path.join(root_dir, ".gitignore")
    patterns = []
    if not os.path.exists(gitignore_path):
        logging.warning(f"No .gitignore found at {gitignore_path}")
        return patterns
    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = [line.strip().rstrip('/') for line in f if line.strip() and not line.startswith("#")]
        logging.info(f"Loaded {len(patterns)} patterns from {gitignore_path}: {patterns}")
        return patterns
    except (OSError, UnicodeDecodeError) as e:
        logging.error(f"Failed to read .gitignore at {gitignore_path}: {e}")
        return []

def load_goals(goals_input: Optional[str] = None) -> List[str]:
    """Load goals from semicolon-separated string, file, or interactive editor."""
    if goals_input:
        # Try parsing as semicolon-separated goals
        if ';' in goals_input:
            goals = [g.strip() for g in goals_input.split(';') if g.strip()]
            if goals:
                logging.info(f"Parsed {len(goals)} semicolon-separated goals: {goals}")
                return goals
        # Try parsing as comma-separated goals (fallback)
        if ',' in goals_input:
            goals = [g.strip() for g in goals_input.split(',') if g.strip()]
            if goals:
                logging.info(f"Parsed {len(goals)} comma-separated goals: {goals}")
                return goals
        # Try loading as a file
        if os.path.isfile(goals_input):
            try:
                with open(goals_input, "r", encoding="utf-8") as f:
                    goals = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    logging.info(f"Loaded {len(goals)} goals from file {goals_input}: {goals}")
                    return goals if goals else DEFAULT_GOALS
            except (OSError, UnicodeDecodeError) as e:
                logging.error(f"Failed to read goals file {goals_input}: {e}")
                return DEFAULT_GOALS
    # Fallback to interactive editor
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as temp:
        temp.write("# Enter goals (one per line, # for comments)\n")
        temp.write("\n".join(f"# {g}" for g in DEFAULT_GOALS))
        temp.flush()
        editor = os.environ.get("EDITOR", "nano" if os.name != "nt" else "notepad")
        try:
            subprocess.run([editor, temp.name], check=True)
            with open(temp.name, "r", encoding="utf-8") as f:
                goals = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                logging.info(f"Loaded {len(goals)} goals from interactive editor: {goals}")
                return goals if goals else DEFAULT_GOALS
        except (subprocess.SubprocessError, OSError) as e:
            logging.error(f"Failed to open editor {editor}: {e}")
            return DEFAULT_GOALS
        finally:
            try:
                os.unlink(temp.name)
            except OSError:
                pass

def file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of file contents."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except (OSError, UnicodeDecodeError) as e:
        logging.error(f"Failed to compute hash for {filepath}: {e}")
        return ""

def extract_comments(filepath: str) -> List[Dict[str, Any]]:
    """Extract single-line and multi-line comments using tokenize."""
    comments = []
    try:
        with open(filepath, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comments.append({"type": "single", "text": token.string.strip(), "line": token.start[0]})
                elif token.type == tokenize.STRING and token.string.startswith('"""'):
                    text = token.string.strip('"""').strip()
                    if text:
                        comments.append({"type": "docstring", "text": text, "line": token.start[0]})
    except (tokenize.TokenError, UnicodeDecodeError) as e:
        logging.error(f"Failed to tokenize {filepath}: {e}")
    return comments

def compute_file_metadata(filepath: str, include_hashes: bool) -> Dict[str, Any]:
    """Compute file size, last modified time, line count, and optional hash."""
    try:
        stat = os.stat(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
        metadata = {
            "size_bytes": stat.st_size,
            "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
            "line_count": line_count
        }
        if include_hashes:
            metadata["hash"] = file_hash(filepath)
        return metadata
    except (OSError, UnicodeDecodeError) as e:
        logging.error(f"Failed to compute metadata for {filepath}: {e}")
        return {}

def infer_category(path: str, dependencies: List[str]) -> str:
    """Infer module category based on path and dependencies."""
    path_lower = path.lower()
    if "utils" in path_lower or "helper" in path_lower:
        return "utils"
    elif "cli" in path_lower or "argparse" in dependencies:
        return "cli"
    elif "api" in path_lower or "requests" in dependencies or "http" in path_lower:
        return "api"
    elif any(x in path_lower for x in ["core", "main", "manager"]):
        return "core"
    return "other"

def get_signature(func_node: ast.FunctionDef) -> str:
    """Generate function signature."""
    args = [arg.arg for arg in func_node.args.args]
    return f"{func_node.name}({', '.join(args)})"

class CallVisitor(ast.NodeVisitor):
    """Extract function calls and module dependencies."""
    def __init__(self):
        self.called_funcs = set()
        self.module_calls = set()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_funcs.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called_funcs.add(node.func.attr)
            if isinstance(node.func.value, ast.Name):
                self.module_calls.add(f"{node.func.value.id}.{node.func.attr}")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.module_calls.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.module_calls.add(node.module)
        self.generic_visit(node)

def extract_dependencies(tree: ast.AST) -> List[str]:
    """Extract module-level imports."""
    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencies.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.add(node.module)
    return sorted(dependencies)

def analyze_module(filepath: str, root_dir: str, include_ranges: bool, include_hashes: bool) -> Dict[str, Any]:
    """Analyze a Python module in a single pass."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError) as e:
        logging.error(f"Failed to parse {filepath}: {e}")
        return {"path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"), "error": str(e)}

    module_id = hashlib.sha256(os.path.relpath(filepath, root_dir).encode()).hexdigest()[:8]
    module_doc = ast.get_docstring(tree)
    comments = extract_comments(filepath)
    dependencies = extract_dependencies(tree)
    file_metadata = compute_file_metadata(filepath, include_hashes)
    category = infer_category(filepath, dependencies)
    source_lines = source.splitlines()
    functions = []
    classes = []
    callgraph = {}
    func_counter = 1
    class_counter = 1

    visitor = CallVisitor()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
            func_id = f"f{func_counter}"
            func_counter += 1
            sig = get_signature(node)
            doc = ast.get_docstring(node)
            start, end = node.lineno, getattr(node, 'end_lineno', node.lineno)
            func_comments = [
                c["text"] for c in comments
                if start <= c["line"] <= end and c["type"] == "single"
            ]
            visitor.visit(node)
            callgraph[node.name] = sorted(visitor.called_funcs)
            func_data = {
                "function_id": func_id,
                "name": node.name,
                "signature": sig,
                "doc": doc,
                "internal_comments": func_comments,
                "module_calls": sorted(visitor.module_calls)
            }
            if include_ranges:
                func_data["range"] = {"start": start, "end": end}
            functions.append(func_data)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
            class_id = f"c{class_counter}"
            class_counter += 1
            class_doc = ast.get_docstring(node)
            start, end = node.lineno, getattr(node, 'end_lineno', node.lineno)
            class_comments = [
                c["text"] for c in comments
                if start <= c["line"] <= end and c["type"] == "single"
            ]
            methods = []
            method_counter = 1
            for cnode in node.body:
                if isinstance(cnode, ast.FunctionDef) and not cnode.name.startswith('_'):
                    method_id = f"m{method_counter}"
                    method_counter += 1
                    msig = get_signature(cnode)
                    mdoc = ast.get_docstring(cnode)
                    mstart, mend = cnode.lineno, getattr(cnode, 'end_lineno', cnode.lineno)
                    method_comments = [
                        c["text"] for c in comments
                        if mstart <= c["line"] <= mend and c["type"] == "single"
                    ]
                    visitor.visit(cnode)
                    callgraph[cnode.name] = sorted(visitor.called_funcs)
                    method_data = {
                        "method_id": method_id,
                        "name": cnode.name,
                        "signature": msig,
                        "doc": mdoc,
                        "internal_comments": method_comments,
                        "module_calls": sorted(visitor.module_calls)
                    }
                    if include_ranges:
                        method_data["range"] = {"start": mstart, "end": mend}
                    methods.append(method_data)
            class_data = {
                "class_id": class_id,
                "name": node.name,
                "doc": class_doc,
                "internal_comments": class_comments,
                "methods": methods
            }
            if include_ranges:
                class_data["range"] = {"start": start, "end": end}
            classes.append(class_data)

    return {
        "module_id": module_id,
        "path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"),
        "category": category,
        "module_doc": module_doc,
        "file_metadata": file_metadata,
        "dependencies": dependencies,
        "functions": functions,
        "classes": classes,
        "callgraph": callgraph
    }

def build_toc_and_modules(root_dir: str, include_patterns: List[str] = None, exclude_patterns: List[str] = None, include_ranges: bool = False, include_hashes: bool = False) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], int, int, int]:
    """Build TOC and modules with robust .gitignore filtering using pathlib."""
    root_path = Path(root_dir).resolve()
    include_patterns = include_patterns or ["*.py"]
    exclude_patterns = exclude_patterns or []
    exclude_patterns.extend(EXCLUDE_DIRS)
    gitignore_patterns = load_gitignore(root_dir)

    modules = []
    total_functions = 0
    total_classes = 0
    total_calls = 0

    for dirpath, _, filenames in os.walk(root_path, topdown=True):
        dir_path = Path(dirpath)
        rel_dir = str(dir_path.relative_to(root_path)).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        skip_dir = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(rel_dir, pattern) or fnmatch.fnmatch(dir_path.name, pattern) or any(fnmatch.fnmatch(p, pattern) for p in rel_dir.split("/")):
                logging.debug(f"Skipping directory {dirpath} due to exclude pattern {pattern}")
                skip_dir = True
                break
        if skip_dir:
            continue
        for pattern in gitignore_patterns:
            if fnmatch.fnmatch(rel_dir, pattern) or fnmatch.fnmatch(dir_path.name, pattern) or (rel_dir and any(fnmatch.fnmatch(p, pattern) for p in rel_dir.split("/"))):
                logging.debug(f"Skipping directory {dirpath} due to .gitignore pattern {pattern}")
                skip_dir = True
                break
        if skip_dir:
            continue

        for filename in filenames:
            file_path = dir_path / filename
            rel_path = str(file_path.relative_to(root_path)).replace(os.sep, "/")
            if not any(fnmatch.fnmatch(filename, pat) for pat in include_patterns):
                logging.debug(f"Skipping file {rel_path} due to not matching include patterns {include_patterns}")
                continue
            if any(fnmatch.fnmatch(rel_path, pat) for pat in gitignore_patterns):
                logging.debug(f"Skipping file {rel_path} due to .gitignore pattern")
                continue
            if any(fnmatch.fnmatch(filename, pat) for pat in exclude_patterns if pat not in EXCLUDE_DIRS):
                logging.debug(f"Skipping file {rel_path} due to exclude pattern {pat}")
                continue
            logging.info(f"Processing file {rel_path}")
            module = analyze_module(str(file_path), root_dir, include_ranges, include_hashes)
            if "error" not in module:
                modules.append(module)
                total_functions += len(module["functions"])
                total_classes += len(module["classes"])
                total_calls += sum(len(calls) for calls in module["callgraph"].values())

    toc = []
    for m in modules:
        if "error" in m:
            continue
        summary_line = (m["module_doc"] or "").split('\n')[0] if m["module_doc"] else ""
        toc.append({
            "module_id": m["module_id"],
            "path": m["path"],
            "category": m["category"],
            "functions": len(m["functions"]),
            "classes": len(m["classes"]),
            "summary": summary_line
        })

    return toc, modules, total_functions, total_classes, total_calls

def generate_json(root_dir: str, include_patterns: List[str] = None, exclude_patterns: List[str] = None, include_ranges: bool = False, include_hashes: bool = False, goals_input: Optional[str] = None) -> Dict[str, Any]:
    """Generate JSON structure for project."""
    toc, modules, total_functions, total_classes, total_calls = build_toc_and_modules(root_dir, include_patterns, exclude_patterns, include_ranges, include_hashes)

    metadata = {
        "project_name": os.path.basename(os.path.abspath(root_dir)),
        "description": "Utility for generating structured JSON for codebases",
        "version": datetime.datetime.utcnow().isoformat() + "Z",
        "instructions": INSTRUCTIONS,
        "goals": load_goals(goals_input),
        "stats": {
            "modules_count": len(toc),
            "functions_count": total_functions,
            "classes_count": total_classes,
            "call_edges_count": total_calls
        }
    }

    return {
        "metadata": metadata,
        "toc": toc,
        "modules": modules
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate JSON structure for project with AI instructions")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("-o", "--output", default="struct_for_workspace.json", help="Output JSON file")
    parser.add_argument("--include", action="append", help="Include files matching pattern (e.g., '*.py')")
    parser.add_argument("--exclude", action="append", help="Exclude files/directories beyond defaults")
    parser.add_argument("--include-ranges", action="store_true", help="Include line ranges for functions/classes")
    parser.add_argument("--include-hashes", action="store_true", help="Include file content hashes")
    parser.add_argument("--goals", help="Semicolon-separated goals or path to goals file")
    parser.add_argument("--language", choices=["python", "javascript"], help="Programming language to parse")
    parser.add_argument("--tasks", help="Path to tasks JSON file (ignored)")
    args = parser.parse_args()

    if args.tasks:
        logging.warning(f"--tasks {args.tasks} is not supported and will be ignored")

    include_patterns = args.include
    if args.language:
        language_patterns = {
            "python": ["*.py"],
            "javascript": ["*.js"]
        }
        include_patterns = include_patterns or []
        include_patterns.extend(language_patterns.get(args.language, ["*.py"]))

    data = generate_json(args.project_root, include_patterns, args.exclude, args.include_ranges, args.include_hashes, args.goals)
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"JSON saved to {args.output}")
    except (OSError, UnicodeEncodeError) as e:
        logging.error(f"Failed to write JSON to {args.output}: {e}")
        raise

if __name__ == "__main__":
    main()