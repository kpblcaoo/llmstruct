#!/usr/bin/env python3
"""
Export script for GitHub Projects integration
Converts official tasks.json and ideas.json to GitHub Project cards
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path to import gh_view module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from llmstruct.gh_view import GitHubProjectsExporter


class GitHubProjectsExportScript(GitHubProjectsExporter):
    """Extended exporter with command-line interface and GitHub CLI integration"""
    
    def __init__(self, config_path: str = None, dry_run: bool = True):
        super().__init__(config_path)
        self.dry_run = dry_run
        self.exported_count = {"tasks": 0, "ideas": 0}
        
    def check_github_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated"""
        success, output = self._run_gh_command(['auth', 'status'])
        if not success:
            print(f"❌ GitHub CLI issue: {output}")
            return False
        
        print("✅ GitHub CLI authenticated")
        return True
    
    def list_projects(self, owner: str = None, repo: str = None) -> List[Dict[str, Any]]:
        """List available GitHub Projects (via gh-projects extension)"""
        if repo and owner:
            cmd = ['projects', 'list', '--owner', owner, '--repo', repo, '--format', 'json']
        else:
            cmd = ['projects', 'list', '--format', 'json']
        
        success, output = self._run_gh_command(cmd)
        if not success:
            print(f"❌ Failed to list projects: {output}")
            return []
        
        try:
            projects = json.loads(output)
            return projects if isinstance(projects, list) else []
        except json.JSONDecodeError:
            print("❌ Failed to parse projects list")
            return []
    
    def create_project_item(self, project_number: int, title: str, body: str, 
                           owner: str = None, repo: str = None) -> Optional[str]:
        """Create a new item in GitHub Project (via gh-projects extension)
        TODO: заменить на GraphQL API или собственную реализацию в будущем
        """
        # Если owner/org не указан — используем --user "@me"
        if owner:
            cmd = ['projects', 'item-create', str(project_number),
                   '--user', owner,
                   '--title', title, '--body', body]
        else:
            cmd = ['projects', 'item-create', str(project_number),
                   '--user', '@me',
                   '--title', title, '--body', body]
        
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would create item: {title}")
            return "dry-run-id"
        
        success, output = self._run_gh_command(cmd)
        if not success:
            print(f"❌ Failed to create item '{title}': {output}")
            return None
        
        # Extract item ID from output (GitHub CLI returns item URL)
        return output.strip()
    
    def export_tasks_to_project(self, tasks: List[Dict[str, Any]], 
                               project_number: int, owner: str = None, 
                               repo: str = None) -> int:
        """Export tasks to GitHub Project"""
        exported = 0
        
        print(f"\n📋 Exporting {len(tasks)} tasks to project #{project_number}...")
        
        for task in tasks:
            task_id = task.get('id', 'unknown')
            
            # Skip if already exported
            if task_id in self.mapping.get('tasks', {}):
                print(f"⏭️  Skipping {task_id} (already exported)")
                continue
            
            # Format for GitHub
            formatted = self.format_task_for_github(task)
            
            # Create item
            item_id = self.create_project_item(
                project_number, 
                formatted['title'], 
                formatted['body'],
                owner, 
                repo
            )
            
            if item_id:
                # Save mapping
                if 'tasks' not in self.mapping:
                    self.mapping['tasks'] = {}
                self.mapping['tasks'][task_id] = item_id
                exported += 1
                print(f"✅ Exported {task_id}: {formatted['title'][:50]}...")
            else:
                print(f"❌ Failed to export {task_id}")
        
        self.exported_count['tasks'] = exported
        return exported
    
    def export_ideas_to_project(self, ideas: List[Dict[str, Any]], 
                               project_number: int, owner: str = None, 
                               repo: str = None) -> int:
        """Export ideas to GitHub Project"""
        exported = 0
        
        print(f"\n💡 Exporting {len(ideas)} ideas to project #{project_number}...")
        
        for idea in ideas:
            idea_id = idea.get('id', 'unknown')
            
            # Skip if already exported
            if idea_id in self.mapping.get('ideas', {}):
                print(f"⏭️  Skipping {idea_id} (already exported)")
                continue
            
            # Format for GitHub
            formatted = self.format_idea_for_github(idea)
            
            # Create item
            item_id = self.create_project_item(
                project_number, 
                formatted['title'], 
                formatted['body'],
                owner, 
                repo
            )
            
            if item_id:
                # Save mapping
                if 'ideas' not in self.mapping:
                    self.mapping['ideas'] = {}
                self.mapping['ideas'][idea_id] = item_id
                exported += 1
                print(f"✅ Exported {idea_id}: {formatted['title'][:50]}...")
            else:
                print(f"❌ Failed to export {idea_id}")
        
        self.exported_count['ideas'] = exported
        return exported
    
    def filter_data(self, data: List[Dict[str, Any]], 
                   status_filter: List[str] = None,
                   priority_filter: List[str] = None) -> List[Dict[str, Any]]:
        """Filter data by status and priority"""
        filtered = data
        
        if status_filter:
            filtered = [item for item in filtered 
                       if item.get('status') in status_filter]
        
        if priority_filter:
            filtered = [item for item in filtered 
                       if item.get('priority') in priority_filter]
        
        return filtered


