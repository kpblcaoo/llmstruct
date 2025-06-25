"""
Test Critical Fixes for Phase 1

Tests the new LLM-optional architecture and fixes for:
1. Summary system with heuristic provider by default
2. UID system without duplicates
3. Hash utilities for incremental builds
4. Configuration management
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_manager():
    """Test configuration manager with LLM disabled by default"""
    print("Testing Configuration Manager...")
    
    from llmstruct.core.config_manager import get_config_manager, is_llm_enabled
    
    # Test default configuration
    config_manager = get_config_manager()
    config = config_manager.get_config()
    
    # LLM should be disabled by default
    assert config.enable_llm == False, "LLM should be disabled by default"
    assert config.llm.enabled == False, "LLM provider should be disabled by default"
    assert is_llm_enabled() == False, "is_llm_enabled() should return False by default"
    
    # Test offline mode environment variable
    os.environ["LLMSTRUCT_OFFLINE"] = "1"
    config_manager._config = None  # Reset config
    config = config_manager.get_config()
    assert config.security.offline_mode == True, "Offline mode should be enabled via env var"
    assert config.enable_llm == False, "LLM should be disabled in offline mode"
    
    # Clean up
    if "LLMSTRUCT_OFFLINE" in os.environ:
        del os.environ["LLMSTRUCT_OFFLINE"]
    
    print("✓ Configuration Manager tests passed")


def test_summary_providers():
    """Test summary providers with heuristic as default"""
    print("Testing Summary Providers...")
    
    from llmstruct.core.summary_providers import (
        get_summary_system, HeuristicProvider, generate_summary
    )
    
    # Test heuristic provider
    heuristic = HeuristicProvider()
    
    # Test docstring extraction
    code_with_docstring = '''
def example_function():
    """This is a test function that does something useful."""
    return True
'''
    
    summary = heuristic.generate_summary(
        code=code_with_docstring,
        entity_type="function",
        entity_name="example_function",
        docstring="This is a test function that does something useful."
    )
    
    assert summary.source.value == "docstring", "Should use docstring source"
    assert summary.confidence == 0.9, "Docstring should have high confidence"
    assert "test function" in summary.text.lower(), "Should extract docstring content"
    
    # Test heuristic generation
    summary_heuristic = heuristic.generate_summary(
        code="def get_user_name(): pass",
        entity_type="function", 
        entity_name="get_user_name"
    )
    
    assert summary_heuristic.source.value == "heuristic", "Should use heuristic source"
    assert summary_heuristic.confidence == 0.3, "Heuristic should have lower confidence"
    assert "retrieves" in summary_heuristic.text.lower(), "Should generate heuristic summary"
    
    # Test global summary system
    system_summary = generate_summary(
        code=code_with_docstring,
        entity_type="function",
        entity_name="example_function",
        docstring="This is a test function that does something useful."
    )
    
    assert system_summary.source.value == "docstring", "Global system should work"
    
    print("✓ Summary Providers tests passed")


def test_uid_generator():
    """Test UID generator without duplicates"""
    print("Testing UID Generator...")
    
    from llmstruct.core.uid_generator import (
        generate_uid, generate_uid_components, UIDType, enhance_entity_with_uid
    )
    
    # Test UID generation
    uid = generate_uid(
        UIDType.FUNCTION,
        "src/llmstruct/core/test.py",
        "test_function"
    )
    
    assert uid == "llmstruct.core.test.test_function#function", f"Unexpected UID: {uid}"
    
    # Test UID components without duplicates
    components = generate_uid_components(
        UIDType.FUNCTION,
        "src/llmstruct/core/test.py", 
        "test_function"
    )
    
    # Check for no duplicates
    assert len(components) == len(set(components)), f"Found duplicates in components: {components}"
    
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
    
    print("✓ UID Generator tests passed")


def test_hash_utils():
    """Test hash utilities for incremental builds"""
    print("Testing Hash Utilities...")
    
    from llmstruct.core.hash_utils import (
        hash_content, hash_source, hash_entity, quick_file_hash
    )
    
    # Test content hashing
    content = "def test(): pass"
    hash1 = hash_content(content)
    hash2 = hash_content(content)
    
    assert hash1 == hash2, "Same content should produce same hash"
    assert len(hash1) == 64, "SHA-256 should produce 64 character hex string"
    
    # Test source hashing (normalized)
    source1 = "def test():\n    pass\n"
    source2 = "def test():\n    pass"  # Different whitespace
    
    hash_source1 = hash_source(source1)
    hash_source2 = hash_source(source2)
    
    assert hash_source1 == hash_source2, "Normalized source should produce same hash"
    
    # Test entity hashing
    entity = {
        "type": "function",
        "name": "test_func",
        "content": "def test_func(): pass"
    }
    
    entity_hash = hash_entity(entity)
    assert len(entity_hash) == 64, "Entity hash should be SHA-256"
    
    # Test file hashing with temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("def temp_function(): pass")
        temp_path = f.name
    
    try:
        file_hash = quick_file_hash(temp_path)
        assert file_hash is not None, "Should hash existing file"
        assert len(file_hash) == 64, "File hash should be SHA-256"
    finally:
        os.unlink(temp_path)
    
    print("✓ Hash Utilities tests passed")


def test_integration():
    """Test integration of all components"""
    print("Testing Integration...")
    
    from llmstruct.core import (
        get_config, is_llm_enabled, generate_summary, 
        enhance_entity_with_uid, quick_content_hash
    )
    
    # Test configuration
    config = get_config()
    assert config.enable_llm == False, "Default config should disable LLM"
    
    # Test summary generation
    summary = generate_summary(
        code="def get_data(): pass",
        entity_type="function",
        entity_name="get_data"
    )
    
    assert summary.source.value == "heuristic", "Should use heuristic by default"
    assert not summary.is_empty(), "Should generate non-empty summary"
    
    # Test entity enhancement
    entity = {
        "type": "function",
        "name": "test_func",
        "file_path": "test.py",
        "content": "def test_func(): pass"
    }
    
    enhanced = enhance_entity_with_uid(entity)
    content_hash = quick_content_hash(entity["content"])
    
    assert "uid" in enhanced, "Should have UID"
    assert content_hash, "Should generate content hash"
    
    print("✓ Integration tests passed")


def main():
    """Run all tests"""
    print("Running Critical Fixes Tests for Phase 1...")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_summary_providers() 
        test_uid_generator()
        test_hash_utils()
        test_integration()
        
        print("=" * 50)
        print("🎉 All tests PASSED!")
        print("\nKey fixes verified:")
        print("✓ LLM support is DISABLED by default")
        print("✓ Heuristic summary provider works offline")
        print("✓ UID components have no duplicates")
        print("✓ Hash utilities support incremental builds")
        print("✓ Configuration system manages security")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 