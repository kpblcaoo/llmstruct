"""
Universal Converter Configuration and Constants

Contains configuration dataclasses, enums, and utilities for the universal converter.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from pathlib import Path


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    GO = "go"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    UNKNOWN = "unknown"


@dataclass
class ConverterConfig:
    """Configuration for universal converter"""
    include_ranges: bool = True
    include_hashes: bool = True
    include_tests: bool = True
    goals: List[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.goals is None:
            self.goals = []
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "node_modules", ".git", "__pycache__", ".pytest_cache",
                "vendor", "target", "build", "dist", ".venv", "venv"
            ]


class LanguageDetector:
    """Utility class for language detection"""
    
    LANGUAGE_EXTENSIONS = {
        Language.PYTHON: [".py", ".pyw"],
        Language.GO: [".go"],
        Language.JAVASCRIPT: [".js", ".jsx", ".mjs"],
        Language.TYPESCRIPT: [".ts", ".tsx"],
        Language.RUST: [".rs"],
        Language.JAVA: [".java"],
        Language.CPP: [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"],
        Language.CSHARP: [".cs"],
    }
    
    @classmethod
    def detect_language(cls, file_path: str) -> Language:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        for lang, extensions in cls.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
                
        return Language.UNKNOWN
    
    @classmethod
    def detect_project_languages(cls, project_path: str, exclude_patterns: List[str]) -> Dict[Language, int]:
        """Detect all languages in project and count files"""
        import os
        languages = {}
        
        for root, dirs, files in os.walk(project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                lang = cls.detect_language(file_path)
                
                if lang != Language.UNKNOWN:
                    languages[lang] = languages.get(lang, 0) + 1
                    
        return languages 