#!/usr/bin/env python3
"""
Cursor AI Bridge - API Layer for AI Assistant Integration
Provides CLI and HTTP endpoints so Cursor AI can use WorkflowOrchestrator
"""

import json
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our existing systems
from .workflow_orchestrator import WorkflowOrchestrator
from .ai_self_awareness import SystemCapabilityDiscovery
from .cursor_integration import CursorIntegrationManager

logger = logging.getLogger(__name__)


class CursorAIBridge:
    """
    Bridge that allows Cursor AI assistant to use WorkflowOrchestrator
    through CLI commands and structured JSON responses.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.orchestrator = WorkflowOrchestrator(str(self.project_root))
        self.cursor_integration = CursorIntegrationManager(str(self.project_root))
        
    def ai_get_context(self, query_type: str = "general", file_path: str = None) -> Dict[str, Any]:
        """Get AI-optimized context for current development state."""
        try:
            # Get comprehensive context from WorkflowOrchestrator
            context = self.orchestrator.get_current_context()
            
            # Get Cursor-optimized context
            cursor_context = self.cursor_integration.get_comprehensive_cursor_response(
                query=f"Context request: {query_type}",
                file_context=file_path
            )
            
            # Combine and optimize for AI consumption
            ai_context = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "query_type": query_type,
                "project_state": {
                    "modules_count": context.get("struct_analysis", {}).get("stats", {}).get("modules_count", 0),
                    "functions_count": context.get("struct_analysis", {}).get("stats", {}).get("functions_count", 0),
                    "active_tasks": len(context.get("active_tasks", [])),
                    "copilot_layers": len(context.get("copilot_status", {}).get("loaded_layers", [])),
                    "ai_capabilities": len(context.get("system_capabilities", {}).get("capabilities", [])),
                },
                "recommendations": cursor_context.get("goal_aligned_suggestions", []),
                "ai_delegation": cursor_context.get("ai_delegation", {}),
                "context_optimization": cursor_context.get("context_optimization", {}),
                "workflow_suggestions": self._get_workflow_suggestions(query_type),
                "available_commands": self._get_available_ai_commands(),
            }
            
            return ai_context
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}
    
    def ai_analyze_task(self, task_description: str) -> Dict[str, Any]:
        """Analyze a task and provide AI-optimized guidance."""
        try:
            # Get current context
            context = self.orchestrator.get_current_context()
            
            # Analyze task against current codebase
            struct_analysis = context.get("struct_analysis", {})
            
            # Determine task type and complexity
            task_analysis = {
                "task_description": task_description,
                "estimated_complexity": self._estimate_task_complexity(task_description, struct_analysis),
                "suggested_approach": self._suggest_approach(task_description, struct_analysis),
                "relevant_modules": self._find_relevant_modules(task_description, struct_analysis),
                "potential_duplicates": self._check_potential_duplicates(task_description, struct_analysis),
                "recommended_ai": self._recommend_ai_for_task(task_description),
                "workflow_steps": self._generate_workflow_steps(task_description),
                "context_requirements": self._determine_context_requirements(task_description),
            }
            
            return task_analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def ai_create_task(self, title: str, description: str, priority: int = 3) -> Dict[str, Any]:
        """Create a task through AI interface."""
        try:
            task_id = self.orchestrator.create_task(title, description, priority)
            
            # Get task analysis
            analysis = self.ai_analyze_task(description)
            
            return {
                "task_id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "analysis": analysis,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "status": "created_successfully"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def ai_get_onboarding_guide(self) -> Dict[str, Any]:
        """Get comprehensive AI onboarding guide."""
        try:
            guide = self.orchestrator.get_ai_onboarding_guide()
            
            # Add AI-specific guidance
            guide["ai_assistant_guidance"] = {
                "how_to_use_this_system": [
                    "1. Always start with: python -m llmstruct.cursor_ai_bridge ai-context",
                    "2. For tasks: python -m llmstruct.cursor_ai_bridge ai-analyze-task 'description'",
                    "3. Check duplicates: python -m llmstruct.cursor_ai_bridge ai-check-duplicates",
                    "4. Get suggestions: python -m llmstruct.cursor_ai_bridge ai-suggest 'context'",
                ],
                "workflow_integration": {
                    "before_coding": "Get context and analyze task",
                    "during_coding": "Check for duplicates and get suggestions",
                    "after_coding": "Update struct.json and validate changes",
                },
                "ai_delegation_usage": {
                    "code_analysis": "Use Grok for complex code analysis",
                    "documentation": "Use Claude for documentation tasks",
                    "creative_solutions": "Use Grok for innovative approaches",
                    "personal_planning": "Use Claude for business planning",
                },
            }
            
            return guide
            
        except Exception as e:
            return {"error": str(e)}
    
    def ai_check_duplicates(self, threshold: int = 3) -> Dict[str, Any]:
        """Check for code duplicates with AI-friendly output."""
        try:
            analysis = self.orchestrator.analyze_codebase_for_duplicates()
            
            # Format for AI consumption
            ai_analysis = {
                "duplication_summary": {
                    "total_functions": analysis.get("analysis", {}).get("total_unique_functions", 0),
                    "duplicated_functions": analysis.get("analysis", {}).get("duplicated_functions", 0),
                    "duplication_percentage": analysis.get("analysis", {}).get("duplication_percentage", 0),
                },
                "high_priority_duplicates": self._identify_high_priority_duplicates(analysis),
                "refactoring_suggestions": self._generate_refactoring_suggestions(analysis),
                "ai_recommendations": [
                    "Focus on duplicates with >5 occurrences first",
                    "Consider extracting common patterns into utilities",
                    "Use struct.json to understand function relationships before refactoring",
                ],
            }
            
            return ai_analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def ai_suggest(self, context: str) -> Dict[str, Any]:
        """Get AI suggestions based on context."""
        try:
            # Get goal-aligned suggestions
            suggestions = self.cursor_integration.personal_bridge.get_goal_aligned_suggestions(context)
            
            # Get workflow suggestions
            workflow_suggestions = self._get_workflow_suggestions(context)
            
            # Get AI delegation recommendation
            delegation = self.cursor_integration.ai_orchestrator.delegate_to_optimal_ai(
                task_type=self._classify_task_type(context),
                context={"description": context}
            )
            
            return {
                "context": context,
                "goal_aligned_suggestions": suggestions,
                "workflow_suggestions": workflow_suggestions,
                "recommended_ai": delegation.get("recommended_ai", "claude"),
                "confidence": delegation.get("confidence", 0.7),
                "reasoning": delegation.get("reasoning", ""),
                "next_steps": self._generate_next_steps(context),
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _estimate_task_complexity(self, task: str, struct_analysis: Dict) -> str:
        """Estimate task complexity based on codebase analysis."""
        # Simple heuristic based on keywords and codebase size
        complexity_keywords = {
            "high": ["refactor", "architecture", "redesign", "migrate", "overhaul"],
            "medium": ["implement", "add", "create", "extend", "integrate"],
            "low": ["fix", "update", "modify", "adjust", "tweak"]
        }
        
        task_lower = task.lower()
        for level, keywords in complexity_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return level
        
        return "medium"  # Default
    
    def _suggest_approach(self, task: str, struct_analysis: Dict) -> List[str]:
        """Suggest approach based on task and codebase state."""
        approaches = [
            "1. Analyze struct.json to understand current architecture",
            "2. Check for existing similar implementations",
            "3. Identify affected modules and dependencies",
        ]
        
        if "test" in task.lower():
            approaches.append("4. Create comprehensive test cases")
        if "api" in task.lower():
            approaches.append("4. Design API interface first")
        if "refactor" in task.lower():
            approaches.append("4. Plan refactoring in small, safe steps")
        
        approaches.append("5. Update documentation and struct.json after changes")
        
        return approaches
    
    def _find_relevant_modules(self, task: str, struct_analysis: Dict) -> List[str]:
        """Find modules relevant to the task."""
        # Simple keyword matching against module names
        modules = struct_analysis.get("modules", [])
        task_keywords = task.lower().split()
        
        relevant = []
        for module in modules[:10]:  # Limit to top 10
            module_path = module.get("path", "").lower()
            if any(keyword in module_path for keyword in task_keywords):
                relevant.append(module.get("path", ""))
        
        return relevant
    
    def _check_potential_duplicates(self, task: str, struct_analysis: Dict) -> List[str]:
        """Check if task might create duplicates."""
        # This would need more sophisticated analysis
        return ["Check existing implementations before creating new functions"]
    
    def _recommend_ai_for_task(self, task: str) -> Dict[str, Any]:
        """Recommend which AI to use for the task."""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ["code", "implement", "algorithm", "optimize"]):
            return {"ai": "grok", "reason": "Code implementation and optimization"}
        elif any(keyword in task_lower for keyword in ["document", "explain", "plan", "design"]):
            return {"ai": "claude", "reason": "Documentation and planning tasks"}
        else:
            return {"ai": "claude", "reason": "General purpose fallback"}
    
    def _generate_workflow_steps(self, task: str) -> List[str]:
        """Generate workflow steps for the task."""
        return [
            "1. Get current context with ai-context command",
            "2. Analyze task complexity and requirements",
            "3. Check for existing implementations",
            "4. Plan implementation approach",
            "5. Execute with appropriate AI assistance",
            "6. Test and validate changes",
            "7. Update documentation and struct.json"
        ]
    
    def _determine_context_requirements(self, task: str) -> List[str]:
        """Determine what context is needed for the task."""
        requirements = ["struct.json", "init_enhanced.json"]
        
        task_lower = task.lower()
        if "cli" in task_lower:
            requirements.append("cli_enhanced.json")
        if "test" in task_lower:
            requirements.append("test modules analysis")
        if "api" in task_lower:
            requirements.append("API documentation")
        
        return requirements
    
    def _get_workflow_suggestions(self, context: str) -> List[str]:
        """Get workflow suggestions based on context."""
        return [
            "Use WorkflowOrchestrator for comprehensive context",
            "Check struct.json before making changes",
            "Leverage AI delegation for optimal results",
            "Update documentation after changes"
        ]
    
    def _get_available_ai_commands(self) -> Dict[str, str]:
        """Get available AI commands."""
        return {
            "ai-context": "Get current development context",
            "ai-analyze-task": "Analyze a specific task",
            "ai-create-task": "Create a new task",
            "ai-check-duplicates": "Check for code duplicates",
            "ai-suggest": "Get suggestions for context",
            "ai-onboard": "Get AI onboarding guide",
        }
    
    def _identify_high_priority_duplicates(self, analysis: Dict) -> List[Dict]:
        """Identify high-priority duplicates for refactoring."""
        # This would analyze the duplication data
        return [{"function": "example", "occurrences": 5, "priority": "high"}]
    
    def _generate_refactoring_suggestions(self, analysis: Dict) -> List[str]:
        """Generate refactoring suggestions."""
        return [
            "Extract common patterns into utility functions",
            "Create base classes for repeated functionality",
            "Consider using composition over inheritance"
        ]
    
    def _classify_task_type(self, context: str) -> str:
        """Classify task type for AI delegation."""
        context_lower = context.lower()
        
        if any(keyword in context_lower for keyword in ["code", "implement", "algorithm"]):
            return "code_analysis"
        elif any(keyword in context_lower for keyword in ["document", "explain"]):
            return "documentation"
        elif any(keyword in context_lower for keyword in ["plan", "strategy"]):
            return "personal_planning"
        elif any(keyword in context_lower for keyword in ["debug", "fix"]):
            return "debugging_analysis"
        else:
            return "technical_implementation"
    
    def _generate_next_steps(self, context: str) -> List[str]:
        """Generate next steps based on context."""
        return [
            "Review suggestions and select approach",
            "Use recommended AI for implementation",
            "Follow workflow suggestions",
            "Validate changes with struct.json analysis"
        ]


def main():
    """CLI interface for Cursor AI Bridge."""
    parser = argparse.ArgumentParser(description="Cursor AI Bridge - CLI for AI Assistant")
    parser.add_argument("command", choices=[
        "ai-context", "ai-analyze-task", "ai-create-task", 
        "ai-check-duplicates", "ai-suggest", "ai-onboard"
    ])
    parser.add_argument("--query-type", default="general", help="Type of query for context")
    parser.add_argument("--file-path", help="File path for context")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--title", help="Task title")
    parser.add_argument("--priority", type=int, default=3, help="Task priority")
    parser.add_argument("--context", help="Context for suggestions")
    parser.add_argument("--threshold", type=int, default=3, help="Duplication threshold")
    
    args = parser.parse_args()
    
    # Initialize bridge
    bridge = CursorAIBridge()
    
    # Execute command
    result = None
    
    if args.command == "ai-context":
        result = bridge.ai_get_context(args.query_type, args.file_path)
    
    elif args.command == "ai-analyze-task":
        if not args.task:
            result = {"error": "Task description required (--task)"}
        else:
            result = bridge.ai_analyze_task(args.task)
    
    elif args.command == "ai-create-task":
        if not args.title or not args.task:
            result = {"error": "Title and task description required (--title --task)"}
        else:
            result = bridge.ai_create_task(args.title, args.task, args.priority)
    
    elif args.command == "ai-check-duplicates":
        result = bridge.ai_check_duplicates(args.threshold)
    
    elif args.command == "ai-suggest":
        if not args.context:
            result = {"error": "Context required (--context)"}
        else:
            result = bridge.ai_suggest(args.context)
    
    elif args.command == "ai-onboard":
        result = bridge.ai_onboarding_guide()
    
    # Output result as JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 