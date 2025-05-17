import ast
import os
import hashlib
import datetime
from typing import Dict, Any, List

class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []  # List of (name, is_qualified) tuples

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append((node.func.id, False))  # Local call, e.g., "main"
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            call_name = f"{node.func.value.id}.{node.func.attr}"
            self.calls.append((call_name, True))  # Qualified call, e.g., "utils.helper"
        self.generic_visit(node)

class PythonParser:
    def __init__(self):
        self.dependencies = set()
        self.functions = []
        self.classes = []
        self.callgraph = {}

    def file_hash(self, filepath: str) -> str:
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return ""

    def compute_file_metadata(self, filepath: str, include_hashes: bool) -> Dict[str, Any]:
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
                metadata["hash"] = self.file_hash(filepath)
            return metadata
        except OSError:
            return {}

    def parse_module(self, filepath: str, root_dir: str, include_ranges: bool, include_hashes: bool) -> Dict[str, Any]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception as e:
            return {"path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"), "error": str(e)}

        module_doc = ast.get_docstring(tree)
        file_metadata = self.compute_file_metadata(filepath, include_hashes)
        category = "core"  # Simplified; extend with infer_category
        dependencies = []
        functions = []
        classes = []
        callgraph = {}

        # Extract dependencies
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)

        # Extract functions and classes
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                doc = ast.get_docstring(node)
                signature = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                visitor = CallVisitor()
                visitor.visit(node)
                module_calls = [call for call, is_qualified in visitor.calls if is_qualified]
                callgraph[node.name] = [
                    call.split(".")[1] for call, is_qualified in visitor.calls
                    if is_qualified and "." in call
                ]
                func_data = {
                    "name": node.name,
                    "signature": signature,
                    "doc": doc,
                    "internal_comments": [],
                    "module_calls": module_calls
                }
                if include_ranges:
                    func_data["range"] = {"start": node.lineno, "end": node.end_lineno}
                functions.append(func_data)
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                doc = ast.get_docstring(node)
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        method_doc = ast.get_docstring(n)
                        signature = f"{n.name}({', '.join(arg.arg for arg in n.args.args)})"
                        visitor = CallVisitor()
                        visitor.visit(n)
                        method_calls = [call for call, is_qualified in visitor.calls if is_qualified]
                        callgraph[n.name] = [
                            call.split(".")[1] for call, is_qualified in visitor.calls
                            if is_qualified and "." in call
                        ]
                        method_data = {
                            "name": n.name,
                            "signature": signature,
                            "doc": method_doc,
                            "internal_comments": [],
                            "module_calls": method_calls
                        }
                        if include_ranges:
                            method_data["range"] = {"start": n.lineno, "end": n.end_lineno}
                        methods.append(method_data)
                class_data = {
                    "name": node.name,
                    "doc": doc,
                    "internal_comments": [],
                    "methods": methods
                }
                if include_ranges:
                    class_data["range"] = {"start": node.lineno, "end": node.end_lineno}
                classes.append(class_data)

        return {
            "path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"),
            "language": "python",
            "category": category,
            "module_doc": module_doc,
            "file_metadata": file_metadata,
            "dependencies": sorted(list(set(dependencies))),
            "functions": functions,
            "classes": classes,
            "callgraph": callgraph
        }