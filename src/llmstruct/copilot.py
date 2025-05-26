"""
LLMStruct Copilot Integration Module
Provides context-aware development assistance with hybrid copilot capabilities.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from llmstruct.cache import JSONCache
from llmstruct.context_orchestrator import SmartContextOrchestrator, create_context_orchestrator

# Configure logging
logger = logging.getLogger(__name__)


class ContextLayer(Enum):
    """Context layer priorities for copilot integration."""

    ESSENTIAL = 1
    STRUCTURAL = 2
    OPERATIONAL = 3
    ANALYTICAL = 4


class AttachMode(Enum):
    """Context attachment modes."""

    AUTO = "auto"
    ON_EDIT = "on_code_edit"
    ON_REQUEST = "on_request"
    SMART = "smart"


@dataclass
class ContextLayerConfig:
    """Configuration for a context layer."""

    priority: int
    auto_attach: Union[bool, str]
    sources: List[str]
    description: str
    loaded: bool = False
    last_accessed: Optional[float] = None


@dataclass
class CopilotEvent:
    """Represents a copilot event for context triggering."""

    event_type: str
    file_path: Optional[str] = None
    scope: str = "local"
    metadata: Dict[str, Any] = None


class CopilotContextManager:
    """
    Manages context layers and integration with GitHub Copilot.
    Provides intelligent context loading and workflow assistance.
    """

    def __init__(self, project_root: str = None, config_path: str = None):
        """
        Initialize the Copilot Context Manager.

        Args:
            project_root: Project root directory
            config_path: Path to copilot_init.json
        """
        self.project_root = Path(project_root or os.getcwd())
        self.config_path = (
            config_path or self.project_root / "data" / "copilot_init.json"
        )

        self.config: Dict[str, Any] = {}
        self.context_layers: Dict[str, ContextLayerConfig] = {}
        self.cache = JSONCache()
        self.active_contexts: Dict[str, Any] = {}
        
        # Initialize Smart Context Orchestrator
        self.context_orchestrator = create_context_orchestrator(str(self.project_root))

        self._load_config()
        self._initialize_layers()

    def _load_config(self) -> None:
        """Load copilot configuration from JSON file."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                logger.info(f"Loaded copilot config from {self.config_path}")
            else:
                logger.warning(f"Copilot config not found at {self.config_path}")
                self.config = {"copilot_init": {}}
        except Exception as e:
            logger.error(f"Failed to load copilot config: {e}")
            self.config = {"copilot_init": {}}

    def _initialize_layers(self) -> None:
        """Initialize context layers from configuration."""
        layers_config = self.config.get("copilot_init", {}).get("context_layers", {})

        for layer_name, layer_config in layers_config.items():
            self.context_layers[layer_name] = ContextLayerConfig(
                priority=layer_config.get("priority", 99),
                auto_attach=layer_config.get("auto_attach", False),
                sources=layer_config.get("sources", []),
                description=layer_config.get("description", ""),
            )

    def load_context_layer(self, layer_name: str, force: bool = False) -> bool:
        """
        Load a specific context layer.

        Args:
            layer_name: Name of the layer to load
            force: Force reload if already loaded

        Returns:
            bool: True if successful
        """
        if layer_name not in self.context_layers:
            logger.error(f"Unknown context layer: {layer_name}")
            return False

        layer = self.context_layers[layer_name]

        if layer.loaded and not force:
            logger.debug(f"Layer {layer_name} already loaded")
            return True

        try:
            layer_context = {}

            for source in layer.sources:
                source_path = self.project_root / source
                if source_path.exists():
                    with open(source_path, "r", encoding="utf-8") as f:
                        source_data = json.load(f)
                        layer_context[source] = source_data
                else:
                    logger.warning(f"Source file not found: {source_path}")

            self.active_contexts[layer_name] = layer_context
            layer.loaded = True
            layer.last_accessed = time.time()

            logger.info(f"Loaded context layer: {layer_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load context layer {layer_name}: {e}")
            return False

    def unload_context_layer(self, layer_name: str) -> bool:
        """
        Unload a context layer to free memory.

        Args:
            layer_name: Name of the layer to unload

        Returns:
            bool: True if successful
        """
        if layer_name in self.active_contexts:
            del self.active_contexts[layer_name]

        if layer_name in self.context_layers:
            self.context_layers[layer_name].loaded = False
            logger.info(f"Unloaded context layer: {layer_name}")
            return True

        return False

    def get_optimized_context(
        self, 
        scenario: str, 
        file_path: str = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """
        Get optimized context using Smart Context Orchestrator.
        
        Args:
            scenario: Usage scenario (vscode_copilot, cli_direct, etc.)
            file_path: Optional file path for focused context
            max_tokens: Optional token limit override
            
        Returns:
            Optimized context dictionary
        """
        try:
            # Map scenario to context orchestrator scenarios
            scenario_mapping = {
                "vscode_copilot": "vscode_copilot",
                "cli_direct": "cli_direct", 
                "session_work": "session_work",
                "quick_operation": "quick_operation"
            }
            
            mapped_scenario = scenario_mapping.get(scenario, "vscode_copilot")
            
            context = self.context_orchestrator.get_context_for_scenario(
                scenario=mapped_scenario,
                file_path=file_path,
                custom_budget=None if not max_tokens else {
                    "max_tokens": max_tokens,
                    "priority_files": [],
                    "essential_sections": []
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get optimized context: {e}")
            # Fallback to legacy context loading
            return self._get_legacy_context()

    def _get_legacy_context(self) -> Dict[str, Any]:
        """Fallback to legacy context loading."""
        context = {}
        
        # Load essential layer as fallback
        if self.load_context_layer("essential"):
            context = self.active_contexts.get("essential", {})
            
        return context

    def get_context_for_vscode(self, file_path: str = None) -> Dict[str, Any]:
        """
        Get optimized context specifically for VS Code Copilot integration.
        
        Args:
            file_path: Optional file path for focused context
            
        Returns:
            Token-optimized context for VS Code
        """
        return self.get_optimized_context(
            scenario="vscode_copilot",
            file_path=file_path,
            max_tokens=2000  # VS Code Copilot token limit
        )
    def get_context_for_event(self, event: CopilotEvent) -> Dict[str, Any]:
        """
        Get relevant context for a copilot event using Smart Context Orchestrator.

        Args:
            event: The copilot event

        Returns:
            Dict containing relevant context
        """
        try:
            # Determine scenario based on event type
            scenario_mapping = {
                "file_create": "vscode_copilot",
                "file_edit": "vscode_copilot", 
                "file_delete": "vscode_copilot",
                "function_creation": "vscode_copilot",
                "class_creation": "vscode_copilot",
                "import_changes": "vscode_copilot",
                "cli_command_detected": "cli_direct",
                "queue_operation": "session_work",
                "task_creation": "session_work"
            }
            
            scenario = scenario_mapping.get(event.event_type, "vscode_copilot")
            
            # Get optimized context using orchestrator
            context = self.get_optimized_context(
                scenario=scenario,
                file_path=event.file_path
            )
            
            # Add event-specific metadata
            context["event_metadata"] = {
                "event_type": event.event_type,
                "file_path": event.file_path,
                "scope": event.scope,
                "metadata": event.metadata
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for event {event.event_type}: {e}")
            return self._get_legacy_event_context(event)

    def _get_legacy_event_context(self, event: CopilotEvent) -> Dict[str, Any]:
        """Legacy event context loading as fallback."""
        context = {}

        # Get triggers configuration
        triggers = self.config.get("copilot_init", {}).get("copilot_triggers", {})

        # Check file operation triggers
        if event.event_type in ["file_create", "file_edit", "file_delete"]:
            file_triggers = triggers.get("file_operations", {}).get(
                f"on_{event.event_type}", {}
            )
            layers_to_load = file_triggers.get("layers", [])

            for layer_name in layers_to_load:
                if self.load_context_layer(layer_name):
                    context[layer_name] = self.active_contexts.get(layer_name, {})

        # Check code event triggers
        elif event.event_type in [
            "function_creation",
            "class_creation",
            "import_changes",
        ]:
            code_triggers = triggers.get("code_events", {}).get(event.event_type, {})
            layers_to_attach = code_triggers.get("attach_context", [])

            for layer_name in layers_to_attach:
                if self.load_context_layer(layer_name):
                    context[layer_name] = self.active_contexts.get(layer_name, {})

        # Check workflow triggers
        elif event.event_type in [
            "cli_command_detected",
            "queue_operation",
            "task_creation",
        ]:
            workflow_triggers = triggers.get("workflow_triggers", {}).get(
                event.event_type, {}
            )
            context_sources = workflow_triggers.get("context_sources", [])

            # Load specific sources for workflow events
            for source in context_sources:
                source_path = self.project_root / source
                if source_path.exists():
                    try:
                        with open(source_path, "r", encoding="utf-8") as f:
                            context[source] = json.load(f)
                    except Exception as e:
                        logger.error(f"Failed to load {source}: {e}")

        return context

    def suggest_completion(
        self, current_code: str, file_path: str, cursor_position: int
    ) -> List[str]:
        """
        Generate context-aware code completions.

        Args:
            current_code: Current code content
            file_path: Path to the current file
            cursor_position: Cursor position in the code

        Returns:
            List of completion suggestions
        """
        suggestions = []

        # Load essential context
        self.load_context_layer("essential")

        # Get struct.json for function signatures and imports
        struct_context = self.active_contexts.get("essential", {}).get(
            "struct.json", {}
        )

        if struct_context:
            # Extract current module info
            relative_path = str(Path(file_path).relative_to(self.project_root))
            current_module = None

            for module in struct_context.get("modules", []):
                if module.get("path") == relative_path:
                    current_module = module
                    break

            if current_module:
                # Suggest function completions
                for func in current_module.get("functions", []):
                    suggestions.append(
                        f"def {func['name']}({', '.join(func.get('parameters', []))})"
                    )

                # Suggest import completions
                for dep in current_module.get("dependencies", []):
                    suggestions.append(f"import {dep}")

        return suggestions[:5]  # Limit to top 5 suggestions

    def validate_change(self, file_path: str, change_type: str) -> Dict[str, Any]:
        """
        Validate a code change against safety rules.

        Args:
            file_path: Path to the changed file
            change_type: Type of change (create, edit, delete)

        Returns:
            Dict with validation results
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
        }

        # Get validation rules from config
        safety_features = self.config.get("copilot_init", {}).get("safety_features", {})
        validation_rules = safety_features.get("validation_rules", [])

        for rule in validation_rules:
            rule_name = rule.get("rule")
            scope = rule.get("scope", "**/*")
            trigger = rule.get("trigger", "on_save")

            # Check if rule applies to this file and change type
            if self._matches_scope(file_path, scope) and self._matches_trigger(
                change_type, trigger
            ):

                if rule_name == "validate_json_schema":
                    result = self._validate_json_schema(file_path)
                    validation_result["warnings"].extend(result.get("warnings", []))
                    validation_result["errors"].extend(result.get("errors", []))

                elif rule_name == "check_circular_dependencies":
                    result = self._check_circular_dependencies(file_path)
                    validation_result["warnings"].extend(result.get("warnings", []))

                elif rule_name == "validate_task_references":
                    result = self._validate_task_references(file_path)
                    validation_result["errors"].extend(result.get("errors", []))

        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result

    def _matches_scope(self, file_path: str, scope: str) -> bool:
        """Check if file matches scope pattern."""
        from fnmatch import fnmatch

        relative_path = str(Path(file_path).relative_to(self.project_root))
        return fnmatch(relative_path, scope)

    def _matches_trigger(self, change_type: str, trigger: str) -> bool:
        """Check if change type matches trigger."""
        trigger_map = {
            "on_save": ["edit"],
            "on_create": ["create"],
            "on_delete": ["delete"],
            "on_import_change": ["edit"],
            "on_task_update": ["edit"],
        }
        return change_type in trigger_map.get(trigger, [])

    def _validate_json_schema(self, file_path: str) -> Dict[str, Any]:
        """Validate JSON file against schema."""
        result = {"warnings": [], "errors": []}

        if not file_path.endswith(".json"):
            return result

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)  # Basic JSON validation
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON syntax: {e}")
        except Exception as e:
            result["warnings"].append(f"Could not validate JSON: {e}")

        return result

    def _check_circular_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Check for circular dependencies."""
        result = {"warnings": []}

        # Load struct.json for dependency analysis
        self.load_context_layer("essential")
        struct_data = self.active_contexts.get("essential", {}).get("struct.json", {})

        if struct_data:
            # Simple circular dependency check
            modules = struct_data.get("modules", [])
            relative_path = str(Path(file_path).relative_to(self.project_root))

            for module in modules:
                if module.get("path") == relative_path:
                    dependencies = module.get("dependencies", [])
                    # This is a simplified check - a full implementation would
                    # build a dependency graph and detect cycles
                    if len(dependencies) > 10:
                        result["warnings"].append(
                            f"Module has many dependencies ({len(dependencies)}), "
                            "consider refactoring to reduce coupling"
                        )
                    break

        return result

    def _validate_task_references(self, file_path: str) -> Dict[str, Any]:
        """Validate task references in tasks.json."""
        result = {"errors": []}

        if not file_path.endswith("tasks.json"):
            return result

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            # Validate task structure
            tasks = tasks_data.get("tasks", [])
            task_ids = set()

            for task in tasks:
                task_id = task.get("id")
                if not task_id:
                    result["errors"].append("Task missing required 'id' field")
                elif task_id in task_ids:
                    result["errors"].append(f"Duplicate task ID: {task_id}")
                else:
                    task_ids.add(task_id)

        except Exception as e:
            result["errors"].append(f"Failed to validate tasks: {e}")

        return result

    def get_workflow_suggestions(self, command: str) -> List[str]:
        """
        Get workflow suggestions based on current command context.

        Args:
            command: Current command or operation

        Returns:
            List of workflow suggestions
        """
        suggestions = []

        # Load operational context for workflows
        self.load_context_layer("operational")

        cli_queue_data = self.active_contexts.get("operational", {}).get(
            "data/cli_queue_enhanced.json", {}
        )

        if cli_queue_data and "queue_workflows" in cli_queue_data:
            workflows = cli_queue_data["queue_workflows"]

            # Find matching workflows
            for workflow_name, workflow in workflows.items():
                if command.lower() in workflow.get("description", "").lower():
                    steps = workflow.get("steps", [])
                    if steps:
                        suggestions.append(f"Workflow: {workflow_name}")
                        suggestions.extend([f"  - {step}" for step in steps[:3]])

        return suggestions

    def refresh_all_contexts(self) -> bool:
        """
        Refresh all loaded context layers.

        Returns:
            bool: True if successful
        """
        success = True

        for layer_name in list(self.active_contexts.keys()):
            if not self.load_context_layer(layer_name, force=True):
                success = False

        logger.info("Refreshed all context layers")
        return success

    def get_context_status(self) -> Dict[str, Any]:
        """
        Get status of all context layers.

        Returns:
            Dict with context status information
        """
        status = {
            "loaded_layers": [],
            "available_layers": list(self.context_layers.keys()),
            "memory_usage": {},
            "last_accessed": {},
        }

        for layer_name, layer in self.context_layers.items():
            if layer.loaded:
                status["loaded_layers"].append(layer_name)

            if layer.last_accessed:
                status["last_accessed"][layer_name] = layer.last_accessed

        return status

    def export_context(self, layers: List[str] = None, format: str = "json") -> str:
        """
        Export context in specified format.

        Args:
            layers: List of layers to export (None for all loaded)
            format: Export format (json, yaml, etc.)

        Returns:
            Exported context as string
        """
        if layers is None:
            layers = list(self.active_contexts.keys())

        export_data = {}
        for layer_name in layers:
            if layer_name in self.active_contexts:
                export_data[layer_name] = self.active_contexts[layer_name]

        if format == "json":
            return json.dumps(export_data, indent=2)
        else:
            return str(export_data)

    def close(self) -> None:
        """Clean up resources."""
        if self.cache:
            self.cache.close()
        self.active_contexts.clear()
        
        # Close context orchestrator if it has cleanup methods
        if hasattr(self.context_orchestrator, 'close'):
            self.context_orchestrator.close()
            
        logger.info("Copilot context manager closed")


# Convenience functions for copilot integration


def initialize_copilot(project_root: str = None) -> CopilotContextManager:
    """
    Initialize copilot context manager for the project.

    Args:
        project_root: Project root directory

    Returns:
        Configured CopilotContextManager instance
    """
    return CopilotContextManager(project_root)


def trigger_copilot_event(
    manager: CopilotContextManager, event_type: str, file_path: str = None, **kwargs
) -> Dict[str, Any]:
    """
    Trigger a copilot event and get relevant context.

    Args:
        manager: CopilotContextManager instance
        event_type: Type of event
        file_path: Optional file path
        **kwargs: Additional event metadata

    Returns:
        Dict with event context
    """
    event = CopilotEvent(event_type=event_type, file_path=file_path, metadata=kwargs)

    return manager.get_context_for_event(event)


def smart_suggest(
    manager: CopilotContextManager, query: str, context: str = "code"
) -> List[str]:
    """
    Get smart suggestions based on query and context.

    Args:
        manager: CopilotContextManager instance
        query: Query string
        context: Context type (code, workflow, task, etc.)

    Returns:
        List of suggestions
    """
    if context == "workflow":
        return manager.get_workflow_suggestions(query)
    elif context == "code":
        # This would integrate with actual copilot for code suggestions
        return [f"Code suggestion for: {query}"]
    else:
        return [f"General suggestion for: {query}"]


def get_optimized_context_for_scenario(
    project_root: str,
    scenario: str, 
    file_path: str = None,
    max_tokens: int = None
) -> Dict[str, Any]:
    """
    Get optimized context for specific scenario - standalone function.
    
    Args:
        project_root: Project root directory
        scenario: Usage scenario (vscode_copilot, cli_direct, etc.)
        file_path: Optional file path for focused context
        max_tokens: Optional token limit override
        
    Returns:
        Optimized context dictionary
    """
    try:
        manager = initialize_copilot(project_root)
        return manager.get_optimized_context(scenario, file_path, max_tokens)
    finally:
        if 'manager' in locals():
            manager.close()
