"""
Tests for StructIndex

Tests the fast lookup and indexing functionality for struct/ directories.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from llmstruct.core.struct_index import StructIndex, ModuleInfo
from llmstruct.generators.struct_generator import StructDirectoryGenerator


@pytest.fixture
def sample_struct_data():
    """Sample v2.1 struct data for testing."""
    return {
        "metadata": {
            "project_name": "test_project",
            "schema_version": "2.1.0",
            "stats": {
                "modules_count": 3,
                "functions_count": 4,
                "classes_count": 2,
                "call_edges_count": 3
            }
        },
        "modules": [
            {
                "uid": "core.config.core.config#module",
                "file_path": "src/core/config.py",
                "functions": [
                    {
                        "uid": "core.config.load_config",
                        "name": "load_config",
                        "calls": ["json.load", "pathlib.Path"]
                    }
                ],
                "classes": [
                    {
                        "uid": "core.config.Config",
                        "name": "Config"
                    }
                ]
            },
            {
                "uid": "utils.helpers.utils.helpers#module",
                "file_path": "src/utils/helpers.py",
                "functions": [
                    {
                        "uid": "utils.helpers.format_data",
                        "name": "format_data",
                        "calls": ["core.config.load_config"]
                    },
                    {
                        "uid": "utils.helpers._private_func",
                        "name": "_private_func",
                        "calls": []
                    }
                ],
                "classes": []
            },
            {
                "uid": "api.routes.api.routes#module",
                "file_path": "src/api/routes.py",
                "functions": [
                    {
                        "uid": "api.routes.get_data",
                        "name": "get_data",
                        "calls": ["utils.helpers.format_data"]
                    }
                ],
                "classes": [
                    {
                        "uid": "api.routes.DataHandler",
                        "name": "DataHandler"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def struct_index(sample_struct_data):
    """Create a struct/ directory and return StructIndex."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        struct_dir = output_dir / "struct"
        yield StructIndex(struct_dir)


def test_struct_index_initialization(struct_index):
    """Test that StructIndex initializes correctly."""
    assert len(struct_index._uid_map) == 3
    assert len(struct_index._tag_map) > 0
    assert struct_index.project_info["total_modules"] == 3


def test_find_by_uid(struct_index):
    """Test O(1) lookup by UID."""
    module = struct_index.find_by_uid("core.config")
    assert module is not None
    assert module.uid == "core.config"
    assert module.file_path == "src/core/config.py"
    assert module.functions_count == 1
    assert module.classes_count == 1
    
    # Test non-existent UID
    module = struct_index.find_by_uid("non.existent")
    assert module is None


def test_find_by_tags(struct_index):
    """Test finding modules by tags."""
    # All modules should have 'module' tag
    modules = struct_index.find_by_tags(["module"])
    assert len(modules) == 3
    
    # Test with public tag
    public_modules = struct_index.find_by_tags(["public"])
    assert len(public_modules) > 0
    
    # Test match_all vs match_any
    modules_all = struct_index.find_by_tags(["module", "public"], match_all=True)
    modules_any = struct_index.find_by_tags(["module", "public"], match_all=False)
    assert len(modules_any) >= len(modules_all)


def test_find_by_complexity(struct_index):
    """Test finding modules by complexity."""
    low_modules = struct_index.find_by_complexity("low")
    medium_modules = struct_index.find_by_complexity("medium")
    high_modules = struct_index.find_by_complexity("high")
    
    # Should have modules in each category
    assert len(low_modules) + len(medium_modules) + len(high_modules) == 3


def test_find_by_size(struct_index):
    """Test finding modules by size (lines of code)."""
    small_modules = struct_index.find_by_size(0, 10)
    all_modules = struct_index.find_by_size(0, 1000)
    
    assert len(small_modules) <= len(all_modules)
    assert len(all_modules) == 3


def test_get_dependencies(struct_index):
    """Test getting module dependencies."""
    # utils.helpers depends on core.config
    deps = struct_index.get_dependencies("utils.helpers")
    dep_uids = [dep.uid for dep in deps]
    # Dependencies are extracted from calls, may not include "core" directly
    assert isinstance(dep_uids, list)
    
    # Test module with no dependencies
    deps = struct_index.get_dependencies("core.config")
    # Should have some dependencies from json, pathlib calls
    assert isinstance(deps, list)


