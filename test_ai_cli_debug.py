#!/usr/bin/env python3
"""
Simple test for AI CLI Integration - Debug Version
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path("/home/kpblc/projects/github/llmstruct")
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic functionality step by step."""
    
    print("🔍 DEBUGGING AI CLI INTEGRATION")
    print("=" * 50)
    
    # Test 1: Check if we can import the module
    print("\n1. Testing import of ai_cli_integration...")
    try:
        from src.llmstruct.ai_cli_integration import AISelfAwarenessCLIIntegration
        print("✅ Successfully imported AISelfAwarenessCLIIntegration")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test 2: Check if we can create an instance
    print("\n2. Testing instance creation...")
    try:
        integration = AISelfAwarenessCLIIntegration(str(project_root))
        print("✅ Successfully created AISelfAwarenessCLIIntegration instance")
    except Exception as e:
        print(f"❌ Instance creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check available commands
    print("\n3. Testing command discovery...")
    try:
        print(f"Available commands: {len(integration.available_commands)}")
        for cmd_name, cmd_info in integration.available_commands.items():
            status = cmd_info['status']
            utility = cmd_info['ai_utility']
            print(f"   - {cmd_name}: {status} ({utility})")
    except Exception as e:
        print(f"❌ Command discovery failed: {e}")
        return False
    
    # Test 4: Test integration summary
    print("\n4. Testing integration summary...")
    try:
        summary = integration.get_integration_summary()
        print(f"✅ Integration summary generated")
        print(f"   Total commands: {summary['total_unused_commands']}")
        print(f"   Available: {summary['available_for_integration']}")
        print(f"   Integration rate: {summary['integration_rate']:.1%}")
    except Exception as e:
        print(f"❌ Integration summary failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Test status integration
    print("\n5. Testing status command integration...")
    try:
        status_result = integration.integrate_ai_status_command()
        print(f"✅ Status integration: {status_result['integration_status']}")
        if status_result.get('fallback'):
            print("   (Using fallback implementation)")
    except Exception as e:
        print(f"❌ Status integration failed: {e}")
        return False
    
    return True

def test_ai_self_awareness():
    """Test the main AI self-awareness system."""
    
    print("\n" + "=" * 50)
    print("🧠 TESTING AI SELF-AWARENESS SYSTEM")
    print("=" * 50)
    
    try:
        from src.llmstruct.ai_self_awareness import SystemCapabilityDiscovery
        print("✅ Successfully imported SystemCapabilityDiscovery")
        
        discovery = SystemCapabilityDiscovery(str(project_root))
        print("✅ Successfully created SystemCapabilityDiscovery instance")
        
        # Test basic capabilities
        print("\n📊 Testing basic capability discovery...")
        capabilities = discovery.discover_all_capabilities()
        print(f"✅ Capabilities discovered at: {capabilities.timestamp}")
        
        # Test enhanced summary
        print("\n📋 Testing enhanced capabilities summary...")
        enhanced_summary = discovery.get_enhanced_capabilities_summary()
        print("✅ Enhanced summary generated")
        print("\n" + "="*60)
        print("ENHANCED CAPABILITIES SUMMARY:")
        print("="*60)
        print(enhanced_summary[:1000] + "..." if len(enhanced_summary) > 1000 else enhanced_summary)
        
        return True
        
    except Exception as e:
        print(f"❌ AI Self-Awareness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 STARTING DEBUG TESTS")
    print("Project root:", project_root)
    print("Python path:", sys.path[0])
    
    # Run basic functionality test
    basic_success = test_basic_functionality()
    
    if basic_success:
        # Run AI self-awareness test
        ai_success = test_ai_self_awareness()
        
        if ai_success:
            print("\n" + "="*60)
            print("🎉 ALL TESTS PASSED!")
            print("✅ AI CLI Integration is working correctly")
            print("✅ Enhanced AI Self-Awareness system is functional")
            print("🚀 Strategic transformation from unused functions to AI capabilities: SUCCESS")
        else:
            print("\n❌ AI Self-Awareness test failed")
    else:
        print("\n❌ Basic functionality test failed")
        
    print("\n" + "="*60)
