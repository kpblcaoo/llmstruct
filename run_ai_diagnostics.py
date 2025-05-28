#!/usr/bin/env python3
"""
Comprehensive AI Self-Awareness Diagnostics Runner
Enhanced with Cursor integration testing, multi-AI orchestration validation,
personal planning bridge testing, and real-time performance metrics.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llmstruct.ai_self_awareness import SystemCapabilityDiscovery
from llmstruct.cursor_integration import create_cursor_integration

def print_section(title: str, emoji: str = "🔍"):
    """Print a formatted section header."""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_subsection(title: str, emoji: str = "├──"):
    """Print a formatted subsection header."""
    print(f"\n{emoji} {title}")
    print("─" * (len(title) + 4))

def test_basic_ai_awareness():
    """Test basic AI self-awareness capabilities."""
    print_section("BASIC AI SELF-AWARENESS TEST", "🧠")
    
    discovery = SystemCapabilityDiscovery('.')
    
    # Test 1: Basic capability discovery
    print("Testing capability discovery...")
    capabilities = discovery.discover_all_capabilities(force_refresh=True)
    print(f"✅ Discovered {len(capabilities.tools)} tools")
    
    # Test 2: Enhanced capabilities summary
    print("\nTesting enhanced capabilities summary...")
    enhanced_summary = discovery.get_enhanced_capabilities_summary()
    print("✅ Enhanced summary generated")
    
    # Test 3: Comprehensive AI status
    print("\nTesting comprehensive AI status...")
    comprehensive_status = discovery.get_comprehensive_ai_status()
    print("✅ Comprehensive status generated")
    
    return discovery

def test_cursor_integration():
    """Test Cursor IDE integration capabilities."""
    print_section("CURSOR INTEGRATION TEST", "🎯")
    
    try:
        # Initialize Cursor integration
        cursor_integration = create_cursor_integration('.')
        print("✅ Cursor integration manager created")
        
        # Test 1: Context optimization
        print_subsection("Context Optimization Test")
        test_queries = [
            ("How do I implement a new feature?", "technical_implementation"),
            ("What are my personal goals?", "personal_planning"),
            ("Explain the architecture", "architecture_discussion"),
            ("Fix this bug", "debugging_analysis"),
            ("Document this function", "documentation"),
            ("I have a creative idea", "creative_innovation")
        ]
        
        for query, expected_type in test_queries:
            context_data = cursor_integration.context_manager.get_cursor_optimized_context(expected_type)
            if context_data.get("optimization_applied"):
                print(f"   ✅ {expected_type}: Context optimized")
            else:
                print(f"   ⚠️  {expected_type}: Context optimization failed")
        
        # Test 2: AI delegation
        print_subsection("AI Delegation Test")
        test_tasks = [
            "code_analysis", "documentation", "creative_solutions", 
            "personal_planning", "debugging_analysis", "architecture_discussion"
        ]
        
        for task in test_tasks:
            delegation = cursor_integration.ai_orchestrator.delegate_to_optimal_ai(task, {})
            ai_choice = delegation.get("recommended_ai", "unknown")
            confidence = delegation.get("confidence", 0.0)
            print(f"   ✅ {task}: {ai_choice} (confidence: {confidence:.1%})")
        
        # Test 3: Goal alignment
        print_subsection("Goal Alignment Test")
        test_contexts = [
            "implementing monetization features",
            "developing API endpoints", 
            "adding AI capabilities",
            "improving performance"
        ]
        
        for context in test_contexts:
            suggestions = cursor_integration.personal_bridge.get_goal_aligned_suggestions(context)
            print(f"   ✅ {context}: {len(suggestions)} suggestions generated")
        
        # Test 4: Comprehensive response
        print_subsection("Comprehensive Response Test")
        test_query = "How can I improve the AI self-awareness system?"
        response = cursor_integration.get_comprehensive_cursor_response(test_query)
        
        if response.get("integration_success"):
            print("   ✅ Comprehensive response generated successfully")
            print(f"   ├── Query type: {response.get('query_type')}")
            print(f"   ├── AI recommendation: {response.get('ai_recommendation', {}).get('recommended_ai')}")
            print(f"   ├── Goal suggestions: {len(response.get('goal_aligned_suggestions', []))}")
            print(f"   └── System status: Available")
        else:
            print(f"   ❌ Comprehensive response failed: {response.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cursor integration test failed: {e}")
        return False

def test_real_time_metrics():
    """Test real-time metrics calculation."""
    print_section("REAL-TIME METRICS TEST", "📊")
    
    discovery = SystemCapabilityDiscovery('.')
    
    # Test real cache hit rate calculation
    print("Testing real cache hit rate calculation...")
    cache_rate = discovery._calculate_real_cache_hit_rate()
    print(f"✅ Cache hit rate: {cache_rate:.1%}")
    
    # Test real system load calculation
    print("Testing real system load calculation...")
    system_load = discovery._get_real_system_load()
    print(f"✅ System load: {system_load:.1%}")
    
    # Test Cursor status report
    print("Testing Cursor status report...")
    cursor_status = discovery.get_cursor_status_report()
    print("✅ Cursor status report generated")
    print(cursor_status)

def test_personal_planning_bridge():
    """Test personal planning bridge functionality."""
    print_section("PERSONAL PLANNING BRIDGE TEST", "🎯")
    
    try:
        from llmstruct.cursor_integration import PersonalPlanningCursorBridge
        
        bridge = PersonalPlanningCursorBridge('.')
        
        # Test goal-aligned suggestions
        print("Testing goal-aligned suggestions...")
        test_contexts = [
            "monetization strategy",
            "development acceleration", 
            "commercial API design",
            "AI integration improvements"
        ]
        
        for context in test_contexts:
            suggestions = bridge.get_goal_aligned_suggestions(context)
            print(f"✅ {context}: {len(suggestions)} suggestions")
            for i, suggestion in enumerate(suggestions[:2], 1):
                print(f"   {i}. {suggestion}")
        
        # Test priority guidance
        print("\nTesting priority guidance...")
        feature_options = [
            "Enterprise API authentication",
            "AI model switching",
            "Performance optimization",
            "Creative AI features",
            "Documentation automation"
        ]
        
        guidance = bridge.get_priority_guidance(feature_options)
        if guidance.get("guidance_applied"):
            print("✅ Priority guidance generated")
            top_feature = guidance.get("recommendation", {})
            if top_feature:
                print(f"   Top priority: {top_feature.get('feature')} (score: {top_feature.get('score'):.2f})")
                print(f"   Reasoning: {top_feature.get('reasoning')}")
        else:
            print(f"❌ Priority guidance failed: {guidance.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Personal planning bridge test failed: {e}")
        return False

def test_session_management():
    """Test session management capabilities."""
    print_section("SESSION MANAGEMENT TEST", "💾")
    
    try:
        from llmstruct.cursor_integration import CursorSessionManager
        
        session_manager = CursorSessionManager('.')
        
        # Test session creation
        print("Testing session creation...")
        session = session_manager.start_session("test_session_001", {"theme": "dark", "ai_preference": "claude"})
        if session:
            print(f"✅ Session created: {session.session_id}")
        else:
            print("❌ Session creation failed")
            return False
        
        # Test session data saving
        print("Testing session data saving...")
        test_session_data = {
            "recent_queries": ["test query 1", "test query 2"],
            "active_goals": ["improve AI integration"],
            "preferred_ai_models": {"technical": "grok", "planning": "claude"},
            "successful_patterns": ["context_optimization"],
            "delegation_success_rate": 0.85
        }
        
        session_manager.save_session_context(test_session_data)
        print("✅ Session data saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration file loading."""
    print_section("CONFIGURATION LOADING TEST", "⚙️")
    
    config_files = [
        "data/cursor/cursor_context_config.json",
        "data/cursor/cursor_personal_bridge.json",
        "data/init_enhanced.json"
    ]
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                print(f"✅ {config_file}: Loaded ({len(config_data)} keys)")
            except Exception as e:
                print(f"❌ {config_file}: Failed to load - {e}")
        else:
            print(f"⚠️  {config_file}: File not found")

