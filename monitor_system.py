#!/usr/bin/env python3
"""
System Monitor - Continuous logging for debugging terminal issues
Runs in background and logs system status to files
"""

import time
import json
import datetime
import subprocess
import sys
import os
from pathlib import Path

def log_system_status():
    """Log current system status to file."""
    timestamp = datetime.datetime.now()
    log_file = f"system_monitor_{timestamp.strftime('%Y%m%d')}.log"
    
    status = {
        "timestamp": timestamp.isoformat(),
        "system_checks": {},
        "errors": []
    }
    
    # Check WorkflowOrchestrator
    try:
        sys.path.insert(0, 'src')
        from llmstruct.workflow_orchestrator import WorkflowOrchestrator
        wo = WorkflowOrchestrator(".", debug=False)
        context = wo.get_current_context()
        status["system_checks"]["workflow_orchestrator"] = "OK"
        status["context_summary"] = {
            "copilot_layers": len(context.get('copilot_status', {}).get('loaded_layers', [])),
            "ai_capabilities": len(context.get('system_capabilities', {}).get('capabilities', [])),
            "struct_analysis": "OK" if 'error' not in context.get('struct_analysis', {}) else "ERROR"
        }
    except Exception as e:
        status["system_checks"]["workflow_orchestrator"] = f"ERROR: {str(e)}"
        status["errors"].append(f"WorkflowOrchestrator: {str(e)}")
    
    # Check file existence
    required_files = [
        "struct.json", 
        "data/init_enhanced.json",
        "data/cursor/cursor_context_config.json"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            status["system_checks"][f"file_{file_path}"] = "EXISTS"
        else:
            status["system_checks"][f"file_{file_path}"] = "MISSING"
            status["errors"].append(f"Missing file: {file_path}")
    
    # Save to log
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(status, indent=2) + "\n" + "="*50 + "\n")
    
    return status

def main():
    """Run continuous monitoring."""
    print("🔍 System Monitor Started")
    print("📝 Logs will be saved to system_monitor_YYYYMMDD.log")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            status = log_system_status()
            
            # Print summary
            timestamp = status["timestamp"]
            errors = len(status["errors"])
            
            if errors == 0:
                print(f"✅ {timestamp}: All systems OK")
            else:
                print(f"⚠️  {timestamp}: {errors} errors detected")
                for error in status["errors"][:3]:
                    print(f"   - {error}")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once and exit
        status = log_system_status()
        print(json.dumps(status, indent=2))
    else:
        # Run continuously
        main() 