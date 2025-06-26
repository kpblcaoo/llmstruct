"""llmstruct.core.tag_inference

Utilities for inferring semantic tags for code entities.

The tag system is used across the project for quick categorisation and
filtering.  This module centralises heuristics so that they are consistent
and testable.  It does **not** modify existing entities – higher-level
parsers/generators should call it when they need fresh tags.

Rules mirror those used in Phase 1 but вынесены в отдельный модуль для
Phase 1.5 quality-assurance.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List, Set

__all__ = [
    "Tag",
    "infer_tags",
]


class Tag(str, Enum):
    """Canonical tag values used in the project."""

    PUBLIC = "public"
    PRIVATE = "private"
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    MODULE = "module"
    ASYNC = "async"
    GENERATOR = "generator"
    PROPERTY = "property"
    STATIC = "static"
    CLASSMETHOD = "classmethod"

    def __str__(self) -> str:  # pragma: no cover – for nicer repr
        return self.value


_NAME_BASED_PATTERNS = {
    r"^_": Tag.PRIVATE,
    r"^__": Tag.PRIVATE,
    r"^[a-z]": Tag.PUBLIC,
    r"^[A-Z]": Tag.PUBLIC,  # CamelCase class or constant
}

_CODE_BASED_PATTERNS = {
    r"async\s+def": Tag.ASYNC,
    r"yield\s": Tag.GENERATOR,
    r"@property": Tag.PROPERTY,
    r"@staticmethod": Tag.STATIC,
    r"@classmethod": Tag.CLASSMETHOD,
}


def _name_based_tags(name: str) -> Set[Tag]:
    """Infer tags from naming conventions."""
    result: Set[Tag] = set()
    for pattern, tag in _NAME_BASED_PATTERNS.items():
        if re.search(pattern, name):
            result.add(tag)
    return result


def _code_based_tags(code: str) -> Set[Tag]:
    """Infer tags by scanning source code for specific patterns."""
    result: Set[Tag] = set()
    for pattern, tag in _CODE_BASED_PATTERNS.items():
        if re.search(pattern, code):
            result.add(tag)
    return result


def infer_tags(*,
               code: str,
               entity_type: str,
               entity_name: str | None = None) -> List[str]:
    """Infer a list of semantic tags for a code entity.

    Args:
        code: Raw source code snippet (may be trimmed).
        entity_type: One of ``"module"``, ``"class"``, ``"function"``,
            ``"method"`` – anything else will be treated as generic.
        entity_name: Canonical name of the entity (optional).

    Returns:
        Sorted list of *unique* tag strings.
    """

    tags: Set[Tag] = set()

    # Type-based tag is mandatory
    try:
        tags.add(Tag(entity_type))
    except ValueError:
        pass  # Unknown type – skip

    # Name-based heuristics
    if entity_name:
        tags |= _name_based_tags(entity_name)

    # Code-based heuristics (fast regex scan)
    if code:
        tags |= _code_based_tags(code)

    # Guarantee deterministic order
    return sorted(str(tag) for tag in tags) 