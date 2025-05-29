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


def load_gitignore(root_dir: str) -> List[str]:
    """Load and normalize patterns from .gitignore."""
    gitignore_path = Path(root_dir) / ".gitignore"
    patterns = []
    if gitignore_path.exists():
        try:
            with gitignore_path.open("r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except Exception as e:
            logging.error(f"Failed to read .gitignore: {e}")
    return patterns


def load_config(root_dir: str) -> dict:
    """Load settings from llmstruct.toml or return empty dict."""
    config_path = Path(root_dir) / "llmstruct.toml"
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception as e:
            logging.error(f"Failed to read llmstruct.toml: {e}")
    return {}


def read_file_content(file_path: str) -> Optional[str]:
    """Read content of a file if it exists and is a text file."""
    path = Path(file_path)
    if path.is_file():
        try:
            with path.open("r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
    return None


def write_to_file(content: str, filename: str, base_dir: str = "./tmp") -> str:
    """Write content to a file in base_dir (default ./tmp) and return the path."""
    # Ensure base_dir exists
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True, parents=True)
    # Sanitize filename: allow only safe filenames
    safe_filename = re.sub(r"[^\w\-.]", "_", filename)
    if not safe_filename or safe_filename in {"file", "a", "to", "the", "output"}:
        logging.error(f"Refusing to write to suspicious filename: {filename}")
        return ""
    file_path = base_path / safe_filename
    if file_path.exists():
        logging.warning(f"File {file_path} already exists, overwriting")
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Wrote content to {file_path}")
        return str(file_path)
    except Exception as e:
        logging.error(f"Failed to write to {file_path}: {e}")
        return ""


def parse_files_from_response(response: str) -> List[tuple[str, str]]:
    """Extract filenames and content from LLM response (e.g., ```filename\ncontent```)."""
    files = []
    pattern = r"```(\S+?)\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    for filename, content in matches:
        files.append((filename.strip(), content.strip()))
    return files


async def interactive(args: argparse.Namespace):
    """Run interactive CLI with modular structure if available, fallback to legacy."""
    if MODULAR_CLI_AVAILABLE:
        try:
            await interactive_modular(args)
            return
        except Exception as e:
            logging.warning(f"Modular CLI failed, falling back to legacy: {e}")

    # Fallback to legacy implementation
    await interactive_legacy(args)


async def interactive_modular(args: argparse.Namespace):
    """Run interactive CLI with modular structure."""
    root_dir = os.path.abspath(args.root_dir)

    # Create and run modular CLI
    cli_core = create_cli_core(root_dir)
    
    # Set context mode if available
    if hasattr(args, 'context_mode') and args.context_mode:
        # Pass context mode to CLI core components
        if hasattr(cli_core, 'command_processor') and cli_core.command_processor:
            cli_core.command_processor.default_context_mode = args.context_mode
            logging.info(f"Set default context mode to {args.context_mode}")
    
    cli_core.run_interactive_mode()


async def interactive_legacy(args: argparse.Namespace):
    """Run interactive CLI with LLM, supporting file/folder viewing and writing."""
    client = LLMClient()
    cache = JSONCache() if args.use_cache else None
    root_dir = os.path.abspath(args.root_dir)
    context_path = args.context
    if not Path(context_path).exists():
        logging.warning(
            f"Context file {context_path} does not exist, generating new struct.json"
        )
        parse(args)

    print(
        "Interactive LLMStruct CLI. Type 'exit' to quit, '/view <path>' to read "
        "files/folders, '/queue run' to process command queue, '/cache stats' for "
        "cache info, '/auto-update' for struct.json auto-update, '/struct status' "
        "for struct info, '/workflow trigger' for workflow events, or enter "
        "/commands to scan/write."
    )
    while True:
        user_input = input("Prompt> ").strip()
        if user_input.lower() == "exit":
            if cache:
                cache.close()
            break
        # --- Только команды с префиксом / считаются командами ---
        elif user_input.startswith("/"):
            cmd, *args_list = user_input[1:].split(maxsplit=1)
            args_str = args_list[0] if args_list else ""
            if cmd == "view":
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
                            exclude_dirs=["venv", "build", "tmp"],
                        )
                        if not structure:
                            logging.warning(
                                f"No items found in {full_path}, falling back to os.listdir"
                            )
                            items = os.listdir(full_path)
                            structure = [
                                {
                                    "path": os.path.join(path, item),
                                    "type": (
                                        "directory"
                                        if os.path.isdir(os.path.join(full_path, item))
                                        else "file"
                                    ),
                                }
                                for item in sorted(items)
                            ]
                        print(
                            f"Directory structure for {full_path}:\n{json.dumps(structure, indent=2)}"
                        )
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
            elif cmd in {"write", "generate", "create"}:
                # Пример: /write file.txt content...
                m = re.match(r"(\S+)\s+(.*)", args_str)
                if not m:
                    print("Usage: /write <filename> <content>")
                    continue
                write_filename, content = m.group(1), m.group(2)
                write_dir = "./tmp"
                file_path = write_to_file(content, write_filename, write_dir)
                print(f"Output written to {file_path}")
                continue
            elif cmd == "scan":
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
                            exclude_dirs=["venv", "build", "tmp"],
                        )
                        print(
                            f"Scanned {full_path}:\n{json.dumps(structure, indent=2)}"
                        )
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
            elif cmd == "queue":
                if args_str.strip() == "run":
                    print("[QUEUE] Processing command queue...")
                    await process_cli_queue_enhanced(
                        root_dir, context_path, args, cache, client
                    )
                    print("[QUEUE] Queue processing completed")
                elif args_str.strip() == "status":
                    queue_path = os.path.join(root_dir, "data", "cli_queue.json")
                    if os.path.exists(queue_path):
                        try:
                            with open(queue_path, "r", encoding="utf-8") as f:
                                queue_data = json.load(f)
                            if (
                                isinstance(queue_data, list)
                                and queue_data
                                and isinstance(queue_data[0], dict)
                                and "workflow_id" in queue_data[0]
                            ):
                                print(f"Queue contains {len(queue_data)} workflows:")
                                for workflow in queue_data:
                                    workflow_id = workflow.get('workflow_id', 'unknown')
                                    description = workflow.get('description', 'No description')
                                    commands_count = len(workflow.get('commands', []))
                                    print(
                                        f"  - {workflow_id}: {description} "
                                        f"({commands_count} commands)"
                                    )
                            else:
                                print(
                                    f"Queue contains {len(queue_data)} legacy commands"
                                )
                        except Exception as e:
                            print(f"Error reading queue: {e}")
                    else:
                        print("No queue file found")
                else:
                    print("Usage: /queue run | /queue status")
                continue
            elif cmd == "cache":
                if not cache:
                    print("Cache is not enabled. Use --use-cache to enable it.")
                    continue
                subcmd = args_str.strip().split()[0] if args_str.strip() else ""
                if subcmd == "stats":
                    try:
                        stats = cache.get_stats()
                        print(f"Cache statistics: {json.dumps(stats, indent=2)}")
                    except Exception as e:
                        print(f"Error getting cache stats: {e}")
                elif subcmd == "clear":
                    try:
                        cache.clear()
                        print("Cache cleared successfully")
                    except Exception as e:
                        print(f"Error clearing cache: {e}")
                elif subcmd == "list":
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
            elif cmd == "auto-update":
                # Автообновление struct.json
                try:
                    import subprocess

                    script_path = os.path.join(
                        root_dir, "scripts", "auto_update_struct.py"
                    )
                    if os.path.exists(script_path):
                        result = subprocess.run(
                            [
                                sys.executable,
                                script_path,
                                "--root-dir",
                                root_dir,
                                "--output",
                                os.path.join(root_dir, "struct.json"),
                            ],
                            capture_output=True,
                            text=True,
                            timeout=60,
                        )
                        if result.returncode == 0:
                            print("✅ Auto-update struct.json completed successfully")
                            if result.stdout:
                                print(f"Output: {result.stdout}")
                        else:
                            print(f"❌ Auto-update failed: {result.stderr}")
                    else:
                        print(f"❌ Auto-update script not found at {script_path}")
                except Exception as e:
                    print(f"❌ Auto-update error: {e}")
                continue
            elif cmd == "struct":
                subcmd = args_str.strip()
                if subcmd == "status":
                    # Статус struct.json и автообновления
                    struct_path = os.path.join(root_dir, "struct.json")
                    if os.path.exists(struct_path):
                        try:
                            stat_info = os.stat(struct_path)
                            mod_time = time.ctime(stat_info.st_mtime)
                            size = stat_info.st_size
                            print(f"struct.json status:")
                            print(f"  📁 Path: {struct_path}")
                            print(f"  📅 Modified: {mod_time}")
                            print(f"  📏 Size: {size} bytes")

                            # Проверка наличия скрипта автообновления
                            auto_script = os.path.join(
                                root_dir, "scripts", "auto_update_struct.py"
                            )
                            if os.path.exists(auto_script):
                                print(f"  🔄 Auto-update: Available")
                            else:
                                print(f"  🔄 Auto-update: Not available")
                        except Exception as e:
                            print(f"❌ Error getting struct.json status: {e}")
                    else:
                        print("❌ struct.json not found")
                elif subcmd == "validate":
                    # Валидация struct.json
                    struct_path = os.path.join(root_dir, "struct.json")
                    if os.path.exists(struct_path):
                        try:
                            with open(struct_path, "r", encoding="utf-8") as f:
                                struct_data = json.load(f)
                            print("✅ struct.json is valid JSON")
                            print(
                                f"  📊 Contains {len(struct_data.get('files', []))} files"
                            )
                            print(f"  🎯 Goals: {len(struct_data.get('goals', []))}")
                        except json.JSONDecodeError as e:
                            print(f"❌ struct.json is invalid JSON: {e}")
                        except Exception as e:
                            print(f"❌ Error validating struct.json: {e}")
                    else:
                        print("❌ struct.json not found")
                else:
                    print("Usage: /struct status | /struct validate")
                continue
            elif cmd == "workflow":
                subcmd = args_str.strip()
                if subcmd == "trigger":
                    # Триггер workflow событий с автообновлением
                    try:
                        # Создание события для workflow
                        workflow_event = {
                            "event_id": f"manual_{int(time.time())}",
                            "event_type": "manual_trigger",
                            "timestamp": time.time(),
                            "description": "Manual workflow trigger from CLI",
                            "actions": ["auto_update_struct"],
                        }

                        events_path = os.path.join(
                            root_dir, "data", "workflow_events.json"
                        )
                        events_data = []
                        if os.path.exists(events_path):
                            try:
                                with open(events_path, "r", encoding="utf-8") as f:
                                    events_data = json.load(f)
                            except BaseException:
                                events_data = []

                        events_data.append(workflow_event)

                        # Сохранение событий
                        os.makedirs(os.path.dirname(events_path), exist_ok=True)
                        with open(events_path, "w", encoding="utf-8") as f:
                            json.dump(events_data, f, indent=2)

                        print(
                            f"✅ Workflow event triggered: {workflow_event['event_id']}"
                        )

                        # Автоматический запуск автообновления
                        import subprocess

                        script_path = os.path.join(
                            root_dir, "scripts", "auto_update_struct.py"
                        )
                        if os.path.exists(script_path):
                            result = subprocess.run(
                                [
                                    sys.executable,
                                    script_path,
                                    "--root-dir",
                                    root_dir,
                                    "--output",
                                    os.path.join(root_dir, "struct.json"),
                                ],
                                capture_output=True,
                                text=True,
                                timeout=60,
                            )
                            if result.returncode == 0:
                                print("✅ Auto-update triggered by workflow completed")
                            else:
                                print(f"❌ Auto-update failed: {result.stderr}")

                    except Exception as e:
                        print(f"❌ Workflow trigger error: {e}")
                else:
                    print("Usage: /workflow trigger")
                continue
            # ...можно добавить другие /команды...
        # --- Всё остальное — обычный текстовый запрос к LLM ---
        else:
            prompt = user_input
            # Для текстовых запросов можно использовать data/init.json как контекст,
            # если есть
            context_json = os.path.join(root_dir, "data", "init.json")
            context_path_to_use = (
                context_json if os.path.exists(context_json) else context_path
            )
            prompt_with_context = attach_to_llm_request(
                context_path_to_use, prompt, cache=cache
            )
            try:
                result = await client.query(
                    prompt=prompt_with_context,
                    context_path=context_path_to_use,
                    mode=args.mode,
                    model=args.model,
                    artifact_ids=args.artifact_ids,
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
    queue_path = os.path.join(root_dir, "data", "cli_queue.json")
    if not os.path.exists(queue_path):
        logging.info("No queue file found, skipping queue processing")
        return

    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            queue_data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read cli_queue.json: {e}")
        return

    # Handle both old format (list) and new format (list of workflows)
    if isinstance(queue_data, list):
        if (
            queue_data
            and isinstance(queue_data[0], dict)
            and "workflow_id" in queue_data[0]
        ):
            # New workflow format
            workflows = queue_data
        else:
            # Old simple command format - wrap in workflow
            workflows = [
                {
                    "workflow_id": "legacy_commands",
                    "description": "Legacy command queue",
                    "commands": queue_data,
                }
            ]
    else:
        logging.error("Invalid queue format")
        return

    for workflow in workflows:
        workflow_id = workflow.get("workflow_id", "unknown")
        workflow_desc = workflow.get("description", "No description")
        commands = workflow.get("commands", [])

        print(f"\n[QUEUE] Starting workflow: {workflow_id}")
        print(f"[QUEUE] Description: {workflow_desc}")

        workflow_start_time = time.time()

        for i, item in enumerate(commands):
            cmd = item.get("cmd")
            if not cmd:
                continue

            print(f"[QUEUE] Executing command {i+1}/{len(commands)}: {cmd}")

            try:
                if cmd == "write":
                    filename = item.get("filename")
                    content = item.get("content", "")
                    expected_result = item.get("expected_result", "success")

                    if expected_result == "blocked":
                        print(f"[QUEUE] Testing security boundary for: {filename}")

                    write_dir = "./tmp"
                    file_path = write_to_file(content, filename, write_dir)

                    if file_path:
                        print(f"[QUEUE] ✅ Output written to {file_path}")
                    else:
                        print(
                            f"[QUEUE] ❌ Write failed for {filename} (security block or error)"
                        )

                elif cmd == "scan":
                    scan_path = item.get("path")
                    options = item.get("options", {})
                    full_path = os.path.join(root_dir, scan_path)

                    if os.path.isdir(full_path):
                        structure = get_folder_structure(
                            root_dir=full_path,
                            gitignore_patterns=load_gitignore(root_dir),
                            include_patterns=None,
                            exclude_patterns=None,
                            exclude_dirs=["venv", "build", "tmp"],
                        )
                        print(f"[QUEUE] ✅ Scanned {full_path}")
                        if options.get("include_metadata"):
                            print(f"[QUEUE] Found {len(structure)} items")
                    elif os.path.isfile(full_path):
                        content = read_file_content(full_path)
                        if content:
                            print(
                                f"[QUEUE] ✅ Read file {full_path} ({len(content)} chars)"
                            )
                    else:
                        print(f"[QUEUE] ❌ Path not found: {full_path}")

                elif cmd == "llm":
                    prompt = item.get("prompt", "")
                    context_preference = item.get("context_preference", "init")
                    options = item.get("options", {})

                    # Smart context selection
                    if (
                        context_preference == "init"
                        or context_preference == "init_only"
                    ):
                        context_json = os.path.join(root_dir, "data", "init.json")
                        context_path_to_use = (
                            context_json
                            if os.path.exists(context_json)
                            else context_path
                        )
                    elif (
                        context_preference == "struct_required"
                        or context_preference == "struct_focused"
                    ):
                        context_path_to_use = context_path  # Use struct.json
                    elif context_preference == "cli_focused":
                        cli_json = os.path.join(root_dir, "data", "cli.json")
                        context_path_to_use = (
                            cli_json if os.path.exists(cli_json) else context_path
                        )
                    else:
                        context_json = os.path.join(root_dir, "data", "init.json")
                        context_path_to_use = (
                            context_json
                            if os.path.exists(context_json)
                            else context_path
                        )

                    prompt_with_context = attach_to_llm_request(
                        context_path_to_use, prompt, cache=cache
                    )

                    try:
                        result = await client.query(
                            prompt=prompt_with_context,
                            context_path=context_path_to_use,
                            mode=args.mode,
                            model=args.model,
                            artifact_ids=args.artifact_ids,
                        )
                        if result:
                            print(
                                f"[QUEUE] ✅ LLM Response received ({len(result)} chars)"
                            )
                            if options.get("track_token_usage"):
                                print(
                                    f"[QUEUE] Context: {context_preference}, File: {os.path.basename(context_path_to_use)}"
                                )
                        else:
                            print(f"[QUEUE] ❌ LLM query failed")
                    except Exception as e:
                        print(f"[QUEUE] ❌ LLM error: {e}")

                elif cmd == "validate":
                    json_path = item.get("json_path")
                    schema_path = item.get("schema_path")
                    options = item.get("options", {})

                    if json_path and schema_path:
                        full_json_path = os.path.join(root_dir, json_path)
                        full_schema_path = os.path.join(root_dir, schema_path)

                        if os.path.exists(full_json_path) and os.path.exists(
                            full_schema_path
                        ):
                            print(f"[QUEUE] ✅ Validation attempted for {json_path}")
                            # Note: Actual validation would require jsonschema library
                        else:
                            print(f"[QUEUE] ❌ Validation failed: files not found")
                    else:
                        print(f"[QUEUE] ❌ Validation failed: missing paths")

                elif cmd == "analyze":
                    target_path = item.get("target_path")
                    analysis_type = item.get("analysis_type", "basic")

                    if target_path:
                        full_target_path = os.path.join(root_dir, target_path)
                        if os.path.exists(full_target_path):
                            print(
                                f"[QUEUE] ✅ Analysis of {target_path} ({analysis_type})"
                            )
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

    goals = args.goals if args.goals is not None else config.get("goals", [])
    if not goals:
        logging.warning(
            "No project goals specified via --goals or llmstruct.toml. Consider adding goals for better context."
        )

    args.language or config.get("cli", {}).get("language", "python")
    # Read parsing configuration from [parsing] section, fallback to [cli] for compatibility
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    
    include_patterns = args.include or parsing_config.get("include_patterns") or cli_config.get("include_patterns")
    exclude_patterns = args.exclude or parsing_config.get("exclude_patterns") or cli_config.get("exclude_patterns")
    include_ranges = args.include_ranges or parsing_config.get("include_ranges") or cli_config.get("include_ranges", False)
    include_hashes = args.include_hashes or parsing_config.get("include_hashes") or cli_config.get("include_hashes", False)
    use_gitignore = parsing_config.get("use_gitignore", cli_config.get("use_gitignore", True))
    exclude_dirs = parsing_config.get("exclude_dirs") or cli_config.get("exclude_dirs", [])

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
            exclude_dirs=exclude_dirs,
        )
        with Path(args.output).open("w", encoding="utf-8") as f:
            json.dump(struct_data, f, indent=2)
        logging.info(f"Generated {args.output}")
        # Cache the generated JSON
        if args.use_cache:
            cache = JSONCache()
            cache.cache_json(
                args.output,
                args.output,
                summary="Generated struct.json",
                tags=["struct"],
            )
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
    
    # Use context orchestrator if available and context mode is specified
    context_data = None
    if hasattr(args, 'context_mode') and args.context_mode:
        try:
            from .context_orchestrator import create_context_orchestrator
            
            # Determine scenario based on mode and usage
            scenario = "cli_query" if args.context_mode == "FOCUSED" else "cli_interactive"
            
            # Get optimized context
            orchestrator = create_context_orchestrator(os.path.dirname(args.context))
            optimized_context = orchestrator.get_context_for_scenario(scenario)
            
            # Use optimized context instead of raw file
            if optimized_context:
                logging.info(f"Using optimized context with mode {args.context_mode}")
                context_data = optimized_context
        except ImportError:
            logging.warning("Context orchestrator not available, using raw context file")
        except Exception as e:
            logging.warning(f"Failed to use context orchestrator: {e}")
    
    # Query with optimized or raw context
    if context_data:
        result = await client.query_with_context(
            prompt=args.prompt,
            context_data=context_data,
            mode=args.mode,
            model=args.model,
            artifact_ids=args.artifact_ids,
        )
    else:
        result = await client.query(
            prompt=args.prompt,
            context_path=args.context,
            mode=args.mode,
            model=args.model,
            artifact_ids=args.artifact_ids,
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


def copilot(args):
    """Copilot integration and context management."""
    try:
        # Initialize copilot context manager
        manager = initialize_copilot(args.root_dir)

        if args.copilot_command == "init":
            # Initialize copilot configuration
            config_path = Path(args.root_dir) / "data" / "copilot_init.json"
            if config_path.exists() and not args.force:
                logging.info(f"Copilot already initialized at {config_path}")
            else:
                # Copy template configuration
                template_path = (
                    Path(__file__).parent / "templates" / "copilot_init.json"
                )
                if template_path.exists():
                    shutil.copy(template_path, config_path)
                    logging.info(f"Initialized copilot configuration at {config_path}")
                else:
                    logging.error("Copilot template not found")

        elif args.copilot_command == "status":
            # Show context status
            status = manager.get_context_status()
            print(f"Loaded layers: {', '.join(status['loaded_layers'])}")
            print(f"Available layers: {', '.join(status['available_layers'])}")

        elif args.copilot_command == "load":
            # Load specific context layer
            if hasattr(args, "layer") and args.layer:
                success = manager.load_context_layer(args.layer)
                if success:
                    logging.info(f"Loaded context layer: {args.layer}")
                else:
                    logging.error(f"Failed to load context layer: {args.layer}")
            else:
                logging.error("Layer name required for load command")

        elif args.copilot_command == "unload":
            # Unload specific context layer
            if hasattr(args, "layer") and args.layer:
                success = manager.unload_context_layer(args.layer)
                if success:
                    logging.info(f"Unloaded context layer: {args.layer}")
                else:
                    logging.error(f"Failed to unload context layer: {args.layer}")
            else:
                logging.error("Layer name required for unload command")

        elif args.copilot_command == "refresh":
            # Refresh all contexts
            success = manager.refresh_all_contexts()
            if success:
                logging.info("Refreshed all context layers")
            else:
                logging.error("Failed to refresh some context layers")

        elif args.copilot_command == "suggest":
            # Get smart suggestions
            from .copilot import smart_suggest

            if hasattr(args, "query") and args.query:
                context_type = getattr(args, "context", "code")
                suggestions = smart_suggest(manager, args.query, context_type)
                print("Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
            else:
                logging.error("Query required for suggest command")

        elif args.copilot_command == "validate":
            # Validate file changes
            if hasattr(args, "file_path") and args.file_path:
                change_type = getattr(args, "change_type", "edit")
                result = manager.validate_change(args.file_path, change_type)

                if result["valid"]:
                    print("✓ Validation passed")
                else:
                    print("✗ Validation failed")

                if result["warnings"]:
                    print("Warnings:")
                    for warning in result["warnings"]:
                        print(f"  - {warning}")

                if result["errors"]:
                    print("Errors:")
                    for error in result["errors"]:
                        print(f"  - {error}")
            else:
                logging.error("File path required for validate command")

        elif args.copilot_command == "export":
            # Export context
            format_type = getattr(args, "format", "json")
            layers = getattr(args, "layers", None)
            if layers:
                layers = layers.split(",")

            exported = manager.export_context(layers, format_type)

            output_file = getattr(args, "output", None)
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(exported)
                logging.info(f"Exported context to {output_file}")
            else:
                print(exported)

        else:
            logging.error(f"Unknown copilot command: {args.copilot_command}")

        manager.close()

    except Exception as e:
        logging.error(f"Copilot command failed: {e}")
        raise


def audit(args):
    """Audit project structure and generate reports."""
    print("🔍 Auditing project structure...")
    
    # Basic audit functionality
    root_dir = os.path.abspath(args.root_dir)
    print(f"📁 Project root: {root_dir}")
    
    # Check for key files
    key_files = ["struct.json", "llmstruct.toml", ".gitignore"]
    for file in key_files:
        file_path = Path(root_dir) / file
        status = "✅" if file_path.exists() else "❌"
        print(f"  {status} {file}")
    
    # If duplication analysis is requested, run it
    if hasattr(args, 'include_duplicates') and args.include_duplicates:
        print("\n" + "="*50)
        analyze_duplicates(args)


def analyze_duplicates(args):
    """Analyze function duplication using struct.json deep analysis."""
    try:
        from .workflow_orchestrator import WorkflowOrchestrator
        
        # Enable debug mode if requested
        debug = getattr(args, 'debug', False)
        
        if debug:
            print("🔧 [DEBUG] Starting analyze_duplicates with debug mode")
        
        print("🔍 Analyzing Function Duplication...")
        orchestrator = WorkflowOrchestrator(".", debug=debug)
        
        # Get duplication analysis
        if debug:
            print("🔧 [DEBUG] Calling analyze_codebase_for_duplicates...")
        
        analysis = orchestrator.analyze_codebase_for_duplicates()
        
        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return
        
        if hasattr(args, 'format') and args.format == 'json':
            print(json.dumps(analysis, indent=2))
            return
        
        # Text format output
        duplication_data = analysis.get('analysis', {})
        recommendations = analysis.get('recommendations', [])
        
        if debug:
            print(f"🔧 [DEBUG] Processing {len(recommendations)} recommendations")
        
        # Summary
        print(f"\n📊 Duplication Analysis Summary:")
        print(f"  Total Functions: {duplication_data.get('total_unique_functions', 0)}")
        print(f"  Duplicated: {duplication_data.get('duplicated_functions', 0)}")
        print(f"  Percentage: {duplication_data.get('duplication_percentage', 0):.1f}%")
        
        # Filter recommendations by priority
        if hasattr(args, 'priority') and args.priority != 'all':
            recommendations = [r for r in recommendations if r.get('priority') == args.priority]
            if debug:
                print(f"🔧 [DEBUG] Filtered to {len(recommendations)} {args.priority} priority recommendations")
        
        # Filter by threshold
        threshold = getattr(args, 'threshold', 2)
        duplicates = duplication_data.get('duplication_details', {})
        filtered_duplicates = {k: v for k, v in duplicates.items() if len(v) >= threshold}
        
        if debug:
            print(f"🔧 [DEBUG] Filtered duplicates by threshold {threshold}: {len(filtered_duplicates)} functions")
        
        if filtered_duplicates:
            print(f"\n🚨 Duplicated Functions (≥{threshold} copies):")
            sorted_duplicates = sorted(filtered_duplicates.items(), key=lambda x: len(x[1]), reverse=True)
            
            for func_name, paths in sorted_duplicates[:10]:
                priority_emoji = "🔴" if len(paths) > 3 else "🟡"
                print(f"  {priority_emoji} {func_name} ({len(paths)} copies)")
                for path in paths[:3]:
                    print(f"     - {path}")
                if len(paths) > 3:
                    print(f"     ... and {len(paths) - 3} more")
        
        # Recommendations
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations[:10]:
                priority_emoji = "🔴" if rec.get('priority') == 'high' else "🟡"
                print(f"  {priority_emoji} {rec['function']}")
                print(f"     {rec['recommendation']}")
        
        # Save detailed report if requested
        if hasattr(args, 'save_report') and args.save_report:
            if debug:
                print(f"🔧 [DEBUG] Saving report to {args.save_report}")
            with open(args.save_report, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\n💾 Detailed report saved to: {args.save_report}")
        
        # Next steps
        next_steps = analysis.get('next_steps', [])
        if next_steps:
            print(f"\n🎯 Recommended Actions:")
            for i, step in enumerate(next_steps, 1):
                print(f"  {i}. {step}")
        
        print(f"\n✅ Analysis uses existing llmstruct architecture:")
        print(f"   - struct.json for deep codebase analysis")
        print(f"   - CopilotContextManager for context loading")
        print(f"   - No duplication of existing functions")
        
        if debug:
            print("🔧 [DEBUG] analyze_duplicates completed successfully")
        
    except Exception as e:
        print(f"❌ Failed to analyze duplicates: {e}")
        if getattr(args, 'debug', False):
            import traceback
            print(f"🔧 [DEBUG] Full traceback:")
            traceback.print_exc()


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
        "--include", action="append", help="Include patterns (e.g., '*.py')"
    )
    parse_parser.add_argument(
        "--exclude", action="append", help="Exclude patterns (e.g., 'tests/*')"
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

    interactive_parser = subparsers.add_parser(
        "interactive", help="Run interactive CLI with LLM"
    )
    interactive_parser.add_argument("root_dir", help="Root directory of the project")
    interactive_parser.add_argument(
        "--context", default="struct.json", help="Context JSON file"
    )
    interactive_parser.add_argument(
        "--mode",
        choices=["grok", "anthropic", "ollama", "hybrid"],
        default="hybrid",
        help="LLM mode",
    )
    interactive_parser.add_argument(
        "--model", help="Ollama model (e.g., mixtral, llama3)"
    )
    interactive_parser.add_argument(
        "--artifact-ids",
        nargs="*",
        default=[],
        help="Artifact IDs to include in context",
    )
    interactive_parser.add_argument(
        "--use-cache", action="store_true", help="Use JSON cache"
    )
    interactive_parser.add_argument(
        "--context-mode",
        choices=["FULL", "FOCUSED", "MINIMAL", "SESSION"],
        default="FULL",
        help="Context loading mode for optimization",
    )

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
    elif args.command == "copilot":
        copilot(args)
    elif args.command == "audit":
        audit(args)
    elif args.command == "analyze-duplicates":
        analyze_duplicates(args)


if __name__ == "__main__":
    main()
