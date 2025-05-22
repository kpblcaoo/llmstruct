# cli.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import argparse
import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import List, Optional
import uuid

import toml
from llmstruct import LLMClient
from llmstruct.generators.json_generator import generate_json, get_folder_structure
from llmstruct.self_run import attach_to_llm_request
from llmstruct.cache import JSONCache

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

def read_file_content(file_path: str) -> Optional[str]:
    """Read content of a file if it exists and is a text file."""
    path = Path(file_path)
    if path.is_file():
        try:
            with path.open('r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
    return None

def write_to_file(content: str, filename: str, base_dir: str = '/tmp') -> str:
    """Write content to a file in base_dir (default /tmp) and return the path."""
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True)
    file_path = base_path / filename
    if file_path.exists():
        logging.warning(f"File {file_path} already exists, overwriting")
    try:
        with file_path.open('w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Wrote content to {file_path}")
        return str(file_path)
    except Exception as e:
        logging.error(f"Failed to write to {file_path}: {e}")
        return ""

def parse_files_from_response(response: str) -> List[tuple[str, str]]:
    """Extract filenames and content from LLM response (e.g., ```filename\ncontent```)."""
    files = []
    pattern = r'```(\S+?)\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    for filename, content in matches:
        files.append((filename.strip(), content.strip()))
    return files

async def interactive(args: argparse.Namespace):
    """Run interactive CLI with LLM, supporting file/folder viewing and writing."""
    client = LLMClient()
    cache = JSONCache() if args.use_cache else None
    root_dir = os.path.abspath(args.root_dir)
    context_path = args.context
    if not Path(context_path).exists():
        logging.warning(f"Context file {context_path} does not exist, generating new struct.json")
        parse(args)

    print("Interactive LLMStruct CLI. Type 'exit' to quit, 'view <path>' to read files/folders, or enter prompts to scan/write.")
    while True:
        user_input = input("Prompt> ").strip()
        if user_input.lower() == 'exit':
            if cache:
                cache.close()
            break
        elif user_input.lower().startswith('view '):
            path = user_input[5:].strip()
            full_path = os.path.join(root_dir, path)
            if os.path.isdir(full_path):
                try:
                    gitignore_patterns = load_gitignore(root_dir)
                    structure = get_folder_structure(
                        root_dir=full_path,
                        gitignore_patterns=gitignore_patterns,
                        include_patterns=None,
                        exclude_patterns=None,
                        exclude_dirs=['venv', 'build', 'tmp']
                    )
                    if not structure:
                        logging.warning(f"No items found in {full_path}, falling back to os.listdir")
                        items = os.listdir(full_path)
                        structure = [
                            {"path": os.path.join(path, item), "type": "directory" if os.path.isdir(os.path.join(full_path, item)) else "file"}
                            for item in sorted(items)
                        ]
                    print(f"Directory structure for {full_path}:\n{json.dumps(structure, indent=2)}")
                except Exception as e:
                    logging.error(f"Error reading directory {full_path}: {e}")
                    print(f"Error reading directory {full_path}: {e}")
            elif os.path.isfile(full_path):
                content = read_file_content(full_path)
                if content:
                    print(f"Content of {full_path}:\n{content}")
                else:
                    print(f"Cannot read file {full_path}")
            else:
                print(f"Path {full_path} does not exist")
            continue
        else:
            prompt = user_input
            scan_match = re.search(r'(?:scan|view|analyze)\s+(\S+)', prompt, re.IGNORECASE)
            write_match = re.search(r'(?:write|generate|create)\s+(?:to\s+)?(\S+)', prompt, re.IGNORECASE)
            scan_path = scan_match.group(1) if scan_match else None
            write_filename = write_match.group(1) if write_match else None
            write_dir = '/tmp'
            if write_filename and '/' in write_filename:
                write_dir, write_filename = os.path.split(write_filename)
                write_dir = os.path.join(root_dir, write_dir) if not write_dir.startswith('/') else write_dir

            scan_result = None
            if scan_path:
                full_path = os.path.join(root_dir, scan_path)
                if os.path.isdir(full_path):
                    try:
                        gitignore_patterns = load_gitignore(root_dir)
                        structure = get_folder_structure(
                            root_dir=full_path,
                            gitignore_patterns=gitignore_patterns,
                            include_patterns=None,
                            exclude_patterns=None,
                            exclude_dirs=['venv', 'build', 'tmp']
                        )
                        scan_result = json.dumps(structure, indent=2)
                        print(f"Scanned {full_path}:\n{scan_result}")
                    except Exception as e:
                        logging.error(f"Error scanning {full_path}: {e}")
                        print(f"Error scanning {full_path}: {e}")
                elif os.path.isfile(full_path):
                    scan_result = read_file_content(full_path)
                    if scan_result:
                        print(f"Content of {full_path}:\n{scan_result}")
                    else:
                        print(f"Cannot read file {full_path}")
                else:
                    print(f"Path {full_path} does not exist")

            prompt_with_context = attach_to_llm_request(context_path, prompt + (f"\n\nScanned data:\n{scan_result}" if scan_result else ""), cache=cache)
            try:
                result = await client.query(
                    prompt=prompt_with_context,
                    context_path=context_path,
                    mode=args.mode,
                    model=args.model,
                    artifact_ids=args.artifact_ids
                )
                if result:
                    print(f"LLM Response:\n{result}")
                    files_to_write = parse_files_from_response(result)
                    if write_filename:
                        files_to_write.append((write_filename, result))
                    for filename, content in files_to_write:
                        file_path = write_to_file(content, filename, write_dir)
                        print(f"Output written to {file_path}")
                else:
                    print("Query failed, please try again")
            except Exception as e:
                logging.error(f"LLM query failed: {e}")
                print(f"Query failed: {e}")
                continue

def parse(args: argparse.Namespace):
    """Parse codebase and generate struct.json."""
    root_dir = os.path.abspath(args.root_dir)
    config = load_config(root_dir)
    
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
        # Cache the generated JSON
        if args.use_cache:
            cache = JSONCache()
            cache.cache_json(args.output, args.output, summary="Generated struct.json", tags=["struct"])
            cache.close()
    except Exception as e:
        logging.error(f"Failed to generate JSON: {e}")
        raise

async def query(args: argparse.Namespace):
    """Query LLMs with prompt and context."""
    if not Path(args.context).exists():
        logging.error(f"Context file {args.context} does not exist")
        return
    cache = JSONCache() if args.use_cache else None
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
    if cache:
        cache.close()

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

    parse_parser = subparsers.add_parser("parse", help="Parse codebase and generate struct.json")
    parse_parser.add_argument("root_dir", help="Root directory of the project")
    parse_parser.add_argument("-o", "--output", default="struct.json", help="Output JSON file")
    parse_parser.add_argument("--language", choices=["python", "javascript"], help="Programming language")
    parse_parser.add_argument("--include", action="append", help="Include patterns (e.g., '*.py')")
    parse_parser.add_argument("--exclude", action="append", help="Exclude patterns (e.g., 'tests/*')")
    parse_parser.add_argument("--include-ranges", action="store_true", help="Include line ranges for functions/classes")
    parse_parser.add_argument("--include-hashes", action="store_true", help="Include file hashes")
    parse_parser.add_argument("--goals", nargs="*", help="Custom project goals")
    parse_parser.add_argument("--use-cache", action="store_true", help="Cache generated JSON")

    query_parser = subparsers.add_parser("query", help="Query LLMs with prompt and context")
    query_parser.add_argument("--prompt", required=True, help="Prompt for LLM")
    query_parser.add_argument("--context", default="struct.json", help="Context JSON file")
    query_parser.add_argument("--mode", choices=["grok", "anthropic", "ollama", "hybrid"], default="hybrid", help="LLM mode")
    query_parser.add_argument("--model", help="Ollama model (e.g., mixtral, llama3)")
    query_parser.add_argument("--artifact-ids", nargs="*", default=[], help="Artifact IDs to include in context")
    query_parser.add_argument("--output", default="llm_response.json", help="Output JSON file for LLM response")
    query_parser.add_argument("--use-cache", action="store_true", help="Use JSON cache")

    interactive_parser = subparsers.add_parser("interactive", help="Run interactive CLI with LLM")
    interactive_parser.add_argument("root_dir", help="Root directory of the project")
    interactive_parser.add_argument("--context", default="struct.json", help="Context JSON file")
    interactive_parser.add_argument("--mode", choices=["grok", "anthropic", "ollama", "hybrid"], default="hybrid", help="LLM mode")
    interactive_parser.add_argument("--model", help="Ollama model (e.g., mixtral, llama3)")
    interactive_parser.add_argument("--artifact-ids", nargs="*", default=[], help="Artifact IDs to include in context")
    interactive_parser.add_argument("--use-cache", action="store_true", help="Use JSON cache")

    context_parser = subparsers.add_parser("context", help="Generate context.json from input JSON")
    context_parser.add_argument("--input", default="struct.json", help="Input JSON file")
    context_parser.add_argument("--output", default="context.json", help="Output context JSON file")
    context_parser.add_argument("--priority", action="append", default=["src/llmstruct/"], help="Priority directories/files")

    dogfood_parser = subparsers.add_parser("dogfood", help="Run dogfooding analysis")
    dogfood_parser.add_argument("--input", default="src/llmstruct/", help="Input directory")
    dogfood_parser.add_argument("--output", default="dogfood_report.json", help="Output report JSON")

    review_parser = subparsers.add_parser("review", help="Review codebase with LLM")
    review_parser.add_argument("--input", default="src/llmstruct/", help="Input directory")
    review_parser.add_argument("--mode", choices=["grok", "anthropic", "ollama", "hybrid"], default="hybrid", help="LLM mode")
    review_parser.add_argument("--output", default="review_report.json", help="Output report JSON")

    args = parser.parse_args()

    if args.command == "parse":
        parse(args)
    elif args.command == "query":
        asyncio.run(query(args))
    elif args.command == "interactive":
        asyncio.run(interactive(args))
    elif args.command == "context":
        context(args)
    elif args.command == "dogfood":
        dogfood(args)
    elif args.command == "review":
        review(args)

if __name__ == "__main__":
    main()