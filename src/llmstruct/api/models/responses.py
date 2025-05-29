"""
Response models for LLMStruct FastAPI
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ProjectInfo(BaseModel):
    """Response model for project information"""
    name: str = Field(..., description="Project name")
    version: str = Field(..., description="Project version")
    description: Optional[str] = Field(None, description="Project description")
    author: Optional[str] = Field(None, description="Project author")
    created_at: datetime = Field(..., description="Project creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    file_count: int = Field(..., description="Total number of files")
    total_lines: int = Field(..., description="Total lines of code")
    languages: List[str] = Field(..., description="Programming languages detected")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "llmstruct",
                "version": "0.4.1",
                "description": "Universal JSON format for codebases",
                "author": "Mikhail Stepanov",
                "created_at": "2024-01-01T00:00:00Z",
                "last_updated": "2024-03-26T12:00:00Z",
                "file_count": 42,
                "total_lines": 15000,
                "languages": ["Python", "JavaScript", "TypeScript"]
            }
        }


class ScanResponse(BaseModel):
    """Response model for project scan results"""
    status: str = Field(..., description="Scan status")
    scan_id: str = Field(..., description="Unique scan identifier")
    timestamp: datetime = Field(..., description="Scan completion timestamp")
    files_processed: int = Field(..., description="Number of files processed")
    output_path: Optional[str] = Field(None, description="Path to scan results file")
    summary: Dict[str, Any] = Field(..., description="Scan summary data")
    warnings: List[str] = Field(default_factory=list, description="Scan warnings")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "completed",
                "scan_id": "scan_20240326_120000",
                "timestamp": "2024-03-26T12:00:00Z",
                "files_processed": 42,
                "output_path": "/tmp/scan_results.json",
                "summary": {
                    "total_files": 42,
                    "languages": {"Python": 30, "JavaScript": 12},
                    "total_lines": 15000
                },
                "warnings": ["Large file detected: src/large_file.py"]
            }
        }


class ContextResponse(BaseModel):
    """Response model for context generation"""
    mode: str = Field(..., description="Context mode used")
    token_count: int = Field(..., description="Total token count")
    file_count: int = Field(..., description="Number of files included")
    context_data: Dict[str, Any] = Field(..., description="Generated context data")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Optimization suggestions")
    
    class Config:
        schema_extra = {
            "example": {
                "mode": "FOCUSED",
                "token_count": 2500,
                "file_count": 5,
                "context_data": {
                    "src/main.py": "def main():\n    pass",
                    "src/utils.py": "def helper():\n    pass"
                },
                "optimization_suggestions": ["Consider reducing file scope"]
            }
        }


class TaskResponse(BaseModel):
    """Response model for task operations"""
    id: str = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(..., description="Task status")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    tags: List[str] = Field(..., description="Task tags")
    estimated_effort: Optional[int] = Field(None, description="Estimated effort in hours")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "task_001",
                "title": "Add FastAPI endpoints",
                "description": "Implement REST API endpoints",
                "status": "in_progress",
                "priority": "high",
                "created_at": "2024-03-26T10:00:00Z",
                "updated_at": "2024-03-26T12:00:00Z",
                "tags": ["api", "backend"],
                "estimated_effort": 8
            }
        }


class QueryResponse(BaseModel):
    """Response model for LLM queries"""
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="LLM response")
    context_used: Dict[str, Any] = Field(..., description="Context data used")
    processing_time: float = Field(..., description="Processing time in seconds")
    token_usage: Dict[str, int] = Field(..., description="Token usage statistics")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How does authentication work?",
                "response": "The authentication system uses JWT tokens...",
                "context_used": {
                    "files": ["src/auth.py"],
                    "token_count": 1500
                },
                "processing_time": 2.5,
                "token_usage": {
                    "input_tokens": 1500,
                    "output_tokens": 300,
                    "total_tokens": 1800
                }
            }
        }


class ValidationResponse(BaseModel):
    """Response model for JSON validation"""
    valid: bool = Field(..., description="Validation result")
    file_path: str = Field(..., description="Validated file path")
    schema_used: str = Field(..., description="Schema used for validation")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "file_path": "output/project_structure.json",
                "schema_used": "default",
                "errors": [],
                "warnings": ["Large file size detected"]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health checks"""
    status: HealthStatus = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    cli_available: bool = Field(..., description="CLI availability")
    version_info: str = Field(..., description="Version information")
    dependencies: Dict[str, bool] = Field(default_factory=dict, description="Dependency status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-03-26T12:00:00Z",
                "cli_available": True,
                "version_info": "llmstruct 0.4.1",
                "dependencies": {
                    "python3": True,
                    "git": True,
                    "disk_space": True
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for API errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "CLI command failed",
                "detail": "Command timed out after 300 seconds",
                "timestamp": "2024-03-26T12:00:00Z",
                "request_id": "req_001"
            }
        } 