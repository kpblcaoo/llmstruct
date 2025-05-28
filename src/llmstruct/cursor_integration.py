"""
Cursor IDE Integration Module
Provides seamless integration between llmstruct AI capabilities and Cursor IDE.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from llmstruct.ai_self_awareness import SystemCapabilityDiscovery
from llmstruct.context_orchestrator import create_context_orchestrator

logger = logging.getLogger(__name__)


@dataclass
class CursorSession:
    """Represents a Cursor IDE session with context and preferences."""
    session_id: str
    user_preferences: Dict[str, Any]
    active_context: Dict[str, Any]
    goal_alignment: Dict[str, Any]
    ai_delegation_history: List[Dict[str, Any]]


class CursorContextManager:
    """Manages context optimization specifically for Cursor interactions."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.discovery = SystemCapabilityDiscovery(project_root)
        self.orchestrator = create_context_orchestrator(project_root)
        self.config = self._load_cursor_config()
        
    def get_cursor_optimized_context(self, query_type: str, file_context: str = None) -> Dict[str, Any]:
        """Provide Cursor with perfectly sized context based on query analysis."""
        try:
            # Analyze query to determine optimal context level
            context_rules = self.config.get("context_optimization", {}).get("query_analysis_patterns", {})
            optimal_config = context_rules.get(query_type, context_rules.get("technical_implementation", {}))
            
            # Load specified context files
            context_data = {}
            for file_name in optimal_config.get("context_files", []):
                file_path = self.project_root / "data" / file_name
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        context_data[file_name] = json.load(f)
            
            # Apply privacy filtering
            privacy_level = optimal_config.get("privacy_filter", "none")
            if privacy_level != "none":
                context_data = self._apply_privacy_filter(context_data, privacy_level)
            
            # Add file context if provided
            if file_context:
                context_data["current_file_context"] = file_context
            
            return {
                "context_data": context_data,
                "token_budget": optimal_config.get("token_budget", 16000),
                "ai_preference": optimal_config.get("ai_preference", "claude"),
                "response_style": optimal_config.get("response_style", "detailed_technical"),
                "query_type": query_type,
                "optimization_applied": True
            }
        except Exception as e:
            logger.error(f"Cursor context optimization error: {e}")
            return {"error": str(e), "optimization_applied": False}
    
    def _load_cursor_config(self) -> Dict:
        """Load Cursor-specific configuration."""
        try:
            config_path = self.project_root / "data" / "cursor" / "cursor_context_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Cursor config loading error: {e}")
            return {}
    
    def _apply_privacy_filter(self, context_data: Dict, privacy_level: str) -> Dict:
        """Apply privacy filtering based on level."""
        if privacy_level == "none":
            return context_data
        
        filtered_data = {}
        for key, value in context_data.items():
            if privacy_level == "high":
                if isinstance(value, dict):
                    filtered_value = self._filter_sensitive_dict(value)
                    filtered_data[key] = filtered_value
                else:
                    filtered_data[key] = value
            else:
                filtered_data[key] = value
        
        return filtered_data
    
    def _filter_sensitive_dict(self, data: Dict) -> Dict:
        """Filter sensitive information from dictionary."""
        sensitive_keys = ["personal", "financial", "location", "family", "private"]
        filtered = {}
        
        for key, value in data.items():
            if not any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, dict):
                    filtered[key] = self._filter_sensitive_dict(value)
                else:
                    filtered[key] = value
        
        return filtered


