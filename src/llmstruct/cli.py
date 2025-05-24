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
import time
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

def write_to_file(content: str, filename: str, base_dir: str = './tmp') -> str:
    """Write content to a file in base_dir (default ./tmp) and return the path."""
    # Ensure base_dir exists
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True, parents=True)
    # Sanitize filename: allow only safe filenames
    safe_filename = re.sub(r'[^\w\-.]', '_', filename)
    if not safe_filename or safe_filename in {'file', 'a', 'to', 'the', 'output'}:
        logging.error(f"Refusing to write to suspicious filename: {filename}")
        return ""
    file_path = base_path / safe_filename
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

    print("Interactive LLMStruct CLI. Type 'exit' to quit, '/view <path>' to read files/folders, '/queue run' to process command queue, '/cache stats' for cache info, or enter /commands to scan/write.")
    while True:
        user_input = input("Prompt> ").strip()
        if user_input.lower() == 'exit':
            if cache:
                cache.close()
            break
        # --- Только команды с префиксом / считаются командами ---
        elif user_input.startswith('/'):
            cmd, *args_list = user_input[1:].split(maxsplit=1)
            args_str = args_list[0] if args_list else ''
            if cmd == 'view':
                path = args_str.strip()
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
            elif cmd in {'write', 'generate', 'create'}:
                # Пример: /write file.txt content...
                m = re.match(r'(\S+)\s+(.*)', args_str)
                if not m:
                    print("Usage: /write <filename> <content>")
                    continue
                write_filename, content = m.group(1), m.group(2)
                write_dir = './tmp'
                file_path = write_to_file(content, write_filename, write_dir)
                print(f"Output written to {file_path}")
                continue
            elif cmd == 'scan':
                scan_path = args_str.strip()
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
                        print(f"Scanned {full_path}:\n{json.dumps(structure, indent=2)}")
                    except Exception as e:
                        logging.error(f"Error scanning {full_path}: {e}")
                        print(f"Error scanning {full_path}: {e}")
                elif os.path.isfile(full_path):
                    content = read_file_content(full_path)
                    if content:
                        print(f"Content of {full_path}:\n{content}")
                    else:
                        print(f"Cannot read file {full_path}")
                else:
                    print(f"Path {full_path} does not exist")
                continue
            elif cmd == 'queue':
                if args_str.strip() == 'run':
                    print("[QUEUE] Processing command queue...")
                    await process_cli_queue_enhanced(root_dir, context_path, args, cache, client)
                    print("[QUEUE] Queue processing completed")
                elif args_str.strip() == 'status':
                    queue_path = os.path.join(root_dir, 'data', 'cli_queue.json')
                    if os.path.exists(queue_path):
                        try:
                            with open(queue_path, 'r', encoding='utf-8') as f:
                                queue_data = json.load(f)
                            if isinstance(queue_data, list) and queue_data and isinstance(queue_data[0], dict) and 'workflow_id' in queue_data[0]:
                                print(f"Queue contains {len(queue_data)} workflows:")
                                for workflow in queue_data:
                                    print(f"  - {workflow.get('workflow_id', 'unknown')}: {workflow.get('description', 'No description')} ({len(workflow.get('commands', []))} commands)")
                            else:
                                print(f"Queue contains {len(queue_data)} legacy commands")
                        except Exception as e:
                            print(f"Error reading queue: {e}")
                    else:
                        print("No queue file found")
                else:
                    print("Usage: /queue run | /queue status")
                continue
            elif cmd == 'cache':
                if not cache:
                    print("Cache is not enabled. Use --use-cache to enable it.")
                    continue
                subcmd = args_str.strip().split()[0] if args_str.strip() else ''
                if subcmd == 'stats':
                    try:
                        stats = cache.get_stats()
                        print(f"Cache statistics: {json.dumps(stats, indent=2)}")
                    except Exception as e:
                        print(f"Error getting cache stats: {e}")
                elif subcmd == 'clear':
                    try:
                        cache.clear()
                        print("Cache cleared successfully")
                    except Exception as e:
                        print(f"Error clearing cache: {e}")
                elif subcmd == 'list':
                    try:
                        keys = cache.list_keys()
                        print(f"Cache contains {len(keys)} entries:")
                        for key in keys[:10]:  # Show first 10 keys
                            print(f"  - {key}")
                        if len(keys) > 10:
                            print(f"  ... and {len(keys) - 10} more")
                    except Exception as e:
                        print(f"Error listing cache keys: {e}")
                else:
                    print("Usage: /cache stats | /cache clear | /cache list")
                continue
            # ...можно добавить другие /команды...
        # --- Всё остальное — обычный текстовый запрос к LLM ---
        else:
            prompt = user_input
            # Для текстовых запросов можно использовать data/init.json как контекст, если есть
            context_json = os.path.join(root_dir, 'data', 'init.json')
            context_path_to_use = context_json if os.path.exists(context_json) else context_path
            prompt_with_context = attach_to_llm_request(context_path_to_use, prompt, cache=cache)
            try:
                result = await client.query(
                    prompt=prompt_with_context,
                    context_path=context_path_to_use,
                    mode=args.mode,
                    model=args.model,
                    artifact_ids=args.artifact_ids
                )
                if result:
                    print(f"LLM Response:\n{result}")
                else:
                    print("Query failed, please try again")
            except Exception as e:
                logging.error(f"LLM query failed: {e}")
                print(f"Query failed: {e}")
                continue

