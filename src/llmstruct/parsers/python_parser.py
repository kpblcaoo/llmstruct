import ast
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def infer_category(file_path: str) -> str:
    """Infer module category based on its path."""
    path = Path(file_path)
    if path.name.startswith('test_') or 'tests' in path.parts:
        return 'test'
    if path.name in ('__init__.py', '__main__.py') or path.parent.name == 'cli':
        return 'cli'
    return 'core'

class CallVisitor(ast.NodeVisitor):
    """AST visitor to collect function calls and dependencies."""
    def __init__(self):
        self.calls: Dict[str, Set[str]] = {}
        self.dependencies: Set[str] = set()
        self.current_function: Optional[str] = None

    def visit_Import(self, node: ast.Import) -> None:
        """Capture import statements."""
        for alias in node.names:
            self.dependencies.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Capture from-import statements."""
        if node.module:
            self.dependencies.add(node.module)
        for alias in node.names:
            self.dependencies.add(alias.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions and their calls."""
        self.current_function = node.name
        self.calls[node.name] = set()
        self.generic_visit(node)
        self.current_function = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions and their calls."""
        self.current_function = node.name
        self.calls[node.name] = set()
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node: ast.Call) -> None:
        """Capture function calls."""
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.calls[self.current_function].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    self.calls[self.current_function].add(f"{node.func.value.id}.{node.func.attr}")
        self.generic_visit(node)

def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logging.error(f"Failed to compute hash for {file_path}: {e}")
        return ""

def analyze_module(file_path: str, root_dir: str, include_ranges: bool, include_hashes: bool) -> Optional[Dict[str, Any]]:
    """Analyze Python module and return structured data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except Exception as e:
        logging.error(f"Failed to parse {file_path}: {e}")
        return None

    visitor = CallVisitor()
    visitor.visit(tree)

    module_id = str(Path(file_path).relative_to(root_dir)).replace(os.sep, '.').rsplit('.py', 1)[0]
    module_doc = ast.get_docstring(tree) or ""
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            docstring = ast.get_docstring(node) or ""
            functions.append({
                "name": node.name,
                "docstring": docstring,
                "line_range": [node.lineno, node.end_lineno] if include_ranges else None,
                "parameters": [arg.arg for arg in node.args.args],
                "decorators": [ast.unparse(dec) for dec in node.decorator_list]
            })
        elif isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node) or ""
            methods = [
                {
                    "name": n.name,
                    "docstring": ast.get_docstring(n) or "",
                    "line_range": [n.lineno, n.end_lineno] if include_ranges else None,
                    "parameters": [arg.arg for arg in n.args.args]
                }
                for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append({
                "name": node.name,
                "docstring": docstring,
                "line_range": [node.lineno, node.end_lineno] if include_ranges else None,
                "methods": methods,
                "bases": [ast.unparse(base) for base in node.bases]
            })

    return {
        "module_id": module_id,
        "path": str(Path(file_path).relative_to(root_dir)),
        "category": infer_category(file_path),
        "module_doc": module_doc,
        "functions": functions,
        "classes": classes,
        "callgraph": {k: list(v) for k, v in visitor.calls.items()},
        "dependencies": sorted([d for d in visitor.dependencies if d is not None]),
        "hash": compute_file_hash(file_path) if include_hashes else None
    }