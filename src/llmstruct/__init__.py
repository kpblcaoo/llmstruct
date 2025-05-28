from .llm_client import LLMClient

# AI Self-Awareness imports
try:
    from .ai_self_awareness import SystemCapabilityDiscovery
    from .ai_cli_integration import AISelfAwarenessCLIIntegration
    AI_MODULES_AVAILABLE = True
except ImportError:
    # Graceful fallback if AI modules not available
    SystemCapabilityDiscovery = None
    AISelfAwarenessCLIIntegration = None
    AI_MODULES_AVAILABLE = False

"""LLMStruct: A tool for generating JSON-based code structures for LLM integration.

This package provides modular parsers, generators, and validators to create and
validate JSON representations of code projects, supporting automation and
context-aware LLM assistance.

Enhanced with AI self-awareness capabilities for intelligent system monitoring
and capability discovery.
"""

__version__ = "0.4.1-ai-enhanced"

__all__ = [
    "LLMClient",
    "cli",
    "self_run", 
    "generators",
    "parsers",
    "validators",
    "templates",
    # AI Self-Awareness modules
    "SystemCapabilityDiscovery",
    "AISelfAwarenessCLIIntegration",
    "AI_MODULES_AVAILABLE",
]

