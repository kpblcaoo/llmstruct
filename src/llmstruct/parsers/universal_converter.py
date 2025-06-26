#!/usr/bin/env python3
"""
Universal Code Converter - Orchestrates all language parsers
Converts any codebase to llmstruct JSON format
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from .python_parser import analyze_module as analyze_python
    from .go_analyzer import GoAnalyzer
    from .javascript_parser import JavaScriptParser
    from .converter_config import Language, ConverterConfig, LanguageDetector
except ImportError:
    # Fallback for standalone execution
    from python_parser import analyze_module as analyze_python
    from go_analyzer import GoAnalyzer
    from javascript_parser import JavaScriptParser
    from converter_config import Language, ConverterConfig, LanguageDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalConverter:
    """Universal code converter for any programming language"""
    
    def __init__(self, config: ConverterConfig = None):
        self.config = config or ConverterConfig()
        self.go_analyzer = GoAnalyzer()
        self.js_parser = JavaScriptParser()
        
    def detect_language(self, file_path: str) -> Language:
        """Detect programming language from file extension"""
        return LanguageDetector.detect_language(file_path)
    
    def detect_project_languages(self, project_path: str) -> Dict[Language, int]:
        """Detect all languages in project and count files"""
        return LanguageDetector.detect_project_languages(project_path, self.config.exclude_patterns)
    
    def get_project_files(self, project_path: str, language: Language = None) -> List[str]:
        """Get all relevant files for conversion"""
        files = []
        
        for root, dirs, filenames in os.walk(project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.config.exclude_patterns)]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # Skip large files
                try:
                    if os.path.getsize(file_path) > self.config.max_file_size:
                        continue
                except OSError:
                    continue
                
                file_lang = self.detect_language(file_path)
                
                # Filter by language if specified
                if language and file_lang != language:
                    continue
                    
                if file_lang != Language.UNKNOWN:
                    files.append(file_path)
                    
        return files
    
    def convert_python_project(self, project_path: str) -> Dict[str, Any]:
        """Convert Python project to llmstruct format"""
        logger.info("Converting Python project...")
        
        files = self.get_project_files(project_path, Language.PYTHON)
        modules = []
        toc = []
        
        for file_path in files:
            try:
                module_data = analyze_python(
                    file_path, 
                    project_path, 
                    self.config.include_ranges, 
                    self.config.include_hashes
                )
                
                if module_data:
                    modules.append(module_data)
                    toc.append({
                        "module_id": module_data["module_id"],
                        "path": module_data["path"],
                        "category": module_data["category"],
                        "functions": len(module_data.get("functions", [])),
                        "classes": len(module_data.get("classes", [])),
                        "summary": module_data.get("module_doc", "")[:100],
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return self._build_project_structure("python", project_path, modules, toc)
    
    def convert_go_project(self, project_path: str) -> Dict[str, Any]:
        """Convert Go project to llmstruct format"""
        logger.info("Converting Go project...")
        
        try:
            analysis = self.go_analyzer.analyze_project(project_path)
            
            # Use the existing convert_to_llmstruct_format from go_converter
            from .go_converter import convert_to_llmstruct_format
            return convert_to_llmstruct_format(
                analysis, 
                self.config.include_ranges, 
                self.config.goals
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze Go project: {e}")
            return self._build_empty_project_structure("go", project_path, str(e))
    
    def convert_javascript_project(self, project_path: str) -> Dict[str, Any]:
        """Convert JavaScript project to llmstruct format"""
        logger.info("Converting JavaScript project...")
        
        files = self.get_project_files(project_path, Language.JAVASCRIPT)
        modules = []
        toc = []
        
        for file_path in files:
            try:
                module_data = self.js_parser.parse_module(
                    file_path, 
                    project_path, 
                    self.config.include_ranges, 
                    self.config.include_hashes
                )
                
                if module_data and "error" not in module_data:
                    modules.append(module_data)
                    toc.append({
                        "module_id": module_data["path"].replace("/", ".").replace(".js", ""),
                        "path": module_data["path"],
                        "category": module_data.get("category", "core"),
                        "functions": len(module_data.get("functions", [])),
                        "classes": len(module_data.get("classes", [])),
                        "summary": module_data.get("module_doc", "")[:100] if module_data.get("module_doc") else "",
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return self._build_project_structure("javascript", project_path, modules, toc)
    
    def convert_project(self, project_path: str, language: Language = None) -> Dict[str, Any]:
        """Convert any project to llmstruct format"""
        project_path = os.path.abspath(project_path)
        
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # Auto-detect primary language if not specified
        if language is None:
            languages = self.detect_project_languages(project_path)
            if not languages:
                raise ValueError("No supported programming languages found in project")
            
            # Use the language with most files
            language = max(languages.keys(), key=lambda k: languages[k])
            logger.info(f"Auto-detected primary language: {language.value}")
        
        # Convert based on language
        if language == Language.PYTHON:
            return self.convert_python_project(project_path)
        elif language == Language.GO:
            return self.convert_go_project(project_path)
        elif language == Language.JAVASCRIPT:
            return self.convert_javascript_project(project_path)
        else:
            raise NotImplementedError(f"Language {language.value} not yet supported")
    
    def convert_multi_language_project(self, project_path: str) -> Dict[str, Any]:
        """Convert multi-language project with separate sections per language"""
        project_path = os.path.abspath(project_path)
        languages = self.detect_project_languages(project_path)
        
        if not languages:
            raise ValueError("No supported programming languages found")
        
        logger.info(f"Found languages: {[lang.value for lang in languages.keys()]}")
        
        # Convert each language separately
        language_results = {}
        for language in languages.keys():
            try:
                if language == Language.PYTHON:
                    result = self.convert_python_project(project_path)
                elif language == Language.GO:
                    result = self.convert_go_project(project_path)
                elif language == Language.JAVASCRIPT:
                    result = self.convert_javascript_project(project_path)
                else:
                    logger.warning(f"Skipping unsupported language: {language.value}")
                    continue
                    
                language_results[language.value] = result
                
            except Exception as e:
                logger.error(f"Failed to convert {language.value}: {e}")
        
        # Merge results
        return self._merge_language_results(project_path, language_results)
    
    def _build_project_structure(self, language: str, project_path: str, modules: List[Dict], toc: List[Dict]) -> Dict[str, Any]:
        """Build standard llmstruct project structure"""
        project_name = os.path.basename(project_path)
        
        stats = {
            "modules_count": len(modules),
            "functions_count": sum(len(m.get("functions", [])) for m in modules),
            "classes_count": sum(len(m.get("classes", [])) for m in modules),
            "total_lines": sum(m.get("line_count", 0) for m in modules),
        }
        
        return {
            "metadata": {
                "project_name": project_name,
                "description": f"{language.title()} project analysis for {project_name}",
                "language": language,
                "version": "1.0.0",
                "authors": [{"name": "Universal Converter", "tool": "llmstruct-universal-converter"}],
                "goals": self.config.goals,
                "stats": stats,
                "converter_config": {
                    "include_ranges": self.config.include_ranges,
                    "include_hashes": self.config.include_hashes,
                    "include_tests": self.config.include_tests,
                },
            },
            "toc": toc,
            "modules": modules,
        }
    
    def _build_empty_project_structure(self, language: str, project_path: str, error: str) -> Dict[str, Any]:
        """Build empty structure when conversion fails"""
        project_name = os.path.basename(project_path)
        
        return {
            "metadata": {
                "project_name": project_name,
                "description": f"Failed {language} project analysis",
                "language": language,
                "version": "1.0.0",
                "error": error,
                "stats": {"modules_count": 0, "functions_count": 0, "classes_count": 0},
            },
            "toc": [],
            "modules": [],
        }
    
    def _merge_language_results(self, project_path: str, language_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Merge multiple language results into unified structure"""
        project_name = os.path.basename(project_path)
        
        all_modules = []
        all_toc = []
        combined_stats = {"modules_count": 0, "functions_count": 0, "classes_count": 0, "total_lines": 0}
        
        for language, result in language_results.items():
            # Prefix module IDs with language
            for module in result.get("modules", []):
                module["module_id"] = f"{language}.{module['module_id']}"
                module["language"] = language
                all_modules.append(module)
            
            for toc_entry in result.get("toc", []):
                toc_entry["module_id"] = f"{language}.{toc_entry['module_id']}"
                toc_entry["language"] = language
                all_toc.append(toc_entry)
            
            # Combine stats
            stats = result.get("metadata", {}).get("stats", {})
            for key in combined_stats:
                combined_stats[key] += stats.get(key, 0)
        
        return {
            "metadata": {
                "project_name": project_name,
                "description": f"Multi-language project analysis for {project_name}",
                "languages": list(language_results.keys()),
                "version": "1.0.0",
                "authors": [{"name": "Universal Converter", "tool": "llmstruct-universal-converter"}],
                "goals": self.config.goals,
                "stats": combined_stats,
                "language_breakdown": {
                    lang: result.get("metadata", {}).get("stats", {})
                    for lang, result in language_results.items()
                },
            },
            "toc": all_toc,
            "modules": all_modules,
        }


