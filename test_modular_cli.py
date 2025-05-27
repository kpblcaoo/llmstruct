#!/usr/bin/env python3
"""
Test script for modular CLI structure
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, '/home/kpblc/projects/github/llmstruct/src')

def test_modular_cli():
    """Test basic modular CLI functionality."""
    print("Testing modular CLI structure...")
    
    try:
        # Test imports
        from llmstruct.cli_core import CLICore, create_cli_core
        from llmstruct.cli_config import CLIConfig
        from llmstruct.cli_utils import CLIUtils
        from llmstruct.cli_commands import CommandProcessor
        print("✓ All modular CLI components imported successfully")
        
        # Test config loading with temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"✓ Testing with temporary directory: {temp_dir}")
            
            # Test CLIConfig
            config = CLIConfig(temp_dir)
            cache_config = config.get_cache_config()
            print(f"✓ Cache config loaded: {len(cache_config)} settings")
            
            # Test CLIUtils
            utils = CLIUtils(temp_dir)
            
            # Create test file
            test_file = "test.txt"
            test_content = "Hello, modular CLI!"
            success = utils.write_file_content(test_file, test_content)
            print(f"✓ File write test: {'success' if success else 'failed'}")
            
            # Read test file
            content = utils.read_file_content(test_file)
            print(f"✓ File read test: {'success' if content == test_content else 'failed'}")
            
            # Test CLICore creation
            cli_core = create_cli_core(temp_dir)
            print("✓ CLI core created successfully")
            
            # Test CommandProcessor
            command_processor = CommandProcessor(temp_dir, config, utils)
            print("✓ Command processor created successfully")
            
        print("\n🎉 All modular CLI tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_copilot_integration():
    """Test Copilot integration."""
    print("\nTesting Copilot integration...")
    
    try:
        from llmstruct.copilot import CopilotContextManager, CopilotEvent, initialize_copilot
        print("✓ Copilot components imported successfully")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test initialization
            manager = initialize_copilot(temp_dir)
            print("✓ Copilot manager initialized")
            
            # Test status
            status = manager.get_context_status()
            print(f"✓ Context status retrieved: {len(status)} fields")
            
            # Test event creation
            event = CopilotEvent(
                event_type="test_event",
                file_path="test.py",
                metadata={"test": True}
            )
            print("✓ Copilot event created")
            
            manager.close()
            print("✓ Copilot manager cleaned up")
            
        print("🎉 Copilot integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Copilot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Modular CLI Test Suite ===")
    
    success = True
    success &= test_modular_cli()
    success &= test_copilot_integration()
    
    if success:
        print("\n✅ All tests passed! Modular CLI structure is working.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
