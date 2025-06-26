"""
Chat Routes

WebSocket-based real-time chat with LLM integration
"""

import json
import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import logging

from ..middleware.auth import get_api_key
from ..services.llm_service import LLMService
from ..services.chat_session import ChatSessionManager
from ..models.requests import ChatMessage
from ..models.responses import ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Global session manager
session_manager = ChatSessionManager()
llm_service = LLMService()

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
        
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
            
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/chat/ws")
async def websocket_chat(websocket: WebSocket, session_id: str = None, api_key: str = None):
    """WebSocket endpoint for real-time chat"""
    
    # Basic auth for WebSocket (optional)
    if api_key and api_key != "dev-key":
        await websocket.close(code=4001, reason="Invalid API key")
        return
        
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        
    await manager.connect(websocket, session_id)
    
    # Initialize session
    session = await session_manager.get_or_create_session(session_id)
    
    try:
        # Send welcome message
        await manager.send_message(session_id, {
            "type": "welcome",
            "session_id": session_id,
            "message": "Connected to LLMStruct AI Assistant",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            context_mode = message_data.get("context_mode", "focused")
            
            logger.info(f"[{session_id}] User message: {user_message}")
            
            # Add user message to session
            await session_manager.add_message(session_id, "user", user_message)
            
            # Send typing indicator
            await manager.send_message(session_id, {
                "type": "typing",
                "timestamp": datetime.now().isoformat()
            })
            
            try:
                # Process with LLM
                response = await llm_service.process_message(
                    message=user_message,
                    session_id=session_id,
                    context_mode=context_mode
                )
                
                # Add AI response to session
                await session_manager.add_message(session_id, "assistant", response.content)
                
                # Send response to client
                await manager.send_message(session_id, {
                    "type": "message",
                    "content": response.content,
                    "context_used": response.context_info,
                    "timestamp": datetime.now().isoformat(),
                    "token_usage": response.token_usage
                })
                
            except Exception as e:
                logger.error(f"LLM processing error: {e}")
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": f"Processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"Client {session_id} disconnected")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)

@router.get("/chat/sessions", dependencies=[Depends(get_api_key)])
async def list_sessions():
    """List active chat sessions"""
    sessions = await session_manager.list_sessions()
    return {"sessions": sessions}

@router.get("/chat/sessions/{session_id}", dependencies=[Depends(get_api_key)])
async def get_session(session_id: str):
    """Get session details and history"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/chat/sessions/{session_id}", dependencies=[Depends(get_api_key)])
async def delete_session(session_id: str):
    """Delete a chat session"""
    deleted = await session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}

@router.post("/chat/message", dependencies=[Depends(get_api_key)])
async def send_message(message: ChatMessage):
    """Send a message via HTTP (alternative to WebSocket)"""
    try:
        response = await llm_service.process_message(
            message=message.content,
            session_id=message.session_id,
            context_mode=message.context_mode
        )
        
        # Add to session if session_id provided
        if message.session_id:
            await session_manager.add_message(message.session_id, "user", message.content)
            await session_manager.add_message(message.session_id, "assistant", response.content)
        
        return ChatResponse(
            content=response.content,
            session_id=message.session_id,
            context_info=response.context_info,
            token_usage=response.token_usage
        )
        
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 