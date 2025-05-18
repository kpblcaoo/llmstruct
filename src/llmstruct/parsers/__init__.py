"""Language-specific parsers for extracting code structure data for LLMStruct JSON."""

from .python_parser import analyze_module
from .javascript_parser import JavaScriptParser

__all__ = ["PythonParser", "JavaScriptParser"]