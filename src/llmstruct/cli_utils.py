# cli_utils.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""CLI utility functions."""

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from llmstruct.generators.json_generator import get_folder_structure


class CLIUtils:
    """Utility functions for CLI operations."""

    def __init__(self, root_dir: str):
        """Initialize utils with root directory."""
        self.root_dir = root_dir

    def read_file_content(
        self, file_path: str, max_size: int = 1024 * 1024
    ) -> Optional[str]:
        """Read file content with size limit."""
        full_path = (
            os.path.join(self.root_dir, file_path)
            if not os.path.isabs(file_path)
            else file_path
        )

        try:
            file_stat = os.stat(full_path)
            if file_stat.st_size > max_size:
                logging.warning(
                    f"File {full_path} is too large ({file_stat.st_size} bytes), skipping"
                )
                return None

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading file {full_path}: {e}")
            return None

    def write_file_content(self, file_path: str, content: str) -> bool:
        """Write content to file."""
        full_path = (
            os.path.join(self.root_dir, file_path)
            if not os.path.isabs(file_path)
            else file_path
        )

        try:
            # Create directory if it doesn't exist
            Path(full_path).parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"File {full_path} written successfully")
            return True
        except Exception as e:
            logging.error(f"Error writing file {full_path}: {e}")
            return False

    def get_directory_structure(
        self,
        path: str,
        gitignore_patterns: List[str],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get directory structure using folder generator."""
        full_path = (
            os.path.join(self.root_dir, path) if not os.path.isabs(path) else path
        )

        if not os.path.isdir(full_path):
            return []

        try:
            structure = get_folder_structure(
                root_dir=full_path,
                gitignore_patterns=gitignore_patterns,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                exclude_dirs=exclude_dirs or ["venv", "build", "tmp"],
            )

            if not structure:
                # Fallback to simple directory listing
                items = os.listdir(full_path)
                structure = [
                    {
                        "path": os.path.join(path, item),
                        "type": (
                            "directory"
                            if os.path.isdir(os.path.join(full_path, item))
                            else "file"
                        ),
                    }
                    for item in sorted(items)
                ]

            return structure
        except Exception as e:
            logging.error(f"Error reading directory {full_path}: {e}")
            return []

    def validate_json(self, content: str) -> tuple[bool, Optional[str]]:
        """Validate JSON content."""
        try:
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)

    def format_json(self, data: Any, indent: int = 2) -> str:
        """Format data as JSON string."""
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error formatting JSON: {e}")
            return str(data)

    def generate_unique_id(self, prefix: str = "cmd") -> str:
        """Generate unique ID for commands, queues, etc."""
        timestamp = int(time.time() * 1000)
        unique_part = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_part}"

    def safe_path_join(self, *parts: str) -> str:
        """Safely join path parts, preventing directory traversal."""
        path = os.path.join(*parts)
        # Resolve and check if path is within root_dir
        resolved_path = os.path.abspath(path)
        root_abs = os.path.abspath(self.root_dir)

        if not resolved_path.startswith(root_abs):
            raise ValueError(f"Path {path} is outside root directory {self.root_dir}")

        return resolved_path

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        try:
            full_path = self.safe_path_join(self.root_dir, file_path)
            return os.path.isfile(full_path)
        except (ValueError, OSError):
            return False

    def dir_exists(self, dir_path: str) -> bool:
        """Check if directory exists."""
        try:
            full_path = self.safe_path_join(self.root_dir, dir_path)
            return os.path.isdir(full_path)
        except (ValueError, OSError):
            return False

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            full_path = self.safe_path_join(self.root_dir, file_path)
            return os.path.getsize(full_path)
        except (ValueError, OSError):
            return 0

    def backup_file(self, file_path: str) -> Optional[str]:
        """Create backup of file with timestamp."""
        try:
            full_path = self.safe_path_join(self.root_dir, file_path)
            if not os.path.isfile(full_path):
                return None

            timestamp = int(time.time())
            backup_path = f"{full_path}.backup.{timestamp}"

            with open(full_path, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())

            return backup_path
        except Exception as e:
            logging.error(f"Error creating backup for {file_path}: {e}")
            return None

    def cleanup_old_backups(self, file_path: str, keep_count: int = 5) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            full_path = self.safe_path_join(self.root_dir, file_path)
            backup_pattern = f"{full_path}.backup."

            # Find all backup files
            directory = os.path.dirname(full_path)
            backups = []

            for filename in os.listdir(directory):
                if filename.startswith(os.path.basename(backup_pattern)):
                    backup_file = os.path.join(directory, filename)
                    try:
                        timestamp = int(filename.split(".")[-1])
                        backups.append((timestamp, backup_file))
                    except ValueError:
                        continue

            # Sort by timestamp and remove old ones
            backups.sort(reverse=True)  # Most recent first
            for _, backup_file in backups[keep_count:]:
                try:
                    os.remove(backup_file)
                    logging.info(f"Removed old backup: {backup_file}")
                except OSError as e:
                    logging.warning(f"Failed to remove backup {backup_file}: {e}")

        except Exception as e:
            logging.error(f"Error cleaning up backups for {file_path}: {e}")
