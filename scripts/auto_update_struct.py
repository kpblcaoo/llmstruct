#!/usr/bin/env python3
"""
Automatic struct.json update script
This script automatically parses the project and updates struct.json
without requiring LLM intervention.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from llmstruct.cli import load_config, load_gitignore
    from llmstruct.generators.json_generator import generate_json
except ImportError:
    # Fallback for when module is not installed
    def load_config():
        return {}
    def load_gitignore():
        return lambda x: False
    def generate_json(*args, **kwargs):
        raise ImportError("llmstruct module not available")
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def detect_project_changes(root_dir: str, struct_path: str) -> bool:
    """
    Detect if project files have changed since last struct.json generation.
    Uses git status to check for modifications.
    """
    try:
        # Check if struct.json exists
        if not Path(struct_path).exists():
            logger.info("struct.json not found, will generate")
            return True

        # Get last modification time of struct.json
        struct_mtime = Path(struct_path).stat().st_mtime

        # Check if any Python files were modified after struct.json
        for pattern in ['**/*.py', '**/*.js', '**/*.ts']:
            for file_path in Path(root_dir).glob(pattern):
                if file_path.stat().st_mtime > struct_mtime:
                    logger.info(f"File {file_path} is newer than struct.json")
                    return True

        # Check git status for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=root_dir,
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            logger.info("Git working directory has changes")
            return True

        return False

    except Exception as e:
        logger.warning(f"Error detecting changes: {e}")
        return True  # Conservative approach - regenerate if unsure


def backup_struct_json(struct_path: str) -> Optional[str]:
    """
    Create a backup of existing struct.json.
    """
    try:
        if Path(struct_path).exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{struct_path}.bak.{timestamp}"
            subprocess.run(['cp', struct_path, backup_path], check=True)
            logger.info(f"Backed up struct.json to {backup_path}")
            return backup_path
    except Exception as e:
        logger.error(f"Failed to backup struct.json: {e}")
    return None


def validate_struct_json(struct_path: str) -> bool:
    """
    Validate generated struct.json for basic structure.
    """
    try:
        with open(struct_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required_fields = ['metadata', 'toc', 'modules']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False

        # Check metadata structure
        metadata = data['metadata']
        required_metadata = ['project_name', 'version', 'stats']
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Missing metadata field: {field}")
                return False

        logger.info("struct.json validation passed")
        return True

    except Exception as e:
        logger.error(f"struct.json validation failed: {e}")
        return False


def update_struct_json(
    root_dir: str = None,
    struct_path: str = None,
    force: bool = False,
    config_override: Dict[str, Any] = None
) -> bool:
    """
    Main function to update struct.json automatically.

    Args:
        root_dir: Project root directory (default: current directory)
        struct_path: Path to struct.json (default: ./struct.json)
        force: Force regeneration even if no changes detected
        config_override: Override default configuration

    Returns:
        bool: True if update was successful
    """
    # Set defaults
    root_dir = root_dir or os.getcwd()
    struct_path = struct_path or os.path.join(root_dir, 'struct.json')

    logger.info(f"Checking for updates in {root_dir}")

    # Check if update is needed
    if not force and not detect_project_changes(root_dir, struct_path):
        logger.info("No changes detected, struct.json is up to date")
        return True

    # Backup existing struct.json
    backup_path = backup_struct_json(struct_path)

    try:
        # Load configuration
        config = load_config(root_dir)
        if config_override:
            config.update(config_override)

        # Extract configuration parameters
        cli_config = config.get('cli', {})
        goals = config.get('goals', [])
        include_patterns = cli_config.get('include_patterns')
        exclude_patterns = cli_config.get('exclude_patterns')
        include_ranges = cli_config.get('include_ranges', False)
        include_hashes = cli_config.get('include_hashes', False)
        use_gitignore = cli_config.get('use_gitignore', True)
        exclude_dirs = cli_config.get('exclude_dirs', [])

        # Load gitignore patterns
        gitignore_patterns = load_gitignore(root_dir) if use_gitignore else []

        logger.info("Generating new struct.json")

        # Generate struct.json
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

        # Write to file
        with open(struct_path, 'w', encoding='utf-8') as f:
            json.dump(struct_data, f, indent=2)

        # Validate the generated file
        if not validate_struct_json(struct_path):
            if backup_path:
                logger.error("Restoring from backup due to validation failure")
                subprocess.run(['cp', backup_path, struct_path], check=True)
            return False

        logger.info(f"Successfully updated {struct_path}")

        # Print summary
        stats = struct_data['metadata']['stats']
        logger.info(f"Summary: {stats['modules_count']} modules, "
                    f"{stats['functions_count']} functions, "
                    f"{stats['classes_count']} classes")

        return True

    except Exception as e:
        logger.error(f"Failed to update struct.json: {e}")

        # Restore from backup if available
        if backup_path:
            logger.info("Restoring from backup")
            subprocess.run(['cp', backup_path, struct_path], check=True)

        return False


def main():
    """
    Command-line interface for auto-update script.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically update struct.json"
    )
    parser.add_argument(
        '--root-dir',
        default=os.getcwd(),
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='struct.json',
        help='Output file path (default: struct.json)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration even if no changes detected'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check if update is needed, do not update'
    )

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Convert relative path to absolute
    struct_path = os.path.abspath(args.output)

    if args.check_only:
        needs_update = detect_project_changes(args.root_dir, struct_path)
        if needs_update:
            print("UPDATE_NEEDED")
            sys.exit(1)
        else:
            print("UP_TO_DATE")
            sys.exit(0)

    success = update_struct_json(
        root_dir=args.root_dir,
        struct_path=struct_path,
        force=args.force
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