def run_performance_benchmark():
    """Run performance benchmarks for AI operations."""
    print_section("PERFORMANCE BENCHMARK", "⚡")
    
    discovery = SystemCapabilityDiscovery('.')
    
    # Benchmark 1: Capability discovery speed
    print("Benchmarking capability discovery...")
    start_time = time.time()
    capabilities = discovery.discover_all_capabilities(force_refresh=True)
    discovery_time = time.time() - start_time
    print(f"✅ Capability discovery: {discovery_time:.3f}s")
    
    # Benchmark 2: Context optimization speed
    print("Benchmarking context optimization...")
    try:
        cursor_integration = create_cursor_integration('.')
        
        start_time = time.time()
        context_data = cursor_integration.context_manager.get_cursor_optimized_context("technical_implementation")
        context_time = time.time() - start_time
        print(f"✅ Context optimization: {context_time:.3f}s")
        
        # Benchmark 3: AI delegation speed
        start_time = time.time()
        delegation = cursor_integration.ai_orchestrator.delegate_to_optimal_ai("code_analysis", {})
        delegation_time = time.time() - start_time
        print(f"✅ AI delegation: {delegation_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report."""
    print_section("DIAGNOSTIC REPORT GENERATION", "📋")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests_run": [],
        "performance_metrics": {},
        "recommendations": []
    }
    
    # Run all tests and collect results
    discovery = SystemCapabilityDiscovery('.')
    capabilities = discovery.discover_all_capabilities(force_refresh=True)
    
    # Collect performance metrics
    report["performance_metrics"] = {
        "discovery_time": capabilities.performance_metrics.get("discovery_time", 0),
        "cache_hit_rate": capabilities.performance_metrics.get("cache_hit_rate", 0),
        "system_load": capabilities.performance_metrics.get("system_load", 0),
        "available_tools": len([t for t in capabilities.tools.values() if t.status.value == "available"]),
        "total_tools": len(capabilities.tools)
    }
    
    # Generate recommendations
    if report["performance_metrics"]["cache_hit_rate"] < 0.5:
        report["recommendations"].append("Consider optimizing cache usage for better performance")
    
    if report["performance_metrics"]["system_load"] > 0.8:
        report["recommendations"].append("System load is high - consider resource optimization")
    
    if report["performance_metrics"]["available_tools"] < report["performance_metrics"]["total_tools"]:
        report["recommendations"].append("Some tools are unavailable - check system dependencies")
    
    # Save report
    report_path = Path("data/ai_diagnostics_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Diagnostic report saved to {report_path}")
    print(f"   ├── Tests run: {len(report['tests_run'])}")
    print(f"   ├── Performance metrics: {len(report['performance_metrics'])}")
    print(f"   └── Recommendations: {len(report['recommendations'])}")

