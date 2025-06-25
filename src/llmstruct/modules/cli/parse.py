import os
import json
import logging
from pathlib import Path
from llmstruct.modules.cli.utils import load_config
from llmstruct.generators.json_generator import generate_json
from llmstruct.generators.index_generator import save_index_json
from llmstruct.cache import JSONCache
from llmstruct.core.config_manager import get_config_manager, ConfigManager

def parse(args):
    """Parse codebase and generate struct.json."""
    root_dir = os.path.abspath(args.root_dir)
    config = load_config(root_dir)
    
    # Initialize configuration manager with CLI overrides
    config_manager = get_config_manager()
    
    # Load configuration file if specified
    if hasattr(args, 'config') and args.config:
        llm_config = config_manager.load_config(args.config)
    else:
        llm_config = config_manager.get_config()
    
    # Apply CLI overrides
    if hasattr(args, 'enable_llm') and args.enable_llm:
        llm_config.enable_llm = True
        llm_config.llm.enabled = True
        
    if hasattr(args, 'offline') and args.offline:
        llm_config.security.offline_mode = True
        llm_config.security.allow_network_calls = False
        llm_config.enable_llm = False
        llm_config.llm.enabled = False
        
    if hasattr(args, 'summary_provider') and args.summary_provider:
        llm_config.summary.provider = args.summary_provider
        
    # Log configuration status
    if llm_config.enable_llm:
        logging.info("LLM features ENABLED - AI-powered summaries and analysis available")
    else:
        logging.info("LLM features DISABLED - Using heuristic analysis only (default for security)")
        
    if llm_config.security.offline_mode:
        logging.info("OFFLINE MODE - No network calls will be made")

    goals = args.goals if args.goals is not None else config.get("goals", [])
    if not goals:
        logging.warning(
            "No project goals specified via --goals or llmstruct.toml. Consider adding goals for better context."
        )

    args.language or config.get("cli", {}).get("language", "python")
    # Read parsing configuration from [parsing] section, fallback to [cli] for compatibility
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    
    include_patterns = (args.include or parsing_config.get("include_patterns") or cli_config.get("include_patterns"))
    exclude_patterns = (args.exclude or parsing_config.get("exclude_patterns") or cli_config.get("exclude_patterns"))
    include_ranges = args.include_ranges or parsing_config.get("include_ranges") or cli_config.get("include_ranges", True)
    include_hashes = args.include_hashes or parsing_config.get("include_hashes") or cli_config.get("include_hashes", False)
    use_gitignore = parsing_config.get("use_gitignore", cli_config.get("use_gitignore", True))
    exclude_dirs = (args.exclude_dir or parsing_config.get("exclude_dirs") or cli_config.get("exclude_dirs", []))
    include_dirs = args.include_dir or []

    gitignore_patterns = load_config(root_dir) if use_gitignore else []

    # Комментарий: include_dirs пока не используется в генераторе, но можно добавить фильтрацию по ним при необходимости

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
            include_dirs=include_dirs,
        )
        with Path(args.output).open("w", encoding="utf-8") as f:
            json.dump(struct_data, f, indent=2)
        logging.info(f"Generated {args.output}")
        
        # NEW: Generate index.json for Phase 1 completion
        if include_hashes:
            index_file = args.output.replace(".json", "_index.json") if args.output != "struct.json" else "index.json"
            save_index_json(struct_data, index_file)
            logging.info(f"Generated index file: {index_file}")
            
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
        # --- Модульный индекс ---
        if getattr(args, 'modular_index', False):
            index_root = Path(root_dir) / ".llmstruct_index"
            for module in struct_data.get("modules", []):
                mod_path = Path(module["path"])
                mod_dir = index_root / mod_path.parent
                mod_dir.mkdir(parents=True, exist_ok=True)
                # Сохраняем struct.json для модуля
                struct_path = mod_dir / (mod_path.stem + ".struct.json")
                with struct_path.open("w", encoding="utf-8") as f:
                    json.dump(module, f, indent=2, ensure_ascii=False)
                # Сохраняем ast.json (только AST-хеши и исходники функций)
                ast_data = {
                    "module": module["path"],
                    "functions": [
                        {
                            "name": func["name"],
                            "ast_hash": func.get("ast_hash"),
                            "source": func.get("source"),
                            "start_line": func.get("start_line"),
                            "end_line": func.get("end_line"),
                        }
                        for func in module.get("functions", [])
                    ],
                }
                ast_path = mod_dir / (mod_path.stem + ".ast.json")
                with ast_path.open("w", encoding="utf-8") as f:
                    json.dump(ast_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Модульный индекс сохранён в {index_root}")
    except Exception as e:
        logging.error(f"Failed to generate JSON: {e}")
        raise 