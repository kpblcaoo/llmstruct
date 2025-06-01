# cli.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""LLMStruct CLI - Main entry point for the command-line interface."""

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

import toml
from llmstruct import LLMClient
from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import generate_json, get_folder_structure
from llmstruct.self_run import attach_to_llm_request

# Import modular CLI components
try:
    from .cli_core import create_cli_core
    from .copilot import initialize_copilot

    MODULAR_CLI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Modular CLI components not available: {e}")
    MODULAR_CLI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

from llmstruct.modules.cli.utils import load_gitignore, load_config, read_file_content, write_to_file, parse_files_from_response
from llmstruct.modules.cli.handlers import interactive, interactive_modular, interactive_legacy
from llmstruct.modules.commands.queue import process_cli_queue_enhanced
from llmstruct.modules.cli.parse import parse
from llmstruct.modules.cli.query import query
from llmstruct.modules.cli.context import context
from llmstruct.modules.cli.dogfood import dogfood
from llmstruct.modules.cli.review import review
from llmstruct.modules.cli.copilot import copilot
from llmstruct.modules.cli.audit import audit
from llmstruct.modules.cli.analyze_duplicates import analyze_duplicates
from llmstruct.modules.cli import epic

def main():
    """Command-line interface for LLMstruct."""
    parser = argparse.ArgumentParser(
        description="Generate structured JSON for codebases and query LLMs"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    parse_parser = subparsers.add_parser(
        "parse", help="Parse codebase and generate struct.json"
    )
    parse_parser.add_argument("root_dir", help="Root directory of the project")
    parse_parser.add_argument(
        "-o", "--output", default="struct.json", help="Output JSON file"
    )
    parse_parser.add_argument(
        "--language", choices=["python", "javascript"], help="Programming language"
    )
    parse_parser.add_argument(
        "--include",
        action="append",
        help="Include patterns (e.g., '*.py' или несколько через запятую: '*.py,*.md')"
    )
    parse_parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude patterns (e.g., 'tests/*' или несколько через запятую: 'tests/*,*.md')"
    )
    parse_parser.add_argument(
        "--include-dir",
        action="append",
        help="Include directories (e.g., 'src/llmstruct/')"
    )
    parse_parser.add_argument(
        "--exclude-dir",
        action="append",
        help="Exclude directories (e.g., '.ARCHIVE/' или несколько через запятую: '.ARCHIVE/,tests/')"
    )
    parse_parser.add_argument(
        "--include-ranges",
        action="store_true",
        help="Include line ranges for functions/classes",
    )
    parse_parser.add_argument(
        "--include-hashes", action="store_true", help="Include file hashes"
    )
    parse_parser.add_argument("--goals", nargs="*", help="Custom project goals")
    parse_parser.add_argument(
        "--use-cache", action="store_true", help="Cache generated JSON"
    )
    parse_parser.add_argument(
        "--modular-index",
        action="store_true",
        help="Save struct and AST index per file/module in .llmstruct_index/ (модульный индекс для ускоренного анализа)"
    )

    query_parser = subparsers.add_parser(
        "query", help="Query LLMs with prompt and context"
    )
    query_parser.add_argument("--prompt", required=True, help="Prompt for LLM")
    query_parser.add_argument(
        "--context", default="struct.json", help="Context JSON file"
    )
    query_parser.add_argument(
        "--mode",
        choices=["grok", "anthropic", "ollama", "hybrid"],
        default="hybrid",
        help="LLM mode",
    )
    query_parser.add_argument("--model", help="Ollama model (e.g., mixtral, llama3)")
    query_parser.add_argument(
        "--context-mode",
        choices=["FULL", "FOCUSED", "MINIMAL", "SESSION"],
        default="FOCUSED",
        help="Context loading mode for optimization",
    )
    query_parser.add_argument(
        "--artifact-ids",
        nargs="*",
        default=[],
        help="Artifact IDs to include in context",
    )
    query_parser.add_argument(
        "--output",
        default="llm_response.json",
        help="Output JSON file for LLM response",
    )
    query_parser.add_argument("--use-cache", action="store_true", help="Use JSON cache")

    context_parser = subparsers.add_parser(
        "context", help="Generate context.json from input JSON"
    )
    context_parser.add_argument(
        "--input", default="struct.json", help="Input JSON file"
    )
    context_parser.add_argument(
        "--output", default="context.json", help="Output context JSON file"
    )
    context_parser.add_argument(
        "--priority",
        action="append",
        default=["src/llmstruct/"],
        help="Priority directories/files",
    )

    dogfood_parser = subparsers.add_parser("dogfood", help="Run dogfooding analysis")
    dogfood_parser.add_argument(
        "--input", default="src/llmstruct/", help="Input directory"
    )
    dogfood_parser.add_argument(
        "--output", default="dogfood_report.json", help="Output report JSON"
    )

    review_parser = subparsers.add_parser("review", help="Review codebase with LLM")
    review_parser.add_argument(
        "--input", default="src/llmstruct/", help="Input directory"
    )
    review_parser.add_argument(
        "--mode",
        choices=["grok", "anthropic", "ollama", "hybrid"],
        default="hybrid",
        help="LLM mode",
    )
    review_parser.add_argument(
        "--output", default="review_report.json", help="Output report JSON"
    )

    copilot_parser = subparsers.add_parser(
        "copilot", help="Copilot integration and context management"
    )
    copilot_parser.add_argument("root_dir", help="Root directory of the project")
    copilot_parser.add_argument(
        "copilot_command",
        choices=[
            "init",
            "status",
            "load",
            "unload",
            "refresh",
            "suggest",
            "validate",
            "export",
        ],
        help="Copilot command",
    )
    copilot_parser.add_argument("--layer", help="Layer name for load/unload commands")
    copilot_parser.add_argument("--query", help="Query for suggest command")
    copilot_parser.add_argument("--file-path", help="File path for validate command")
    copilot_parser.add_argument(
        "--change-type",
        choices=["edit", "delete", "add"],
        default="edit",
        help="Change type for validate command",
    )
    copilot_parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="Export format for export command",
    )
    copilot_parser.add_argument(
        "--layers", help="Comma-separated list of layers for export command"
    )
    copilot_parser.add_argument("--output", help="Output file for export command")
    copilot_parser.add_argument(
        "--force", action="store_true", help="Force initialization for init command"
    )

    # Audit command parser
    audit_parser = subparsers.add_parser(
        "audit", help="Audit project structure and check for issues"
    )
    audit_parser.add_argument("root_dir", help="Root directory of the project")
    audit_parser.add_argument(
        "--include-duplicates", action="store_true", help="Include duplication analysis"
    )
    audit_parser.add_argument(
        "--deep-duplicates",
        choices=["same-name", "any-name"],
        default="same-name",
        help="Duplicate analysis mode: 'same-name' (default) or 'any-name' (compare all function bodies regardless of name; slow!)"
    )
    audit_parser.add_argument(
        "--no-prod-filter",
        action="store_true",
        help="Show ALL duplicates, including those only in archive/tests (by default только production-код)"
    )

    # Duplication analysis command parser
    duplicates_parser = subparsers.add_parser(
        "analyze-duplicates", help="Analyze function duplication using struct.json deep analysis"
    )
    duplicates_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    duplicates_parser.add_argument(
        "--priority", choices=["all", "high", "medium"], default="all", help="Filter by priority"
    )
    duplicates_parser.add_argument(
        "--threshold", type=int, default=2, help="Minimum copies to consider duplication"
    )
    duplicates_parser.add_argument(
        "--save-report", type=str, help="Save detailed report to file"
    )
    duplicates_parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug output"
    )
    duplicates_parser.add_argument(
        "--deep-duplicates",
        choices=["same-name", "any-name"],
        default="same-name",
        help="Duplicate analysis mode: 'same-name' (default) or 'any-name' (compare all function bodies regardless of name; slow!)"
    )
    duplicates_parser.add_argument(
        "--no-prod-filter",
        action="store_true",
        help="Show ALL duplicates, including those only in archive/tests (by default только production-код)"
    )

    # Epic management
    epic.add_epic_cli_subparser(subparsers)

    args = parser.parse_args()

    # Нормализация include/exclude паттернов и директорий
    def normalize_patterns(arglist):
        if not arglist:
            return []
        result = []
        for item in arglist:
            if not item:
                continue
            if "," in item:
                result.extend([p.strip() for p in item.split(",") if p.strip()])
            else:
                result.append(item.strip())
        return result

    if hasattr(args, "include"):
        args.include = normalize_patterns(args.include)
    if hasattr(args, "exclude"):
        args.exclude = normalize_patterns(args.exclude)
    if hasattr(args, "include_dir"):
        args.include_dir = normalize_patterns(args.include_dir)
    if hasattr(args, "exclude_dir"):
        args.exclude_dir = normalize_patterns(args.exclude_dir)

    if args.command == "parse":
        parse(args)
    elif args.command == "query":
        asyncio.run(query(args))
    elif args.command == "context":
        context(args)
    elif args.command == "dogfood":
        dogfood(args)
    elif args.command == "review":
        review(args)
    elif args.command == "copilot":
        copilot(args)
    elif args.command == "audit":
        audit(args)
    elif args.command == "analyze-duplicates":
        analyze_duplicates(args)

if __name__ == "__main__":
    main()
