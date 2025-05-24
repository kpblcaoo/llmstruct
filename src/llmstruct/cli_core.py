# cli_core.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""Core CLI functionality and main loop."""

import logging
from pathlib import Path
from typing import Optional

from llmstruct.cache import JSONCache
from .cli_commands import CommandProcessor
from .cli_config import CLIConfig
from .cli_utils import CLIUtils
from .copilot import CopilotContextManager, initialize_copilot

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CLICore:
    """Core CLI class handling main loop and coordination."""

    def __init__(self, root_dir: str):
        """Initialize CLI core with root directory."""
        self.root_dir = root_dir
        self.config = CLIConfig(root_dir)
        self.utils = CLIUtils(root_dir)
        self.command_processor = CommandProcessor(root_dir, self.config, self.utils)
        self.cache: Optional[JSONCache] = None
        self.copilot_manager: Optional[CopilotContextManager] = None

    def setup_cache(self) -> None:
        """Initialize cache if enabled in config."""
        cache_config = self.config.get_cache_config()
        if cache_config.get("enabled", True):
            try:
                cache_dir = cache_config.get("directory", ".llmstruct_cache")
                cache_path = Path(self.root_dir) / cache_dir
                cache_path.mkdir(exist_ok=True)

                self.cache = JSONCache(
                    cache_dir=str(cache_path),
                    max_size=cache_config.get("max_size", 100),
                    ttl=cache_config.get("ttl", 3600),
                )
                logging.info(f"Cache initialized at {cache_path}")
            except Exception as e:
                logging.warning(f"Failed to initialize cache: {e}")

    def setup_copilot(self) -> None:
        """Initialize Copilot integration if enabled."""
        copilot_config = self.config.get_copilot_config()
        if copilot_config.get("enabled", False):
            try:
                self.copilot_manager = initialize_copilot(self.root_dir, copilot_config)
                logging.info("Copilot integration initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize Copilot: {e}")

    def run_interactive_mode(self) -> None:
        """Run the interactive CLI mode."""
        # Setup components
        self.setup_cache()
        self.setup_copilot()

        # Pass cache and copilot to command processor
        self.command_processor.set_cache(self.cache)
        self.command_processor.set_copilot(self.copilot_manager)

        print(
            "Interactive LLMStruct CLI. Type 'exit' to quit, '/help' for available commands."
        )

        try:
            while True:
                user_input = input("Prompt> ").strip()

                if user_input.lower() == "exit":
                    break

                # Process commands (starting with /) or regular prompts
                if user_input.startswith("/"):
                    self.command_processor.process_command(user_input[1:])
                else:
                    self.command_processor.process_prompt(user_input)

        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            logging.error(f"Unexpected error in interactive mode: {e}")
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.cache:
            self.cache.close()
            logging.info("Cache closed")

        if self.copilot_manager:
            # Add any copilot cleanup if needed
            logging.info("Copilot manager cleanup completed")


def create_cli_core(root_dir: str) -> CLICore:
    """Factory function to create CLI core instance."""
    return CLICore(root_dir)
