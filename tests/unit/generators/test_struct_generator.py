"""
Tests for StructDirectoryGenerator

Tests the struct/ directory generation functionality.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from llmstruct.generators.struct_generator import StructDirectoryGenerator


@pytest.fixture
def sample_struct_data():
    """Sample v2.1 struct data for testing."""
    return {
        "metadata": {
            "project_name": "test_project",
            "schema_version": "2.1.0",
            "stats": {
                "modules_count": 2,
                "functions_count": 3,
                "classes_count": 1,
                "call_edges_count": 2
            }
        },
        "modules": [
            {
                "uid": "test.module1.test.module1#module",
                "file_path": "src/test/module1.py",
                "functions": [
                    {
                        "uid": "test.module1.func1",
                        "name": "func1",
                        "calls": ["json.dumps", "logging.info"]
                    },
                    {
                        "uid": "test.module1.func2", 
                        "name": "func2",
                        "calls": ["func1"]
                    }
                ],
                "classes": [
                    {
                        "uid": "test.module1.TestClass",
                        "name": "TestClass"
                    }
                ]
            },
            {
                "uid": "test.module2.test.module2#module",
                "file_path": "src/test/module2.py",
                "functions": [
                    {
                        "uid": "test.module2.func3",
                        "name": "func3",
                        "calls": ["test.module1.func1"]
                    }
                ],
                "classes": []
            }
        ]
    }


def test_struct_generator_creates_directories(sample_struct_data):
    """Test that generator creates proper directory structure."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        struct_dir = output_dir / "struct"
        assert struct_dir.exists()
        assert (struct_dir / "modules").exists()
        assert (struct_dir / "index.json").exists()
        assert (struct_dir / "callgraph.json").exists()
        assert (struct_dir / "schema.json").exists()
        assert (struct_dir / "metadata.json").exists()
        assert (struct_dir / "struct.json").exists()


def test_struct_generator_creates_module_files(sample_struct_data):
    """Test that generator creates individual module files."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        modules_dir = output_dir / "struct" / "modules"
        module_files = list(modules_dir.glob("*.json"))
        
        assert len(module_files) == 2
        
        # Check specific module files exist
        assert (modules_dir / "test.module1.json").exists()
        assert (modules_dir / "test.module2.json").exists()


def test_struct_generator_index_content(sample_struct_data):
    """Test that index.json contains correct data."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        index_file = output_dir / "struct" / "index.json"
        with open(index_file, 'r') as f:
            index_data = json.load(f)
            
        assert index_data["schema_version"] == "2.1.0"
        assert index_data["project_info"]["total_modules"] == 2
        assert index_data["project_info"]["total_functions"] == 3
        assert index_data["project_info"]["total_classes"] == 1
        assert len(index_data["modules"]) == 2
        
        # Check module entries
        module_uids = [m["uid"] for m in index_data["modules"]]
        assert "test.module1" in module_uids
        assert "test.module2" in module_uids


def test_struct_generator_module_content(sample_struct_data):
    """Test that module files contain correct data."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        module_file = output_dir / "struct" / "modules" / "test.module1.json"
        with open(module_file, 'r') as f:
            module_data = json.load(f)
            
        assert module_data["module_info"]["uid"] == "test.module1"
        assert module_data["module_info"]["file_path"] == "src/test/module1.py"
        assert len(module_data["functions"]) == 2
        assert len(module_data["classes"]) == 1
        assert "json" in module_data["module_info"]["dependencies"]


def test_struct_generator_callgraph_content(sample_struct_data):
    """Test that callgraph.json contains correct call data."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        callgraph_file = output_dir / "struct" / "callgraph.json"
        with open(callgraph_file, 'r') as f:
            callgraph_data = json.load(f)
            
        assert callgraph_data["schema_version"] == "2.1.0"
        assert len(callgraph_data["calls"]) > 0
        
        # Check specific calls exist
        call_names = [call["callee_name"] for call in callgraph_data["calls"]]
        assert "dumps" in call_names  # from json.dumps
        assert "info" in call_names   # from logging.info


def test_struct_generator_uid_cleanup(sample_struct_data):
    """Test that UIDs are properly cleaned up."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        index_file = output_dir / "struct" / "index.json"
        with open(index_file, 'r') as f:
            index_data = json.load(f)
            
        # Check that duplicate UIDs are cleaned up
        module_uids = [m["uid"] for m in index_data["modules"]]
        assert "test.module1" in module_uids
        assert "test.module2" in module_uids
        
        # Should not contain duplicated parts
        for uid in module_uids:
            assert "#module" not in uid
            parts = uid.split('.')
            # Check no duplicate consecutive parts
            for i in range(len(parts) - 1):
                assert parts[i] != parts[i + 1]


def test_struct_generator_legacy_compatibility(sample_struct_data):
    """Test that legacy struct.json is generated for backward compatibility."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        legacy_file = output_dir / "struct" / "struct.json"
        with open(legacy_file, 'r') as f:
            legacy_data = json.load(f)
            
        # Should be identical to input data
        assert legacy_data["metadata"]["project_name"] == "test_project"
        assert len(legacy_data["modules"]) == 2


def test_struct_generator_metadata_content(sample_struct_data):
    """Test that metadata.json contains generation info."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = StructDirectoryGenerator(output_dir, sample_struct_data)
        generator.generate()
        
        metadata_file = output_dir / "struct" / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            
        assert metadata["generation"]["generator_version"] == "2.1.0"
        assert metadata["generation"]["source_format"] == "v2.1"
        assert metadata["generation"]["target_format"] == "struct/"
        assert metadata["statistics"]["total_modules"] == 2
        assert metadata["performance"]["file_count"] == 7  # 2 modules + 5 other files 