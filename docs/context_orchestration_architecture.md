# Smart Context Orchestration Architecture

## Overview

LLMStruct implements a sophisticated **multi-layered context orchestration system** designed to optimize context loading for different LLM integration scenarios. The system addresses the critical challenge of providing the right amount of context for each usage pattern while maintaining performance and token efficiency.

## Architecture Components

### 1. SmartContextOrchestrator (`src/llmstruct/context_orchestrator.py`)

**Purpose**: Orchestrates context loading based on usage scenario and token budget.

#### Context Modes
```python
class ContextMode(Enum):
    FULL = "full"           # For direct CLI calls - unlimited context
    FOCUSED = "focused"     # For VS Code Copilot - optimized context (max 2K tokens)
    MINIMAL = "minimal"     # For quick operations - core only (max 500 tokens)
    SESSION = "session"     # For session-based work - contextual history
```

#### Scenarios Configuration
- **`cli_direct`**: Full context mode, no token restrictions
- **`vscode_copilot`**: Focused mode, 2K token budget
- **`session_work`**: Session mode, 4K token budget with history

#### Key Features
- **Progressive context levels**: CORE → ESSENTIAL → COMPREHENSIVE → FULL
- **Token budgeting**: Automatic context trimming based on token limits
- **Smart source prioritization**: Dynamic weighting of context sources
- **Performance metrics**: Load time, cache hit rate, token usage tracking

### 2. CopilotContextManager (`src/llmstruct/copilot.py`)

**Purpose**: Manages context layers and integration with GitHub Copilot.

#### Context Layers (Priority-Based)
```json
{
  "essential": {
    "priority": 1,
    "auto_attach": true,
    "sources": ["struct.json", "data/init.json"],
    "description": "Core project structure and initialization context"
  },
  "structural": {
    "priority": 2, 
    "auto_attach": "on_code_edit",
    "sources": ["data/cli_enhanced.json", "schema/base_schema.json"],
    "description": "CLI workflows and architectural schemas"
  },
  "operational": {
    "priority": 3,
    "auto_attach": "on_request", 
    "sources": ["data/tasks.json", "data/cli_queue_enhanced.json"],
    "description": "Task management and queue operations"
  },
  "analytical": {
    "priority": 4,
    "auto_attach": "smart",
    "sources": ["data/ideas.json", "data/prs.json", "docs.json"],
    "description": "Ideas, pull requests, and documentation context"
  }
}
```

#### Context Attachment Modes
- **`AUTO`**: Always loaded
- **`ON_EDIT`**: Loaded on code editing events
- **`ON_REQUEST`**: Loaded explicitly when requested
- **`SMART`**: Loaded based on intelligent heuristics

## Event-Driven Context Loading

### Trigger System
The system responds to different types of events:

#### File Operation Triggers
```yaml
file_operations:
  on_file_create:
    layers: ["essential", "structural"]
  on_file_edit:
    layers: ["essential", "operational"]
  on_file_delete:
    layers: ["essential"]
```

#### Code Event Triggers
```yaml
code_events:
  function_creation:
    attach_context: ["structural", "essential"]
  class_creation:
    attach_context: ["structural", "analytical"]
  import_changes:
    attach_context: ["essential"]
```

#### Workflow Triggers
```yaml
workflow_triggers:
  cli_command_detected:
    context_sources: ["data/cli_enhanced.json"]
  queue_operation:
    context_sources: ["data/cli_queue_enhanced.json"]
  task_creation:
    context_sources: ["data/tasks.json"]
```

## Context Validation and Safety

### Validation Rules
- **JSON schema validation**: Ensures context integrity
- **Circular dependency checking**: Prevents infinite loops
- **Task reference validation**: Validates task links in tasks.json
- **Token budget enforcement**: Prevents context overflow

### Safety Features
- **Change validation**: Pre-validates code changes against safety rules
- **Scope limiting**: Prevents unauthorized scope expansion
- **Error isolation**: Graceful handling of context loading failures

## Integration Points

### VS Code Copilot Integration

#### Initialization
```python
# Initialize copilot context manager
manager = initialize_copilot(project_root)

# Trigger event for context loading
event = CopilotEvent(
    event_type="file_edit",
    file_path="src/main.py",
    metadata={"user": "developer"}
)
context = manager.get_context_for_event(event)
```

