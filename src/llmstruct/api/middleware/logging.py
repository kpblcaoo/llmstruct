"""
Logging middleware for LLMStruct FastAPI
"""

from fastapi import Request
import time
import logging
import uuid
from typing import Callable

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next: Callable):
    """Request and response logging middleware"""
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    # Log request start
    start_time = time.time()
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - Start",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "authenticated": getattr(request.state, "authenticated", False)
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log successful response
        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
                "authenticated": getattr(request.state, "authenticated", False)
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Log error
        duration = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - ERROR ({duration:.3f}s): {str(e)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration": duration,
                "error": str(e),
                "authenticated": getattr(request.state, "authenticated", False)
            }
        )
        raise 