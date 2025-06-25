"""
LLMStruct Core Module

Provides core functionality for code analysis and structure generation.
All LLM-dependent features are optional and disabled by default.
"""

from .config_manager import (
    get_config_manager,
    get_config,
    is_llm_enabled,
    get_summary_provider,
    ConfigManager,
    LLMStructConfig
)

from .hash_utils import (
    hash_content,
    hash_file,
    hash_source,
    hash_entity,
    quick_file_hash,
    quick_content_hash,
    quick_source_hash
)

from .uid_generator import (
    generate_uid,
    generate_uid_components,
    UIDType,
    enhance_entity_with_uid,
    create_legacy_artifact_id
)

from .summary_providers import (
    generate_summary,
    get_summary_system,
    SummarySystem,
    HeuristicProvider,
    LLMProvider,
    CodeSummary,
    SummarySource
)

__version__ = "2.1.0"
__all__ = [
    # Config management
    "get_config_manager",
    "get_config", 
    "is_llm_enabled",
    "get_summary_provider",
    "ConfigManager",
    "LLMStructConfig",
    # Hash utilities
    "hash_content",
    "hash_file", 
    "hash_source",
    "hash_entity",
    "quick_file_hash",
    "quick_content_hash",
    "quick_source_hash",
    # UID system
    "generate_uid",
    "generate_uid_components",
    "UIDType",
    "enhance_entity_with_uid", 
    "create_legacy_artifact_id",
    # Summary system
    "generate_summary",
    "get_summary_system",
    "SummarySystem",
    "HeuristicProvider",
    "LLMProvider",
    "CodeSummary",
    "SummarySource"
] 