import os
import json
import logging
from pathlib import Path
from llmstruct.modules.cli.utils import load_config
from llmstruct.generators.json_generator import generate_json
from llmstruct.cache import JSONCache

def parse_codebase(
    root_dir,
    output=None,
    language=None,
    include=None,
    exclude=None,
    include_dir=None,
    exclude_dir=None,
    include_ranges=False,
    include_hashes=False,
    goals=None,
    use_cache=False,
    modular_index=False
):
    """
    Анализирует кодовую базу и возвращает структуру проекта (dict).
    При необходимости сохраняет struct.json и модульный индекс.
    """
    root_dir = os.path.abspath(root_dir)
    config = load_config(root_dir)
    goals = goals if goals is not None else config.get("goals", [])
    if not goals:
        logging.warning("No project goals specified via --goals or llmstruct.toml. Consider adding goals for better context.")
    language = language or config.get("cli", {}).get("language", "python")
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    include_patterns = (include or parsing_config.get("include_patterns") or cli_config.get("include_patterns"))
    exclude_patterns = (exclude or parsing_config.get("exclude_patterns") or cli_config.get("exclude_patterns"))
    include_ranges = include_ranges or parsing_config.get("include_ranges") or cli_config.get("include_ranges", False)
    include_hashes = include_hashes or parsing_config.get("include_hashes") or cli_config.get("include_hashes", False)
    use_gitignore = parsing_config.get("use_gitignore", cli_config.get("use_gitignore", True))
    exclude_dirs = (exclude_dir or parsing_config.get("exclude_dirs") or cli_config.get("exclude_dirs", []))
    include_dirs = include_dir or []
    gitignore_patterns = load_config(root_dir) if use_gitignore else []
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
    if output:
        with Path(output).open("w", encoding="utf-8") as f:
            json.dump(struct_data, f, indent=2)
        logging.info(f"Generated {output}")
    if use_cache and output:
        cache = JSONCache()
        cache.cache_json(output, output, summary="Generated struct.json", tags=["struct"])
        cache.close()
    if modular_index and "modules" in struct_data:
        index_root = Path(root_dir) / ".llmstruct_index"
        for module in struct_data.get("modules", []):
            mod_path = Path(module["path"])
            mod_dir = index_root / mod_path.parent
            mod_dir.mkdir(parents=True, exist_ok=True)
            struct_path = mod_dir / (mod_path.stem + ".struct.json")
            with struct_path.open("w", encoding="utf-8") as f:
                json.dump(module, f, indent=2, ensure_ascii=False)
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
    return struct_data 