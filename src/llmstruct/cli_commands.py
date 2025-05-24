# cli_commands.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""CLI command processing and handlers."""

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from llmstruct import LLMClient
from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import generate_json
from llmstruct.self_run import attach_to_llm_request
from llmstruct.copilot import initialize_copilot, trigger_copilot_event
from .cli_config import CLIConfig
from .cli_utils import CLIUtils
from .copilot import CopilotContextManager, CopilotEvent


class CommandProcessor:
    """Processes CLI commands and user prompts."""
    
    def __init__(self, root_dir: str, config: CLIConfig, utils: CLIUtils):
        """Initialize command processor."""
        self.root_dir = root_dir
        self.config = config
        self.utils = utils
        self.cache: Optional[JSONCache] = None
        self.copilot_manager: Optional[CopilotContextManager] = None
        
        # Initialize command handlers
        self.commands = {
            'help': self.cmd_help,
            'view': self.cmd_view,
            'write': self.cmd_write,
            'generate': self.cmd_write,
            'create': self.cmd_write,
            'queue': self.cmd_queue,
            'cache': self.cmd_cache,
            'copilot': self.cmd_copilot,
            'config': self.cmd_config,
            'status': self.cmd_status,
            'backup': self.cmd_backup,
            'parse': self.cmd_parse,
            'auto-update': self.handle_auto_update,
            'struct-status': self.handle_struct_status,
        }
    
    def set_cache(self, cache: Optional[JSONCache]) -> None:
        """Set cache instance."""
        self.cache = cache
    
    def set_copilot(self, copilot_manager: Optional[CopilotContextManager]) -> None:
        """Set Copilot manager instance."""
        self.copilot_manager = copilot_manager
    
    def process_command(self, command_line: str) -> None:
        """Process a command starting with /."""
        if not command_line.strip():
            return
        
        parts = command_line.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                logging.error(f"Error executing command '{cmd}': {e}")
                print(f"Error executing command '{cmd}': {e}")
        else:
            print(f"Unknown command: {cmd}. Type '/help' for available commands.")
    
    def process_prompt(self, prompt: str) -> None:
        """Process a regular user prompt (not a command)."""
        if not prompt.strip():
            return
        
        try:
            # Emit Copilot event if manager is available
            if self.copilot_manager:
                event = CopilotEvent(
                    event_type="prompt_received",
                    data={"prompt": prompt},
                    source="cli"
                )
                self.copilot_manager.emit_event(event)
            
            # For now, just acknowledge the prompt
            # TODO: Integrate with LLM processing
            print(f"Received prompt: {prompt}")
            print("Note: LLM processing integration is pending.")
            
        except Exception as e:
            logging.error(f"Error processing prompt: {e}")
            print(f"Error processing prompt: {e}")
    
    def cmd_help(self, args: str) -> None:
        """Show help information."""
        help_text = """
Available commands:
  /help                 - Show this help message
  /view <path>         - View file or directory contents
  /write <file> <content> - Write content to file
  /generate <file> <content> - Same as write
  /create <file> <content>   - Same as write
  /queue <action>      - Queue operations (run, status, clear, list)
  /cache <action>      - Cache operations (stats, clear, info)
  /copilot <action>    - Copilot operations (status, config, test)
  /config <section>    - View or modify configuration
  /status              - Show system status
  /backup <file>       - Create backup of file
  /parse               - Parse project structure
  /auto-update         - Trigger auto-update of struct.json
  /struct-status       - Show struct.json status and last update info
  
Examples:
  /view src/           - Show directory structure
  /view README.md      - Show file content
  /write test.txt "Hello World" - Write to file
  /queue run           - Process command queue
  /cache stats         - Show cache statistics
  /copilot status      - Show Copilot status
  /auto-update         - Trigger struct.json update
  /struct-status       - Show struct.json status
"""
        print(help_text)
    
    def cmd_view(self, args: str) -> None:
        """View file or directory contents."""
        path = args.strip()
        if not path:
            print("Usage: /view <path>")
            return
        
        full_path = os.path.join(self.root_dir, path)
        
        if os.path.isdir(full_path):
            gitignore_patterns = self.config.get_gitignore_patterns()
            structure = self.utils.get_directory_structure(
                path,
                gitignore_patterns,
                self.config.get_include_patterns(),
                self.config.get_exclude_patterns(),
                self.config.get_exclude_dirs()
            )
            
            if structure:
                print(f"Directory structure for {full_path}:")
                print(self.utils.format_json(structure))
            else:
                print(f"No accessible items found in {full_path}")
                
        elif os.path.isfile(full_path):
            content = self.utils.read_file_content(path, self.config.get_max_file_size())
            if content is not None:
                print(f"Content of {full_path}:")
                print(content)
            else:
                print(f"Cannot read file {full_path} (too large or inaccessible)")
        else:
            print(f"Path {full_path} does not exist")
    
    def cmd_write(self, args: str) -> None:
        """Write content to file."""
        # Parse: filename content
        match = re.match(r'(\S+)\s+(.*)', args, re.DOTALL)
        if not match:
            print("Usage: /write <filename> <content>")
            return
        
        filename, content = match.groups()
        
        # Remove quotes if present
        content = content.strip()
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
        
        # Create backup if file exists
        if self.utils.file_exists(filename):
            backup_path = self.utils.backup_file(filename)
            if backup_path:
                print(f"Backup created: {backup_path}")
        
        if self.utils.write_file_content(filename, content):
            print(f"Successfully wrote to {filename}")
            
            # Auto-update struct.json if enabled
            if self.config.is_auto_update_enabled():
                self._trigger_auto_update()
        else:
            print(f"Failed to write to {filename}")
    
    def cmd_queue(self, args: str) -> None:
        """Handle queue operations."""
        if not args:
            print("Usage: /queue <run|status|clear|list>")
            return
        
        action = args.strip().lower()
        
        if action == 'run':
            self._process_queue()
        elif action == 'status':
            self._show_queue_status()
        elif action == 'clear':
            self._clear_queue()
        elif action == 'list':
            self._list_queue()
        else:
            print(f"Unknown queue action: {action}")
    
    def cmd_cache(self, args: str) -> None:
        """Handle cache operations."""
        if not self.cache:
            print("Cache is not initialized")
            return
        
        if not args:
            print("Usage: /cache <stats|clear|info>")
            return
        
        action = args.strip().lower()
        
        if action == 'stats':
            stats = self.cache.get_stats()
            print("Cache Statistics:")
            print(self.utils.format_json(stats))
        elif action == 'clear':
            self.cache.clear()
            print("Cache cleared")
        elif action == 'info':
            info = {
                'cache_dir': self.cache.cache_dir,
                'max_size': self.cache.max_size,
                'ttl': self.cache.ttl,
                'current_size': len(self.cache._cache)
            }
            print("Cache Information:")
            print(self.utils.format_json(info))
        else:
            print(f"Unknown cache action: {action}")
    
    def cmd_copilot(self, args: str) -> None:
        """Handle Copilot operations."""
        if not args:
            print("Usage: /copilot <status|config|test>")
            return
        
        action = args.strip().lower()
        
        if action == 'status':
            if self.copilot_manager:
                status = self.copilot_manager.get_status()
                print("Copilot Status:")
                print(self.utils.format_json(status))
            else:
                print("Copilot is not initialized")
        elif action == 'config':
            config = self.config.get_copilot_config()
            print("Copilot Configuration:")
            print(self.utils.format_json(config))
        elif action == 'test':
            if self.copilot_manager:
                test_event = CopilotEvent(
                    event_type="test_event",
                    data={"message": "Test from CLI"},
                    source="cli_test"
                )
                self.copilot_manager.emit_event(test_event)
                print("Test event sent to Copilot manager")
            else:
                print("Copilot is not initialized")
        else:
            print(f"Unknown copilot action: {action}")
    
    def cmd_config(self, args: str) -> None:
        """View or modify configuration."""
        if not args:
            # Show all configuration
            config_data = {
                'cache': self.config.get_cache_config(),
                'copilot': self.config.get_copilot_config(),
                'queue': self.config.get_queue_config(),
                'context': self.config.get_context_config(),
                'auto_update': self.config.get_auto_update_config()
            }
            print("Current Configuration:")
            print(self.utils.format_json(config_data))
        else:
            section = args.strip().lower()
            if section == 'cache':
                config = self.config.get_cache_config()
            elif section == 'copilot':
                config = self.config.get_copilot_config()
            elif section == 'queue':
                config = self.config.get_queue_config()
            elif section == 'context':
                config = self.config.get_context_config()
            elif section == 'auto_update':
                config = self.config.get_auto_update_config()
            else:
                print(f"Unknown config section: {section}")
                return
            
            print(f"{section.title()} Configuration:")
            print(self.utils.format_json(config))
    
    def cmd_status(self, args: str) -> None:
        """Show system status."""
        status = {
            'root_directory': self.root_dir,
            'cache_enabled': self.cache is not None,
            'copilot_enabled': self.copilot_manager is not None,
            'auto_update_enabled': self.config.is_auto_update_enabled(),
            'struct_file': self.config.get_struct_file_path(),
            'context_file': self.config.get_context_file_path()
        }
        
        if self.cache:
            status['cache_stats'] = self.cache.get_stats()
        
        if self.copilot_manager:
            status['copilot_status'] = self.copilot_manager.get_status()
        
        print("System Status:")
        print(self.utils.format_json(status))
    
    def cmd_backup(self, args: str) -> None:
        """Create backup of file."""
        if not args:
            print("Usage: /backup <file>")
            return
        
        file_path = args.strip()
        backup_path = self.utils.backup_file(file_path)
        
        if backup_path:
            print(f"Backup created: {backup_path}")
        else:
            print(f"Failed to create backup for {file_path}")
    
    def cmd_parse(self, args: str) -> None:
        """Parse project structure."""
        try:
            print("Parsing project structure...")
            
            # Generate new struct.json
            output_file = self.config.get_struct_file_path()
            gitignore_patterns = self.config.get_gitignore_patterns()
            
            result = generate_json(
                root_dir=self.root_dir,
                output_file=output_file,
                gitignore_patterns=gitignore_patterns,
                include_patterns=self.config.get_include_patterns(),
                exclude_patterns=self.config.get_exclude_patterns(),
                exclude_dirs=self.config.get_exclude_dirs()
            )
            
            if result:
                print(f"Project structure parsed and saved to {output_file}")
            else:
                print("Failed to parse project structure")
                
        except Exception as e:
            logging.error(f"Error parsing project: {e}")
            print(f"Error parsing project: {e}")
    
    def _process_queue(self) -> None:
        """Process command queue."""
        queue_file = Path(self.root_dir) / "data" / "cli_queue.json"
        if not queue_file.exists():
            print("No queue file found")
            return
        
        try:
            with queue_file.open('r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            # Process queue items
            processed = 0
            for item in queue_data.get('queue', []):
                if item.get('status') == 'pending':
                    print(f"Processing: {item.get('command', 'Unknown command')}")
                    # TODO: Implement actual queue processing
                    processed += 1
            
            print(f"Processed {processed} queue items")
            
        except Exception as e:
            logging.error(f"Error processing queue: {e}")
            print(f"Error processing queue: {e}")
    
    def _show_queue_status(self) -> None:
        """Show queue status."""
        queue_file = Path(self.root_dir) / "data" / "cli_queue.json"
        if not queue_file.exists():
            print("No queue file found")
            return
        
        try:
            with queue_file.open('r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            queue_items = queue_data.get('queue', [])
            pending = sum(1 for item in queue_items if item.get('status') == 'pending')
            completed = sum(1 for item in queue_items if item.get('status') == 'completed')
            failed = sum(1 for item in queue_items if item.get('status') == 'failed')
            
            status = {
                'total_items': len(queue_items),
                'pending': pending,
                'completed': completed,
                'failed': failed
            }
            
            print("Queue Status:")
            print(self.utils.format_json(status))
            
        except Exception as e:
            print(f"Error reading queue status: {e}")
    
    def _clear_queue(self) -> None:
        """Clear command queue."""
        queue_file = Path(self.root_dir) / "data" / "cli_queue.json"
        if not queue_file.exists():
            print("No queue file found")
            return
        
        try:
            # Create backup
            backup_path = self.utils.backup_file("data/cli_queue.json")
            if backup_path:
                print(f"Queue backup created: {backup_path}")
            
            # Clear queue
            with queue_file.open('r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            queue_data['queue'] = []
            
            with queue_file.open('w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2)
            
            print("Queue cleared")
            
        except Exception as e:
            print(f"Error clearing queue: {e}")
    
    def _list_queue(self) -> None:
        """List queue items."""
        queue_file = Path(self.root_dir) / "data" / "cli_queue.json"
        if not queue_file.exists():
            print("No queue file found")
            return
        
        try:
            with queue_file.open('r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            queue_items = queue_data.get('queue', [])
            if not queue_items:
                print("Queue is empty")
                return
            
            print("Queue Items:")
            for i, item in enumerate(queue_items, 1):
                print(f"{i}. {item.get('command', 'Unknown')} [{item.get('status', 'unknown')}]")
                
        except Exception as e:
            print(f"Error listing queue: {e}")
    
    def _trigger_auto_update(self) -> None:
        """Trigger auto-update of struct.json."""
        try:
            self.handle_auto_update([])
        except Exception as e:
            logging.error(f"Auto-update failed: {e}")
    
    def handle_auto_update(self, args: List[str]) -> None:
        """Handle auto-update struct.json command."""
        try:
            # Path to auto_update script
            script_path = Path(self.root_dir) / "scripts" / "auto_update_struct.py"
            
            if not script_path.exists():
                self.utils.log_error(f"Auto-update script not found: {script_path}")
                return
            
            # Run auto-update script with proper arguments
            result = subprocess.run([
                sys.executable, str(script_path), 
                '--root-dir', str(self.root_dir),
                '--output', str(Path(self.root_dir) / "struct.json")
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.utils.log_info("✅ struct.json updated successfully")
                if result.stdout:
                    print(result.stdout)
            else:
                self.utils.log_error(f"❌ Auto-update failed: {result.stderr}")
                
        except Exception as e:
            self.utils.log_error(f"Auto-update error: {e}")

    def handle_struct_status(self, args: List[str]) -> None:
        """Show struct.json status and last update info."""
        try:
            struct_path = Path(self.root_dir) / "struct.json"
            
            if not struct_path.exists():
                print("❌ struct.json not found")
                return
                
            # Get file stats
            stat = os.stat(struct_path)
            
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            
            print(f"📊 struct.json Status:")
            print(f"  Last modified: {modified_time}")
            print(f"  Size: {size} bytes")
            
            # Check if auto-update is enabled
            git_hooks_path = Path(self.root_dir) / ".git" / "hooks"
            if (git_hooks_path / "pre-commit").exists():
                print("  ✅ Auto-update enabled (Git hooks)")
            else:
                print("  ⚠️  Auto-update not configured")
                
        except Exception as e:
            self.utils.log_error(f"Status check error: {e}")

    def handle_workflow_trigger(self, event_type: str, context: Dict[str, Any] = None) -> None:
        """Trigger workflow events that may require struct.json update."""
        try:
            # Initialize copilot context manager
            copilot = initialize_copilot(str(self.root_dir))
            
            # Trigger the event
            event_context = trigger_copilot_event(
                copilot, event_type, **context or {}
            )
            
            # Check if struct.json update is needed
            if event_type in ["file_create", "file_edit", "function_creation"]:
                self.utils.log_info(f"🔄 Triggering auto-update for event: {event_type}")
                self.handle_auto_update([])
            
            # Log context for LLM
            if event_context:
                self.utils.log_info(f"📋 Context loaded for {event_type}: {len(event_context)} layers")
                
            copilot.close()
            
        except Exception as e:
            self.utils.log_error(f"Workflow trigger error: {e}")
