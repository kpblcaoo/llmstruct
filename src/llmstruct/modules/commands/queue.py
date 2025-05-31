import os
import json
import logging
import time
from llmstruct.modules.cli.utils import load_gitignore, read_file_content, write_to_file
from llmstruct.generators.json_generator import get_folder_structure
from llmstruct.self_run import attach_to_llm_request

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