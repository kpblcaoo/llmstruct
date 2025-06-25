import ast
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Set

# Import Phase 1 infrastructure that was created but not integrated
from ..core.uid_generator import (
    UIDType, 
    generate_uid, 
    generate_uid_components, 
    enhance_entity_with_uid
)
from ..core.hash_utils import hash_file, hash_entity, hash_content
from ..core.summary_providers import generate_summary

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def infer_category(file_path: str) -> str:
    """Infer module category based on its path."""
    path = Path(file_path)
    if path.name.startswith("test_") or "tests" in path.parts:
        return "test"
    if path.name in ("__init__.py", "__main__.py") or path.parent.name == "cli":
        return "cli"
    return "core"


class CallVisitor(ast.NodeVisitor):
    """AST visitor to collect function calls and dependencies."""

    def __init__(self):
        self.calls: Dict[str, Set[str]] = {}
        self.called_by: Dict[str, Set[str]] = {}  # NEW: Track called_by relationships
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
        if node.name not in self.called_by:
            self.called_by[node.name] = set()
        self.generic_visit(node)
        self.current_function = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions and their calls."""
        self.current_function = node.name
        self.calls[node.name] = set()
        if node.name not in self.called_by:
            self.called_by[node.name] = set()
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node: ast.Call) -> None:
        """Capture function calls."""
        if self.current_function:
            called_function = None
            if isinstance(node.func, ast.Name):
                called_function = node.func.id
                self.calls[self.current_function].add(called_function)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    called_function = f"{node.func.value.id}.{node.func.attr}"
                    self.calls[self.current_function].add(called_function)
            
            # NEW: Build called_by relationships
            if called_function:
                if called_function not in self.called_by:
                    self.called_by[called_function] = set()
                self.called_by[called_function].add(self.current_function)
        self.generic_visit(node)


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file content using new hash system."""
    try:
        return hash_file(file_path)
    except Exception as e:
        logging.error(f"Failed to compute hash for {file_path}: {e}")
        return ""


