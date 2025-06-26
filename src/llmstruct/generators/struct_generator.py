"""
struct/ Directory Generator for LLMStruct v2.1+

This module implements the StructDirectoryGenerator class that converts
flat JSON v2.1 format into the modular struct/ directory structure.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.uid_generator import generate_uid
from ..core.tag_inference import infer_tags


class StructDirectoryGenerator:
    """
    Generates modular struct/ directory from v2.1 JSON data.
    
    The struct/ format provides:
    - Rich index.json for O(1) lookups
    - Modular modules/*.json files
    - Call graph and schema validation
    - Better LLM integration and performance
    """
    
    def __init__(self, output_dir: Path, struct_data: Dict):
        """
        Initialize generator with output directory and v2.1 data.
        
        Args:
            output_dir: Base output directory (struct/ will be created inside)
            struct_data: Full v2.1 JSON structure data
        """
        self.output_dir = Path(output_dir)
        self.struct_dir = self.output_dir / "struct"
        self.struct_data = struct_data
        self.modules_dir = self.struct_dir / "modules"
        
        # Internal state
        self._module_index = {}
        self._call_graph = {}
        self._dependency_graph = {}
        
    def generate(self) -> None:
        """Generate complete struct/ directory from v2.1 data."""
        print(f"🚀 Generating struct/ directory at {self.struct_dir}")
        
        # Create directory structure
        self._create_directories()
        
        # Generate all components
        self._generate_modules()
        self._generate_index()
        self._generate_callgraph()
        self._generate_schema()
        self._generate_metadata()
        
        # Backward compatibility
        self._generate_legacy_struct()
        
        print(f"✅ struct/ generation complete: {len(self._module_index)} modules")
        
    def _create_directories(self) -> None:
        """Create struct/ directory structure."""
        self.struct_dir.mkdir(parents=True, exist_ok=True)
        self.modules_dir.mkdir(exist_ok=True)
        
    def _generate_modules(self) -> None:
        """Generate individual modules/*.json files and build index."""
        print("📁 Generating module files...")
        
        # Group functions and classes by module
        modules_data = self._group_by_module()
        
        for module_uid, module_data in modules_data.items():
            # Generate module file
            module_file = self.modules_dir / f"{module_uid}.json"
            
            # Build rich module data
            module_json = self._build_module_json(module_uid, module_data)
            
            # Write module file
            with open(module_file, 'w', encoding='utf-8') as f:
                json.dump(module_json, f, indent=2, ensure_ascii=False)
            
            # Add to index
            self._module_index[module_uid] = self._build_index_entry(module_uid, module_json)
            
        print(f"📁 Generated {len(modules_data)} module files")
        
    def _group_by_module(self) -> Dict[str, Dict]:
        """Group functions and classes by module UID."""
        modules = {}
        
        # Get functions and classes from modules array
        for module in self.struct_data.get('modules', []):
            module_uid = module.get('uid', 'unknown')
            if module_uid == 'unknown':
                # Generate UID from file path if missing
                file_path = module.get('file_path', '')
                if file_path:
                    # Clean up file path to create proper UID
                    module_uid = file_path.replace('/', '.').replace('.py', '')
                    if module_uid.startswith('src.llmstruct.'):
                        module_uid = module_uid[len('src.llmstruct.'):]
                    elif module_uid.startswith('src.'):
                        module_uid = module_uid[len('src.'):]
            
            # Clean up duplicate prefixes and suffixes in UID
            if '#' in module_uid:
                module_uid = module_uid.split('#')[0]
                
            # Remove duplicate parts like "llmstruct.api.app.llmstruct.api.app"
            parts = module_uid.split('.')
            if len(parts) > 3:
                # Check if second half duplicates first half
                mid = len(parts) // 2
                first_half = '.'.join(parts[:mid])
                second_half = '.'.join(parts[mid:])
                if first_half == second_half:
                    module_uid = first_half
                    
            modules[module_uid] = {
                'functions': module.get('functions', []),
                'classes': module.get('classes', []),
                'file_path': module.get('file_path', ''),
                'imports': module.get('imports', []),
                'calls': []
            }
            
            # Extract calls from functions (calls are already in the right format)
            for func in module.get('functions', []):
                modules[module_uid]['calls'].extend(func.get('calls', []))
            
        return modules
        
    def _build_module_json(self, module_uid: str, module_data: Dict) -> Dict:
        """Build complete module JSON structure."""
        file_path = module_data.get('file_path', '')
        
        # Extract module info
        functions = module_data.get('functions', [])
        classes = module_data.get('classes', [])
        
        # Calculate hash from file path and content
        content_hash = self._calculate_module_hash(functions, classes)
        
        # Infer tags for module
        module_code = f"# Module: {file_path}\n"
        if functions:
            module_code += f"# {len(functions)} functions\n"
        if classes:
            module_code += f"# {len(classes)} classes\n"
            
        tags = infer_tags(
            code=module_code,
            entity_type="module",
            entity_name=module_uid
        )
        
        # Build dependencies from function calls
        dependencies = self._extract_dependencies(functions, classes)
        
        # Generate summary
        summary = self._generate_module_summary(module_uid, functions, classes)
        
        # Extract exports (public functions/classes)
        exports = self._extract_exports(functions, classes)
        
        return {
            "module_info": {
                "uid": module_uid,
                "file_path": file_path,
                "tags": tags,
                "summary": summary,
                "hash": content_hash,
                "dependencies": dependencies,
                "exports": exports
            },
            "functions": functions,
            "classes": classes,
            "imports": module_data.get('imports', []),
            "calls": module_data.get('calls', []),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "2.1.0",
                "source_hash": content_hash,
                "lines_of_code": self._count_lines_of_code(functions, classes)
            }
        }
        
    def _build_index_entry(self, module_uid: str, module_json: Dict) -> Dict:
        """Build index entry for a module."""
        module_info = module_json['module_info']
        functions = module_json.get('functions', [])
        classes = module_json.get('classes', [])
        
        return {
            "uid": module_uid,
            "module_path": f"modules/{module_uid}.json",
            "file_path": module_info['file_path'],
            "tags": module_info['tags'],
            "summary": module_info['summary'],
            "hash": module_info['hash'],
            "functions_count": len(functions),
            "classes_count": len(classes),
            "lines_of_code": module_json['metadata']['lines_of_code'],
            "last_modified": module_json['metadata']['generated_at'],
            "dependencies": module_info['dependencies'],
            "dependents": [],  # Will be calculated in post-processing
            "complexity": self._calculate_complexity(functions, classes),
            "test_coverage": 0.0  # TODO: Calculate from test data
        }
        
    def _generate_index(self) -> None:
        """Generate rich index.json with O(1) lookup data."""
        print("📊 Generating index.json...")
        
        # Calculate dependents (reverse dependencies)
        self._calculate_dependents()
        
        # Build project info
        project_info = self._build_project_info()
        
        index_data = {
            "schema_version": "2.1.0",
            "generated_at": datetime.now().isoformat(),
            "project_info": project_info,
            "modules": list(self._module_index.values())
        }
        
        # Write index
        index_file = self.struct_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
            
        print(f"📊 Generated index with {len(self._module_index)} modules")
        
    def _generate_callgraph(self) -> None:
        """Generate global call relationships."""
        print("🔗 Generating callgraph.json...")
        
        # Build call graph from function calls
        call_graph = {
            "schema_version": "2.1.0",
            "generated_at": datetime.now().isoformat(),
            "calls": [],
            "statistics": {
                "total_calls": 0,
                "unique_callers": 0,
                "unique_callees": 0
            }
        }
        
        # Extract calls from all functions in modules
        all_calls = []
        callers = set()
        callees = set()
        
        for module in self.struct_data.get('modules', []):
            for func in module.get('functions', []):
                for call in func.get('calls', []):
                    # calls are strings like "module.function" or just "function"
                    if isinstance(call, str):
                        if '.' in call:
                            callee_module, callee_name = call.split('.', 1)
                        else:
                            callee_module = ''
                            callee_name = call
                            
                        call_entry = {
                            "caller_uid": func.get('uid', ''),
                            "caller_module": func.get('module_uid', module.get('uid', '')),
                            "callee_name": callee_name,
                            "callee_module": callee_module,
                            "call_type": "function",
                            "line_number": 0
                        }
                        all_calls.append(call_entry)
                        callers.add(func.get('uid', ''))
                        callees.add(callee_name)
                
        call_graph["calls"] = all_calls
        call_graph["statistics"] = {
            "total_calls": len(all_calls),
            "unique_callers": len(callers),
            "unique_callees": len(callees)
        }
        
        # Write call graph
        callgraph_file = self.struct_dir / "callgraph.json"
        with open(callgraph_file, 'w', encoding='utf-8') as f:
            json.dump(call_graph, f, indent=2, ensure_ascii=False)
            
        print(f"🔗 Generated call graph with {len(all_calls)} calls")
        
    def _generate_schema(self) -> None:
        """Generate JSON Schema for struct/ validation."""
        print("📋 Generating schema.json...")
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "LLMStruct v2.1 struct/ Directory Schema",
            "description": "Schema for validating LLMStruct modular structure",
            "type": "object",
            "definitions": {
                "module_info": {
                    "type": "object",
                    "properties": {
                        "uid": {"type": "string"},
                        "file_path": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"},
                        "hash": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "exports": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["uid", "file_path", "tags", "summary", "hash"]
                }
            }
        }
        
        # Write schema
        schema_file = self.struct_dir / "schema.json"
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            
        print("📋 Generated schema.json")
        
    def _generate_metadata(self) -> None:
        """Generate generation metadata and statistics."""
        print("📈 Generating metadata.json...")
        
        metadata = {
            "generation": {
                "timestamp": datetime.now().isoformat(),
                "generator_version": "2.1.0",
                "source_format": "v2.1",
                "target_format": "struct/"
            },
            "statistics": self._build_project_info(),
            "performance": {
                "generation_time_ms": 0,  # TODO: Track actual time
                "memory_usage_mb": 0,     # TODO: Track memory
                "file_count": len(self._module_index) + 5  # modules + index + callgraph + schema + metadata + struct.json
            }
        }
        
        # Write metadata
        metadata_file = self.struct_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        print("📈 Generated metadata.json")
        
    def _generate_legacy_struct(self) -> None:
        """Generate backward-compatible struct.json file."""
        print("🔄 Generating legacy struct.json for backward compatibility...")
        
        # Copy original struct data
        legacy_file = self.struct_dir / "struct.json"
        with open(legacy_file, 'w', encoding='utf-8') as f:
            json.dump(self.struct_data, f, indent=2, ensure_ascii=False)
            
        print("🔄 Generated legacy struct.json")
        
    # Helper methods
    
    def _calculate_module_hash(self, functions: List, classes: List) -> str:
        """Calculate hash for module content."""
        content = json.dumps({
            'functions': [f.get('uid', '') for f in functions],
            'classes': [c.get('uid', '') for c in classes]
        }, sort_keys=True)
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
        
    def _extract_dependencies(self, functions: List, classes: List) -> List[str]:
        """Extract module dependencies from function calls."""
        deps = set()
        
        for func in functions:
            for call in func.get('calls', []):
                # calls are strings like "module.function" or just "function"
                if isinstance(call, str) and '.' in call:
                    module = call.split('.')[0]
                    if module and module != 'builtin':
                        deps.add(module)
                        
        return sorted(list(deps))
        
    def _generate_module_summary(self, module_uid: str, functions: List, classes: List) -> str:
        """Generate human-readable module summary."""
        func_count = len(functions)
        class_count = len(classes)
        
        if func_count == 0 and class_count == 0:
            return f"Module {module_uid} (empty)"
        elif class_count == 0:
            return f"Module {module_uid} with {func_count} functions"
        elif func_count == 0:
            return f"Module {module_uid} with {class_count} classes"
        else:
            return f"Module {module_uid} with {func_count} functions and {class_count} classes"
            
    def _extract_exports(self, functions: List, classes: List) -> List[str]:
        """Extract public exports from functions and classes."""
        exports = []
        
        # Add public functions (not starting with _)
        for func in functions:
            name = func.get('name', '')
            if name and not name.startswith('_'):
                exports.append(name)
                
        # Add public classes
        for cls in classes:
            name = cls.get('name', '')
            if name and not name.startswith('_'):
                exports.append(name)
                
        return sorted(exports)
        
    def _count_lines_of_code(self, functions: List, classes: List) -> int:
        """Count total lines of code in module."""
        total_lines = 0
        
        for func in functions:
            total_lines += func.get('end_line', 0) - func.get('start_line', 0) + 1
            
        for cls in classes:
            total_lines += cls.get('end_line', 0) - cls.get('start_line', 0) + 1
            
        return max(total_lines, 0)
        
    def _calculate_complexity(self, functions: List, classes: List) -> str:
        """Calculate module complexity rating."""
        total_items = len(functions) + len(classes)
        
        if total_items <= 5:
            return "low"
        elif total_items <= 15:
            return "medium"
        else:
            return "high"
            
    def _calculate_dependents(self) -> None:
        """Calculate reverse dependencies for all modules."""
        # Build dependency map
        for module_uid, module_info in self._module_index.items():
            for dep in module_info.get('dependencies', []):
                if dep in self._module_index:
                    self._module_index[dep]['dependents'].append(module_uid)
                    
        # Remove duplicates and sort
        for module_info in self._module_index.values():
            module_info['dependents'] = sorted(list(set(module_info['dependents'])))
            
    def _build_project_info(self) -> Dict:
        """Build project-level statistics."""
        # Count functions and classes from modules
        total_functions = 0
        total_classes = 0
        
        for module in self.struct_data.get('modules', []):
            total_functions += len(module.get('functions', []))
            total_classes += len(module.get('classes', []))
            
        total_modules = len(self._module_index)
        
        # Calculate total lines
        total_lines = sum(
            module['lines_of_code'] 
            for module in self._module_index.values()
        )
        
        return {
            "name": "llmstruct",
            "version": "2.1.0",
            "total_modules": total_modules,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines": total_lines
        } 