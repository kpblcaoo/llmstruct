"""Language-specific parsers for extracting code structure data for LLMStruct JSON."""

from .javascript_parser import JavaScriptParser

__all__ = ["PythonParser", "JavaScriptParser"]
