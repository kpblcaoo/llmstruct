"""
Chat Session Manager

Manages persistent chat sessions and conversation history
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChatSession:
    """Represents a chat session with history"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now().isoformat()
        self.last_activity = self.created_at
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the session"""
        message = {
            "id": len(self.messages) + 1,
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_activity = message["timestamp"]
        
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages from session, optionally limited"""
        if limit:
            return self.messages[-limit:]
        return self.messages
        
    def get_context_string(self, limit: int = 10) -> str:
        """Get recent messages as context string"""
        recent_messages = self.get_messages(limit)
        context_parts = []
        
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
            
        return "\n".join(context_parts)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages),
            "messages": self.messages,
            "metadata": self.metadata
        }

class ChatSessionManager:
    """Manages multiple chat sessions"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.cwd() / "data" / "chat_sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, ChatSession] = {}
        
    async def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            # Try to load from storage
            session_file = self.storage_path / f"{session_id}.json"
            if session_file.exists():
                session = await self._load_session(session_id)
            else:
                session = ChatSession(session_id)
                
            self.sessions[session_id] = session
            
        return self.sessions[session_id]
        
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        if session_id in self.sessions:
            return self.sessions[session_id]
            
        # Try to load from storage
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            session = await self._load_session(session_id)
            self.sessions[session_id] = session
            return session
            
        return None
        
    async def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to session"""
        session = await self.get_or_create_session(session_id)
        session.add_message(role, content, metadata)
        
        # Save to storage
        await self._save_session(session)
        
    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all sessions with summary info"""
        sessions = []
        
        # Load session files from storage
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            try:
                if session_id not in self.sessions:
                    session = await self._load_session(session_id)
                    self.sessions[session_id] = session
                else:
                    session = self.sessions[session_id]
                    
                sessions.append({
                    "session_id": session.session_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "message_count": len(session.messages)
                })
                
            except Exception as e:
                logger.error(f"Error loading session {session_id}: {e}")
                continue
                
        # Sort by last activity
        sessions.sort(key=lambda x: x["last_activity"], reverse=True)
        return sessions[:limit]
        
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        # Remove from memory
        if session_id in self.sessions:
            del self.sessions[session_id]
            
        # Remove from storage
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            return True
            
        return False
        
    async def _load_session(self, session_id: str) -> ChatSession:
        """Load session from storage"""
        session_file = self.storage_path / f"{session_id}.json"
        
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        session = ChatSession(session_id)
        session.created_at = data.get("created_at", session.created_at)
        session.last_activity = data.get("last_activity", session.last_activity)
        session.messages = data.get("messages", [])
        session.metadata = data.get("metadata", {})
        
        return session
        
    async def _save_session(self, session: ChatSession):
        """Save session to storage"""
        session_file = self.storage_path / f"{session.session_id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
            
    async def cleanup_old_sessions(self, days: int = 30):
        """Clean up sessions older than specified days"""
        # TODO: Implement cleanup logic
        pass 