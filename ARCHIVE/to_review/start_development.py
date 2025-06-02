#!/usr/bin/env python3
"""
LLMStruct Development Startup Script
Convenient one-command startup for daily development workflow.
Enhanced with AI Workflow Middleware and Self-Monitoring for seamless llmstruct integration.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header():
    """Print startup header."""
    print("🚀 LLMStruct Development Environment Startup")
    print("=" * 50)
    print()

def initialize_ai_integration_layer():
    """Initialize AI integration layer - this is the NEW seamless integration"""
    print("🤖 Initializing AI Integration Layer...")
    
    try:
        # Import our AI middleware and monitoring components
        from llmstruct.ai_workflow_middleware import initialize_ai_middleware, AIWorkflowMode
        from llmstruct.ai_self_monitor import initialize_ai_monitor, record_ai_usage
        
        project_root = str(Path(__file__).parent)
        
        # 1. Initialize middleware in GUIDED mode for development (not STRICT to avoid blocking)
        print("   🎯 Activating AI Workflow Middleware (GUIDED mode)...")
        middleware = initialize_ai_middleware(project_root, AIWorkflowMode.GUIDED)
        
        # 2. Initialize monitoring system
        print("   📊 Activating AI Self-Monitor...")
        monitor = initialize_ai_monitor(project_root)
        
        # 3. Quick integration test
        test_response = middleware.process_ai_request("[startup] Initialize development environment")
        
        print(f"   ✅ AI Integration Layer active")
        print(f"   📈 Middleware ready: {test_response.used_llmstruct}")
        print(f"   🧠 Context optimization: {test_response.context_optimization.get('optimization_successful', False)}")
        
        # 4. Record the startup event
        record_ai_usage(
            query="development_environment_startup",
            tools_used=["ai_workflow_middleware", "ai_self_monitor", "context_orchestrator"],
            used_llmstruct=True,
            context_tags=["startup"],
            metadata={"environment": "development", "auto_init": True}
        )
        
        return {
            "middleware": middleware,
            "monitor": monitor,
            "integration_active": True,
            "startup_test_successful": test_response.used_llmstruct
        }
        
    except Exception as e:
        print(f"   ⚠️ AI Integration Layer initialization failed: {e}")
        print("   💡 Continuing without AI integration enforcement")
        return {
            "middleware": None,
            "monitor": None,
            "integration_active": False,
            "error": str(e)
        }

def check_environment():
    """Check if development environment is properly set up."""
    print("🔍 Checking development environment...")
    
    # Check virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   Consider running: source venv/bin/activate")
    else:
        print("✅ Virtual environment active")
    
    # Check required files
    required_files = [
        "data/init_enhanced.json",
        "data/cursor/cursor_context_config.json", 
        "data/cursor/cursor_personal_bridge.json",
        "run_ai_diagnostics.py",
        "struct.json",  # Essential for WorkflowOrchestrator
        "force_ai_integration.py"  # AI integration components
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        if "struct.json" in missing_files:
            print("   🔧 Run: python -m llmstruct parse . -o ./struct.json")
        return False
    
    print("✅ All required files present")
    return True

def initialize_workflow_orchestrator():
    """Initialize and test WorkflowOrchestrator integration."""
    print("\n🎼 Initializing Workflow Orchestrator...")
    
    try:
        from llmstruct.workflow_orchestrator import WorkflowOrchestrator
        
        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(".", debug=False)
        print("✅ WorkflowOrchestrator initialized")
        
        # Test context loading
        print("🔍 Loading comprehensive context...")
        context = orchestrator.get_current_context()
        
        if 'error' not in context:
            print("✅ Context loaded successfully")
            
            # Show key context metrics
            copilot_status = context.get('copilot_status', {})
            system_caps = context.get('system_capabilities', {})
            struct_analysis = context.get('struct_analysis', {})
            
            print(f"   📊 Copilot layers: {len(copilot_status.get('loaded_layers', []))}")
            print(f"   🧠 AI capabilities: {len(system_caps.get('capabilities', []))}")
            
            if 'stats' in struct_analysis:
                stats = struct_analysis['stats']
                print(f"   📁 Modules: {stats.get('modules_count', 0)}")
                print(f"   ⚙️  Functions: {stats.get('functions_count', 0)}")
                
                # Show duplication metrics
                dup_analysis = struct_analysis.get('duplication_analysis', {})
                if dup_analysis:
                    dup_pct = dup_analysis.get('duplication_percentage', 0)
                    print(f"   🔄 Duplication: {dup_pct:.1f}%")
            
            return orchestrator
        else:
            print(f"❌ Context loading failed: {context.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ WorkflowOrchestrator initialization failed: {e}")
        return None

def initialize_cursor_ai_bridge():
    """Initialize and test CursorAIBridge integration."""
    print("\n🤖 Initializing Cursor AI Bridge...")
    
    try:
        from llmstruct.cursor_ai_bridge import CursorAIBridge
        
        # Initialize bridge
        bridge = CursorAIBridge(".")
        print("✅ CursorAIBridge initialized")
        
        # Test AI context
        print("🔍 Testing AI context loading...")
        context = bridge.ai_get_context("startup_check")
        
        if 'error' not in context:
            print("✅ AI context loaded successfully")
            
            project_state = context.get('project_state', {})
            print(f"   📁 Modules: {project_state.get('modules_count', 0)}")
            print(f"   ⚙️  Functions: {project_state.get('functions_count', 0)}")
            print(f"   📋 Active tasks: {project_state.get('active_tasks', 0)}")
            
            # Test AI delegation
            print("🤖 Testing AI delegation...")
            task_analysis = bridge.ai_analyze_task("startup system check")
            ai_rec = task_analysis.get('recommended_ai', {})
            print(f"   🎯 Recommended AI: {ai_rec.get('ai', 'unknown')}")
            
            # Test available commands
            commands = context.get('available_commands', {})
            print(f"   ⚙️  Available AI commands: {len(commands)}")
            
            return bridge
        else:
            print(f"❌ AI context loading failed: {context.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ CursorAIBridge initialization failed: {e}")
        return None

def sync_architecture_components(orchestrator, ai_integration):
    """Sync with existing llmstruct architecture components and AI integration."""
    print("\n🔄 Syncing architecture components...")
    
    try:
        sync_success = True
        
        # Sync workflow orchestrator
        if orchestrator:
            sync_results = orchestrator.sync_with_existing_architecture()
            
            for component, success in sync_results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {component}")
                if not success:
                    sync_success = False
        else:
            print("   ❌ WorkflowOrchestrator not available for sync")
            sync_success = False
        
        # Sync AI integration layer
        if ai_integration and ai_integration.get('integration_active'):
            middleware = ai_integration.get('middleware')
            monitor = ai_integration.get('monitor')
            
            if middleware:
                stats = middleware.get_middleware_stats()
                print(f"   ✅ AI Middleware (mode: {stats['current_mode']})")
            
            if monitor:
                print("   ✅ AI Self-Monitor")
            
            print("   ✅ AI Integration Layer synced")
        else:
            print("   ⚠️  AI Integration Layer not active")
        
        return sync_success
            
    except Exception as e:
        print(f"❌ Architecture sync failed: {e}")
        return False

def run_system_health_check():
    """Run comprehensive system health check."""
    print("\n🏥 Running system health check...")
    
    try:
        result = subprocess.run([
            sys.executable, "run_ai_diagnostics.py", "health"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ System health check passed")
            return True
        else:
            print("❌ System health check failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Health check timed out")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def get_optimization_suggestions(orchestrator=None):
    """Get AI optimization suggestions with WorkflowOrchestrator integration."""
    print("\n💡 Getting optimization suggestions...")
    
    # Try WorkflowOrchestrator first for enhanced suggestions
    if orchestrator:
        try:
            print("🎼 Using WorkflowOrchestrator for enhanced analysis...")
            duplication_analysis = orchestrator.analyze_codebase_for_duplicates()
            
            if 'error' not in duplication_analysis:
                recommendations = duplication_analysis.get('recommendations', [])
                high_priority = [r for r in recommendations if r.get('priority') == 'high']
                
                if high_priority:
                    print("🔴 High Priority Code Improvements:")
                    for rec in high_priority[:3]:
                        print(f"   • {rec['function']}: {rec['recommendation']}")
                
                next_steps = duplication_analysis.get('next_steps', [])
                if next_steps:
                    print("🎯 Recommended Actions:")
                    for i, step in enumerate(next_steps[:2], 1):
                        print(f"   {i}. {step}")
                
                return True
        except Exception as e:
            print(f"⚠️  WorkflowOrchestrator suggestions failed: {e}")
    
    # Fallback to run_ai_diagnostics
    try:
        result = subprocess.run([
            sys.executable, "run_ai_diagnostics.py", "optimize"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Extract suggestions from output
            lines = result.stdout.split('\n')
            suggestions = []
            for line in lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    suggestions.append(line.strip())
            
            if suggestions:
                print("📋 System optimization suggestions:")
                for suggestion in suggestions:
                    print(f"   {suggestion}")
            else:
                print("🎉 No optimization suggestions - system running optimally!")
            return True
        else:
            print("⚠️  Could not get optimization suggestions")
            return False
    except Exception as e:
        print(f"⚠️  Optimization check error: {e}")
        return False

def check_git_status():
    """Check git repository status."""
    print("\n📦 Checking git status...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run([
            "git", "status", "--porcelain"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print("📝 Uncommitted changes detected:")
                change_lines = changes.split('\n')
                for line in change_lines[:5]:  # Show first 5 changes
                    print(f"   {line}")
                if len(change_lines) > 5:
                    remaining_count = len(change_lines) - 5
                    print(f"   ... and {remaining_count} more")
            else:
                print("✅ Working directory clean")
            
            # Check for remote updates
            try:
                subprocess.run(["git", "fetch"], capture_output=True, timeout=10)
                result = subprocess.run([
                    "git", "log", "HEAD..origin/main", "--oneline"
                ], capture_output=True, text=True, timeout=10)
                
                if result.stdout.strip():
                    print("📥 Remote updates available:")
                    for line in result.stdout.strip().split('\n')[:3]:
                        print(f"   {line}")
                    print("   Consider running: git pull origin main")
                else:
                    print("✅ Up to date with remote")
            except:
                print("⚠️  Could not check remote status")
            
            return True
        else:
            print("⚠️  Not in a git repository or git error")
            return False
    except Exception as e:
        print(f"⚠️  Git check error: {e}")
        return False

def show_current_context():
    """Show current project context and priorities."""
    print("\n📋 Current project context...")
    
    try:
        # Load and display key information from JSON files
        init_file = Path("data/init_enhanced.json")
        if init_file.exists():
            with open(init_file, 'r') as f:
                init_data = json.load(f)
            
            print("🎯 Project Vision:")
            vision = init_data.get("project_vision", {})
            mission = vision.get("core_mission", "Not defined")
            print(f"   {mission}")
            
            goals = vision.get("goals", [])
            if goals:
                print("📌 Current Goals:")
                for i, goal in enumerate(goals[:3], 1):
                    print(f"   {i}. {goal}")
        
        # Show personal planning context
        bridge_file = Path("data/cursor/cursor_personal_bridge.json")
        if bridge_file.exists():
            with open(bridge_file, 'r') as f:
                bridge_data = json.load(f)
            
            business_obj = bridge_data.get("business_objectives", {})
            primary_goal = business_obj.get("primary_goal", "Not defined")
            print(f"💼 Primary Business Goal: {primary_goal}")
            
            focus_areas = business_obj.get("focus_areas", [])
            if focus_areas:
                print("🔍 Focus Areas:")
                for area in focus_areas[:3]:
                    print(f"   • {area}")
        
        return True
    except Exception as e:
        print(f"⚠️  Context loading error: {e}")
        return False

def show_useful_commands():
    """Show useful commands for development."""
    print("\n🛠️  Useful development commands:")
    print("   python run_ai_diagnostics.py           - Full system diagnostics")
    print("   python run_ai_diagnostics.py health    - Quick health check")
    print("   python run_ai_diagnostics.py optimize  - Get optimization suggestions")
    print("   python run_ai_diagnostics.py stress    - Performance stress test")
    print("   python run_ai_diagnostics.py monitor   - Continuous monitoring")
    print("   python -m llmstruct.cli --help         - CLI help")
    print()
    print("🤖 AI Integration Commands (NEW - SEAMLESS LLMSTRUCT):")
    print("   python force_ai_integration.py          - Force STRICT AI integration mode")
    print("   python force_ai_integration.py status   - Check AI integration status")
    print("   python -c \"from llmstruct.ai_workflow_middleware import get_ai_middleware; print(get_ai_middleware().get_middleware_stats())\" - Get AI usage stats")
    print("   python -c \"from llmstruct.ai_self_monitor import get_ai_monitor; print(get_ai_monitor().get_monitoring_report())\" - Get AI behavior report")
    print()
    print("🎼 Workflow Orchestrator commands:")
    print("   python -m llmstruct analyze-duplicates  - Analyze code duplication")
    print("   python -m llmstruct audit --include-duplicates - Full project audit")
    print("   python -c \"from llmstruct.workflow_orchestrator import WorkflowOrchestrator; print(WorkflowOrchestrator('.').get_ai_onboarding_guide())\" - AI onboarding guide")
    print()
    print("🤖 Cursor AI Bridge commands:")
    print("   python -m llmstruct.cursor_ai_bridge ai-context                    - Get AI-optimized context")
    print("   python -m llmstruct.cursor_ai_bridge ai-analyze-task --task \"description\" - Analyze task with AI")
    print("   python -m llmstruct.cursor_ai_bridge ai-check-duplicates           - Check code duplicates")
    print("   python -m llmstruct.cursor_ai_bridge ai-suggest --context \"topic\"   - Get AI suggestions")
    print("   python -m llmstruct.cursor_ai_bridge ai-onboard                    - Get AI onboarding guide")
    print("   python test_ai_bridge.py context                                   - Quick context check")
    print("   python test_ai_bridge.py analyze \"task description\"                - Quick task analysis")
    print()
    print("🎯 AI Integration Testing & Monitoring:")
    print("   # Test AI middleware integration")
    print("   python -c \"from llmstruct.ai_workflow_middleware import process_ai_query; print(process_ai_query('[test] Check llmstruct integration'))\"")
    print()
    print("   # Get real-time AI guidance")
    print("   python -c \"from llmstruct.ai_self_monitor import get_ai_monitor; print(get_ai_monitor().get_real_time_guidance('implement new feature'))\"")
    print()
    print("   # Force strict AI integration")
    print("   python -c \"from llmstruct.ai_workflow_middleware import get_ai_middleware; get_ai_middleware().force_llmstruct_mode(); print('STRICT mode activated')\"")
    print()
    print("🎯 Legacy AI Integration commands:")
    print("   # Get comprehensive AI status")
    print("   python -c \"from llmstruct.ai_self_awareness import SystemCapabilityDiscovery; print(SystemCapabilityDiscovery('.').get_cursor_status_report())\"")
    print()
    print("   # Test Cursor integration")
    print("   python -c \"from llmstruct.cursor_integration import create_cursor_integration; ci = create_cursor_integration('.'); print(ci.get_comprehensive_cursor_response('system status'))\"")
    print()
    print("   # Get current workflow context")
    print("   python -c \"from llmstruct.workflow_orchestrator import WorkflowOrchestrator; print(WorkflowOrchestrator('.').get_current_context())\"")
    print()
    print("💡 AI Assistant Workflow (ENHANCED):")
    print("   🎯 Context Tags: Use [code], [debug], [discuss], [review], [meta] in queries")
    print("   🧠 AI Delegation: System automatically routes tasks to optimal AI")
    print("   📊 Context Optimization: Automatic context enhancement for all requests")
    print("   📈 Usage Monitoring: Real-time feedback on AI interaction patterns")
    print("   For new AI: Read docs/CURSOR_AI_INTEGRATION.md and use AI Bridge")
    print("   Start with: python test_ai_bridge.py context")
    print()
    print("🔄 Quick AI Integration Test:")
    print("   python -c \"from llmstruct.ai_workflow_middleware import process_ai_query; result = process_ai_query('[test] analyze project architecture'); print('✅ AI Integration Working' if result.used_llmstruct else '❌ AI Integration Failed')\"")

def main():
    """Main startup routine with AI Workflow Middleware and WorkflowOrchestrator integration."""
    print_header()
    
    # Track overall success and component states
    all_checks_passed = True
    orchestrator = None
    ai_bridge = None
    ai_integration = None
    
    # === CRITICAL: Initialize AI Integration Layer FIRST ===
    # This ensures ALL AI interactions from this point forward use llmstruct
    ai_integration = initialize_ai_integration_layer()
    if not ai_integration.get('integration_active'):
        print("   ⚠️  Continuing without AI enforcement (development mode)")
    else:
        print("   🎯 AI Integration Layer: ACTIVE - all AI requests will use llmstruct")
    
    # Run environment checks
    if not check_environment():
        all_checks_passed = False
    
    # Initialize WorkflowOrchestrator
    orchestrator = initialize_workflow_orchestrator()
    if orchestrator is None:
        all_checks_passed = False
    
    # Initialize CursorAIBridge
    ai_bridge = initialize_cursor_ai_bridge()
    if ai_bridge is None:
        all_checks_passed = False
    
    # Sync all architecture components including AI integration
    if not sync_architecture_components(orchestrator, ai_integration):
        all_checks_passed = False
    
    # Run system health check
    if not run_system_health_check():
        all_checks_passed = False
    
    # Get optimization suggestions
    if not get_optimization_suggestions(orchestrator):
        all_checks_passed = False
    
    # Check git status
    if not check_git_status():
        all_checks_passed = False
    
    # Show current project context
    if not show_current_context():
        all_checks_passed = False
    
    # === AI INTEGRATION STATUS REPORT ===
    print("\n🤖 AI Integration Status Report:")
    if ai_integration and ai_integration.get('integration_active'):
        middleware = ai_integration.get('middleware')
        monitor = ai_integration.get('monitor')
        
        if middleware:
            stats = middleware.get_middleware_stats()
            print(f"   ✅ AI Middleware: {stats['current_mode']} mode")
            print(f"   📊 Requests processed: {stats['total_requests']}")
            print(f"   🎯 LLMStruct usage rate: {stats['llmstruct_usage_rate']:.1%}")
        
        if monitor:
            analysis = monitor.analyze_behavior_trends(days=1)
            print(f"   ✅ AI Monitor: Active")
            print(f"   🧠 Context awareness: {analysis.context_awareness_score:.1%}")
            print(f"   💡 Real-time guidance: Available")
        
        print("   🎉 AI Integration: SEAMLESSLY ACTIVE")
        print("   💬 All AI interactions will now use enhanced llmstruct context!")
    else:
        print("   ⚠️  AI Integration: Not active (fallback mode)")
        error = ai_integration.get('error') if ai_integration else 'Unknown'
        print(f"   🔧 Issue: {error}")
    
    # Show summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 Development environment ready!")
        print("✅ All systems operational")
        if ai_integration and ai_integration.get('integration_active'):
            print("🤖 AI Integration: SEAMLESSLY ENFORCED")
        if orchestrator:
            print("🎼 WorkflowOrchestrator: Active and integrated")
        if ai_bridge:
            print("🤖 CursorAIBridge: Active and ready for AI assistance")
    else:
        print("⚠️  Development environment has issues")
        print("🔧 Please address the warnings above")
    
    show_useful_commands()
    
    # Final AI integration message
    print("\n🚀 Happy coding with AI-enhanced development!")
    if ai_integration and ai_integration.get('integration_active'):
        print("🎯 AI INTEGRATION: All AI interactions now use llmstruct system automatically!")
        print("📝 Use context tags: [code], [debug], [discuss], [review] for optimal results")
        print("🧠 AI assistants will receive enhanced context and guidance")
    else:
        print("💡 To activate AI integration later, run: python force_ai_integration.py")
    
    print("🎼 WorkflowOrchestrator provides comprehensive context management")
    if ai_bridge:
        print("🤖 CursorAIBridge enables seamless AI integration")
    print("=" * 50)

    # Return status for scripting/testing
    return {
        "success": all_checks_passed,
        "ai_integration_active": ai_integration.get('integration_active', False) if ai_integration else False,
        "orchestrator_ready": orchestrator is not None,
        "ai_bridge_ready": ai_bridge is not None,
        "components": {
            "ai_integration": ai_integration,
            "orchestrator": orchestrator,
            "ai_bridge": ai_bridge
        }
    }

if __name__ == "__main__":
    main() 