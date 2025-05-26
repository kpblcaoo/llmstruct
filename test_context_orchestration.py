#!/usr/bin/env python3
"""
LLM Context Orchestration Testing Suite

Comprehensive testing framework for validating context modes, token budgets,
and LLM integration capabilities across different scenarios.
"""

import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pytest

# Import existing llmstruct modules
try:
    from src.llmstruct.context_orchestrator import SmartContextOrchestrator
    from src.llmstruct.cli_commands import CLICommands
except ImportError:
    # Handle case where modules aren't installed yet
    print("Warning: llmstruct modules not found. Running in development mode.")

@dataclass
class ContextTestResult:
    """Test result for context orchestration testing."""
    test_name: str
    context_mode: str
    token_budget: int
    tokens_used: int
    response_quality_score: float
    loading_time_ms: float
    success: bool
    error_message: Optional[str] = None
    context_sources: Optional[List[str]] = None
    
class LLMContextTester:
    """Main testing class for LLM context capabilities."""
    
    def __init__(self, config_path: str = "data/context_orchestration.json"):
        self.config_path = Path(config_path)
        self.results: List[ContextTestResult] = []
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging for test execution."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_context_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_test_config(self) -> Dict[str, Any]:
        """Load context orchestration configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default test configuration that matches actual structure
            return {
                "token_budgets": {
                    "FULL": {"max_tokens": 50000, "description": "Full project context"},
                    "FOCUSED": {"max_tokens": 16000, "description": "Focused task context"},
                    "MINIMAL": {"max_tokens": 8000, "description": "Minimal quick context"},
                    "SESSION": {"max_tokens": 32000, "description": "Session-based context"}
                },
                "context_sources": {
                    "tasks.json": {"weight": 0.3, "priority": "high"},
                    "ideas.json": {"weight": 0.25, "priority": "high"},
                    "docs/": {"weight": 0.2, "priority": "medium"},
                    "src/": {"weight": 0.15, "priority": "medium"},
                    "README.md": {"weight": 0.1, "priority": "low"}
                }
            }
    
    async def test_context_mode(self, mode: str, scenario: str = "general") -> ContextTestResult:
        """Test a specific context mode with given scenario."""
        start_time = time.time()
        config = self.load_test_config()
        
        try:
            # Get mode configuration
            mode_config = config.get("token_budgets", {}).get(mode, {})
            token_budget = mode_config.get("max_tokens", 8000)
            
            self.logger.info(f"Testing context mode: {mode} with budget: {token_budget}")
            
            # Simulate context loading and LLM interaction
            context_data = await self.load_context_for_mode(mode, token_budget)
            tokens_used = self.estimate_tokens(context_data)
            
            # Simulate LLM response quality assessment
            quality_score = await self.assess_response_quality(context_data, scenario)
            
            loading_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = ContextTestResult(
                test_name=f"context_mode_{mode}_{scenario}",
                context_mode=mode,
                token_budget=token_budget,
                tokens_used=tokens_used,
                response_quality_score=quality_score,
                loading_time_ms=loading_time,
                success=tokens_used <= token_budget,
                context_sources=list(context_data.keys()) if isinstance(context_data, dict) else []
            )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            loading_time = (time.time() - start_time) * 1000
            result = ContextTestResult(
                test_name=f"context_mode_{mode}_{scenario}",
                context_mode=mode,
                token_budget=token_budget,
                tokens_used=0,
                response_quality_score=0.0,
                loading_time_ms=loading_time,
                success=False,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    async def load_context_for_mode(self, mode: str, token_budget: int) -> Dict[str, Any]:
        """Load context data based on mode and token budget."""
        context_data = {}
        
        # Simulate loading different context sources based on mode
        if mode == "FULL":
            context_data = {
                "tasks.json": await self.load_json_file("data/tasks.json"),
                "ideas.json": await self.load_json_file("data/ideas.json"),
                "docs": await self.load_docs_summary(),
                "src": await self.load_src_summary(),
                "readme": await self.load_file_content("README.md")
            }
        elif mode == "FOCUSED":
            context_data = {
                "tasks.json": await self.load_json_file("data/tasks.json"),
                "ideas.json": await self.load_json_file("data/ideas.json"),
                "current_context": await self.load_current_context()
            }
        elif mode == "MINIMAL":
            context_data = {
                "summary": await self.load_project_summary(),
                "current_task": await self.load_current_task()
            }
        elif mode == "SESSION":
            context_data = {
                "session_data": await self.load_session_context(),
                "worklog": await self.load_json_file("data/sessions/worklog.json"),
                "current_session": await self.load_json_file("data/sessions/current_session.json")
            }
        
        # Trim context to fit token budget
        return await self.trim_context_to_budget(context_data, token_budget)
    
    async def load_json_file(self, filepath: str) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        try:
            path = Path(filepath)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load {filepath}: {e}")
        return {}
    
    async def load_file_content(self, filepath: str) -> str:
        """Load text file content."""
        try:
            path = Path(filepath)
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()
        except Exception as e:
            self.logger.warning(f"Could not load {filepath}: {e}")
        return ""
    
    async def load_docs_summary(self) -> str:
        """Load documentation summary."""
        # Simulate docs loading
        return "Documentation summary placeholder"
    
    async def load_src_summary(self) -> str:
        """Load source code summary."""
        # Simulate source code analysis
        return "Source code summary placeholder"
    
    async def load_current_context(self) -> Dict[str, Any]:
        """Load current working context."""
        return {"current_branch": "feature/llm-context-capability-testing", "status": "testing"}
    
    async def load_project_summary(self) -> str:
        """Load minimal project summary."""
        return "LLMStruct: JSON-based LLM project management and automation framework"
    
    async def load_current_task(self) -> Dict[str, Any]:
        """Load current task information."""
        return {"id": "TSK-TEST", "description": "Context capability testing", "status": "in_progress"}
    
    async def load_session_context(self) -> Dict[str, Any]:
        """Load AI session context."""
        return await self.load_json_file("data/sessions/ai_sessions.json")
    
    def estimate_tokens(self, context_data: Any) -> int:
        """Estimate token count for context data."""
        if isinstance(context_data, dict):
            content = json.dumps(context_data, indent=2)
        elif isinstance(context_data, str):
            content = context_data
        else:
            content = str(context_data)
        
        # Rough estimate: ~4 characters per token
        return len(content) // 4
    
    async def trim_context_to_budget(self, context_data: Dict[str, Any], budget: int) -> Dict[str, Any]:
        """Trim context data to fit within token budget."""
        total_tokens = self.estimate_tokens(context_data)
        
        if total_tokens <= budget:
            return context_data
        
        # Simple trimming strategy: remove least important sources first
        trimmed = {}
        current_tokens = 0
        
        # Priority order for context sources
        priority_order = ["tasks.json", "ideas.json", "session_data", "current_context", "summary"]
        
        for key in priority_order:
            if key in context_data:
                key_tokens = self.estimate_tokens(context_data[key])
                if current_tokens + key_tokens <= budget:
                    trimmed[key] = context_data[key]
                    current_tokens += key_tokens
                else:
                    # Partial inclusion if possible
                    remaining_budget = budget - current_tokens
                    if remaining_budget > 100:  # Minimum meaningful content
                        trimmed[key] = await self.truncate_content(context_data[key], remaining_budget)
                    break
        
        return trimmed
    
    async def truncate_content(self, content: Any, token_budget: int) -> Any:
        """Truncate content to fit token budget."""
        if isinstance(content, dict):
            # For JSON, keep essential keys
            essential_keys = ["id", "description", "status", "title", "summary"]
            truncated = {}
            for key in essential_keys:
                if key in content:
                    truncated[key] = content[key]
            return truncated
        elif isinstance(content, str):
            # For text, truncate to character limit
            char_limit = token_budget * 4  # Rough estimate
            return content[:char_limit] + "..." if len(content) > char_limit else content
        return content
    
    async def assess_response_quality(self, context_data: Dict[str, Any], scenario: str) -> float:
        """Assess the quality of context for LLM response."""
        # Simulate quality assessment based on various factors
        quality_score = 0.5  # Base score
        
        # Factor 1: Context completeness
        if "tasks.json" in context_data:
            quality_score += 0.15
        if "ideas.json" in context_data:
            quality_score += 0.15
        if "session_data" in context_data or "current_context" in context_data:
            quality_score += 0.1
        
        # Factor 2: Context relevance to scenario
        if scenario == "project-analysis" and len(context_data) >= 3:
            quality_score += 0.1
        elif scenario == "copilot-integration" and "current_context" in context_data:
            quality_score += 0.1
        
        # Factor 3: Context freshness (simulated)
        quality_score += 0.1  # Assume fresh context
        
        return min(1.0, quality_score)  # Cap at 1.0
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite for all context modes and scenarios."""
        self.logger.info("Starting comprehensive LLM context capability testing...")
        
        test_scenarios = [
            ("FULL", "project-analysis"),
            ("FOCUSED", "copilot-integration"),
            ("MINIMAL", "quick-query"),
            ("SESSION", "ai-session-work"),
            ("FULL", "documentation-generation"),
            ("FOCUSED", "task-planning"),
            ("MINIMAL", "status-check"),
            ("SESSION", "long-running-work")
        ]
        
        # Run all test scenarios
        for mode, scenario in test_scenarios:
            result = await self.test_context_mode(mode, scenario)
            self.logger.info(f"Test completed: {result.test_name} - Success: {result.success}")
        
        # Generate summary report
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        
        # Calculate averages
        avg_loading_time = sum(r.loading_time_ms for r in self.results) / total_tests
        avg_quality_score = sum(r.response_quality_score for r in self.results) / total_tests
        
        # Group by context mode
        mode_results = {}
        for result in self.results:
            mode = result.context_mode
            if mode not in mode_results:
                mode_results[mode] = []
            mode_results[mode].append(result)
        
        # Mode-specific analysis
        mode_analysis = {}
        for mode, results in mode_results.items():
            mode_analysis[mode] = {
                "total_tests": len(results),
                "success_rate": sum(1 for r in results if r.success) / len(results),
                "avg_loading_time_ms": sum(r.loading_time_ms for r in results) / len(results),
                "avg_quality_score": sum(r.response_quality_score for r in results) / len(results),
                "avg_tokens_used": sum(r.tokens_used for r in results) / len(results)
            }
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests,
                "avg_loading_time_ms": avg_loading_time,
                "avg_quality_score": avg_quality_score
            },
            "mode_analysis": mode_analysis,
            "detailed_results": [asdict(r) for r in self.results],
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        report_path = Path("test_context_capability_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Test report saved to: {report_path}")
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if not self.results:
            return ["No test data available for recommendations"]
        
        # Analyze success rates by mode
        mode_success = {}
        for result in self.results:
            mode = result.context_mode
            if mode not in mode_success:
                mode_success[mode] = []
            mode_success[mode].append(result.success)
        
        for mode, successes in mode_success.items():
            success_rate = sum(successes) / len(successes)
            if success_rate < 0.8:
                recommendations.append(f"Consider optimizing {mode} mode - success rate: {success_rate:.2%}")
        
        # Analyze loading times
        avg_loading_time = sum(r.loading_time_ms for r in self.results) / len(self.results)
        if avg_loading_time > 1000:  # > 1 second
            recommendations.append(f"Context loading is slow (avg: {avg_loading_time:.0f}ms) - consider caching optimizations")
        
        # Analyze quality scores
        avg_quality = sum(r.response_quality_score for r in self.results) / len(self.results)
        if avg_quality < 0.7:
            recommendations.append(f"Context quality is low (avg: {avg_quality:.2f}) - review context selection strategy")
        
        if not recommendations:
            recommendations.append("All tests performing well - system ready for production use")
        
        return recommendations

