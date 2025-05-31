# cli_main_commands.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""Main CLI command handlers for LLMStruct."""

import argparse
import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from llmstruct import LLMClient
from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import generate_json
from llmstruct.self_run import attach_to_llm_request

# Try to import modular components
try:
    from .cli_core import create_cli_core
    from .copilot import initialize_copilot
    MODULAR_CLI_AVAILABLE = True
except ImportError:
    MODULAR_CLI_AVAILABLE = False


def parse(args: argparse.Namespace):
    """Parse codebase and generate struct.json."""
    logging.info(f"Generating JSON structure from {args.root_dir}")
    cache = JSONCache() if args.use_cache else None

    # Load gitignore patterns
    from .cli import load_gitignore
    gitignore_patterns = load_gitignore(args.root_dir)

    try:
        result = generate_json(
            root_dir=args.root_dir,
            output_file=args.output,
            gitignore_patterns=gitignore_patterns,
            include_patterns=args.include_patterns,
            exclude_patterns=args.exclude_patterns,
            exclude_dirs=args.exclude_dirs,
        )
        
        if result:
            logging.info(f"Successfully generated {args.output}")
        else:
            logging.error(f"Failed to generate {args.output}")
        
        if cache:
            attach_to_llm_request(
                cache,
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


async def interactive(args: argparse.Namespace):
    """Run interactive CLI with modular structure if available, fallback to legacy."""
    if MODULAR_CLI_AVAILABLE:
        await interactive_modular(args)
    else:
        logging.warning("Modular CLI not available, using legacy implementation")
        await interactive_legacy(args)


async def interactive_modular(args: argparse.Namespace):
    """Run interactive CLI with modular structure."""
    try:
        cli_core = create_cli_core(args.root_dir)
        cli_core.run_interactive_mode()
    except Exception as e:
        logging.error(f"Modular CLI failed: {e}")
        await interactive_legacy(args)


async def interactive_legacy(args: argparse.Namespace):
    """Run interactive CLI with LLM, supporting file/folder viewing and writing."""
    print(
        "Interactive LLMStruct CLI. Type 'exit' to quit, '/view <path>' to read files/folders, "
        "'/queue run' to process command queue, '/cache stats' for cache info, "
        "'/auto-update' for struct.json auto-update, '/struct status' for struct info, "
        "'/workflow trigger' for workflow events, or enter /commands to scan/write."
    )
    
    cache = JSONCache() if args.use_cache else None
    client = LLMClient()

    if not Path(args.context).exists():
        logging.error(f"Context file {args.context} does not exist")
        return

    # Use queue enhanced processing if available
    try:
        await process_cli_queue_enhanced(
            args.root_dir, args.context, args, cache, client
        )
    except ImportError:
        # Fall back to basic interactive processing
        await basic_interactive_processing(args, cache, client)

    if cache:
        cache.close()


async def basic_interactive_processing(args: argparse.Namespace, cache: Optional[JSONCache], client: LLMClient):
    """Basic interactive processing without enhanced features."""
    try:
        while True:
            user_input = input("Prompt> ").strip()

            if user_input.lower() == "exit":
                break

            if user_input.startswith("/view"):
                # Basic file viewing
                path = user_input[5:].strip()
                if path:
                    full_path = os.path.join(args.root_dir, path)
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"Content of {full_path}:")
                            print(content)
                        except Exception as e:
                            print(f"Error reading file: {e}")
                    else:
                        print(f"Path not found: {full_path}")
                else:
                    print("Usage: /view <path>")
                continue

            if user_input == "/help":
                print("Available commands:")
                print("  /view <path> - View file contents")
                print("  /help - Show this help")
                print("  exit - Exit the CLI")
                continue

            # Process regular prompts with LLM
            if user_input:
                result = await client.query(
                    prompt=user_input,
                    context_path=args.context,
                    mode=args.mode,
                    model=args.model,
                    artifact_ids=args.artifact_ids,
                )
                
                if result:
                    print("Response:")
                    print(result)
                else:
                    print("Failed to get response from LLM")

    except KeyboardInterrupt:
        print("\nExiting...")


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
        
        # Filter results by priority if specified
        priority_filter = getattr(args, 'priority', 'all').lower()
        threshold = getattr(args, 'threshold', 2)
        
        duplicated_functions = analysis.get('duplicated_functions', [])
        
        if priority_filter != 'all':
            duplicated_functions = [
                f for f in duplicated_functions 
                if f.get('priority', 'medium').lower() == priority_filter
            ]
        
        # Filter by threshold
        duplicated_functions = [
            f for f in duplicated_functions 
            if len(f.get('duplicated_in', [])) >= threshold
        ]
        
        # Output results
        output_format = getattr(args, 'format', 'text').lower()
        
        if output_format == 'json':
            result = {
                'analysis': analysis.get('analysis', {}),
                'filtered_duplicates': duplicated_functions,
                'filter_criteria': {
                    'priority': priority_filter,
                    'threshold': threshold
                }
            }
            print(json.dumps(result, indent=2))
        else:
            # Text format
            total_functions = analysis.get('analysis', {}).get('total_unique_functions', 0)
            print(f"📊 Analysis Results:")
            print(f"   Total unique functions: {total_functions}")
            print(f"   Duplicated functions (filtered): {len(duplicated_functions)}")
            print(f"   Filter: priority={priority_filter}, threshold>={threshold}")
            
            if duplicated_functions:
                print(f"\n🔍 Duplicated Functions:")
                for func in duplicated_functions[:10]:  # Show top 10
                    func_name = func.get('function', 'unknown')
                    locations = func.get('duplicated_in', [])
                    priority = func.get('priority', 'medium')
                    print(f"   • {func_name} [{priority}] - {len(locations)} copies")
                    for loc in locations[:3]:  # Show first 3 locations
                        print(f"     - {loc}")
                    if len(locations) > 3:
                        print(f"     ... and {len(locations) - 3} more")
                
                if len(duplicated_functions) > 10:
                    print(f"   ... and {len(duplicated_functions) - 10} more duplicated functions")
        
        # Save detailed report if requested
        save_report = getattr(args, 'save_report', None)
        if save_report:
            detailed_report = {
                'metadata': {
                    'timestamp': analysis.get('analysis', {}).get('timestamp'),
                    'filter_criteria': {
                        'priority': priority_filter,
                        'threshold': threshold
                    }
                },
                'summary': analysis.get('analysis', {}),
                'duplicated_functions': duplicated_functions,
                'next_steps': analysis.get('next_steps', [])
            }
            
            with open(save_report, 'w', encoding='utf-8') as f:
                json.dump(detailed_report, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Detailed report saved to: {save_report}")
            
    except ImportError as e:
        logging.error(f"WorkflowOrchestrator not available: {e}")
        print("❌ Advanced duplication analysis not available")
        print("   Ensure workflow_orchestrator module is properly installed")
    except Exception as e:
        logging.error(f"Duplication analysis failed: {e}")
        print(f"❌ Analysis failed: {e}")


# Import the enhanced queue processing function
try:
    from .cli import process_cli_queue_enhanced
except ImportError:
    pass
