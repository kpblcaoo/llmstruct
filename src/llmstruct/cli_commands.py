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
from .workspace import WorkspaceStateManager


class CommandProcessor:
    """Processes CLI commands and user prompts."""

    def __init__(self, root_dir: str, config: CLIConfig, utils: CLIUtils):
        """Initialize command processor."""
        self.root_dir = root_dir
        self.config = config
        self.utils = utils
        self.cache: Optional[JSONCache] = None
        self.copilot_manager: Optional[CopilotContextManager] = None
        self.workspace_manager: Optional[WorkspaceStateManager] = None
        self.default_context_mode: str = "FOCUSED"  # Default context mode for optimization

        # Initialize workspace manager
        workspace_dir = os.path.join(root_dir, "data", "workspace")
        try:
            self.workspace_manager = WorkspaceStateManager(workspace_dir)
            print(f"✅ Workspace State Manager initialized")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Workspace Manager: {e}")

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
            "workspace": self.cmd_workspace,  # New workspace command
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
  /workspace <action>  - Workspace state and permissions management

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

Workspace Commands:
  /workspace status              - Show current workspace state
  /workspace mode [mode1][mode2] - Set workspace mode(s)
  /workspace permissions         - Show current permissions
  /workspace override <level>    - Grant emergency override
  /workspace history             - Show mode history

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
  /workspace mode [code][debug] - Set workspace mode