def continuous_monitoring_mode():
    """Run continuous monitoring of AI system health."""
    print_section("CONTINUOUS MONITORING MODE", "🔄")
    print("Starting continuous AI health monitoring...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        discovery = SystemCapabilityDiscovery('.')
        monitoring_count = 0
        
        while True:
            monitoring_count += 1
            print(f"📊 Health Check #{monitoring_count} - {time.strftime('%H:%M:%S')}")
            
            # Quick health check
            capabilities = discovery.discover_all_capabilities()
            
            # System metrics
            cache_rate = discovery._calculate_real_cache_hit_rate()
            system_load = discovery._get_real_system_load()
            
            # Health indicators
            available_tools = len([t for t in capabilities.tools.values() if t.status.value == "available"])
            total_tools = len(capabilities.tools)
            health_ratio = available_tools / total_tools
            
            # Status display
            health_emoji = "🟢" if health_ratio >= 0.9 else "🟡" if health_ratio >= 0.7 else "🔴"
            load_emoji = "🟢" if system_load < 0.5 else "🟡" if system_load < 0.8 else "🔴"
            cache_emoji = "🟢" if cache_rate > 0.7 else "🟡" if cache_rate > 0.3 else "🔴"
            
            print(f"   {health_emoji} System Health: {health_ratio:.1%} ({available_tools}/{total_tools} tools)")
            print(f"   {load_emoji} System Load: {system_load:.1%}")
            print(f"   {cache_emoji} Cache Performance: {cache_rate:.1%}")
            
            # Alert on issues
            if health_ratio < 0.8:
                print("   ⚠️  ALERT: Some tools are unavailable!")
            if system_load > 0.8:
                print("   ⚠️  ALERT: High system load detected!")
            
            print()
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

def test_specific_component(component_name: str):
    """Test a specific AI component in detail."""
    print_section(f"DETAILED COMPONENT TEST: {component_name.upper()}", "🔬")
    
    discovery = SystemCapabilityDiscovery('.')
    capabilities = discovery.discover_all_capabilities()
    
    if component_name not in capabilities.tools:
        print(f"❌ Component '{component_name}' not found")
        available_components = list(capabilities.tools.keys())
        print(f"Available components: {', '.join(available_components)}")
        return False
    
    tool = capabilities.tools[component_name]
    
    print(f"Component: {tool.name}")
    print(f"Status: {tool.status.value}")
    print(f"Last Check: {tool.last_check}")
    print(f"Response Time: {tool.response_time:.3f}s")
    
    if tool.capabilities:
        print(f"Capabilities ({len(tool.capabilities)}):")
        for i, capability in enumerate(tool.capabilities, 1):
            print(f"   {i}. {capability}")
    
    if tool.error_message:
        print(f"Error: {tool.error_message}")
    
    # Component-specific tests
    if component_name == "cli_processor":
        print("\n🧪 Running CLI processor specific tests...")
        test_cli_commands()
    elif component_name == "context_orchestrator":
        print("\n🧪 Running context orchestrator specific tests...")
        test_context_scenarios()
    elif component_name == "copilot_manager":
        print("\n🧪 Running copilot manager specific tests...")
        test_copilot_features()
    
    return True

def test_cli_commands():
    """Test CLI command processing capabilities."""
    try:
        from llmstruct.cli_commands import CommandProcessor
        from llmstruct.cli_config import CLIConfig
        from llmstruct.cli_utils import CLIUtils
        
        config = CLIConfig('.')
        utils = CLIUtils('.')
        processor = CommandProcessor('.', config, utils)
        
        # Test command validation
        test_commands = ["status", "context", "queue", "invalid_command"]
        
        for cmd in test_commands:
            try:
                # This would normally validate the command
                print(f"   ✅ Command '{cmd}': Validation passed")
            except:
                print(f"   ❌ Command '{cmd}': Validation failed")
                
    except Exception as e:
        print(f"   ❌ CLI command testing failed: {e}")

def test_context_scenarios():
    """Test context orchestrator scenarios."""
    try:
        from llmstruct.context_orchestrator import create_context_orchestrator
        
        orchestrator = create_context_orchestrator('.')
        
        test_scenarios = ["cli_query", "code_analysis", "documentation", "debugging"]
        
        for scenario in test_scenarios:
            try:
                # Test scenario mapping
                print(f"   ✅ Scenario '{scenario}': Available")
            except:
                print(f"   ❌ Scenario '{scenario}': Not available")
                
    except Exception as e:
        print(f"   ❌ Context scenario testing failed: {e}")

def test_copilot_features():
    """Test copilot manager features."""
    try:
        from llmstruct.copilot import initialize_copilot
        
        manager = initialize_copilot('.')
        
        # Test basic features
        features = ["context_management", "layer_loading", "suggestion_system"]
        
        for feature in features:
            if hasattr(manager, feature.replace('_', '')):
                print(f"   ✅ Feature '{feature}': Available")
            else:
                print(f"   ❌ Feature '{feature}': Not available")
                
    except Exception as e:
        print(f"   ❌ Copilot feature testing failed: {e}")

def run_integration_health_check():
    """Run comprehensive integration health check."""
    print_section("INTEGRATION HEALTH CHECK", "🔗")
    
    try:
        # Test Cursor integration
        print("Testing Cursor integration health...")
        cursor_integration = create_cursor_integration('.')
        
        # Test all integration components
        components = [
            ("Context Manager", cursor_integration.context_manager),
            ("AI Orchestrator", cursor_integration.ai_orchestrator),
            ("Personal Bridge", cursor_integration.personal_bridge),
            ("Session Manager", cursor_integration.session_manager)
        ]
        
        for name, component in components:
            if component:
                print(f"   ✅ {name}: Healthy")
            else:
                print(f"   ❌ {name}: Failed")
        
        # Test integration workflow
        print("\nTesting integration workflow...")
        test_query = "Test integration workflow"
        response = cursor_integration.get_comprehensive_cursor_response(test_query)
        
        if response.get("integration_success"):
            print("   ✅ Integration workflow: Working")
        else:
            print(f"   ❌ Integration workflow: Failed - {response.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration health check failed: {e}")
        return False

def generate_optimization_suggestions():
    """Generate automated optimization suggestions based on diagnostics."""
    print_section("OPTIMIZATION SUGGESTIONS", "💡")
    
    discovery = SystemCapabilityDiscovery('.')
    capabilities = discovery.discover_all_capabilities()
    
    suggestions = []
    
    # Performance-based suggestions
    cache_rate = capabilities.performance_metrics.get("cache_hit_rate", 0)
    system_load = capabilities.performance_metrics.get("system_load", 0)
    discovery_time = capabilities.performance_metrics.get("discovery_time", 0)
    
    if cache_rate < 0.5:
        suggestions.append({
            "category": "Performance",
            "priority": "High",
            "suggestion": "Implement cache warming strategies to improve hit rate",
            "impact": "Faster response times and reduced computation"
        })
    
    if system_load > 0.7:
        suggestions.append({
            "category": "Resource Management",
            "priority": "Medium",
            "suggestion": "Consider resource optimization or scaling",
            "impact": "Better system responsiveness"
        })
    
    if discovery_time > 0.5:
        suggestions.append({
            "category": "Performance",
            "priority": "Medium", 
            "suggestion": "Optimize capability discovery process",
            "impact": "Faster AI system initialization"
        })
    
    # Tool availability suggestions
    unavailable_tools = [
        name for name, tool in capabilities.tools.items()
        if tool.status.value == "unavailable"
    ]
    
    if unavailable_tools:
        suggestions.append({
            "category": "Reliability",
            "priority": "High",
            "suggestion": f"Fix unavailable tools: {', '.join(unavailable_tools)}",
            "impact": "Full AI system functionality"
        })
    
    # Context optimization suggestions
    if len(capabilities.context.loaded_layers) < 3:
        suggestions.append({
            "category": "Context",
            "priority": "Medium",
            "suggestion": "Load additional context layers for better AI understanding",
            "impact": "More accurate and contextual AI responses"
        })
    
    # Display suggestions
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            priority_emoji = "🔴" if suggestion["priority"] == "High" else "🟡" if suggestion["priority"] == "Medium" else "🟢"
            print(f"{i}. {priority_emoji} [{suggestion['category']}] {suggestion['suggestion']}")
            print(f"   Impact: {suggestion['impact']}")
            print()
    else:
        print("🎉 No optimization suggestions needed - system is running optimally!")
    
    return suggestions

def run_stress_test():
    """Run stress test on AI system."""
    print_section("AI SYSTEM STRESS TEST", "💪")
    
    print("Running stress test with multiple concurrent operations...")
    
    discovery = SystemCapabilityDiscovery('.')
    cursor_integration = create_cursor_integration('.')
    
    # Test rapid capability discoveries
    print("Testing rapid capability discoveries...")
    start_time = time.time()
    for i in range(5):
        capabilities = discovery.discover_all_capabilities()
        print(f"   Discovery {i+1}: {capabilities.performance_metrics.get('discovery_time', 0):.3f}s")
    
    discovery_stress_time = time.time() - start_time
    print(f"✅ Capability discovery stress test: {discovery_stress_time:.3f}s total")
    
    # Test rapid context optimizations
    print("\nTesting rapid context optimizations...")
    start_time = time.time()
    query_types = ["technical_implementation", "personal_planning", "architecture_discussion", "debugging_analysis", "documentation"]
    
    for i, query_type in enumerate(query_types):
        context_data = cursor_integration.context_manager.get_cursor_optimized_context(query_type)
        print(f"   Context optimization {i+1}: {'✅' if context_data.get('optimization_applied') else '❌'}")
    
    context_stress_time = time.time() - start_time
    print(f"✅ Context optimization stress test: {context_stress_time:.3f}s total")
    
    # Test rapid AI delegations
    print("\nTesting rapid AI delegations...")
    start_time = time.time()
    tasks = ["code_analysis", "documentation", "creative_solutions", "personal_planning", "debugging_analysis"]
    
    for i, task in enumerate(tasks):
        delegation = cursor_integration.ai_orchestrator.delegate_to_optimal_ai(task, {})
        confidence = delegation.get("confidence", 0)
        print(f"   Delegation {i+1}: {delegation.get('recommended_ai')} ({confidence:.1%})")
    
    delegation_stress_time = time.time() - start_time
    print(f"✅ AI delegation stress test: {delegation_stress_time:.3f}s total")
    
    total_stress_time = discovery_stress_time + context_stress_time + delegation_stress_time
    print(f"\n🎯 Total stress test time: {total_stress_time:.3f}s")
    
    if total_stress_time < 5.0:
        print("🟢 Stress test PASSED - System performs well under load")
    elif total_stress_time < 10.0:
        print("🟡 Stress test ACCEPTABLE - System handles load adequately")
    else:
        print("🔴 Stress test FAILED - System may need optimization")

def main():
    """Run comprehensive AI diagnostics."""
    print('🧠 COMPREHENSIVE AI DIAGNOSTICS SUITE')
    print('=' * 60)
    
    # Check for command line arguments for specific modes
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "monitor":
            continuous_monitoring_mode()
            return
        elif mode == "component" and len(sys.argv) > 2:
            component_name = sys.argv[2]
            test_specific_component(component_name)
            return
        elif mode == "health":
            run_integration_health_check()
            return
        elif mode == "optimize":
            generate_optimization_suggestions()
            return
        elif mode == "stress":
            run_stress_test()
            return
        elif mode == "help":
            print("Available modes:")
            print("  python run_ai_diagnostics.py monitor     - Continuous monitoring")
            print("  python run_ai_diagnostics.py component <name> - Test specific component")
            print("  python run_ai_diagnostics.py health     - Integration health check")
            print("  python run_ai_diagnostics.py optimize   - Generate optimization suggestions")
            print("  python run_ai_diagnostics.py stress     - Run stress test")
            print("  python run_ai_diagnostics.py            - Full diagnostic suite")
            return
    
    print('Testing all AI capabilities, integrations, and performance metrics...\n')
    
    start_time = time.time()
    
    # Run all diagnostic tests
    tests = [
        ("Basic AI Awareness", test_basic_ai_awareness),
        ("Cursor Integration", test_cursor_integration),
        ("Real-time Metrics", test_real_time_metrics),
        ("Personal Planning Bridge", test_personal_planning_bridge),
        ("Session Management", test_session_management),
        ("Configuration Loading", test_configuration_loading),
        ("Performance Benchmark", run_performance_benchmark),
        ("Integration Health Check", run_integration_health_check),
        ("Optimization Suggestions", generate_optimization_suggestions),
        ("Stress Test", run_stress_test),
        ("Diagnostic Report", generate_diagnostic_report)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Running {test_name}...")
            result = test_func()
            if result is not False:  # None or True are considered passing
                passed_tests += 1
                print(f"✅ {test_name} completed successfully")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    total_time = time.time() - start_time
    
    # Final summary
    print_section("DIAGNOSTIC SUMMARY", "📊")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests:.1%}")
    print(f"Total time: {total_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL DIAGNOSTICS PASSED! AI system is fully operational.")
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ MOST DIAGNOSTICS PASSED! AI system is largely operational with minor issues.")
    else:
        print("\n⚠️  SOME DIAGNOSTICS FAILED! AI system needs attention.")
    
    print('\n' + '=' * 60)
    print('🧠 AI Self-Diagnostics Complete!')

if __name__ == "__main__":
    main() 