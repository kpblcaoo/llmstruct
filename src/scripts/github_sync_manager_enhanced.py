#!/usr/bin/env python3
"""
Enhanced GitHub Sync Manager - Объединяет лучшие элементы из full_project_rollout
Интегрирует: processing results + GitHub API + token management + CLI fallback
"""

import json
import os
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

# Цветной вывод (из full_project_rollout.sh)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")

def print_step(step, total, msg):
    print(f"{Colors.BLUE}[{step}/{total}]{Colors.NC} {msg}")

class GitHubTokenManager:
    """Управление GitHub токенами (из setup_github_token.sh)"""
    
    def __init__(self):
        self.load_env_file()
        
    def load_env_file(self):
        """Загрузить переменные из .env файла"""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
    
    def test_github_token(self, token: str) -> bool:
        """Проверка работоспособности токена"""
        if not token:
            return False
            
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            return response.status_code == 200 and 'login' in response.json()
        except:
            return False
    
    def check_gh_cli(self) -> bool:
        """Проверка доступности GitHub CLI"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def get_token_from_gh_cli(self) -> Optional[str]:
        """Получение токена из GitHub CLI"""
        try:
            result = subprocess.run(['gh', 'auth', 'token'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_github_token(self) -> tuple[Optional[str], str]:
        """Получить GitHub токен с multiple fallbacks
        
        Returns:
            (token, method) где method = 'env' | 'cli' | 'none'
        """
        # 1. Проверка environment variable
        token = os.getenv('GITHUB_TOKEN')
        if token and self.test_github_token(token):
            return token, 'env'
            
        # 2. Попытка получить из GitHub CLI
        if self.check_gh_cli():
            cli_token = self.get_token_from_gh_cli()
            if cli_token and self.test_github_token(cli_token):
                return cli_token, 'cli'
                
        # 3. Использование GitHub CLI напрямую
        if self.check_gh_cli():
            print_warning("Using GitHub CLI authentication directly")
            return None, 'cli'
            
        return None, 'none'

class EnhancedGitHubSyncManager:
    """Улучшенный GitHub Sync Manager с интеграцией всех лучших практик"""
    
    def __init__(self, repo_owner: str = None, repo_name: str = None, dry_run: bool = True):
        self.dry_run = dry_run
        
        # Инициализация токен менеджера
        self.token_manager = GitHubTokenManager()
        
        # Автоопределение repo из git remote
        if not repo_owner or not repo_name:
            repo_owner, repo_name = self.detect_repo_from_git()
            
        self.repo_owner = repo_owner or "kpblc"
        self.repo_name = repo_name or "llmstruct"
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.results_path = self.base_path / "processing_results"
        self.sync_log_path = self.base_path / "github_sync_log.json"
        
        # GitHub API setup
        self.api_base = "https://api.github.com"
        self.repo_api = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}"
        
        # Token setup
        self.token, self.auth_method = self.token_manager.get_github_token()
        
        # Headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "llmstruct-enhanced-sync-manager"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            
        # Rate limiting
        self.request_delay = 1.0
        
        # Load sync log
        self.sync_log = self.load_sync_log()
        
        print_info(f"Repository: {self.repo_owner}/{self.repo_name}")
        print_info(f"Authentication: {self.auth_method}")
        print_info(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
    
    def detect_repo_from_git(self) -> tuple[str, str]:
        """Автоопределение owner/repo из git remote"""
        try:
            result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                url = result.stdout.strip()
                print_info(f"Git remote URL: {url}")
                
                # Parse GitHub URL (both HTTPS and SSH formats)
                if 'github.com' in url:
                    # Remove .git suffix if present
                    if url.endswith('.git'):
                        url = url[:-4]
                    
                    # Handle SSH format: git@github.com:owner/repo
                    if url.startswith('git@github.com:'):
                        path = url.replace('git@github.com:', '')
                        parts = path.split('/')
                        if len(parts) == 2:
                            return parts[0], parts[1]
                    
                    # Handle HTTPS format: https://github.com/owner/repo
                    elif 'github.com/' in url:
                        path = url.split('github.com/')[-1]
                        parts = path.split('/')
                        if len(parts) >= 2:
                            return parts[0], parts[1]
                            
        except Exception as e:
            print_warning(f"Could not detect repo from git: {e}")
            
        return None, None
    
    def load_sync_log(self) -> Dict:
        """Load previous sync results"""
        if self.sync_log_path.exists():
            with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_sync": None,
            "synced_items": {},
            "failed_items": [],
            "github_rate_limit": {},
            "sync_sessions": []
        }
    
    def save_sync_log(self):
        """Save sync log"""
        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.sync_log, f, indent=2, ensure_ascii=False)
    
    def api_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Enhanced API request with CLI fallback"""
        time.sleep(self.request_delay)
        
        # Try API first if we have token
        if self.auth_method in ['env', 'cli'] and self.token:
            return self._api_request_direct(method, endpoint, data)
        
        # Fallback to gh CLI
        if self.auth_method == 'cli':
            return self._api_request_via_cli(method, endpoint, data)
            
        print_error("No valid GitHub authentication available")
        return None
    
    def _api_request_direct(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Direct API request"""
        if endpoint == "user":
            url = f"{self.api_base}/user"
        else:
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
                
            # Rate limit tracking
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                if remaining < 10:
                    print_warning(f"GitHub API rate limit low: {remaining} requests remaining")
                    
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print_error(f"GitHub API error: {e}")
            return None
    
    def _api_request_via_cli(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """API request via GitHub CLI"""
        if method.upper() == 'GET':
            if endpoint == "user":
                cmd = ['gh', 'api', 'user']
            else:
                cmd = ['gh', 'api', f"repos/{self.repo_owner}/{self.repo_name}{endpoint}"]
        elif method.upper() == 'POST' and data:
            cmd = ['gh', 'api', '-X', 'POST', f"repos/{self.repo_owner}/{self.repo_name}{endpoint}"]
            # Add data as JSON
            cmd.extend(['--input', '-'])
        else:
            print_warning(f"CLI method {method} not implemented for endpoint {endpoint}")
            return None
            
        try:
            if data:
                result = subprocess.run(cmd, input=json.dumps(data), 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            else:
                print_error(f"GitHub CLI error: {result.stderr}")
                return None
                
        except Exception as e:
            print_error(f"CLI request error: {e}")
            return None
    
    def create_github_issue_enhanced(self, item: Dict) -> Optional[Dict]:
        """Enhanced issue creation (из create_github_issues.py)"""
        title = item.get('title', 'Untitled')
        description = item.get('description', '')
        
        # Enhanced body template
        body = f"""{description}

---

## 🤖 Auto-generated from llmstruct processing

**Processing Metadata:**
- Category: `{item.get('processing_metadata', {}).get('category_assigned', 'unknown')}`
- Confidence: {item.get('processing_metadata', {}).get('confidence_score', 0)}%
- Team implementable: {item.get('processing_metadata', {}).get('team_implementable', 'unknown')}
- GitHub ready: {item.get('processing_metadata', {}).get('github_ready', 'unknown')}

## ✅ Acceptance Criteria

{self._format_acceptance_criteria(item)}

## 🏗️ Implementation Notes

{self._format_implementation_notes(item)}

## 🧪 Testing Requirements

- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases covered

---

**Definition of Done**: All acceptance criteria ✅, tests pass ✅, code reviewed ✅, deployed ✅
"""
        
        # Enhanced labels
        labels = ["llmstruct-auto"]
        processing_meta = item.get('processing_metadata', {})
        
        if processing_meta.get('team_implementable'):
            labels.append("team-autonomous")
        if processing_meta.get('github_ready'):
            labels.append("ready-to-implement")
        if processing_meta.get('t_pot_related'):
            labels.append("t-pot")
        if processing_meta.get('confidence_score', 0) >= 90:
            labels.append("high-confidence")
            
        issue_data = {
            "title": title,
            "body": body,
            "labels": labels
        }
        
        if self.dry_run:
            print_info(f"[DRY-RUN] Would create issue: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            result = self.api_request('POST', "/issues", issue_data)
            if result:
                print_success(f"Created issue #{result['number']}: {title}")
            return result
    
    def _format_acceptance_criteria(self, item: Dict) -> str:
        """Format acceptance criteria from item metadata"""
        criteria = []
        
        # Add criteria based on item metadata
        if item.get('processing_metadata', {}).get('team_implementable'):
            criteria.append("Implementation can be completed by team without architecture review")
            
        if item.get('processing_metadata', {}).get('t_pot_related'):
            criteria.append("T-Pot integration tested and working")
            
        # Add default criteria
        criteria.extend([
            "Feature implemented according to description",
            "All tests passing",
            "Code review completed",
            "Documentation updated"
        ])
        
        return "\n".join([f"- [ ] {criterion}" for criterion in criteria])
    
    def _format_implementation_notes(self, item: Dict) -> str:
        """Format implementation notes"""
        notes = []
        
        processing_meta = item.get('processing_metadata', {})
        
        if processing_meta.get('requires_architecture_review'):
            notes.append("⚠️ **Architecture Review Required** - Do not start without design approval")
            
        if processing_meta.get('epic_candidate'):
            notes.append("📈 **Epic Candidate** - Consider breaking into smaller tasks")
            
        if processing_meta.get('t_pot_related'):
            notes.append("🍯 **T-Pot Related** - Coordinate with T-Pot deployment timeline")
            
        return "\n".join(notes) if notes else "Standard implementation - follow existing patterns"
    
    def validate_before_sync(self) -> bool:
        """Enhanced validation"""
        print_step(1, 6, "Validating GitHub access...")
        
        # Test authentication
        user_info = self.api_request('GET', "user")
        if not user_info:
            print_error("Cannot access GitHub API")
            return False
            
        print_success(f"GitHub access OK (user: {user_info.get('login', 'unknown')})")
        
        # Check repository access
        repo_info = self.api_request('GET', "")
        if not repo_info:
            print_error(f"Cannot access repository: {self.repo_owner}/{self.repo_name}")
            return False
            
        print_success(f"Repository access OK: {repo_info.get('full_name')}")
        
        # Check processing results
        print_step(2, 6, "Validating processing results...")
        required_files = [
            'github_issues_2025-05-29.json',
            'github_epics_2025-05-29.json', 
            'github_discussions_2025-05-29.json'
        ]
        
        for filename in required_files:
            file_path = self.results_path / filename
            if not file_path.exists():
                print_error(f"Required file not found: {filename}")
                return False
                
        print_success("All processing result files found")
        return True
    
    def run_enhanced_sync(self, categories: List[str] = None) -> Dict:
        """Enhanced sync with full project rollout integration"""
        print_info("🚀 Enhanced GitHub Sync Manager - Starting")
        print("=" * 50)
        
        # Validation
        if not self.validate_before_sync():
            return {"success": False, "error": "Validation failed"}
        
        # Default categories
        if not categories:
            categories = ['github_issues', 'github_epics', 'github_discussions']
            
        print_step(3, 6, "Processing categories...")
        
        # Sync each category
        results = {}
        total_synced = 0
        total_skipped = 0
        total_failed = 0
        
        for i, category in enumerate(categories, 1):
            print_step(3 + i, 6, f"Syncing {category}...")
            result = self.sync_category_enhanced(category)
            results[category] = result
            
            total_synced += result.get('synced', 0)
            total_skipped += result.get('skipped', 0)
            total_failed += result.get('failed', 0)
        
        # Save sync log
        self.sync_log['last_sync'] = datetime.now().isoformat()
        self.sync_log['sync_sessions'].append({
            "timestamp": datetime.now().isoformat(),
            "categories": categories,
            "results": results
        })
        self.save_sync_log()
        
        print_step(6, 6, "Sync complete!")
        print()
        print_success(f"Synced: {total_synced}, Skipped: {total_skipped}, Failed: {total_failed}")
        
        if total_synced > 0:
            print()
            print_info("🚀 NEXT STEPS:")
            print(f"   1. Check GitHub issues: https://github.com/{self.repo_owner}/{self.repo_name}/issues")
            print("   2. Review created items and assign to team")
            print("   3. Start development workflow")
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "synced": total_synced,
                "skipped": total_skipped,
                "failed": total_failed
            }
        }
    
    def sync_category_enhanced(self, category: str) -> Dict:
        """Enhanced category sync"""
        filename = f"{category}_2025-05-29.json"
        file_path = self.results_path / filename
        
        if not file_path.exists():
            print_error(f"File not found: {filename}")
            return {"success": False, "error": "File not found"}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        items = data.get('items', [])
        if not items:
            print_info(f"No items to sync in {category}")
            return {"success": True, "synced": 0, "skipped": 0}
        
        # Sync items
        synced_count = 0
        skipped_count = 0
        failed_count = 0
        
        for item in items:
            # Check if already synced (idempotency)
            if self.item_already_synced(item, category):
                print_info(f"Already synced: {item.get('title', 'Untitled')}")
                skipped_count += 1
                continue
                
            # Create GitHub item
            if category == 'github_issues':
                result = self.create_github_issue_enhanced(item)
            elif category == 'github_epics':
                result = self.create_github_epic_enhanced(item)
            elif category == 'github_discussions':
                result = self.create_github_discussion_enhanced(item)
            else:
                print_warning(f"Unknown category: {category}")
                continue
                
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
    
    def item_already_synced(self, item: Dict, category: str) -> bool:
        """Check if item was already synced"""
        item_id = item.get('id') or item.get('title', '')
        sync_key = f"{category}:{item_id}"
        return sync_key in self.sync_log.get('synced_items', {})
    
    def create_github_epic_enhanced(self, item: Dict) -> Optional[Dict]:
        """Enhanced epic creation"""
        title = f"[EPIC] {item.get('title', 'Untitled')}"
        
        body = f"""{item.get('description', '')}

---

## 🎯 EPIC OVERVIEW

This is a major feature/milestone requiring multiple related issues.

**Processing Metadata:**
- Epic Group: {item.get('processing_metadata', {}).get('epic_group', 'unknown')}
- Requires Architecture Review: {item.get('processing_metadata', {}).get('requires_architecture_review', 'unknown')}

## 📋 RELATED ISSUES

This epic will be broken down into multiple issues. Track progress here.

## ✅ EPIC COMPLETION CRITERIA

- [ ] All related issues completed
- [ ] Integration testing passed
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

**🤖 Auto-generated Epic from llmstruct processing**
"""
        
        epic_data = {
            "title": title,
            "body": body,
            "labels": ["llmstruct-auto", "epic", "major-feature"]
        }
        
        if self.dry_run:
            print_info(f"[DRY-RUN] Would create epic: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            result = self.api_request('POST', "/issues", epic_data)
            if result:
                print_success(f"Created epic #{result['number']}: {title}")
            return result
    
    def create_github_discussion_enhanced(self, item: Dict) -> Optional[Dict]:
        """Enhanced discussion creation (placeholder - requires GraphQL)"""
        title = item.get('title', 'Untitled Discussion')
        
        if self.dry_run:
            print_info(f"[DRY-RUN] Would create discussion: {title}")
            return {"number": 999, "url": "dry-run-url", "title": title}
        else:
            print_warning(f"Discussions require GraphQL API implementation: {title}")
            return None

def main():
    """Enhanced CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced GitHub Sync Manager")
    parser.add_argument('--live', action='store_true', help='Run in live mode (default: dry-run)')
    parser.add_argument('--categories', nargs='+', 
                       choices=['github_issues', 'github_epics', 'github_discussions'],
                       help='Categories to sync (default: all)')
    parser.add_argument('--repo', help='GitHub repository (owner/name, auto-detected if not provided)')
    
    args = parser.parse_args()
    
    # Parse repo if provided
    repo_owner, repo_name = None, None
    if args.repo:
        repo_parts = args.repo.split('/')
        if len(repo_parts) != 2:
            print_error("Invalid repo format. Use: owner/name")
            return
        repo_owner, repo_name = repo_parts
    
    # Create enhanced sync manager
    manager = EnhancedGitHubSyncManager(
        repo_owner=repo_owner,
        repo_name=repo_name,
        dry_run=not args.live
    )
    
    # Run enhanced sync
    result = manager.run_enhanced_sync(args.categories)
    
    if result['success']:
        print_success("🎯 Enhanced sync completed successfully!")
    else:
        print_error(f"Sync failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 