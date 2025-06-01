#!/usr/bin/env python3
"""
AI Workflow Orchestrator - Integration Layer for Existing llmstruct Architecture
Extends CopilotContextManager and SmartContextOrchestrator instead of duplicating
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import time
import ast
import hashlib

# Import existing llmstruct components instead of duplicating
from .ai_self_awareness import SystemCapabilityDiscovery
from .copilot import CopilotContextManager
from .context_orchestrator import SmartContextOrchestrator
from .parsers.universal_converter import UniversalConverter
from llmstruct.modules.cli.utils import (
    load_config, get_exclude_dirs, get_include_patterns, get_exclude_patterns,
    get_max_file_size, get_struct_file_path, get_context_file_path,
    get_cache_config, get_copilot_config, get_queue_config, get_context_config, save_config
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class SessionType(Enum):
    DEVELOPMENT = "development"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    DEBUGGING = "debugging"
    RESEARCH = "research"


@dataclass
class Task:
    """Structured task representation"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int  # 1-5, 5 = highest
    created_at: str
    updated_at: str
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = None
    dependencies: List[str] = None
    progress_notes: List[str] = None
    related_files: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.progress_notes is None:
            self.progress_notes = []
        if self.related_files is None:
            self.related_files = []


@dataclass
class Session:
    """AI work session with context and goals"""
    id: str
    type: SessionType
    title: str
    description: str
    started_at: str
    ended_at: Optional[str] = None
    goals: List[str] = None
    achievements: List[str] = None
    context_files: List[str] = None
    decisions_made: List[str] = None
    next_steps: List[str] = None
    ai_insights: List[str] = None
    
    def __post_init__(self):
        if self.goals is None:
            self.goals = []
        if self.achievements is None:
            self.achievements = []
        if self.context_files is None:
            self.context_files = []
        if self.decisions_made is None:
            self.decisions_made = []
        if self.next_steps is None:
            self.next_steps = []
        if self.ai_insights is None:
            self.ai_insights = []


