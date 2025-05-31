import logging
import shutil
from pathlib import Path

def copilot(args):
    """Copilot integration and context management."""
    try:
        from llmstruct.copilot import initialize_copilot
        manager = initialize_copilot(args.root_dir)

        if args.copilot_command == "init":
            config_path = Path(args.root_dir) / "data" / "copilot_init.json"
            if config_path.exists() and not args.force:
                logging.info(f"Copilot already initialized at {config_path}")
            else:
                template_path = (
                    Path(__file__).parent.parent.parent / "templates" / "copilot_init.json"
                )
                if template_path.exists():
                    shutil.copy(template_path, config_path)
                    logging.info(f"Initialized copilot configuration at {config_path}")
                else:
                    logging.error("Copilot template not found")

        elif args.copilot_command == "status":
            status = manager.get_context_status()
            print(f"Loaded layers: {', '.join(status['loaded_layers'])}")
            print(f"Available layers: {', '.join(status['available_layers'])}")

        elif args.copilot_command == "load":
            if hasattr(args, "layer") and args.layer:
                success = manager.load_context_layer(args.layer)
                if success:
                    logging.info(f"Loaded context layer: {args.layer}")
                else:
                    logging.error(f"Failed to load context layer: {args.layer}")
            else:
                logging.error("Layer name required for load command")

        elif args.copilot_command == "unload":
            if hasattr(args, "layer") and args.layer:
                success = manager.unload_context_layer(args.layer)
                if success:
                    logging.info(f"Unloaded context layer: {args.layer}")
                else:
                    logging.error(f"Failed to unload context layer: {args.layer}")
            else:
                logging.error("Layer name required for unload command")

        elif args.copilot_command == "refresh":
            success = manager.refresh_all_contexts()
            if success:
                logging.info("Refreshed all context layers")
            else:
                logging.error("Failed to refresh some context layers")

        elif args.copilot_command == "suggest":
            from llmstruct.copilot import smart_suggest
            if hasattr(args, "query") and args.query:
                context_type = getattr(args, "context", "code")
                suggestions = smart_suggest(manager, args.query, context_type)
                print("Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
            else:
                logging.error("Query required for suggest command")

        elif args.copilot_command == "validate":
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