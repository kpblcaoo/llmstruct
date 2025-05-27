    # GitHub Projects Export - Complete Guide

## Overview

The GitHub Projects export system (`gh-view`) allows you to automatically export LLMStruct's tasks and ideas from local JSON files to GitHub Projects as project cards. This feature enables seamless integration between local project management and GitHub's collaborative tools.

## System Architecture

### Core Components

1. **Base Exporter** (`src/llmstruct/gh_view.py`)
   - `GitHubProjectsExporter` class for core functionality
   - Data formatting and transformation logic
   - GitHub CLI integration wrapper
   - ID mapping system for synchronization

2. **Extended Export Script** (`scripts/export_to_github_projects.py`)
   - `GitHubProjectsExportScript` class with CLI interface
   - Advanced filtering and batch operations
   - Error handling and retry logic
   - Comprehensive export statistics

3. **Bash Helper** (`scripts/gh_export.sh`)
   - Convenient shell wrapper for common operations
   - Quick setup and status checking
   - Error handling and colored output
   - Project listing and authentication

### Data Flow Architecture

```
data/tasks.json  ──┐
                   ├─► GitHubProjectsExporter ──► GitHub CLI ──► GitHub Projects
data/ideas.json  ──┘                              (gh projects)    (Project Cards)
        │                                              │
        ├─► Status/Priority Mapping ───────────────────┤
        ├─► Content Formatting ────────────────────────┤
        └─► ID Mapping (data/gh_mapping.json) ─────────┘
```

## Configuration

### Main Configuration (`llmstruct.toml`)

```toml
[gh_view]
# GitHub repository settings
default_owner = "your-github-username"
default_repo = "your-repository"
default_project_number = 1

# Export settings
export_tasks = true
export_ideas = true
dry_run_default = true

# Status mapping
[gh_view.status_mapping]
proposed = "Todo"
in_progress = "In Progress"
completed = "Done"
blocked = "Blocked"
cancelled = "Cancelled"

# Priority mapping
[gh_view.priority_mapping]
critical = "🔴 Critical"
high = "🟠 High"
medium = "🟡 Medium"
low = "🟢 Low"
```

### ID Mapping System (`data/gh_mapping.json`)

```json
{
  "version": "1.0.0",
  "last_updated": "2025-05-26T10:30:00Z",
  "tasks": {
    "TSK-001": "PVTI_lADOA1234567890",
    "TSK-002": "PVTI_lADOB2345678901"
  },
  "ideas": {
    "IDEA-001": "PVTI_lADOC3456789012",
    "IDEA-002": "PVTI_lADOD4567890123"
  },
  "metadata": {
    "total_exported": 45,
    "last_export_count": 12,
    "export_history": []
  }
}
```

## Usage Guide

### Prerequisites

1. **Install GitHub CLI**:
   ```bash
   # Ubuntu/Debian
   sudo apt install gh
   
   # macOS
   brew install gh
   
   # Windows
   winget install GitHub.cli
   ```

2. **Authenticate GitHub CLI**:
   ```bash
   gh auth login
   ```

3. **Verify Authentication**:
   ```bash
   ./scripts/gh_export.sh check
   ```

### Basic Export Operations

#### 1. Dry Run (Preview Export)
```bash
# Preview all data
./scripts/gh_export.sh preview 1

# Preview with Python script (more detailed)
python scripts/export_to_github_projects.py 1 --dry-run
```

#### 2. Full Export
```bash
# Export all tasks and ideas
./scripts/gh_export.sh export 1

# Execute export with Python script
python scripts/export_to_github_projects.py 1 --execute
```

#### 3. Selective Export
```bash
# Export only tasks
./scripts/gh_export.sh export-tasks 1

# Export only ideas
./scripts/gh_export.sh export-ideas 1

# Export with specific owner/repo
./scripts/gh_export.sh export 1 --owner kpblcaoo --repo llmstruct
```

### Advanced Filtering

#### Filter by Status
```bash
# Export only proposed and in-progress items
python scripts/export_to_github_projects.py 1 --execute \
  --status proposed in_progress

# Filter preview
./scripts/gh_export.sh filter-preview 1 --status proposed,in_progress
```

#### Filter by Priority
```bash
# Export only high and critical priority items
python scripts/export_to_github_projects.py 1 --execute \
  --priority high critical

# Combined filters
python scripts/export_to_github_projects.py 1 --execute \
  --status proposed in_progress \
  --priority high medium
```

#### Export Specific Data Types
```bash
# Tasks only with filters
python scripts/export_to_github_projects.py 1 --execute \
  --tasks-only --status in_progress

# Ideas only with filters  
python scripts/export_to_github_projects.py 1 --execute \
  --ideas-only --priority high
```

