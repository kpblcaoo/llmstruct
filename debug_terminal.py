#!/usr/bin/env python3
"""
Debug Terminal Script - Fallback for when terminal output is not visible
Saves all output to files for manual inspection
"""

import subprocess
import sys
import os
import datetime
from pathlib import Path

def run_with_output_capture(command, description="Command"):
    """Run command and capture output to both console and file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"debug_output_{timestamp}.txt"
    
    print(f"🔍 Running: {description}")
    print(f"📝 Output will be saved to: {output_file}")
    
    try:
        # Run command and capture output
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        # Prepare output content
        output_content = f"""
=== DEBUG TERMINAL OUTPUT ===
Command: {command}
Description: {description}
Timestamp: {datetime.datetime.now().isoformat()}
Exit Code: {result.returncode}

=== STDOUT ===
{result.stdout}

=== STDERR ===
{result.stderr}

=== END ===
"""
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        # Print summary
        print(f"✅ Command completed with exit code: {result.returncode}")
        print(f"📄 Full output saved to: {output_file}")
        
        if result.stdout:
            print("📤 STDOUT Preview:")
            print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
        
        if result.stderr:
            print("⚠️ STDERR Preview:")
            print(result.stderr[:500] + ("..." if len(result.stderr) > 500 else ""))
        
        return result.returncode == 0, output_file
        
    except subprocess.TimeoutExpired:
        error_msg = f"❌ Command timed out after 60 seconds"
        print(error_msg)
        with open(output_file, 'w') as f:
            f.write(f"{error_msg}\nCommand: {command}\n")
        return False, output_file
        
    except Exception as e:
        error_msg = f"❌ Command failed: {e}"
        print(error_msg)
        with open(output_file, 'w') as f:
            f.write(f"{error_msg}\nCommand: {command}\n")
        return False, output_file

def main():
    """Run common diagnostic commands with output capture."""
    print("🚀 Debug Terminal - Fallback Output Capture")
    print("=" * 50)
    
    commands = [
        ("python start_development.py", "Start Development Script"),
        ("python -m llmstruct analyze-duplicates --format json", "Duplication Analysis"),
        ("python run_ai_diagnostics.py health", "AI Health Check"),
        ("python -c \"from llmstruct.workflow_orchestrator import WorkflowOrchestrator; wo = WorkflowOrchestrator('.'); print('WorkflowOrchestrator OK')\"", "WorkflowOrchestrator Test"),
    ]
    
    results = []
    
    for command, description in commands:
        print(f"\n{'='*20}")
        success, output_file = run_with_output_capture(command, description)
        results.append((description, success, output_file))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 SUMMARY:")
    for description, success, output_file in results:
        status = "✅" if success else "❌"
        print(f"  {status} {description}")
        print(f"     📄 {output_file}")
    
    print(f"\n💡 To view any output file:")
    print(f"   cat debug_output_*.txt")
    print(f"   # or")
    print(f"   ls -la debug_output_*.txt")

if __name__ == "__main__":
    main() 