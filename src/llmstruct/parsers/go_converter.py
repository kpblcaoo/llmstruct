"""
Go to LLMStruct Converter

Utilities for converting Go analysis results to llmstruct JSON format.
"""

import datetime
import hashlib
import uuid
from typing import Dict, Any, List, Optional

# Phase 1.5: unified tag inference
from llmstruct.core.tag_inference import infer_tags


def convert_to_llmstruct_format(analysis: Dict[str, Any], include_ranges: bool = False, goals: List[str] = None) -> Dict[str, Any]:
    """Конвертирует результат анализа в формат llmstruct"""
    
    modules = []
    toc = []
    
    for file_data in analysis.get("files", []):
        # Преобразуем функции
        functions = []
        for fn in file_data.get("functions", []):
            func_tags = infer_tags(code="", entity_type="function", entity_name=fn["name"])
            functions.append({
                "name": fn["name"],
                "docstring": fn.get("docstring", ""),
                "line_range": [fn["line"], fn.get("end_line", fn["line"])] if include_ranges else None,
                "parameters": fn.get("params", []),
                "returns": fn.get("returns", []),
                "receiver": fn.get("receiver", ""),
                "is_exported": fn.get("is_exported", False),
                "is_method": fn.get("is_method", False),
                "tags": func_tags,
            })
        
        # Преобразуем структуры
        classes = []
        for struct in file_data.get("structs", []):
            class_tags = infer_tags(code="", entity_type="class", entity_name=struct["name"])
            classes.append({
                "name": struct["name"],
                "docstring": struct.get("docstring", ""),
                "line_range": [struct["line"], struct.get("end_line", struct["line"])] if include_ranges else None,
                "fields": struct.get("fields", []),
                "methods": struct.get("methods", []),
                "is_exported": struct.get("is_exported", False),
                "tags": class_tags,
            })
        
        # Добавляем интерфейсы как классы
        for iface in file_data.get("interfaces", []):
            iface_tags = infer_tags(code="", entity_type="class", entity_name=iface["name"])
            classes.append({
                "name": iface["name"],
                "docstring": iface.get("docstring", ""),
                "line_range": [iface["line"], iface.get("end_line", iface["line"])] if include_ranges else None,
                "fields": iface.get("fields", []),
                "methods": iface.get("methods", []),
                "is_exported": iface.get("is_exported", False),
                "is_interface": True,
                "tags": iface_tags,
            })
        
        # Зависимости из импортов
        dependencies = [imp["path"] for imp in file_data.get("imports", [])]
        
        # Простой callgraph
        callgraph = {}
        for fn in functions:
            callgraph[fn["name"]] = []
        
        # Определяем категорию
        path = file_data["path"]
        category = "core"
        if "test" in path or path.endswith("_test.go"):
            category = "test"
        elif "cmd" in path or "main.go" in path:
            category = "cli"
        elif "internal" in path:
            category = "internal"
        
        module_id = path.replace("/", ".").replace("\\", ".").replace(".go", "")
        
        module_tags = infer_tags(code="", entity_type="module", entity_name=module_id)
        module = {
            "module_id": module_id,
            "path": path,
            "category": category,
            "package": file_data.get("package", "unknown"),
            "module_doc": "",
            "functions": functions,
            "classes": classes,
            "callgraph": callgraph,
            "dependencies": dependencies,
            "hash": compute_file_hash(path) if include_ranges else None,
            "artifact_id": str(uuid.uuid4()),
            "line_count": file_data.get("line_count", 0),
            "has_tests": file_data.get("has_tests", False),
            "tags": module_tags,
        }
        
        modules.append(module)
        toc.append({
            "module_id": module["module_id"],
            "path": module["path"],
            "category": module["category"],
            "package": module.get("package", "unknown"),
            "functions": len(module["functions"]),
            "structs": len(module["classes"]),
            "summary": "",
            "artifact_id": module["artifact_id"],
        })
    
    # Статистика
    stats = {
        "modules_count": len(modules),
        "functions_count": sum(len(m["functions"]) for m in modules),
        "structs_count": sum(len(m["classes"]) for m in modules),
        "packages_count": len(analysis.get("all_packages", [])),
        "call_edges_count": 0,
        "total_lines": analysis.get("total_lines", 0),
        "test_files_count": len(analysis.get("test_files", [])),
    }
    
    project_name = analysis.get("module_name", "go-project")
    
    return {
        "metadata": {
            "project_name": project_name,
            "description": f"Go project analysis for {project_name}",
            "version": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "language": "go",
            "go_version": analysis.get("go_version", "unknown"),
            "authors": [{"name": "Go Project Author", "tool": "llmstruct-go-analyzer"}],
            "instructions": [
                "Follow Go best practices and conventions",
                "Preserve functionality, ensure idempotency",
                "Use attached struct.json for context and navigation",
            ],
            "goals": goals or [],
            "stats": stats,
            "go_mod_info": {
                "module_name": analysis.get("module_name", ""),
                "go_version": analysis.get("go_version", ""),
                "has_go_mod": analysis.get("has_go_mod", False),
                "dependencies": analysis.get("dependencies", []),
            },
            "artifact_id": str(uuid.uuid4()),
            "summary": f"Structured JSON for Go project {project_name}",
            "tags": ["codebase", "golang", "automation"],
            "analysis_errors": analysis.get("errors", []),
        },
        "toc": toc,
        "modules": modules,
    }


def compute_file_hash(file_path: str) -> str:
    """Вычисляет SHA-256 хэш файла"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "" 