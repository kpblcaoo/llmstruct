#!/usr/bin/env python3
"""
GitHub Sync Manager - Идемпотентная синхронизация processing results с GitHub
Supports: Issues, Epics (Projects), Discussions
Safety: dry-run mode, logging, collision detection
"""

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

class GitHubSyncManager:
    def __init__(self, repo_owner: str = "kpblc", repo_name: str = "llmstruct", dry_run: bool = True):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.dry_run = dry_run
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.results_path = self.base_path / "processing_results"
        self.sync_log_path = self.base_path / "github_sync_log.json"
        
        # GitHub API
        self.api_base = "https://api.github.com"
        self.repo_api = f"{self.api_base}/repos/{repo_owner}/{repo_name}"
        
        # Auth (from environment or config)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "llmstruct-sync-manager"
        }
        
        # Add token if available
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        else:
            print("⚠️  No GITHUB_TOKEN found. Read-only mode.")
            
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        
        # Load sync log
        self.sync_log = self.load_sync_log()
        
    def load_sync_log(self) -> Dict:
        """Load previous sync results for idempotency"""
        if self.sync_log_path.exists():
            with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_sync": None,
            "synced_items": {},
            "failed_items": [],
            "github_rate_limit": {}
        }
    
    def save_sync_log(self):
        """Save sync log for future idempotency"""
        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.sync_log, f, indent=2, ensure_ascii=False)
    
    def api_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Safe GitHub API request with rate limiting"""
        time.sleep(self.request_delay)
        
        url = f"{self.repo_api}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            # Check rate limit
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                if remaining < 10:
                    print(f"⚠️  GitHub API rate limit low: {remaining} requests remaining")
                    
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API error: {e}")
            return None
    
    def get_existing_issues(self) -> List[Dict]:
        """Get existing GitHub issues for collision detection"""
        issues = []
        page = 1
        
        while True:
            result = self.api_request('GET', f"/issues?state=all&page={page}&per_page=100")
            if not result:
                break
                
            issues.extend(result)
            
            if len(result) < 100:  # Last page
                break
            page += 1
            
        return issues
    
    def get_existing_discussions(self) -> List[Dict]:
        """Get existing GitHub discussions"""
        # Note: Discussions API requires GraphQL, simplified for now
        # TODO: Implement GraphQL query for discussions
        return []
    
    def item_already_synced(self, item: Dict, category: str) -> bool:
        """Check if item was already synced (idempotency)"""
        item_id = item.get('id') or item.get('title', '')
        sync_key = f"{category}:{item_id}"
        
        return sync_key in self.sync_log.get('synced_items', {})
    
    def find_existing_by_title(self, title: str, existing_items: List[Dict]) -> Optional[Dict]:
        """Find existing GitHub item by title similarity"""
        title_lower = title.lower().strip()
        
        for item in existing_items:
            existing_title = item.get('title', '').lower().strip()
            
            # Exact match
            if title_lower == existing_title:
                return item
                
            # High similarity match (avoid duplicates)
            if title_lower in existing_title or existing_title in title_lower:
                if len(title_lower) > 10 and len(existing_title) > 10:  # Only for substantial titles
                    return item
                    
        return None
    
    def create_github_issue(self, item: Dict) -> Optional[Dict]:
        """Create GitHub issue from processed item"""
        title = item.get('title', 'Untitled')
        description = item.get('description', '')
        
        # Enhanced description with metadata
        body = f"{description}\n\n"
        body += "---\n"
        body += "**Auto-generated from llmstruct processing**\n"
        body += f"- Category: `{item.get('processing_metadata', {}).get('category_assigned', 'unknown')}`\n"
        body += f"- Confidence: {item.get('processing_metadata', {}).get('confidence_score', 0)}%\n"
        body += f"- Team implementable: {item.get('processing_metadata', {}).get('team_implementable', 'unknown')}\n"
        
        # Labels based on metadata
        labels = ["llmstruct-auto"]
        
        processing_meta = item.get('processing_metadata', {})
        if processing_meta.get('team_implementable'):
            labels.append("team-autonomous")
        if processing_meta.get('github_ready'):
            labels.append("ready-to-implement")
        if processing_meta.get('t_pot_related'):
            labels.append("t-pot")
            
        issue_data = {
            "title": title,
            "body": body,
            "labels": labels
        }
        
        if self.dry_run:
            print(f"🔄 [DRY-RUN] Would create issue: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            result = self.api_request('POST', "/issues", issue_data)
            if result:
                print(f"✅ Created issue #{result['number']}: {title}")
            return result
    
    def create_github_discussion(self, item: Dict) -> Optional[Dict]:
        """Create GitHub discussion from processed item"""
        # Simplified - would need GraphQL implementation
        title = item.get('title', 'Untitled Discussion')
        
        if self.dry_run:
            print(f"🔄 [DRY-RUN] Would create discussion: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            print(f"⚠️  Discussions require GraphQL API (TODO): {title}")
            return None
    
    def create_github_epic(self, item: Dict) -> Optional[Dict]:
        """Create GitHub epic (as Project or enhanced Issue)"""
        # GitHub doesn't have native "epics" - using Issues with special labels
        title = f"[EPIC] {item.get('title', 'Untitled')}"
        
        epic_data = {
            "title": title,
            "body": f"{item.get('description', '')}\n\n---\n**Epic Management**\nThis is a major feature/milestone requiring multiple related issues.",
            "labels": ["llmstruct-auto", "epic", "major-feature"]
        }
        
        if self.dry_run:
            print(f"🔄 [DRY-RUN] Would create epic: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            result = self.api_request('POST', "/issues", epic_data)
            if result:
                print(f"✅ Created epic #{result['number']}: {title}")
            return result
    
    def sync_category(self, category: str, filename: str) -> Dict:
        """Sync specific category with GitHub"""
        print(f"\n🔄 Syncing category: {category}")
        
        # Load category data
        file_path = self.results_path / filename
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            return {"success": False, "error": "File not found"}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        items = data.get('items', [])
        if not items:
            print(f"ℹ️  No items to sync in {category}")
            return {"success": True, "synced": 0, "skipped": 0}
            
        # Get existing GitHub items for collision detection
        if category == 'github_issues':
            existing_items = self.get_existing_issues()
        elif category == 'github_discussions':
            existing_items = self.get_existing_discussions()
        elif category == 'github_epics':
            existing_items = self.get_existing_issues()  # Epics are issues with labels
        else:
            existing_items = []
            
        # Sync items
        synced_count = 0
        skipped_count = 0
        failed_count = 0
        
        for item in items:
            # Check if already synced (idempotency)
            if self.item_already_synced(item, category):
                print(f"⏭️  Already synced: {item.get('title', 'Untitled')}")
                skipped_count += 1
                continue
                
            # Check for existing duplicates
            existing = self.find_existing_by_title(item.get('title', ''), existing_items)
            if existing:
                print(f"⚠️  Similar item exists: {existing.get('title')} (#{existing.get('number')})")
                skipped_count += 1
                continue
                
            # Create GitHub item
            result = None
            if category == 'github_issues':
                result = self.create_github_issue(item)
            elif category == 'github_epics':
                result = self.create_github_epic(item)
            elif category == 'github_discussions':
                result = self.create_github_discussion(item)
                
            if result:
                # Log successful sync
                item_id = item.get('id') or item.get('title', '')
                sync_key = f"{category}:{item_id}"
                self.sync_log['synced_items'][sync_key] = {
                    "github_url": result.get('url', ''),
                    "github_number": result.get('number'),
                    "synced_at": datetime.now().isoformat()
                }
                synced_count += 1
            else:
                failed_count += 1
                
        return {
            "success": True,
            "synced": synced_count,
            "skipped": skipped_count,
            "failed": failed_count
        }
    
    def validate_before_sync(self) -> bool:
        """Pre-sync validation checks"""
        print("🔍 Pre-sync validation...")
        
        # Check GitHub API access
        user_info = self.api_request('GET', "/../../user")
        if not user_info:
            print("❌ Cannot access GitHub API")
            return False
            
        print(f"✅ GitHub API access OK (user: {user_info.get('login', 'unknown')})")
        
        # Check rate limit
        rate_limit = self.api_request('GET', "/../../rate_limit")
        if rate_limit:
            core_limit = rate_limit.get('resources', {}).get('core', {})
            remaining = core_limit.get('remaining', 0)
            print(f"📊 GitHub API rate limit: {remaining} requests remaining")
            
            if remaining < 50:
                print("⚠️  Low rate limit - consider waiting")
                return False
                
        # Check repository access
        repo_info = self.api_request('GET', "")
        if not repo_info:
            print(f"❌ Cannot access repository: {self.repo_owner}/{self.repo_name}")
            return False
            
        print(f"✅ Repository access OK: {repo_info.get('full_name')}")
        return True
    
    def run_sync(self, categories: List[str] = None) -> Dict:
        """Main sync execution"""
        print("🚀 GitHub Sync Manager - Starting")
        print(f"📂 Repository: {self.repo_owner}/{self.repo_name}")
        print(f"🏃 Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        
        # Validation
        if not self.validate_before_sync():
            return {"success": False, "error": "Validation failed"}
            
        # Default categories
        if not categories:
            categories = ['github_issues', 'github_epics', 'github_discussions']
            
        # Category file mapping
        category_files = {
            'github_issues': 'github_issues_2025-05-29.json',
            'github_epics': 'github_epics_2025-05-29.json',
            'github_discussions': 'github_discussions_2025-05-29.json'
        }
        
        # Sync each category
        results = {}
        for category in categories:
            if category in category_files:
                results[category] = self.sync_category(category, category_files[category])
            else:
                print(f"⚠️  Unknown category: {category}")
                
        # Save sync log
        self.sync_log['last_sync'] = datetime.now().isoformat()
        self.save_sync_log()
        
        # Summary
        total_synced = sum(r.get('synced', 0) for r in results.values())
        total_skipped = sum(r.get('skipped', 0) for r in results.values())
        total_failed = sum(r.get('failed', 0) for r in results.values())
        
        print("\n✅ Sync complete!")
        print(f"📊 Synced: {total_synced}, Skipped: {total_skipped}, Failed: {total_failed}")
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "synced": total_synced,
                "skipped": total_skipped,
                "failed": total_failed
            }
        }

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Sync Manager")
    parser.add_argument('--live', action='store_true', help='Run in live mode (default: dry-run)')
    parser.add_argument('--categories', nargs='+', choices=['github_issues', 'github_epics', 'github_discussions'],
                        help='Categories to sync (default: all)')
    parser.add_argument('--repo', default='kpblc/llmstruct', help='GitHub repository (owner/name)')
    
    args = parser.parse_args()
    
    # Parse repo
    repo_parts = args.repo.split('/')
    if len(repo_parts) != 2:
        print("❌ Invalid repo format. Use: owner/name")
        return
        
    owner, name = repo_parts
    
    # Create sync manager
    manager = GitHubSyncManager(
        repo_owner=owner,
        repo_name=name,
        dry_run=not args.live
    )
    
    # Run sync
    result = manager.run_sync(args.categories)
    
    if result['success']:
        print("🎯 Sync completed successfully!")
    else:
        print(f"❌ Sync failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 