class CursorMultiAIOrchestrator:
    """Coordinates different AI models through Cursor interface."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config = self._load_cursor_config()
        self.delegation_history = []
        
    def delegate_to_optimal_ai(self, task_type: str, context: Dict) -> Dict[str, Any]:
        """Route tasks to best AI model based on preferences."""
        try:
            delegation_rules = self.config.get("ai_delegation_rules", {})
            
            # Determine optimal AI
            grok_tasks = delegation_rules.get("grok_optimal_tasks", [])
            claude_tasks = delegation_rules.get("claude_optimal_tasks", [])
            
            if task_type in grok_tasks:
                optimal_ai = "grok"
            elif task_type in claude_tasks:
                optimal_ai = "claude"
            else:
                optimal_ai = delegation_rules.get("fallback_strategy", "claude_for_safety").split("_")[0]
            
            # Record delegation decision
            delegation_record = {
                "task_type": task_type,
                "selected_ai": optimal_ai,
                "confidence": self._calculate_delegation_confidence(task_type, optimal_ai),
                "timestamp": str(Path().cwd())  # Placeholder for timestamp
            }
            
            self.delegation_history.append(delegation_record)
            
            return {
                "recommended_ai": optimal_ai,
                "confidence": delegation_record["confidence"],
                "reasoning": f"Task '{task_type}' is optimal for {optimal_ai}",
                "delegation_record": delegation_record
            }
        except Exception as e:
            logger.error(f"AI delegation error: {e}")
            return {"error": str(e), "recommended_ai": "claude"}
    
    def _calculate_delegation_confidence(self, task_type: str, selected_ai: str) -> float:
        """Calculate confidence in AI delegation decision."""
        # Simple confidence calculation based on task-AI matching
        delegation_rules = self.config.get("ai_delegation_rules", {})
        
        if selected_ai == "grok":
            optimal_tasks = delegation_rules.get("grok_optimal_tasks", [])
        else:
            optimal_tasks = delegation_rules.get("claude_optimal_tasks", [])
        
        if task_type in optimal_tasks:
            return 0.95
        else:
            return 0.7  # Lower confidence for fallback decisions
    
    def _load_cursor_config(self) -> Dict:
        """Load Cursor configuration."""
        try:
            config_path = Path(self.project_root) / "data" / "cursor" / "cursor_context_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {}


class PersonalPlanningCursorBridge:
    """Bridge between personal planning and Cursor without exposing sensitive data."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.personal_bridge = self._load_personal_bridge()
        
    def get_goal_aligned_suggestions(self, technical_context: str) -> List[str]:
        """Provide suggestions aligned with business goals."""
        try:
            business_objectives = self.personal_bridge.get("business_objectives", {})
            suggestions = []
            
            # Monetization-focused suggestions
            if "monetization" in technical_context.lower():
                suggestions.extend([
                    "Consider enterprise API features for revenue generation",
                    "Implement usage-based pricing metrics",
                    "Add commercial-grade security features",
                    "Design for multi-tenant architecture"
                ])
            
            # Development acceleration suggestions
            if any(keyword in technical_context.lower() for keyword in ["implement", "develop", "build"]):
                suggestions.extend([
                    "Leverage AI automation to accelerate development",
                    "Focus on MVP features for faster market entry",
                    "Use existing patterns to minimize development time",
                    "Implement automated testing for reliability"
                ])
            
            # Commercial readiness suggestions
            if "api" in technical_context.lower():
                suggestions.extend([
                    "Design for enterprise scalability",
                    "Implement comprehensive error handling",
                    "Add detailed API documentation",
                    "Include rate limiting and authentication"
                ])
            
            # AI integration suggestions
            if "ai" in technical_context.lower():
                suggestions.extend([
                    "Implement multi-AI model support",
                    "Add AI response caching for performance",
                    "Design for AI model switching",
                    "Include AI usage analytics"
                ])
            
            return suggestions[:5]  # Limit to top 5 suggestions
        except Exception as e:
            logger.error(f"Goal alignment error: {e}")
            return ["Error generating goal-aligned suggestions"]
    
    def get_priority_guidance(self, feature_options: List[str]) -> Dict[str, Any]:
        """Provide priority guidance based on business objectives."""
        try:
            decision_guidance = self.personal_bridge.get("decision_guidance", {})
            prioritization = decision_guidance.get("feature_prioritization", {})
            
            # Score each feature option
            scored_features = []
            for feature in feature_options:
                score = self._calculate_feature_score(feature, prioritization)
                scored_features.append({
                    "feature": feature,
                    "score": score,
                    "reasoning": self._get_scoring_reasoning(feature, prioritization)
                })
            
            # Sort by score
            scored_features.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "prioritized_features": scored_features,
                "recommendation": scored_features[0] if scored_features else None,
                "guidance_applied": True
            }
        except Exception as e:
            logger.error(f"Priority guidance error: {e}")
            return {"error": str(e), "guidance_applied": False}
    
    def _calculate_feature_score(self, feature: str, prioritization: Dict) -> float:
        """Calculate priority score for a feature."""
        score = 0.0
        
        # Monetization potential
        if any(keyword in feature.lower() for keyword in ["api", "enterprise", "commercial", "revenue"]):
            score += float(prioritization.get("monetization_potential", "weight: 0.4").split(": ")[1])
        
        # Development acceleration
        if any(keyword in feature.lower() for keyword in ["automation", "ai", "optimization"]):
            score += float(prioritization.get("development_acceleration", "weight: 0.3").split(": ")[1])
        
        # Commercial readiness
        if any(keyword in feature.lower() for keyword in ["security", "scalability", "documentation"]):
            score += float(prioritization.get("commercial_readiness", "weight: 0.2").split(": ")[1])
        
        # Innovation value
        if any(keyword in feature.lower() for keyword in ["new", "innovative", "experimental"]):
            score += float(prioritization.get("innovation_value", "weight: 0.1").split(": ")[1])
        
        return score
    
    def _get_scoring_reasoning(self, feature: str, prioritization: Dict) -> str:
        """Get reasoning for feature scoring."""
        reasons = []
        
        if any(keyword in feature.lower() for keyword in ["api", "enterprise", "commercial"]):
            reasons.append("High monetization potential")
        
        if any(keyword in feature.lower() for keyword in ["automation", "ai"]):
            reasons.append("Accelerates development")
        
        if any(keyword in feature.lower() for keyword in ["security", "scalability"]):
            reasons.append("Improves commercial readiness")
        
        return "; ".join(reasons) if reasons else "Standard priority"
    
    def _load_personal_bridge(self) -> Dict:
        """Load personal planning bridge data."""
        try:
            bridge_path = self.project_root / "data" / "cursor" / "cursor_personal_bridge.json"
            if bridge_path.exists():
                with open(bridge_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Personal bridge loading error: {e}")
            return {}


class CursorSessionManager:
    """Maintains context across Cursor sessions for better continuity."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.session_file = self.project_root / "data" / "cursor" / "cursor_session_memory.json"
        self.current_session = None
        
    def start_session(self, session_id: str, user_preferences: Dict = None) -> CursorSession:
        """Start a new Cursor session."""
        try:
            self.current_session = CursorSession(
                session_id=session_id,
                user_preferences=user_preferences or {},
                active_context={},
                goal_alignment={},
                ai_delegation_history=[]
            )
            
            # Load previous session data if available
            previous_context = self._load_session_context()
            if previous_context:
                self.current_session.active_context.update(previous_context.get("carry_over_context", {}))
            
            return self.current_session
        except Exception as e:
            logger.error(f"Session start error: {e}")
            return None
    
    def save_session_context(self, session_data: Dict):
        """Save important context for next session."""
        try:
            # Prepare data for persistence
            session_memory = {
                "last_session_id": self.current_session.session_id if self.current_session else "unknown",
                "carry_over_context": {
                    "recent_queries": session_data.get("recent_queries", [])[-5:],  # Last 5 queries
                    "active_goals": session_data.get("active_goals", []),
                    "preferred_ai_models": session_data.get("preferred_ai_models", {}),
                    "context_preferences": session_data.get("context_preferences", {})
                },
                "learning_data": {
                    "successful_patterns": session_data.get("successful_patterns", []),
                    "optimization_preferences": session_data.get("optimization_preferences", {}),
                    "delegation_success_rate": session_data.get("delegation_success_rate", 0.0)
                },
                "timestamp": str(Path().cwd())  # Placeholder for timestamp
            }
            
            # Save to file
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(session_memory, f, indent=2)
                
        except Exception as e:
            logger.error(f"Session save error: {e}")
    
    def _load_session_context(self) -> Optional[Dict]:
        """Load context from previous sessions."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Session load error: {e}")
            return None


