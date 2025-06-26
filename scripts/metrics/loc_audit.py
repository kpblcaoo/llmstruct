#!/usr/bin/env python3
"""LOC & class count audit.

Scans all Python modules in the given directory (default: ``src``) and
prints a table listing:
  * total lines of code (non-blank, non-comment)
  * number of ``class`` definitions (top-level)

If a module exceeds the Architecture Guideline limits ( >400 LOC **or**
>5 classes) it is marked **FAIL**.

Usage
-----
$ python scripts/metrics/loc_audit.py [path]

Exit status ``1`` if any module violates the limits – this allows easy
integration into CI.
"""
from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path
from typing import Iterable, Tuple

LIMIT_LOC = 400
LIMIT_CLASSES = 5


def iter_py_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if "/venv/" in str(path):
            continue
        yield path


def count_loc(path: Path) -> int:
    lines = 0
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines += 1
    return lines


def count_top_level_classes(path: Path) -> int:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return 0
    return sum(isinstance(node, ast.ClassDef) for node in tree.body)


def audit_module(path: Path) -> Tuple[int, int, bool]:
    loc = count_loc(path)
    cls_cnt = count_top_level_classes(path)
    ok = loc <= LIMIT_LOC and cls_cnt <= LIMIT_CLASSES
    return loc, cls_cnt, ok


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src")
    print(f"📊 LOC Audit for {root}\n")
    fmt = "{:<60} {:>7} LOC  {:>5} classes  {}"
    any_fail = False
    project_root = Path.cwd()
    for file in sorted(iter_py_files(root)):
        loc, cls_cnt, ok = audit_module(file)
        status = "✅" if ok else "❌"
        if not ok:
            any_fail = True
        try:
            rel_path = file.relative_to(project_root)
        except ValueError:
            rel_path = file
        print(fmt.format(str(rel_path), loc, cls_cnt, status))

    if any_fail:
        print("\n❌ Architecture guideline violations found (limit: 400 LOC or 5 classes).")
        sys.exit(1)
    print("\n✅ All modules comply with architecture guidelines.")


if __name__ == "__main__":
    main() 