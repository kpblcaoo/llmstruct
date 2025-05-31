# cli_config.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""CLI configuration management."""

import logging
from pathlib import Path
from typing import Dict, Any, List

import toml


class CLIConfig:
    """Manages CLI configuration from llmstruct.toml and other sources."""

    def __init__(self, root_dir: str):
        """Initialize configuration manager."""
        self.root_dir = root_dir
        self.config_path = Path(root_dir) / "llmstruct.toml"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from llmstruct.toml."""
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    return toml.load(f)
            except Exception as e:
                logging.error(f"Failed to read llmstruct.toml: {e}")
        return {}

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration section."""
        return self._config.get("cache", {})

    def get_copilot_config(self) -> Dict[str, Any]:
        """Get Copilot configuration section."""
        return self._config.get("copilot", {})

    def get_queue_config(self) -> Dict[str, Any]:
        """Get queue configuration section."""
        return self._config.get("queue", {})

    def get_context_config(self) -> Dict[str, Any]:
        """Get context configuration section."""
        return self._config.get("context", {})

    def get_gitignore_patterns(self) -> List[str]:
        """Load and normalize patterns from .gitignore."""
        gitignore_path = Path(self.root_dir) / ".gitignore"
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

    def get_exclude_dirs(self) -> List[str]:
        """Get directories to exclude from scanning."""
        default_excludes = [
            "venv",
            "build",
            "tmp",
            ".git",
            "__pycache__",
            "node_modules",
        ]
        # Check [parsing] section first, then [cli] for compatibility
        parsing_config = self._config.get("parsing", {})
        cli_config = self._config.get("cli", {})
        config_excludes = parsing_config.get("exclude_dirs") or cli_config.get("exclude_dirs", [])
        return list(set(default_excludes + config_excludes))

    def get_include_patterns(self) -> List[str]:
        """Get file patterns to include."""
        # Check [parsing] section first, then [cli] for compatibility
        parsing_config = self._config.get("parsing", {})
        cli_config = self._config.get("cli", {})
        return parsing_config.get("include_patterns") or cli_config.get("include_patterns", [])

    def get_exclude_patterns(self) -> List[str]:
        """Get file patterns to exclude."""
        # Check [parsing] section first, then [cli] for compatibility
        parsing_config = self._config.get("parsing", {})
        cli_config = self._config.get("cli", {})
        return parsing_config.get("exclude_patterns") or cli_config.get("exclude_patterns", [])

    def get_max_file_size(self) -> int:
        """Get maximum file size for processing (in bytes)."""
        return self._config.get("max_file_size", 1024 * 1024)  # 1MB default

    def get_auto_update_config(self) -> Dict[str, Any]:
        """Get auto-update configuration."""
        return self._config.get("auto_update", {})

    def is_auto_update_enabled(self) -> bool:
        """Check if auto-update is enabled."""
        return self.get_auto_update_config().get("enabled", True)

    def get_struct_file_path(self) -> str:
        """Get path to struct.json file."""
        return self._config.get("struct_file", "struct.json")

    def get_context_file_path(self) -> str:
        """Get path to context file."""
        return self._config.get("context_file", "data/init.json")

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with self.config_path.open("w", encoding="utf-8") as f:
                toml.dump(self._config, f)
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")

    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update configuration value."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self.save_config()

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()
