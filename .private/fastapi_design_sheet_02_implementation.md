# FastAPI Design Sheet #02: Implementation Plan

**Date**: 2024-03-26  
**Author**: Claude + @kpblcaoo  
**Status**: Design Phase  
**Related**: fastapi_design_sheet_01_architecture.md  

---

## 🎯 IMPLEMENTATION ROADMAP

### Week 1: Foundation (40% of work)

#### Day 1-2: Project Setup
```bash
# New directory structure
src/llmstruct/
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI app instance
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── project.py      # Project operations
│   │   ├── context.py      # Context management
│   │   ├── tasks.py        # Task operations
│   │   └── system.py       # Health, metrics
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py     # Request models
│   │   ├── responses.py    # Response models
│   │   └── common.py       # Common types
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cli_bridge.py   # CLI integration
│   │   └── auth.py         # Authentication
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py         # Auth middleware
│       └── logging.py      # Request logging
```

#### Day 3-4: Core Infrastructure
```python
# src/llmstruct/api/app.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .routes import project, context, tasks, system
from .middleware.auth import api_key_middleware
from .middleware.logging import request_logging

app = FastAPI(
    title="LLMStruct API",
    version="0.1.0",
    description="Universal codebase analysis API with LLM integration"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.middleware("http")(api_key_middleware)
app.middleware("http")(request_logging)

# Routes
app.include_router(project.router, prefix="/api/v1/project", tags=["project"])
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
```

#### Day 5-7: Basic Endpoints
```python
# src/llmstruct/api/services/cli_bridge.py
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional
from pathlib import Path

class CLIBridge:
    """Bridge between FastAPI and existing CLI functionality"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        
    async def scan_project(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project scan via CLI"""
        cmd = ["python", "-m", "llmstruct.cli", "scan"]
        
        if options.get("output_path"):
            cmd.extend(["--output", options["output_path"]])
            
        if options.get("include_patterns"):
            for pattern in options["include_patterns"]:
                cmd.extend(["--include", pattern])
                
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def get_context(self, mode: str) -> Dict[str, Any]:
        """Get project context in specified mode"""
        cmd = ["python", "-m", "llmstruct.cli", "context", "--mode", mode]
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def _run_command(self, cmd: list) -> str:
        """Run CLI command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.base_path
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"CLI command failed: {stderr.decode()}")
            
        return stdout.decode()
    
    def _parse_cli_output(self, output: str) -> Dict[str, Any]:
        """Parse CLI JSON output"""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Handle non-JSON output
            return {"output": output, "type": "text"}
```

### Week 2: Core Endpoints (30% of work)

#### Project Operations
```python
# src/llmstruct/api/routes/project.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List

from ..models.requests import ScanRequest, ContextRequest
from ..models.responses import ScanResponse, ContextResponse, ProjectInfo
from ..services.cli_bridge import CLIBridge

router = APIRouter()

@router.get("/info", response_model=ProjectInfo)
async def get_project_info(cli: CLIBridge = Depends()):
    """Get basic project information"""
    try:
        result = await cli.get_project_info()
        return ProjectInfo(**result)
    except Exception as e:
        raise HTTPException(500, f"Failed to get project info: {str(e)}")

@router.post("/scan", response_model=ScanResponse)
async def scan_project(
    request: ScanRequest,
    cli: CLIBridge = Depends()
):
    """Scan project structure and generate analysis"""
    try:
        options = request.dict(exclude_none=True)
        result = await cli.scan_project(options)
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Scan failed: {str(e)}")

@router.get("/context/{mode}", response_model=ContextResponse)
async def get_project_context(
    mode: str,
    include_files: Optional[List[str]] = None,
    cli: CLIBridge = Depends()
):
    """Get project context in specified mode"""
    if mode not in ["FULL", "FOCUSED", "MINIMAL", "SESSION"]:
        raise HTTPException(400, "Invalid context mode")
    
    try:
        result = await cli.get_context(mode)
        return ContextResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Context generation failed: {str(e)}")
```

#### Models Definition
```python
# src/llmstruct/api/models/requests.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ScanRequest(BaseModel):
    output_path: Optional[str] = None
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)
    deep_analysis: bool = False
    
class ContextRequest(BaseModel):
    mode: str = Field(..., regex="^(FULL|FOCUSED|MINIMAL|SESSION)$")
    include_files: List[str] = Field(default_factory=list)
    query: Optional[str] = None

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium", regex="^(low|medium|high|urgent)$")
    tags: List[str] = Field(default_factory=list)
    estimated_effort: Optional[int] = None  # hours

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    context_mode: str = Field(default="FOCUSED")
    include_files: List[str] = Field(default_factory=list)
    llm_model: Optional[str] = None
```

