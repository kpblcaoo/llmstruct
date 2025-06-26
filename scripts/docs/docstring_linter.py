#!/usr/bin/env python3
"""Google-style docstring linter for public symbols.

Walks through Python files (default: ``src``) and reports public
functions / classes / modules that lack a Google-style docstring.

Criteria (simplified):
* Symbol is *public* if its name does **not** start with ``_``.
* A valid Google docstring starts with a short summary line and contains
  at least one section header like ``Args:``, ``Returns:``, ``Raises:``
  (case-sensitive, per guideline).

Run standalone or in CI; exits with status 1 if violations found.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Iterable, List

GOOGLE_SECTION_RE = re.compile(r"^(Args|Returns|Raises|Attributes|Examples?):", re.MULTILINE)


def iter_py_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if "/venv/" in str(path):
            continue
        yield path


def has_google_docstring(node: ast.AST) -> bool:
    doc = ast.get_docstring(node) or ""
    if not doc:
        return False
    return bool(GOOGLE_SECTION_RE.search(doc))


def analyse_file(path: Path) -> List[str]:
    """Return list of diagnostic strings for violations in *path*."""
    diagnostics: List[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as exc:
        diagnostics.append(f"SyntaxError parsing {path}: {exc}")
        return diagnostics

    # Module docstring (public module unless it is __init__.py)
    if path.name != "__init__.py" and not has_google_docstring(tree):
        diagnostics.append(f"module {path} missing Google docstring")

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_") and not has_google_docstring(node):
                diagnostics.append(f"function {path}:{node.lineno} {node.name} missing Google docstring")
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_") and not has_google_docstring(node):
                diagnostics.append(f"class {path}:{node.lineno} {node.name} missing Google docstring")
            # methods
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("_"):
                        continue
                    if not has_google_docstring(item):
                        diagnostics.append(f"method {path}:{item.lineno} {node.name}.{item.name} missing Google docstring")
    return diagnostics


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src")
    print(f"📝 Docstring Linter for {root}\n")
    violations: List[str] = []
    for file in iter_py_files(root):
        violations.extend(analyse_file(file))

    if violations:
        print("❌ Docstring violations:")
        for v in violations:
            print("  -", v)
        sys.exit(1)
    print("✅ All public symbols have Google-style docstrings.")


if __name__ == "__main__":
    main() 