# FastAPI Implementation Plan: From Design to Production

**Date**: 2024-03-26  
**Author**: Claude + @kpblcaoo  
**Status**: Ready for Implementation  
**Based on**: Design Sheets #01-03  

---

## 🎯 EXECUTIVE SUMMARY

**Goal**: Implement FastAPI layer for LLMStruct to enable HTTP/REST access to CLI functionality, with migration path to custom high-performance implementation.

**Timeline**: 4 weeks to MVP, 8 weeks to production-ready with migration strategy  
**Resources**: 1 developer, 40-60 hours per month  
**ROI**: Enables LLM API access goal, opens path to broader adoption  

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: FastAPI MVP (Weeks 1-2)

#### Week 1: Foundation & Infrastructure
**Goal**: Basic FastAPI app with CLI bridge

**Day 1-2: Project Setup**
```bash
# Create API module structure
mkdir -p src/llmstruct/api/{routes,models,services,middleware}

# Add FastAPI dependencies to pyproject.toml
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
```

**Day 3-4: Core Infrastructure**
- [ ] FastAPI app instance with middleware
- [ ] CLI bridge service for subprocess management
- [ ] Basic authentication (API key)
- [ ] Health check endpoint
- [ ] Request/response logging

**Day 5-7: CLI Integration**
- [ ] CLIBridge class with async subprocess execution
- [ ] Error handling and timeout management
- [ ] JSON output parsing
- [ ] Basic endpoint: `/api/v1/system/health`

**Deliverable**: Working FastAPI server that can execute CLI commands

#### Week 2: Core Endpoints
**Goal**: All major CLI functions accessible via HTTP

**Day 8-10: Project Operations**
- [ ] `/api/v1/project/info` - Project metadata
- [ ] `/api/v1/project/scan` - Project scanning
- [ ] `/api/v1/project/context/{mode}` - Context generation
- [ ] Request/response models with validation

**Day 11-12: Task Management**
- [ ] `/api/v1/tasks` - CRUD operations for tasks
- [ ] `/api/v1/tasks/{id}` - Individual task operations
- [ ] Task filtering and search

**Day 13-14: Testing & Documentation**
- [ ] Unit tests for all endpoints
- [ ] Integration tests with real CLI
- [ ] OpenAPI documentation
- [ ] Basic error handling

**Deliverable**: Full REST API with all CLI functionality

### Phase 2: Production Features (Weeks 3-4)

#### Week 3: Advanced Features
**Goal**: Production-ready features and performance

**Day 15-17: Real-time Features**
- [ ] WebSocket endpoint for streaming updates
- [ ] Real-time scan progress
- [ ] Context update notifications
- [ ] Connection management

**Day 18-19: Performance & Security**
- [ ] Request rate limiting
- [ ] Response caching (Redis optional)
- [ ] Security headers and CORS
- [ ] Input validation and sanitization

**Day 20-21: Monitoring**
- [ ] Prometheus metrics
- [ ] Request/response time tracking
- [ ] Error rate monitoring
- [ ] Health check with dependencies

**Deliverable**: Production-ready API with monitoring

#### Week 4: Deployment & Documentation
**Goal**: Ready for production deployment

**Day 22-24: Deployment**
- [ ] Docker configuration
- [ ] docker-compose for development
- [ ] Production deployment scripts
- [ ] Environment configuration management

**Day 25-26: Documentation & Testing**
- [ ] Complete API documentation
- [ ] User guide and examples
- [ ] Load testing and benchmarking
- [ ] Performance optimization

**Day 27-28: Integration**
- [ ] Integration with existing CLI workflows
- [ ] Testing with Cursor/VS Code
- [ ] Bug fixes and polish

**Deliverable**: Production-deployed FastAPI service

---

## 🛠️ TECHNICAL IMPLEMENTATION

### Directory Structure
```
src/llmstruct/
├── api/
│   ├── __init__.py
│   ├── app.py                 # FastAPI app instance
│   ├── config.py              # Configuration management
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── project.py         # Project operations
│   │   ├── context.py         # Context management  
│   │   ├── tasks.py           # Task CRUD
│   │   ├── system.py          # Health & metrics
│   │   └── websocket.py       # Real-time updates
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py        # Pydantic request models
│   │   ├── responses.py       # Pydantic response models
│   │   └── common.py          # Shared types
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cli_bridge.py      # CLI integration
│   │   ├── auth.py            # Authentication
│   │   └── cache.py           # Caching service
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py            # Auth middleware
│       ├── logging.py         # Request logging
│       └── rate_limit.py      # Rate limiting
├── cli.py                     # Existing CLI (unchanged)
└── ...                        # Existing modules
```

### Key Files to Create