def main():
    parser = argparse.ArgumentParser(description='Export llmstruct data to GitHub Projects')
    parser.add_argument('project_number', type=int, help='GitHub Project number')
    parser.add_argument('--owner', help='Repository owner (optional)')
    parser.add_argument('--repo', help='Repository name (optional)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be exported without actually doing it')
    parser.add_argument('--execute', action='store_true', 
                        help='Actually perform the export (overrides --dry-run)')
    parser.add_argument('--tasks-only', action='store_true', 
                        help='Export only tasks')
    parser.add_argument('--ideas-only', action='store_true', 
                        help='Export only ideas')
    parser.add_argument('--status', nargs='+', 
                        help='Filter by status (e.g., proposed, in_progress)')
    parser.add_argument('--priority', nargs='+', 
                        help='Filter by priority (e.g., high, medium, low)')
    
    args = parser.parse_args()
    
    # Determine dry run mode
    dry_run = args.dry_run and not args.execute
    
    print("🚀 GitHub Projects Export Script")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Project: #{args.project_number}")
    if args.owner and args.repo:
        print(f"Repository: {args.owner}/{args.repo}")
    print()
    
    # Initialize exporter
    exporter = GitHubProjectsExportScript(dry_run=dry_run)
    
    # Check GitHub CLI
    if not dry_run and not exporter.check_github_cli():
        sys.exit(1)
    
    # Load official data
    tasks, ideas = exporter.load_official_data()
    
    if not tasks and not ideas:
        print("❌ No data found to export")
        sys.exit(1)
    
    # Apply filters
    if args.status:
        tasks = exporter.filter_data(tasks, status_filter=args.status)
        ideas = exporter.filter_data(ideas, status_filter=args.status)
        print(f"🔍 Filtered by status: {', '.join(args.status)}")
    
    if args.priority:
        tasks = exporter.filter_data(tasks, priority_filter=args.priority)
        ideas = exporter.filter_data(ideas, priority_filter=args.priority)
        print(f"🔍 Filtered by priority: {', '.join(args.priority)}")
    
    # Export data
    total_exported = 0
    
    if not args.ideas_only and tasks:
        exported_tasks = exporter.export_tasks_to_project(
            tasks, args.project_number, args.owner, args.repo
        )
        total_exported += exported_tasks
    
    if not args.tasks_only and ideas:
        exported_ideas = exporter.export_ideas_to_project(
            ideas, args.project_number, args.owner, args.repo
        )
        total_exported += exported_ideas
    
    # Save mapping
    if not dry_run and total_exported > 0:
        exporter._save_mapping()
        print(f"\n💾 Saved mapping to {exporter.mapping_file}")
    
    # Summary
    print("\n📊 Export Summary:")
    print(f"   • Tasks exported: {exporter.exported_count['tasks']}")
    print(f"   • Ideas exported: {exporter.exported_count['ideas']}")
    print(f"   • Total exported: {total_exported}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. Use --execute to perform actual export.")


if __name__ == "__main__":
    main()
