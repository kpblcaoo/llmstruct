"""Tests for Summary Providers system.

Tests heuristic and LLM summary providers with fallback chain.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_heuristic_provider_extracts_docstrings():
    from llmstruct.core.summary_providers import HeuristicProvider
    
    heuristic = HeuristicProvider()
    
    # Test docstring extraction
    code_with_docstring = '''
def example_function():
    """This is a test function that does something useful."""
    return True
'''
    
    summary = heuristic.generate_summary(
        code=code_with_docstring,
        entity_type="function",
        entity_name="example_function",
        docstring="This is a test function that does something useful."
    )
    
    assert summary.source.value == "docstring", "Should use docstring source"
    assert summary.confidence == 0.9, "Docstring should have high confidence"
    assert "test function" in summary.text.lower(), "Should extract docstring content"


def test_heuristic_provider_generates_from_names():
    from llmstruct.core.summary_providers import HeuristicProvider
    
    heuristic = HeuristicProvider()
    
    # Test heuristic generation
    summary = heuristic.generate_summary(
        code="def get_user_name(): pass",
        entity_type="function", 
        entity_name="get_user_name"
    )
    
    assert summary.source.value == "heuristic", "Should use heuristic source"
    assert summary.confidence == 0.3, "Heuristic should have lower confidence"
    assert "retrieves" in summary.text.lower(), "Should generate heuristic summary"


def test_global_summary_system_integration():
    from llmstruct.core.summary_providers import generate_summary
    
    code_with_docstring = '''
def example_function():
    """This is a test function that does something useful."""
    return True
'''
    
    # Test global summary system
    summary = generate_summary(
        code=code_with_docstring,
        entity_type="function",
        entity_name="example_function",
        docstring="This is a test function that does something useful."
    )
    
    assert summary.source.value == "docstring", "Global system should work"


def test_summary_providers():
    print("Testing Summary Providers...")
    
    test_heuristic_provider_extracts_docstrings()
    test_heuristic_provider_generates_from_names()
    test_global_summary_system_integration()
    
    print("✓ Summary Providers tests passed")


if __name__ == "__main__":
    test_summary_providers() 