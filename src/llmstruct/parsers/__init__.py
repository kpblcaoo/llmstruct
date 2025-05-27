"""Language-specific parsers for extracting code structure data for LLMStruct JSON."""

from .javascript_parser import JavaScriptParser
from .go_parser import analyze_module as analyze_go_module

__all__ = ["PythonParser", "JavaScriptParser", "analyze_go_module"]
