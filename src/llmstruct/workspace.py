"""
Workspace State & Mode Management System
Enhanced AI-Human Collaboration with Context Boundaries
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Union, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WorkspaceStateManager:
    """
    Core workspace state management with mode-based permissions and context boundaries.
    
    Features:
    - Multi-dimensional mode system ([code][debug], [discuss][meta])
    - Hybrid permission system (capabilities + file restrictions)
    - Smart mode combinations with context awareness
    - Emergency override protocols with time-boxing
    - Integration with existing strict mode system
    """
    
    def __init__(self, workspace_dir: str = "data/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.workspace_dir / "workspace_state.json"
        self.permissions_file = self.workspace_dir / "permissions.json"
        
        # Initialize default state
        self._load_or_create_state()
        self._load_permission_templates()
        
    def _load_or_create_state(self):
        """Load existing workspace state or create default"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "current_mode": [],
                "active_session": None,
                "permissions": {
                    "capabilities": [],
                    "file_restrictions": [],
                    "safe_operations": []
                },
                "context_boundaries": {
                    "focus_files": [],
                    "related_files": [],
                    "restricted_areas": ["config/", ".env", "*.key", "*.secret"]
                },
                "mode_history": [],
                "emergency_overrides": {
                    "active": False,
                    "level": 0,
                    "expires_at": None,
                    "reason": None
                },
                "strict_mode_integration": {
                    "enabled": True,
                    "current_strict_tags": []
                },
                "decision_workflow": {
                    "active_decisions": [],
                    "pending_implementations": []
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            self._save_state()
    
    def _load_permission_templates(self):
        """Load permission templates for different modes"""
        self.permission_templates = {
            # Core modes
            "code": {
                "capabilities": ["filesystem", "execution"],
                "file_restrictions": ["!config/", "!.env", "!*.key"],
                "safe_operations": ["read_files", "write_code", "run_tests", "format_code"]
            },
            "discuss": {
                "capabilities": ["filesystem:read"],
                "file_restrictions": ["!config/", "!.env"],
                "safe_operations": ["read_files", "view_docs", "analyze_structure"]
            },
            "debug": {
                "capabilities": ["filesystem", "execution", "network:local"],
                "file_restrictions": ["!config/", "!.env"],
                "safe_operations": ["read_logs", "run_debug_commands", "inspect_variables"]
            },
            "review": {
                "capabilities": ["filesystem:read"],
                "file_restrictions": ["!.env"],
                "safe_operations": ["read_files", "analyze_code", "suggest_improvements"]
            },
            "meta": {
                "capabilities": ["filesystem"],
                "file_restrictions": ["!.env", "!*.key"],
                "safe_operations": ["read_docs", "write_docs", "manage_structure"]
            },
            "decide": {
                "capabilities": ["filesystem"],
                "file_restrictions": ["!config/", "!.env"],
                "safe_operations": ["read_context", "create_decisions", "track_implementations"]
            },
            
            # Smart combinations (Context-Aware)
            "code+debug": {
                "capabilities": ["filesystem", "execution", "network:local", "debugging"],
                "file_restrictions": ["!config/", "!.env"],
                "safe_operations": ["enhanced_debugging_in_development", "write_code", "run_tests", "run_debug_commands"]
            },
            "discuss+meta": {
                "capabilities": ["filesystem"],
                "file_restrictions": ["!.env"],
                "safe_operations": ["planning_and_documentation", "read_docs", "write_docs", "analyze_structure"]
            },
            "review+security": {
                "capabilities": ["filesystem:read", "security_analysis"],
                "file_restrictions": ["!.env", "!*.key", "!*.secret"],
                "safe_operations": ["security_focused_code_review", "read_files", "analyze_code"]
            }
        }
    
    def set_mode(self, modes: Union[str, List[str]], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Set workspace mode(s) with smart combination logic.
        
        Args:
            modes: Single mode string "[code]" or list of modes ["code", "debug"]
            session_id: Optional session identifier
            
        Returns:
            Dict with mode change result and applied permissions
        """
        # Parse modes from string format if needed
        if isinstance(modes, str):
            modes = self._parse_modes_from_string(modes)
        
        # Record previous mode for history
        previous_mode = self.state["current_mode"].copy()
        
        # Apply smart combination logic
        combined_permissions = self._combine_mode_permissions(modes)
        
        # Update state
        self.state["current_mode"] = modes
        if session_id:
            self.state["active_session"] = session_id
        
        self.state["permissions"] = combined_permissions
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Add to history
        if previous_mode:
            self.state["mode_history"].append({
                "mode": previous_mode,
                "session": self.state.get("active_session"),
                "ended_at": datetime.now(timezone.utc).isoformat()
            })
        
        self._save_state()
        
        return {
            "success": True,
            "previous_mode": previous_mode,
            "current_mode": modes,
            "permissions": combined_permissions,
            "restrictions_applied": len(combined_permissions.get("file_restrictions", [])),
            "mode_combination": self._get_mode_combination_name(modes)
        }
    
    def _parse_modes_from_string(self, mode_string: str) -> List[str]:
        """Parse modes from string like '[code][debug]' to ['code', 'debug']"""
        import re
        modes = re.findall(r'\[([^\]]+)\]', mode_string)
        return modes
    
    def _combine_mode_permissions(self, modes: List[str]) -> Dict[str, Any]:
        """
        Smart combination of mode permissions (Decision: C - Smart Combination)
        """
        if not modes:
            return self.permission_templates.get("discuss", {}).copy()
        
        # Check for predefined smart combinations first
        combination_key = "+".join(sorted(modes))
        if combination_key in self.permission_templates:
            logger.info(f"Using smart combination template: {combination_key}")
            return self.permission_templates[combination_key].copy()
        
        # Fall back to intelligent merging
        combined = {
            "capabilities": set(),
            "file_restrictions": set(),
            "safe_operations": set()
        }
        
        for mode in modes:
            if mode in self.permission_templates:
                template = self.permission_templates[mode]
                combined["capabilities"].update(template.get("capabilities", []))
                combined["file_restrictions"].update(template.get("file_restrictions", []))
                combined["safe_operations"].update(template.get("safe_operations", []))
        
        # Convert sets back to lists
        return {
            "capabilities": list(combined["capabilities"]),
            "file_restrictions": list(combined["file_restrictions"]),
            "safe_operations": list(combined["safe_operations"])
        }
    
    def _get_mode_combination_name(self, modes: List[str]) -> str:
        """Get descriptive name for mode combination"""
        if not modes:
            return "default"
        
        combination_key = "+".join(sorted(modes))
        combination_names = {
            "code+debug": "Enhanced Debugging in Development",
            "discuss+meta": "Planning and Documentation",
            "review+security": "Security-Focused Code Review",
            "code+review": "Development with Review",
            "discuss+decide": "Decision-Making Discussion"
        }
        
        return combination_names.get(combination_key, f"Custom: {'+'.join(modes)}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current workspace state"""
        return self.state.copy()
    
    def check_permission(self, operation: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if operation is permitted under current mode.
        
        Args:
            operation: Operation type (e.g., "write_file", "run_command")
            target: Optional target (file path, command, etc.)
            
        Returns:
            Dict with permission result and reasoning
        """
        permissions = self.state["permissions"]
        
        # Check if operation is in safe_operations (auto-granted)
        if operation in permissions.get("safe_operations", []):
            return {
                "allowed": True,
                "reason": "Operation in safe_operations list",
                "auto_granted": True
            }
        
        # Check emergency overrides first (they can bypass file restrictions)
        if self._check_emergency_override():
            override_level = self.state["emergency_overrides"]["level"]
            # Level 2+ can bypass file restrictions, Level 1 still respects them
            if override_level >= 2:
                return {
                    "allowed": True,
                    "reason": f"Emergency override L{override_level} bypasses all restrictions",
                    "override_level": override_level,
                    "bypass_restrictions": True
                }
            elif override_level == 1 and not self._is_restricted_target(target):
                return {
                    "allowed": True,
                    "reason": f"Emergency override L{override_level} active (non-restricted target)",
                    "override_level": override_level,
                    "bypass_restrictions": False
                }
        
        # Check capability requirements
        required_capability = self._get_required_capability(operation)
        if required_capability:
            if required_capability in permissions.get("capabilities", []):
                # Check file restrictions if target is provided
                if target and self._is_restricted_target(target):
                    return {
                        "allowed": False,
                        "reason": f"Target {target} is in restricted areas",
                        "restrictions": permissions.get("file_restrictions", [])
                    }
                
                return {
                    "allowed": True,
                    "reason": f"Capability {required_capability} granted",
                    "capability_based": True
                }
        
        # Default: require approval (AI Override Authority: C - Permissive with limits)
        return {
            "allowed": False,
            "reason": "Operation requires explicit permission",
            "requires_approval": True,
            "suggested_action": f"Request permission for {operation} operation"
        }
    
    def _get_required_capability(self, operation: str) -> Optional[str]:
        """Map operations to required capabilities"""
        capability_map = {
            "read_file": "filesystem",
            "write_file": "filesystem",
            "run_command": "execution",
            "run_test": "execution",
            "fetch_url": "network",
            "install_package": "execution",
            "debug_process": "debugging"
        }
        
        for op_prefix, capability in capability_map.items():
            if operation.startswith(op_prefix):
                return capability
        
        return None
    
    def _is_restricted_target(self, target: str) -> bool:
        """Check if target matches any file restrictions"""
        restrictions = self.state["permissions"].get("file_restrictions", [])
        
        import fnmatch
        for restriction in restrictions:
            # Handle negation (!)
            if restriction.startswith("!"):
                pattern = restriction[1:]
                if fnmatch.fnmatch(target, pattern) or target.startswith(pattern):
                    return True
        
        return False
    
    def set_emergency_override(self, level: int = 1, reason: str = "", duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Grant emergency override (Hybrid B+C: Escalation + Time-boxing)
        
        Args:
            level: Override level (1=extend permissions, 2=filesystem, 3=system)
            reason: Reason for override
            duration_minutes: Override duration
        """
        if level not in [1, 2, 3]:
            return {"success": False, "error": "Invalid override level"}
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        
        self.state["emergency_overrides"] = {
            "active": True,
            "level": level,
            "expires_at": expires_at.isoformat(),
            "reason": reason,
            "granted_at": datetime.now(timezone.utc).isoformat()
        }
        
        self._save_state()
        
        return {
            "success": True,
            "level": level,
            "expires_in_minutes": duration_minutes,
            "reason": reason
        }
    
    def _check_emergency_override(self) -> bool:
        """Check if emergency override is active and not expired"""
        override = self.state["emergency_overrides"]
        
        if not override.get("active"):
            return False
        
        expires_at = override.get("expires_at")
        if expires_at and datetime.now(timezone.utc) > datetime.fromisoformat(expires_at):
            # Override expired
            self.state["emergency_overrides"]["active"] = False
            self._save_state()
            return False
        
        return True
    
    def integrate_strict_mode(self, strict_tags: List[str]):
        """Integration with existing strict mode system"""
        self.state["strict_mode_integration"]["current_strict_tags"] = strict_tags
        self.state["strict_mode_integration"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
    
    def add_decision_workflow(self, decision_id: str, decision_data: Dict[str, Any]):
        """Add decision to workflow tracking (for [decide] mode)"""
        self.state["decision_workflow"]["active_decisions"].append({
            "id": decision_id,
            "data": decision_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        self._save_state()
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Get comprehensive workspace status for debugging and display"""
        override = self.state["emergency_overrides"]
        
        return {
            "current_mode": self.state["current_mode"],
            "mode_combination": self._get_mode_combination_name(self.state["current_mode"]),
            "active_session": self.state.get("active_session"),
            "permissions": {
                "capabilities": self.state["permissions"].get("capabilities", []),
                "file_restrictions": self.state["permissions"].get("file_restrictions", []),
                "safe_operations_count": len(self.state["permissions"].get("safe_operations", []))
            },
            "emergency_override": {
                "active": override.get("active", False),
                "level": override.get("level", 0),
                "reason": override.get("reason", ""),
                "expires_at": override.get("expires_at"),
                "time_remaining": self._get_override_time_remaining() if override.get("active") else None
            },
            "mode_history_count": len(self.state.get("mode_history", [])),
            "last_updated": self.state.get("last_updated")
        }
    
    def _get_override_time_remaining(self) -> Optional[str]:
        """Get formatted time remaining for emergency override"""
        override = self.state["emergency_overrides"]
        if not override.get("active") or not override.get("expires_at"):
            return None
        
        from datetime import datetime, timezone
        expires_at = datetime.fromisoformat(override["expires_at"])
        now = datetime.now(timezone.utc)
        
        if expires_at <= now:
            return "EXPIRED"
        
        remaining = expires_at - now
        minutes = int(remaining.total_seconds() / 60)
        return f"{minutes} minutes"
    
    def _save_state(self):
        """Save current state to file"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def get_mode_status(self) -> str:
        """Get formatted status string for CLI display"""
        modes = self.state["current_mode"]
        if not modes:
            return "No active mode"
        
        mode_str = "".join(f"[{mode}]" for mode in modes)
        combination = self._get_mode_combination_name(modes)
        
        override = self.state["emergency_overrides"]
        override_str = ""
        if override.get("active"):
            override_str = f" 🚨 Emergency Override L{override['level']}"
        
        return f"{mode_str} - {combination}{override_str}"


def create_workspace_manager(workspace_dir: str = "data/workspace") -> WorkspaceStateManager:
    """Factory function to create workspace manager"""
    return WorkspaceStateManager(workspace_dir)
