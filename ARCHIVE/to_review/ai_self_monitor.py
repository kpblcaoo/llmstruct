"""
AI Self-Monitoring System
Tracks AI usage patterns and ensures proper llmstruct integration.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AIBehaviorPattern(Enum):
    """AI behavior patterns to monitor."""
    PROPER_LLMSTRUCT_USAGE = "proper_llmstruct_usage"
    CONTEXT_TAG_USAGE = "context_tag_usage"
    SEMANTIC_SEARCH_USAGE = "semantic_search_usage"
    STRUCT_JSON_ANALYSIS = "struct_json_analysis"
    DELEGATION_AWARENESS = "delegation_awareness"
    BYPASSING_SYSTEM = "bypassing_system"
    IGNORING_GUIDANCE = "ignoring_guidance"


@dataclass
class AIUsageEvent:
    """Single AI usage event."""
    timestamp: str
    query: str
    used_llmstruct: bool
    tools_used: List[str]
    context_tags: List[str]
    behavior_patterns: List[str]
    effectiveness_score: float
    metadata: Dict[str, Any]


@dataclass
class AIBehaviorAnalysis:
    """Analysis of AI behavior patterns."""
    llmstruct_usage_rate: float
    context_awareness_score: float
    tool_usage_diversity: float
    guidance_adherence: float
    improvement_needed: List[str]
    strengths: List[str]
    recommendations: List[str]


class AISelfMonitor:
    """
    Monitors AI behavior and ensures proper llmstruct integration.
    Provides feedback and corrective guidance.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.events_file = self.project_root / "data" / "ai_self_awareness" / "ai_usage_events.json"
        self.analysis_file = self.project_root / "data" / "ai_self_awareness" / "ai_behavior_analysis.json"
        
        # Event storage
        self.events: List[AIUsageEvent] = []
        self.max_events = 1000  # Keep last 1000 events
        
        # Monitoring patterns
        self.required_patterns = {
            AIBehaviorPattern.PROPER_LLMSTRUCT_USAGE: 0.8,  # 80% of requests should use llmstruct
            AIBehaviorPattern.CONTEXT_TAG_USAGE: 0.6,       # 60% should use context tags
            AIBehaviorPattern.SEMANTIC_SEARCH_USAGE: 0.4,   # 40% should use semantic search
            AIBehaviorPattern.STRUCT_JSON_ANALYSIS: 0.3,    # 30% should reference struct.json
        }
        
        # Load existing data
        self._load_events()
        
        logger.info("AI Self-Monitor initialized")
    
    def record_ai_interaction(
        self,
        query: str,
        tools_used: List[str],
        used_llmstruct: bool = False,
        context_tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Record an AI interaction for monitoring."""
        
        # Analyze behavior patterns
        patterns = self._analyze_interaction_patterns(query, tools_used, used_llmstruct, context_tags)
        
        # Calculate effectiveness score
        effectiveness = self._calculate_effectiveness_score(patterns, tools_used, used_llmstruct)
        
        # Create event
        event = AIUsageEvent(
            timestamp=datetime.now().isoformat(),
            query=query[:200],  # Truncate long queries
            used_llmstruct=used_llmstruct,
            tools_used=tools_used,
            context_tags=context_tags or [],
            behavior_patterns=[p.value for p in patterns],
            effectiveness_score=effectiveness,
            metadata=metadata or {}
        )
        
        # Store event
        self.events.append(event)
        
        # Trim events if needed
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Save to disk
        self._save_events()
        
        # Check if immediate feedback needed
        self._check_immediate_feedback(event)
    
    def _analyze_interaction_patterns(
        self,
        query: str,
        tools_used: List[str],
        used_llmstruct: bool,
        context_tags: List[str]
    ) -> List[AIBehaviorPattern]:
        """Analyze patterns in AI interaction."""
        patterns = []
        
        query_lower = query.lower()
        
        # Check llmstruct usage
        if used_llmstruct:
            patterns.append(AIBehaviorPattern.PROPER_LLMSTRUCT_USAGE)
        else:
            patterns.append(AIBehaviorPattern.BYPASSING_SYSTEM)
        
        # Check context tag usage
        if context_tags:
            patterns.append(AIBehaviorPattern.CONTEXT_TAG_USAGE)
        
        # Check semantic search usage
        if any("search" in tool for tool in tools_used):
            patterns.append(AIBehaviorPattern.SEMANTIC_SEARCH_USAGE)
        
        # Check struct.json analysis
        if any("struct" in tool for tool in tools_used) or "struct.json" in query_lower:
            patterns.append(AIBehaviorPattern.STRUCT_JSON_ANALYSIS)
        
        # Check delegation awareness
        if "delegation" in query_lower or "ai" in query_lower:
            patterns.append(AIBehaviorPattern.DELEGATION_AWARENESS)
        
        return patterns
    
    def _calculate_effectiveness_score(
        self,
        patterns: List[AIBehaviorPattern],
        tools_used: List[str],
        used_llmstruct: bool
    ) -> float:
        """Calculate effectiveness score for interaction."""
        score = 0.5  # Base score
        
        # Bonus for llmstruct usage
        if used_llmstruct:
            score += 0.3
        
        # Bonus for good patterns
        pattern_scores = {
            AIBehaviorPattern.PROPER_LLMSTRUCT_USAGE: 0.2,
            AIBehaviorPattern.CONTEXT_TAG_USAGE: 0.1,
            AIBehaviorPattern.SEMANTIC_SEARCH_USAGE: 0.1,
            AIBehaviorPattern.STRUCT_JSON_ANALYSIS: 0.15,
            AIBehaviorPattern.DELEGATION_AWARENESS: 0.05
        }
        
        for pattern in patterns:
            score += pattern_scores.get(pattern, 0)
        
        # Bonus for tool diversity
        tool_diversity_bonus = min(len(set(tools_used)) * 0.05, 0.1)
        score += tool_diversity_bonus
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _check_immediate_feedback(self, event: AIUsageEvent) -> None:
        """Check if immediate feedback/correction is needed."""
        
        # Check for critical issues
        if not event.used_llmstruct and any(
            keyword in event.query.lower() 
            for keyword in ["analyze", "implement", "debug", "architecture"]
        ):
            self._log_immediate_feedback("⚠️ CRITICAL: Complex task performed without llmstruct system!")
        
        # Check for missing context tags on technical queries
        if not event.context_tags and any(
            keyword in event.query.lower()
            for keyword in ["code", "debug", "implement", "refactor"]
        ):
            self._log_immediate_feedback("💡 SUGGESTION: Consider using context tags like [code], [debug] for better results")
        
        # Check for inefficient tool usage
        if event.effectiveness_score < 0.4:
            self._log_immediate_feedback(f"📊 LOW EFFECTIVENESS ({event.effectiveness_score:.2f}): Consider using llmstruct system")
    
    def _log_immediate_feedback(self, message: str) -> None:
        """Log immediate feedback message."""
        logger.warning(f"AI SELF-MONITOR: {message}")
        print(f"\n🤖 {message}\n")
    
    def analyze_behavior_trends(self, days: int = 7) -> AIBehaviorAnalysis:
        """Analyze AI behavior trends over specified period."""
        
        # Filter events to time period
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_events = [
            event for event in self.events
            if datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')) > cutoff_date
        ]
        
        if not recent_events:
            return AIBehaviorAnalysis(
                llmstruct_usage_rate=0.0,
                context_awareness_score=0.0,
                tool_usage_diversity=0.0,
                guidance_adherence=0.0,
                improvement_needed=["No recent activity to analyze"],
                strengths=[],
                recommendations=["Start using the llmstruct system"]
            )
        
        # Calculate metrics
        total_events = len(recent_events)
        llmstruct_usage = sum(1 for e in recent_events if e.used_llmstruct) / total_events
        
        # Context awareness (usage of tags and semantic tools)
        context_aware_events = sum(
            1 for e in recent_events 
            if e.context_tags or any("search" in tool for tool in e.tools_used)
        )
        context_awareness = context_aware_events / total_events
        
        # Tool diversity
        all_tools = set()
        for event in recent_events:
            all_tools.update(event.tools_used)
        tool_diversity = len(all_tools) / 10.0  # Normalize by expected max tools
        
        # Guidance adherence (effectiveness scores)
        avg_effectiveness = sum(e.effectiveness_score for e in recent_events) / total_events
        
        # Identify improvements needed
        improvements = []
        if llmstruct_usage < self.required_patterns[AIBehaviorPattern.PROPER_LLMSTRUCT_USAGE]:
            improvements.append("Increase llmstruct system usage")
        
        if context_awareness < 0.5:
            improvements.append("Use more context tags and semantic search")
        
        if tool_diversity < 0.3:
            improvements.append("Diversify tool usage for better results")
        
        if avg_effectiveness < 0.6:
            improvements.append("Focus on high-effectiveness interaction patterns")
        
        # Identify strengths
        strengths = []
        if llmstruct_usage >= 0.8:
            strengths.append("Excellent llmstruct system integration")
        
        if context_awareness >= 0.7:
            strengths.append("Good context awareness and tool usage")
        
        if avg_effectiveness >= 0.7:
            strengths.append("High effectiveness in task completion")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            llmstruct_usage, context_awareness, tool_diversity, avg_effectiveness
        )
        
        analysis = AIBehaviorAnalysis(
            llmstruct_usage_rate=llmstruct_usage,
            context_awareness_score=context_awareness,
            tool_usage_diversity=tool_diversity,
            guidance_adherence=avg_effectiveness,
            improvement_needed=improvements,
            strengths=strengths,
            recommendations=recommendations
        )
        
        # Save analysis
        self._save_analysis(analysis)
        
        return analysis
    
    def _generate_recommendations(
        self,
        llmstruct_usage: float,
        context_awareness: float, 
        tool_diversity: float,
        effectiveness: float
    ) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        if llmstruct_usage < 0.6:
            recommendations.append("🎯 Use initialize_ai_middleware() to force llmstruct integration")
            recommendations.append("📝 Add context tags like [code], [debug], [discuss] to queries")
        
        if context_awareness < 0.5:
            recommendations.append("🔍 Use codebase_search for semantic exploration")
            recommendations.append("📊 Reference struct.json for project understanding")
        
        if tool_diversity < 0.3:
            recommendations.append("🛠️ Explore available tools: file_search, read_file, edit_file")
            recommendations.append("⚙️ Use AI delegation for optimal task routing")
        
        if effectiveness < 0.6:
            recommendations.append("🧠 Follow middleware guidance messages")
            recommendations.append("🔄 Use feedback loops for continuous improvement")
        
        # Always include general recommendations
        recommendations.extend([
            "💡 Start every complex task with system capability discovery",
            "🎨 Use workflow patterns: [discuss] → [code] → [review]",
            "📈 Monitor effectiveness scores and adjust approach"
        ])
        
        return recommendations[:5]  # Limit to top 5
    
    def get_real_time_guidance(self, current_query: str) -> List[str]:
        """Get real-time guidance for current query."""
        guidance = []
        
        query_lower = current_query.lower()
        
        # Check if query suggests llmstruct should be used
        technical_keywords = ["analyze", "implement", "debug", "refactor", "architecture"]
        if any(keyword in query_lower for keyword in technical_keywords):
            guidance.append("🎯 This query should use llmstruct system - add context tags!")
        
        # Suggest specific tags
        if "debug" in query_lower or "error" in query_lower:
            guidance.append("🐛 Suggested tags: [debug] for error analysis")
        
        if "implement" in query_lower or "code" in query_lower:
            guidance.append("💻 Suggested tags: [code] for implementation")
        
        if "plan" in query_lower or "discuss" in query_lower:
            guidance.append("💭 Suggested tags: [discuss] for planning (no file changes)")
        
        # Tool suggestions
        if "find" in query_lower or "search" in query_lower:
            guidance.append("🔍 Consider using codebase_search for semantic exploration")
        
        if "struct" in query_lower or "architecture" in query_lower:
            guidance.append("📊 Use struct.json analysis for project understanding")
        
        return guidance
    
    def _load_events(self) -> None:
        """Load events from disk."""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.events = [
                        AIUsageEvent(**event_data) for event_data in data
                    ]
                logger.info(f"Loaded {len(self.events)} AI usage events")
        except Exception as e:
            logger.error(f"Failed to load events: {e}")
            self.events = []
    
    def _save_events(self) -> None:
        """Save events to disk."""
        try:
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.events_file, 'w') as f:
                json.dump([asdict(event) for event in self.events], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save events: {e}")
    
    def _save_analysis(self, analysis: AIBehaviorAnalysis) -> None:
        """Save behavior analysis to disk."""
        try:
            self.analysis_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.analysis_file, 'w') as f:
                json.dump(asdict(analysis), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
    
    def get_monitoring_report(self) -> str:
        """Get comprehensive monitoring report."""
        analysis = self.analyze_behavior_trends()
        
        return f"""
🤖 **AI SELF-MONITORING REPORT**
===============================

📊 **Behavior Analysis (Last 7 days):**
├── LLMStruct Usage Rate: {analysis.llmstruct_usage_rate:.1%}
├── Context Awareness: {analysis.context_awareness_score:.1%}  
├── Tool Diversity: {analysis.tool_usage_diversity:.1%}
└── Guidance Adherence: {analysis.guidance_adherence:.1%}

✅ **Strengths:**
{chr(10).join(f"   • {strength}" for strength in analysis.strengths)}

⚠️ **Areas for Improvement:**
{chr(10).join(f"   • {improvement}" for improvement in analysis.improvement_needed)}

💡 **Recommendations:**
{chr(10).join(f"   • {rec}" for rec in analysis.recommendations)}

📈 **Total Events Tracked:** {len(self.events)}
🕒 **Last Analysis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 **Next Steps:** {"Use middleware.force_llmstruct_mode() for strict enforcement" if analysis.llmstruct_usage_rate < 0.7 else "Continue current approach - performing well!"}
"""


# Global monitor instance
_monitor_instance = None


def initialize_ai_monitor(project_root: str) -> AISelfMonitor:
    """Initialize global AI monitor."""
    global _monitor_instance
    _monitor_instance = AISelfMonitor(project_root)
    return _monitor_instance


def get_ai_monitor() -> Optional[AISelfMonitor]:
    """Get current AI monitor instance."""
    return _monitor_instance


def record_ai_usage(
    query: str,
    tools_used: List[str],
    used_llmstruct: bool = False,
    context_tags: List[str] = None,
    metadata: Dict[str, Any] = None
) -> None:
    """Global function to record AI usage."""
    if _monitor_instance:
        _monitor_instance.record_ai_interaction(
            query, tools_used, used_llmstruct, context_tags, metadata
        ) 