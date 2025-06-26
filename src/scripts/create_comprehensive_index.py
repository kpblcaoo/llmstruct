#!/usr/bin/env python3
"""
Comprehensive Project Index Creator
Scans ALL project directories for tasks, ideas, sessions, and concepts.
Provides complete visibility into project state and unaccounted innovations.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ProjectItem:
    """Unified representation of any project item (task, idea, session, concept)."""
    id: str
    title: str
    description: str
    type: str  # "task", "idea", "session", "concept", "epic", "todo"
    status: str
    priority: str
    category: str
    file_source: str
    line_number: int
    estimated_effort: str
    tags: List[str]
    created_date: str
    discovery_method: str  # "docs_scan", "json_parse", "personal_scan", "temp_scan"
    content_preview: str
    related_items: List[str]
    strategic_value: str  # "revolutionary", "high", "medium", "low"


class ComprehensiveIndexer:
    """Comprehensive indexer for all project content."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.items = []
        self.patterns = self._init_patterns()
        
        # Define scan directories with priorities
        self.scan_config = {
            "docs": {"priority": "high", "recursive": True, "types": ["md", "txt"]},
            ".personal": {"priority": "critical", "recursive": True, "types": ["md", "txt", "json"]},
            "temp_workfiles": {"priority": "high", "recursive": True, "types": ["md", "txt", "json", "py"]},
            "data": {"priority": "medium", "recursive": False, "types": ["json"]},
            "data/sessions": {"priority": "high", "recursive": True, "types": ["json", "md"]},
            ".": {"priority": "low", "recursive": False, "types": ["md", "txt"]}  # Root level files
        }
    
    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize comprehensive extraction patterns."""
        return {
            # Task patterns (English and Russian)
            'task_header': re.compile(r'^#{1,4}\s*(?:TASK|Task|TSK|ЗАДАЧА|Задача)[:\s-]*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'task_checkbox': re.compile(r'^-\s*\[\s*([x\s])\s*\]\s*(?:\*\*)?(.+?)(?:\*\*)?$', re.MULTILINE),
            'task_numbered': re.compile(r'^\d+\.\s*(?:\*\*)?(.+?)(?:\*\*)?', re.MULTILINE),
            
            # Epic patterns
            'epic_header': re.compile(r'^#{1,3}\s*(?:EPIC|Epic|ЭПИК)[:\s]*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'epic_meta': re.compile(r'\[META\]', re.IGNORECASE),
            
            # TODO patterns
            'todo_comment': re.compile(r'#?\s*TODO[:\s]*(.+)', re.IGNORECASE),
            'todo_checkbox': re.compile(r'^-\s*\[\s*[x\s]\s*\]\s*TODO[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            
            # Idea patterns
            'idea_header': re.compile(r'^#{1,4}\s*(?:IDEA|Idea|ИДЕЯ|Идея)[:\s-]*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            'innovation_keywords': re.compile(r'(революц|прорыв|breakthrough|innovation|pioneer|cutting.?edge|game.?chang|patent|first.?mover)', re.IGNORECASE),
            
            # Session patterns
            'session_header': re.compile(r'^#{1,4}\s*(?:SESSION|Session|СЕССИЯ|Сессия)[:\s-]*(\d+)?[:\s]*(.+)', re.MULTILINE | re.IGNORECASE),
            
            # Priority/Status patterns
            'priority_critical': re.compile(r'(критич|critical|CRITICAL|революц|revolutionary)', re.IGNORECASE),
            'priority_high': re.compile(r'(высок|high|HIGH|важн|important)', re.IGNORECASE),
            'status_completed': re.compile(r'(завершен|completed|COMPLETED|готов|done)', re.IGNORECASE),
            'status_progress': re.compile(r'(выполня|in.?progress|IN.?PROGRESS|проработ)', re.IGNORECASE),
            
            # Strategic value patterns
            'strategic_revolutionary': re.compile(r'(prize.?worthy|patent|first.?mover|game.?chang|revolutio|прорыв)', re.IGNORECASE),
            'strategic_high': re.compile(r'(competitive.?advantage|market.?leader|enterprise|revenue)', re.IGNORECASE),
        }
    
    def scan_all_directories(self) -> List[ProjectItem]:
        """Scan all configured directories comprehensively."""
        logger.info("Starting comprehensive project scan...")
        
        for directory, config in self.scan_config.items():
            if directory == ".":
                self._scan_root_files(config)
            else:
                self._scan_directory(directory, config)
        
        # Parse JSON files for structured data
        self._parse_json_files()
        
        # Post-process and enhance items
        self._enhance_items()
        
        logger.info(f"Comprehensive scan completed: {len(self.items)} items discovered")
        return self.items
    
    def _scan_directory(self, directory: str, config: Dict):
        """Scan a specific directory according to its configuration."""
        dir_path = self.project_root / directory
        
        if not dir_path.exists():
            logger.warning(f"Directory not found: {directory}")
            return
        
        logger.info(f"Scanning {directory} (priority: {config['priority']})")
        
        file_pattern = "**/*" if config["recursive"] else "*"
        
        for file_path in dir_path.glob(file_pattern):
            if file_path.is_file() and self._should_scan_file(file_path, config["types"]):
                self._scan_file(file_path, directory, config["priority"])
    
    def _scan_root_files(self, config: Dict):
        """Scan root-level files."""
        for file_path in self.project_root.glob("*"):
            if file_path.is_file() and self._should_scan_file(file_path, config["types"]):
                self._scan_file(file_path, "root", config["priority"])
    
    def _should_scan_file(self, file_path: Path, allowed_types: List[str]) -> bool:
        """Check if file should be scanned based on extension."""
        return file_path.suffix.lstrip('.').lower() in allowed_types
    
    def _scan_file(self, file_path: Path, source_dir: str, priority: str):
        """Scan individual file for project items."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract different types of items
            if file_path.suffix.lower() == '.json':
                self._extract_from_json(file_path, content, source_dir, priority)
            else:
                self._extract_from_text(file_path, content, source_dir, priority)
                
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
    
    def _extract_from_text(self, file_path: Path, content: str, source_dir: str, priority: str):
        """Extract items from text/markdown files."""
        
        # Extract tasks
        for match in self.patterns['task_header'].finditer(content):
            item = self._create_item_from_match(
                match, content, file_path, "task", source_dir, priority
            )
            self.items.append(item)
        
        # Extract checkboxes as tasks
        for match in self.patterns['task_checkbox'].finditer(content):
            if not self._is_noise_checkbox(match.group(2)):
                item = self._create_checkbox_item(
                    match, content, file_path, "task", source_dir, priority
                )
                self.items.append(item)
        
        # Extract EPICs
        for match in self.patterns['epic_header'].finditer(content):
            item = self._create_item_from_match(
                match, content, file_path, "epic", source_dir, priority
            )
            # Check for META epic
            if self.patterns['epic_meta'].search(match.group(2)):
                item.strategic_value = "revolutionary"
                item.tags.append("meta")
            self.items.append(item)
        
        # Extract ideas
        for match in self.patterns['idea_header'].finditer(content):
            item = self._create_item_from_match(
                match, content, file_path, "idea", source_dir, priority
            )
            self.items.append(item)
        
        # Extract TODOs
        for match in self.patterns['todo_comment'].finditer(content):
            item = self._create_simple_item(
                match.group(1), content, file_path, "todo", source_dir, priority, match.start()
            )
            self.items.append(item)
        
        # Extract sessions
        for match in self.patterns['session_header'].finditer(content):
            item = self._create_item_from_match(
                match, content, file_path, "session", source_dir, priority
            )
            self.items.append(item)
        
        # Look for innovation concepts
        if self.patterns['innovation_keywords'].search(content):
            self._extract_innovation_concepts(file_path, content, source_dir, priority)
    
    def _extract_from_json(self, file_path: Path, content: str, source_dir: str, priority: str):
        """Extract items from JSON files."""
        try:
            data = json.loads(content)
            
            # Handle different JSON structures
            if "tasks" in data:
                self._extract_json_tasks(data["tasks"], file_path, source_dir, priority)
            elif "ideas" in data:
                self._extract_json_ideas(data["ideas"], file_path, source_dir, priority)
            elif "sessions" in data:
                self._extract_json_sessions(data["sessions"], file_path, source_dir, priority)
            elif isinstance(data, list) and data:
                # Handle arrays of items
                self._extract_json_array(data, file_path, source_dir, priority)
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {file_path}")
    
    def _create_item_from_match(self, match, content: str, file_path: Path, item_type: str, source_dir: str, priority: str) -> ProjectItem:
        """Create ProjectItem from regex match."""
        line_num = content[:match.start()].count('\n') + 1
        title = match.group(2) if match.lastindex >= 2 else match.group(1)
        
        return ProjectItem(
            id=f"{item_type}_{file_path.stem}_{line_num}",
            title=title.strip(),
            description=self._extract_context(content, match.start(), 200),
            type=item_type,
            status=self._detect_status(content, match.start()),
            priority=self._detect_priority(content, match.start(), priority),
            category=self._detect_category(title, content),
            file_source=str(file_path),
            line_number=line_num,
            estimated_effort=self._estimate_effort(title, content),
            tags=self._extract_tags(title, content, source_dir),
            created_date=datetime.now().strftime("%Y-%m-%d"),
            discovery_method=f"{source_dir}_scan",
            content_preview=self._extract_context(content, match.start(), 100),
            related_items=[],
            strategic_value=self._assess_strategic_value(title, content)
        )
    
    def _create_checkbox_item(self, match, content: str, file_path: Path, item_type: str, source_dir: str, priority: str) -> ProjectItem:
        """Create ProjectItem from checkbox match."""
        line_num = content[:match.start()].count('\n') + 1
        checked = match.group(1).strip() == 'x'
        title = match.group(2).strip()
        
        return ProjectItem(
            id=f"checkbox_{file_path.stem}_{line_num}",
            title=title,
            description=self._extract_context(content, match.start(), 150),
            type=item_type,
            status="completed" if checked else "planned",
            priority=self._detect_priority(content, match.start(), priority),
            category=self._detect_category(title, content),
            file_source=str(file_path),
            line_number=line_num,
            estimated_effort=self._estimate_effort(title, content),
            tags=self._extract_tags(title, content, source_dir),
            created_date=datetime.now().strftime("%Y-%m-%d"),
            discovery_method=f"{source_dir}_scan",
            content_preview=title[:100],
            related_items=[],
            strategic_value=self._assess_strategic_value(title, content)
        )
    
    def _create_simple_item(self, title: str, content: str, file_path: Path, item_type: str, source_dir: str, priority: str, position: int) -> ProjectItem:
        """Create simple ProjectItem."""
        line_num = content[:position].count('\n') + 1
        
        return ProjectItem(
            id=f"{item_type}_{file_path.stem}_{line_num}",
            title=title.strip(),
            description=self._extract_context(content, position, 100),
            type=item_type,
            status="planned",
            priority=priority,
            category=item_type,
            file_source=str(file_path),
            line_number=line_num,
            estimated_effort="quick",
            tags=[item_type, source_dir],
            created_date=datetime.now().strftime("%Y-%m-%d"),
            discovery_method=f"{source_dir}_scan",
            content_preview=title[:100],
            related_items=[],
            strategic_value="low"
        )
    
    def _detect_status(self, content: str, position: int) -> str:
        """Detect item status from surrounding content."""
        context = content[max(0, position-200):position+200]
        
        if self.patterns['status_completed'].search(context):
            return "completed"
        elif self.patterns['status_progress'].search(context):
            return "in_progress"
        else:
            return "planned"
    
    def _detect_priority(self, content: str, position: int, default: str) -> str:
        """Detect item priority from surrounding content."""
        context = content[max(0, position-300):position+300]
        
        if self.patterns['priority_critical'].search(context):
            return "critical"
        elif self.patterns['priority_high'].search(context):
            return "high"
        else:
            return default
    
    def _assess_strategic_value(self, title: str, content: str) -> str:
        """Assess strategic value of item."""
        combined = f"{title} {content}"
        
        if self.patterns['strategic_revolutionary'].search(combined):
            return "revolutionary"
        elif self.patterns['strategic_high'].search(combined):
            return "high"
        else:
            return "medium"
    
    def _extract_context(self, content: str, position: int, length: int) -> str:
        """Extract context around position."""
        start = max(0, position - length//2)
        end = min(len(content), position + length//2)
        return content[start:end].strip()
    
    def _detect_category(self, title: str, content: str) -> str:
        """Detect item category."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['security', 'audit', 'safety']):
            return 'security'
        elif any(word in title_lower for word in ['api', 'integration', 'platform']):
            return 'architecture'  
        elif any(word in title_lower for word in ['ai', 'llm', 'model', 'intelligence']):
            return 'ai_enhancement'
        elif any(word in title_lower for word in ['docs', 'documentation', 'guide']):
            return 'documentation'
        else:
            return 'general'
    
    def _estimate_effort(self, title: str, content: str) -> str:
        """Estimate effort required."""
        combined = f"{title} {content}".lower()
        
        if any(word in combined for word in ['mvp', 'prototype', 'quick', 'simple']):
            return 'quick'
        elif any(word in combined for word in ['platform', 'system', 'comprehensive', 'framework']):
            return 'large'
        else:
            return 'medium'
    
    def _extract_tags(self, title: str, content: str, source_dir: str) -> List[str]:
        """Extract relevant tags."""
        tags = [source_dir.replace('.', '').replace('_', '-')]
        
        title_lower = title.lower()
        if 'ai' in title_lower or 'llm' in title_lower:
            tags.append('ai')
        if 'security' in title_lower:
            tags.append('security')
        if 'api' in title_lower:
            tags.append('api')
        if 'meta' in title_lower:
            tags.append('meta')
        
        return tags
    
    def _is_noise_checkbox(self, text: str) -> bool:
        """Check if checkbox is noise (navigation, etc)."""
        noise_patterns = ['docs/', 'file:', 'http', 'see also', 'reference']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in noise_patterns) or len(text.strip()) < 10
    
    def _parse_json_files(self):
        """Parse structured JSON files for existing data."""
        json_files = [
            "data/ideas.json",
            "data/tasks.json", 
            "data/sessions/ai_sessions.json"
        ]
        
        for json_file in json_files:
            file_path = self.project_root / json_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._process_structured_json(data, file_path)
                except Exception as e:
                    logger.error(f"Error parsing {json_file}: {e}")
    
    def _process_structured_json(self, data: Dict, file_path: Path):
        """Process structured JSON data."""
        if "ideas" in data:
            for idea in data["ideas"]:
                if isinstance(idea, dict) and "id" in idea:
                    self._add_json_item(idea, file_path, "idea")
        
        if "tasks" in data and isinstance(data["tasks"], list):
            for task in data["tasks"]:
                if isinstance(task, dict) and "id" in task:
                    self._add_json_item(task, file_path, "task")
        
        if "sessions" in data:
            for session in data["sessions"]:
                if isinstance(session, dict) and "id" in session:
                    self._add_json_item(session, file_path, "session")
    
    def _add_json_item(self, item: Dict, file_path: Path, item_type: str):
        """Add item from JSON structure."""
        project_item = ProjectItem(
            id=item.get("id", f"json_{item_type}_{len(self.items)}"),
            title=item.get("title", item.get("description", "Untitled")),
            description=item.get("description", ""),
            type=item_type,
            status=item.get("status", "planned"),
            priority=item.get("priority", "medium"),
            category=item.get("category", "general"),
            file_source=str(file_path),
            line_number=0,
            estimated_effort=item.get("estimated_effort", "medium"),
            tags=item.get("tags", []),
            created_date=item.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            discovery_method="json_parse",
            content_preview=item.get("description", "")[:100],
            related_items=item.get("related_tasks", item.get("related_ideas", [])),
            strategic_value=self._assess_json_strategic_value(item)
        )
        self.items.append(project_item)
    
    def _assess_json_strategic_value(self, item: Dict) -> str:
        """Assess strategic value from JSON item."""
        if item.get("ai_generated") and "[META]" in item.get("title", ""):
            return "revolutionary"
        elif item.get("priority") == "critical":
            return "high"
        else:
            return "medium"
    
    def _extract_innovation_concepts(self, file_path: Path, content: str, source_dir: str, priority: str):
        """Extract innovation concepts from content."""
        # Look for significant innovation markers
        innovation_lines = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if self.patterns['innovation_keywords'].search(line):
                innovation_lines.append((i, line))
        
        for line_num, line in innovation_lines:
            if len(line.strip()) > 20:  # Skip short lines
                item = ProjectItem(
                    id=f"innovation_{file_path.stem}_{line_num}",
                    title=line.strip(),
                    description=self._extract_context(content, content.find(line), 200),
                    type="concept",
                    status="proposed",
                    priority="high",
                    category="innovation",
                    file_source=str(file_path),
                    line_number=line_num + 1,
                    estimated_effort="large",
                    tags=["innovation", "breakthrough", source_dir.replace('.', '')],
                    created_date=datetime.now().strftime("%Y-%m-%d"),
                    discovery_method=f"{source_dir}_innovation_scan",
                    content_preview=line[:100],
                    related_items=[],
                    strategic_value="revolutionary"
                )
                self.items.append(item)
    
    def _enhance_items(self):
        """Post-process items to enhance metadata and find relationships."""
        logger.info("Enhancing items and finding relationships...")
        
        # Create ID mapping for relationship detection
        id_map = {item.id: item for item in self.items}
        title_map = {}
        
        for item in self.items:
            # Normalize title for matching
            normalized_title = re.sub(r'[^\w\s]', '', item.title.lower())
            if normalized_title not in title_map:
                title_map[normalized_title] = []
            title_map[normalized_title].append(item)
        
        # Find related items
        for item in self.items:
            item.related_items = self._find_related_items(item, id_map, title_map)
    
    def _find_related_items(self, item: ProjectItem, id_map: Dict, title_map: Dict) -> List[str]:
        """Find related items based on content similarity."""
        related = []
        
        # Look for explicit references
        content = f"{item.title} {item.description} {item.content_preview}"
        
        # Find ID references
        id_refs = re.findall(r'(TASK|IDEA|TSK|EPIC)-(\d+)', content, re.IGNORECASE)
        for ref_type, ref_num in id_refs:
            ref_id = f"{ref_type.upper()}-{ref_num}"
            if ref_id in id_map:
                related.append(ref_id)
        
        return related[:5]  # Limit to top 5 relationships
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analysis report."""
        # Statistics
        total_items = len(self.items)
        by_type = {}
        by_source = {}
        by_status = {}
        by_priority = {}
        by_strategic_value = {}
        
        for item in self.items:
            by_type[item.type] = by_type.get(item.type, 0) + 1
            by_source[item.discovery_method] = by_source.get(item.discovery_method, 0) + 1
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_priority[item.priority] = by_priority.get(item.priority, 0) + 1
            by_strategic_value[item.strategic_value] = by_strategic_value.get(item.strategic_value, 0) + 1
        
        # Top innovations
        revolutionary_items = [item for item in self.items if item.strategic_value == "revolutionary"]
        high_value_items = [item for item in self.items if item.strategic_value == "high"]
        
        # Unaccounted discoveries
        personal_items = [item for item in self.items if "personal" in item.discovery_method]
        temp_items = [item for item in self.items if "temp" in item.discovery_method]
        
        return {
            "generation_timestamp": datetime.now().isoformat(),
            "total_items_discovered": total_items,
            "statistics": {
                "by_type": by_type,
                "by_source": by_source,
                "by_status": by_status,
                "by_priority": by_priority,
                "by_strategic_value": by_strategic_value
            },
            "revolutionary_innovations": [asdict(item) for item in revolutionary_items],
            "high_value_items": [asdict(item) for item in high_value_items],
            "unaccounted_discoveries": {
                "personal_folder": [asdict(item) for item in personal_items],
                "temp_workfiles": [asdict(item) for item in temp_items]
            },
            "all_items": [asdict(item) for item in self.items]
        }
    
    def save_comprehensive_index(self, output_dir: str = "docs"):
        """Save comprehensive index and reports."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report
        report = self.generate_comprehensive_report()
        
        # Save main index
        with open(f"{output_dir}/COMPREHENSIVE_INDEX.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save analysis report
        analysis_report = self._generate_analysis_report(report)
        with open(f"{output_dir}/COMPREHENSIVE_ANALYSIS.md", "w", encoding="utf-8") as f:
            f.write(analysis_report)
        
        logger.info(f"Comprehensive index saved to {output_dir}/")
        logger.info(f"📊 Total items: {report['total_items_discovered']}")
        logger.info(f"🚀 Revolutionary innovations: {len(report['revolutionary_innovations'])}")
        logger.info(f"💎 High-value items: {len(report['high_value_items'])}")
    
    def _generate_analysis_report(self, report: Dict) -> str:
        """Generate human-readable analysis report."""
        revolutionary = report['revolutionary_innovations']
        high_value = report['high_value_items']
        stats = report['statistics']
        unaccounted = report['unaccounted_discoveries']
        
        return f"""# 🔍 COMPREHENSIVE PROJECT ANALYSIS
## Complete Discovery Report

**Generated**: {report['generation_timestamp']}  
**Total Items Discovered**: {report['total_items_discovered']}  
**Analysis Scope**: ALL project directories  

---

## 📊 DISCOVERY STATISTICS

### By Type:
{self._format_dict(stats['by_type'])}

### By Source:
{self._format_dict(stats['by_source'])}

### By Strategic Value:
{self._format_dict(stats['by_strategic_value'])}

### By Status:
{self._format_dict(stats['by_status'])}

---

## 🚀 REVOLUTIONARY INNOVATIONS ({len(revolutionary)})

{self._format_items_list(revolutionary)}

---

## 💎 HIGH-VALUE ITEMS ({len(high_value)})

{self._format_items_list(high_value[:10])}  # Top 10

---

## 🔍 UNACCOUNTED DISCOVERIES

### Personal Folder ({len(unaccounted['personal_folder'])}):
{self._format_items_list(unaccounted['personal_folder'][:5])}

### Temp Workfiles ({len(unaccounted['temp_workfiles'])}):
{self._format_items_list(unaccounted['temp_workfiles'][:5])}

---

## 🎯 KEY INSIGHTS

### Coverage Analysis:
- **Docs Folder**: {stats['by_source'].get('docs_scan', 0)} items
- **Personal Folder**: {stats['by_source'].get('personal_scan', 0)} items  
- **Temp Workfiles**: {stats['by_source'].get('temp_scan', 0)} items
- **JSON Parse**: {stats['by_source'].get('json_parse', 0)} items

### Innovation Density:
- **Revolutionary Ideas**: {len(revolutionary)} ({len(revolutionary)/report['total_items_discovered']*100:.1f}%)
- **High-Value Items**: {len(high_value)} ({len(high_value)/report['total_items_discovered']*100:.1f}%)

### Project Completeness:
- **Completed Items**: {stats['by_status'].get('completed', 0)}
- **In Progress**: {stats['by_status'].get('in_progress', 0)}
- **Planned**: {stats['by_status'].get('planned', 0)}

---

**CONCLUSION**: This comprehensive scan reveals the full scope of project innovation and identifies unaccounted strategic opportunities that were missed in previous partial scans.
"""
    
    def _format_dict(self, d: Dict) -> str:
        """Format dictionary for markdown display."""
        return '\n'.join(f"- **{k}**: {v}" for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True))
    
    def _format_items_list(self, items: List[Dict]) -> str:
        """Format items list for markdown display."""
        if not items:
            return "*No items found*"
        
        result = []
        for item in items[:10]:  # Limit display
            result.append(f"### {item['title']}")
            result.append(f"- **Type**: {item['type']} | **Priority**: {item['priority']} | **Strategic Value**: {item['strategic_value']}")
            result.append(f"- **Source**: {item['file_source']} (line {item['line_number']})")
            result.append(f"- **Preview**: {item['content_preview'][:100]}...")
            result.append("")
        
        return '\n'.join(result)

    def _extract_json_tasks(self, tasks_data, file_path: Path, source_dir: str, priority: str):
        """Extract tasks from JSON tasks array."""
        if isinstance(tasks_data, list):
            for task in tasks_data:
                if isinstance(task, dict):
                    self._add_json_item(task, file_path, "task")
    
    def _extract_json_ideas(self, ideas_data, file_path: Path, source_dir: str, priority: str):
        """Extract ideas from JSON ideas array."""
        if isinstance(ideas_data, list):
            for idea in ideas_data:
                if isinstance(idea, dict):
                    self._add_json_item(idea, file_path, "idea")
    
    def _extract_json_sessions(self, sessions_data, file_path: Path, source_dir: str, priority: str):
        """Extract sessions from JSON sessions array."""
        if isinstance(sessions_data, list):
            for session in sessions_data:
                if isinstance(session, dict):
                    self._add_json_item(session, file_path, "session")
    
    def _extract_json_array(self, array_data, file_path: Path, source_dir: str, priority: str):
        """Extract items from JSON array."""
        if isinstance(array_data, list):
            for item in array_data[:10]:  # Limit to first 10 items to avoid spam
                if isinstance(item, dict):
                    # Determine type based on content
                    if "workflow" in str(item).lower():
                        self._add_json_item(item, file_path, "workflow")
                    elif "command" in str(item).lower():
                        self._add_json_item(item, file_path, "command")
                    else:
                        self._add_json_item(item, file_path, "config")


def main():
    """Main execution function."""
    indexer = ComprehensiveIndexer()
    
    logger.info("🔍 Starting COMPREHENSIVE project scan...")
    items = indexer.scan_all_directories()
    
    logger.info("📝 Generating comprehensive reports...")
    indexer.save_comprehensive_index()
    
    logger.info("✅ Comprehensive indexing completed!")
    
    # Summary
    by_strategic = {}
    for item in items:
        by_strategic[item.strategic_value] = by_strategic.get(item.strategic_value, 0) + 1
    
    print("\n🎯 DISCOVERY SUMMARY:")
    print(f"   📊 Total Items: {len(items)}")
    print(f"   🚀 Revolutionary: {by_strategic.get('revolutionary', 0)}")
    print(f"   💎 High Value: {by_strategic.get('high', 0)}")
    print("   📄 Files Created: docs/COMPREHENSIVE_INDEX.json, docs/COMPREHENSIVE_ANALYSIS.md")


if __name__ == "__main__":
    main() 