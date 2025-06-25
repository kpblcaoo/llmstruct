"""
Summary Providers System

Provides multiple strategies for generating code summaries:
- HeuristicProvider: Fast, offline, deterministic (default)
- LLMProvider: AI-powered but optional and disabled by default
"""

import re
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

from .config_manager import get_config, is_llm_enabled


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


class HeuristicProvider(SummaryProvider):
    """
    Fast, deterministic summary provider using heuristics.
    
    Fallback chain:
    1. Extract and clean docstring (confidence: 0.9)
    2. Generate from function/class name (confidence: 0.3)
    3. Return empty (confidence: 0.0)
    """
    
    def __init__(self, max_length: int = 120):
        self.max_length = max_length
        
    def generate_summary(self, 
                        code: str,
                        entity_type: str, 
                        entity_name: str,
                        docstring: Optional[str] = None,
                        **kwargs) -> CodeSummary:
        """Generate heuristic summary"""
        
        # Try docstring first
        if docstring and docstring.strip():
            cleaned = self._clean_docstring(docstring)
            if cleaned:
                return CodeSummary(
                    text=cleaned,
                    source=SummarySource.DOCSTRING,
                    confidence=0.9,
                    tags=self._extract_tags_from_docstring(docstring),
                    truncated=len(cleaned) >= self.max_length
                )
        
        # Try heuristic generation
        heuristic_summary = self._generate_heuristic_summary(entity_type, entity_name, code)
        if heuristic_summary:
            return CodeSummary(
                text=heuristic_summary,
                source=SummarySource.HEURISTIC,
                confidence=0.3,
                tags=self._extract_tags_from_code(entity_type, entity_name, code),
                truncated=False
            )
        
        # Return empty
        return CodeSummary(
            text="",
            source=SummarySource.EMPTY,
            confidence=0.0,
            tags=[],
            truncated=False
        )
    
    def _clean_docstring(self, docstring: str) -> str:
        """Clean and truncate docstring"""
        # Remove common docstring formatting
        cleaned = re.sub(r'^\s*"""?\s*', '', docstring)
        cleaned = re.sub(r'\s*"""?\s*$', '', cleaned)
        
        # Take first sentence or paragraph
        sentences = re.split(r'[.!?]\s+', cleaned)
        if sentences:
            first_sentence = sentences[0].strip()
            if first_sentence:
                # Truncate if too long
                if len(first_sentence) > self.max_length:
                    truncated = first_sentence[:self.max_length-3] + "..."
                    return truncated
                return first_sentence
        
        return ""
    
    def _generate_heuristic_summary(self, entity_type: str, entity_name: str, code: str) -> str:
        """Generate summary based on naming patterns and code structure"""
        
        # Simple name-based heuristics
        name_lower = entity_name.lower()
        
        # Common patterns
        if entity_type == "function":
            if name_lower.startswith(('get_', 'fetch_', 'retrieve_')):
                return f"Retrieves {self._humanize_name(entity_name[4:])}"
            elif name_lower.startswith(('set_', 'update_', 'modify_')):
                return f"Updates {self._humanize_name(entity_name[4:])}"
            elif name_lower.startswith(('create_', 'make_', 'build_')):
                return f"Creates {self._humanize_name(entity_name[7:])}"
            elif name_lower.startswith(('delete_', 'remove_', 'destroy_')):
                return f"Removes {self._humanize_name(entity_name[7:])}"
            elif name_lower.startswith(('is_', 'has_', 'can_')):
                return f"Checks if {self._humanize_name(entity_name[3:])}"
            elif name_lower.startswith('validate_'):
                return f"Validates {self._humanize_name(entity_name[9:])}"
            elif name_lower.startswith('parse_'):
                return f"Parses {self._humanize_name(entity_name[6:])}"
            elif name_lower.startswith('format_'):
                return f"Formats {self._humanize_name(entity_name[7:])}"
            
        elif entity_type == "class":
            if name_lower.endswith('manager'):
                return f"Manages {self._humanize_name(entity_name[:-7])}"
            elif name_lower.endswith('handler'):
                return f"Handles {self._humanize_name(entity_name[:-7])}"
            elif name_lower.endswith('provider'):
                return f"Provides {self._humanize_name(entity_name[:-8])}"
            elif name_lower.endswith('client'):
                return f"Client for {self._humanize_name(entity_name[:-6])}"
            elif name_lower.endswith('parser'):
                return f"Parses {self._humanize_name(entity_name[:-6])}"
        
        # Fallback to generic description
        return f"{entity_type.title()} for {self._humanize_name(entity_name)}"
    
    def _humanize_name(self, name: str) -> str:
        """Convert snake_case or CamelCase to human readable"""
        # Handle snake_case
        if '_' in name:
            words = name.split('_')
            return ' '.join(word.lower() for word in words if word)
        
        # Handle CamelCase
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        return ' '.join(word.lower() for word in words if word)
    
    def _extract_tags_from_docstring(self, docstring: str) -> List[str]:
        """Extract tags from docstring content"""
        tags = []
        docstring_lower = docstring.lower()
        
        # Common patterns
        if any(word in docstring_lower for word in ['deprecated', 'obsolete']):
            tags.append('deprecated')
        if any(word in docstring_lower for word in ['async', 'await', 'coroutine']):
            tags.append('async')
        if any(word in docstring_lower for word in ['generator', 'yield']):
            tags.append('generator')
        if any(word in docstring_lower for word in ['property', 'getter', 'setter']):
            tags.append('property')
        if any(word in docstring_lower for word in ['private', 'internal']):
            tags.append('private')
        if any(word in docstring_lower for word in ['public', 'api']):
            tags.append('public')
            
        return tags
    
    def _extract_tags_from_code(self, entity_type: str, entity_name: str, code: str) -> List[str]:
        """Extract tags from code analysis"""
        tags = []
        
        # Type-based tags
        tags.append(entity_type)
        
        # Name-based tags
        if entity_name.startswith('_'):
            tags.append('private')
        else:
            tags.append('public')
            
        # Code pattern tags
        if 'async def' in code:
            tags.append('async')
        if 'yield' in code:
            tags.append('generator')
        if '@property' in code:
            tags.append('property')
        if '@staticmethod' in code:
            tags.append('static')
        if '@classmethod' in code:
            tags.append('classmethod')
            
        return tags
    
    def get_provider_name(self) -> str:
        return "heuristic"


