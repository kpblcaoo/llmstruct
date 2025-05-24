# LLMStruct CLI - Modular Architecture Guide

## Overview

LLMStruct CLI has been refactored into a modular architecture that provides enhanced functionality, better maintainability, and seamless integration with auto-update workflows and Copilot systems.

## Architecture Components

### Core Modules

#### 1. CLICore (`cli_core.py`)
- **Purpose**: Central coordination and lifecycle management
- **Responsibilities**: 
  - Initialize and manage cache, copilot, and configuration systems
  - Coordinate component interactions
  - Handle interactive mode execution
- **Key Classes**: `CLICore`, factory function `create_cli_core()`

#### 2. CLIConfig (`cli_config.py`)
- **Purpose**: Configuration management from `llmstruct.toml`
- **Responsibilities**:
  - Load and validate configuration files
  - Provide typed access to settings
  - Manage gitignore patterns and project settings
- **Key Classes**: `CLIConfig`

#### 3. CLIUtils (`cli_utils.py`)
- **Purpose**: Utility functions and common operations
- **Responsibilities**:
  - File and directory operations with security validation
  - JSON handling and validation
  - Logging and error management
- **Key Classes**: `CLIUtils`

#### 4. CommandProcessor (`cli_commands.py`)
- **Purpose**: Command parsing and execution
- **Responsibilities**:
  - Process CLI commands with `/` prefix
  - Handle auto-update, struct status, workflow triggers
  - Integrate with cache and copilot systems
- **Key Classes**: `CommandProcessor`

#### 5. CopilotContextManager (`copilot.py`)
- **Purpose**: VSCode Copilot integration and context management
- **Responsibilities**:
  - 4-level context system (init, struct, cli, enhanced)
  - Event system for workflow triggers
  - Context validation and optimization
- **Key Classes**: `CopilotContextManager`, `CopilotEvent`

## New CLI Commands

### Auto-Update Commands

#### `/auto-update`
Triggers automatic update of `struct.json` using the auto-update script.

```bash
Prompt> /auto-update
✅ Auto-update struct.json completed successfully
```

#### `/struct status`
Shows detailed information about `struct.json` file and auto-update system.

```bash
Prompt> /struct status
struct.json status:
  📁 Path: /path/to/struct.json
  📅 Modified: Sat May 24 05:00:29 2025
  📏 Size: 96412 bytes
  🔄 Auto-update: Available
```

#### `/struct validate`
Validates `struct.json` format and content.

```bash
Prompt> /struct validate
✅ struct.json is valid JSON
  📊 Contains 45 files
  🎯 Goals: 3
```

### Workflow Commands

#### `/workflow trigger`
Manually triggers workflow events with auto-update integration.

```bash
Prompt> /workflow trigger
✅ Workflow event triggered: manual_1748055279
✅ Auto-update triggered by workflow completed
```

### Enhanced Existing Commands

#### `/queue run`
Enhanced command queue processing with workflow support.

#### `/cache stats`
Improved cache statistics with modular integration.

#### `/copilot status`
Copilot system status and context information.

## Integration Features

### 1. Auto-Update Integration
- **Seamless workflow integration**: Auto-update triggers on LLM events
- **Git hooks support**: Automatic updates on file changes
- **Cron integration**: Scheduled updates
- **Manual triggers**: CLI commands for immediate updates

### 2. Copilot Context System
- **4-level context hierarchy**:
  - Level 1: `init.json` - Basic project info
  - Level 2: `struct.json` - Full project structure
  - Level 3: `cli.json` - CLI-specific context
  - Level 4: `enhanced.json` - Full enhanced context
- **Event-driven**: Workflow events trigger context updates
- **Validation**: Automatic context validation and optimization

### 3. Cache Integration
- **Smart caching**: Automatic caching of generated content
- **Cache statistics**: Detailed usage and performance metrics
- **Cache management**: Clear, list, and analyze cache content

## Configuration

### llmstruct.toml Example

```toml
[cli]
language = "python"
include_patterns = ["*.py", "*.js", "*.ts"]
exclude_patterns = ["tests/*", "build/*"]
exclude_dirs = ["venv", "node_modules", "build", "tmp"]
use_gitignore = true
include_ranges = false
include_hashes = false
max_file_size = 1048576

[auto_update]
enabled = true
check_interval = 300
git_hooks = true
on_file_change = true

[copilot]
enabled = true
context_levels = ["init", "struct", "cli", "enhanced"]
auto_refresh = true
validation_enabled = true
```

## Usage Examples

### Basic Interactive Session

```bash
$ python3 -m llmstruct.cli interactive . --context struct.json
Interactive LLMStruct CLI. Type 'exit' to quit, '/view <path>' to read files/folders, 
'/queue run' to process command queue, '/cache stats' for cache info, 
'/auto-update' for struct.json auto-update, '/struct status' for struct info, 
'/workflow trigger' for workflow events, or enter /commands to scan/write.

Prompt> /struct status
struct.json status:
  📁 Path: /home/project/struct.json
  📅 Modified: Sat May 24 05:00:29 2025
  📏 Size: 96412 bytes
  🔄 Auto-update: Available

Prompt> /auto-update
✅ Auto-update struct.json completed successfully

Prompt> /workflow trigger
✅ Workflow event triggered: manual_1748055279
✅ Auto-update triggered by workflow completed

Prompt> exit
```

### Programmatic Usage

```python
from llmstruct.cli_core import create_cli_core

# Create CLI core instance
cli_core = create_cli_core("/path/to/project")

# Access components
config = cli_core.config
utils = cli_core.utils
commands = cli_core.commands

# Process commands
commands.process_command("/struct status")
commands.process_command("/auto-update")
```

## Migration from Legacy CLI

The modular CLI maintains backward compatibility with the legacy implementation:

1. **Automatic fallback**: If modular components fail, system falls back to legacy CLI
2. **Same command interface**: All existing commands work unchanged
3. **Enhanced functionality**: New commands only available in modular mode
4. **Gradual migration**: Can migrate commands one by one

## Testing

### Integration Tests

```bash
# Run full integration test
python3 test_cli_integration.py

# Test modular components
python3 test_modular_cli.py

# Demo new commands
python3 test_cli_demo.py
```

### Unit Tests

```bash
# Test individual components
python3 -m pytest tests/test_cli_core.py
python3 -m pytest tests/test_cli_commands.py
python3 -m pytest tests/test_copilot.py
```

## Performance Improvements

1. **Modular loading**: Only load required components
2. **Smart caching**: Intelligent cache management
3. **Lazy initialization**: Components loaded on demand
4. **Memory optimization**: Better resource management

## Security Features

1. **Path validation**: Secure file path handling
2. **Input sanitization**: Command input validation  
3. **Permission checks**: File access permission validation
4. **Sandbox execution**: Safe command execution environment

## Future Enhancements

1. **Plugin system**: Support for custom command plugins
2. **API integration**: RESTful API for remote CLI access
3. **Multi-project support**: Handle multiple projects simultaneously
4. **Advanced analytics**: Enhanced usage analytics and reporting

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Permission errors**: Check file system permissions
3. **Configuration errors**: Validate `llmstruct.toml` syntax
4. **Auto-update failures**: Check script permissions and paths

### Debug Mode

```bash
# Enable debug logging
LLMSTRUCT_DEBUG=1 python3 -m llmstruct.cli interactive .
```

### Support

For issues and support:
- Check logs in `llmstruct.log`
- Run integration tests to verify setup
- Review configuration file syntax
- Ensure all required files are present