class CursorIntegrationManager:
    """Main integration manager that coordinates all Cursor-specific features."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.context_manager = CursorContextManager(project_root)
        self.ai_orchestrator = CursorMultiAIOrchestrator(project_root)
        self.personal_bridge = PersonalPlanningCursorBridge(project_root)
        self.session_manager = CursorSessionManager(project_root)
        self.discovery = SystemCapabilityDiscovery(project_root)
        
    def get_comprehensive_cursor_response(self, query: str, file_context: str = None) -> Dict[str, Any]:
        """Get comprehensive response optimized for Cursor."""
        try:
            # Analyze query
            query_analysis = {"query": query}
            query_type = self.context_manager.discovery._analyze_query_type(query_analysis)
            
            # Get optimized context
            context_data = self.context_manager.get_cursor_optimized_context(query_type, file_context)
            
            # Get AI delegation recommendation
            ai_recommendation = self.ai_orchestrator.delegate_to_optimal_ai(query_type, context_data)
            
            # Get goal-aligned suggestions
            goal_suggestions = self.personal_bridge.get_goal_aligned_suggestions(query)
            
            # Get system status
            system_status = self.discovery.get_cursor_status_report()
            
            return {
                "query_type": query_type,
                "optimized_context": context_data,
                "ai_recommendation": ai_recommendation,
                "goal_aligned_suggestions": goal_suggestions,
                "system_status": system_status,
                "integration_success": True
            }
        except Exception as e:
            logger.error(f"Comprehensive response error: {e}")
            return {"error": str(e), "integration_success": False}


# Factory function for easy integration
def create_cursor_integration(project_root: str) -> CursorIntegrationManager:
    """Create a Cursor integration manager for the project."""
    return CursorIntegrationManager(project_root) 