```python
# src/llmstruct/api/models/responses.py
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class ProjectInfo(BaseModel):
    name: str
    version: str
    description: Optional[str]
    author: Optional[str]
    created_at: datetime
    last_updated: datetime
    file_count: int
    total_lines: int
    languages: List[str]

class ScanResponse(BaseModel):
    status: str
    scan_id: str
    timestamp: datetime
    files_processed: int
    output_path: Optional[str]
    summary: Dict[str, Any]
    warnings: List[str] = []

class ContextResponse(BaseModel):
    mode: str
    token_count: int
    file_count: int
    context_data: Dict[str, Any]
    optimization_suggestions: List[str] = []

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    estimated_effort: Optional[int]

class QueryResponse(BaseModel):
    query: str
    response: str
    context_used: Dict[str, Any]
    processing_time: float
    token_usage: Dict[str, int]
```

### Week 3: Advanced Features (20% of work)

#### Authentication & Security
```python
# src/llmstruct/api/middleware/auth.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

security = HTTPBearer()

async def api_key_middleware(request: Request, call_next):
    """API key authentication middleware"""
    if request.url.path == "/api/v1/system/health":
        # Health check doesn't require auth
        return await call_next(request)
    
    api_key = None
    
    # Check header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
    
    # Check X-API-Key header
    if not api_key:
        api_key = request.headers.get("X-API-Key")
    
    # Validate
    valid_key = os.getenv("LLMSTRUCT_API_KEY")
    if not valid_key or api_key != valid_key:
        raise HTTPException(401, "Invalid or missing API key")
    
    return await call_next(request)
```

#### WebSocket Support
```python
# src/llmstruct/api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, Set

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle real-time requests
            if message["type"] == "scan_progress":
                # Stream scan progress
                pass
            elif message["type"] == "context_update":
                # Stream context updates
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Week 4: Testing & Deployment (10% of work)

#### Testing Setup
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.llmstruct.api.app import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}

def test_health_check():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200

def test_project_info(auth_headers):
    response = client.get("/api/v1/project/info", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data

def test_scan_project(auth_headers):
    request_data = {
        "include_patterns": ["*.py"],
        "deep_analysis": False
    }
    response = client.post(
        "/api/v1/project/scan", 
        json=request_data,
        headers=auth_headers
    )
    assert response.status_code == 200
```

#### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.llmstruct.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔧 CONFIGURATION MANAGEMENT

### Environment Variables
```python
# src/llmstruct/api/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_key: str = "dev-key"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CLI Integration
    cli_timeout: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    
    # Cache Settings
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_prefix = "LLMSTRUCT_"
        env_file = ".env"

settings = Settings()
```

---

## 📊 MONITORING & METRICS

### Metrics Collection
```python
# src/llmstruct/api/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

---

## 🚀 DEPLOYMENT STRATEGY

### Development
```bash
# Start development server
uvicorn src.llmstruct.api.app:app --reload --host 0.0.0.0 --port 8000

# Environment setup
export LLMSTRUCT_API_KEY="dev-key-$(date +%s)"
export LLMSTRUCT_DEBUG=true
```

### Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLMSTRUCT_API_KEY=${API_KEY}
      - LLMSTRUCT_DEBUG=false
      - LLMSTRUCT_LOG_LEVEL=INFO
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

---

## ✅ COMPLETION CHECKLIST

### Week 1
- [ ] Project structure created
- [ ] FastAPI app setup with basic middleware
- [ ] CLI bridge service implemented
- [ ] Basic health check endpoint
- [ ] Authentication middleware

### Week 2  
- [ ] All project endpoints implemented
- [ ] Context management endpoints
- [ ] Task management endpoints
- [ ] Request/response models defined
- [ ] Error handling implementation

### Week 3
- [ ] WebSocket support for real-time updates
- [ ] Rate limiting implementation
- [ ] Caching layer
- [ ] Metrics collection
- [ ] Security hardening

### Week 4
- [ ] Comprehensive test suite
- [ ] Docker configuration
- [ ] Production deployment setup
- [ ] API documentation
- [ ] Performance benchmarking

---

*Next: Design Sheet #03 - Custom Implementation Strategy* 