#### 1. FastAPI App (`src/llmstruct/api/app.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import project, context, tasks, system, websocket
from .middleware.auth import api_key_middleware
from .middleware.logging import request_logging_middleware

app = FastAPI(
    title="LLMStruct API",
    version="0.1.0",
    description="Universal codebase analysis API with LLM integration"
)

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.middleware("http")(api_key_middleware)
app.middleware("http")(request_logging_middleware)

# Routes
app.include_router(project.router, prefix="/api/v1/project", tags=["project"])
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["websocket"])
```

#### 2. CLI Bridge (`src/llmstruct/api/services/cli_bridge.py`)
```python
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional
from pathlib import Path

class CLIBridge:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        
    async def scan_project(self, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ["python", "-m", "llmstruct.cli", "scan"]
        
        if options.get("output_path"):
            cmd.extend(["--output", options["output_path"]])
            
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def _run_command(self, cmd: list) -> str:
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
```

#### 3. Configuration (`src/llmstruct/api/config.py`)
```python
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    api_key: str = "dev-key"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    allowed_origins: List[str] = ["*"]
    
    # CLI Integration
    cli_timeout: int = 300
    max_concurrent_requests: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "LLMSTRUCT_"
        env_file = ".env"

settings = Settings()
```

---

## 🚀 DEPLOYMENT STRATEGY

### Development Setup
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Set environment variables
export LLMSTRUCT_API_KEY="dev-key-$(date +%s)"
export LLMSTRUCT_DEBUG=true

# Start development server
uvicorn src.llmstruct.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy source code
COPY src/ ./src/
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.llmstruct.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Deployment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  llmstruct-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLMSTRUCT_API_KEY=${API_KEY}
      - LLMSTRUCT_DEBUG=false
      - LLMSTRUCT_LOG_LEVEL=INFO
    restart: unless-stopped
    volumes:
      - ./data:/app/data:ro  # Read-only access to project data
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - llmstruct-api
```

---

## 🧪 TESTING STRATEGY

### Unit Tests
```python
# tests/api/test_project.py
import pytest
from fastapi.testclient import TestClient
from src.llmstruct.api.app import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}

def test_project_scan(auth_headers):
    response = client.post(
        "/api/v1/project/scan",
        json={"include_patterns": ["*.py"]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
```

### Integration Tests
```python
# tests/api/test_integration.py
def test_full_workflow():
    # 1. Scan project
    scan_response = client.post("/api/v1/project/scan", ...)
    
    # 2. Get context
    context_response = client.get("/api/v1/project/context/FOCUSED", ...)
    
    # 3. Create task
    task_response = client.post("/api/v1/tasks", ...)
    
    # Verify workflow
    assert all responses successful
```

### Load Testing
```python
# tests/load/test_performance.py
import asyncio
import aiohttp

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):  # 100 concurrent requests
            task = session.get('http://localhost:8000/api/v1/project/info')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        # Analyze response times
```

---

## 📊 SUCCESS METRICS

### Performance Targets
- **Response Time**: <500ms for 95th percentile (FastAPI MVP)
- **Throughput**: 100 requests/second
- **Memory Usage**: <512MB baseline
- **Error Rate**: <1% under normal load

### Functional Requirements
- **API Coverage**: 100% of CLI functionality accessible via REST
- **Documentation**: Complete OpenAPI spec with examples
- **Error Handling**: Consistent error responses
- **Security**: Authentication and input validation

---

## 🔄 MIGRATION PREPARATION

### Custom Implementation Readiness
Once FastAPI MVP is complete and performance requirements grow:

1. **Performance Monitoring**: Track when FastAPI limits are reached
2. **Core Engine Development**: Begin building direct engine integration
3. **Gradual Migration**: Traffic splitting between FastAPI and custom
4. **Compatibility Maintenance**: Ensure API contract consistency

### Migration Triggers
- Response time >200ms for 95th percentile
- Memory usage >1GB per instance  
- Need for >1000 requests/second
- Custom features requiring deep integration

---

## ✅ NEXT STEPS

### Immediate Actions (Next 7 Days)
1. **Approve implementation plan** and resource allocation
2. **Set up development environment** with FastAPI dependencies
3. **Create project structure** and initial files
4. **Begin Week 1 implementation** starting with basic app setup

### Decision Points
1. **Week 2**: Review MVP progress, adjust timeline if needed
2. **Week 4**: Evaluate performance, decide on production deployment
3. **Month 2**: Assess need for custom implementation migration

### Resource Requirements
- **Development Time**: 40-60 hours over 4 weeks
- **Infrastructure**: Development and production environments
- **Testing**: Load testing tools and staging environment

---

*Implementation plan approved and ready for execution. Target start date: Next available sprint.* 