"""
        print(help_text)

    def cmd_workspace(self, args: str) -> None:
        """Handle workspace state and permissions management."""
        if not self.workspace_manager:
            print("❌ Workspace State Manager not available")
            return
            
        if not args:
            print("Usage: /workspace <action> [options]")
            print("Actions:")
            print("  status               - Show current workspace state")
            print("  mode [mode1][mode2]  - Set workspace mode(s)")
            print("  permissions          - Show current permissions")
            print("  override <level>     - Grant emergency override")
            print("  history              - Show mode history")
            return

        parts = args.strip().split(maxsplit=1)
        action = parts[0].lower()
        action_args = parts[1] if len(parts) > 1 else ""

        try:
            if action == "status":
                state = self.workspace_manager.get_current_state()
                print("🏗️ Workspace State:")
                print(f"  Current Mode: {self.workspace_manager.get_mode_status()}")
                print(f"  Active Session: {state.get('active_session', 'None')}")
                
                permissions = state.get("permissions", {})
                print(f"  Capabilities: {', '.join(permissions.get('capabilities', []))}")
                print(f"  File Restrictions: {len(permissions.get('file_restrictions', []))}")
                
                override = state.get("emergency_overrides", {})
                if override.get("active"):
                    print(f"  🚨 Emergency Override: Level {override.get('level')} active")
                
                # Show context boundaries
                boundaries = state.get("context_boundaries", {})
                focus_files = boundaries.get("focus_files", [])
                if focus_files:
                    print(f"  Focus Files: {len(focus_files)} files")

            elif action == "mode":
                if not action_args:
                    state = self.workspace_manager.get_current_state()
                    current_modes = state.get("current_mode", [])
                    print(f"Current workspace mode: {current_modes}")
                    print("Available modes: code, discuss, debug, review, meta, decide")
                    print("Usage: /workspace mode [code][debug]")
                    return
                
                # Set new mode
                result = self.workspace_manager.set_mode(action_args, session_id="SES-004A")
                
                if result.get("success"):
                    print(f"✅ Mode changed: {result['previous_mode']} → {result['current_mode']}")
                    print(f"   Combination: {result['mode_combination']}")
                    print(f"   Restrictions: {result['restrictions_applied']} rules applied")
                else:
                    print(f"❌ Failed to change mode: {result.get('error', 'Unknown error')}")

            elif action == "permissions":
                state = self.workspace_manager.get_current_state()
                permissions = state.get("permissions", {})
                
                print("🔐 Current Permissions:")
                print(f"  Capabilities: {permissions.get('capabilities', [])}")
                print(f"  Safe Operations: {permissions.get('safe_operations', [])}")
                print(f"  File Restrictions: {permissions.get('file_restrictions', [])}")

            elif action == "override":
                if not action_args:
                    print("Usage: /workspace override <1|2|3> [reason] [duration_minutes]")
                    print("  Level 1: Extend current permissions")
                    print("  Level 2: Full filesystem access")
                    print("  Level 3: Full system access")
                    return
                
                override_parts = action_args.split()
                level = int(override_parts[0]) if override_parts[0].isdigit() else 1
                reason = " ".join(override_parts[1:]) if len(override_parts) > 1 else "Manual override"
                
                result = self.workspace_manager.set_emergency_override(
                    level=level, 
                    reason=reason, 
                    duration_minutes=30
                )
                
                if result.get("success"):
                    print(f"🚨 Emergency override granted:")
                    print(f"   Level: {result['level']}")
                    print(f"   Duration: {result['expires_in_minutes']} minutes")
                    print(f"   Reason: {result['reason']}")
                else:
                    print(f"❌ Override failed: {result.get('error')}")

            elif action == "history":
                state = self.workspace_manager.get_current_state()
                history = state.get("mode_history", [])
                
                print("📈 Mode History:")
                if not history:
                    print("  No mode changes recorded")
                else:
                    for entry in history[-5:]:  # Show last 5 entries
                        mode = entry.get("mode", [])
                        ended_at = entry.get("ended_at", "")
                        session = entry.get("session", "")
                        print(f"  {mode} - {ended_at} (Session: {session})")

            else:
                print(f"Unknown workspace action: {action}")
                print("Available actions: status, mode, permissions, override, history")

        except Exception as e:
            logging.error(f"Workspace command error: {e}")
            print(f"Error in workspace command: {e}")

    def cmd_mode(self, args: str) -> None:
        """Handle context mode operations with workspace integration."""
        if not args:
            print(f"Current context mode: {self.default_context_mode}")
            
            # Show workspace mode if available
            if self.workspace_manager:
                print(f"Workspace mode: {self.workspace_manager.get_mode_status()}")
            
            print("Usage: /mode <FULL|FOCUSED|MINIMAL|SESSION> or [workspace_mode]")
            print("Context modes:")
            print("  FULL    - Complete context with documentation and code")
            print("  FOCUSED - Balanced context for interactive work")  
            print("  MINIMAL - Lightweight context for quick queries")
            print("  SESSION - Session-only context for continuity")
            print("Workspace modes:")
            print("  [code]     - Development and coding")
            print("  [discuss]  - Discussion and planning")
            print("  [debug]    - Debugging and troubleshooting")
            print("  [review]   - Code review and analysis")
            print("  [meta]     - Documentation and meta work")
            print("  [decide]   - Decision-making sessions")
            print("  Examples: [code][debug], [discuss][meta], [review][security]")
            return

        args = args.strip()
        
        # Check if this is a workspace mode (contains brackets)
        if '[' in args and ']' in args:
            if not self.workspace_manager:
                print("❌ Workspace State Manager not available for workspace modes")
                return
            
            # Extract strict mode tags if present
            strict_tags = []
            if 'strict' in args.lower():
                # Parse strict mode integration
                import re
                strict_patterns = re.findall(r'\[([^\]]*strict[^\]]*)\]', args.lower())
                strict_tags = [tag for tag in strict_patterns if 'strict' in tag]
                
                if strict_tags:
                    print(f"🔒 Strict mode detected: {strict_tags}")
                    self.workspace_manager.integrate_strict_mode(strict_tags)
            
            # Set workspace mode
            result = self.workspace_manager.set_mode(args, session_id="SES-004A")
            
            if result.get("success"):
                print(f"✅ Workspace mode set: {result['current_mode']}")
                print(f"   {result['mode_combination']}")
                
                # Show permissions summary
                permissions = result.get("permissions", {})
                capabilities = permissions.get("capabilities", [])
                restrictions = permissions.get("file_restrictions", [])
                
                print(f"   Capabilities: {', '.join(capabilities[:3])}{'...' if len(capabilities) > 3 else ''}")
                print(f"   Restrictions: {len(restrictions)} rules applied")
                
                if strict_tags:
                    print(f"   🔒 Strict mode active: {strict_tags}")
            else:
                print(f"❌ Failed to set workspace mode: {result.get('error', 'Unknown error')}")
            
            return

        # Handle traditional context modes
        mode = args.upper()
        valid_modes = ["FULL", "FOCUSED", "MINIMAL", "SESSION"]
        
        if mode not in valid_modes:
            print(f"Invalid mode: {mode}")
            print(f"Valid context modes: {', '.join(valid_modes)}")
            print("For workspace modes, use: [code], [discuss], [debug], etc.")
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

    def cmd_view(self, args: str) -> None:
        """View file or directory contents."""
        if not args:
            print("Usage: /view <path>")
            return
        
        path = args.strip()
        try:
            full_path = self.utils.safe_path_join(self.root_dir, path)
            
            if not os.path.exists(full_path):
                print(f"Path not found: {path}")
                return
            
            if os.path.isfile(full_path):
                # Display file contents
                content = self.utils.read_file_content(path)
                if content is not None:
                    print(f"=== {path} ===")
                    print(content)
                else:
                    print(f"Failed to read file: {path}")
            elif os.path.isdir(full_path):
                # Display directory contents
                try:
                    items = os.listdir(full_path)
                    print(f"=== Directory: {path} ===")
                    for item in sorted(items):
                        item_path = os.path.join(full_path, item)
                        if os.path.isdir(item_path):
                            print(f"📁 {item}/")
                        else:
                            print(f"📄 {item}")
                except PermissionError:
                    print(f"Permission denied: {path}")
            else:
                print(f"Unknown file type: {path}")
                
        except Exception as e:
            print(f"Error viewing {path}: {e}")

    def cmd_write(self, args: str) -> None:
        """Write content to a file."""
        if not args:
            print("Usage: /write <file> <content>")
            return
        
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: /write <file> <content>")
            return
        
        file_path = parts[0]
        content = parts[1]
        
        # Remove quotes if present
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        try:
            success = self.utils.write_file_content(file_path, content)
            if success:
                print(f"✅ File written: {file_path}")
            else:
                print(f"❌ Failed to write file: {file_path}")
        except Exception as e:
            print(f"Error writing file: {e}")

    def cmd_queue(self, args: str) -> None:
        """Handle queue operations."""
        if not args:
            print("Usage: /queue <action>")
            print("Actions: run, status, clear, list")
            return
        
        action = args.strip().lower()
        queue_path = os.path.join(self.root_dir, "data", "cli_queue.json")
        
        try:
            if action == "status":
                if os.path.exists(queue_path):
                    with open(queue_path, 'r') as f:
                        queue_data = json.load(f)
                    print(f"Queue status: {len(queue_data.get('commands', []))} items")
                else:
                    print("Queue is empty")
            
            elif action == "list":
                if os.path.exists(queue_path):
                    with open(queue_path, 'r') as f:
                        queue_data = json.load(f)
                    commands = queue_data.get('commands', [])
                    print(f"Queue contains {len(commands)} items:")
                    for i, cmd in enumerate(commands):
                        print(f"  {i+1}. {cmd.get('description', 'No description')}")
                else:
                    print("Queue is empty")
            
            elif action == "clear":
                if os.path.exists(queue_path):
                    os.remove(queue_path)
                print("✅ Queue cleared")
            
            elif action == "run":
                print("Queue processing not implemented yet")
            
            else:
                print(f"Unknown queue action: {action}")
                
        except Exception as e:
            print(f"Queue error: {e}")

    def cmd_cache(self, args: str) -> None:
        """Handle cache operations."""
        if not args:
            print("Usage: /cache <action>")
            print("Actions: stats, clear, info")
            return
        
        action = args.strip().lower()
        
        try:
            if action == "stats":
                if self.cache:
                    stats = self.cache.get_stats()
                    print("📊 Cache Statistics:")
                    print(f"  Total items: {stats.get('total_items', 0)}")
                    print(f"  Size: {stats.get('size_mb', 0):.2f} MB")
                else:
                    print("Cache not initialized")
            
            elif action == "info":
                cache_dir = os.path.join(self.root_dir, "data", ".cache")
                if os.path.exists(cache_dir):
                    print(f"Cache directory: {cache_dir}")
                    files = os.listdir(cache_dir)
                    print(f"Cache files: {len(files)}")
                else:
                    print("No cache directory found")
            
            elif action == "clear":
                if self.cache:
                    self.cache.clear()
                    print("✅ Cache cleared")
                else:
                    print("Cache not initialized")
            
            else:
                print(f"Unknown cache action: {action}")
                
        except Exception as e:
            print(f"Cache error: {e}")

    def cmd_copilot(self, args: str) -> None:
        """Handle Copilot operations."""
        if not args:
            print("Usage: /copilot <action>")
            print("Actions: status, config, test")
            return
        
        action = args.strip().lower()
        
        try:
            if action == "status":
                if self.copilot_manager:
                    print("✅ Copilot manager active")
                    # Could add more status info here
                else:
                    print("❌ Copilot manager not initialized")
            
            elif action == "config":
                copilot_config_path = os.path.join(self.root_dir, "data", "copilot.json")
                if os.path.exists(copilot_config_path):
                    with open(copilot_config_path, 'r') as f:
                        config = json.load(f)
                    print("🔧 Copilot Configuration:")
                    print(json.dumps(config, indent=2))
                else:
                    print("No Copilot configuration found")
            
            elif action == "test":
                print("Copilot test not implemented yet")
            
            else:
                print(f"Unknown copilot action: {action}")
                
        except Exception as e:
            print(f"Copilot error: {e}")

    def cmd_config(self, args: str) -> None:
        """Handle configuration operations."""
        if not args:
            print("Usage: /config <section>")
            print("Available sections: cache, copilot, workspace")
            return
        
        section = args.strip().lower()
        
        try:
            if section == "cache":
                cache_config = self.config.get_cache_config()
                print("💾 Cache Configuration:")
                print(json.dumps(cache_config, indent=2))
            
            elif section == "copilot":
                copilot_config = self.config.get_copilot_config()
                print("🤖 Copilot Configuration:")
                print(json.dumps(copilot_config, indent=2))
            
            elif section == "workspace":
                if self.workspace_manager:
                    state = self.workspace_manager.get_current_state()
                    print("🏗️ Workspace Configuration:")
                    print(json.dumps(state, indent=2))
                else:
                    print("Workspace manager not available")
            
            else:
                print(f"Unknown config section: {section}")
                
        except Exception as e:
            print(f"Config error: {e}")

    def cmd_status(self, args: str) -> None:
        """Show system status."""
        try:
            print("🔍 System Status:")
            print(f"  Root directory: {self.root_dir}")
            print(f"  Cache: {'✅' if self.cache else '❌'}")
            print(f"  Copilot: {'✅' if self.copilot_manager else '❌'}")
            print(f"  Workspace: {'✅' if self.workspace_manager else '❌'}")
            print(f"  Context mode: {self.default_context_mode}")
            
            if self.workspace_manager:
                print(f"  Workspace mode: {self.workspace_manager.get_mode_status()}")
            
        except Exception as e:
            print(f"Status error: {e}")

    def cmd_backup(self, args: str) -> None:
        """Create backup of a file."""
        if not args:
            print("Usage: /backup <file>")
            return
        
        file_path = args.strip()
        
        try:
            backup_path = self.utils.backup_file(file_path)
            if backup_path:
                print(f"✅ Backup created: {backup_path}")
            else:
                print(f"❌ Failed to create backup for: {file_path}")
        except Exception as e:
            print(f"Backup error: {e}")

    def cmd_parse(self, args: str) -> None:
        """Parse project structure."""
        try:
            print("📁 Parsing project structure...")
            
            # Use existing generate_json functionality
            struct_path = os.path.join(self.root_dir, "struct.json")
            success = generate_json(
                input_path=self.root_dir,
                output_path=struct_path,
                include_git=True,
                max_depth=10
            )
            
            if success:
                print(f"✅ Structure parsed and saved to: struct.json")
            else:
                print("❌ Failed to parse project structure")
                
        except Exception as e:
            print(f"Parse error: {e}")

    def cmd_audit(self, args: str) -> None:
        """Handle audit operations."""
        if not args:
            print("Usage: /audit <action>")
            print("Actions: scan, recover, status")
            return
        
        action = args.strip().lower()
        
        try:
            if action == "scan":
                print("🔍 Scanning for missing tasks/ideas...")
                print("Audit scan not fully implemented yet")
            
            elif action == "recover":
                print("🔄 Recovering missing tasks/ideas...")
                print("Audit recovery not fully implemented yet")
            
            elif action == "status":
                print("📊 Audit Status:")
                print("Audit status not fully implemented yet")
            
            else:
                print(f"Unknown audit action: {action}")
                
        except Exception as e:
            print(f"Audit error: {e}")

    def handle_auto_update(self, args: str) -> None:
        """Handle auto-update operations."""
        try:
            print("🔄 Triggering auto-update...")
            
            # Call the parse functionality to update struct.json
            struct_path = os.path.join(self.root_dir, "struct.json")
            success = generate_json(
                input_path=self.root_dir,
                output_path=struct_path,
                include_git=True,
                max_depth=10
            )
            
            if success:
                print(f"✅ Auto-update completed: {struct_path}")
            else:
                print("❌ Auto-update failed")
                
        except Exception as e:
            print(f"Auto-update error: {e}")

    def handle_struct_status(self, args: str) -> None:
        """Handle struct status operations."""
        try:
            struct_path = os.path.join(self.root_dir, "struct.json")
            
            if os.path.exists(struct_path):
                stat_info = os.stat(struct_path)
                print("📋 Struct.json Status:")
                print(f"  Path: {struct_path}")
                print(f"  Size: {stat_info.st_size} bytes")
                print(f"  Modified: {datetime.fromtimestamp(stat_info.st_mtime)}")
                
                # Try to load and show basic info
                try:
                    with open(struct_path, 'r') as f:
                        struct_data = json.load(f)
                    print(f"  Files tracked: {len(struct_data.get('files', []))}")
                    print(f"  Directories: {len(struct_data.get('directories', []))}")
                except json.JSONDecodeError:
                    print("  ⚠️ Invalid JSON format")
            else:
                print("❌ struct.json not found")
                
        except Exception as e:
            print(f"Struct status error: {e}")

    def cmd_context(self, args: str) -> None:
        """Handle context operations."""
        if not args:
            print("Usage: /context <action> [options]")
            print("Actions: get, scenarios, metrics, optimize")
            return
        
        parts = args.strip().split()
        action = parts[0].lower()
        
        try:
            if action == "scenarios":
                print("📋 Available Context Scenarios:")
                scenarios = [
                    "cli_interactive", "cli_query", "vscode_copilot", 
                    "development", "debugging", "documentation"
                ]
                for scenario in scenarios:
                    print(f"  • {scenario}")
            
            elif action == "get":
                if len(parts) < 2:
                    print("Usage: /context get <scenario> [file]")
                    return
                
                scenario = parts[1]
                file_path = parts[2] if len(parts) > 2 else None
                
                print(f"🔍 Getting context for scenario: {scenario}")
                context_data = get_optimized_context(
                    project_root=self.root_dir,
                    scenario=scenario,
                    file_path=file_path
                )
                
                if context_data:
                    metrics = context_data.get("metrics", {})
                    print(f"✅ Context loaded:")
                    print(f"  Sources: {len(context_data.get('sources', {}))}")
                    print(f"  Tokens: {metrics.get('tokens_used', 'unknown')}")
                    print(f"  Load time: {metrics.get('load_time', 'unknown')}s")
                else:
                    print("❌ Failed to get context")
            
            elif action == "metrics":
                print("📊 Context Metrics:")
                print("Context metrics not fully implemented yet")
            
            elif action == "optimize":
                print("⚡ Context Optimization:")
                print("Context optimization not fully implemented yet")
            
            else:
                print(f"Unknown context action: {action}")
                
        except Exception as e:
            print(f"Context error: {e}")

    def cmd_session(self, args: str) -> None:
        """Handle session operations."""
        if not args:
            print("Usage: /session <action> [options]")
            print("Actions: start, switch, status, summary, list")
            return
        
        parts = args.strip().split()
        action = parts[0].lower()
        
        try:
            if action == "status":
                if self.workspace_manager:
                    state = self.workspace_manager.get_current_state()
                    session_id = state.get("active_session", "None")
                    print(f"📋 Session Status:")
                    print(f"  Active Session: {session_id}")
                    print(f"  Mode: {self.workspace_manager.get_mode_status()}")
                else:
                    print("❌ Workspace manager not available")
            
            elif action == "start":
                if len(parts) < 2:
                    print("Usage: /session start <branch_name>")
                    return
                
                branch_name = parts[1]
                session_id = f"SES-{datetime.now().strftime('%m%d%H%M')}"
                
                print(f"🚀 Starting session: {session_id}")
                print(f"   Branch: {branch_name}")
                
                if self.workspace_manager:
                    # Update workspace state with new session
                    state = self.workspace_manager.get_current_state()
                    state["active_session"] = session_id
                    self.workspace_manager.save_state(state)
                    print("✅ Session started and workspace updated")
                
            elif action == "list":
                print("📋 Session List:")
                print("Session listing not fully implemented yet")
            
            elif action == "summary":
                print("📊 Session Summary:")
                print("Session summary not fully implemented yet")
            
            else:
                print(f"Unknown session action: {action}")
                
        except Exception as e:
            print(f"Session error: {e}")
