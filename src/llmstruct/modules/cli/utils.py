import logging
import re
from pathlib import Path
from typing import List, Optional

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
    import toml
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
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True, parents=True)
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

def get_cache_config(config: dict) -> dict:
    return config.get("cache", {})

def get_copilot_config(config: dict) -> dict:
    return config.get("copilot", {})

def get_queue_config(config: dict) -> dict:
    return config.get("queue", {})

def get_context_config(config: dict) -> dict:
    return config.get("context", {})

def get_exclude_dirs(config: dict) -> list:
    default_excludes = [
        "venv", "build", "tmp", ".git", "__pycache__", "node_modules"
    ]
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    config_excludes = parsing_config.get("exclude_dirs") or cli_config.get("exclude_dirs", [])
    return list(set(default_excludes + config_excludes))

def get_include_patterns(config: dict) -> list:
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    return parsing_config.get("include_patterns") or cli_config.get("include_patterns", [])

def get_exclude_patterns(config: dict) -> list:
    parsing_config = config.get("parsing", {})
    cli_config = config.get("cli", {})
    return parsing_config.get("exclude_patterns") or cli_config.get("exclude_patterns", [])

def get_max_file_size(config: dict) -> int:
    return config.get("max_file_size", 1024 * 1024)

def get_struct_file_path(config: dict) -> str:
    return config.get("struct_file", "struct.json")

def get_context_file_path(config: dict) -> str:
    return config.get("context_file", "data/init.json")

def save_config(config: dict, root_dir: str) -> None:
    import toml
    config_path = Path(root_dir) / "llmstruct.toml"
    try:
        with config_path.open("w", encoding="utf-8") as f:
            toml.dump(config, f)
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}") 