class LLMProvider(SummaryProvider):
    """
    LLM-powered summary provider (optional, disabled by default).
    
    Only works when LLM is explicitly enabled via configuration.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._cache: Dict[str, CodeSummary] = {}
        
    def generate_summary(self,
                        code: str,
                        entity_type: str,
                        entity_name: str, 
                        docstring: Optional[str] = None,
                        **kwargs) -> CodeSummary:
        """Generate LLM-powered summary"""
        
        # Check if LLM is enabled
        if not is_llm_enabled():
            return CodeSummary(
                text="",
                source=SummarySource.EMPTY,
                confidence=0.0,
                tags=[],
                truncated=False
            )
        
        # Create cache key
        cache_key = self._create_cache_key(code, entity_type, entity_name)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Generate LLM summary
            summary = self._call_llm_api(code, entity_type, entity_name, docstring)
            self._cache[cache_key] = summary
            return summary
            
        except Exception as e:
            # Fallback to empty on error
            print(f"Warning: LLM summary generation failed: {e}")
            return CodeSummary(
                text="",
                source=SummarySource.EMPTY,
                confidence=0.0,
                tags=[],
                truncated=False
            )
    
    def _create_cache_key(self, code: str, entity_type: str, entity_name: str) -> str:
        """Create cache key for LLM results"""
        content = f"{entity_type}:{entity_name}:{code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _call_llm_api(self, code: str, entity_type: str, entity_name: str, docstring: Optional[str]) -> CodeSummary:
        """Call LLM API to generate summary"""
        config = get_config()
        
        # Prepare prompt
        prompt = self._create_prompt(code, entity_type, entity_name, docstring)
        
        # This is a placeholder - actual implementation would call OpenAI/Anthropic API
        # For now, return a mock response to avoid API calls during development
        
        return CodeSummary(
            text=f"AI-generated summary for {entity_type} {entity_name}",
            source=SummarySource.LLM,
            confidence=0.7,
            tags=[entity_type, "ai-generated"],
            truncated=False
        )
    
    def _create_prompt(self, code: str, entity_type: str, entity_name: str, docstring: Optional[str]) -> str:
        """Create LLM prompt for summary generation"""
        config = get_config()
        max_length = config.summary.max_length
        
        prompt = f"""Generate a concise summary for this {entity_type}:

Name: {entity_name}
Code:
```python
{code[:500]}  # Truncated for security
```
"""
        
        if docstring:
            prompt += f"\nExisting docstring: {docstring[:200]}"
        
        prompt += f"""

Requirements:
- Maximum {max_length} characters
- Focus on functionality and purpose
- Be specific and actionable
- Avoid generic phrases
- Return only the summary text
"""
        
        return prompt
    
    def get_provider_name(self) -> str:
        return "llm"


class SummarySystem:
    """Main summary system that orchestrates different providers"""
    
    def __init__(self):
        self.heuristic_provider = HeuristicProvider()
        self.llm_provider = LLMProvider()
        
    def generate_summary(self,
                        code: str,
                        entity_type: str,
                        entity_name: str,
                        docstring: Optional[str] = None,
                        **kwargs) -> CodeSummary:
        """Generate summary using configured provider"""
        
        config = get_config()
        provider_name = config.summary.provider
        
        # Use LLM provider if enabled and requested
        if provider_name == "llm" and is_llm_enabled():
            llm_summary = self.llm_provider.generate_summary(
                code, entity_type, entity_name, docstring, **kwargs
            )
            # Fallback to heuristic if LLM fails or low confidence
            if llm_summary.confidence >= config.summary.confidence_threshold:
                return llm_summary
        
        # Use heuristic provider (default)
        return self.heuristic_provider.generate_summary(
            code, entity_type, entity_name, docstring, **kwargs
        )
    
    def get_active_provider(self) -> str:
        """Get name of currently active provider"""
        config = get_config()
        if config.summary.provider == "llm" and is_llm_enabled():
            return "llm"
        return "heuristic"


# Global summary system instance
_summary_system: Optional[SummarySystem] = None


def get_summary_system() -> SummarySystem:
    """Get global summary system instance"""
    global _summary_system
    if _summary_system is None:
        _summary_system = SummarySystem()
    return _summary_system


def generate_summary(code: str,
                    entity_type: str, 
                    entity_name: str,
                    docstring: Optional[str] = None,
                    **kwargs) -> CodeSummary:
    """Generate summary using the configured provider"""
    return get_summary_system().generate_summary(
        code, entity_type, entity_name, docstring, **kwargs
    ) 