### Project Management

#### List Available Projects
```bash
# List all projects
./scripts/gh_export.sh list-projects

# List projects for specific repo
./scripts/gh_export.sh list-projects --owner kpblcaoo --repo llmstruct
```

#### Check Export Status
```bash
# Check mapping file
cat data/gh_mapping.json | jq '.metadata'

# Count exported items
echo "Tasks: $(cat data/gh_mapping.json | jq '.tasks | length')"
echo "Ideas: $(cat data/gh_mapping.json | jq '.ideas | length')"
```

## Data Format Specifications

### Task Export Format

**GitHub Card Title**: `[TSK-001] Implement user authentication`

**GitHub Card Body**:
```markdown
**Task ID:** TSK-001
**Status:** in_progress
**Priority:** high
**Effort:** 5d
**Assignee:** @kpblcaoo
**Dependencies:** TSK-002, TSK-003
**Target Release:** v0.2.0

**Description:**
Implement comprehensive user authentication system with JWT tokens and role-based access control.

**Implementation Details:**
- OAuth2 integration
- JWT token management
- Role-based permissions
```

**Labels**: `task`, `priority-high`, `status-in_progress`

### Idea Export Format

**GitHub Card Title**: `[IDEA-001] Smart Context Orchestration`

**GitHub Card Body**:
```markdown
**Idea ID:** IDEA-001
**Status:** proposed
**Priority:** high
**Category:** architecture

**Description:**
Implement smart context orchestration system for optimized LLM integration scenarios.

**Implementation Notes:**
Multi-mode context system with token budgeting and scenario-specific optimization.
```

**Labels**: `idea`, `category-architecture`, `priority-high`

## Command Reference

### Python Script Options

```bash
python scripts/export_to_github_projects.py <project_number> [OPTIONS]

Required:
  project_number          GitHub Project number

Optional:
  --owner OWNER          Repository owner/organization
  --repo REPO            Repository name
  --dry-run              Preview only (default)
  --execute              Perform actual export
  --tasks-only           Export only tasks
  --ideas-only           Export only ideas
  --status STATUS [...]  Filter by status
  --priority PRIORITY [...]  Filter by priority
```

### Bash Helper Commands

```bash
./scripts/gh_export.sh <command> [options]

Commands:
  check                     Check GitHub CLI setup
  list-projects            List available projects
  preview <project_id>     Preview export (dry-run)
  export <project_id>      Full export
  export-tasks <project_id>    Export tasks only
  export-ideas <project_id>    Export ideas only
  filter-preview <project_id>  Preview with filters

Options:
  --owner <owner>          Repository owner
  --repo <repo>           Repository name
  --status <statuses>     Comma-separated status list
  --priority <priorities> Comma-separated priority list
```

## Integration Workflows

### Development Workflow

1. **Local Development**:
   ```bash
   # Work with local data
   vi data/tasks.json
   vi data/ideas.json
   ```

2. **Preview Changes**:
   ```bash
   ./scripts/gh_export.sh preview 1
   ```

3. **Export to GitHub**:
   ```bash
   ./scripts/gh_export.sh export 1
   ```

4. **Team Collaboration**:
   - Team members view/edit cards in GitHub Projects
   - Status updates tracked in GitHub interface
   - Comments and discussions in GitHub

### CI/CD Integration

```yaml
# .github/workflows/sync-projects.yml
name: Sync GitHub Projects
on:
  push:
    paths:
      - 'data/tasks.json'
      - 'data/ideas.json'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install GitHub CLI
        run: sudo apt install gh
      - name: Sync Projects
        run: ./scripts/gh_export.sh export 1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit mapping updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/gh_mapping.json
          git commit -m "Update GitHub Projects mapping" || exit 0
          git push
```

### Automation Scripts

#### Daily Export Automation
```bash
#!/bin/bash
# scripts/daily_export.sh

# Check for new/updated items
if [ "$(git diff --name-only data/tasks.json data/ideas.json)" ]; then
    echo "📊 Changes detected, exporting to GitHub..."
    ./scripts/gh_export.sh export 1 --status proposed in_progress
    
    # Commit mapping updates
    git add data/gh_mapping.json
    git commit -m "Auto-update GitHub Projects mapping"
fi
```

#### Selective Export by Labels
```bash
#!/bin/bash
# Export high-priority items only

python scripts/export_to_github_projects.py 1 --execute \
    --priority high critical \
    --status proposed in_progress planned
```

## Error Handling and Troubleshooting

### Common Issues

#### 1. GitHub CLI Not Found
```
Error: GitHub CLI (gh) not found. Please install it first.
```
**Solution**: Install GitHub CLI from https://cli.github.com/

