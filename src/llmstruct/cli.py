import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import toml

from .generators.json_generator import generate_json

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

def main():
    """Command-line interface for LLMstruct."""
    parser = argparse.ArgumentParser(description="Generate structured JSON for codebases")
    parser.add_argument('root_dir', help="Root directory of the project")
    parser.add_argument('-o', '--output', default='struct.json', help="Output JSON file")
    parser.add_argument('--language', choices=['python', 'javascript'], help="Programming language")
    parser.add_argument('--include', action='append', help="Include patterns (e.g., '*.py')")
    parser.add_argument('--exclude', action='append', help="Exclude patterns (e.g., 'tests/*')")
    parser.add_argument('--include-ranges', action='store_true', help="Include line ranges for functions/classes")
    parser.add_argument('--include-hashes', action='store_true', help="Include file hashes")
    parser.add_argument('--goals', nargs='*', help="Custom project goals")
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    config = load_config(root_dir)
    
    # CLI args override config
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
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(struct_data, f, indent=2)
        logging.info(f"Generated {args.output}")
    except Exception as e:
        logging.error(f"Failed to generate JSON: {e}")
        raise

if __name__ == "__main__":
    main()