def main():
    """CLI interface for universal converter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Code Converter")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--language", "-l", choices=[lang.value for lang in Language], 
                       help="Force specific language (auto-detect if not specified)")
    parser.add_argument("--multi-language", action="store_true", 
                       help="Convert as multi-language project")
    parser.add_argument("--no-ranges", action="store_true", help="Exclude line ranges")
    parser.add_argument("--no-hashes", action="store_true", help="Exclude file hashes")
    parser.add_argument("--goals", nargs="*", help="Project goals", default=[])
    
    args = parser.parse_args()
    
    # Build config
    config = ConverterConfig(
        include_ranges=not args.no_ranges,
        include_hashes=not args.no_hashes,
        goals=args.goals or []
    )
    
    converter = UniversalConverter(config)
    
    try:
        if args.multi_language:
            result = converter.convert_multi_language_project(args.project_path)
        else:
            language = Language(args.language) if args.language else None
            result = converter.convert_project(args.project_path, language)
        
        # Output result
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"✅ Converted to {args.output}")
            
            # Print stats
            stats = result.get("metadata", {}).get("stats", {})
            print(f"📊 Stats: {stats.get('modules_count', 0)} modules, "
                  f"{stats.get('functions_count', 0)} functions, "
                  f"{stats.get('classes_count', 0)} classes")
        else:
            print(json_output)
            
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main() 