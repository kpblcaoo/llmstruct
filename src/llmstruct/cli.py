import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import toml

from llmstruct import LLMClient
from llmstruct.generators.json_generator import generate_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_gitignore(root_dir: str) -> List[str]:
    """Load and normalize patterns from .gitignore."""
    gitignore_path = Path(root_dir) / '.gitignore'
    patterns = []
    if gitignore_path.exists():
        try:
            with gitignore_path.open('r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            logging.error(f"Failed to read .gitignore: {e}")
    return patterns

def load_config(root_dir: str) -> dict:
    """Load settings from llmstruct.toml or return empty dict."""
    config_path = Path(root_dir) / 'llmstruct.toml'
    if config_path.exists():
        try:
            with config_path.open('r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            logging.error(f"Failed to read llmstruct.toml: {e}")
    return {}

def parse(args: argparse.Namespace):
    """Parse codebase and generate struct.json."""
    root_dir = os.path.abspath(args.root_dir)
    config = load_config(root_dir)
    
    # CLI args override config
    goals = args.goals if args.goals is not None else config.get('goals', [])
    if not goals:
        logging.warning("No project goals specified via --goals or llmstruct.toml. Consider adding goals for better context.")
    
    language = args.language or config.get('cli', {}).get('language', 'python')
    include_patterns = args.include or config.get('cli', {}).get('include_patterns')
    exclude_patterns = args.exclude or config.get('cli', {}).get('exclude_patterns')
    include_ranges = args.include_ranges or config.get('cli', {}).get('include_ranges', False)
    include_hashes = args.include_hashes or config.get('cli', {}).get('include_hashes', False)
    use_gitignore = config.get('cli', {}).get('use_gitignore', True)
    exclude_dirs = config.get('cli', {}).get('exclude_dirs', [])
    
    gitignore_patterns = load_gitignore(root_dir) if use_gitignore else []

    try:
        struct_data = generate_json(
            root_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            gitignore_patterns=gitignore_patterns,
            include_ranges=include_ranges,
            include_hashes=include_hashes,
            goals=goals,
            exclude_dirs=exclude_dirs
        )
        with Path(args.output).open('w', encoding='utf-8') as f:
            json.dump(struct_data, f, indent=2)
        logging.info(f"Generated {args.output}")
    except Exception as e:
        logging.error(f"Failed to generate JSON: {e}")
        raise

async def query(args: argparse.Namespace):
    """Query LLMs with prompt and context."""
    if not Path(args.context).exists():
        logging.error(f"Context file {args.context} does not exist")
        return
    client = LLMClient()
    result = await client.query(
        prompt=args.prompt,
        context_path=args.context,
        mode=args.mode,
        model=args.model,
        artifact_ids=args.artifact_ids
    )
    if result:
        with Path(args.output).open("w", encoding="utf-8") as f:
            json.dump({"prompt": args.prompt, "response": result}, f, indent=2)
        logging.info(f"Generated {args.output}")
    else:
        logging.error("Query failed")

def context(args: argparse.Namespace):
    """Generate context.json from input JSON."""
    logging.warning("Context command not implemented yet (TSK-091)")

def dogfood(args: argparse.Namespace):
    """Run dogfooding analysis."""
    logging.warning("Dogfood command not implemented yet (TSK-095)")

def review(args: argparse.Namespace):
    """Review codebase with LLM."""
    logging.warning("Review command not implemented yet (TSK-096)")

def main():
    """Command-line interface for LLMstruct."""
    parser = argparse.ArgumentParser(description="Generate structured JSON for codebases and query LLMs")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse codebase and generate struct.json")
    parse_parser.add_argument("root_dir", help="Root directory of the project")
    parse_parser.add_argument("-o", "--output", default="struct.json", help="Output JSON file")
    parse_parser.add_argument("--language", choices=["python", "javascript"], help="Programming language")
    parse_parser.add_argument("--include", action="append", help="Include patterns (e.g., '*.py')")
    parse_parser.add_argument("--exclude", action="append", help="Exclude patterns (e.g., 'tests/*')")
    parse_parser.add_argument("--include-ranges", action="store_true", help="Include line ranges for functions/classes")
    parse_parser.add_argument("--include-hashes", action="store_true", help="Include file hashes")
    parse_parser.add_argument("--goals", nargs="*", help="Custom project goals")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query LLMs with prompt and context")
    query_parser.add_argument("--prompt", required=True, help="Prompt for LLM")
    query_parser.add_argument("--context", default="context.json", help="Context JSON file")
    query_parser.add_argument("--mode", choices=["grok", "anthropic", "ollama", "hybrid"], default="hybrid", help="LLM mode")
    query_parser.add_argument("--model", help="Ollama model (e.g., mixtral, llama3)")
    query_parser.add_argument("--artifact-ids", nargs="*", default=[], help="Artifact IDs to include in context")
    query_parser.add_argument("--output", default="llm_response.json", help="Output JSON file for LLM response")

    # Context command
    context_parser = subparsers.add_parser("context", help="Generate context.json from input JSON")
    context_parser.add_argument("--input", default="struct.json", help="Input JSON file")
    context_parser.add_argument("--output", default="context.json", help="Output context JSON file")
    context_parser.add_argument("--priority", action="append", default=["src/llmstruct/"], help="Priority directories/files")

    # Dogfood command
    dogfood_parser = subparsers.add_parser("dogfood", help="Run dogfooding analysis")
    dogfood_parser.add_argument("--input", default="src/llmstruct/", help="Input directory")
    dogfood_parser.add_argument("--output", default="dogfood_report.json", help="Output report JSON")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review codebase with LLM")
    review_parser.add_argument("--input", default="src/llmstruct/", help="Input directory")
    review_parser.add_argument("--mode", choices=["grok", "anthropic", "ollama", "hybrid"], default="hybrid", help="LLM mode")
    review_parser.add_argument("--output", default="review_report.json", help="Output report JSON")

    args = parser.parse_args()

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

if __name__ == "__main__":
    main()