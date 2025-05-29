"""
LLM Service

Integrates with existing LLM models and context orchestration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from ...context_orchestrator import ContextOrchestrator
from ...copilot_manager import CopilotManager

logger = logging.getLogger(__name__)

class LLMResponse:
    """Response from LLM processing"""
    
    def __init__(self, content: str, context_info: Dict[str, Any] = None, token_usage: Dict[str, int] = None):
        self.content = content
        self.context_info = context_info or {}
        self.token_usage = token_usage or {"input": 0, "output": 0}
        self.timestamp = datetime.now().isoformat()

class LLMService:
    """Service for LLM processing with context integration"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.context_orchestrator = None
        self.copilot_manager = None
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize context orchestrator and copilot manager"""
        try:
            # Initialize context orchestrator
            self.context_orchestrator = ContextOrchestrator(
                project_root=str(self.base_path)
            )
            logger.info("Context orchestrator initialized")
            
            # Initialize copilot manager
            self.copilot_manager = CopilotManager()
            logger.info("Copilot manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM components: {e}")
            # Continue without context integration
            
    async def process_message(self, message: str, session_id: str = None, context_mode: str = "focused") -> LLMResponse:
        """Process a user message and return AI response"""
        
        try:
            # Get context based on mode
            context_info = await self._get_context(message, context_mode)
            
            # For now, use a simple mock response
            # TODO: Integrate with actual LLM (Anthropic, OpenAI, etc.)
            response_content = await self._generate_mock_response(message, context_info)
            
            return LLMResponse(
                content=response_content,
                context_info=context_info,
                token_usage={"input": len(message), "output": len(response_content)}
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return LLMResponse(
                content=f"Sorry, I encountered an error processing your message: {str(e)}",
                context_info={"error": str(e)},
                token_usage={"input": 0, "output": 0}
            )
            
    async def _get_context(self, message: str, context_mode: str) -> Dict[str, Any]:
        """Get relevant context for the message"""
        
        context_info = {
            "mode": context_mode,
            "files_analyzed": 0,
            "functions_found": 0,
            "relevant_modules": []
        }
        
        if not self.context_orchestrator:
            return context_info
            
        try:
            if context_mode == "full":
                # Full project context
                context = await self._get_full_context()
            elif context_mode == "focused":
                # Focused context based on message
                context = await self._get_focused_context(message)
            elif context_mode == "minimal":
                # Minimal context - just current state
                context = await self._get_minimal_context()
            else:
                context = {}
                
            context_info.update(context)
            
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            context_info["context_error"] = str(e)
            
        return context_info
        
    async def _get_full_context(self) -> Dict[str, Any]:
        """Get full project context"""
        # Load struct.json if available
        struct_file = self.base_path / "struct.json"
        if struct_file.exists():
            with open(struct_file, 'r') as f:
                struct_data = json.load(f)
                return {
                    "files_analyzed": len(struct_data.get("files", [])),
                    "functions_found": len(struct_data.get("functions", [])),
                    "modules": list(struct_data.get("modules", {}).keys())[:10]  # Limit output
                }
        return {}
        
    async def _get_focused_context(self, message: str) -> Dict[str, Any]:
        """Get focused context based on message content"""
        # Simple keyword-based context selection
        keywords = message.lower().split()
        
        context = {"keywords": keywords[:5]}  # Limit keywords
        
        # Check if message mentions specific files or modules
        if any(word in message.lower() for word in ["fastapi", "api", "endpoint"]):
            context["relevant_modules"] = ["fastapi", "api"]
        elif any(word in message.lower() for word in ["cli", "command"]):
            context["relevant_modules"] = ["cli"]
        elif any(word in message.lower() for word in ["context", "orchestrator"]):
            context["relevant_modules"] = ["context_orchestrator"]
            
        return context
        
    async def _get_minimal_context(self) -> Dict[str, Any]:
        """Get minimal context - basic project info"""
        return {
            "project_root": str(self.base_path),
            "timestamp": datetime.now().isoformat()
        }
        
    async def _generate_mock_response(self, message: str, context_info: Dict[str, Any]) -> str:
        """Generate a mock AI response (placeholder for real LLM)"""
        
        # Check for specific patterns and respond accordingly
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return f"Hello! I'm the LLMStruct AI Assistant. I can help you with your project using {context_info.get('mode', 'focused')} context mode. What would you like to know?"
            
        elif "api" in message_lower or "fastapi" in message_lower:
            return f"I can help with FastAPI development! Currently analyzing {context_info.get('files_analyzed', 0)} files in the project. The API system includes WebSocket support, authentication middleware, and CLI integration."
            
        elif "cli" in message_lower:
            return f"The CLI system supports commands like parse, query, interactive, context, and more. I can help you understand how to use these commands or integrate them with the API."
            
        elif "context" in message_lower:
            return f"Context management is handled by the ContextOrchestrator. Current mode: {context_info.get('mode')}. I found {context_info.get('functions_found', 0)} functions and {len(context_info.get('relevant_modules', []))} relevant modules."
            
        elif "help" in message_lower:
            return """I can assist with:
• FastAPI development and WebSocket integration
• CLI command usage and integration  
• Context orchestration and management
• Project structure analysis
• Code debugging and optimization

What specific area would you like help with?"""
            
        else:
            # Generic response with context info
            modules_info = ""
            if context_info.get("relevant_modules"):
                modules_info = f" I found these relevant modules: {', '.join(context_info['relevant_modules'])}."
                
            return f"I understand you're asking about: {message}. Using {context_info.get('mode', 'focused')} context mode.{modules_info} How can I help you with this specific topic?" 