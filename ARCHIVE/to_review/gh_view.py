#!/usr/bin/env python3
"""
GitHub visualization/graph feature (gh-view-v1)
Export consolidated tasks/ideas from JSON files to GitHub Project cards
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import toml


class GitHubProjectsExporter:
    """Export tasks and ideas to GitHub Projects as cards"""
    
    def __init__(self, config_path: str = None):
        """Initialize exporter with configuration"""
        self.config_path = config_path or "/home/kpblc/projects/github/llmstruct/llmstruct.toml"
        self.config = self._load_config()
        self.data_dir = Path("/home/kpblc/projects/github/llmstruct/data")
        self.mapping_file = self.data_dir / "gh_mapping.json"
        self.mapping = self._load_mapping()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = toml.load(f)
                return config.get('gh_view', {})
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}
    
    def _load_mapping(self) -> Dict[str, str]:
        """Load existing ID mapping between local and GitHub"""
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"tasks": {}, "ideas": {}}
    
    def _save_mapping(self):
        """Save ID mapping to file"""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mapping, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save mapping: {e}")
    
    def _run_gh_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run GitHub CLI command and return success status and output"""
        try:
            result = subprocess.run(
                ['gh'] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
        except FileNotFoundError:
            return False, "GitHub CLI (gh) not found. Please install it first."
    
    def load_official_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Load tasks and ideas from official JSON files"""
        tasks_file = self.data_dir / "tasks.json"
        ideas_file = self.data_dir / "ideas.json"
        
        tasks = []
        ideas = []
        
        # Load tasks
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                    tasks = tasks_data.get('tasks', [])
                    print(f"✅ Loaded {len(tasks)} tasks from official data")
            except Exception as e:
                print(f"❌ Error loading tasks: {e}")
        
        # Load ideas
        if ideas_file.exists():
            try:
                with open(ideas_file, 'r') as f:
                    ideas_data = json.load(f)
                    ideas = ideas_data.get('ideas', [])
                    print(f"✅ Loaded {len(ideas)} ideas from official data")
            except Exception as e:
                print(f"❌ Error loading ideas: {e}")
        
        return tasks, ideas
    
    def format_task_for_github(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Format task data for GitHub Project card"""
        title = f"[{task['id']}] {task['description']}"
        
        # Create body with metadata
        body_parts = [
            f"**Task ID:** {task['id']}",
            f"**Status:** {task.get('status', 'unknown')}",
            f"**Priority:** {task.get('priority', 'medium')}",
            f"**Effort:** {task.get('estimated_effort', 'TBD')}",
            f"**Assignee:** {task.get('assignee', 'unassigned')}",
        ]
        
        if task.get('dependencies'):
            deps = ', '.join(task['dependencies'])
            body_parts.append(f"**Dependencies:** {deps}")
        
        if task.get('target_release'):
            body_parts.append(f"**Target Release:** {task['target_release']}")
        
        body = '\n'.join(body_parts)
        
        # Map status to GitHub Project status
        status_map = {
            'proposed': 'Todo',
            'in_progress': 'In Progress', 
            'completed': 'Done',
            'blocked': 'Blocked',
            'cancelled': 'Cancelled'
        }
        
        return {
            'title': title,
            'body': body,
            'status': status_map.get(task.get('status'), 'Todo'),
            'priority': task.get('priority', 'medium'),
            'labels': [f"task", f"priority-{task.get('priority', 'medium')}"]
        }
    
    def format_idea_for_github(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Format idea data for GitHub Project card"""
        title = f"[{idea['id']}] {idea.get('title', idea.get('description', 'Untitled Idea'))}"
        
        # Create body with metadata
        body_parts = [
            f"**Idea ID:** {idea['id']}",
            f"**Status:** {idea.get('status', 'proposed')}",
            f"**Priority:** {idea.get('priority', 'medium')}",
            f"**Category:** {idea.get('category', 'general')}",
        ]
        
        if idea.get('description') and idea.get('title'):
            body_parts.append(f"\n**Description:**\n{idea['description']}")
        
        if idea.get('implementation_notes'):
            body_parts.append(f"\n**Implementation Notes:**\n{idea['implementation_notes']}")
        
        body = '\n'.join(body_parts)
        
        # Map status to GitHub Project status
        status_map = {
            'proposed': 'Todo',
            'active': 'In Progress',
            'implemented': 'Done',
            'on_hold': 'Blocked',
            'cancelled': 'Cancelled'
        }
        
        return {
            'title': title,
            'body': body,
            'status': status_map.get(idea.get('status'), 'Todo'),
            'priority': idea.get('priority', 'medium'),
            'labels': [f"idea", f"category-{idea.get('category', 'general')}", f"priority-{idea.get('priority', 'medium')}"]
        }


def main():
    """Main entry point for GitHub Projects export"""
    exporter = GitHubProjectsExporter()
    
    print("🚀 GitHub Projects Exporter (gh-view-v1)")
    print("=" * 50)
    
    # Load official data
    tasks, ideas = exporter.load_official_data()
    
    if not tasks and not ideas:
        print("❌ No data found to export")
        sys.exit(1)
    
    print(f"\n📋 Ready to export:")
    print(f"   • {len(tasks)} tasks")
    print(f"   • {len(ideas)} ideas")
    
    # Show sample formatted data
    if tasks:
        print(f"\n📝 Sample task format:")
        sample_task = exporter.format_task_for_github(tasks[0])
        print(f"   Title: {sample_task['title']}")
        print(f"   Status: {sample_task['status']}")
        print(f"   Labels: {', '.join(sample_task['labels'])}")
    
    if ideas:
        print(f"\n💡 Sample idea format:")
        sample_idea = exporter.format_idea_for_github(ideas[0])
        print(f"   Title: {sample_idea['title']}")
        print(f"   Status: {sample_idea['status']}")
        print(f"   Labels: {', '.join(sample_idea['labels'])}")


if __name__ == "__main__":
    main()
