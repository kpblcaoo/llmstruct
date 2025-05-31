"""
Request models for LLMStruct FastAPI
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ContextMode(str, Enum):
    FULL = "FULL"
    FOCUSED = "FOCUSED"
    MINIMAL = "MINIMAL"
    SESSION = "SESSION"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ScanRequest(BaseModel):
    """Request model for project scanning"""
    output_path: Optional[str] = Field(None, description="Path to save scan results")
    include_patterns: List[str] = Field(default_factory=list, description="File patterns to include")
    exclude_patterns: List[str] = Field(default_factory=list, description="File patterns to exclude")
    deep_analysis: bool = Field(False, description="Enable deep analysis mode")
    
    class Config:
        schema_extra = {
            "example": {
                "include_patterns": ["*.py", "*.js"],
                "exclude_patterns": ["*.test.*", "node_modules/*"],
                "deep_analysis": False
            }
        }


class ContextRequest(BaseModel):
    """Request model for context generation"""
    mode: ContextMode = Field(..., description="Context generation mode")
    include_files: List[str] = Field(default_factory=list, description="Specific files to include")
    query: Optional[str] = Field(None, description="Query hint for AI optimization")
    
    class Config:
        schema_extra = {
            "example": {
                "mode": "FOCUSED",
                "include_files": ["src/main.py", "src/utils.py"],
                "query": "authentication functions"
            }
        }


class TaskCreateRequest(BaseModel):
    """Request model for creating tasks"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    estimated_effort: Optional[int] = Field(None, description="Estimated effort in hours")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Add FastAPI endpoints",
                "description": "Implement REST API endpoints for project scanning",
                "priority": "high",
                "tags": ["api", "backend"],
                "estimated_effort": 8
            }
        }


class TaskUpdateRequest(BaseModel):
    """Request model for updating tasks"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    estimated_effort: Optional[int] = None
    status: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "completed",
                "tags": ["api", "backend", "done"]
            }
        }


class QueryRequest(BaseModel):
    """Request model for LLM queries"""
    query: str = Field(..., min_length=1, max_length=1000, description="Query text")
    context_mode: ContextMode = Field(ContextMode.FOCUSED, description="Context mode for query")
    include_files: List[str] = Field(default_factory=list, description="Files to include in context")
    llm_model: Optional[str] = Field(None, description="Specific LLM model to use")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How does the authentication system work?",
                "context_mode": "FOCUSED",
                "include_files": ["src/auth.py"],
                "llm_model": "gpt-4"
            }
        }


class ValidationRequest(BaseModel):
    """Request model for JSON validation"""
    json_path: str = Field(..., description="Path to JSON file to validate")
    schema_path: Optional[str] = Field(None, description="Path to custom schema file")
    
    class Config:
        schema_extra = {
            "example": {
                "json_path": "output/project_structure.json",
                "schema_path": "schema/custom.json"
            }
        }


class ChatMessage(BaseModel):
    """Chat message request"""
    content: str = Field(..., description="Message content")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation history")
    context_mode: str = Field("focused", description="Context mode: full, focused, minimal, session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional message metadata") 