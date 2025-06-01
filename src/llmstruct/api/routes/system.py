"""
System routes for LLMStruct FastAPI

Health checks, metrics, and system information endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import asyncio

from ..models.responses import HealthResponse, HealthStatus
from ..services.cli_bridge import CLIBridge

router = APIRouter()


def get_cli_bridge():
    """Dependency to get CLI bridge instance"""
    return CLIBridge()


@router.get("/health", response_model=HealthResponse)
async def health_check(cli: CLIBridge = Depends(get_cli_bridge)):
    """
    Health check endpoint
    
    Returns the health status of the API and its dependencies.
    This endpoint does not require authentication.
    """
    try:
        # Check CLI availability
        cli_health = await cli.health_check()
        
        # Determine overall status
        if cli_health.get("cli_available", False):
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.UNHEALTHY
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            cli_available=cli_health.get("cli_available", False),
            version_info=cli_health.get("version_info", "Unknown"),
            dependencies={
                "cli": cli_health.get("cli_available", False),
                "python3": True,  # If we're running, Python is available
            }
        )
        
    except Exception as e:
        return HealthResponse(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.utcnow(),
            cli_available=False,
            version_info=f"Error: {str(e)}",
            dependencies={
                "cli": False,
                "python3": True,
            }
        )


@router.get("/status")
async def get_system_status():
    """
    Get detailed system status
    
    Returns detailed system information including:
    - API version and configuration
    - CLI status and version
    - Resource usage (if available)
    """
    try:
        cli = CLIBridge()
        cli_health = await cli.health_check()
        
        return {
            "api": {
                "name": "LLMStruct API",
                "version": "0.1.0",
                "status": "running",
                "timestamp": datetime.utcnow().isoformat()
            },
            "cli": {
                "available": cli_health.get("cli_available", False),
                "version": cli_health.get("version_info", "Unknown"),
                "status": cli_health.get("status", "unknown")
            },
            "system": {
                "python_version": "3.x",
                "platform": "unknown"  # Could add platform.platform() if needed
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to get system status: {str(e)}")


@router.get("/version")
async def get_version():
    """
    Get API version information
    
    Returns version information for the API and underlying components.
    """
    try:
        cli = CLIBridge()
        cli_health = await cli.health_check()
        
        return {
            "api_version": "0.1.0",
            "cli_version": cli_health.get("version_info", "Unknown"),
            "build_timestamp": datetime.utcnow().isoformat(),
            "components": {
                "fastapi": "0.104.0+",
                "pydantic": "2.5.0+",
                "uvicorn": "0.24.0+"
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to get version info: {str(e)}")


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity testing
    """
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    } 