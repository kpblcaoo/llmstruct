"""
Configuration Management System for LLMStruct

Manages global settings including LLM enablement, provider selection,
and security controls for offline mode.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class LLMConfig:
    """LLM-specific configuration"""
    enabled: bool = False  # Disabled by default for security
    provider: str = "openai"  # openai | anthropic | local
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 500
    temperature: float = 0.3
    timeout: int = 30
    cache_ttl: int = 604800  # 7 days


@dataclass
class SummaryConfig:
    """Summary generation configuration"""
    provider: str = "heuristic"  # heuristic | llm
    max_length: int = 120
    confidence_threshold: float = 0.5
    fallback_chain: list = field(default_factory=lambda: ["docstring", "heuristic", "llm"])
    enable_caching: bool = True


@dataclass
class MetricsConfig:
    """Code metrics configuration"""
    calculate_complexity: bool = True
    calculate_maintainability: bool = True
    calculate_real_loc: bool = True
    include_test_coverage: bool = True
    coverage_file_patterns: list = field(default_factory=lambda: [".coverage", "coverage.out", "coverage.xml"])


@dataclass
class SecurityConfig:
    """Security and privacy configuration"""
    offline_mode: bool = False  # Set via LLMSTRUCT_OFFLINE=1
    allow_network_calls: bool = True
    sanitize_code_snippets: bool = True
    max_code_snippet_length: int = 500


@dataclass
class LLMStructConfig:
    """Main LLMStruct configuration"""
    enable_llm: bool = False  # Global LLM switch - DISABLED by default
    llm: LLMConfig = field(default_factory=LLMConfig)
    summary: SummaryConfig = field(default_factory=SummaryConfig) 
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    def __post_init__(self):
        """Apply environment variable overrides"""
        # Check for offline mode
        if os.getenv("LLMSTRUCT_OFFLINE", "").lower() in ("1", "true", "yes"):
            self.security.offline_mode = True
            self.security.allow_network_calls = False
            self.enable_llm = False
            self.llm.enabled = False
            
        # Override LLM settings from environment
        if os.getenv("LLMSTRUCT_ENABLE_LLM", "").lower() in ("1", "true", "yes"):
            self.enable_llm = True
            self.llm.enabled = True
            
        # API key from environment
        if api_key := os.getenv("OPENAI_API_KEY"):
            self.llm.api_key = api_key


class ConfigManager:
    """Manages LLMStruct configuration with security-first defaults"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[LLMStructConfig] = None
        
    def load_config(self, config_path: Optional[str] = None) -> LLMStructConfig:
        """Load configuration from file or create default"""
        if config_path:
            self.config_path = config_path
            
        # Try to load from file
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                self._config = self._create_config_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                self._config = LLMStructConfig()
        else:
            # Use default configuration
            self._config = LLMStructConfig()
            
        return self._config
    
    def _create_config_from_dict(self, data: Dict[str, Any]) -> LLMStructConfig:
        """Create configuration from dictionary"""
        config = LLMStructConfig()
        
        # Global settings
        config.enable_llm = data.get("enable_llm", False)
        
        # LLM settings
        if llm_data := data.get("llm", {}):
            config.llm.enabled = llm_data.get("enabled", False)
            config.llm.provider = llm_data.get("provider", "openai")
            config.llm.model = llm_data.get("model", "gpt-3.5-turbo")
            config.llm.max_tokens = llm_data.get("max_tokens", 500)
            config.llm.temperature = llm_data.get("temperature", 0.3)
            
        # Summary settings
        if summary_data := data.get("summary", {}):
            config.summary.provider = summary_data.get("provider", "heuristic")
            config.summary.max_length = summary_data.get("max_length", 120)
            config.summary.confidence_threshold = summary_data.get("confidence_threshold", 0.5)
            
        # Security settings
        if security_data := data.get("security", {}):
            config.security.offline_mode = security_data.get("offline_mode", False)
            config.security.allow_network_calls = security_data.get("allow_network_calls", True)
            
        return config
    
    def get_config(self) -> LLMStructConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def is_llm_enabled(self) -> bool:
        """Check if LLM functionality is enabled"""
        config = self.get_config()
        return (
            config.enable_llm and 
            config.llm.enabled and 
            config.security.allow_network_calls and
            not config.security.offline_mode
        )
    
    def get_summary_provider(self) -> str:
        """Get active summary provider"""
        config = self.get_config()
        if self.is_llm_enabled() and config.summary.provider == "llm":
            return "llm"
        return "heuristic"
    
    def save_config_template(self, path: str):
        """Save configuration template file"""
        template = {
            "# LLMStruct Configuration": None,
            "# LLM support is DISABLED by default for security": None,
            "enable_llm": False,
            "llm": {
                "enabled": False,
                "provider": "openai",
                "model": "gpt-3.5-turbo", 
                "max_tokens": 500,
                "temperature": 0.3
            },
            "summary": {
                "provider": "heuristic",
                "max_length": 120,
                "confidence_threshold": 0.5
            },
            "metrics": {
                "calculate_real_loc": True,
                "include_test_coverage": True
            },
            "security": {
                "offline_mode": False,
                "allow_network_calls": True
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> LLMStructConfig:
    """Get current configuration"""
    return get_config_manager().get_config()


def is_llm_enabled() -> bool:
    """Check if LLM functionality is globally enabled"""
    return get_config_manager().is_llm_enabled()


def get_summary_provider() -> str:
    """Get active summary provider (heuristic or llm)"""
    return get_config_manager().get_summary_provider() 