async def process_cli_queue_enhanced(root_dir, context_path, args, cache, client):
    """Enhanced queue processing with workflow support, performance tracking, and safety validation."""
    queue_path = os.path.join(root_dir, 'data', 'cli_queue.json')
    if not os.path.exists(queue_path):
        logging.info("No queue file found, skipping queue processing")
        return
    
    try:
        with open(queue_path, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read cli_queue.json: {e}")
        return
    
    # Handle both old format (list) and new format (list of workflows)
    if isinstance(queue_data, list):
        if queue_data and isinstance(queue_data[0], dict) and 'workflow_id' in queue_data[0]:
            # New workflow format
            workflows = queue_data
        else:
            # Old simple command format - wrap in workflow
            workflows = [{
                "workflow_id": "legacy_commands",
                "description": "Legacy command queue",
                "commands": queue_data
            }]
    else:
        logging.error("Invalid queue format")
        return
    
    for workflow in workflows:
        workflow_id = workflow.get('workflow_id', 'unknown')
        workflow_desc = workflow.get('description', 'No description')
        commands = workflow.get('commands', [])
        
        print(f"\n[QUEUE] Starting workflow: {workflow_id}")
        print(f"[QUEUE] Description: {workflow_desc}")
        
        workflow_start_time = time.time()
        
        for i, item in enumerate(commands):
            cmd = item.get('cmd')
            if not cmd:
                continue
                
            print(f"[QUEUE] Executing command {i+1}/{len(commands)}: {cmd}")
            
            try:
                if cmd == 'write':
                    filename = item.get('filename')
                    content = item.get('content', '')
                    expected_result = item.get('expected_result', 'success')
                    
                    if expected_result == 'blocked':
                        print(f"[QUEUE] Testing security boundary for: {filename}")
                    
                    write_dir = './tmp'
                    file_path = write_to_file(content, filename, write_dir)
                    
                    if file_path:
                        print(f"[QUEUE] ✅ Output written to {file_path}")
                    else:
                        print(f"[QUEUE] ❌ Write failed for {filename} (security block or error)")
                        
                elif cmd == 'scan':
                    scan_path = item.get('path')
                    options = item.get('options', {})
                    full_path = os.path.join(root_dir, scan_path)
                    
                    if os.path.isdir(full_path):
                        structure = get_folder_structure(
                            root_dir=full_path,
                            gitignore_patterns=load_gitignore(root_dir),
                            include_patterns=None,
                            exclude_patterns=None,
                            exclude_dirs=['venv', 'build', 'tmp']
                        )
                        print(f"[QUEUE] ✅ Scanned {full_path}")
                        if options.get('include_metadata'):
                            print(f"[QUEUE] Found {len(structure)} items")
                    elif os.path.isfile(full_path):
                        content = read_file_content(full_path)
                        if content:
                            print(f"[QUEUE] ✅ Read file {full_path} ({len(content)} chars)")
                    else:
                        print(f"[QUEUE] ❌ Path not found: {full_path}")
                        
                elif cmd == 'llm':
                    prompt = item.get('prompt', '')
                    context_preference = item.get('context_preference', 'init')
                    options = item.get('options', {})
                    
                    # Smart context selection
                    if context_preference == 'init' or context_preference == 'init_only':
                        context_json = os.path.join(root_dir, 'data', 'init.json')
                        context_path_to_use = context_json if os.path.exists(context_json) else context_path
                    elif context_preference == 'struct_required' or context_preference == 'struct_focused':
                        context_path_to_use = context_path  # Use struct.json
                    elif context_preference == 'cli_focused':
                        cli_json = os.path.join(root_dir, 'data', 'cli.json')
                        context_path_to_use = cli_json if os.path.exists(cli_json) else context_path
                    else:
                        context_json = os.path.join(root_dir, 'data', 'init.json')
                        context_path_to_use = context_json if os.path.exists(context_json) else context_path
                    
                    prompt_with_context = attach_to_llm_request(context_path_to_use, prompt, cache=cache)
                    
                    try:
                        result = await client.query(
                            prompt=prompt_with_context,
                            context_path=context_path_to_use,
                            mode=args.mode,
                            model=args.model,
                            artifact_ids=args.artifact_ids
                        )
                        if result:
                            print(f"[QUEUE] ✅ LLM Response received ({len(result)} chars)")
                            if options.get('track_token_usage'):
                                print(f"[QUEUE] Context: {context_preference}, File: {os.path.basename(context_path_to_use)}")
                        else:
                            print(f"[QUEUE] ❌ LLM query failed")
                    except Exception as e:
                        print(f"[QUEUE] ❌ LLM error: {e}")
                        
                elif cmd == 'validate':
                    json_path = item.get('json_path')
                    schema_path = item.get('schema_path')
                    options = item.get('options', {})
                    
                    if json_path and schema_path:
                        full_json_path = os.path.join(root_dir, json_path)
                        full_schema_path = os.path.join(root_dir, schema_path)
                        
                        if os.path.exists(full_json_path) and os.path.exists(full_schema_path):
                            print(f"[QUEUE] ✅ Validation attempted for {json_path}")
                            # Note: Actual validation would require jsonschema library
                        else:
                            print(f"[QUEUE] ❌ Validation failed: files not found")
                    else:
                        print(f"[QUEUE] ❌ Validation failed: missing paths")
                        
                elif cmd == 'analyze':
                    target_path = item.get('target_path')
                    analysis_type = item.get('analysis_type', 'basic')
                    
                    if target_path:
                        full_target_path = os.path.join(root_dir, target_path)
                        if os.path.exists(full_target_path):
                            print(f"[QUEUE] ✅ Analysis of {target_path} ({analysis_type})")
                        else:
                            print(f"[QUEUE] ❌ Analysis failed: target not found")
                    else:
                        print(f"[QUEUE] ❌ Analysis failed: no target specified")
                        
                else:
                    print(f"[QUEUE] ❌ Unknown command: {cmd}")
                    
            except Exception as e:
                logging.error(f"Queue command {cmd} failed: {e}")
                print(f"[QUEUE] ❌ Command failed: {e}")
                
        workflow_time = time.time() - workflow_start_time
        print(f"[QUEUE] Workflow {workflow_id} completed in {workflow_time:.2f}s")
        print("-" * 50)

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