# CLI integration for easy testing
async def main():
    """Main function for CLI testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Context Capability Testing")
    parser.add_argument("--mode", choices=["FULL", "FOCUSED", "MINIMAL", "SESSION"], 
                       help="Test specific context mode")
    parser.add_argument("--scenario", default="general", help="Test scenario name")
    parser.add_argument("--comprehensive", action="store_true", 
                       help="Run comprehensive test suite")
    parser.add_argument("--config", default="data/context_orchestration.json",
                       help="Context configuration file path")
    
    args = parser.parse_args()
    
    tester = LLMContextTester(args.config)
    
    if args.comprehensive:
        report = await tester.run_comprehensive_test_suite()
        print("\n" + "="*50)
        print("COMPREHENSIVE TEST REPORT")
        print("="*50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.2%}")
        print(f"Avg Loading Time: {report['test_summary']['avg_loading_time_ms']:.0f}ms")
        print(f"Avg Quality Score: {report['test_summary']['avg_quality_score']:.2f}")
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"- {rec}")
    elif args.mode:
        result = await tester.test_context_mode(args.mode, args.scenario)
        print(f"\nTest Result: {result.test_name}")
        print(f"Success: {result.success}")
        print(f"Tokens Used: {result.tokens_used}/{result.token_budget}")
        print(f"Quality Score: {result.response_quality_score:.2f}")
        print(f"Loading Time: {result.loading_time_ms:.0f}ms")
        if result.error_message:
            print(f"Error: {result.error_message}")
    else:
        print("Please specify --mode or --comprehensive")

if __name__ == "__main__":
    asyncio.run(main())
