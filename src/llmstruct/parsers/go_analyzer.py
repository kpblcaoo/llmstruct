#!/usr/bin/env python3
"""
Универсальный Go анализатор для Docker контейнера
Использует правильные подходы: go/packages, go/analysis
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GoAnalyzer:
    """Универсальный анализатор Go проектов"""
    
    def __init__(self):
        self.temp_dir = None
        self.analyzer_path = None
        
    def _setup_analyzer(self) -> None:
        """Настраивает временную среду для анализатора"""
        self.temp_dir = tempfile.mkdtemp()
        temp_path = Path(self.temp_dir)
        
        # Копируем готовый Go анализатор
        analyzer_source = Path(__file__).parent / "analyzer.go"
        analyzer_file = temp_path / "analyzer.go"
        analyzer_file.write_text(analyzer_source.read_text())
        
        # Создаем go.mod для анализатора
        go_mod_content = '''module go-analyzer

go 1.24

require (
    golang.org/x/tools v0.27.0
)

require (
    golang.org/x/mod v0.22.0 // indirect
    golang.org/x/sync v0.10.0 // indirect
)
'''
        
        # Также создаем go.mod для анализатора
        (temp_path / "go.mod").write_text(go_mod_content)
        
        # Загружаем зависимости заранее с отключенной проверкой контрольных сумм
        env = os.environ.copy()
        env['GOSUMDB'] = 'off'  # Отключаем проверку контрольных сумм
        env['GOPROXY'] = 'https://proxy.golang.org,direct'
        
        try:
            subprocess.run(['go', 'mod', 'download'], cwd=temp_path, check=True, capture_output=True, env=env)
        except subprocess.CalledProcessError:
            logging.warning("Failed to download Go modules, continuing anyway")
        
        self.analyzer_path = str(analyzer_file)
        
    def _cleanup(self) -> None:
        """Очищает временные файлы"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Анализирует Go проект"""
        try:
            self._setup_analyzer()
            
            logging.info(f"Analyzing Go project: {project_path}")
            
            # Настраиваем окружение для Go
            env = os.environ.copy()
            env['GOSUMDB'] = 'off'  # Отключаем проверку контрольных сумм
            env['GOPROXY'] = 'https://proxy.golang.org,direct'
            
            # Предварительно загружаем зависимости
            try:
                subprocess.run(['go', 'mod', 'tidy'], cwd=self.temp_dir, check=True, capture_output=True, env=env)
                subprocess.run(['go', 'mod', 'download'], cwd=self.temp_dir, check=True, capture_output=True, env=env)
            except subprocess.CalledProcessError as e:
                logging.warning(f"Failed to prepare Go modules: {e}")
            
            # Запускаем анализатор
            result = subprocess.run(
                ['go', 'run', 'analyzer.go', project_path],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=120,  # 2 минуты
                env=env
            )
            
            if result.returncode != 0:
                logging.error(f"Analyzer failed: {result.stderr}")
                return self._fallback_analysis(project_path)
            
            # Показываем отладочную информацию если есть
            if result.stderr:
                logging.info(f"Analyzer debug output: {result.stderr}")
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                logging.error("Failed to parse analyzer output")
                logging.error(f"Raw output: {result.stdout}")
                return self._fallback_analysis(project_path)
                
        except subprocess.TimeoutExpired:
            logging.error("Analyzer timed out")
            return self._fallback_analysis(project_path)
        except Exception as e:
            logging.error(f"Analyzer error: {e}")
            return self._fallback_analysis(project_path)
        finally:
            self._cleanup()
    
    def _fallback_analysis(self, project_path: str) -> Dict[str, Any]:
        """Fallback анализ через простой парсинг файлов"""
        logging.info("Using fallback analysis")
        
        result = {
            "module_name": "unknown",
            "go_version": "unknown", 
            "files": [],
            "dependencies": [],
            "all_packages": [],
            "test_files": [],
            "total_lines": 0,
            "has_go_mod": False,
            "errors": ["Fallback analysis used - limited functionality"]
        }
        
        # Простой анализ go.mod
        go_mod_path = Path(project_path) / "go.mod"
        if go_mod_path.exists():
            result["has_go_mod"] = True
            try:
                content = go_mod_path.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('module '):
                        result["module_name"] = line.split()[1]
                    elif line.startswith('go '):
                        result["go_version"] = line.split()[1]
            except Exception:
                pass
        
        # Простой анализ файлов
        go_files = list(Path(project_path).rglob("*.go"))
        packages = set()
        
        for file_path in go_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                result["total_lines"] += len(lines)
                
                # Извлекаем имя пакета
                package_name = "main"
                for line in lines:
                    if line.strip().startswith('package '):
                        package_name = line.strip().split()[1]
                        packages.add(package_name)
                        break
                
                rel_path = str(file_path.relative_to(project_path))
                is_test = file_path.name.endswith("_test.go")
                
                file_analysis = {
                    "path": rel_path,
                    "package": package_name,
                    "imports": [],
                    "functions": [],
                    "structs": [],
                    "variables": [],
                    "constants": [],
                    "interfaces": [],
                    "line_count": len(lines),
                    "has_tests": is_test
                }
                
                result["files"].append(file_analysis)
                
                if is_test:
                    result["test_files"].append(rel_path)
                    
            except Exception as e:
                logging.warning(f"Failed to analyze {file_path}: {e}")
        
        result["all_packages"] = sorted(list(packages))
        return result

