# VS Code Copilot Integration Guide

## Overview

LLMStruct provides seamless integration with VS Code Copilot through a sophisticated context management system. This guide covers the proper initialization methods, configuration options, and best practices for VS Code Copilot integration.

## Architecture

### CopilotContextManager

The core component for VS Code Copilot integration is the `CopilotContextManager` class, which provides:

- **4-level context hierarchy** (Essential → Structural → Operational → Analytical)
- **Event-driven context loading** based on code editing activities
- **Smart context attachment** with configurable trigger rules
- **Validation and safety features** for code changes

### Context Layers

#### 1. Essential Layer (Priority 1)
- **Auto-attach**: Always loaded
- **Sources**: `struct.json`, `data/init.json`
- **Purpose**: Core project structure and initialization context
- **Token budget**: ~500 tokens

#### 2. Structural Layer (Priority 2)
- **Auto-attach**: On code editing
- **Sources**: `data/cli_enhanced.json`, `schema/base_schema.json`
- **Purpose**: CLI workflows and architectural schemas
- **Token budget**: ~1000 tokens

#### 3. Operational Layer (Priority 3)
- **Auto-attach**: On request
- **Sources**: `data/tasks.json`, `data/cli_queue_enhanced.json`
- **Purpose**: Task management and queue operations
- **Token budget**: ~2000 tokens

#### 4. Analytical Layer (Priority 4)
- **Auto-attach**: Smart (based on context analysis)
- **Sources**: `data/ideas.json`, `data/prs.json`, `docs.json`
- **Purpose**: Ideas, pull requests, and documentation context
- **Token budget**: ~4000 tokens

## Initialization Methods

### Method 1: Direct Initialization (Recommended)

```python
from llmstruct.copilot import initialize_copilot

# Initialize with project root
manager = initialize_copilot("/path/to/project")

# Initialize with custom config
manager = initialize_copilot(
    project_root="/path/to/project",
    config_path="/path/to/custom/copilot_init.json"
)
```

### Method 2: Class-based Initialization

```python
from llmstruct.copilot import CopilotContextManager

# Basic initialization
manager = CopilotContextManager(project_root="/path/to/project")

# With custom configuration
manager = CopilotContextManager(
    project_root="/path/to/project",
    config_path="/custom/path/copilot_init.json"
)
```

### Method 3: CLI Initialization

```bash
# Initialize copilot configuration
llmstruct copilot init

# Initialize with force (overwrite existing)
llmstruct copilot init --force

# Check initialization status
llmstruct copilot status
```

## Configuration

### Main Configuration File (`data/copilot_init.json`)

```json
{
  "copilot_init": {
    "version": "1.0.0",
    "description": "LLMStruct Copilot Integration",
    "integration_mode": "hybrid_context",
    
    "context_layers": {
      "essential": {
        "priority": 1,
        "auto_attach": true,
        "sources": ["struct.json", "data/init.json"],
        "description": "Core project structure"
      },
      "structural": {
        "priority": 2,
        "auto_attach": "on_code_edit",
        "sources": ["data/cli_enhanced.json", "schema/base_schema.json"],
        "description": "CLI workflows and schemas"
      }
    },
    
    "copilot_triggers": {
      "file_operations": {
        "on_file_create": {
          "layers": ["essential", "structural"],
          "scope": "local"
        },
        "on_file_edit": {
          "layers": ["essential", "operational"],
          "scope": "local"
        }
      },
      
      "code_events": {
        "function_creation": {
          "attach_context": ["structural", "essential"],
          "validation_rules": ["validate_json_schema"]
        },
        "class_creation": {
          "attach_context": ["structural", "analytical"],
          "validation_rules": ["check_circular_dependencies"]
        }
      }
    }
  }
}
```

### Token Budget Configuration

```json
{
  "token_budgets": {
    "vscode_copilot": {
      "max_tokens": 2000,
      "priority_files": ["struct.json", "data/init.json"],
      "essential_sections": ["summary", "structure", "active_tasks"],
      "exclude_sections": ["full_history", "archived_data"]
    }
  }
}
```

## Event-Driven Context Loading

### Triggering Context Events

```python
from llmstruct.copilot import CopilotEvent, trigger_copilot_event

# Create an event
event = CopilotEvent(
    event_type="file_edit",
    file_path="src/main.py",
    scope="local",
    metadata={
        "user": "developer",
        "change_type": "function_addition"
    }
)

# Trigger event and get context
context = trigger_copilot_event(manager, event.event_type, event.file_path)
```

### Event Types

#### File Operations
- `file_create`: New file created
- `file_edit`: Existing file modified  
- `file_delete`: File deleted

#### Code Events
- `function_creation`: New function added
- `class_creation`: New class added
- `import_changes`: Import statements modified