class WorkflowOrchestrator:
    """
    Integration layer that extends existing llmstruct architecture
    Uses CopilotContextManager, SmartContextOrchestrator, and struct.json analysis
    """
    
    def __init__(self, project_root: str = ".", debug: bool = False):
        self.project_root = Path(project_root).resolve()
        self.debug = debug
        
        if self.debug:
            print(f"🔧 [DEBUG] Initializing WorkflowOrchestrator at {self.project_root}")
        
        # Use existing llmstruct components
        start_time = time.time()
        
        if self.debug:
            print(f"🔧 [DEBUG] Loading SystemCapabilityDiscovery...")
        self.capability_discovery = SystemCapabilityDiscovery(str(self.project_root))
        
        if self.debug:
            print(f"🔧 [DEBUG] Loading CopilotContextManager...")
        self.copilot_manager = CopilotContextManager(str(self.project_root))
        
        if self.debug:
            print(f"🔧 [DEBUG] Loading SmartContextOrchestrator...")
        self.context_orchestrator = SmartContextOrchestrator(str(self.project_root))
        
        if self.debug:
            print(f"🔧 [DEBUG] Loading config via load_config...")
        self.config = load_config(str(self.project_root))
        
        if self.debug:
            print(f"🔧 [DEBUG] Loading UniversalConverter...")
        self.converter = UniversalConverter()
        
        # Task and session management files
        self.data_dir = self.project_root / "data"
        self.personal_dir = self.project_root / ".personal"
        self.data_dir.mkdir(exist_ok=True)
        self.personal_dir.mkdir(exist_ok=True)
        
        # Current session
        self.current_session: Optional[Session] = None
        
        init_time = time.time() - start_time
        if self.debug:
            print(f"🔧 [DEBUG] Initialization completed in {init_time:.2f}s")
    
    def get_ai_onboarding_guide(self) -> Dict[str, Any]:
        """Generate comprehensive AI onboarding guide using existing architecture"""
        return {
            "project_overview": self._get_project_overview_from_struct(),
            "existing_architecture": self._get_existing_architecture_guide(),
            "workflow_patterns": self._get_workflow_patterns(),
            "copilot_integration": self._get_copilot_integration_guide(),
            "context_orchestration": self._get_context_orchestration_guide(),
            "struct_analysis_approach": self._get_struct_analysis_guide(),
            "available_commands": self._get_available_commands(),
        }
    
    def _get_project_overview_from_struct(self) -> Dict[str, Any]:
        """Get project overview from struct.json analysis"""
        try:
            struct_path = self.project_root / "struct.json"
            if struct_path.exists():
                with open(struct_path, 'r', encoding='utf-8') as f:
                    struct_data = json.load(f)
                
                return {
                    "stats": struct_data.get("metadata", {}).get("stats", {}),
                    "modules": len(struct_data.get("modules", [])),
                    "architecture": self._analyze_architecture_from_struct(struct_data),
                    "key_components": self._identify_key_components(struct_data),
                    "last_analysis": struct_data.get("metadata", {}).get("version", ""),
                }
        except Exception as e:
            logger.warning(f"Failed to load struct.json: {e}")
        
        return {"error": "struct.json not available - run 'llmstruct parse . -o ./struct.json'"}
    
    def _get_existing_architecture_guide(self) -> Dict[str, Any]:
        """Guide to existing llmstruct architecture"""
        return {
            "copilot_context_manager": {
                "description": "4-level context system (Essential, Structural, Operational, Analytical)",
                "usage": "Use copilot_manager.load_context_layer() instead of custom JSON loading",
                "layers": ["init.json", "struct.json", "cli_enhanced.json", "enhanced.json"],
            },
            "smart_context_orchestrator": {
                "description": "Adaptive token budgets and scenario-based context loading",
                "scenarios": ["cli_direct", "cli_interactive", "vscode_copilot", "session_work"],
                "usage": "Use context_orchestrator.load_context() with proper scenario",
            },
            "system_capability_discovery": {
                "description": "Existing AI self-awareness system",
                "usage": "Use capability_discovery.get_comprehensive_status_report()",
                "features": ["Real system metrics", "Cursor integration", "Health monitoring"],
            },
            "cli_config": {
                "description": "Centralized configuration management",
                "usage": "Use cli_config.load_config() instead of custom config loading",
            }
        }
    
    def _get_copilot_integration_guide(self) -> Dict[str, Any]:
        """Guide for proper CopilotContextManager usage"""
        return {
            "initialization": "copilot_manager = CopilotContextManager(project_root)",
            "context_loading": {
                "essential": "copilot_manager.load_context_layer('essential')",
                "structural": "copilot_manager.load_context_layer('structural')",
                "operational": "copilot_manager.load_context_layer('operational')",
                "analytical": "copilot_manager.load_context_layer('analytical')",
            },
            "status_checking": "copilot_manager.get_status()",
            "validation": "copilot_manager.validate_change(file_path, change_type)",
            "export": "copilot_manager.export_context(format='json')",
        }
    
    def _get_context_orchestration_guide(self) -> Dict[str, Any]:
        """Guide for SmartContextOrchestrator usage"""
        return {
            "scenario_based_loading": {
                "vscode_copilot": "context_orchestrator.load_context('vscode_copilot')",
                "cli_interactive": "context_orchestrator.load_context('cli_interactive')",
                "session_work": "context_orchestrator.load_context('session_work')",
            },
            "token_budgets": {
                "FULL": "150,000 tokens for VS Code",
                "FOCUSED": "50,000 tokens for CLI interactive",
                "MINIMAL": "15,000 tokens for direct CLI",
                "SESSION": "30,000 tokens for session work",
            },
            "optimization": "context_orchestrator.optimize_context(feedback)",
        }
    
    def _get_struct_analysis_guide(self) -> Dict[str, Any]:
        """Guide for proper struct.json analysis approach"""
        return {
            "principle": "ALWAYS analyze struct.json before making code changes",
            "workflow": [
                "1. Load struct.json to understand current codebase state",
                "2. Analyze function dependencies and call graphs",
                "3. Check for existing implementations before creating new ones",
                "4. Use struct.json to identify refactoring opportunities",
                "5. Update struct.json after significant changes",
            ],
            "analysis_methods": {
                "find_function": "Search modules[].functions[] for specific function",
                "analyze_dependencies": "Check call_edges for function relationships",
                "identify_duplicates": "Compare function signatures across modules",
                "assess_complexity": "Use stats and call_edges_count for complexity",
            },
            "integration": "Use universal_converter.convert_project() to update struct.json",
        }
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get comprehensive current context using existing architecture"""
        if self.debug:
            print(f"🔧 [DEBUG] Getting current context...")
        
        start_time = time.time()
        
        # Use existing systems instead of custom implementation
        if self.debug:
            print(f"🔧 [DEBUG] Getting copilot status...")
        copilot_status = self.copilot_manager.get_context_status()
        
        if self.debug:
            print(f"🔧 [DEBUG] Getting AI capabilities...")
        
        # Handle both string and dict returns from capability discovery
        try:
            capability_report = self.capability_discovery.get_comprehensive_ai_status()
            # If it's a string, wrap it in a dict
            if isinstance(capability_report, str):
                capability_report = {"status_report": capability_report, "capabilities": []}
        except Exception as e:
            logger.warning(f"Failed to get AI capabilities: {e}")
            capability_report = {"error": str(e), "capabilities": []}
        
        context = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "copilot_status": copilot_status,
            "system_capabilities": capability_report,
            "active_session": self._get_active_session_context(),
            "active_tasks": self.get_active_tasks(),
            "struct_analysis": self._get_struct_analysis(),
            "context_orchestrator_state": self._get_orchestrator_state(),
        }
        
        context_time = time.time() - start_time
        if self.debug:
            print(f"🔧 [DEBUG] Context loaded in {context_time:.2f}s")
        
        return context
    
    def _get_struct_analysis(self) -> Dict[str, Any]:
        """Analyze struct.json for current codebase state"""
        if self.debug:
            print(f"🔧 [DEBUG] Analyzing struct.json...")
        
        start_time = time.time()
        
        try:
            struct_path = self.project_root / "struct.json"
            if not struct_path.exists():
                if self.debug:
                    print(f"🔧 [DEBUG] struct.json not found at {struct_path}")
                return {"error": "struct.json not found - run struct analysis first"}
            
            if self.debug:
                print(f"🔧 [DEBUG] Loading struct.json from {struct_path}")
            
            with open(struct_path, 'r', encoding='utf-8') as f:
                struct_data = json.load(f)
            
            if self.debug:
                modules_count = len(struct_data.get("modules", []))
                print(f"🔧 [DEBUG] Loaded struct.json with {modules_count} modules")
            
            if self.debug:
                print(f"🔧 [DEBUG] Analyzing architecture...")
            arch_analysis = self._analyze_architecture_from_struct(struct_data)
            
            if self.debug:
                print(f"🔧 [DEBUG] Analyzing duplication...")
            dup_analysis = self._analyze_function_duplication(struct_data)
            
            if self.debug:
                print(f"🔧 [DEBUG] Calculating complexity...")
            complexity = self._calculate_complexity_metrics(struct_data)
            
            result = {
                "stats": struct_data.get("metadata", {}).get("stats", {}),
                "architecture_analysis": arch_analysis,
                "duplication_analysis": dup_analysis,
                "complexity_metrics": complexity,
                "last_updated": struct_data.get("metadata", {}).get("version", ""),
            }
            
            analysis_time = time.time() - start_time
            if self.debug:
                print(f"🔧 [DEBUG] Struct analysis completed in {analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze struct.json: {e}")
            if self.debug:
                print(f"🔧 [DEBUG] ERROR in struct analysis: {e}")
            return {"error": str(e)}
    
    def _analyze_architecture_from_struct(self, struct_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze architecture patterns from struct.json"""
        modules = struct_data.get("modules", [])
        
        # Group modules by directory
        directories = {}
        for module in modules:
            path_parts = Path(module["path"]).parts
            if len(path_parts) > 1:
                dir_name = path_parts[-2] if path_parts[-2] != "src" else path_parts[-1]
                if dir_name not in directories:
                    directories[dir_name] = []
                directories[dir_name].append(module)
        
        return {
            "module_distribution": {k: len(v) for k, v in directories.items()},
            "core_components": list(directories.keys()),
            "total_modules": len(modules),
        }
    
    def _analyze_function_duplication(self, struct_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze function duplication across modules"""
        function_names = {}
        modules = struct_data.get("modules", [])
        
        for module in modules:
            module_path = module["path"]
            for func in module.get("functions", []):
                func_name = func["name"]
                if func_name not in function_names:
                    function_names[func_name] = []
                function_names[func_name].append(module_path)
        
        # Find duplicates
        duplicates = {name: paths for name, paths in function_names.items() if len(paths) > 1}
        
        return {
            "total_unique_functions": len(function_names),
            "duplicated_functions": len(duplicates),
            "duplication_details": duplicates,
            "duplication_percentage": len(duplicates) / len(function_names) * 100 if function_names else 0,
        }
    
    def _calculate_complexity_metrics(self, struct_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate complexity metrics from struct.json"""
        stats = struct_data.get("metadata", {}).get("stats", {})
        modules = struct_data.get("modules", [])
        
        # Calculate average functions per module
        total_functions = sum(len(m.get("functions", [])) for m in modules)
        avg_functions_per_module = total_functions / len(modules) if modules else 0
        
        return {
            "modules_count": stats.get("modules_count", 0),
            "functions_count": stats.get("functions_count", 0),
            "classes_count": stats.get("classes_count", 0),
            "call_edges_count": stats.get("call_edges_count", 0),
            "avg_functions_per_module": round(avg_functions_per_module, 2),
            "complexity_score": self._calculate_complexity_score(stats),
        }
    
    def _calculate_complexity_score(self, stats: Dict[str, Any]) -> float:
        """Calculate overall complexity score"""
        modules = stats.get("modules_count", 0)
        functions = stats.get("functions_count", 0)
        call_edges = stats.get("call_edges_count", 0)
        
        if modules == 0:
            return 0.0
        
        # Simple complexity heuristic
        function_density = functions / modules
        interconnectedness = call_edges / functions if functions > 0 else 0
        
        return round((function_density * 0.6 + interconnectedness * 0.4), 2)
    
    def _get_orchestrator_state(self) -> Dict[str, Any]:
        """Get SmartContextOrchestrator state"""
        try:
            # This would need to be implemented in SmartContextOrchestrator
            return {
                "current_scenario": "unknown",
                "loaded_contexts": [],
                "token_budget_used": 0,
                "optimization_level": "standard",
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_codebase_for_duplicates(self, deep_duplicates: str = 'same-name') -> Dict[str, Any]:
        """Analyze codebase for duplicate functions using struct.json (AST/hash analysis by mode)."""
        if self.debug:
            print(f"🔧 [DEBUG] Starting duplication analysis... (deep_mode={deep_duplicates})")
        start_time = time.time()
        struct_analysis = self._get_struct_analysis()
        if "error" in struct_analysis:
            return struct_analysis
        duplication = struct_analysis.get("duplication_analysis", {})
        whitelist = {"main", "__init__", "__post_init__", "run", "setup", "teardown"}
        recommendations = []
        func_bodies = {}  # (func_name, file_path) -> ast_hash
        all_func_bodies = []  # For any-name mode: list of (name, file_path, ast_hash)
        if deep_duplicates in ("same-name", "any-name"):
            for module in struct_analysis.get("modules", []):
                file_path = module.get("path")
                for func in module.get("functions", []):
                    name = func["name"]
                    code = func.get("source")
                    if code:
                        try:
                            tree = ast.parse(code)
                            ast_hash = hashlib.md5(ast.dump(tree).encode()).hexdigest()
                        except Exception:
                            ast_hash = None
                    else:
                        ast_hash = None
                    func_bodies[(name, file_path)] = ast_hash
                    if deep_duplicates == "any-name":
                        all_func_bodies.append((name, file_path, ast_hash))
        if deep_duplicates == "any-name":
            # Группируем все функции по ast_hash независимо от имени
            hash_to_funcs = {}
            for name, file_path, ast_hash in all_func_bodies:
                if not ast_hash:
                    continue
                hash_to_funcs.setdefault(ast_hash, []).append((name, file_path))
            for ast_hash, funcs in hash_to_funcs.items():
                if len(funcs) < 2:
                    continue
                func_names = [f[0] for f in funcs]
                paths = [f[1] for f in funcs]
                dirs = set(p.split(os.sep)[0] for p in paths)
                is_prod = any(d in {"src", "llmstruct"} for d in dirs)
                is_only_tests_or_archive = all(d in {"tests", ".ARCHIVE", "test", "archive"} for d in dirs)
                if is_only_tests_or_archive:
                    continue
                recommendations.append({
                    "function": ", ".join(sorted(set(func_names))),
                    "duplicated_in": paths,
                    "directories": list(dirs),
                    "match_type": "identical_body_any_name",
                    "recommendation": (
                        f"Consider consolidating functions with identical bodies (different names) into a shared utility module"
                        if is_prod else
                        "Duplicate only in tests/archive, refactor if needed"
                    ),
                    "priority": "high" if len(paths) > 3 and is_prod else "medium",
                })
        else:
            for func_name, paths in duplication.get("duplication_details", {}).items():
                dirs = set(p.split(os.sep)[0] for p in paths)
                is_prod = any(d in {"src", "llmstruct"} for d in dirs)
                is_only_tests_or_archive = all(d in {"tests", ".ARCHIVE", "test", "archive"} for d in dirs)
                if func_name in whitelist or is_only_tests_or_archive:
                    continue
                # deep_duplicates: группируем по ast_hash
                if deep_duplicates == "same-name":
                    ast_hashes = [func_bodies.get((func_name, p)) for p in paths]
                    unique_hashes = set(h for h in ast_hashes if h)
                    if len(unique_hashes) == 1 and len(ast_hashes) > 1:
                        match_type = "identical_body"
                    else:
                        match_type = "name_only"
                else:
                    match_type = "name_only"
                recommendations.append({
                    "function": func_name,
                    "duplicated_in": paths,
                    "directories": list(dirs),
                    "match_type": match_type,
                    "recommendation": (
                        f"Consider consolidating {func_name} into a shared utility module (identical bodies)"
                        if match_type == "identical_body" and is_prod else
                        ("Duplicate only in tests/archive, refactor if needed" if not is_prod else "Check if consolidation is needed (name only)")
                    ),
                    "priority": "high" if len(paths) > 3 and is_prod and match_type == "identical_body" else "medium",
                })
        if self.debug:
            print(f"🔧 [DEBUG] Generated {len(recommendations)} recommendations (filtered)")
        result = {
            "analysis": duplication,
            "recommendations": recommendations,
            "next_steps": [
                "Review high-priority duplicates first",
                "Create shared utility modules for common functions (если match_type == 'identical_body' or 'identical_body_any_name')",
                "Update imports after consolidation",
                "Re-run struct analysis to verify improvements",
            ],
            "warning": "⚠️ Анализ дубликатов может содержать ложноположительные срабатывания: совпадение только по имени не всегда означает дублирование кода. Для точного анализа используйте deep_duplicates='same-name' или 'any-name' (AST/хеш-анализ), но даже он не гарантирует 100% точность (например, если код отличается незначительно или есть динамические конструкции)."
        }
        total_time = time.time() - start_time
        if self.debug:
            print(f"🔧 [DEBUG] Duplication analysis completed in {total_time:.2f}s")
        return result
    
    def sync_with_existing_architecture(self) -> Dict[str, bool]:
        """Sync with existing llmstruct architecture instead of duplicating"""
        results = {}
        
        try:
            # Update struct.json using existing converter
            analysis = self.converter.convert_project(str(self.project_root))
            struct_path = self.project_root / "struct.json"
            with open(struct_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            results["struct_update"] = True
        except Exception as e:
            logger.error(f"Failed to update struct.json: {e}")
            results["struct_update"] = False
        
        try:
            # Refresh copilot context layers
            self.copilot_manager.refresh_all_contexts()
            results["copilot_refresh"] = True
        except Exception as e:
            logger.error(f"Failed to refresh copilot contexts: {e}")
            results["copilot_refresh"] = False
        
        return results

    # ... existing code for task and session management ...
    # Keep the task/session methods as they add new functionality
    # rather than duplicating existing features
    
    def create_task(self, title: str, description: str, priority: int = 3, 
                   tags: List[str] = None, dependencies: List[str] = None) -> str:
        """Create new task (this is new functionality, not duplication)"""
        task_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=now,
            updated_at=now,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        # Use existing CLI config for data storage
        tasks_file = self.data_dir / "tasks.json"
        tasks_data = self._load_json_safe(tasks_file)
        if "tasks" not in tasks_data:
            tasks_data["tasks"] = []
        
        tasks_data["tasks"].append(asdict(task))
        self._save_json_safe(tasks_file, tasks_data)
        
        logger.info(f"Created task: {title} (ID: {task_id})")
        return task_id
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        tasks_file = self.data_dir / "tasks.json"
        tasks_data = self._load_json_safe(tasks_file)
        
        if "tasks" in tasks_data:
            return [t for t in tasks_data["tasks"] 
                   if t.get("status") not in ["completed", "cancelled"]]
        return []
    
    def _load_json_safe(self, file_path: Path) -> Dict[str, Any]:
        """Safe JSON loading with error handling"""
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return {}
    
    def _save_json_safe(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Safe JSON saving with error handling"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")
            return False

    # ... rest of session management methods ...
    def _get_active_session_context(self) -> Optional[Dict[str, Any]]:
        """Get current session context"""
        if self.current_session:
            return asdict(self.current_session)
        return None

    def _identify_key_components(self, struct_data: Dict[str, Any]) -> List[str]:
        """Identify key components from struct analysis"""
        modules = struct_data.get("modules", [])
        
        # Identify modules with high function count or many dependencies
        key_components = []
        for module in modules:
            func_count = len(module.get("functions", []))
            if func_count > 10:  # Modules with many functions
                key_components.append(module["path"])
        
        return key_components[:10]  # Top 10 key components

    def _get_workflow_patterns(self) -> Dict[str, Any]:
        """Define workflow patterns that integrate with existing architecture"""
        return {
            "proper_analysis_workflow": {
                "1_struct_analysis": "Always start with struct.json analysis",
                "2_copilot_context": "Load appropriate context via CopilotContextManager",
                "3_capability_check": "Use SystemCapabilityDiscovery for current state",
                "4_implement_changes": "Make changes with existing architecture",
                "5_update_struct": "Update struct.json after changes",
            },
            "avoid_duplication": {
                "check_existing": "Search struct.json for existing implementations",
                "use_existing_systems": "Extend CopilotContextManager, not replace",
                "consolidate_duplicates": "Use duplication analysis to clean up",
            },
            "integration_patterns": {
                "context_loading": "Use context_orchestrator.load_context(scenario)",
                "config_management": "Use cli_config.load_config()",
                "capability_discovery": "Use capability_discovery.get_status()",
            }
        }

    def _get_available_commands(self) -> Dict[str, str]:
        """Available commands that work with existing architecture"""
        return {
            # Analysis Commands (using existing systems)
            "get_current_context()": "Get context via existing CopilotContextManager",
            "analyze_codebase_for_duplicates()": "Find duplicates using struct.json",
            "sync_with_existing_architecture()": "Sync with existing systems",
            
            # Task Management (new functionality)
            "create_task(title, desc, priority)": "Create new task",
            "get_active_tasks()": "Get all active tasks",
            
            # Integration Commands
            "copilot_manager.load_context_layer(layer)": "Load copilot context",
            "context_orchestrator.load_context(scenario)": "Load orchestrated context",
            "capability_discovery.get_status()": "Get system capabilities",
        }


def main():
    """CLI interface that integrates with existing llmstruct architecture"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Workflow Orchestrator - Integration Layer")
    parser.add_argument("command", choices=[
        "onboard", "context", "analyze-duplicates", "sync", "status"
    ])
    parser.add_argument("--deep-duplicates", action="store_true", help="Use AST/хеш-анализ для глубокого поиска дубликатов")
    
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator()
    
    if args.command == "onboard":
        guide = orchestrator.get_ai_onboarding_guide()
        print(json.dumps(guide, indent=2, ensure_ascii=False))
    
    elif args.command == "context":
        context = orchestrator.get_current_context()
        print(json.dumps(context, indent=2, ensure_ascii=False))
    
    elif args.command == "analyze-duplicates":
        analysis = orchestrator.analyze_codebase_for_duplicates(deep_duplicates=getattr(args, "deep_duplicates", False))
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    elif args.command == "sync":
        results = orchestrator.sync_with_existing_architecture()
        print("Sync results:")
        for component, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {component}")
    
    elif args.command == "status":
        context = orchestrator.get_current_context()
        print("System Status:")
        print(f"  Copilot: {context.get('copilot_status', {}).get('status', 'unknown')}")
        print(f"  Capabilities: {len(context.get('system_capabilities', {}).get('capabilities', []))} active")
        print(f"  Active Tasks: {len(context.get('active_tasks', []))}")


if __name__ == "__main__":
    main() 