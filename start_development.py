#!/usr/bin/env python3
"""
LLMStruct Development Startup Script
Convenient one-command startup for daily development workflow.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

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
        "run_ai_diagnostics.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

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

def get_optimization_suggestions():
    """Get AI optimization suggestions."""
    print("\n💡 Getting optimization suggestions...")
    
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
                print("📋 Optimization suggestions:")
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
    print("🎯 AI Integration commands:")
    print("   # Get comprehensive AI status")
    print("   python -c \"from llmstruct.ai_self_awareness import SystemCapabilityDiscovery; print(SystemCapabilityDiscovery('.').get_cursor_status_report())\"")
    print()
    print("   # Test Cursor integration")
    print("   python -c \"from llmstruct.cursor_integration import create_cursor_integration; ci = create_cursor_integration('.'); print(ci.get_comprehensive_cursor_response('system status'))\"")

def main():
    """Main startup routine."""
    print_header()
    
    # Track overall success
    all_checks_passed = True
    
    # Run startup checks
    if not check_environment():
        all_checks_passed = False
    
    if not run_system_health_check():
        all_checks_passed = False
    
    if not get_optimization_suggestions():
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
    else:
        print("⚠️  Development environment has issues")
        print("🔧 Please address the warnings above")
    
    show_useful_commands()
    
    print("\n🚀 Happy coding with AI-enhanced development!")
    print("=" * 50)

if __name__ == "__main__":
    main() 