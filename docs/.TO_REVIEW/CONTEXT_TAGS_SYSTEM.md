# 🏷️ Context Tags System for AI Integration

**Discovered from existing llmstruct workflow - Ready for CursorAIBridge integration**

## 📌 **Core Context Tags**

### **Basic Work Modes:**
- `[discuss]` - Planning, ideation, no file changes
- `[meta]` - Working on LLM interaction mechanisms, tooling
- `[llmstruct]` - Core project development
- `[code]` - Pure implementation work
- `[docs]` - Documentation focused
- `[plan]` - Strategic planning, roadmaps
- `[session]` - Session management work
- `[debug]` - Troubleshooting, fixing issues
- `[test]` - Testing, validation
- `[refactor]` - Code restructuring
- `[review]` - Code review and analysis

### **Smart Mode Combinations:**
- `[discuss][meta]` - Planning LLM interaction improvements
- `[plan][llmstruct]` - Strategic project planning
- `[code][debug]` - Implementation + troubleshooting
- `[docs][meta]` - Documenting LLM interaction patterns
- `[code][test]` - Implementation with testing
- `[review][security]` - Security-focused code review

## 🎯 **Context Template from AI Constraints**

```
"request_template": {
  "what": "Describe task (e.g., 'Generate README')",
  "format": "Specify output (e.g., 'Markdown, Russian, GPL-3.0')",
  "context": "[llmstruct] or [meta]",
  "files": "List files (e.g., 'tasks.json, artifact_id: XYZ')",
  "example": "Generate Russian README for llmstruct [llmstruct], use tasks.json (artifact_id: f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7), GPL-3.0."
}
```

## 🔧 **Permission System per Mode**

### **Mode Permissions Matrix:**

| Mode | Capabilities | File Restrictions | Safe Operations |
|------|-------------|------------------|-----------------|
| `[code]` | filesystem, execution | !config/, !.env, !*.key | read_files, write_code, run_tests |
| `[discuss]` | filesystem:read | !config/, !.env | read_files, view_docs, analyze_structure |
| `[debug]` | filesystem, execution, network:local | !config/, !.env | read_logs, run_debug_commands |
| `[meta]` | filesystem | !.env, !*.key | read_docs, write_docs, manage_structure |
| `[review]` | filesystem:read | !.env | read_files, analyze_code, suggest_improvements |

### **Smart Combinations:**
- `[code][debug]` - Enhanced debugging in development
- `[discuss][meta]` - Planning and documentation
- `[review][security]` - Security-focused code review

## 🤖 **AI Integration Usage**

### **For CursorAIBridge:**

```python
def get_context_with_tags(self, query: str, tags: List[str] = None) -> Dict[str, Any]:
    """Get AI context with mode-aware permissions."""
    
    # Parse tags from query if not provided
    if not tags:
        tags = self._extract_tags_from_query(query)
    
    # Get mode permissions
    permissions = self._get_mode_permissions(tags)
    
    # Apply context restrictions
    context = self._get_filtered_context(permissions)
    
    return {
        "context": context,
        "active_modes": tags,
        "permissions": permissions,
        "ai_delegation": self._get_ai_for_modes(tags),
        "workflow_suggestions": self._get_mode_suggestions(tags)
    }

def _extract_tags_from_query(self, query: str) -> List[str]:
    """Extract [tag] patterns from query."""
    import re
    return re.findall(r'\[([^\]]+)\]', query)

def _get_ai_for_modes(self, tags: List[str]) -> str:
    """Determine optimal AI based on mode tags."""
    if any(tag in ["code", "debug", "refactor"] for tag in tags):
        return "grok"  # Technical implementation
    elif any(tag in ["docs", "discuss", "meta", "plan"] for tag in tags):
        return "claude"  # Documentation and planning
    else:
        return "claude"  # Default fallback
```

### **Query Examples:**

```bash
# Technical implementation with debugging
python test_ai_bridge.py context "[code][debug] fix authentication bug"

# Documentation planning
python test_ai_bridge.py context "[docs][meta] plan API documentation structure"

# Strategic planning
python test_ai_bridge.py context "[plan][llmstruct] roadmap for v0.4.0"

# Code review
python test_ai_bridge.py context "[review][security] check user input validation"
```

## 📊 **Context Layers Integration**

### **Layer Mapping by Mode:**

| Mode | Essential | Structural | Operational | Analytical |
|------|-----------|------------|-------------|------------|
| `[code]` | struct.json | schema/ | tasks.json | - |
| `[docs]` | init.json | - | - | docs.json |
| `[meta]` | init.json | copilot/ | - | ideas.json |
| `[plan]` | init.json | - | tasks.json | ideas.json, prs.json |
| `[debug]` | struct.json | cli_enhanced.json | tasks.json | - |

## 🎯 **Practical Implementation**

### **Integration with Existing Systems:**

1. **WorkflowOrchestrator** - Uses tags to determine context scope
2. **CursorAIBridge** - Routes to appropriate AI based on tags
3. **AI Self-Awareness** - Adapts behavior per mode
4. **Context Orchestrator** - Loads appropriate layers per tags

### **Usage in start_development.py:**

```python
def show_context_examples():
    """Show context tag usage examples."""
    print("🏷️  Context Tags Usage:")
    print("   [code] - Implementation work")
    print("   [meta] - LLM/AI system work")
    print("   [docs] - Documentation")
    print("   [debug] - Troubleshooting")
    print("   [plan] - Strategic planning")
    print()
    print("🔄 Combinations:")
    print("   [code][debug] - Debug while coding")
    print("   [docs][meta] - Document AI systems")
    print("   [plan][llmstruct] - Project roadmap")
```

## 🚀 **Next Steps for Integration**

1. **Add tag parsing to CursorAIBridge**
2. **Implement mode-based AI delegation**
3. **Create context filtering per permissions**
4. **Add mode history tracking**
5. **Integrate with WorkspaceStateManager**

## 📝 **Example Session Commands**

```bash
# Start focused coding session
python test_ai_bridge.py context "[code] implement user authentication"

# Planning session
python test_ai_bridge.py context "[plan][meta] design AI integration roadmap"

# Documentation work
python test_ai_bridge.py context "[docs][llmstruct] update README with new features"

# Debug session
python test_ai_bridge.py context "[code][debug] fix performance issues in struct parsing"

# Review work
python test_ai_bridge.py context "[review] analyze code quality in cursor_integration.py"
```

---

**🎯 This system is already partially implemented in llmstruct and ready for full CursorAIBridge integration!** 