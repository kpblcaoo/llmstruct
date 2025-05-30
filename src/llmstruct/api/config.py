"""
Configuration management for LLMStruct FastAPI
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_key: str = "dev-key"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    allowed_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # CLI Integration
    cli_timeout: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    
    # Caching
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    model_config = {
        "env_prefix": "LLMSTRUCT_",
        "env_file": ".env",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings() 