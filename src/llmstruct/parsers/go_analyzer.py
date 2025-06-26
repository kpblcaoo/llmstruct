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

if __name__ == "__main__":
    import argparse
    import sys
    import json
    from .go_converter import convert_to_llmstruct_format
    
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