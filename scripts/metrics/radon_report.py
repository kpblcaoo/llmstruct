#!/usr/bin/env python3
"""Generate Radon complexity & MI baseline report.

Outputs two sections:
* Cyclomatic Complexity (radon cc -s -a)
* Maintainability Index (radon mi -s)

Usage::

    python scripts/metrics/radon_report.py [src_dir] [outfile]

If *outfile* omitted – prints to stdout; otherwise also writes to file.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List
import os

RADON_NOT_FOUND_MSG = (
    "Radon package not installed. Install with `pip install radon`."
)

def run(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, env={**dict(**os.environ), "RADON_NOCOLOR": "1"})
        return out
    except subprocess.CalledProcessError as exc:
        # Even if radon returns non-zero (e.g., BrokenPipe), capture its output
        return exc.output
    except FileNotFoundError:
        sys.exit(RADON_NOT_FOUND_MSG)

def main() -> None:
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    outfile = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    header = f"📈 Radon report for {src_dir}  ({datetime.utcnow().isoformat()})\n"

    cc_output = run([sys.executable, "-m", "radon", "cc", "-s", "-a", src_dir])
    mi_output = run([sys.executable, "-m", "radon", "mi", "-s", src_dir])

    report = (
        header
        + "\n=== Cyclomatic Complexity ===\n" + cc_output
        + "\n=== Maintainability Index ===\n" + mi_output
    )

    if outfile:
        outfile.write_text(report, encoding="utf-8")
        print(f"Report written to {outfile}")
    else:
        print(report)

if __name__ == "__main__":
    main() 