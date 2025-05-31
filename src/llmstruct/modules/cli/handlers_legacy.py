import os
import logging
import json
import re
import time
from pathlib import Path
from llmstruct import LLMClient
from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import get_folder_structure
from llmstruct.self_run import attach_to_llm_request
from llmstruct.modules.cli.utils import load_gitignore, read_file_content, write_to_file

# LEGACY: Архивная реализация интерактивного CLI (используется только как fallback)
async def interactive_legacy(args):
    """Run interactive CLI with LLM, supporting file/folder viewing and writing."""
    client = LLMClient()
    cache = JSONCache() if args.use_cache else None
    root_dir = os.path.abspath(args.root_dir)
    context_path = args.context
    if not Path(context_path).exists():
        logging.warning(
            f"Context file {context_path} does not exist, generating new struct.json"
        )
        from llmstruct.cli import parse
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
            # ... остальные команды (queue, cache, auto-update, struct, workflow) реализуются аналогично ...
        else:
            prompt = user_input
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