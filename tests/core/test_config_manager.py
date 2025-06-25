"""Tests for ConfigManager and configuration system.

Tests the LLM-optional architecture with security-first defaults.
"""

import os
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_default_configuration():
    """Test that LLM is disabled by default for security."""
    from llmstruct.core.config_manager import get_config_manager, is_llm_enabled
    
    # Test default configuration
    config_manager = get_config_manager()
    config = config_manager.get_config()
    
    # LLM should be disabled by default
    assert config.enable_llm == False, "LLM should be disabled by default"
    assert config.llm.enabled == False, "LLM provider should be disabled by default"
    assert is_llm_enabled() == False, "is_llm_enabled() should return False by default"


def test_offline_mode_environment():
    """Test offline mode via environment variable."""
    from llmstruct.core.config_manager import get_config_manager
    
    # Test offline mode environment variable
    os.environ["LLMSTRUCT_OFFLINE"] = "1"
    config_manager = get_config_manager()
    config_manager._config = None  # Reset config
    config = config_manager.get_config()
    
    assert config.security.offline_mode == True, "Offline mode should be enabled via env var"
    assert config.enable_llm == False, "LLM should be disabled in offline mode"
    
    # Clean up
    if "LLMSTRUCT_OFFLINE" in os.environ:
        del os.environ["LLMSTRUCT_OFFLINE"]


def test_llm_enable_environment():
    """Test LLM enablement via environment variable."""
    from llmstruct.core.config_manager import get_config_manager
    
    # Test LLM enable environment variable
    os.environ["LLMSTRUCT_ENABLE_LLM"] = "1"
    config_manager = get_config_manager()
    config_manager._config = None  # Reset config
    config = config_manager.get_config()
    
    assert config.enable_llm == True, "LLM should be enabled via env var"
    assert config.llm.enabled == True, "LLM provider should be enabled via env var"
    
    # Clean up
    if "LLMSTRUCT_ENABLE_LLM" in os.environ:
        del os.environ["LLMSTRUCT_ENABLE_LLM"]


def test_config_manager():
    """Run all ConfigManager tests."""
    print("Testing Configuration Manager...")
    
    test_default_configuration()
    test_offline_mode_environment()
    test_llm_enable_environment()
    
    print("✓ Configuration Manager tests passed")


if __name__ == "__main__":
    test_config_manager() 