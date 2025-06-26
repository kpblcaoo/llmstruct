#!/usr/bin/env python3
"""
Tasks Index Creator
Scans all documentation files and creates comprehensive index of tasks, EPICs, TODOs, and other actionable items.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a single task or actionable item."""
    title: str
    description: str
    status: str  # "planned", "in_progress", "completed", "on_hold", "cancelled"
    priority: str  # "high", "medium", "low", "critical"
    category: str  # "epic", "task", "todo", "idea", "research", "bugfix"
    file_source: str
    line_number: int
    estimated_effort: str  # "quick", "medium", "large", "unknown"
    dependencies: List[str]
    tags: List[str]
    created_date: str
    target_date: Optional[str] = None
    assignee: Optional[str] = None
    notes: str = ""


class TaskExtractor:
    """Extract tasks from various document formats."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for task extraction."""
        return {
            # EPIC patterns
            'epic_header': re.compile(r'^#{1,3}\s*(?:EPIC|Epic)\s*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'epic_checkbox': re.compile(r'^-\s*\[\s*[x\s]\s*\]\s*(?:EPIC|Epic)[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            
            # Task patterns
            'task_header': re.compile(r'^#{1,4}\s*(?:TASK|Task|TSK)[:\s-]*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'task_checkbox': re.compile(r'^-\s*\[\s*([x\s])\s*\]\s*(.+)', re.MULTILINE),
            'task_numbered': re.compile(r'^\d+\.\s*(.+)', re.MULTILINE),
            
            # TODO patterns
            'todo_comment': re.compile(r'#?\s*TODO[:\s]*(.+)', re.IGNORECASE),
            'todo_checkbox': re.compile(r'^-\s*\[\s*[x\s]\s*\]\s*TODO[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            
            # Phase/Step patterns
            'phase_header': re.compile(r'^#{1,4}\s*(?:ФАЗА|PHASE|Phase)\s*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'step_pattern': re.compile(r'^-\s*\[\s*[x\s]\s*\]\s*(.+)', re.MULTILINE),
            
            # Status patterns
            'status_pattern': re.compile(r'\*\*Статус\*\*[:\s]*(.+)', re.IGNORECASE),
            'priority_pattern': re.compile(r'\*\*Приоритет\*\*[:\s]*(.+)', re.IGNORECASE),
            
            # Date patterns
            'date_pattern': re.compile(r'\*\*Дата\*\*[:\s]*(\d{2}\.\d{2}\.\d{4})', re.IGNORECASE),
            'target_date_pattern': re.compile(r'(?:до|deadline|target)[:\s]*(\d{2}\.\d{2}\.\d{4})', re.IGNORECASE),
        }
    
    def extract_from_markdown(self, file_path: Path) -> List[Task]:
        """Extract tasks from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tasks = []
            
            # Extract document metadata
            doc_status = self._extract_status(content)
            doc_priority = self._extract_priority(content)
            doc_date = self._extract_date(content)
            
            # Extract EPICs
            tasks.extend(self._extract_epics(content, file_path, doc_status, doc_priority, doc_date))
            
            # Extract explicit tasks
            tasks.extend(self._extract_tasks(content, file_path, doc_status, doc_priority, doc_date))
            
            # Extract TODOs
            tasks.extend(self._extract_todos(content, file_path, doc_status, doc_priority, doc_date))
            
            # Extract phases and steps
            tasks.extend(self._extract_phases(content, file_path, doc_status, doc_priority, doc_date))
            
            # Extract checkbox items
            tasks.extend(self._extract_checkboxes(content, file_path, doc_status, doc_priority, doc_date))
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error extracting from {file_path}: {e}")
            return []
    
    def _extract_status(self, content: str) -> str:
        """Extract document status."""
        match = self.patterns['status_pattern'].search(content)
        if match:
            status = match.group(1).strip().lower()
            if 'проработка' in status or 'research' in status:
                return 'in_progress'
            elif 'готов' in status or 'completed' in status:
                return 'completed'
            elif 'план' in status or 'planned' in status:
                return 'planned'
        return 'planned'
    
    def _extract_priority(self, content: str) -> str:
        """Extract document priority."""
        match = self.patterns['priority_pattern'].search(content)
        if match:
            priority = match.group(1).strip().lower()
            if 'критич' in priority or 'critical' in priority:
                return 'critical'
            elif 'высок' in priority or 'high' in priority:
                return 'high'
            elif 'средн' in priority or 'medium' in priority:
                return 'medium'
            elif 'низк' in priority or 'low' in priority:
                return 'low'
        return 'medium'
    
    def _extract_date(self, content: str) -> str:
        """Extract document date."""
        match = self.patterns['date_pattern'].search(content)
        if match:
            return match.group(1)
        return datetime.now().strftime("%d.%m.%Y")
    
    def _extract_epics(self, content: str, file_path: Path, doc_status: str, doc_priority: str, doc_date: str) -> List[Task]:
        """Extract EPIC items."""
        tasks = []
        
        for match in self.patterns['epic_header'].finditer(content):
            epic_num = match.group(1) or ""
            epic_title = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            task = Task(
                title=f"EPIC {epic_num}: {epic_title}" if epic_num else f"EPIC: {epic_title}",
                description=self._extract_context(content, match.start(), match.end()),
                status=doc_status,
                priority=doc_priority,
                category="epic",
                file_source=str(file_path),
                line_number=line_num,
                estimated_effort="large",
                dependencies=[],
                tags=["epic"],
                created_date=doc_date
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_tasks(self, content: str, file_path: Path, doc_status: str, doc_priority: str, doc_date: str) -> List[Task]:
        """Extract explicit task items."""
        tasks = []
        
        for match in self.patterns['task_header'].finditer(content):
            task_num = match.group(1) or ""
            task_title = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            task = Task(
                title=f"TASK {task_num}: {task_title}" if task_num else task_title,
                description=self._extract_context(content, match.start(), match.end()),
                status=doc_status,
                priority=doc_priority,
                category="task",
                file_source=str(file_path),
                line_number=line_num,
                estimated_effort="medium",
                dependencies=[],
                tags=["task"],
                created_date=doc_date
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_todos(self, content: str, file_path: Path, doc_status: str, doc_priority: str, doc_date: str) -> List[Task]:
        """Extract TODO items."""
        tasks = []
        
        for match in self.patterns['todo_comment'].finditer(content):
            todo_title = match.group(1).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            task = Task(
                title=f"TODO: {todo_title}",
                description="",
                status="planned",
                priority="low",
                category="todo",
                file_source=str(file_path),
                line_number=line_num,
                estimated_effort="quick",
                dependencies=[],
                tags=["todo"],
                created_date=doc_date
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_phases(self, content: str, file_path: Path, doc_status: str, doc_priority: str, doc_date: str) -> List[Task]:
        """Extract phase/step items."""
        tasks = []
        
        for match in self.patterns['phase_header'].finditer(content):
            phase_num = match.group(1) or ""
            phase_title = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            task = Task(
                title=f"PHASE {phase_num}: {phase_title}" if phase_num else f"PHASE: {phase_title}",
                description=self._extract_context(content, match.start(), match.end()),
                status=doc_status,
                priority=doc_priority,
                category="phase",
                file_source=str(file_path),
                line_number=line_num,
                estimated_effort="large",
                dependencies=[],
                tags=["phase"],
                created_date=doc_date
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_checkboxes(self, content: str, file_path: Path, doc_status: str, doc_priority: str, doc_date: str) -> List[Task]:
        """Extract checkbox items as tasks."""
        tasks = []
        
        for match in self.patterns['task_checkbox'].finditer(content):
            checked = match.group(1).strip() == 'x'
            task_title = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            # Skip if it's already captured as EPIC or TODO
            if any(keyword in task_title.upper() for keyword in ['EPIC', 'TODO', 'ФАЗА', 'PHASE']):
                continue
            
            task = Task(
                title=task_title,
                description="",
                status="completed" if checked else "planned",
                priority="medium",
                category="task",
                file_source=str(file_path),
                line_number=line_num,
                estimated_effort="medium",
                dependencies=[],
                tags=["checkbox"],
                created_date=doc_date
            )
            tasks.append(task)
        
        return tasks
    
    def _extract_context(self, content: str, start: int, end: int, context_lines: int = 3) -> str:
        """Extract surrounding context for a match."""
        lines = content.split('\n')
        match_line = content[:start].count('\n')
        
        start_line = max(0, match_line - context_lines)
        end_line = min(len(lines), match_line + context_lines + 1)
        
        context = '\n'.join(lines[start_line:end_line])
        return context.strip()


class TaskIndexGenerator:
    """Generate comprehensive task index."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.extractor = TaskExtractor(project_root)
    
    def scan_documentation(self) -> List[Task]:
        """Scan all documentation files for tasks."""
        all_tasks = []
        
        # Scan docs/ directory
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for md_file in docs_dir.glob("*.md"):
                logger.info(f"Scanning {md_file}")
                tasks = self.extractor.extract_from_markdown(md_file)
                all_tasks.extend(tasks)
        
        # Scan root directory markdown files
        for md_file in self.project_root.glob("*.md"):
            logger.info(f"Scanning {md_file}")
            tasks = self.extractor.extract_from_markdown(md_file)
            all_tasks.extend(tasks)
        
        return all_tasks
    
    def generate_index(self, tasks: List[Task]) -> Dict:
        """Generate comprehensive task index."""
        # Group tasks by various criteria
        by_category = {}
        by_status = {}
        by_priority = {}
        by_file = {}
        
        for task in tasks:
            # By category
            if task.category not in by_category:
                by_category[task.category] = []
            by_category[task.category].append(task)
            
            # By status
            if task.status not in by_status:
                by_status[task.status] = []
            by_status[task.status].append(task)
            
            # By priority
            if task.priority not in by_priority:
                by_priority[task.priority] = []
            by_priority[task.priority].append(task)
            
            # By file
            if task.file_source not in by_file:
                by_file[task.file_source] = []
            by_file[task.file_source].append(task)
        
        # Generate statistics
        stats = {
            'total_tasks': len(tasks),
            'by_category': {cat: len(tasks) for cat, tasks in by_category.items()},
            'by_status': {status: len(tasks) for status, tasks in by_status.items()},
            'by_priority': {priority: len(tasks) for priority, tasks in by_priority.items()},
            'by_file': {file: len(tasks) for file, tasks in by_file.items()}
        }
        
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_files_scanned': len(by_file),
                'statistics': stats
            },
            'tasks': [asdict(task) for task in tasks],
            'grouped': {
                'by_category': {cat: [asdict(t) for t in tasks] for cat, tasks in by_category.items()},
                'by_status': {status: [asdict(t) for t in tasks] for status, tasks in by_status.items()},
                'by_priority': {priority: [asdict(t) for t in tasks] for priority, tasks in by_priority.items()},
                'by_file': {file: [asdict(t) for t in tasks] for file, tasks in by_file.items()}
            }
        }
    
    def generate_summary_report(self, index: Dict) -> str:
        """Generate human-readable summary report."""
        stats = index['metadata']['statistics']
        
        report = f"""# 📋 TASKS INDEX SUMMARY REPORT

**Generated**: {index['metadata']['generated_at']}  
**Files Scanned**: {index['metadata']['total_files_scanned']}  
**Total Tasks Found**: {stats['total_tasks']}

---

## 📊 STATISTICS OVERVIEW

### By Category:
"""
        
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category.upper()}**: {count} items\n"
        
        report += "\n### By Status:\n"
        for status, count in sorted(stats['by_status'].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{status.upper()}**: {count} items\n"
        
        report += "\n### By Priority:\n"
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            if priority in stats['by_priority']:
                count = stats['by_priority'][priority]
                report += f"- **{priority.upper()}**: {count} items\n"
        
        report += "\n---\n\n## 📁 BY FILE\n\n"
        
        for file_path, tasks in index['grouped']['by_file'].items():
            file_name = Path(file_path).name
            report += f"### {file_name}\n"
            report += f"**Location**: `{file_path}`  \n"
            report += f"**Tasks**: {len(tasks)} items  \n\n"
            
            # Group by category in this file
            file_categories = {}
            for task in tasks:
                cat = task['category']
                if cat not in file_categories:
                    file_categories[cat] = []
                file_categories[cat].append(task)
            
            for category, cat_tasks in file_categories.items():
                report += f"**{category.upper()}** ({len(cat_tasks)}):\n"
                for task in cat_tasks[:5]:  # Show first 5 tasks
                    status_emoji = "✅" if task['status'] == 'completed' else "🔄" if task['status'] == 'in_progress' else "📋"
                    report += f"- {status_emoji} {task['title']}\n"
                
                if len(cat_tasks) > 5:
                    report += f"- ... and {len(cat_tasks) - 5} more\n"
                report += "\n"
        
        report += "\n---\n\n## 🎯 ACTION ITEMS\n\n"
        
        # Show high priority planned tasks
        high_priority_planned = [
            task for task in index['tasks'] 
            if task['priority'] in ['critical', 'high'] and task['status'] == 'planned'
        ]
        
        if high_priority_planned:
            report += "### High Priority Planned Tasks:\n"
            for task in high_priority_planned[:10]:  # Top 10
                report += f"- **{task['title']}** ({task['category']}) - {task['file_source']}\n"
        
        # Show in-progress tasks
        in_progress = [task for task in index['tasks'] if task['status'] == 'in_progress']
        if in_progress:
            report += "\n### In Progress Tasks:\n"
            for task in in_progress:
                report += f"- **{task['title']}** ({task['category']}) - {task['file_source']}\n"
        
        return report
    
    def save_index(self, index: Dict, summary: str, output_dir: str = "docs"):
        """Save index and summary to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save JSON index
        json_path = output_path / "TASKS_INDEX.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        summary_path = output_path / "TASKS_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Saved index to {json_path}")
        logger.info(f"Saved summary to {summary_path}")
        
        return json_path, summary_path


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comprehensive tasks index")
    parser.add_argument("--output-dir", default="docs", help="Output directory for generated files")
    parser.add_argument("--summary-only", action="store_true", help="Generate only summary report")
    
    args = parser.parse_args()
    
    generator = TaskIndexGenerator()
    
    logger.info("Scanning documentation for tasks...")
    tasks = generator.scan_documentation()
    
    logger.info(f"Found {len(tasks)} tasks")
    
    if not args.summary_only:
        logger.info("Generating comprehensive index...")
        index = generator.generate_index(tasks)
        
        logger.info("Generating summary report...")
        summary = generator.generate_summary_report(index)
        
        # Save files
        json_path, summary_path = generator.save_index(index, summary, args.output_dir)
        
        print("\n✅ Generated task index:")
        print(f"   📄 JSON Index: {json_path}")
        print(f"   📋 Summary: {summary_path}")
    else:
        # Generate quick summary
        by_category = {}
        by_status = {}
        
        for task in tasks:
            by_category[task.category] = by_category.get(task.category, 0) + 1
            by_status[task.status] = by_status.get(task.status, 0) + 1
        
        print(f"\n📋 QUICK SUMMARY - {len(tasks)} tasks found:")
        print("\nBy Category:")
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        
        print("\nBy Status:")
        for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")


if __name__ == "__main__":
    main() 