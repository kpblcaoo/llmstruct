# cli_argument_parser.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""CLI argument parsing for LLMStruct."""

import argparse
from pathlib import Path


def create_argument_parser():
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(description="LLMStruct - LLM-powered codebase analysis tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse codebase and generate struct.json")
    parse_parser.add_argument("root_dir", help="Root directory of the project")
    parse_parser.add_argument("--output", default="struct.json", help="Output JSON file")
    parse_parser.add_argument("--use-cache", action="store_true", help="Use caching")
    parse_parser.add_argument("--include-patterns", nargs="*", help="Include patterns")
    parse_parser.add_argument("--exclude-patterns", nargs="*", help="Exclude patterns")
    parse_parser.add_argument("--exclude-dirs", nargs="*", help="Exclude directories")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query LLM with context")
    query_parser.add_argument("prompt", help="Prompt for the LLM")
    query_parser.add_argument("context", help="Context file path")
    query_parser.add_argument("--output", default="response.json", help="Output file")
    query_parser.add_argument("--use-cache", action="store_true", help="Use caching")
    query_parser.add_argument("--mode", default="complex", help="LLM mode")
    query_parser.add_argument("--model", help="LLM model to use")
    query_parser.add_argument("--artifact-ids", nargs="*", help="Artifact IDs")
    query_parser.add_argument("--context-mode", choices=["FULL", "FOCUSED", "MINIMAL", "SESSION"], 
                             help="Context optimization mode")

    # Interactive command  
    interactive_parser = subparsers.add_parser("interactive", help="Run interactive CLI")
    interactive_parser.add_argument("root_dir", help="Root directory of the project")
    interactive_parser.add_argument("--context", default="struct.json", help="Context file")
    interactive_parser.add_argument("--use-cache", action="store_true", help="Use caching")
    interactive_parser.add_argument("--mode", default="complex", help="LLM mode")
    interactive_parser.add_argument("--model", help="LLM model to use")
    interactive_parser.add_argument("--artifact-ids", nargs="*", help="Artifact IDs")

    # Context command
    context_parser = subparsers.add_parser("context", help="Generate context.json from input")
    context_parser.add_argument("input", help="Input JSON file")
    context_parser.add_argument("--output", default="context.json", help="Output context file")

    # Dogfood command
    dogfood_parser = subparsers.add_parser("dogfood", help="Run dogfooding analysis")
    dogfood_parser.add_argument("root_dir", help="Root directory of the project")
    dogfood_parser.add_argument("--output", default="dogfood_report.json", help="Output report JSON")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review codebase with LLM")
    review_parser.add_argument("root_dir", help="Root directory of the project")
    review_parser.add_argument("--context", default="struct.json", help="Context file")
    review_parser.add_argument("--mode", default="complex", help="LLM mode")
    review_parser.add_argument("--output", default="review_report.json", help="Output report JSON")

    # Copilot command
    copilot_parser = subparsers.add_parser("copilot", help="Copilot integration and context management")
    copilot_parser.add_argument("root_dir", help="Root directory of the project")
    copilot_parser.add_argument(
        "copilot_command",
        choices=["init", "status", "load", "unload", "refresh", "suggest", "validate", "export"],
        help="Copilot command",
    )
    copilot_parser.add_argument("--layer", help="Layer name for load/unload commands")
    copilot_parser.add_argument("--query", help="Query for suggest command")
    copilot_parser.add_argument("--file-path", help="File path for validate command")
    copilot_parser.add_argument(
        "--change-type",
        choices=["edit", "delete", "add"],
        help="Change type for validate command"
    )
    copilot_parser.add_argument("--context", help="Context type for suggest command")
    copilot_parser.add_argument("--force", action="store_true", help="Force initialization")
    copilot_parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Export format")
    copilot_parser.add_argument("--layers", help="Comma-separated list of layers to export")
    copilot_parser.add_argument("--output", help="Output file for export")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit project structure")
    audit_parser.add_argument("root_dir", help="Root directory of the project")
    audit_parser.add_argument("--include-duplicates", action="store_true", help="Include duplication analysis")

    # Analyze duplicates command
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

    return parser


def add_api_bot_commands(subparsers):
    """Add API and bot management commands to the parser."""
    try:
        from .api_commands import add_api_commands
        from .bot_commands import add_bot_commands
        
        add_api_commands(subparsers)
        add_bot_commands(subparsers)
    except ImportError:
        # API/Bot commands not available
        pass


def create_full_argument_parser():
    """Create the full argument parser with all commands."""
    parser = create_argument_parser()
    subparsers = parser._subparsers._group_actions[0]
    
    # Add API and Bot commands if available
    add_api_bot_commands(subparsers)
    
    return parser
