#!/usr/bin/env python3
"""
LLMStruct Development Startup Script
Convenient one-command startup for daily development workflow.
Enhanced with WorkflowOrchestrator integration for comprehensive context management.
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
        "struct.json"  # Essential for WorkflowOrchestrator
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

def sync_architecture_components(orchestrator):
    """Sync with existing llmstruct architecture components."""
    print("\n🔄 Syncing architecture components...")
    
    try:
        if orchestrator:
            sync_results = orchestrator.sync_with_existing_architecture()
            
            for component, success in sync_results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {component}")
            
            return all(sync_results.values())
        else:
            print("❌ No orchestrator available for sync")
            return False
            
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
    print("🎯 AI Integration commands:")
    print("   # Get comprehensive AI status")
    print("   python -c \"from llmstruct.ai_self_awareness import SystemCapabilityDiscovery; print(SystemCapabilityDiscovery('.').get_cursor_status_report())\"")
    print()
    print("   # Test Cursor integration")
    print("   python -c \"from llmstruct.cursor_integration import create_cursor_integration; ci = create_cursor_integration('.'); print(ci.get_comprehensive_cursor_response('system status'))\"")
    print()
    print("   # Get current workflow context")
    print("   python -c \"from llmstruct.workflow_orchestrator import WorkflowOrchestrator; print(WorkflowOrchestrator('.').get_current_context())\"")
    print()
    print("💡 Quick AI assistance:")
    print("   For new AI: Read docs/CURSOR_AI_INTEGRATION.md and use AI Bridge")
    print("   Start with: python test_ai_bridge.py context")

def main():
    """Main startup routine with WorkflowOrchestrator integration."""
    print_header()
    
    # Track overall success
    all_checks_passed = True
    orchestrator = None
    ai_bridge = None
    
    # Run startup checks
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
    
    # Sync architecture components
    if orchestrator and not sync_architecture_components(orchestrator):
        all_checks_passed = False
    
    if not run_system_health_check():
        all_checks_passed = False
    
    if not get_optimization_suggestions(orchestrator):
        all_checks_passed = False
    
    if not check_git_status():
        all_checks_passed = False
    
    if not show_current_context():
        all_checks_passed = False
    
    # Show summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 Development environment ready!")
        print("✅ All systems operational")
        if orchestrator:
            print("🎼 WorkflowOrchestrator: Active and integrated")
        if ai_bridge:
            print("🤖 CursorAIBridge: Active and ready for AI assistance")
    else:
        print("⚠️  Development environment has issues")
        print("🔧 Please address the warnings above")
    
    show_useful_commands()
    
    print("\n🚀 Happy coding with AI-enhanced development!")
    print("🎼 WorkflowOrchestrator provides comprehensive context management")
    if ai_bridge:
        print("🤖 CursorAIBridge enables seamless AI integration")
    print("=" * 50)

if __name__ == "__main__":
    main() 