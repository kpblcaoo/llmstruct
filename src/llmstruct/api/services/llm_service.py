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
import os
import httpx

from ...context_orchestrator import SmartContextOrchestrator
from ...copilot import CopilotContextManager

logger = logging.getLogger(__name__)

class LLMResponse:
    """Response from LLM processing"""
    
    def __init__(self, content: str, context_info: Dict[str, Any] = None, token_usage: Dict[str, int] = None):
        self.content = content
        self.context_info = context_info or {}
        self.token_usage = token_usage or {"input": 0, "output": 0}
        self.timestamp = datetime.now().isoformat()

class AnthropicClient:
    """Client for Anthropic Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-haiku-20240307"
        
    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Send chat completion request to Anthropic"""
        
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable")
            
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages format for Anthropic
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": temperature,
            "messages": user_messages
        }
        
        if system_message:
            payload["system"] = system_message
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

class GrokClient:
    """Client for Grok API integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        self.model = "grok-beta"
        
    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Send chat completion request to Grok"""
        
        if not self.api_key:
            raise ValueError("Grok API key not found. Set GROK_API_KEY or XAI_API_KEY environment variable")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

class LLMService:
    """Service for LLM processing with context integration"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.context_orchestrator = None
        self.copilot_manager = None
        self.grok_client = GrokClient()
        self.anthropic_client = AnthropicClient()
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize context orchestrator and copilot manager"""
        try:
            # Initialize context orchestrator
            self.context_orchestrator = SmartContextOrchestrator(
                project_root=str(self.base_path)
            )
            logger.info("Context orchestrator initialized")
            
            # Initialize copilot manager
            self.copilot_manager = CopilotContextManager()
            logger.info("Copilot manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM components: {e}")
            # Continue without context integration
            
    async def process_message(self, message: str, session_id: str = None, context_mode: str = "focused") -> LLMResponse:
        """Process a user message and return AI response"""
        
        try:
            # Get context based on mode
            context_info = await self._get_context(message, context_mode)
            
            # Try LLM providers in order: Grok -> Anthropic -> Mock
            response_content, token_usage, provider_used = await self._try_llm_providers(message, context_info)
            
            # Add provider info to context
            context_info["provider_used"] = provider_used
            
            return LLMResponse(
                content=response_content,
                context_info=context_info,
                token_usage=token_usage
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return LLMResponse(
                content=f"Sorry, I encountered an error processing your message: {str(e)}",
                context_info={"error": str(e)},
                token_usage={"input": 0, "output": 0}
            )
            
    async def _try_llm_providers(self, message: str, context_info: Dict[str, Any]) -> tuple[str, Dict[str, int], str]:
        """Try LLM providers in order and return response"""
        
        # Try Grok first
        try:
            response_content = await self._generate_grok_response(message, context_info)
            token_usage = {"input": len(message), "output": len(response_content)}
            logger.info("✅ Grok API response received")
            return response_content, token_usage, "grok"
        except Exception as e:
            logger.warning(f"Grok API failed: {e}")
        
        # Try Anthropic as fallback
        try:
            response_content = await self._generate_anthropic_response(message, context_info)
            token_usage = {"input": len(message), "output": len(response_content)}
            logger.info("✅ Anthropic API response received")
            return response_content, token_usage, "anthropic"
        except Exception as e:
            logger.warning(f"Anthropic API failed: {e}")
        
        # Fallback to mock
        logger.info("🤖 Using mock response (no API keys available)")
        response_content = await self._generate_mock_response(message, context_info)
        token_usage = {"input": len(message), "output": len(response_content)}
        return response_content, token_usage, "mock"
            
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
        
    async def _generate_grok_response(self, message: str, context_info: Dict[str, Any]) -> str:
        """Generate response using Grok API"""
        
        # Build system message with context
        system_content = self._build_system_prompt(context_info)
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message}
        ]
        
        # Call Grok API
        response = await self.grok_client.chat_completion(messages)
        
        # Extract content from response
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            raise ValueError("Invalid response from Grok API")
            
    async def _generate_anthropic_response(self, message: str, context_info: Dict[str, Any]) -> str:
        """Generate response using Anthropic API"""
        
        # Build system message with context
        system_content = self._build_system_prompt(context_info)
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message}
        ]
        
        # Call Anthropic API
        response = await self.anthropic_client.chat_completion(messages)
        
        # Extract content from response
        if "content" in response and len(response["content"]) > 0:
            return response["content"][0]["text"]
        else:
            raise ValueError("Invalid response from Anthropic API")
            
    def _build_system_prompt(self, context_info: Dict[str, Any]) -> str:
        """Build system prompt with project context"""
        
        prompt = """You are an AI assistant for the LLMStruct project - a universal JSON format for codebases with LLM integration.

Current project context:
"""
        
        if context_info.get("mode"):
            prompt += f"- Context mode: {context_info['mode']}\n"
            
        if context_info.get("files_analyzed"):
            prompt += f"- Files analyzed: {context_info['files_analyzed']}\n"
            
        if context_info.get("functions_found"):
            prompt += f"- Functions found: {context_info['functions_found']}\n"
            
        if context_info.get("relevant_modules"):
            modules = ", ".join(context_info["relevant_modules"])
            prompt += f"- Relevant modules: {modules}\n"
            
        if context_info.get("keywords"):
            keywords = ", ".join(context_info["keywords"])
            prompt += f"- Query keywords: {keywords}\n"

        prompt += """
You have access to:
• FastAPI web server with WebSocket chat
• CLI tools for project analysis  
• Context orchestration system
• Session management with persistent chat history
• Project scanning and structure analysis

Be helpful, concise, and technical when appropriate. Focus on LLMStruct project specifics when relevant."""

        return prompt

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