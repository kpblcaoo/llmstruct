#!/usr/bin/env python3
"""
GitHub Issues Creator for AI-Dogfooding Project
Автоматическое создание GitHub issues из наших эпиков и задач
"""

import json
import os
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Загрузка .env файла если существует
def load_env_file():
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
        print("✅ Loaded .env file")

# Загружаем .env файл первым делом
load_env_file()

class GitHubIssuesCreator:
    def __init__(self, repo_owner: str, repo_name: str, token: str = None, use_cli: bool = False):
        self.owner = repo_owner
        self.repo = repo_name
        self.token = token
        self.use_cli = use_cli
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            "Authorization": f"token {token}" if token else "",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_epic_issue(self, epic_data: Dict[str, Any]) -> int:
        """Создать GitHub issue для эпика"""
        
        title = f"EPIC {epic_data['id']}: {epic_data['name']}"
        
        body = f"""# EPIC {epic_data['id']}: {epic_data['name']}

**Статус**: {epic_data['status']}  
**Приоритет**: {epic_data['priority']}  
**Оценка**: {epic_data['estimate']}  
**Связь**: {epic_data.get('dependencies', 'None')}

## 🎯 ОПИСАНИЕ

{epic_data['description']}

## ✅ КРИТЕРИИ ГОТОВНОСТИ

{self._format_criteria(epic_data['done_criteria'])}

## 📋 ISSUES (TASKS)

{self._format_tasks(epic_data['tasks'])}

## 📊 МЕТРИКИ

{self._format_metrics(epic_data['metrics'])}

---

**🚀 READY FOR DEVELOPMENT!**
"""
        
        labels = ["epic", "planning", epic_data['priority'].lower()]
        
        if self.use_cli:
            return self._create_issue_via_cli(title, body, labels)
        else:
            return self._create_issue_via_api(title, body, labels)
    
    def create_task_issue(self, task_data: Dict[str, Any], epic_number: int) -> int:
        """Создать GitHub issue для задачи"""
        
        title = f"ISSUE-{task_data['id']:03d}: {task_data['name']}"
        
        body = f"""# ISSUE-{task_data['id']:03d}: {task_data['name']}

**Epic**: #{epic_number}  
**Приоритет**: {task_data['priority']}  
**Оценка**: {task_data['estimate']}  
**Статус**: 🆕 NEW

## 🎯 ОПИСАНИЕ

{task_data['description']}

## ✅ ACCEPTANCE CRITERIA

{self._format_criteria(task_data['acceptance_criteria'])}

## 🏗️ ТЕХНИЧЕСКАЯ РЕАЛИЗАЦИЯ

```python
{task_data.get('code_example', '# Implementation details')}
```

## 🧪 ТЕСТИРОВАНИЕ

- [ ] Unit тесты написаны
- [ ] Integration тесты проходят  
- [ ] Manual testing выполнен
- [ ] Edge cases покрыты

---

**Definition of Done**: All acceptance criteria ✅, tests pass ✅, code reviewed ✅, deployed ✅
"""
        
        labels = ["task", "development", task_data['priority'].lower()]
        
        if self.use_cli:
            return self._create_issue_via_cli(title, body, labels)
        else:
            return self._create_issue_via_api(title, body, labels)
    
    def _create_issue_via_api(self, title: str, body: str, labels: List[str]) -> int:
        """Создать issue через GitHub API"""
        issue_data = {
            "title": title,
            "body": body,
            "labels": labels
        }
        
        response = requests.post(
            f"{self.base_url}/issues",
            headers=self.headers,
            json=issue_data
        )
        
        if response.status_code == 201:
            issue_number = response.json()['number']
            print(f"✅ Created issue #{issue_number}: {title}")
            return issue_number
        else:
            print(f"❌ Failed to create issue: {response.json()}")
            return None
    
    def _create_issue_via_cli(self, title: str, body: str, labels: List[str]) -> int:
        """Создать issue через GitHub CLI"""
        try:
            # Создание временного файла для body
            body_file = f"/tmp/gh_issue_body_{os.getpid()}.md"
            with open(body_file, 'w', encoding='utf-8') as f:
                f.write(body)
            
            # Команда gh CLI
            cmd = [
                'gh', 'issue', 'create',
                '--title', title,
                '--body-file', body_file,
                '--label', ','.join(labels),
                '--repo', f"{self.owner}/{self.repo}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Удаление временного файла
            os.unlink(body_file)
            
            if result.returncode == 0:
                # Извлечение номера issue из URL
                issue_url = result.stdout.strip()
                issue_number = int(issue_url.split('/')[-1])
                print(f"✅ Created issue #{issue_number}: {title}")
                return issue_number
            else:
                print(f"❌ Failed to create issue via CLI: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating issue via CLI: {e}")
            return None
    
    def _format_criteria(self, criteria: List[str]) -> str:
        return "\n".join([f"- [ ] {criterion}" for criterion in criteria])
    
    def _format_tasks(self, tasks: List[Dict]) -> str:
        result = ""
        for task in tasks:
            result += f"""
### **ISSUE-{task['id']:03d}: {task['name']}**
- **Приоритет**: {task['priority']}
- **Оценка**: {task['estimate']}
- **Описание**: {task['description']}
"""
        return result
    
    def _format_metrics(self, metrics: Dict[str, str]) -> str:
        return "\n".join([f"- **{key}**: {value}" for key, value in metrics.items()])

def load_epics_data() -> List[Dict[str, Any]]:
    """Загрузить данные эпиков из JSON"""
    epics_file = Path("epics/epics_data.json")
    if epics_file.exists():
        with open(epics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("❌ File epics/epics_data.json not found!")
        return []

def main():
    """Основная функция для создания issues"""
    
    # Настройки GitHub (получить из environment variables)
    repo_owner = os.getenv('GITHUB_OWNER', 'kpblc')
    repo_name = os.getenv('GITHUB_REPO', 'llmstruct')  
    github_token = os.getenv('GITHUB_TOKEN')
    use_cli = os.getenv('GITHUB_USE_CLI', 'false').lower() == 'true'
    
    if not github_token and not use_cli:
        print("❌ GITHUB_TOKEN environment variable required!")
        print("   OR set GITHUB_USE_CLI=true to use GitHub CLI")
        return
    
    print(f"🚀 Creating GitHub issues for repository {repo_owner}/{repo_name}")
    print(f"   Mode: {'GitHub CLI' if use_cli else 'GitHub API'}")
    
    creator = GitHubIssuesCreator(repo_owner, repo_name, github_token, use_cli)
    epics_data = load_epics_data()
    
    if not epics_data:
        print("❌ No epics data found!")
        return
    
    epics_list = epics_data.get('epics', epics_data)  # Handle both structures
    
    print(f"📋 Found {len(epics_list)} epics to process...")
    
    for epic_data in epics_list:
        # Создать issue для эпика
        epic_issue_number = creator.create_epic_issue(epic_data)
        
        if epic_issue_number:
            # Создать issues для всех задач эпика
            for task_data in epic_data.get('tasks', []):
                creator.create_task_issue(task_data, epic_issue_number)
    
    print("🎉 All issues created successfully!")

if __name__ == "__main__":
    main() 