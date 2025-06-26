"""
Global test configuration and fixtures for LLMStruct test suite.

This module provides shared fixtures, utilities, and configuration
for all test types (unit, integration, e2e, performance).
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llmstruct.core import (
    get_config_manager,
    ConfigManager,
    LLMStructConfig
)


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test fixtures and data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session") 
def sample_code_dir(test_data_dir: Path) -> Path:
    """Path to sample code fixtures."""
    return test_data_dir / "sample_code"


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test isolation."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def clean_config() -> Generator[ConfigManager, None, None]:
    """Provide clean config manager for each test."""
    # Save original env vars
    original_env = {}
    env_vars_to_clean = [
        "LLMSTRUCT_LLM_ENABLED",
        "LLMSTRUCT_OFFLINE_MODE", 
        "LLMSTRUCT_API_KEY",
        "LLMSTRUCT_SUMMARY_PROVIDER"
    ]
    
    for var in env_vars_to_clean:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    # Create clean config manager
    config_manager = ConfigManager()
    config_manager._config = None  # Reset cached config
    
    try:
        yield config_manager
    finally:
        # Restore original env vars
        for var, value in original_env.items():
            os.environ[var] = value
        
        # Reset global state
        config_manager._config = None


@pytest.fixture(scope="function")
def sample_python_code() -> str:
    """Sample Python code for testing parsers."""
    return '''
"""Sample module for testing."""

import os
from typing import List, Optional

def hello_world(name: str = "World") -> str:
    """Greet someone with a hello message.
    
    Args:
        name (str): Name to greet. Defaults to "World".
        
    Returns:
        str: Greeting message.
    """
    return f"Hello, {name}!"

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.history: List[str] = []
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers.
        
        Args:
            a (int): First number.
            b (int): Second number.
            
        Returns:
            int: Sum of a and b.
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def _private_method(self) -> None:
        """Private method for internal use."""
        pass
'''


@pytest.fixture(scope="function")
def sample_struct_data() -> Dict[str, Any]:
    """Sample structure data for testing."""
    return {
        "metadata": {
            "project_name": "test_project",
            "description": "Test project description",
            "version": "2025-01-01T00:00:00Z",
            "schema_version": "2.1.0",
            "stats": {
                "modules_count": 1,
                "functions_count": 1,
                "classes_count": 1,
                "call_edges_count": 0
            }
        },
        "toc": [
            {
                "module_id": "test_module",
                "path": "test_module.py",
                "category": "core",
                "functions": 1,
                "classes": 1
            }
        ],
        "modules": [
            {
                "module_id": "test_module",
                "path": "test_module.py", 
                "category": "core",
                "functions": [
                    {
                        "name": "test_function",
                        "docstring": "Test function",
                        "line_range": [1, 5],
                        "uid": "test_module.test_function#function",
                        "hash": "abc123"
                    }
                ],
                "classes": [
                    {
                        "name": "TestClass",
                        "docstring": "Test class",
                        "line_range": [6, 10],
                        "uid": "test_module.TestClass#class",
                        "hash": "def456",
                        "methods": []
                    }
                ],
                "callgraph": {},
                "dependencies": []
            }
        ]
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup global test environment."""
    # Ensure we're in offline mode for tests
    os.environ["LLMSTRUCT_OFFLINE_MODE"] = "true"
    os.environ["LLMSTRUCT_LLM_ENABLED"] = "false"
    
    yield
    
    # Cleanup after all tests
    env_vars_to_clean = [
        "LLMSTRUCT_LLM_ENABLED",
        "LLMSTRUCT_OFFLINE_MODE"
    ]
    
    for var in env_vars_to_clean:
        if var in os.environ:
            del os.environ[var]


# Test markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (moderate speed)"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test (slow, full system)"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test (benchmarking)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (may take several seconds)"
    )


# Test collection rules
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Auto-mark based on test file location
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance/" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow) 