def convert_to_llmstruct_format(analysis: Dict[str, Any], include_ranges: bool = False, goals: List[str] = None) -> Dict[str, Any]:
    """Конвертирует результат анализа в формат llmstruct"""
    
    modules = []
    toc = []
    
    for file_data in analysis.get("files", []):
        # Преобразуем функции
        functions = []
        for fn in file_data.get("functions", []):
            functions.append({
                "name": fn["name"],
                "docstring": fn.get("docstring", ""),
                "line_range": [fn["line"], fn.get("end_line", fn["line"])] if include_ranges else None,
                "parameters": fn.get("params", []),
                "returns": fn.get("returns", []),
                "receiver": fn.get("receiver", ""),
                "is_exported": fn.get("is_exported", False),
                "is_method": fn.get("is_method", False),
            })
        
        # Преобразуем структуры
        classes = []
        for struct in file_data.get("structs", []):
            classes.append({
                "name": struct["name"],
                "docstring": struct.get("docstring", ""),
                "line_range": [struct["line"], struct.get("end_line", struct["line"])] if include_ranges else None,
                "fields": struct.get("fields", []),
                "methods": struct.get("methods", []),
                "is_exported": struct.get("is_exported", False),
            })
        
        # Добавляем интерфейсы как классы
        for iface in file_data.get("interfaces", []):
            classes.append({
                "name": iface["name"],
                "docstring": iface.get("docstring", ""),
                "line_range": [iface["line"], iface.get("end_line", iface["line"])] if include_ranges else None,
                "fields": iface.get("fields", []),
                "methods": iface.get("methods", []),
                "is_exported": iface.get("is_exported", False),
                "is_interface": True,
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
            "hash": _compute_file_hash(path) if include_ranges else None,
            "artifact_id": str(uuid.uuid4()),
            "line_count": file_data.get("line_count", 0),
            "has_tests": file_data.get("has_tests", False),
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
            "version": datetime.datetime.utcnow().isoformat() + "Z",
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

def _compute_file_hash(file_path: str) -> str:
    """Вычисляет SHA-256 хэш файла"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""

def main():
    parser = argparse.ArgumentParser(description='Universal Go Project Analyzer')
    parser.add_argument('project_path', help='Path to Go project directory')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--include-ranges', action='store_true', help='Include line ranges')
    parser.add_argument('--goals', nargs='*', help='Project goals', default=[])
    
    args = parser.parse_args()
    
    if not Path(args.project_path).exists():
        print(f"❌ Error: Project path {args.project_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 Analyzing Go project: {args.project_path}")
    
    try:
        analyzer = GoAnalyzer()
        analysis_result = analyzer.analyze_project(args.project_path)
        
        if not analysis_result:
            print("❌ Analysis failed", file=sys.stderr)
            sys.exit(1)
        
        # Конвертируем в формат llmstruct
        result = convert_to_llmstruct_format(
            analysis_result,
            include_ranges=args.include_ranges,
            goals=args.goals
        )
        
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"✅ Output written to {args.output}")
            
            stats = result.get('metadata', {}).get('stats', {})
            print(f"📊 Statistics:")
            print(f"   - Modules: {stats.get('modules_count', 0)}")
            print(f"   - Functions: {stats.get('functions_count', 0)}")
            print(f"   - Structs: {stats.get('structs_count', 0)}")
            print(f"   - Packages: {stats.get('packages_count', 0)}")
            print(f"   - Total Lines: {stats.get('total_lines', 0)}")
            print(f"   - Test Files: {stats.get('test_files_count', 0)}")
            
            if result.get('metadata', {}).get('analysis_errors'):
                print(f"⚠️  Warnings: {len(result['metadata']['analysis_errors'])} issues")
        else:
            print(json_output)
            
    except Exception as e:
        print(f"❌ Error analyzing project: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    import sys
    main() 