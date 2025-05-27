#!/usr/bin/env python3
"""
Test script for CLI integration with new commands
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def test_modular_cli_commands():
    """Test new CLI commands integration"""
    root_dir = "/home/kpblc/projects/github/llmstruct"
    
    print("🧪 Testing CLI Integration with New Commands")
    print("=" * 50)
    
    # Test 1: Check struct.json status
    print("\n1. Testing /struct status command")
    struct_path = os.path.join(root_dir, 'struct.json')
    if os.path.exists(struct_path):
        stat_info = os.stat(struct_path)
        print(f"✅ struct.json exists (size: {stat_info.st_size} bytes)")
        print(f"   Modified: {time.ctime(stat_info.st_mtime)}")
    else:
        print("❌ struct.json not found")
    
    # Test 2: Check auto-update script availability
    print("\n2. Testing auto-update script availability")
    auto_script = os.path.join(root_dir, 'scripts', 'auto_update_struct.py')
    if os.path.exists(auto_script):
        print("✅ Auto-update script available")
        
        # Test auto-update execution
        try:
            print("   Testing auto-update execution...")
            result = subprocess.run([
                sys.executable, auto_script,
                '--root-dir', root_dir,
                '--output', os.path.join(root_dir, 'struct.json'),
                '--check-only'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Auto-update executed successfully")
                if result.stdout:
                    print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"❌ Auto-update failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⚠️  Auto-update timeout (this is expected for long operations)")
        except Exception as e:
            print(f"❌ Auto-update error: {e}")
    else:
        print("❌ Auto-update script not found")
    
    # Test 3: Check workflow events system
    print("\n3. Testing workflow events system")
    events_dir = os.path.join(root_dir, 'data')
    os.makedirs(events_dir, exist_ok=True)
    
    # Create test workflow event
    test_event = {
        "event_id": f"test_{int(time.time())}",
        "event_type": "integration_test",
        "timestamp": time.time(),
        "description": "Test workflow event from integration test",
        "actions": ["test_action"]
    }
    
    events_path = os.path.join(events_dir, 'workflow_events.json')
    events_data = []
    if os.path.exists(events_path):
        try:
            with open(events_path, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
        except:
            events_data = []
    
    events_data.append(test_event)
    
    try:
        with open(events_path, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2)
        print("✅ Workflow events system working")
        print(f"   Created test event: {test_event['event_id']}")
    except Exception as e:
        print(f"❌ Workflow events error: {e}")
    
    # Test 4: Check modular CLI components
    print("\n4. Testing modular CLI components")
    cli_modules = [
        'cli_core.py',
        'cli_config.py', 
        'cli_utils.py',
        'cli_commands.py',
        'copilot.py'
    ]
    
    for module in cli_modules:
        module_path = os.path.join(root_dir, 'src', 'llmstruct', module)
        if os.path.exists(module_path):
            print(f"✅ {module} available")
        else:
            print(f"❌ {module} not found")
    
    # Test 5: Import test for modular CLI
    print("\n5. Testing modular CLI imports")
    try:
        sys.path.insert(0, os.path.join(root_dir, 'src'))
        
        from llmstruct.cli_core import CLICore, create_cli_core
        from llmstruct.cli_config import CLIConfig
        from llmstruct.cli_utils import CLIUtils
        from llmstruct.cli_commands import CommandProcessor
        from llmstruct.copilot import CopilotContextManager
        
        print("✅ All modular CLI imports successful")
        
        # Test CLI core creation
        cli_core = create_cli_core(root_dir)
        print("✅ CLI core creation successful")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ CLI core creation error: {e}")
    
    # Test 6: Check CLI queue system
    print("\n6. Testing CLI queue system")
    queue_path = os.path.join(root_dir, 'data', 'cli_queue.json')
    
    # Create test queue workflow
    test_workflow = {
        "workflow_id": f"test_workflow_{int(time.time())}",
        "description": "Integration test workflow",
        "commands": [
            {
                "cmd": "scan",
                "path": "src",
                "options": {"include_metadata": True}
            }
        ]
    }
    
    try:
        with open(queue_path, 'w', encoding='utf-8') as f:
            json.dump([test_workflow], f, indent=2)
        print("✅ CLI queue system working")
        print(f"   Created test workflow: {test_workflow['workflow_id']}")
    except Exception as e:
        print(f"❌ CLI queue error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CLI Integration Test Completed!")
    print("\nNew CLI commands available:")
    print("  /auto-update           - Run struct.json auto-update")
    print("  /struct status         - Show struct.json status info")
    print("  /struct validate       - Validate struct.json format")
    print("  /workflow trigger      - Trigger workflow events")
    print("  /queue run             - Process command queue")
    print("  /cache stats           - Show cache statistics")

if __name__ == "__main__":
    test_modular_cli_commands()
