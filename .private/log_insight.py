#!/usr/bin/env python3
"""
Quick insight logging helper for workflow optimization
Usage: python .private/log_insight.py "category" "type" "insight text"
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def log_insight(category, insight_type, insight_text, context="", solution="", improvement=""):
    """Log a workflow insight to the JSON file"""
    
    insights_file = Path(__file__).parent / "context_insights.json"
    
    # Load existing insights
    if insights_file.exists():
        with open(insights_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "version": "0.1.0",
            "description": "Real-time insights collection for AI workflow optimization",
            "current_session": "SES-E5-001",
            "insights": [],
            "patterns": {"successful": [], "problematic": []},
            "cursorrules_queue": [],
            "next_review": ""
        }
    
    # Add new insight
    new_insight = {
        "timestamp": datetime.now().isoformat() + "Z",
        "category": category,
        "type": insight_type,  # "issue", "success", "pattern", "improvement"
        "insight": insight_text
    }
    
    if context:
        new_insight["context"] = context
    if solution:
        new_insight["solution"] = solution
    if improvement:
        new_insight["cursorrules_improvement"] = improvement
    
    data["insights"].append(new_insight)
    
    # Save back
    with open(insights_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Logged {insight_type} insight in {category}: {insight_text}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python .private/log_insight.py <category> <type> <insight>")
        print("Types: issue, success, pattern, improvement")
        print("Categories: dependency_management, cli_integration, session_management, testing, context_optimization")
        sys.exit(1)
    
    category = sys.argv[1]
    insight_type = sys.argv[2] 
    insight_text = " ".join(sys.argv[3:])
    
    log_insight(category, insight_type, insight_text) 