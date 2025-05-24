#!/usr/bin/env python3
"""Test script for audit functionality."""

import json
from pathlib import Path

def test_audit_status():
    """Test audit status directly."""
    root_dir = "/home/kpblc/projects/github/llmstruct"
    
    tasks_file = Path(root_dir) / "data" / "tasks.json"
    ideas_file = Path(root_dir) / "data" / "ideas.json"
    
    print(f"Tasks file exists: {tasks_file.exists()}")
    print(f"Ideas file exists: {ideas_file.exists()}")
    
    if not tasks_file.exists() or not ideas_file.exists():
        print("❌ Core data files not found")
        return
        
    with open(tasks_file, 'r') as f:
        tasks_data = json.load(f)
    with open(ideas_file, 'r') as f:
        ideas_data = json.load(f)
        
    print(f"Tasks data keys: {list(tasks_data.keys())}")
    print(f"Ideas data keys: {list(ideas_data.keys())}")
    
    if "tasks" in tasks_data:
        print(f"Total tasks: {len(tasks_data['tasks'])}")
        task_placeholders = [t for t in tasks_data["tasks"] if "Placeholder: Missing task details" in t.get("description", "")]
        print(f"Task placeholders found: {len(task_placeholders)}")
        
    if "ideas" in ideas_data:
        print(f"Total ideas: {len(ideas_data['ideas'])}")
        idea_placeholders = [i for i in ideas_data["ideas"] if "Placeholder: Missing idea details" in i.get("description", "")]
        print(f"Idea placeholders found: {len(idea_placeholders)}")
        
    print("📊 Current placeholder status:")
    print(f"   Tasks: {len(task_placeholders)} placeholders of {len(tasks_data['tasks'])} total")
    print(f"   Ideas: {len(idea_placeholders)} placeholders of {len(ideas_data['ideas'])} total")
    
    if task_placeholders:
        task_ids = [t["id"] for t in task_placeholders[:5]]
        print(f"   Example task IDs: {', '.join(task_ids)}{'...' if len(task_placeholders) > 5 else ''}")
        
    if idea_placeholders:
        idea_ids = [i["id"] for i in idea_placeholders[:5]]
        print(f"   Example idea IDs: {', '.join(idea_ids)}{'...' if len(idea_placeholders) > 5 else ''}")

if __name__ == "__main__":
    test_audit_status()
