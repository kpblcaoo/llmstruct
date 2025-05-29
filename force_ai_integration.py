#!/usr/bin/env python3
"""
Force AI Integration Script
Initializes middleware and monitoring to ensure AI uses llmstruct system.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llmstruct.ai_workflow_middleware import initialize_ai_middleware, AIWorkflowMode
from llmstruct.ai_self_monitor import initialize_ai_monitor, record_ai_usage


def force_ai_integration():
    """Force AI to use llmstruct system."""
    project_root = str(Path(__file__).parent)
    
    print("🚀 FORCING AI INTEGRATION WITH LLMSTRUCT")
    print("=" * 50)
    
    # 1. Initialize middleware in STRICT mode
    print("1. Initializing AI Workflow Middleware (STRICT mode)...")
    middleware = initialize_ai_middleware(project_root, AIWorkflowMode.STRICT)
    print("   ✅ Middleware active - ALL AI requests will use llmstruct")
    
    # 2. Initialize monitoring system
    print("2. Initializing AI Self-Monitor...")
    monitor = initialize_ai_monitor(project_root)
    print("   ✅ Monitor active - tracking AI behavior patterns")
    
    # 3. Test the system
    print("3. Testing forced integration...")
    test_query = "analyze the project structure and suggest improvements"
    response = middleware.process_ai_request(test_query)
    
    print(f"   🧪 Test query: {test_query}")
    print(f"   🎯 Used LLMStruct: {response.used_llmstruct}")
    print(f"   📊 Context tokens: {response.performance_metrics.get('context_tokens', 0)}")
    
    # 4. Record the test usage
    record_ai_usage(
        query=test_query,
        tools_used=["ai_workflow_middleware", "context_orchestrator"],
        used_llmstruct=response.used_llmstruct,
        context_tags=[],
        metadata={"test": True}
    )
    
    # 5. Generate guidance for AI
    guidance = monitor.get_real_time_guidance(test_query)
    print("4. AI Guidance generated:")
    for tip in guidance:
        print(f"   💡 {tip}")
    
    # 6. Create configuration file for persistence
    config = {
        "ai_integration": {
            "middleware_mode": "strict",
            "monitoring_enabled": True,
            "force_llmstruct": True,
            "auto_context_tags": True,
            "guidance_active": True
        },
        "enforcement_rules": {
            "require_semantic_search": True,
            "require_struct_analysis": True,
            "require_context_optimization": True,
            "block_bypass_attempts": True
        },
        "success_criteria": {
            "llmstruct_usage_rate": 0.9,
            "context_awareness_score": 0.8,
            "tool_diversity_score": 0.6,
            "effectiveness_threshold": 0.7
        }
    }
    
    config_file = Path(project_root) / "data" / "ai_integration_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"5. Configuration saved to: {config_file}")
    
    print("\n🎯 AI INTEGRATION FORCED SUCCESSFULLY!")
    print("=" * 50)
    print("From now on, ALL AI interactions will:")
    print("  ✅ Use llmstruct context orchestration")
    print("  ✅ Apply AI delegation rules")
    print("  ✅ Optimize context for scenario")
    print("  ✅ Track usage patterns")
    print("  ✅ Provide real-time guidance")
    print("\n💡 The AI assistant is now REQUIRED to use the system!")
    
    # Return stats for verification
    return {
        "middleware_active": True,
        "monitor_active": True,
        "mode": "strict",
        "test_successful": response.used_llmstruct,
        "config_saved": config_file.exists()
    }


def check_integration_status():
    """Check current AI integration status."""
    print("🔍 CHECKING AI INTEGRATION STATUS")
    print("=" * 40)
    
    try:
        from llmstruct.ai_workflow_middleware import get_ai_middleware
        from llmstruct.ai_self_monitor import get_ai_monitor
        
        middleware = get_ai_middleware()
        monitor = get_ai_monitor()
        
        if middleware:
            stats = middleware.get_middleware_stats()
            print(f"✅ Middleware: Active ({stats['current_mode']} mode)")
            print(f"   📊 Total requests: {stats['total_requests']}")
            print(f"   🎯 LLMStruct usage: {stats['llmstruct_usage_rate']:.1%}")
        else:
            print("❌ Middleware: Not initialized")
        
        if monitor:
            analysis = monitor.analyze_behavior_trends(days=1)
            print(f"✅ Monitor: Active")
            print(f"   📊 Usage rate: {analysis.llmstruct_usage_rate:.1%}")
            print(f"   🧠 Context awareness: {analysis.context_awareness_score:.1%}")
        else:
            print("❌ Monitor: Not initialized")
            
    except ImportError as e:
        print(f"❌ Integration not available: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_integration_status()
    else:
        force_ai_integration() 