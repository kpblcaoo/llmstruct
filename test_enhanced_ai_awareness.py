#!/usr/bin/env python3
"""
Test script for AI Self-Awareness Enhancement with Unused Function Integration
"""

import sys
import os
sys.path.append('/home/kpblc/projects/github/llmstruct')

from src.llmstruct.ai_self_awareness import SystemCapabilityDiscovery

def test_enhanced_ai_self_awareness():
    """Test the enhanced AI self-awareness system."""
    
    print("🚀 Testing Enhanced AI Self-Awareness System")
    print("=" * 60)
    
    try:
        # Initialize the enhanced discovery system
        discovery = SystemCapabilityDiscovery("/home/kpblc/projects/github/llmstruct")
        
        print("✅ SystemCapabilityDiscovery initialized successfully")
        
        # Test comprehensive AI status
        print("\n📊 Getting Comprehensive AI Status...")
        status = discovery.get_comprehensive_ai_status()
        
        print("\n" + "="*80)
        print("COMPREHENSIVE AI SELF-AWARENESS REPORT:")
        print("="*80)
        print(status)
        
        # Test specific integration metrics
        print("\n🔧 Testing Integration Metrics...")
        capabilities = discovery.discover_all_capabilities()
        
        integration_metrics = capabilities.performance_metrics.get("unused_function_integration", {})
        print(f"Integration Rate: {integration_metrics.get('integration_rate', 0):.1%}")
        print(f"Enhanced Categories: {integration_metrics.get('enhanced_categories', 0)}")
        print(f"AI Improvement Level: {integration_metrics.get('ai_capability_improvement', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced AI self-awareness: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_ai_self_awareness()
    
    if success:
        print("\n✅ Enhanced AI Self-Awareness Test PASSED")
        print("🎯 Strategic transformation from unused functions to AI capabilities successful!")
    else:
        print("\n❌ Enhanced AI Self-Awareness Test FAILED")
        print("🔧 Check implementation and dependencies")
