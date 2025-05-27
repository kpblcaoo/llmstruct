from .llm_client import LLMClient

"""LLMStruct: A tool for generating JSON-based code structures for LLM integration.

This package provides modular parsers, generators, and validators to create and
validate JSON representations of code projects, supporting automation and
context-aware LLM assistance.
"""

__version__ = "0.4.1"

__all__ = [
    "LLMClient",
    "cli",
    "self_run",
    "generators",
    "parsers",
    "validators",
    "templates",
]