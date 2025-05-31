import os
import json
import logging
from pathlib import Path
from llmstruct.modules.cli.utils import load_config
from llmstruct.generators.json_generator import generate_json
from llmstruct.cache import JSONCache

def parse(args):
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

    gitignore_patterns = load_config(root_dir) if use_gitignore else []

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