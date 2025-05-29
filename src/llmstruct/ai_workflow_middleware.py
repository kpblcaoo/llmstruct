"""
AI Workflow Middleware - Forces AI Integration with LLMStruct
Intercepts all AI requests and ensures they go through our orchestration system.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from llmstruct.context_orchestrator import create_context_orchestrator
from llmstruct.cursor_ai_bridge import CursorAIBridge
from llmstruct.ai_self_awareness import SystemCapabilityDiscovery

logger = logging.getLogger(__name__)


class AIWorkflowMode(Enum):
    """AI workflow enforcement modes."""
    STRICT = "strict"        # All requests MUST go through llmstruct
    GUIDED = "guided"        # Suggest llmstruct usage  
    MONITORING = "monitoring" # Log usage but don't enforce
    DISABLED = "disabled"    # No enforcement


@dataclass
class AIRequest:
    """Standardized AI request structure."""
    query: str
    context_tags: List[str]
    file_context: Optional[str] = None
    mode: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass 
class AIResponse:
    """Standardized AI response structure."""
    content: str
    used_llmstruct: bool
    context_optimization: Dict[str, Any]
    delegation_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class AIWorkflowMiddleware:
    """
    Middleware that ensures ALL AI interactions go through LLMStruct system.
    This solves the problem of AI not using its own infrastructure.
    """
    
    def __init__(self, project_root: str, mode: AIWorkflowMode = AIWorkflowMode.GUIDED):
        self.project_root = Path(project_root)
        self.mode = mode
        self.orchestrator = create_context_orchestrator(str(project_root))
        self.bridge = CursorAIBridge(project_root)
        self.capability_discovery = SystemCapabilityDiscovery(project_root)
        
        # Load configuration
        self._load_middleware_config()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "llmstruct_usage": 0,
            "bypassed_requests": 0,
            "context_optimizations": 0,
            "ai_delegations": 0
        }
        
        logger.info(f"AI Workflow Middleware initialized in {mode.value} mode")
    
    def _load_middleware_config(self) -> None:
        """Load middleware configuration."""
        config_path = self.project_root / "data" / "ai_workflow_config.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "enforcement_rules": {
                    "require_context_tags": True,
                    "require_delegation_analysis": True,
                    "require_context_optimization": True,
                    "auto_inject_project_context": True
                },
                "bypass_patterns": [
                    "simple greeting",
                    "basic confirmation", 
                    "short clarification"
                ],
                "mandatory_llmstruct_patterns": [
                    "analyze", "implement", "refactor", "debug",
                    "architecture", "planning", "documentation"
                ]
            }
    
    def process_ai_request(self, raw_query: str, ai_handler: Callable = None) -> AIResponse:
        """
        Main middleware entry point - ALL AI requests should go through this.
        
        Args:
            raw_query: Raw AI query/request
            ai_handler: Optional custom AI handler function
            
        Returns:
            Processed AI response with llmstruct integration
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Parse and analyze request
            request = self._parse_ai_request(raw_query)
            
            # Check if llmstruct usage is required
            if self._should_use_llmstruct(request):
                return self._process_with_llmstruct(request, ai_handler)
            else:
                return self._process_bypass(request, ai_handler)
                
        except Exception as e:
            logger.error(f"AI middleware error: {e}")
            return AIResponse(
                content=f"Middleware error: {e}",
                used_llmstruct=False,
                context_optimization={},
                delegation_info={"error": str(e)},
                performance_metrics={"processing_time": time.time() - start_time}
            )
    
    def _parse_ai_request(self, raw_query: str) -> AIRequest:
        """Parse raw query into structured AI request."""
        # Extract context tags if present
        context_tags = []
        query = raw_query
        
        # Look for [tag] patterns
        import re
        tag_pattern = r'\[([^\]]+)\]'
        tags = re.findall(tag_pattern, query)
        context_tags.extend(tags)
        
        # Remove tags from query for cleaner processing
        clean_query = re.sub(tag_pattern, '', query).strip()
        
        return AIRequest(
            query=clean_query,
            context_tags=context_tags,
            metadata={
                "original_query": raw_query,
                "extracted_tags": tags,
                "timestamp": time.time()
            }
        )
    
    def _should_use_llmstruct(self, request: AIRequest) -> bool:
        """Determine if request should use llmstruct system."""
        if self.mode == AIWorkflowMode.DISABLED:
            return False
        
        if self.mode == AIWorkflowMode.STRICT:
            return True
        
        # Check for bypass patterns
        query_lower = request.query.lower()
        for pattern in self.config["bypass_patterns"]:
            if pattern in query_lower:
                return False
        
        # Check for mandatory patterns
        for pattern in self.config["mandatory_llmstruct_patterns"]:
            if pattern in query_lower:
                return True
        
        # Check context tags
        if request.context_tags:
            return True
        
        # Default behavior based on mode
        return self.mode == AIWorkflowMode.GUIDED
    
    def _process_with_llmstruct(self, request: AIRequest, ai_handler: Callable) -> AIResponse:
        """Process request through full llmstruct system."""
        start_time = time.time()
        self.stats["llmstruct_usage"] += 1
        
        # 1. Context optimization
        context_result = self._optimize_context(request)
        
        # 2. AI delegation analysis
        delegation_result = self._analyze_ai_delegation(request)
        
        # 3. Get enhanced context
        enhanced_context = self._get_enhanced_context(request, context_result)
        
        # 4. Process through AI with enhanced context
        if ai_handler:
            ai_response = ai_handler(request.query, enhanced_context)
        else:
            ai_response = self._default_ai_processing(request, enhanced_context)
        
        # 5. Post-process and wrap response
        return AIResponse(
            content=ai_response,
            used_llmstruct=True,
            context_optimization=context_result,
            delegation_info=delegation_result,
            performance_metrics={
                "processing_time": time.time() - start_time,
                "context_tokens": enhanced_context.get("tokens_used", 0),
                "optimization_applied": True
            }
        )
    
    def _process_bypass(self, request: AIRequest, ai_handler: Callable) -> AIResponse:
        """Process request without llmstruct system."""
        self.stats["bypassed_requests"] += 1
        
        if ai_handler:
            response = ai_handler(request.query, {})
        else:
            response = f"Processed query: {request.query}"
        
        return AIResponse(
            content=response,
            used_llmstruct=False,
            context_optimization={},
            delegation_info={"reason": "bypassed"},
            performance_metrics={"processing_time": 0.01}
        )
    
    def _optimize_context(self, request: AIRequest) -> Dict[str, Any]:
        """Optimize context using orchestrator."""
        try:
            self.stats["context_optimizations"] += 1
            
            # Determine scenario from context tags
            scenario = self._map_tags_to_scenario(request.context_tags)
            
            # Get optimized context
            context = self.orchestrator.get_context_for_scenario(
                scenario=scenario,
                file_path=request.file_context
            )
            
            return {
                "scenario": scenario,
                "tokens_used": context.get("tokens_used", 0),
                "sources_loaded": len(context.get("sources", {})),
                "optimization_successful": True
            }
            
        except Exception as e:
            logger.error(f"Context optimization error: {e}")
            return {"error": str(e), "optimization_successful": False}
    
    def _analyze_ai_delegation(self, request: AIRequest) -> Dict[str, Any]:
        """Analyze which AI should handle this request."""
        try:
            self.stats["ai_delegations"] += 1
            
            # Use bridge for delegation analysis
            delegation = self.bridge.ai_analyze_task(request.query)
            
            return {
                "recommended_ai": delegation.get("recommended_ai", "current"),
                "confidence": delegation.get("confidence", 0.5),
                "reasoning": delegation.get("reasoning", "No specific preference"),
                "delegation_successful": True
            }
            
        except Exception as e:
            logger.error(f"AI delegation error: {e}")
            return {"error": str(e), "delegation_successful": False}
    
    def _get_enhanced_context(self, request: AIRequest, context_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhanced context with project awareness."""
        enhanced = {
            "request_info": {
                "query": request.query,
                "tags": request.context_tags,
                "timestamp": request.metadata.get("timestamp")
            },
            "llmstruct_context": context_result,
            "system_capabilities": self._get_capability_summary(),
            "usage_guidance": self._generate_usage_guidance(request)
        }
        
        return enhanced
    
    def _get_capability_summary(self) -> Dict[str, Any]:
        """Get current system capabilities."""
        try:
            capabilities = self.capability_discovery.discover_all_capabilities()
            return {
                "available_tools": [
                    name for name, tool in capabilities.tools.items()
                    if tool.status.value == "available"
                ],
                "context_modes": capabilities.context.available_modes,
                "ai_integration_active": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_usage_guidance(self, request: AIRequest) -> List[str]:
        """Generate guidance for AI on how to use llmstruct system."""
        guidance = [
            "✅ You are now using the LLMStruct system - context has been optimized",
            "🔍 Use `codebase_search` for semantic code exploration", 
            "📊 Check `struct.json` for project structure understanding",
            "🎯 Apply context tags like [code], [debug], [discuss] for better results"
        ]
        
        # Add specific guidance based on context tags
        if "debug" in request.context_tags:
            guidance.append("🐛 Debug mode: Focus on error analysis and troubleshooting")
        
        if "code" in request.context_tags:
            guidance.append("💻 Code mode: Implement changes using project patterns")
        
        if "discuss" in request.context_tags:
            guidance.append("💭 Discussion mode: No file changes, focus on planning")
        
        return guidance
    
    def _map_tags_to_scenario(self, tags: List[str]) -> str:
        """Map context tags to orchestrator scenarios."""
        tag_mapping = {
            "code": "cli_direct",
            "debug": "cli_query",
            "discuss": "session_work",
            "review": "vscode_copilot",
            "meta": "cli_query",
            "test": "cli_query"
        }
        
        for tag in tags:
            if tag in tag_mapping:
                return tag_mapping[tag]
        
        return "cli_query"  # Default
    
    def _default_ai_processing(self, request: AIRequest, context: Dict[str, Any]) -> str:
        """Default AI processing when no custom handler provided."""
        return f"""
🧠 **LLMStruct AI Response**

Query: {request.query}
Tags: {', '.join(request.context_tags) if request.context_tags else 'None'}

**System Status**: ✅ Operating with full LLMStruct integration
**Context Optimization**: Applied ({context['llmstruct_context'].get('tokens_used', 0)} tokens)
**Available Tools**: {', '.join(context['system_capabilities'].get('available_tools', []))}

**Response**: This request has been processed through the LLMStruct system with optimized context and AI delegation analysis. The AI assistant should now have access to full project awareness and enhanced capabilities.

**Recommendation**: Continue using context tags and the llmstruct system for optimal results.
"""
    
    def get_middleware_stats(self) -> Dict[str, Any]:
        """Get middleware usage statistics."""
        total = self.stats["total_requests"]
        
        return {
            **self.stats,
            "llmstruct_usage_rate": self.stats["llmstruct_usage"] / total if total > 0 else 0,
            "bypass_rate": self.stats["bypassed_requests"] / total if total > 0 else 0,
            "current_mode": self.mode.value
        }
    
    def force_llmstruct_mode(self) -> None:
        """Force all future requests to use llmstruct system."""
        self.mode = AIWorkflowMode.STRICT
        logger.info("AI Workflow Middleware switched to STRICT mode - all requests will use LLMStruct")
    
    def enable_guidance_mode(self) -> None:
        """Enable guided mode with llmstruct suggestions."""
        self.mode = AIWorkflowMode.GUIDED
        logger.info("AI Workflow Middleware switched to GUIDED mode")


# Global middleware instance
_middleware_instance = None


def initialize_ai_middleware(project_root: str, mode: AIWorkflowMode = AIWorkflowMode.GUIDED) -> AIWorkflowMiddleware:
    """Initialize global AI middleware."""
    global _middleware_instance
    _middleware_instance = AIWorkflowMiddleware(project_root, mode)
    return _middleware_instance


def get_ai_middleware() -> Optional[AIWorkflowMiddleware]:
    """Get current AI middleware instance."""
    return _middleware_instance


def process_ai_query(query: str, ai_handler: Callable = None) -> AIResponse:
    """Global function to process AI queries through middleware."""
    if _middleware_instance is None:
        raise RuntimeError("AI Middleware not initialized. Call initialize_ai_middleware() first.")
    
    return _middleware_instance.process_ai_request(query, ai_handler)


# Decorator for AI functions to ensure llmstruct usage
def ensure_llmstruct_integration(func: Callable) -> Callable:
    """Decorator that ensures function uses llmstruct system."""
    def wrapper(*args, **kwargs):
        middleware = get_ai_middleware()
        if middleware is None:
            logger.warning(f"Function {func.__name__} called without AI middleware - consider initializing")
            return func(*args, **kwargs)
        
        # Extract query from function args/kwargs
        query = kwargs.get('query') or (args[0] if args else "Unknown query")
        
        # Process through middleware
        result = middleware.process_ai_request(str(query), 
                                             lambda q, ctx: func(*args, **kwargs))
        
        return result.content
    
    return wrapper 