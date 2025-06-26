"""
Summary Core Types and Abstractions

Contains base classes, enums, and data structures for the summary system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class SummarySource(Enum):
    """Source of the summary"""
    DOCSTRING = "docstring"
    HEURISTIC = "heuristic" 
    LLM = "llm"
    EMPTY = "empty"


@dataclass
class CodeSummary:
    """Container for code summary with metadata"""
    text: str
    source: SummarySource
    confidence: float  # 0.0 - 1.0
    tags: List[str]
    truncated: bool = False
    
    def is_empty(self) -> bool:
        """Check if summary is effectively empty"""
        return not self.text or self.text.strip() == ""


class SummaryProvider(ABC):
    """Abstract base class for summary providers"""
    
    @abstractmethod
    def generate_summary(self, 
                        code: str, 
                        entity_type: str,
                        entity_name: str,
                        docstring: Optional[str] = None,
                        **kwargs) -> CodeSummary:
        """Generate summary for code entity"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass 