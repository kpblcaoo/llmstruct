#!/usr/bin/env python3
"""
AI-Powered Universal Transpiler
Converts entire codebases from one language to another using LLM analysis
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .parsers.universal_converter import UniversalConverter, Language, ConverterConfig
from .llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TranspilerConfig:
    """Configuration for AI transpiler"""
    source_language: Language
    target_language: Language
    output_dir: str
    preserve_structure: bool = True
    include_tests: bool = True
    include_docs: bool = True
    chunk_size: int = 5  # Process N modules at once
    model_name: str = "grok-beta"  # or "claude-3-5-sonnet-20241022"
    temperature: float = 0.1
    max_tokens: int = 4000


class LanguageTemplates:
    """Templates and patterns for different target languages"""
    
    GO_PROJECT_TEMPLATE = {
        "go.mod": """module {module_name}

go 1.21

require (
    // Add dependencies as needed
)
""",
        "main.go": """package main

import (
    "fmt"
    "log"
)

func main() {{
    fmt.Println("Generated Go project from {source_language}")
    // TODO: Implement main functionality
}}
""",
        "README.md": """# {project_name} (Go)

This project was automatically transpiled from {source_language} to Go using llmstruct AI transpiler.

## Structure

{structure_info}

## Build & Run

```bash
go mod tidy
go build
./{project_name}
```

## Testing

```bash
go test ./...
```
""",
        ".gitignore": """# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool
*.out

# Dependency directories
vendor/

