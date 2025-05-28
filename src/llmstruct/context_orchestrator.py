"""
Smart Context Orchestration for LLMStruct
Optimizes context loading for different LLM usage scenarios
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import time

logger = logging.getLogger(__name__)


class ContextMode(Enum):
    """Context loading modes for different scenarios."""
    FULL = "full"           # Для прямых CLI вызовов - полный контекст
    FOCUSED = "focused"     # Для VS Code Copilot - фокусированный контекст
    MINIMAL = "minimal"     # Для быстрых операций - минимальный контекст
    SESSION = "session"     # Для сессионной работы - контекст сессии


class ContextLevel(Enum):
    """Progressive context levels with token budgets."""
    CORE = (0, 500)         # < 500 tokens
    ESSENTIAL = (1, 2000)   # < 2000 tokens
    COMPREHENSIVE = (2, 8000)  # < 8000 tokens
    FULL = (3, None)        # unlimited


@dataclass
class ContextBudget:
    """Token budget configuration for context loading."""
    max_tokens: Optional[int]
    priority_files: List[str]
    essential_sections: List[str]
    exclude_sections: List[str] = None


@dataclass
class ContextMetrics:
    """Metrics for context loading performance."""
    tokens_used: int
    files_loaded: int
    load_time: float
    cache_hit_rate: float


class SmartContextOrchestrator:
    """
    Orchestrates context loading based on usage scenario and token budget.
    Provides optimized context for different LLM integration patterns.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cache = {}
        self.metrics = {}
        
        # Load configuration
        self.config = self._load_config()
        
        # Context sources mapping
        self.context_sources = {
            "init": "data/init.json",
            "struct": "struct.json", 
            "tasks": "data/tasks.json",
            "ideas": "data/ideas.json",
            "insights": "data/insights.json",
            "sessions": "data/sessions/ai_sessions.json",
            "current_session": "data/sessions/current_session.json",
            "worklog": "data/sessions/worklog.json"
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load context orchestration configuration."""
        config_path = self.project_root / "data" / "context_orchestration.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "scenarios": {
                "cli_direct": {
                    "mode": "FULL",
                    "budget": {"max_tokens": None}
                },
                "vscode_copilot": {
                    "mode": "FOCUSED", 
                    "budget": {"max_tokens": 2000}
                },
                "session_work": {
                    "mode": "SESSION",
                    "budget": {"max_tokens": 4000}
                }
            },
            "context_levels": {
                "CORE": {
                    "sources": ["init", "current_session"],
                    "sections": ["summary", "goals", "current_focus"]
                },
                "ESSENTIAL": {
                    "sources": ["init", "struct", "current_session", "tasks"],
                    "sections": ["summary", "structure", "active_tasks", "current_session"]
                },
                "COMPREHENSIVE": {
                    "sources": ["init", "struct", "tasks", "ideas", "current_session"],
                    "sections": ["all"]
                },
                "FULL": {
                    "sources": ["all"],
                    "sections": ["all"]
                }
            }
        }
    
    def get_context_for_scenario(
        self, 
        scenario: str, 
        file_path: str = None,
        custom_budget: Optional[ContextBudget] = None
    ) -> Dict[str, Any]:
        """
        Get optimized context for specific usage scenario.
        
        Args:
            scenario: Usage scenario (cli_direct, vscode_copilot, etc.)
            file_path: Optional file path for focused context
            custom_budget: Optional custom token budget
            
        Returns:
            Optimized context dictionary
        """
        start_time = time.time()
        
        # Get scenario configuration
        scenario_config = self.config["scenarios"].get(scenario, {})
        mode = ContextMode(scenario_config.get("mode", "FOCUSED"))
        
        # Determine budget
        budget = custom_budget or self._get_budget_for_scenario(scenario_config)
        
        # Load context based on mode
        if mode == ContextMode.FULL:
            context = self._load_full_context()
        elif mode == ContextMode.FOCUSED:
            context = self._load_focused_context(file_path, budget)
        elif mode == ContextMode.SESSION:
            context = self._load_session_context(budget)
        else:  # MINIMAL
            context = self._load_minimal_context()
        
        # Calculate metrics
        load_time = time.time() - start_time
        self._update_metrics(scenario, context, load_time)
        
        return context
    
    def _get_budget_for_scenario(self, scenario_config: Dict[str, Any]) -> ContextBudget:
        """Create budget configuration for scenario."""
        budget_config = scenario_config.get("budget", {})
        
        return ContextBudget(
            max_tokens=budget_config.get("max_tokens"),
            priority_files=budget_config.get("priority_files", []),
            essential_sections=budget_config.get("essential_sections", []),
            exclude_sections=budget_config.get("exclude_sections", [])
        )
    
    def _load_full_context(self) -> Dict[str, Any]:
        """Load complete context without token restrictions."""
        context = {"mode": "full", "sources": {}}
        
        for source_name, source_path in self.context_sources.items():
            full_path = self.project_root / source_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        context["sources"][source_name] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load {source_name}: {e}")
        
        return context
    
    def _extract_relationship_summary(self, max_modules: int = 15) -> Dict[str, Any]:
        """
        Извлекает краткий граф связей между модулями из struct.json:
        - module_id, path
        - dependencies (только имена модулей)
        - публичные классы/функции
        """
        struct_path = self.project_root / "struct.json"
        if not struct_path.exists():
            return {}
        try:
            with open(struct_path, "r", encoding="utf-8") as f:
                struct = json.load(f)
            modules = struct.get("modules", [])
            summary = []
            for m in modules[:max_modules]:
                entry = {
                    "module_id": m.get("module_id"),
                    "path": m.get("path"),
                    "dependencies": m.get("dependencies", [])[:8],
                    "public_functions": [fn["name"] for fn in m.get("functions", []) if not fn["name"].startswith("_")][:5],
                    "public_classes": [cl["name"] for cl in m.get("classes", []) if not cl["name"].startswith("_")][:3]
                }
                summary.append(entry)
            return {"modules": summary}
        except Exception as e:
            logger.warning(f"Failed to extract relationship summary: {e}")
            return {}

    def _load_focused_context(
        self, 
        file_path: str = None, 
        budget: ContextBudget = None
    ) -> Dict[str, Any]:
        """
        Load focused context optimized for VS Code Copilot.
        - Всегда включает summary из init.json (уровень 1)
        - relationship_context (structural) добавляется только если file_path указывает на исходный код или явно structural запрос
        """
        context = {"mode": "focused", "sources": {}, "focus_file": file_path}
        tokens_used = 0
        max_tokens = budget.max_tokens if budget else 2000

        # 1. Всегда добавляем summary из init.json
        init_path = self.project_root / self.context_sources["init"]
        if init_path.exists():
            try:
                with open(init_path, 'r', encoding='utf-8') as f:
                    init_data = json.load(f)
                summary = self._extract_summary(init_data)
                context["sources"]["init"] = summary
                tokens_used += len(json.dumps(summary)) // 4
            except Exception as e:
                logger.warning(f"Failed to load init.json: {e}")

        # 2. Добавляем file_context если есть file_path
        if file_path:
            context["file_context"] = self._get_file_context(file_path)
            tokens_used += len(json.dumps(context["file_context"])) // 4

        # 3. Добавляем relationship_context только если file_path явно указывает на исходный код (src/ или .py/.js/.ts)
        add_structural = False
        if file_path and ("src/" in file_path or file_path.endswith(('.py', '.js', '.ts'))):
            add_structural = True
        # Можно добавить дополнительные условия для structural запроса
        if add_structural:
            rel = self._extract_relationship_summary()
            context["relationship_context"] = rel
            tokens_used += len(json.dumps(rel)) // 4

        # 4. Добавляем current_session summary если помещается
        if tokens_used < max_tokens:
            session_path = self.project_root / self.context_sources["current_session"]
            if session_path.exists():
                try:
                    with open(session_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    session_summary = self._extract_summary(session_data)
                    est = len(json.dumps(session_summary)) // 4
                    if tokens_used + est <= max_tokens:
                        context["sources"]["current_session"] = session_summary
                        tokens_used += est
                except Exception as e:
                    logger.warning(f"Failed to load current_session: {e}")

        context["tokens_used"] = tokens_used
        return context
    
    def _load_session_context(self, budget: ContextBudget = None) -> Dict[str, Any]:
        """Load session-specific context."""
        context = {"mode": "session", "sources": {}}
        
        # Load session files first
        session_sources = ["current_session", "sessions", "worklog"]
        
        for source_name in session_sources:
            source_data = self._load_source_with_filtering(source_name, budget)
            if source_data:
                context["sources"][source_name] = source_data
        
        # Add essential project context
        essential_sources = ["init", "tasks"]
        for source_name in essential_sources:
            source_data = self._load_source_with_filtering(source_name, budget)
            if source_data:
                # Filter to current session related items
                filtered_data = self._filter_for_current_session(source_data)
                if filtered_data:
                    context["sources"][source_name] = filtered_data
        
        return context
    
    def _load_minimal_context(self) -> Dict[str, Any]:
        """Load minimal context for quick operations."""
        context = {"mode": "minimal", "sources": {}}
        
        # Only load init and current session
        minimal_sources = ["init", "current_session"]
        
        for source_name in minimal_sources:
            source_path = self.project_root / self.context_sources[source_name]
            if source_path.exists():
                try:
                    with open(source_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Extract only summary information
                        context["sources"][source_name] = self._extract_summary(data)
                except Exception as e:
                    logger.warning(f"Failed to load {source_name}: {e}")
        
        return context
    
    def _load_source_with_filtering(
        self, 
        source_name: str, 
        budget: ContextBudget = None
    ) -> Optional[Dict[str, Any]]:
        """Load source with optional filtering based on budget."""
        source_path = self.project_root / self.context_sources.get(source_name, "")
        
        if not source_path.exists():
            return None
        
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Apply filtering if budget specified
            if budget and budget.exclude_sections:
                data = self._apply_section_filtering(data, budget.exclude_sections)
            
            return data
            
        except Exception as e:
            logger.warning(f"Failed to load {source_name}: {e}")
            return None
    
    def _get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get context specific to a file."""
        # This would analyze the file and provide relevant context
        # For now, return basic file info
        file_path_obj = Path(file_path)
        
        return {
            "file_name": file_path_obj.name,
            "file_type": file_path_obj.suffix,
            "relative_path": file_path,
            "context_type": "file_focused"
        }
    
    def _extract_essential_parts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract essential parts of data to fit token budget."""
        if isinstance(data, dict):
            essential = {}
            
            # Keep essential keys
            essential_keys = ["summary", "goals", "title", "description", "status", "priority"]
            
            for key in essential_keys:
                if key in data:
                    essential[key] = data[key]
            
            # For lists, keep only top priority items
            if "tasks" in data and isinstance(data["tasks"], list):
                high_priority_tasks = [
                    task for task in data["tasks"][:5]  # Top 5 tasks
                    if task.get("priority") in ["high", "critical"]
                ]
                essential["tasks"] = high_priority_tasks
            
            return essential
        
        return data
    
    def _filter_for_current_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data to items relevant to current session."""
        # Load current session info
        current_session_path = self.project_root / "data/sessions/current_session.json"
        
        if not current_session_path.exists():
            return data
        
        try:
            with open(current_session_path, 'r', encoding='utf-8') as f:
                current_session = json.load(f)
                
            session_tasks = current_session.get("related_tasks", [])
            session_ideas = current_session.get("related_ideas", [])
            
            # Filter tasks and ideas to session-related items
            filtered_data = {}
            
            if "tasks" in data:
                filtered_data["tasks"] = [
                    task for task in data["tasks"]
                    if task.get("id") in session_tasks
                ]
            
            if "ideas" in data:
                filtered_data["ideas"] = [
                    idea for idea in data["ideas"] 
                    if idea.get("id") in session_ideas
                ]
            
            # Keep other data as-is
            for key, value in data.items():
                if key not in ["tasks", "ideas"]:
                    filtered_data[key] = value
            
            return filtered_data
            
        except Exception as e:
            logger.warning(f"Failed to filter for current session: {e}")
            return data
    
    def _extract_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary information from data."""
        summary = {}
        
        # Extract key summary fields
        summary_fields = ["title", "summary", "description", "goals", "status"]
        
        for field in summary_fields:
            if field in data:
                summary[field] = data[field]
        
        # For complex structures, extract counts
        if "tasks" in data and isinstance(data["tasks"], list):
            summary["tasks_count"] = len(data["tasks"])
            summary["high_priority_tasks"] = len([
                t for t in data["tasks"] 
                if t.get("priority") == "high"
            ])
        
        return summary
    
    def _apply_section_filtering(
        self, 
        data: Dict[str, Any], 
        exclude_sections: List[str]
    ) -> Dict[str, Any]:
        """Apply section filtering to exclude specified sections."""
        filtered_data = {}
        
        for key, value in data.items():
            if key not in exclude_sections:
                filtered_data[key] = value
        
        return filtered_data
    
    def _update_metrics(
        self, 
        scenario: str, 
        context: Dict[str, Any], 
        load_time: float
    ) -> None:
        """Update performance metrics."""
        tokens_used = context.get("tokens_used", 0)
        sources_count = len(context.get("sources", {}))
        
        if scenario not in self.metrics:
            self.metrics[scenario] = []
        
        self.metrics[scenario].append(ContextMetrics(
            tokens_used=tokens_used,
            files_loaded=sources_count,
            load_time=load_time,
            cache_hit_rate=0.0  # TODO: implement cache hit tracking
        ))
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of context loading metrics."""
        summary = {}
        
        for scenario, metrics_list in self.metrics.items():
            if metrics_list:
                avg_tokens = sum(m.tokens_used for m in metrics_list) / len(metrics_list)
                avg_load_time = sum(m.load_time for m in metrics_list) / len(metrics_list)
                
                summary[scenario] = {
                    "avg_tokens_used": avg_tokens,
                    "avg_load_time": avg_load_time,
                    "total_requests": len(metrics_list)
                }
        
        return summary
    
    def save_metrics(self) -> None:
        """Save metrics to file for analysis."""
        metrics_path = self.project_root / "data" / "context_metrics.json"
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_metrics_summary(), f, indent=2)


# Convenience functions for easy integration

def create_context_orchestrator(project_root: str) -> SmartContextOrchestrator:
    """Factory function to create context orchestrator."""
    return SmartContextOrchestrator(project_root)


def get_optimized_context(
    project_root: str,
    scenario: str,
    file_path: str = None,
    max_tokens: int = None
) -> Dict[str, Any]:
    """
    Get optimized context for scenario - convenience function.
    
    Args:
        project_root: Project root directory
        scenario: Usage scenario (cli_direct, vscode_copilot, session_work)
        file_path: Optional file path for focused context
        max_tokens: Optional token limit override
        
    Returns:
        Optimized context dictionary
    """
    orchestrator = create_context_orchestrator(project_root)
    
    custom_budget = None
    if max_tokens:
        custom_budget = ContextBudget(
            max_tokens=max_tokens,
            priority_files=[],
            essential_sections=[]
        )
    
    return orchestrator.get_context_for_scenario(
        scenario=scenario,
        file_path=file_path,
        custom_budget=custom_budget
    )
