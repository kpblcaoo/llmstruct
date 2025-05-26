#!/usr/bin/env python3
import sys
import json
from pathlib import Path

print("🚀 Testing GitHub Projects Export")
print("=" * 40)

# Test loading data
data_dir = Path("/home/kpblc/projects/github/llmstruct/data")
tasks_file = data_dir / "tasks.json"
ideas_file = data_dir / "ideas.json"

print(f"Data directory: {data_dir}")
print(f"Tasks file exists: {tasks_file.exists()}")
print(f"Ideas file exists: {ideas_file.exists()}")

if tasks_file.exists():
    try:
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)
            tasks = tasks_data.get('tasks', [])
            print(f"✅ Loaded {len(tasks)} tasks")
            
            # Show first task
            if tasks:
                first_task = tasks[0]
                print(f"   First task: {first_task.get('id')} - {first_task.get('description', 'No description')[:50]}...")
    except Exception as e:
        print(f"❌ Error loading tasks: {e}")

if ideas_file.exists():
    try:
        with open(ideas_file, 'r') as f:
            ideas_data = json.load(f)
            ideas = ideas_data.get('ideas', [])
            print(f"✅ Loaded {len(ideas)} ideas")
            
            # Show first idea
            if ideas:
                first_idea = ideas[0]
                title = first_idea.get('title', first_idea.get('description', 'No title'))
                print(f"   First idea: {first_idea.get('id')} - {title[:50]}...")
    except Exception as e:
        print(f"❌ Error loading ideas: {e}")

print("\n✅ Test completed successfully")