def analyze_module(
    file_path: str, root_dir: str, include_ranges: bool, include_hashes: bool
) -> Optional[Dict[str, Any]]:
    """Analyze Python module and return structured data with Phase 1 enhancements."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except Exception as e:
        logging.error(f"Failed to parse {file_path}: {e}")
        return None

    visitor = CallVisitor()
    visitor.visit(tree)

    module_id = (
        str(Path(file_path).relative_to(root_dir))
        .replace(os.sep, ".")
        .rsplit(".py", 1)[0]
    )
    module_doc = ast.get_docstring(tree) or ""
    
    # NEW: Generate module UID and hash
    module_path = str(Path(file_path).relative_to(root_dir))
    module_uid = generate_uid(UIDType.MODULE, module_path, module_id)
    module_uid_components = generate_uid_components(UIDType.MODULE, module_path, module_id)
    module_hash = compute_file_hash(file_path) if include_hashes else None
    
    # NEW: Generate module summary
    module_summary = generate_summary(
        code=source[:500],  # First 500 chars for context
        entity_type="module",
        entity_name=module_id,
        docstring=module_doc
    )
    
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            docstring = ast.get_docstring(node) or ""
            
            # NEW: Generate function UID and components with line number disambiguation
            unique_func_name = f"{node.name}:{node.lineno}"
            func_uid = generate_uid(UIDType.FUNCTION, module_path, unique_func_name)
            func_uid_components = generate_uid_components(UIDType.FUNCTION, module_path, unique_func_name)
            
            # NEW: Generate function hash
            func_content = ast.get_source_segment(source, node) if hasattr(ast, 'get_source_segment') else ""
            func_hash = hash_entity({
                "type": "function",
                "name": node.name,
                "content": func_content,
                "docstring": docstring
            }) if include_hashes else None
            
            # NEW: Generate function summary
            func_summary = generate_summary(
                code=func_content,
                entity_type="function", 
                entity_name=node.name,
                docstring=docstring
            )
            
            # NEW: Get calls and called_by for this function
            func_calls = list(visitor.calls.get(node.name, set()))
            func_called_by = list(visitor.called_by.get(node.name, set()))
            
            functions.append({
                "name": node.name,
                "docstring": docstring,
                "line_range": (
                    [node.lineno, node.end_lineno] if include_ranges else None
                ),
                "parameters": [arg.arg for arg in node.args.args],
                "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                # NEW: Phase 1 enhancements
                "uid": func_uid,
                "uid_components": func_uid_components,
                "hash": func_hash,
                "hash_source": "code_ast_v1" if func_hash else None,
                "hash_version": "2.1.0" if func_hash else None,
                "markdown_anchor": f"#{module_id}-{node.name}".lower().replace("_", "-").replace(".", "-"),
                "summary": func_summary.text,
                "summary_source": func_summary.source.value,
                "tags": func_summary.tags,
                "calls": func_calls,
                "called_by": func_called_by,
                # TODO: Add tested/tested_by in future commits
            })
        elif isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node) or ""
            
            # NEW: Generate class UID and components with line number disambiguation
            unique_class_name = f"{node.name}:{node.lineno}"
            class_uid = generate_uid(UIDType.CLASS, module_path, unique_class_name)
            class_uid_components = generate_uid_components(UIDType.CLASS, module_path, unique_class_name)
            
            # NEW: Generate class hash
            class_content = ast.get_source_segment(source, node) if hasattr(ast, 'get_source_segment') else ""
            class_hash = hash_entity({
                "type": "class",
                "name": node.name,
                "content": class_content,
                "docstring": docstring
            }) if include_hashes else None
            
            # NEW: Generate class summary  
            class_summary = generate_summary(
                code=class_content,
                entity_type="class",
                entity_name=node.name,
                docstring=docstring
            )
            
            methods = []
            for n in node.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_docstring = ast.get_docstring(n) or ""
                    
                    # NEW: Generate method UID and components with line number disambiguation
                    unique_method_name = f"{n.name}:{n.lineno}"
                    method_uid = generate_uid(UIDType.METHOD, module_path, unique_method_name, node.name)
                    method_uid_components = generate_uid_components(UIDType.METHOD, module_path, unique_method_name, node.name)
                    
                    # NEW: Generate method hash
                    method_content = ast.get_source_segment(source, n) if hasattr(ast, 'get_source_segment') else ""
                    method_hash = hash_entity({
                        "type": "method",
                        "name": n.name,
                        "parent": node.name,
                        "content": method_content,
                        "docstring": method_docstring
                    }) if include_hashes else None
                    
                    # NEW: Generate method summary
                    method_summary = generate_summary(
                        code=method_content,
                        entity_type="method",
                        entity_name=f"{node.name}.{n.name}",
                        docstring=method_docstring
                    )
                    
                    # NEW: Get calls and called_by for this method
                    method_calls = list(visitor.calls.get(n.name, set()))
                    method_called_by = list(visitor.called_by.get(n.name, set()))
                    
                    methods.append({
                        "name": n.name,
                        "docstring": method_docstring,
                        "line_range": [n.lineno, getattr(n, 'end_lineno', n.lineno)] if include_ranges else None,
                        "parameters": [arg.arg for arg in n.args.args],
                        # NEW: Phase 1 enhancements
                        "uid": method_uid,
                        "uid_components": method_uid_components,
                        "hash": method_hash,
                        "hash_source": "code_ast_v1" if method_hash else None,
                        "hash_version": "2.1.0" if method_hash else None,
                        "markdown_anchor": f"#{module_id}-{node.name}-{n.name}".lower().replace("_", "-").replace(".", "-"),
                        "summary": method_summary.text,
                        "summary_source": method_summary.source.value,
                        "tags": method_summary.tags,
                        "calls": method_calls,
                        "called_by": method_called_by,
                    })
            
            classes.append({
                "name": node.name,
                "docstring": docstring,
                "line_range": (
                    [node.lineno, node.end_lineno] if include_ranges else None
                ),
                "methods": methods,
                "bases": [ast.unparse(base) for base in node.bases],
                # NEW: Phase 1 enhancements
                "uid": class_uid,
                "uid_components": class_uid_components,
                "hash": class_hash,
                "hash_source": "code_ast_v1" if class_hash else None,
                "hash_version": "2.1.0" if class_hash else None,
                "markdown_anchor": f"#{module_id}-{node.name}".lower().replace("_", "-").replace(".", "-"),
                "summary": class_summary.text,
                "summary_source": class_summary.source.value,
                "tags": class_summary.tags,
            })

    return {
        "module_id": module_id,
        "path": module_path,
        "category": infer_category(file_path),
        "module_doc": module_doc,
        "functions": functions,
        "classes": classes,
        "callgraph": {k: list(v) for k, v in visitor.calls.items()},
        "dependencies": sorted([d for d in visitor.dependencies if d is not None]),
        "hash": module_hash,
        "hash_source": "file_content_v1" if module_hash else None,
        "hash_version": "2.1.0" if module_hash else None,
        # NEW: Phase 1 enhancements
        "uid": module_uid,
        "uid_components": module_uid_components,
        "summary": module_summary.text,
        "summary_source": module_summary.source.value,
        "tags": module_summary.tags,
    }
