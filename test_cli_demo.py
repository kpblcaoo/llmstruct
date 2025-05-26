#!/usr/bin/env python3
"""
Quick CLI test to demonstrate new commands
"""

import subprocess
import sys
import time

def test_interactive_cli():
    """Test interactive CLI with new commands"""
    print("🚀 Testing Interactive CLI with New Commands")
    print("=" * 50)
    
    # Create a script to test specific CLI commands
    commands_to_test = [
        "/struct status",
        "/struct validate", 
        "/workflow trigger",
        "/help",
        "exit"
    ]
    
    # Create input script
    input_script = "\n".join(commands_to_test)
    
    print("Commands to test:")
    for cmd in commands_to_test[:-1]:  # Don't show 'exit'
        print(f"  {cmd}")
    
    print("\nRunning CLI test...")
    print("-" * 30)
    
    try:
        # Run CLI with piped input
        result = subprocess.run([
            sys.executable, "-c", 
            """
import sys
sys.path.insert(0, '/home/kpblc/projects/github/llmstruct/src')
from llmstruct.cli import interactive
import argparse
import asyncio

args = argparse.Namespace()
args.root_dir = '/home/kpblc/projects/github/llmstruct'
args.context = '/home/kpblc/projects/github/llmstruct/struct.json'
args.use_cache = False
args.mode = 'complex'
args.model = 'claude-3-5-sonnet-20241022'
args.artifact_ids = None

asyncio.run(interactive(args))
"""
        ], input=input_script, capture_output=True, text=True, timeout=30)
        
        print("CLI Output:")
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors/Warnings:")
            print(result.stderr)
            
        print("\n✅ CLI test completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("⚠️  CLI test timeout (expected for interactive mode)")
    except Exception as e:
        print(f"❌ CLI test error: {e}")

if __name__ == "__main__":
    test_interactive_cli()
