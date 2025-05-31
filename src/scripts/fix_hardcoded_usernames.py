#!/usr/bin/env python3
"""
Fix Hardcoded Usernames Script
Automatically detects and replaces hardcoded usernames with dynamic values from .env or git config.
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class UserInfoDetector:
    """Detect user information from various sources."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.user_info = self._detect_user_info()
    
    def _detect_user_info(self) -> Dict[str, str]:
        """Detect user info from .env, git config, or environment."""
        user_info = {}
        
        # 1. Start with git config as base
        git_info = self._load_from_git()
        if git_info:
            user_info.update(git_info)
            logger.info("Loaded user info from git config")
        
        # 2. Override with environment variables  
        env_vars = self._load_from_environment()
        if env_vars:
            # Only update if values are not empty
            for key, value in env_vars.items():
                if value:  # Only update if not empty
                    user_info[key] = value
            logger.info("Loaded user info from environment variables")
        
        # 3. Override with .env file (highest priority)
        env_info = self._load_from_env()
        if env_info:
            # Only update if values are not empty
            for key, value in env_info.items():
                if value:  # Only update if not empty
                    user_info[key] = value
            logger.info("Loaded user info from .env file")
        
        # 4. Fallback defaults for any missing values
        if not user_info.get('github_username'):
            user_info['github_username'] = 'USER'
        if not user_info.get('email'):
            user_info['email'] = 'user@example.com'
        if not user_info.get('name'):
            user_info['name'] = 'Project User'
        
        return user_info
    
    def _load_from_env(self) -> Dict[str, str]:
        """Load user info from .env file."""
        env_file = self.project_root / ".env"
        if not env_file.exists():
            return {}
        
        try:
            env_vars = {}
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
            
            return {
                'github_username': env_vars.get('GITHUB_USERNAME', ''),
                'email': env_vars.get('GITHUB_EMAIL', env_vars.get('EMAIL', '')),
                'name': env_vars.get('USER_NAME', env_vars.get('NAME', ''))
            }
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
            return {}
    
    def _load_from_git(self) -> Dict[str, str]:
        """Load user info from git config."""
        try:
            # Get git username
            result = subprocess.run(['git', 'config', 'user.name'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            git_name = result.stdout.strip() if result.returncode == 0 else ""
            
            # Get git email
            result = subprocess.run(['git', 'config', 'user.email'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            git_email = result.stdout.strip() if result.returncode == 0 else ""
            
            # Try to get GitHub username from remote
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            github_username = ""
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                # Extract username from GitHub URLs
                if 'github.com' in remote_url:
                    match = re.search(r'github\.com[:/]([^/]+)/', remote_url)
                    if match:
                        github_username = match.group(1)
            
            return {
                'name': git_name,
                'email': git_email,
                'github_username': github_username
            }
        except Exception as e:
            logger.error(f"Error reading git config: {e}")
            return {}
    
    def _load_from_environment(self) -> Dict[str, str]:
        """Load user info from environment variables."""
        return {
            'github_username': os.environ.get('GITHUB_USERNAME', ''),
            'email': os.environ.get('GITHUB_EMAIL', os.environ.get('EMAIL', '')),
            'name': os.environ.get('USER_NAME', os.environ.get('USER', ''))
        }
    
    def get_user_info(self) -> Dict[str, str]:
        """Get detected user information."""
        return self.user_info.copy()


class HardcodeFixer:
    """Fix hardcoded usernames in project files."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.detector = UserInfoDetector(project_root)
        self.user_info = self.detector.get_user_info()
        
        # Patterns to replace
        self.replacement_patterns = [
            ('kpblcaoo', self.user_info['github_username']),
            ('kpblcaoo@gmail.com', self.user_info['email']),
            ('@kpblcaoo', f"@{self.user_info['github_username']}")
        ]
    
    def scan_files(self) -> List[Tuple[Path, int]]:
        """Scan for files containing hardcoded usernames."""
        files_with_hardcode = []
        
        # File patterns to scan
        patterns = ['*.py', '*.json', '*.md', '*.sh', '*.toml', '*.yaml', '*.yml']
        
        for pattern in patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip certain directories
                if any(part in str(file_path) for part in ['.git', '__pycache__', '.pytest_cache']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        count = content.count('kpblcaoo')
                        if count > 0:
                            files_with_hardcode.append((file_path, count))
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        return files_with_hardcode
    
    def fix_file(self, file_path: Path, dry_run: bool = True) -> Dict[str, int]:
        """Fix hardcoded usernames in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements_made = {}
            
            # Apply replacements
            for old_value, new_value in self.replacement_patterns:
                count = content.count(old_value)
                if count > 0:
                    content = content.replace(old_value, new_value)
                    replacements_made[old_value] = count
            
            # Write back if not dry run and changes were made
            if not dry_run and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Fixed {file_path}")
            
            return replacements_made
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return {}
    
    def fix_all_files(self, dry_run: bool = True) -> Dict[str, Dict[str, int]]:
        """Fix hardcoded usernames in all project files."""
        files_with_hardcode = self.scan_files()
        results = {}
        
        logger.info(f"Found {len(files_with_hardcode)} files with hardcoded usernames")
        
        for file_path, count in files_with_hardcode:
            replacements = self.fix_file(file_path, dry_run)
            if replacements:
                results[str(file_path)] = replacements
        
        return results
    
    def generate_env_template(self) -> str:
        """Generate .env template with required variables."""
        template = """# User Configuration for llmstruct
# Copy this to .env and fill in your information

# GitHub Configuration
GITHUB_USERNAME=your_github_username
GITHUB_EMAIL=your_email@example.com

# User Information
USER_NAME=Your Full Name

# GitHub Token (for API access)
GITHUB_TOKEN=your_github_token_here
"""
        return template


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix hardcoded usernames in project")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be changed without making changes")
    parser.add_argument("--create-env-template", action="store_true",
                       help="Create .env.template file")
    parser.add_argument("--scan-only", action="store_true",
                       help="Only scan for files with hardcoded usernames")
    
    args = parser.parse_args()
    
    fixer = HardcodeFixer()
    
    if args.create_env_template:
        template_path = Path(".env.template")
        with open(template_path, 'w') as f:
            f.write(fixer.generate_env_template())
        logger.info(f"Created {template_path}")
        return
    
    if args.scan_only:
        files = fixer.scan_files()
        print(f"\nFound {len(files)} files with hardcoded usernames:")
        for file_path, count in files:
            print(f"  {file_path}: {count} occurrences")
        return
    
    # Show current user info
    user_info = fixer.user_info
    print("\nDetected User Information:")
    print(f"  GitHub Username: {user_info['github_username']}")
    print(f"  Email: {user_info['email']}")
    print(f"  Name: {user_info['name']}")
    
    if not user_info['github_username'] or user_info['github_username'] == 'USER':
        print("\n⚠️  WARNING: Could not detect GitHub username!")
        print("Please create .env file with GITHUB_USERNAME=your_username")
        print("Use --create-env-template to create a template")
        return
    
    # Fix files
    results = fixer.fix_all_files(dry_run=args.dry_run)
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN - Would fix {len(results)} files:")
    else:
        print(f"\n✅ Fixed {len(results)} files:")
    
    for file_path, replacements in results.items():
        print(f"  {file_path}:")
        for old_val, count in replacements.items():
            print(f"    {old_val} → {fixer.user_info['github_username']} ({count} times)")


if __name__ == "__main__":
    main() 