# Go workspace file
go.work
"""
    }
    
    RUST_PROJECT_TEMPLATE = {
        "Cargo.toml": """[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
# Add dependencies as needed
""",
        "src/main.rs": """fn main() {{
    println!("Generated Rust project from {source_language}");
    // TODO: Implement main functionality
}}
""",
        "README.md": """# {project_name} (Rust)

This project was automatically transpiled from {source_language} to Rust using llmstruct AI transpiler.

## Build & Run

```bash
cargo build
cargo run
```

## Testing

```bash
cargo test
```
"""
    }


class AITranspiler:
    """AI-powered code transpiler"""
    
    def __init__(self, config: TranspilerConfig):
        self.config = config
        self.converter = UniversalConverter(ConverterConfig(
            include_ranges=True,
            include_hashes=False,
            include_tests=config.include_tests
        ))
        self.llm_client = LLMClient()
        
    def analyze_source_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze source project structure"""
        logger.info(f"Analyzing {self.config.source_language.value} project: {project_path}")
        
        return self.converter.convert_project(project_path, self.config.source_language)
    
    def create_target_project_structure(self, analysis: Dict[str, Any]) -> None:
        """Create target project directory structure"""
        output_path = Path(self.config.output_dir)
        
        if output_path.exists():
            logger.warning(f"Output directory {output_path} exists, cleaning...")
            shutil.rmtree(output_path)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        project_name = analysis["metadata"]["project_name"]
        source_lang = self.config.source_language.value
        
        # Create project template files
        if self.config.target_language == Language.GO:
            templates = LanguageTemplates.GO_PROJECT_TEMPLATE
            
            # Create go.mod
            (output_path / "go.mod").write_text(
                templates["go.mod"].format(module_name=project_name)
            )
            
            # Create main.go
            (output_path / "main.go").write_text(
                templates["main.go"].format(
                    source_language=source_lang,
                    project_name=project_name
                )
            )
            
            # Create README.md
            structure_info = self._generate_structure_info(analysis)
            (output_path / "README.md").write_text(
                templates["README.md"].format(
                    project_name=project_name,
                    source_language=source_lang,
                    structure_info=structure_info
                )
            )
            
            # Create .gitignore
            (output_path / ".gitignore").write_text(templates[".gitignore"])
            
        elif self.config.target_language == Language.RUST:
            templates = LanguageTemplates.RUST_PROJECT_TEMPLATE
            
            # Create Cargo.toml
            (output_path / "Cargo.toml").write_text(
                templates["Cargo.toml"].format(project_name=project_name)
            )
            
            # Create src directory and main.rs
            src_dir = output_path / "src"
            src_dir.mkdir(exist_ok=True)
            (src_dir / "main.rs").write_text(
                templates["src/main.rs"].format(source_language=source_lang)
            )
            
            # Create README.md
            (output_path / "README.md").write_text(
                templates["README.md"].format(
                    project_name=project_name,
                    source_language=source_lang
                )
            )
    
    def _generate_structure_info(self, analysis: Dict[str, Any]) -> str:
        """Generate structure information for README"""
        stats = analysis["metadata"]["stats"]
        
        info = f"""
- **Modules**: {stats.get('modules_count', 0)}
- **Functions**: {stats.get('functions_count', 0)}
- **Classes**: {stats.get('classes_count', 0)}
- **Total Lines**: {stats.get('total_lines', 0)}

## Module Categories

"""
        
        # Group modules by category
        categories = {}
        for module in analysis.get("toc", []):
            cat = module.get("category", "unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(module)
        
        for category, modules in categories.items():
            info += f"### {category.title()}\n"
            for module in modules[:10]:  # Limit to first 10
                info += f"- `{module['path']}` - {module.get('summary', 'No description')[:50]}...\n"
            if len(modules) > 10:
                info += f"- ... and {len(modules) - 10} more modules\n"
            info += "\n"
        
        return info
    
    def transpile_module(self, module: Dict[str, Any], context: List[Dict[str, Any]]) -> str:
        """Transpile a single module using AI"""
        source_lang = self.config.source_language.value
        target_lang = self.config.target_language.value
        
        # Build context from related modules
        context_info = ""
        if context:
            context_info = "\n\nRelated modules for context:\n"
            for ctx_module in context[:3]:  # Limit context
                context_info += f"- {ctx_module['module_id']}: {len(ctx_module.get('functions', []))} functions, {len(ctx_module.get('classes', []))} classes\n"
        
        prompt = f"""You are an expert programmer transpiling code from {source_lang} to {target_lang}.

Convert this {source_lang} module to idiomatic {target_lang} code:

**Module**: {module['module_id']}
**Path**: {module['path']}
**Category**: {module.get('category', 'unknown')}
**Description**: {module.get('module_doc', 'No description')}

**Functions** ({len(module.get('functions', []))}):
{self._format_functions(module.get('functions', []))}

**Classes** ({len(module.get('classes', []))}):
{self._format_classes(module.get('classes', []))}

**Dependencies**:
{', '.join(module.get('dependencies', []))}

{context_info}

**Requirements**:
1. Convert to idiomatic {target_lang} code
2. Preserve functionality and logic
3. Use appropriate {target_lang} naming conventions
4. Add proper error handling
5. Include package/module declaration
6. Add comments explaining the conversion
7. Handle dependencies appropriately

**Output format**:
```{target_lang.lower()}
// Converted from {source_lang}: {module['path']}
// Original module: {module['module_id']}

[YOUR {target_lang.upper()} CODE HERE]
```

Generate ONLY the {target_lang} code, no explanations."""
        
        try:
            response = self.llm_client.generate_completion(
                prompt=prompt,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to transpile module {module['module_id']}: {e}")
            return f"// ERROR: Failed to transpile {module['module_id']}\n// {str(e)}\n"
    
    def _format_functions(self, functions: List[Dict[str, Any]]) -> str:
        """Format functions for prompt"""
        if not functions:
            return "None"
        
        result = ""
        for func in functions[:10]:  # Limit to first 10
            params = ", ".join(func.get('parameters', []))
            result += f"- {func['name']}({params}): {func.get('docstring', 'No description')[:100]}\n"
        
        if len(functions) > 10:
            result += f"- ... and {len(functions) - 10} more functions\n"
        
        return result
    
    def _format_classes(self, classes: List[Dict[str, Any]]) -> str:
        """Format classes for prompt"""
        if not classes:
            return "None"
        
        result = ""
        for cls in classes[:5]:  # Limit to first 5
            methods = len(cls.get('methods', []))
            result += f"- {cls['name']} ({methods} methods): {cls.get('docstring', 'No description')[:100]}\n"
        
        if len(classes) > 5:
            result += f"- ... and {len(classes) - 5} more classes\n"
        
        return result
    
    def determine_target_path(self, module: Dict[str, Any]) -> str:
        """Determine target file path for transpiled module"""
        source_path = module['path']
        module_id = module['module_id']
        category = module.get('category', 'core')
        
        if self.config.target_language == Language.GO:
            # Convert Python path to Go package structure
            if category == 'test':
                # Test files
                base_name = Path(source_path).stem
                return f"{base_name}_test.go"
            elif category == 'cli':
                # CLI modules go to cmd/
                base_name = Path(source_path).stem
                return f"cmd/{base_name}/{base_name}.go"
            else:
                # Regular modules
                parts = module_id.split('.')
                if len(parts) > 1:
                    package = '/'.join(parts[:-1])
                    filename = f"{parts[-1]}.go"
                    return f"{package}/{filename}"
                else:
                    return f"{parts[0]}.go"
        
        elif self.config.target_language == Language.RUST:
            # Convert to Rust module structure
            if category == 'test':
                base_name = Path(source_path).stem
                return f"tests/{base_name}.rs"
            else:
                parts = module_id.split('.')
                if len(parts) > 1:
                    return f"src/{'/'.join(parts)}.rs"
                else:
                    return f"src/{parts[0]}.rs"
        
        return source_path  # Fallback
    
    def transpile_project(self, project_path: str) -> Dict[str, Any]:
        """Transpile entire project"""
        logger.info(f"Starting transpilation: {self.config.source_language.value} → {self.config.target_language.value}")
        
        # 1. Analyze source project
        analysis = self.analyze_source_project(project_path)
        
        # 2. Create target project structure
        self.create_target_project_structure(analysis)
        
        # 3. Transpile modules in chunks
        modules = analysis.get("modules", [])
        total_modules = len(modules)
        transpiled_files = []
        errors = []
        
        logger.info(f"Transpiling {total_modules} modules...")
        
        for i in range(0, total_modules, self.config.chunk_size):
            chunk = modules[i:i + self.config.chunk_size]
            logger.info(f"Processing chunk {i//self.config.chunk_size + 1}/{(total_modules + self.config.chunk_size - 1)//self.config.chunk_size}")
            
            for module in chunk:
                try:
                    # Get context (other modules in chunk)
                    context = [m for m in chunk if m != module]
                    
                    # Transpile module
                    transpiled_code = self.transpile_module(module, context)
                    
                    # Determine target path
                    target_path = self.determine_target_path(module)
                    full_target_path = Path(self.config.output_dir) / target_path
                    
                    # Create directory if needed
                    full_target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write transpiled code
                    full_target_path.write_text(transpiled_code, encoding='utf-8')
                    
                    transpiled_files.append({
                        "source": module['path'],
                        "target": target_path,
                        "module_id": module['module_id'],
                        "status": "success"
                    })
                    
                    logger.info(f"✅ Transpiled: {module['path']} → {target_path}")
                    
                except Exception as e:
                    error_info = {
                        "source": module['path'],
                        "module_id": module['module_id'],
                        "error": str(e),
                        "status": "failed"
                    }
                    errors.append(error_info)
                    logger.error(f"❌ Failed: {module['path']} - {e}")
        
        # 4. Generate transpilation report
        report = {
            "source_project": project_path,
            "target_directory": self.config.output_dir,
            "source_language": self.config.source_language.value,
            "target_language": self.config.target_language.value,
            "total_modules": total_modules,
            "successful_transpilations": len(transpiled_files),
            "failed_transpilations": len(errors),
            "success_rate": len(transpiled_files) / total_modules * 100 if total_modules > 0 else 0,
            "transpiled_files": transpiled_files,
            "errors": errors,
            "source_analysis": analysis["metadata"]["stats"]
        }
        
        # Save report
        report_path = Path(self.config.output_dir) / "transpilation_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        
        logger.info(f"🎉 Transpilation complete! Success rate: {report['success_rate']:.1f}%")
        logger.info(f"📊 {len(transpiled_files)}/{total_modules} modules transpiled successfully")
        logger.info(f"📄 Report saved to: {report_path}")
        
        return report


def main():
    """CLI interface for AI transpiler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Powered Universal Transpiler")
    parser.add_argument("project_path", help="Path to source project")
    parser.add_argument("--source", "-s", required=True, 
                       choices=[lang.value for lang in Language if lang != Language.UNKNOWN],
                       help="Source language")
    parser.add_argument("--target", "-t", required=True,
                       choices=[lang.value for lang in Language if lang != Language.UNKNOWN],
                       help="Target language")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--model", default="grok-beta", help="LLM model to use")
    parser.add_argument("--chunk-size", type=int, default=5, help="Modules per chunk")
    parser.add_argument("--no-tests", action="store_true", help="Skip test files")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    
    args = parser.parse_args()
    
    config = TranspilerConfig(
        source_language=Language(args.source),
        target_language=Language(args.target),
        output_dir=args.output,
        include_tests=not args.no_tests,
        chunk_size=args.chunk_size,
        model_name=args.model,
        temperature=args.temperature
    )
    
    transpiler = AITranspiler(config)
    
    try:
        report = transpiler.transpile_project(args.project_path)
        
        print(f"\n🎉 Transpilation Complete!")
        print(f"📊 Success Rate: {report['success_rate']:.1f}%")
        print(f"✅ Successful: {report['successful_transpilations']}")
        print(f"❌ Failed: {report['failed_transpilations']}")
        print(f"📁 Output: {report['target_directory']}")
        
        if report['errors']:
            print(f"\n⚠️  Errors:")
            for error in report['errors'][:5]:  # Show first 5 errors
                print(f"  - {error['source']}: {error['error']}")
            if len(report['errors']) > 5:
                print(f"  - ... and {len(report['errors']) - 5} more errors")
        
    except Exception as e:
        logger.error(f"Transpilation failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main() 