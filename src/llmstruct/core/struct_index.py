"""
Fast Index and Lookup System for struct/ Directory

This module provides the StructIndex class for high-performance
querying of the modular struct/ structure with O(1) lookups.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ModuleInfo:
    """Structured module information for fast access."""
    uid: str
    module_path: str
    file_path: str
    tags: List[str]
    summary: str
    hash: str
    functions_count: int
    classes_count: int
    lines_of_code: int
    last_modified: str
    dependencies: List[str]
    dependents: List[str]
    complexity: str
    test_coverage: float
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModuleInfo':
        """Create ModuleInfo from index entry."""
        return cls(
            uid=data.get('uid', ''),
            module_path=data.get('module_path', ''),
            file_path=data.get('file_path', ''),
            tags=data.get('tags', []),
            summary=data.get('summary', ''),
            hash=data.get('hash', ''),
            functions_count=data.get('functions_count', 0),
            classes_count=data.get('classes_count', 0),
            lines_of_code=data.get('lines_of_code', 0),
            last_modified=data.get('last_modified', ''),
            dependencies=data.get('dependencies', []),
            dependents=data.get('dependents', []),
            complexity=data.get('complexity', 'unknown'),
            test_coverage=data.get('test_coverage', 0.0)
        )


class StructIndex:
    """
    High-performance index for struct/ directory structure.
    
    Provides O(1) lookups by UID and fast filtering by tags,
    dependencies, and other criteria.
    """
    
    def __init__(self, struct_dir: Path):
        """
        Initialize index from struct/ directory.
        
        Args:
            struct_dir: Path to struct/ directory containing index.json
        """
        self.struct_dir = Path(struct_dir)
        self.index_file = self.struct_dir / "index.json"
        
        # Load and parse index
        self.index_data = self._load_index()
        self.project_info = self.index_data.get('project_info', {})
        
        # Build lookup tables for O(1) access
        self._uid_map: Dict[str, ModuleInfo] = {}
        self._tag_map: Dict[str, Set[str]] = defaultdict(set)
        self._dependency_map: Dict[str, Set[str]] = defaultdict(set)
        self._dependent_map: Dict[str, Set[str]] = defaultdict(set)
        self._file_map: Dict[str, str] = {}
        
        self._build_lookup_tables()
        
    def _load_index(self) -> Dict:
        """Load index.json file."""
        if not self.index_file.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_file}")
            
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Failed to load index file: {e}")
            
    def _build_lookup_tables(self) -> None:
        """Build internal lookup tables for fast access."""
        modules = self.index_data.get('modules', [])
        
        for module_data in modules:
            module_info = ModuleInfo.from_dict(module_data)
            uid = module_info.uid
            
            # UID lookup
            self._uid_map[uid] = module_info
            
            # Tag lookup
            for tag in module_info.tags:
                self._tag_map[tag].add(uid)
                
            # Dependency lookup
            for dep in module_info.dependencies:
                self._dependency_map[uid].add(dep)
                
            # Dependent lookup
            for dependent in module_info.dependents:
                self._dependent_map[uid].add(dependent)
                
            # File path lookup
            self._file_map[module_info.file_path] = uid
            
    # Core lookup methods
    
    def find_by_uid(self, uid: str) -> Optional[ModuleInfo]:
        """
        Find module by UID with O(1) lookup.
        
        Args:
            uid: Module UID to find
            
        Returns:
            ModuleInfo if found, None otherwise
        """
        return self._uid_map.get(uid)
        
    def find_by_file_path(self, file_path: str) -> Optional[ModuleInfo]:
        """
        Find module by file path.
        
        Args:
            file_path: File path to find
            
        Returns:
            ModuleInfo if found, None otherwise
        """
        uid = self._file_map.get(file_path)
        return self._uid_map.get(uid) if uid else None
        
    def find_by_tags(self, tags: List[str], match_all: bool = True) -> List[ModuleInfo]:
        """
        Find modules matching tags.
        
        Args:
            tags: List of tags to match
            match_all: If True, match all tags (AND). If False, match any tag (OR)
            
        Returns:
            List of matching ModuleInfo objects
        """
        if not tags:
            return list(self._uid_map.values())
            
        if match_all:
            # Intersection of all tag sets
            matching_uids = set(self._uid_map.keys())
            for tag in tags:
                matching_uids &= self._tag_map.get(tag, set())
        else:
            # Union of all tag sets
            matching_uids = set()
            for tag in tags:
                matching_uids |= self._tag_map.get(tag, set())
                
        return [self._uid_map[uid] for uid in matching_uids if uid in self._uid_map]
        
    def find_by_complexity(self, complexity: str) -> List[ModuleInfo]:
        """
        Find modules by complexity level.
        
        Args:
            complexity: Complexity level ('low', 'medium', 'high')
            
        Returns:
            List of matching ModuleInfo objects
        """
        return [
            module for module in self._uid_map.values()
            if module.complexity == complexity
        ]
        
    def find_by_size(self, min_lines: int = 0, max_lines: int = float('inf')) -> List[ModuleInfo]:
        """
        Find modules by size (lines of code).
        
        Args:
            min_lines: Minimum lines of code
            max_lines: Maximum lines of code
            
        Returns:
            List of matching ModuleInfo objects
        """
        return [
            module for module in self._uid_map.values()
            if min_lines <= module.lines_of_code <= max_lines
        ]
        
    # Dependency methods
    
    def get_dependencies(self, uid: str) -> List[ModuleInfo]:
        """
        Get all direct dependencies of a module.
        
        Args:
            uid: Module UID
            
        Returns:
            List of dependency ModuleInfo objects
        """
        dep_uids = self._dependency_map.get(uid, set())
        return [self._uid_map[dep_uid] for dep_uid in dep_uids if dep_uid in self._uid_map]
        
    def get_dependents(self, uid: str) -> List[ModuleInfo]:
        """
        Get all modules that depend on this module.
        
        Args:
            uid: Module UID
            
        Returns:
            List of dependent ModuleInfo objects
        """
        dependent_uids = self._dependent_map.get(uid, set())
        return [self._uid_map[dep_uid] for dep_uid in dependent_uids if dep_uid in self._uid_map]
        
    def get_dependency_tree(self, uid: str, max_depth: int = 10) -> Dict[str, Any]:
        """
        Get full dependency tree for a module.
        
        Args:
            uid: Root module UID
            max_depth: Maximum recursion depth
            
        Returns:
            Nested dictionary representing dependency tree
        """
        visited = set()
        
        def _build_tree(current_uid: str, depth: int) -> Dict[str, Any]:
            if depth >= max_depth or current_uid in visited:
                return {"uid": current_uid, "dependencies": []}
                
            visited.add(current_uid)
            
            deps = self.get_dependencies(current_uid)
            return {
                "uid": current_uid,
                "dependencies": [
                    _build_tree(dep.uid, depth + 1) for dep in deps
                ]
            }
            
        return _build_tree(uid, 0)
        
    def get_impact_analysis(self, uid: str) -> Dict[str, Any]:
        """
        Analyze impact of changes to a module.
        
        Args:
            uid: Module UID to analyze
            
        Returns:
            Impact analysis data
        """
        module = self.find_by_uid(uid)
        if not module:
            return {"error": f"Module {uid} not found"}
            
        dependents = self.get_dependents(uid)
        
        # Calculate impact score based on dependents
        impact_score = len(dependents)
        if impact_score == 0:
            impact_level = "low"
        elif impact_score <= 5:
            impact_level = "medium"
        else:
            impact_level = "high"
            
        return {
            "module": module.uid,
            "direct_dependents": len(dependents),
            "impact_level": impact_level,
            "affected_modules": [dep.uid for dep in dependents],
            "tags": module.tags,
            "complexity": module.complexity
        }
        
    # Search and filter methods
    
    def search(self, query: str, fields: List[str] = None) -> List[ModuleInfo]:
        """
        Search modules by text query in specified fields.
        
        Args:
            query: Search query string
            fields: Fields to search in ['uid', 'summary', 'file_path', 'tags']
            
        Returns:
            List of matching ModuleInfo objects
        """
        if fields is None:
            fields = ['uid', 'summary', 'file_path']
            
        query_lower = query.lower()
        results = []
        
        for module in self._uid_map.values():
            match = False
            
            if 'uid' in fields and query_lower in module.uid.lower():
                match = True
            elif 'summary' in fields and query_lower in module.summary.lower():
                match = True
            elif 'file_path' in fields and query_lower in module.file_path.lower():
                match = True
            elif 'tags' in fields and any(query_lower in tag.lower() for tag in module.tags):
                match = True
                
            if match:
                results.append(module)
                
        return results
        
    def filter_modules(self, **criteria) -> List[ModuleInfo]:
        """
        Filter modules by multiple criteria.
        
        Args:
            **criteria: Filter criteria (tags, complexity, min_lines, max_lines, etc.)
            
        Returns:
            List of matching ModuleInfo objects
        """
        results = list(self._uid_map.values())
        
        if 'tags' in criteria:
            tags = criteria['tags']
            match_all = criteria.get('match_all_tags', True)
            results = [m for m in results if m in self.find_by_tags(tags, match_all)]
            
        if 'complexity' in criteria:
            results = [m for m in results if m.complexity == criteria['complexity']]
            
        if 'min_lines' in criteria:
            results = [m for m in results if m.lines_of_code >= criteria['min_lines']]
            
        if 'max_lines' in criteria:
            results = [m for m in results if m.lines_of_code <= criteria['max_lines']]
            
        if 'min_functions' in criteria:
            results = [m for m in results if m.functions_count >= criteria['min_functions']]
            
        if 'max_functions' in criteria:
            results = [m for m in results if m.functions_count <= criteria['max_functions']]
            
        return results
        
    # Statistics and analysis
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the codebase."""
        modules = list(self._uid_map.values())
        
        if not modules:
            return {"error": "No modules found"}
            
        # Basic stats
        total_modules = len(modules)
        total_functions = sum(m.functions_count for m in modules)
        total_classes = sum(m.classes_count for m in modules)
        total_lines = sum(m.lines_of_code for m in modules)
        
        # Complexity distribution
        complexity_dist = defaultdict(int)
        for module in modules:
            complexity_dist[module.complexity] += 1
            
        # Tag distribution
        tag_dist = defaultdict(int)
        for module in modules:
            for tag in module.tags:
                tag_dist[tag] += 1
                
        # Size distribution
        size_ranges = {
            "small": (0, 100),
            "medium": (100, 500),
            "large": (500, 1000),
            "extra_large": (1000, float('inf'))
        }
        
        size_dist = defaultdict(int)
        for module in modules:
            for size_name, (min_size, max_size) in size_ranges.items():
                if min_size <= module.lines_of_code < max_size:
                    size_dist[size_name] += 1
                    break
                    
        return {
            "totals": {
                "modules": total_modules,
                "functions": total_functions,
                "classes": total_classes,
                "lines_of_code": total_lines
            },
            "distributions": {
                "complexity": dict(complexity_dist),
                "tags": dict(tag_dist),
                "size": dict(size_dist)
            },
            "averages": {
                "functions_per_module": total_functions / total_modules if total_modules > 0 else 0,
                "classes_per_module": total_classes / total_modules if total_modules > 0 else 0,
                "lines_per_module": total_lines / total_modules if total_modules > 0 else 0
            }
        }
        
    def get_module_details(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Load full module details from modules/*.json file.
        
        Args:
            uid: Module UID
            
        Returns:
            Full module data or None if not found
        """
        module_info = self.find_by_uid(uid)
        if not module_info:
            return None
            
        module_file = self.struct_dir / module_info.module_path
        if not module_file.exists():
            return None
            
        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
            
    # Utility methods
    
    def list_all_uids(self) -> List[str]:
        """Get list of all module UIDs."""
        return list(self._uid_map.keys())
        
    def list_all_tags(self) -> List[str]:
        """Get list of all unique tags."""
        return list(self._tag_map.keys())
        
    def validate_index(self) -> Dict[str, Any]:
        """Validate index integrity."""
        issues = []
        
        # Check for missing module files
        for uid, module_info in self._uid_map.items():
            module_file = self.struct_dir / module_info.module_path
            if not module_file.exists():
                issues.append(f"Missing module file: {module_info.module_path}")
                
        # Check dependency consistency
        for uid, deps in self._dependency_map.items():
            for dep in deps:
                if dep not in self._uid_map:
                    issues.append(f"Module {uid} depends on unknown module: {dep}")
                    
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_modules": len(self._uid_map),
            "total_dependencies": sum(len(deps) for deps in self._dependency_map.values())
        } 