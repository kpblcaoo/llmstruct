"""Tests for Hash Utilities system.

Tests hash generation for incremental builds and content comparison.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_content_hashing():
    """Test consistent content hashing."""
    from llmstruct.core.hash_utils import hash_content
    
    # Test content hashing
    content = "def test(): pass"
    hash1 = hash_content(content)
    hash2 = hash_content(content)
    
    assert hash1 == hash2, "Same content should produce same hash"
    assert len(hash1) == 64, "SHA-256 should produce 64 character hex string"


def test_source_normalization():
    """Test source code normalization for consistent hashing."""
    from llmstruct.core.hash_utils import hash_source
    
    # Test source hashing (normalized)
    source1 = "def test():\n    pass\n"
    source2 = "def test():\n    pass"  # Different whitespace
    
    hash_source1 = hash_source(source1)
    hash_source2 = hash_source(source2)
    
    assert hash_source1 == hash_source2, "Normalized source should produce same hash"


def test_entity_hashing():
    """Test entity hashing with metadata."""
    from llmstruct.core.hash_utils import hash_entity
    
    # Test entity hashing
    entity = {
        "type": "function",
        "name": "test_func",
        "content": "def test_func(): pass"
    }
    
    entity_hash = hash_entity(entity)
    assert len(entity_hash) == 64, "Entity hash should be SHA-256"


def test_file_hashing():
    """Test file hashing with temporary files."""
    from llmstruct.core.hash_utils import quick_file_hash
    
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


def test_hash_utils():
    """Run all Hash Utilities tests."""
    print("Testing Hash Utilities...")
    
    test_content_hashing()
    test_source_normalization()
    test_entity_hashing()
    test_file_hashing()
    
    print("✓ Hash Utilities tests passed")


if __name__ == "__main__":
    test_hash_utils() 