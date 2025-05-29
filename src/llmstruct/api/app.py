"""
Main FastAPI application for LLMStruct
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

from .config import settings
from .middleware.auth import api_key_middleware
from .middleware.logging import request_logging_middleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create FastAPI app
app = FastAPI(
    title="LLMStruct API",
    version="0.1.0",
    description="""
    Universal codebase analysis API with LLM integration
    
    This API provides HTTP access to LLMStruct CLI functionality including:
    - Project scanning and analysis
    - Context generation for LLM integration  
    - Task management
    - JSON validation
    
    ## Authentication
    
    All endpoints (except health check) require API key authentication:
    - Header: `Authorization: Bearer <your-api-key>`
    - Header: `X-API-Key: <your-api-key>`
    
    ## Rate Limits
    
    - Max concurrent requests: 10
    - CLI timeout: 300 seconds
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware
app.middleware("http")(request_logging_middleware)
app.middleware("http")(api_key_middleware)

# Import and include routers (will be created next)
from .routes import system
# from .routes import project, context, tasks
# app.include_router(project.router, prefix="/api/v1/project", tags=["project"])
# app.include_router(context.router, prefix="/api/v1/context", tags=["context"])  
# app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LLMStruct API",
        "version": "0.1.0",
        "description": "Universal codebase analysis API with LLM integration",
        "docs_url": "/docs",
        "health_check": "/api/v1/system/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "llmstruct.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 