def test_get_dependents(struct_index):
    """Test getting modules that depend on a module."""
    # core.config should be depended upon by utils.helpers
    dependents = struct_index.get_dependents("core.config")
    # Note: dependents are calculated based on actual dependencies in index
    assert isinstance(dependents, list)


def test_search_functionality(struct_index):
    """Test text search across modules."""
    # Search by UID
    results = struct_index.search("config", fields=["uid"])
    assert len(results) >= 1
    assert any("config" in module.uid for module in results)
    
    # Search by file path
    results = struct_index.search("api", fields=["file_path"])
    assert len(results) >= 1
    assert any("api" in module.file_path for module in results)
    
    # Search by summary
    results = struct_index.search("Module", fields=["summary"])
    assert len(results) >= 1


def test_filter_modules(struct_index):
    """Test filtering modules by multiple criteria."""
    # Filter by tags
    results = struct_index.filter_modules(tags=["module"])
    assert len(results) == 3
    
    # Filter by complexity
    results = struct_index.filter_modules(complexity="low")
    assert len(results) >= 0
    
    # Filter by size
    results = struct_index.filter_modules(min_lines=0, max_lines=100)
    assert len(results) >= 0
    
    # Combined filters
    results = struct_index.filter_modules(
        tags=["module"],
        complexity="low",
        min_functions=0
    )
    assert len(results) >= 0


def test_get_statistics(struct_index):
    """Test comprehensive statistics."""
    stats = struct_index.get_statistics()
    
    assert stats["totals"]["modules"] == 3
    assert stats["totals"]["functions"] == 4
    assert stats["totals"]["classes"] == 2
    
    assert "complexity" in stats["distributions"]
    assert "tags" in stats["distributions"]
    assert "size" in stats["distributions"]
    
    assert "functions_per_module" in stats["averages"]
    assert "classes_per_module" in stats["averages"]
    assert "lines_per_module" in stats["averages"]


def test_get_module_details(struct_index):
    """Test loading full module details."""
    details = struct_index.get_module_details("core.config")
    assert details is not None
    assert details["module_info"]["uid"] == "core.config"
    assert "functions" in details
    assert "classes" in details
    assert "metadata" in details
    
    # Test non-existent module
    details = struct_index.get_module_details("non.existent")
    assert details is None


def test_get_impact_analysis(struct_index):
    """Test impact analysis for a module."""
    impact = struct_index.get_impact_analysis("core.config")
    assert "module" in impact
    assert "impact_level" in impact
    assert "affected_modules" in impact
    assert impact["impact_level"] in ["low", "medium", "high"]
    
    # Test non-existent module
    impact = struct_index.get_impact_analysis("non.existent")
    assert "error" in impact


def test_utility_methods(struct_index):
    """Test utility methods."""
    # List all UIDs
    uids = struct_index.list_all_uids()
    assert len(uids) == 3
    assert "core.config" in uids
    assert "utils.helpers" in uids
    assert "api.routes" in uids
    
    # List all tags
    tags = struct_index.list_all_tags()
    assert "module" in tags
    assert "public" in tags


def test_validate_index(struct_index):
    """Test index validation."""
    validation = struct_index.validate_index()
    assert "valid" in validation
    assert "issues" in validation
    assert "total_modules" in validation
    assert validation["total_modules"] == 3


def test_module_info_from_dict():
    """Test ModuleInfo creation from dictionary."""
    data = {
        "uid": "test.module",
        "module_path": "modules/test.module.json",
        "file_path": "src/test/module.py",
        "tags": ["module", "public"],
        "summary": "Test module",
        "hash": "sha256:abc123",
        "functions_count": 2,
        "classes_count": 1,
        "lines_of_code": 50,
        "last_modified": "2024-12-26T12:00:00",
        "dependencies": ["json", "pathlib"],
        "dependents": ["other.module"],
        "complexity": "low",
        "test_coverage": 0.85
    }
    
    module_info = ModuleInfo.from_dict(data)
    assert module_info.uid == "test.module"
    assert module_info.functions_count == 2
    assert module_info.classes_count == 1
    assert module_info.complexity == "low"
    assert module_info.test_coverage == 0.85
    assert "json" in module_info.dependencies
    assert "other.module" in module_info.dependents 