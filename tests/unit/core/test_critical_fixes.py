"""Test Critical Fixes for Phase 1 - Integration Tests.

Comprehensive integration tests for all Phase 1 critical fixes.
Imports and runs individual component tests.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import individual test modules
try:
    from .test_config_manager import test_config_manager
    from .test_summary_providers import test_summary_providers
    from .test_uid_generator import test_uid_generator
    from .test_hash_utils import test_hash_utils
except ImportError:
    # Fallback for direct execution
    import test_config_manager
    import test_summary_providers
    import test_uid_generator
    import test_hash_utils
    test_config_manager = test_config_manager.test_config_manager
    test_summary_providers = test_summary_providers.test_summary_providers
    test_uid_generator = test_uid_generator.test_uid_generator
    test_hash_utils = test_hash_utils.test_hash_utils




def test_integration():
    """Test integration of all components"""
    print("Testing Integration...")
    
    from llmstruct.core import (
        get_config, is_llm_enabled, generate_summary, 
        enhance_entity_with_uid, quick_content_hash
    )
    from llmstruct.core.config_manager import get_config_manager as _gcm
    _gcm()._config = None  # reset
    config = get_config()
    
    # Test configuration
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