#### 2. Authentication Issues
```
Error: GitHub CLI issue: not logged into any GitHub hosts
```
**Solution**: Run `gh auth login` and follow authentication flow

#### 3. Project Access Issues
```
Error: Failed to list projects: insufficient permissions
```
**Solution**: Ensure proper repository/organization access rights

#### 4. Mapping File Corruption
```
Error: Could not save mapping: Permission denied
```
**Solution**: Check file permissions on `data/gh_mapping.json`

### Debug Mode

#### Enable Verbose Output
```bash
export DEBUG=1
./scripts/gh_export.sh export 1 --dry-run
```

#### Check Mapping Consistency
```bash
python -c "
import json
with open('data/gh_mapping.json') as f:
    mapping = json.load(f)
    print(f'Tasks mapped: {len(mapping.get(\"tasks\", {}))}')
    print(f'Ideas mapped: {len(mapping.get(\"ideas\", {}))}')
    print(f'Last updated: {mapping.get(\"last_updated\", \"unknown\")}')
"
```

#### Validate GitHub CLI Setup
```bash
gh auth status
gh projects list --format json | jq length
```

## Performance and Optimization

### Export Performance

- **Incremental Export**: Only exports new/changed items using ID mapping
- **Batch Operations**: Groups related API calls for efficiency
- **Rate Limiting**: Respects GitHub API limits (5000 requests/hour)
- **Caching**: Local mapping reduces redundant API calls

### Optimization Features

1. **Smart Filtering**: Export only relevant items
2. **Dry-run Mode**: Preview changes without API calls
3. **Mapping System**: Track exported items to avoid duplicates
4. **Error Recovery**: Graceful handling of API failures

### Limits and Considerations

- GitHub API rate limits apply
- Large datasets may require multiple sessions
- Network latency affects export speed
- Project size limits (GitHub Projects capacity)

## Security and Privacy

### Authentication Security
- Uses GitHub CLI secure token storage
- Supports personal access tokens via environment variables
- No credentials stored in configuration files

### Data Privacy
- Only exports non-sensitive project metadata
- Respects gitignore patterns for sensitive files
- Local mapping should be git-ignored if contains sensitive IDs

### Permissions
- Requires repository access for target projects
- Organization projects may require additional permissions
- Read/write access needed for card creation and updates

## Future Enhancements

### Planned Features

1. **Bidirectional Sync**: Import GitHub changes back to local data
2. **Real-time Updates**: Webhook-based synchronization
3. **GraphQL API**: Direct GitHub API integration (replace CLI dependency)
4. **Multi-project Support**: Export to multiple GitHub Projects
5. **Template System**: Customizable card templates
6. **Advanced Filtering**: Complex query-based filtering
7. **Analytics Dashboard**: Export metrics and insights

### Integration Opportunities

1. **GitHub Actions**: Automated sync workflows
2. **VS Code Extension**: GUI for export operations
3. **Slack/Teams Integration**: Export notifications
4. **Custom Fields**: Automatic field assignment via GitHub API
5. **Project Templates**: Standardized project structures

## API Reference

### GitHubProjectsExporter Class

```python
from llmstruct.gh_view import GitHubProjectsExporter

# Initialize exporter
exporter = GitHubProjectsExporter(config_path="llmstruct.toml")

# Load official data
tasks, ideas = exporter.load_official_data()

# Format data for GitHub
task_card = exporter.format_task_for_github(task)
idea_card = exporter.format_idea_for_github(idea)

# Export to GitHub (via extended script class)
from scripts.export_to_github_projects import GitHubProjectsExportScript
script_exporter = GitHubProjectsExportScript(dry_run=False)
script_exporter.export_tasks_to_project(tasks, project_number=1)
```

### Key Methods

- `load_official_data()`: Load tasks.json and ideas.json
- `format_task_for_github(task)`: Convert task to GitHub card format
- `format_idea_for_github(idea)`: Convert idea to GitHub card format  
- `_run_gh_command(command)`: Execute GitHub CLI commands
- `_load_mapping()` / `_save_mapping()`: Manage ID mappings
- `export_tasks_to_project()`: Export tasks with mapping
- `export_ideas_to_project()`: Export ideas with mapping
- `filter_data()`: Apply status/priority filters

## Related Documentation

- [Context Orchestration Architecture](context_orchestration_architecture.md) - Overall system context
- [Session Management](../data/sessions/README.md) - AI session tracking
- [CLI Modular Architecture](cli_modular_architecture.md) - CLI system integration
- [VS Code Integration](copilot_integration.md) - Development environment integration