#### Workflow Events
- `cli_command_detected`: CLI command execution detected
- `queue_operation`: Queue-based operation triggered
- `task_creation`: New task created

## VS Code Integration Patterns

### Pattern 1: Real-time Context Adaptation

```python
# Monitor file changes and adapt context
def on_file_change(file_path, change_type):
    event = CopilotEvent(
        event_type=f"file_{change_type}",
        file_path=file_path
    )
    
    context = manager.get_context_for_event(event)
    return context
```

### Pattern 2: Smart Code Completion

```python
# Get context-aware completions
def get_completions(code, file_path, cursor_pos):
    suggestions = manager.suggest_completion(
        current_code=code,
        file_path=file_path,
        cursor_position=cursor_pos
    )
    return suggestions
```

### Pattern 3: Change Validation

```python
# Validate changes before applying
def validate_code_change(file_path, change_type):
    result = manager.validate_change(file_path, change_type)
    
    if not result["valid"]:
        print("Validation failed:")
        for error in result["errors"]:
            print(f"  - {error}")
        return False
    
    return True
```

## CLI Commands for Copilot Management

### Status and Information
```bash
# Show current context status
llmstruct copilot status

# List available layers
llmstruct copilot status --layers

# Show configuration
llmstruct copilot config
```

### Context Management
```bash
# Load specific context layer
llmstruct copilot load essential

# Unload context layer
llmstruct copilot unload analytical

# Refresh all contexts
llmstruct copilot refresh
```

### Smart Features
```bash
# Get smart suggestions
llmstruct copilot suggest "implement user authentication"

# Validate file changes
llmstruct copilot validate src/auth.py --change-type edit

# Export context for analysis
llmstruct copilot export --format json --output context.json
```

## Integration with Context Orchestrator

### Using Both Systems Together

```python
from llmstruct.context_orchestrator import SmartContextOrchestrator
from llmstruct.copilot import initialize_copilot

# Initialize both systems
orchestrator = SmartContextOrchestrator(project_root)
copilot_manager = initialize_copilot(project_root)

# Get optimized context for VS Code Copilot
vscode_context = orchestrator.get_context_for_scenario(
    "vscode_copilot",
    file_path="current_file.py"
)

# Use copilot manager for event handling
event = CopilotEvent(event_type="file_edit", file_path="current_file.py")
copilot_context = copilot_manager.get_context_for_event(event)

# Merge contexts for comprehensive coverage
merged_context = {**vscode_context, **copilot_context}
```

## Best Practices

### Initialization
1. **Initialize early**: Set up copilot context as soon as VS Code starts
2. **Use default paths**: Stick to standard configuration locations
3. **Handle failures gracefully**: Always check initialization success
4. **Configure token budgets**: Set appropriate limits for your workflow

### Context Management
1. **Load progressively**: Start with essential, expand as needed
2. **Monitor performance**: Track context loading times
3. **Cache efficiently**: Reuse contexts when possible
4. **Validate regularly**: Ensure context integrity

### Event Handling
1. **Use appropriate events**: Match events to actual user actions
2. **Scope correctly**: Use local scope for file changes, global for project changes
3. **Include metadata**: Provide rich context in event metadata
4. **Handle errors**: Gracefully handle event processing failures

### Performance Optimization
1. **Lazy loading**: Load contexts only when needed
2. **Smart caching**: Cache frequently used contexts
3. **Token awareness**: Respect token budgets and limits
4. **Batch operations**: Group related context operations

## Troubleshooting

### Common Issues

#### 1. Configuration Not Found
```bash
Error: Copilot config not found at data/copilot_init.json
```
**Solution**: Run `llmstruct copilot init` to create default configuration.

#### 2. Context Loading Failure
```bash
Error: Failed to load context layer: essential
```
**Solution**: Check if source files exist and are readable.

#### 3. Token Budget Exceeded
```bash
Warning: Context exceeds token budget (2500 > 2000)
```
**Solution**: Adjust token budget or reduce context sources.

#### 4. Validation Errors
```bash
Error: JSON schema validation failed
```
**Solution**: Check source files for valid JSON format.

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with debug info
manager = initialize_copilot(project_root)
manager.logger.setLevel(logging.DEBUG)
```

### Health Check

```bash
# Run comprehensive health check
llmstruct copilot status --verbose

# Test all layers
llmstruct copilot test --all-layers

# Validate configuration
llmstruct copilot validate --config
```

## Related Documentation

- [Context Orchestration Architecture](context_orchestration_architecture.md) - Overall context system
- [Session Management](../data/sessions/README.md) - AI session tracking
- [CLI Modular Architecture](cli_modular_architecture.md) - CLI integration
- [Performance Monitoring](performance_monitoring.md) - Optimization guidelines
