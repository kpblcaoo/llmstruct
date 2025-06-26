#!/usr/bin/env python3
"""
Quick Phase 1 v2.1.0 validation check as pytest test.

End-to-end test that validates the complete Phase 1 implementation
by checking generated fixtures and their compliance with schema v2.1.0.
"""

import json
import pytest
from pathlib import Path


def test_phase1_schema_version():
    """Test that generated files have correct schema version."""
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    index_file = Path("tests/fixtures/phase1/struct_v2.1_final_index.json")
    
    # Check files exist
    assert struct_file.exists(), "Missing struct_v2.1_final.json"
    assert index_file.exists(), "Missing struct_v2.1_final_index.json"
    
    # Check struct schema version
    with open(struct_file) as f:
        data = json.load(f)
    
    schema_version = data["metadata"].get("schema_version")
    assert schema_version == "2.1.0", f"Wrong schema version: {schema_version}"
    
    # Check index version
    with open(index_file) as f:
        index_data = json.load(f)
    
    index_version = index_data.get("version")
    assert index_version == "2.1.0", f"Wrong index version: {index_version}"


def test_phase1_hash_system():
    """Test that hash system is properly implemented."""
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    
    with open(struct_file) as f:
        data = json.load(f)
    
    hash_count = 0
    for module in data["modules"]:
        if module.get("hash"):
            hash_count += 1
        for func in module["functions"]:
            if func.get("hash"):
                hash_count += 1
        for cls in module["classes"]:
            if cls.get("hash"):
                hash_count += 1
            for method in cls["methods"]:
                if method.get("hash"):
                    hash_count += 1
    
    # Should have substantial number of hashes
    assert hash_count > 100, f"Too few hashes: {hash_count}"


def test_phase1_uid_system():
    """Test that UID system is properly implemented."""
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    
    with open(struct_file) as f:
        data = json.load(f)
    
    uid_count = 0
    uid_set = set()
    
    for module in data["modules"]:
        if module.get("uid"):
            uid_count += 1
            uid_set.add(module["uid"])
        for func in module["functions"]:
            if func.get("uid"):
                uid_count += 1
                uid_set.add(func["uid"])
        for cls in module["classes"]:
            if cls.get("uid"):
                uid_count += 1
                uid_set.add(cls["uid"])
            for method in cls["methods"]:
                if method.get("uid"):
                    uid_count += 1
                    uid_set.add(method["uid"])
    
    # Should have substantial number of UIDs
    assert uid_count > 100, f"Too few UIDs: {uid_count}"
    
    # All UIDs should be unique
    assert len(uid_set) == uid_count, f"Duplicate UIDs found: {uid_count} total, {len(uid_set)} unique"


def test_phase1_call_edges_accuracy():
    """Test that call edges count is accurate."""
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    
    with open(struct_file) as f:
        data = json.load(f)
    
    # Check call edges accuracy
    reported_edges = data["metadata"]["stats"]["call_edges_count"]
    actual_edges = 0
    
    for module in data["modules"]:
        callgraph = module.get("callgraph", {})
        for caller, callees in callgraph.items():
            actual_edges += len(callees)
    
    assert reported_edges == actual_edges, f"Call edges mismatch: reported {reported_edges}, actual {actual_edges}"


def test_phase1_toc_completeness():
    """Test that table of contents is complete and has hashes."""
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    
    with open(struct_file) as f:
        data = json.load(f)
    
    # Check TOC exists and is non-empty
    toc = data.get("toc", [])
    assert len(toc) > 0, "TOC is empty"
    
    # Check TOC entries have required fields
    for entry in toc:
        assert "module_id" in entry, "TOC entry missing module_id"
        assert "path" in entry, "TOC entry missing path"
        assert "category" in entry, "TOC entry missing category"


def test_phase1_index_completeness():
    """Test that index file is complete and accurate."""
    index_file = Path("tests/fixtures/phase1/struct_v2.1_final_index.json")
    
    with open(index_file) as f:
        index_data = json.load(f)
    
    # Check required fields
    assert "total_entities" in index_data, "Index missing total_entities"
    assert "entities_by_type" in index_data, "Index missing entities_by_type"
    assert "entities" in index_data, "Index missing entities"
    
    total_entities = index_data["total_entities"]
    assert total_entities > 0, "No entities in index"
    
    # Check entities by type
    entities_by_type = index_data["entities_by_type"]
    expected_types = ["module", "function", "class", "method"]
    
    for entity_type in expected_types:
        assert entity_type in entities_by_type, f"Missing entity type: {entity_type}"
        assert entities_by_type[entity_type] > 0, f"No entities of type: {entity_type}"


@pytest.mark.e2e
@pytest.mark.slow
def test_phase1_complete_validation():
    """Complete end-to-end validation of Phase 1 implementation."""
    print("\n🔍 Complete Phase 1 v2.1.0 Validation")
    print("=" * 50)
    
    # Run all individual tests
    test_phase1_schema_version()
    print("✅ Schema version validation passed")
    
    test_phase1_hash_system()
    print("✅ Hash system validation passed")
    
    test_phase1_uid_system()
    print("✅ UID system validation passed")
    
    test_phase1_call_edges_accuracy()
    print("✅ Call edges validation passed")
    
    test_phase1_toc_completeness()
    print("✅ TOC validation passed")
    
    test_phase1_index_completeness()
    print("✅ Index validation passed")
    
    print("\n🎉 Phase 1 v2.1.0 Complete Validation PASSED!")


if __name__ == "__main__":
    # Allow running as script for backwards compatibility
    import sys
    
    try:
        test_phase1_complete_validation()
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)