#### CLI Integration
```bash
# Copilot commands
llmstruct copilot status           # Show context status  
llmstruct copilot load essential   # Load specific layer
llmstruct copilot refresh          # Refresh all contexts
llmstruct copilot suggest "query"  # Get smart suggestions
llmstruct copilot validate file.py # Validate changes
```

### Session Management Integration
- **Session-aware context**: Context adapts to current session type
- **Knowledge cache**: Fast loading of frequently used contexts  
- **Worklog integration**: Context includes progress tracking information
- **Branch-based organization**: Context switches with Git branches

## Performance Optimization

### Caching Strategy
- **Layer-based caching**: Individual layers cached separately
- **Lazy loading**: Contexts loaded only when needed
- **Memory management**: Automatic unloading of unused contexts
- **Cache invalidation**: Smart cache refresh on file changes

### Token Budget Management
```python
@dataclass
class ContextBudget:
    max_tokens: Optional[int]
    priority_files: List[str]
    essential_sections: List[str]
    exclude_sections: List[str] = None
```

### Metrics and Monitoring
- **Load time tracking**: Context loading performance metrics
- **Cache hit rates**: Efficiency of caching strategy
- **Token usage**: Actual vs budgeted token consumption
- **Error rates**: Context loading failure tracking

## Configuration

### Main Configuration (`data/context_orchestration.json`)
```json
{
  "scenarios": {
    "cli_direct": {
      "mode": "FULL",
      "budget": {"max_tokens": null}
    },
    "vscode_copilot": {
      "mode": "FOCUSED", 
      "budget": {"max_tokens": 2000}
    }
  },
  "context_levels": {
    "CORE": {
      "sources": ["init", "current_session"],
      "sections": ["summary", "goals", "current_focus"]
    }
  }
}
```

### Copilot Configuration (`data/copilot_init.json`)
Defines context layers, triggers, and validation rules for VS Code Copilot integration.

## Usage Examples

### Scenario 1: Direct CLI Usage
```python
orchestrator = SmartContextOrchestrator(project_root)
context = orchestrator.get_context_for_scenario("cli_direct")
# Returns: Full context, no token restrictions
```

### Scenario 2: VS Code Copilot Integration
```python
orchestrator = SmartContextOrchestrator(project_root)
context = orchestrator.get_context_for_scenario(
    "vscode_copilot", 
    file_path="src/main.py"
)
# Returns: Focused context, 2K token budget, file-specific
```

### Scenario 3: Session-Based Work
```python
orchestrator = SmartContextOrchestrator(project_root)
context = orchestrator.get_context_for_scenario("session_work")
# Returns: Session context with worklog and knowledge cache
```

## Best Practices

### Context Design
1. **Layer by priority**: Essential context first, analytical context last
2. **Progressive disclosure**: Start minimal, expand as needed
3. **Event-driven loading**: Load context based on actual usage patterns
4. **Token awareness**: Always consider token budgets in context design

### Performance
1. **Cache aggressively**: Cache frequently used contexts
2. **Load lazily**: Don't load until actually needed
3. **Monitor metrics**: Track performance and adjust accordingly
4. **Validate early**: Catch context issues before they propagate

### Integration
1. **Event consistency**: Use consistent event naming across integrations
2. **Error handling**: Graceful degradation when context unavailable
3. **Configuration externalization**: Keep triggers and rules configurable
4. **Documentation synchronization**: Keep docs in sync with implementation

## Future Enhancements

### Planned Features
- **Machine learning-based context prediction**: AI-driven context optimization
- **Real-time context adaptation**: Dynamic context adjustment based on usage
- **Cross-session learning**: Context patterns learned across sessions
- **Integration with external tools**: Broader IDE and tool integration

### Scalability Considerations
- **Distributed context loading**: Support for large codebases
- **Context streaming**: Progressive context delivery for large contexts
- **Multi-tenant support**: Context isolation for different projects
- **Cloud integration**: Remote context storage and synchronization

## Related Documentation

- [Session Management](../data/sessions/README.md) - AI session tracking and management
- [CLI Modular Architecture](cli_modular_architecture.md) - CLI system integration
- [VS Code Integration](copilot_integration.md) - Copilot-specific documentation
- [Performance Monitoring](performance_monitoring.md) - Metrics and optimization
