"""Tests for UID Generator system.

Tests UID generation without duplicates and proper FQNAME formatting.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_uid_generation_uses_fqname_format():
    from llmstruct.core.uid_generator import generate_uid, UIDType
    
    # Test UID generation
    uid = generate_uid(
        UIDType.FUNCTION,
        "src/llmstruct/core/test.py",
        "test_function"
    )
    
    assert uid == "llmstruct.core.test.test_function#function", f"Unexpected UID: {uid}"


def test_uid_components_have_no_duplicates():
    from llmstruct.core.uid_generator import generate_uid_components, UIDType
    
    # Test UID components without duplicates
    components = generate_uid_components(
        UIDType.FUNCTION,
        "src/llmstruct/core/test.py", 
        "test_function"
    )
    
    # Check for no duplicates
    assert len(components) == len(set(components)), f"Found duplicates in components: {components}"


def test_entity_enhancement_adds_uid_fields():
    from llmstruct.core.uid_generator import enhance_entity_with_uid
    
    # Test entity enhancement
    entity = {
        "type": "function",
        "name": "test_func",
        "file_path": "src/test.py"
    }
    
    enhanced = enhance_entity_with_uid(entity)
    
    assert "uid" in enhanced, "Should add uid field"
    assert "uid_components" in enhanced, "Should add uid_components field" 
    assert "artifact_id" in enhanced, "Should add artifact_id for backward compatibility"
    assert len(enhanced["uid_components"]) == len(set(enhanced["uid_components"])), "No duplicates in uid_components"


def test_uid_generator():
    print("Testing UID Generator...")
    
    test_uid_generation_uses_fqname_format()
    test_uid_components_have_no_duplicates()
    test_entity_enhancement_adds_uid_fields()
    
    print("✓ UID Generator tests passed")


if __name__ == "__main__":
    test_uid_generator() 