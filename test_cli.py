#!/usr/bin/env python3
"""Test script for the enhanced CLI functionality."""

import asyncio
import sys
import os
import subprocess
import time

async def test_cli_commands():
    """Test the CLI with various commands."""
    
    # Test with a simple Python script that pipes commands
    commands = [
        "/cache stats",
        "/queue status", 
        "/view data",
        "exit"
    ]
    
    # Create input for the CLI
    input_text = "\n".join(commands) + "\n"
    
    # Run the CLI with input
    process = subprocess.Popen(
        [sys.executable, "-m", "llmstruct", "interactive", ".", "--context", "data/init.json", "--use-cache"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/kpblc/projects/github/llmstruct"
    )
    
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=30)
        print("=== STDOUT ===")
        print(stdout)
        print("=== STDERR ===")
        print(stderr)
        print("=== Return Code ===")
        print(process.returncode)
    except subprocess.TimeoutExpired:
        process.kill()
        print("Process timed out")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_cli_commands())
