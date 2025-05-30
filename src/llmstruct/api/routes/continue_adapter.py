"""
Continue API Adapter

Translates Continue extension requests to LLMStruct chat API format
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..middleware.auth import get_api_key
from ..models.requests import ChatMessage
from ..models.responses import ChatResponse
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/continue", tags=["Continue Integration"])

# Initialize LLM service
llm_service = LLMService()

class ContinueRequest:
    """Continue API request format"""
    def __init__(self, 
                 messages: List[Dict[str, str]], 
                 model: str = "claude-3-haiku",
                 temperature: float = 0.7,
                 max_tokens: int = 1000,
                 stream: bool = False):
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

class ContinueResponse:
    """Continue API response format (OpenAI-compatible)"""
    def __init__(self, content: str, model: str = "claude-3-haiku"):
        self.id = f"continue-{datetime.now().isoformat()}"
        self.object = "chat.completion"
        self.created = int(datetime.now().timestamp())
        self.model = model
        self.choices = [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
            },
            "finish_reason": "stop"
        }]
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": len(content.split()),
            "total_tokens": len(content.split())
        }

@router.post("/v1/chat/completions")
async def continue_chat_completion(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    """
    Continue-compatible chat completion endpoint
    Translates Continue requests to our LLMStruct format
    """
    try:
        # Get JSON data from request
        request_data = await request.json()
        
        # Extract request data
        messages = request_data.get("messages", [])
        model = request_data.get("model", "claude-3-haiku")
        temperature = request_data.get("temperature", 0.7)
        stream = request_data.get("stream", False)
        
        logger.info(f"Continue API request: {len(messages)} messages, model: {model}")
        
        # Convert to our internal format
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Add context about Continue integration
        context_prompt = """You are integrated with VS Code through Continue extension. 
You have access to the current file context and can see the code the user is working on.
Be helpful with code suggestions, explanations, and improvements.
Focus on clean, maintainable code that follows LLMStruct project patterns."""
        
        enhanced_message = f"{context_prompt}\n\nUser request: {user_message}"
        
        # Process through our LLM service
        session_id = f"continue-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        llm_response = await llm_service.process_message(
            message=enhanced_message,
            session_id=session_id,
            context_mode="focused"
        )
        
        # Convert to Continue format
        continue_response = ContinueResponse(
            content=llm_response.content,
            model=model
        )
        
        logger.info(f"Continue API response: {len(llm_response.content)} chars")
        
        return {
            "id": continue_response.id,
            "object": continue_response.object,
            "created": continue_response.created,
            "model": continue_response.model,
            "choices": continue_response.choices,
            "usage": continue_response.usage
        }
        
    except Exception as e:
        logger.error(f"Continue API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/models")
async def continue_models(api_key: str = Depends(get_api_key)):
    """
    List available models for Continue
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "claude-3-haiku",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "llmstruct",
                "permission": [],
                "root": "claude-3-haiku",
                "parent": None
            },
            {
                "id": "llmstruct-context",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "llmstruct",
                "permission": [],
                "root": "llmstruct-context",
                "parent": None
            }
        ]
    }

@router.post("/v1/embeddings")
async def continue_embeddings(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    """
    Embeddings endpoint for Continue (placeholder)
    """
    try:
        # Get JSON data from request
        request_data = await request.json()
        
        # For now, return empty embeddings
        # In the future, we can integrate with our context system
        input_text = request_data.get("input", "")
        
        return {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.0] * 1536,  # Dummy embedding
                    "index": 0
                }
            ],
            "model": request_data.get("model", "text-embedding-ada-002"),
            "usage": {
                "prompt_tokens": len(input_text.split()),
                "total_tokens": len(input_text.split())
            }
        }
    except Exception as e:
        logger.error(f"Continue embeddings error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 