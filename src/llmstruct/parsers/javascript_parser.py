import esprima
import os
import hashlib
import datetime
from typing import Dict, Any, List

class JavaScriptParser:
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
            tree = esprima.parseModule(source, {"loc": True, "range": True, "comment": True})
        except Exception as e:
            return {"path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"), "error": str(e)}

        module_doc = None
        comments = [
            {"type": "single" if c.type == "Line" else "block", "text": c.value.strip(), "line": c.loc.start.line}
            for c in tree.comments
        ]
        for c in comments:
            if c["line"] <= 2 and c["type"] == "block":
                module_doc = c["text"]
                break

        file_metadata = self.compute_file_metadata(filepath, include_hashes)
        category = "core"  # Simplified; extend with infer_category logic
        dependencies = []  # Extract from ImportDeclaration nodes
        functions = []
        classes = []

        def extract_signature(node):
            params = [p.name for p in node.params] if hasattr(node, "params") else []
            return f"{node.id.name}({', '.join(params)})" if node.id else "anonymous"

        for node in tree.body:
            if node.type == "FunctionDeclaration" and node.id and not node.id.name.startswith("_"):
                signature = extract_signature(node)
                doc = next((c["text"] for c in comments if c["line"] == node.loc.start.line - 1 and c["type"] == "block"), None)
                func_comments = [c["text"] for c in comments if node.loc.start.line <= c["line"] <= node.loc.end.line and c["type"] == "single"]
                functions.append({
                    "name": node.id.name,
                    "signature": signature,
                    "doc": doc,
                    "internal_comments": func_comments,
                    "module_calls": []  # Extract from node.body
                })
            # Add ClassDeclaration handling similarly

        return {
            "path": os.path.relpath(filepath, root_dir).replace(os.sep, "/"),
            "language": "javascript",
            "category": category,
            "module_doc": module_doc,
            "file_metadata": file_metadata,
            "dependencies": dependencies,
            "functions": functions,
            "classes": classes,
            "callgraph": self.callgraph
        }