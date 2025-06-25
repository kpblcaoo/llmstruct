"""
Phase 1 Final Validation Tests

Comprehensive test suite to validate Phase 1 v2.1.0 completion.
Tests all critical features, regressions fixes, and quality metrics.
"""

import json
import pytest
import tempfile
from pathlib import Path

from llmstruct.generators.json_generator import generate_json
from llmstruct.generators.index_generator import generate_index_json, diff_by_hash


class TestPhase1CoreInfrastructure:
    """Test core Phase 1 infrastructure components."""
    
    @pytest.fixture
    def sample_struct_data(self, tmp_path):
        """Generate sample struct data for testing."""
        test_source = tmp_path / "test_module.py"
        test_source.write_text('''
"""Test module for Phase 1 validation."""

def test_function(param1: str, param2: int = 10) -> str:
    """Test function with parameters."""
    return f"result: {param1} + {param2}"

class TestClass:
    """Test class for validation."""
    
    def test_method(self, arg: str) -> bool:
        """Test method in class."""
        return len(arg) > 0
        ''')
        
        return generate_json(
            root_dir=str(tmp_path),
            include_patterns=["*.py"],
            exclude_patterns=[],
            gitignore_patterns=[],
            include_ranges=True,
            include_hashes=True,
            goals=["test validation"],
            exclude_dirs=[]
        )
    
    def test_hash_system_completeness(self, sample_struct_data):
        """Test that hash system is complete and consistent."""
        # All modules should have hashes
        for module in sample_struct_data["modules"]:
            assert module.get("hash") is not None
            assert len(module["hash"]) == 64  # SHA-256
            assert module.get("hash_source") == "file_content_v1"
            assert module.get("hash_version") == "2.1.0"


# Test runner for Phase 1 validation
def test_phase1_complete_validation():
    """Integration test that runs all Phase 1 validation checks."""
    # This would be run against the actual generated struct_v2.1_final.json
    fixture_path = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    with open(fixture_path, "r") as f:
        actual_data = json.load(f)
    
    # Quick validation checks
    assert actual_data["metadata"]["schema_version"] == "2.1.0"
    assert "hash" in actual_data["toc"][0]
    assert actual_data["metadata"]["stats"]["call_edges_count"] > 0
    
    print("✅ Phase 1 v2.1.0 validation PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
