# cli_commands.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""CLI command processing and handlers."""

import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import generate_json
from llmstruct.copilot import initialize_copilot, trigger_copilot_event, get_optimized_context_for_scenario
from llmstruct.context_orchestrator import create_context_orchestrator, get_optimized_context
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
        self.default_context_mode: str = "FOCUSED"  # Default context mode for optimization

        # Initialize command handlers
        self.commands = {
            "help": self.cmd_help,
            "view": self.cmd_view,
            "write": self.cmd_write,
            "generate": self.cmd_write,
            "create": self.cmd_write,
            "queue": self.cmd_queue,
            "cache": self.cmd_cache,
            "copilot": self.cmd_copilot,
            "config": self.cmd_config,
            "status": self.cmd_status,
            "backup": self.cmd_backup,
            "parse": self.cmd_parse,
            "audit": self.cmd_audit,
            "auto-update": self.handle_auto_update,
            "struct-status": self.handle_struct_status,
            "context": self.cmd_context,
            "session": self.cmd_session,
            "mode": self.cmd_mode,
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
        args = parts[1] if len(parts) > 1 else ""

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
            # Use context orchestrator for optimized context
            context_data = None
            try:
                # Determine scenario based on default context mode
                scenario = "cli_interactive" if self.default_context_mode == "FULL" else "cli_query"
                
                # Get optimized context using the orchestrator
                context_data = get_optimized_context(
                    project_root=self.root_dir,
                    scenario=scenario,
                    file_path=None
                )
                
                if context_data:
                    logging.info(f"Using optimized context with mode {self.default_context_mode}")
                else:
                    logging.warning("Failed to get optimized context, using standard processing")
                    
            except Exception as e:
                logging.warning(f"Context orchestration failed: {e}")

            # Emit Copilot event if manager is available
            if self.copilot_manager:
                event = CopilotEvent(
                    event_type="prompt_received", 
                    data={
                        "prompt": prompt,
                        "context_mode": self.default_context_mode,
                        "optimized_context": context_data is not None
                    }, 
                    source="cli"
                )
                self.copilot_manager.emit_event(event)

            # For now, just acknowledge the prompt with context info
            print(f"Received prompt: {prompt}")
            if context_data:
                context_info = context_data.get("metrics", {})
                print(f"Using optimized context - Mode: {self.default_context_mode}, Sources: {len(context_data.get('sources', {}))}")
                if context_info:
                    print(f"  Tokens: {context_info.get('tokens_used', 'unknown')}, Load time: {context_info.get('load_time', 'unknown')}s")
            
            print("Note: LLM processing integration is pending. Use '/context get <scenario>' to test context optimization.")

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
  /audit [scan|recover|status] - Audit and recover missing tasks/ideas
  /auto-update         - Trigger auto-update of struct.json
  /struct-status       - Show struct.json status and last update info
  /context <action>    - Smart context operations (get, optimize, scenarios)
  /session <action>    - Session management (start, switch, status, summary)
  /mode <FULL|FOCUSED|MINIMAL|SESSION> - Switch context mode

Context Commands:
  /context get <scenario> [file] - Get optimized context for scenario
  /context optimize <scenario>   - Show context optimization for scenario
  /context scenarios             - List available scenarios
  /context metrics               - Show context loading metrics

Session Commands:
  /session start <branch>        - Start new session for branch
  /session switch <session_id>   - Switch to existing session
  /session status                - Show current session status
  /session summary               - Generate session summary
  /session list                  - List all sessions

Examples:
  /view src/           - Show directory structure
  /view README.md      - Show file content
  /write test.txt "Hello World" - Write to file
  /queue run           - Process command queue
  /cache stats         - Show cache statistics
  /copilot status      - Show Copilot status
  /audit scan          - Scan source files for missing entries
  /audit recover       - Recover missing tasks/ideas from source files
  /audit status        - Show current placeholder status
  /auto-update         - Trigger struct.json update
  /struct-status       - Show struct.json status
  /context get vscode_copilot src/main.py - Get VS Code context for file
  /context scenarios   - Show available context scenarios
  /session start feature/new-feature - Start session for new branch
  /session status      - Show current session info
  /mode FOCUSED        - Set context mode (FULL|FOCUSED|MINIMAL|SESSION)
  /mode FOCUSED        - Switch to focused context mode
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
                self.config.get_exclude_dirs(),
            )

            if structure:
                print(f"Directory structure for {full_path}:")
                print(self.utils.format_json(structure))
            else:
                print(f"No accessible items found in {full_path}")

        elif os.path.isfile(full_path):
            content = self.utils.read_file_content(
                path, self.config.get_max_file_size()
            )
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
        match = re.match(r"(\S+)\s+(.*)", args, re.DOTALL)
        if not match:
            print("Usage: /write <filename> <content>")
            return

        filename, content = match.groups()

        # Remove quotes if present
        content = content.strip()
        if (content.startswith('"') and content.endswith('"')) or (
            content.startswith("'") and content.endswith("'")
        ):
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

        if action == "run":
            self._process_queue()
        elif action == "status":
            self._show_queue_status()
        elif action == "clear":
            self._clear_queue()
        elif action == "list":
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

        if action == "stats":
            stats = self.cache.get_stats()
            print("Cache Statistics:")
            print(self.utils.format_json(stats))
        elif action == "clear":
            self.cache.clear()
            print("Cache cleared")
        elif action == "info":
            info = {
                "cache_dir": self.cache.cache_dir,
                "max_size": self.cache.max_size,
                "ttl": self.cache.ttl,
                "current_size": len(self.cache._cache),
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

        if action == "status":
            if self.copilot_manager:
                status = self.copilot_manager.get_status()
                print("Copilot Status:")
                print(self.utils.format_json(status))
            else:
                print("Copilot is not initialized")
        elif action == "config":
            config = self.config.get_copilot_config()
            print("Copilot Configuration:")
            print(self.utils.format_json(config))
        elif action == "test":
            if self.copilot_manager:
                test_event = CopilotEvent(
                    event_type="test_event",
                    data={"message": "Test from CLI"},
                    source="cli_test",
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
                "cache": self.config.get_cache_config(),
                "copilot": self.config.get_copilot_config(),
                "queue": self.config.get_queue_config(),
                "context": self.config.get_context_config(),
                "auto_update": self.config.get_auto_update_config(),
            }
            print("Current Configuration:")
            print(self.utils.format_json(config_data))
        else:
            section = args.strip().lower()
            if section == "cache":
                config = self.config.get_cache_config()
            elif section == "copilot":
                config = self.config.get_copilot_config()
            elif section == "queue":
                config = self.config.get_queue_config()
            elif section == "context":
                config = self.config.get_context_config()
            elif section == "auto_update":
                config = self.config.get_auto_update_config()
            else:
                print(f"Unknown config section: {section}")
                return

            print(f"{section.title()} Configuration:")
            print(self.utils.format_json(config))

    def cmd_status(self, args: str) -> None:
        """Show system status."""
        status = {
            "root_directory": self.root_dir,
            "cache_enabled": self.cache is not None,
            "copilot_enabled": self.copilot_manager is not None,
            "auto_update_enabled": self.config.is_auto_update_enabled(),
            "struct_file": self.config.get_struct_file_path(),
            "context_file": self.config.get_context_file_path(),
        }

        if self.cache:
            status["cache_stats"] = self.cache.get_stats()

        if self.copilot_manager:
            status["copilot_status"] = self.copilot_manager.get_status()

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
                exclude_dirs=self.config.get_exclude_dirs(),
            )

            if result:
                print(f"Project structure parsed and saved to {output_file}")
            else:
                print("Failed to parse project structure")

        except Exception as e:
            logging.error(f"Error parsing project: {e}")
            print(f"Error parsing project: {e}")

    def cmd_audit(self, args: str) -> None:
        """Audit and recover missing tasks/ideas from source files."""
        try:
            action = args.strip().lower() if args.strip() else "scan"
            
            if action == "scan":
                self._audit_scan_sources()
            elif action == "recover":
                self._audit_recover_placeholders()
            elif action == "status":
                self._audit_show_status()
            else:
                print("Usage: /audit [scan|recover|status]")
                print("  scan    - Scan source files for missing entries")
                print("  recover - Recover missing tasks/ideas from source files")
                print("  status  - Show current placeholder status")
                
        except Exception as e:
            logging.error(f"Audit command error: {e}")
            print(f"Error in audit command: {e}")

    def cmd_mode(self, args: str) -> None:
        """Handle context mode operations."""
        if not args:
            print(f"Current context mode: {self.default_context_mode}")
            print("Usage: /mode <FULL|FOCUSED|MINIMAL|SESSION>")
            print("  FULL    - Complete context with documentation and code")
            print("  FOCUSED - Balanced context for interactive work")  
            print("  MINIMAL - Lightweight context for quick queries")
            print("  SESSION - Session-only context for continuity")
            return

        mode = args.strip().upper()
        valid_modes = ["FULL", "FOCUSED", "MINIMAL", "SESSION"]
        
        if mode not in valid_modes:
            print(f"Invalid mode: {mode}")
            print(f"Valid modes: {', '.join(valid_modes)}")
            return
        
        old_mode = self.default_context_mode
        self.default_context_mode = mode
        
        print(f"Context mode changed: {old_mode} → {mode}")
        
        # Test the new mode
        try:
            scenario = "cli_interactive" if mode == "FULL" else "cli_query"
            context_data = get_optimized_context(
                project_root=self.root_dir,
                scenario=scenario,
                file_path=None
            )
            
            if context_data:
                metrics = context_data.get("metrics", {})
                print(f"Mode test successful:")
                print(f"  Sources loaded: {len(context_data.get('sources', {}))}")
                print(f"  Estimated tokens: {metrics.get('tokens_used', 'unknown')}")
                print(f"  Load time: {metrics.get('load_time', 'unknown')}s")
            else:
                print("Mode test failed - context orchestrator not available")
                
        except Exception as e:
            print(f"Mode test failed: {e}")

    def handle_auto_update(self, args: str) -> None:
        """Handle auto-update struct.json command."""
        try:
            print("🔄 Triggering auto-update of struct.json...")
            
            # Path to the auto-update script
            script_path = Path(self.root_dir) / "scripts" / "auto_update_struct.py"
            
            if not script_path.exists():
                print("❌ Auto-update script not found at scripts/auto_update_struct.py")
                return
            
            # Run the auto-update script
            import subprocess
            import sys
            
            result = subprocess.run(
                [sys.executable, str(script_path), "--root-dir", self.root_dir],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            if result.returncode == 0:
                print("✅ Auto-update struct.json completed successfully")
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
            else:
                print("❌ Auto-update failed")
                if result.stderr.strip():
                    print(f"Error: {result.stderr.strip()}")
                    
        except Exception as e:
            logging.error(f"Auto-update command error: {e}")
            print(f"Error in auto-update command: {e}")

    def handle_struct_status(self, args: str) -> None:
        """Handle struct status command."""
        try:
            struct_path = Path(self.root_dir) / "struct.json"
            
            print("struct.json status:")
            
            if struct_path.exists():
                stat = struct_path.stat()
                
                # Format file size
                size_bytes = stat.st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                
                # Format modification time
                import time
                mod_time = time.ctime(stat.st_mtime)
                
                print(f"  📁 Path: {struct_path}")
                print(f"  📅 Modified: {mod_time}")
                print(f"  📏 Size: {size_str}")
                
                # Check if auto-update script is available
                script_path = Path(self.root_dir) / "scripts" / "auto_update_struct.py"
                if script_path.exists():
                    print("  🔄 Auto-update: Available")
                else:
                    print("  🔄 Auto-update: Not available")
                
                # Try to get basic statistics from the file
                try:
                    with open(struct_path, 'r', encoding='utf-8') as f:
                        struct_data = json.load(f)
                    
                    metadata = struct_data.get('metadata', {})
                    stats = metadata.get('stats', {})
                    
                    if stats:
                        print(f"  📊 Modules: {stats.get('modules_count', 'unknown')}")
                        print(f"  🎯 Functions: {stats.get('functions_count', 'unknown')}")
                        print(f"  📋 Classes: {stats.get('classes_count', 'unknown')}")
                    
                    goals = struct_data.get('goals', [])
                    if goals:
                        print(f"  🎯 Goals: {len(goals)}")
                        
                except Exception as e:
                    print(f"  ⚠️  Could not parse struct.json: {e}")
                    
            else:
                print("  ❌ struct.json not found")
                print("  💡 Run '/parse' to generate struct.json")
                
        except Exception as e:
            logging.error(f"Struct status command error: {e}")
            print(f"Error in struct status command: {e}")

    def cmd_context(self, args: str) -> None:
        """Handle smart context operations."""
        if not args:
            print("Usage: /context <get|optimize|scenarios|metrics> [options]")
            return

        parts = args.strip().split()
        action = parts[0].lower()

        try:
            if action == "get":
                if len(parts) < 2:
                    print("Usage: /context get <scenario> [file_path]")
                    return
                
                scenario = parts[1]
                file_path = parts[2] if len(parts) > 2 else None
                
                context = get_optimized_context(
                    project_root=self.root_dir,
                    scenario=scenario,
                    file_path=file_path
                )
                
                print(f"Optimized context for scenario '{scenario}':")
                print(self.utils.format_json(context))

            elif action == "optimize":
                if len(parts) < 2:
                    print("Usage: /context optimize <scenario>")
                    return
                
                scenario = parts[1]
                orchestrator = create_context_orchestrator(self.root_dir)
                
                # Get optimization metrics
                context = orchestrator.get_context_for_scenario(scenario)
                metrics = context.get("metrics", {})
                
                print(f"Context optimization for scenario '{scenario}':")
                print(f"  Mode: {context.get('mode', 'unknown')}")
                print(f"  Sources loaded: {len(context.get('sources', {}))}")
                print(f"  Tokens used: {metrics.get('tokens_used', 'unknown')}")
                print(f"  Load time: {metrics.get('load_time', 'unknown')}s")

            elif action == "scenarios":
                orchestrator = create_context_orchestrator(self.root_dir)
                
                # Get available scenarios from config
                config = orchestrator.config.get("scenario_mappings", {})
                
                print("Available context scenarios:")
                for scenario_name, mode in config.items():
                    print(f"  {scenario_name}: {mode}")

            elif action == "metrics":
                # Show context loading metrics
                print("Context loading metrics:")
                print("  Feature available in future version")
                # TODO: Implement metrics collection and display

            else:
                print(f"Unknown context action: {action}")
                print("Available actions: get, optimize, scenarios, metrics")

        except Exception as e:
            logging.error(f"Context command error: {e}")
            print(f"Error in context command: {e}")

    def cmd_session(self, args: str) -> None:
        """Handle session management operations."""
        if not args:
            print("Usage: /session <start|switch|status|summary|list> [options]")
            return

        parts = args.strip().split()
        action = parts[0].lower()

        try:
            sessions_dir = Path(self.root_dir) / "data" / "sessions"
            current_session_file = sessions_dir / "current_session.json"
            ai_sessions_file = sessions_dir / "ai_sessions.json"
            worklog_file = sessions_dir / "worklog.json"

            if action == "start":
                if len(parts) < 2:
                    print("Usage: /session start <branch_name>")
                    return
                
                branch_name = parts[1]
                self._start_new_session(branch_name, sessions_dir)

            elif action == "switch":
                if len(parts) < 2:
                    print("Usage: /session switch <session_id>")
                    return
                
                session_id = parts[1]
                self._switch_session(session_id, sessions_dir)

            elif action == "status":
                self._show_session_status(current_session_file)

            elif action == "summary":
                self._generate_session_summary(current_session_file, worklog_file)

            elif action == "list":
                self._list_sessions(ai_sessions_file)

            else:
                print(f"Unknown session action: {action}")
                print("Available actions: start, switch, status, summary, list")

        except Exception as e:
            logging.error(f"Session command error: {e}")
            print(f"Error in session command: {e}")

    def _start_new_session(self, branch_name: str, sessions_dir: Path) -> None:
        """Start a new session."""
        import uuid
        from datetime import datetime
        
        session_id = f"SES-{str(uuid.uuid4())[:8]}"
        timestamp = datetime.now().isoformat() + "Z"
        
        # Create session data
        session_data = {
            "id": session_id,
            "branch": branch_name,
            "title": f"Session for {branch_name}",
            "status": "active",
            "created_at": timestamp,
            "author": "@user",
            "type": "ai-helped",
            "related_tasks": [],
            "related_ideas": [],
            "related_insights": [],
            "related_docs": [],
            "knowledge_cache": [],
            "context_notes": f"Working on branch {branch_name}",
            "results": [],
            "summary": ""
        }
        
        # Update current_session.json
        current_session = {
            "version": "0.1.0",
            "session_id": session_id,
            "branch": branch_name,
            "status": "active",
            "started_at": timestamp,
            "author": "@user",
            "notes": f"Started session for branch {branch_name}"
        }
        
        # Update ai_sessions.json
        ai_sessions_file = sessions_dir / "ai_sessions.json"
        if ai_sessions_file.exists():
            with open(ai_sessions_file, 'r', encoding='utf-8') as f:
                ai_sessions = json.load(f)
        else:
            ai_sessions = {"version": "0.1.0", "sessions": []}
        
        ai_sessions["sessions"].append(session_data)
        
        # Write files
        os.makedirs(sessions_dir, exist_ok=True)
        
        with open(sessions_dir / "current_session.json", 'w', encoding='utf-8') as f:
            json.dump(current_session, f, indent=2)
        
        with open(ai_sessions_file, 'w', encoding='utf-8') as f:
            json.dump(ai_sessions, f, indent=2)
        
        # Initialize worklog
        worklog = {
            "version": "0.1.0",
            "session_id": session_id,
            "branch": branch_name,
            "log": [
                {
                    "timestamp": timestamp,
                    "author": "@user",
                    "event": f"Session {session_id} started for branch {branch_name}"
                }
            ]
        }
        
        with open(sessions_dir / "worklog.json", 'w', encoding='utf-8') as f:
            json.dump(worklog, f, indent=2)
        
        print(f"✅ Started new session: {session_id} for branch '{branch_name}'")

    def _switch_session(self, session_id: str, sessions_dir: Path) -> None:
        """Switch to an existing session."""
        ai_sessions_file = sessions_dir / "ai_sessions.json"
        
        if not ai_sessions_file.exists():
            print("❌ No sessions found")
            return
        
        with open(ai_sessions_file, 'r', encoding='utf-8') as f:
            ai_sessions = json.load(f)
        
        # Find session
        target_session = None
        for session in ai_sessions.get("sessions", []):
            if session.get("id") == session_id:
                target_session = session
                break
        
        if not target_session:
            print(f"❌ Session {session_id} not found")
            return
        
        # Update current_session.json
        current_session = {
            "version": "0.1.0",
            "session_id": session_id,
            "branch": target_session.get("branch", "unknown"),
            "status": "active",
            "started_at": target_session.get("created_at", "unknown"),
            "author": target_session.get("author", "@user"),
            "notes": f"Switched to session {session_id}"
        }
        
        with open(sessions_dir / "current_session.json", 'w', encoding='utf-8') as f:
            json.dump(current_session, f, indent=2)
        
        print(f"✅ Switched to session: {session_id}")

    def _show_session_status(self, current_session_file: Path) -> None:
        """Show current session status."""
        if not current_session_file.exists():
            print("❌ No active session")
            return
        
        with open(current_session_file, 'r', encoding='utf-8') as f:
            current_session = json.load(f)
        
        print("📊 Current session status:")
        print(f"  Session ID: {current_session.get('session_id', 'unknown')}")
        print(f"  Branch: {current_session.get('branch', 'unknown')}")
        print(f"  Status: {current_session.get('status', 'unknown')}")
        print(f"  Started: {current_session.get('started_at', 'unknown')}")
        print(f"  Author: {current_session.get('author', 'unknown')}")
        print(f"  Notes: {current_session.get('notes', 'No notes')}")

    def _generate_session_summary(self, current_session_file: Path, worklog_file: Path) -> None:
        """Generate session summary."""
        if not current_session_file.exists():
            print("❌ No active session")
            return
        
        with open(current_session_file, 'r', encoding='utf-8') as f:
            current_session = json.load(f)
        
        session_id = current_session.get('session_id', 'unknown')
        
        print(f"📋 Session summary for {session_id}:")
        print(f"  Branch: {current_session.get('branch', 'unknown')}")
        print(f"  Started: {current_session.get('started_at', 'unknown')}")
        
        if worklog_file.exists():
            with open(worklog_file, 'r', encoding='utf-8') as f:
                worklog = json.load(f)
            
            log_entries = worklog.get('log', [])
            print(f"  Log entries: {len(log_entries)}")
            
            if log_entries:
                print("  Recent activities:")
                for entry in log_entries[-3:]:  # Show last 3 entries
                    timestamp = entry.get('timestamp', 'unknown')
                    event = entry.get('event', 'unknown')
                    print(f"    - {timestamp}: {event}")

    def _list_sessions(self, ai_sessions_file: Path) -> None:
        """List all sessions."""
        if not ai_sessions_file.exists():
            print("❌ No sessions found")
            return
        
        with open(ai_sessions_file, 'r', encoding='utf-8') as f:
            ai_sessions = json.load(f)
        
        sessions = ai_sessions.get("sessions", [])
        
        if not sessions:
            print("📋 No sessions found")
            return
        
        print(f"📋 Found {len(sessions)} sessions:")
        for session in sessions:
            session_id = session.get("id", "unknown")
            branch = session.get("branch", "unknown")
            status = session.get("status", "unknown")
            created_at = session.get("created_at", "unknown")
            print(f"  {session_id}: {branch} [{status}] - {created_at}")

    def _audit_scan_sources(self) -> None:
        """Scan dump directory for recoverable content."""
        import json
        import os
        from pathlib import Path
        
        dump_dir = Path(self.root_dir) / "temp_workfiles" / "unsorted_mess" / "dump"
        if not dump_dir.exists():
            print(f"❌ Dump directory not found: {dump_dir}")
            return
            
        print(f"🔍 Scanning recovery sources in: {dump_dir}")
        
        json_files = list(dump_dir.glob("*.json"))
        py_files = list(dump_dir.glob("*.py"))
        
        print(f"📁 Found {len(json_files)} JSON files and {len(py_files)} Python files")
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, dict):
                    if "tasks" in data:
                        tasks = data["tasks"]
                        if isinstance(tasks, list):
                            print(f"📋 {file_path.name}: {len(tasks)} tasks")
                    if "ideas" in data:
                        ideas = data["ideas"]
                        if isinstance(ideas, list):
                            print(f"💡 {file_path.name}: {len(ideas)} ideas")
                            
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️  {file_path.name}: {e}")
                
        print("✅ Scan complete. Use '/audit recover' to restore missing entries.")

    def _audit_recover_placeholders(self) -> None:
        """Recover placeholder entries from source files."""
        print("🔄 Placeholder recovery not yet implemented")
        print("This feature would scan source files and recover missing task/idea entries")

    def _audit_show_status(self) -> None:
        """Show current placeholder status."""
        import json
        from pathlib import Path
        
        tasks_file = Path(self.root_dir) / "data" / "tasks.json"
        ideas_file = Path(self.root_dir) / "data" / "ideas.json"
        
        if not tasks_file.exists() or not ideas_file.exists():
            print("❌ Core data files not found")
            return
            
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)
        with open(ideas_file, 'r') as f:
            ideas_data = json.load(f)
            
        task_placeholders = [t for t in tasks_data["tasks"] if "Placeholder: Missing task details" in t.get("description", "")]
        idea_placeholders = [i for i in ideas_data["ideas"] if "Placeholder: Missing idea details" in i.get("description", "")]
        
        print("📊 Current placeholder status:")
        print(f"   Tasks: {len(task_placeholders)} placeholders of {len(tasks_data['tasks'])} total")
        print(f"   Ideas: {len(idea_placeholders)} placeholders of {len(ideas_data['ideas'])} total")
        
        if task_placeholders:
            task_ids = [t["id"] for t in task_placeholders[:5]]
            print(f"   Example task IDs: {', '.join(task_ids)}{'...' if len(task_placeholders) > 5 else ''}")
            
        if idea_placeholders:
            idea_ids = [i["id"] for i in idea_placeholders[:5]]
            print(f"   Example idea IDs: {', '.join(idea_ids)}{'...' if len(idea_placeholders) > 5 else ''}")

    def _process_queue(self) -> None:
        """Process command queue."""
        queue_file = Path(self.root_dir) / "data" / "cli_queue.json"
        if not queue_file.exists():
            print("No queue file found")
            return

        try:
            with queue_file.open("r", encoding="utf-8") as f:
                queue_data = json.load(f)

            # Process queue items
            processed = 0
            for item in queue_data.get("queue", []):
                if item.get("status") == "pending":
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
            with queue_file.open("r", encoding="utf-8") as f:
                queue_data = json.load(f)

            queue_items = queue_data.get("queue", [])
            pending = sum(1 for item in queue_items if item.get("status") == "pending")
            completed = sum(
                1 for item in queue_items if item.get("status") == "completed"
            )
            failed = sum(1 for item in queue_items if item.get("status") == "failed")

            status = {
                "total_items": len(queue_items),
                "pending": pending,
                "completed": completed,
                "failed": failed,
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
            with queue_file.open("r", encoding="utf-8") as f:
                queue_data = json.load(f)

            queue_data["queue"] = []

            with queue_file.open("w", encoding="utf-8") as f:
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
            with queue_file.open("r", encoding="utf-8") as f:
                queue_data = json.load(f)

            queue_items = queue_data.get("queue", [])
            if not queue_items:
                print("Queue is empty")
                return

            print("Queue Items:")
            for i, item in enumerate(queue_items, 1):
                print(
                    f"{i}. {item.get('command', 'Unknown')} [{item.get('status', 'unknown')}]"
                )

        except Exception as e:
            print(f"Error listing queue: {e}")

    def _trigger_auto_update(self) -> None:
        """Trigger auto-update of struct.json."""
        try:
            self.handle_auto_update("")
        except Exception as e:
            logging.error(f"Auto-update trigger failed: {e}")
            print(f"Auto-update failed: {e}")
