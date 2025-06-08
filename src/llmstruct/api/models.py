from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    content: str

class ParseRequest(BaseModel):
    root_dir: str
    output: Optional[str] = None
    language: Optional[str] = None
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    include_dir: Optional[List[str]] = None
    exclude_dir: Optional[List[str]] = None
    include_ranges: Optional[bool] = False
    include_hashes: Optional[bool] = False
    goals: Optional[List[str]] = None
    use_cache: Optional[bool] = False
    modular_index: Optional[bool] = False

class ParseResponse(BaseModel):
    struct: Any

class CleanupRequest(BaseModel):
    session_id: str

class CleanupResponse(BaseModel):
    status: str 