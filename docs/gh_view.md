# GitHub Projects Integration (gh-view)

**Status**: Complete  
**Version**: v1.0.0  
**Last Updated**: 2025-01-18  
**Feature ID**: gh-view-v1

## Overview

The GitHub Projects integration (`gh-view`) provides a comprehensive solution for exporting LLMStruct's task and idea data to GitHub Projects as project cards. This feature bridges the gap between local project management and GitHub's collaborative project management tools.

## Features

- **Automated Export**: Convert `data/tasks.json` and `data/ideas.json` to GitHub Project cards
- **Bi-directional Mapping**: Maintain ID mapping between local and GitHub items
- **Status Synchronization**: Map local statuses to GitHub Project statuses
- **Rich Metadata**: Export comprehensive task/idea metadata as card content
- **CLI Integration**: Full command-line interface with dry-run capabilities
- **Configuration Support**: TOML-based configuration for flexible setups

## Architecture

### Core Components

1. **GitHubProjectsExporter** (`src/llmstruct/gh_view.py`)
   - Main export logic and data formatting
   - GitHub CLI integration
   - ID mapping management

2. **Export Script** (`scripts/export_to_github_projects.py`)
   - Command-line interface
   - Extended export capabilities
   - Project management functions

3. **Shell Helper** (`scripts/gh_export.sh`)
   - Convenient bash wrapper
   - Quick export commands
   - Status checking utilities

### Data Flow

```
Local Data → Format Conversion → GitHub CLI → GitHub Projects
    ↓              ↓                ↓            ↓
tasks.json → GitHubProjectsExporter → gh CLI → Project Cards
ideas.json → Status/Priority Mapping → API calls → Labels/Status
```

## Configuration

### TOML Configuration

Add to your `llmstruct.toml`:

```toml
[gh_view]
enabled = true
# Optional: Add GitHub API token or repo config here
# api_token = ""
# repo = "owner/repository"
```

### Environment Setup

1. **GitHub CLI Installation**:
   ```bash
   # Install GitHub CLI
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **Authentication**:
   ```bash
   gh auth login
   ```

3. **Projects Extension** (if needed):
   ```bash
   gh extension install github/gh-projects
   ```

## Usage

### Basic Export

```bash
# Export with dry-run (preview only)
python scripts/export_to_github_projects.py --dry-run

# Actual export to GitHub Projects
python scripts/export_to_github_projects.py --export

# Using the shell helper
./scripts/gh_export.sh export --dry-run
```

### Command-Line Options

```bash
python scripts/export_to_github_projects.py [OPTIONS]

Options:
  --dry-run         Preview export without making changes
  --export          Perform actual export to GitHub
  --project-id ID   Specify target GitHub Project ID
  --owner OWNER     Repository owner/organization
  --repo REPO       Repository name
  --config PATH     Custom configuration file path
```

### Shell Helper Commands

```bash
./scripts/gh_export.sh <command> [options]

Commands:
  export      Export tasks and ideas to GitHub Projects
  status      Check export status and mappings
  projects    List available GitHub Projects
  sync        Synchronize existing cards
  help        Show detailed help
```

## Data Mapping

### Task Format Conversion

**Local Task Structure**:
```json
{
  "id": "TSK-001",
  "description": "Implement feature X",
  "status": "in_progress",
  "priority": "high",
  "estimated_effort": "2 days",
  "assignee": "developer1",
  "dependencies": ["TSK-002"],
  "target_release": "v0.3.0"
}
```

**GitHub Project Card**:
```
Title: [TSK-001] Implement feature X

Body:
**Task ID:** TSK-001
**Status:** in_progress
**Priority:** high
**Effort:** 2 days
**Assignee:** developer1
**Dependencies:** TSK-002
**Target Release:** v0.3.0

Labels: task, priority-high
Status: In Progress
```

### Idea Format Conversion

**Local Idea Structure**:
```json
{
  "id": "IDEA-001",
  "title": "New Feature Concept",
  "description": "Detailed description...",
  "status": "proposed",
  "priority": "medium",
  "category": "enhancement",
  "implementation_notes": "Technical notes..."
}
```

**GitHub Project Card**:
```
Title: [IDEA-001] New Feature Concept

Body:
**Idea ID:** IDEA-001
**Status:** proposed
**Priority:** medium
**Category:** enhancement

**Description:**
Detailed description...

**Implementation Notes:**
Technical notes...

Labels: idea, category-enhancement, priority-medium
Status: Todo
```

### Status Mapping

| Local Status | GitHub Status |
|-------------|---------------|
| proposed    | Todo          |
| in_progress | In Progress   |
| active      | In Progress   |
| completed   | Done          |
| implemented | Done          |
| blocked     | Blocked       |
| on_hold     | Blocked       |
| cancelled   | Cancelled     |

## ID Mapping System

The system maintains a bidirectional mapping between local IDs and GitHub Project item IDs in `data/gh_mapping.json`:

```json
{
  "tasks": {
    "TSK-001": "PVTI_lADOBE1234567890_12345",
    "TSK-002": "PVTI_lADOBE1234567890_12346"
  },
  "ideas": {
    "IDEA-001": "PVTI_lADOBE1234567890_12347",
    "IDEA-002": "PVTI_lADOBE1234567890_12348"
  }
}
```

This enables:
- **Update Detection**: Only export changed items
- **Conflict Resolution**: Handle local vs remote changes
- **Sync Operations**: Bidirectional synchronization

## Integration Workflows

### Development Workflow

1. **Local Development**:
   ```bash
   # Work with local tasks/ideas
   python -m llmstruct.tasks add "New task description"
   python -m llmstruct.ideas add "New idea concept"
   ```

2. **Export to GitHub**:
   ```bash
   # Preview changes
   ./scripts/gh_export.sh export --dry-run
   
   # Export to GitHub Projects
   ./scripts/gh_export.sh export
   ```

3. **Collaboration**:
   - Team members can view/edit cards in GitHub Projects
   - Status updates sync back to local data
   - Comments and discussions happen in GitHub

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
        run: ./scripts/gh_export.sh export
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Error Handling

### Common Issues

1. **GitHub CLI Not Found**:
   ```
   Error: GitHub CLI (gh) not found. Please install it first.
   Solution: Install GitHub CLI and authenticate
   ```

2. **Authentication Issues**:
   ```
   Error: GitHub CLI issue: not logged into any GitHub hosts
   Solution: Run 'gh auth login'
   ```

3. **Project Access**:
   ```
   Error: Failed to list projects: insufficient permissions
   Solution: Ensure proper repository/organization access
   ```

### Debugging

Enable verbose output:
```bash
export DEBUG=1
./scripts/gh_export.sh export --dry-run
```

Check mapping consistency:
```bash
python -c "
import json
with open('data/gh_mapping.json') as f:
    mapping = json.load(f)
    print(f'Mapped tasks: {len(mapping.get(\"tasks\", {}))}')
    print(f'Mapped ideas: {len(mapping.get(\"ideas\", {}))}')
"
```

## API Reference

### GitHubProjectsExporter Class

```python
from llmstruct.gh_view import GitHubProjectsExporter

# Initialize exporter
exporter = GitHubProjectsExporter(config_path="llmstruct.toml")

# Load data
tasks, ideas = exporter.load_official_data()

# Format for GitHub
task_card = exporter.format_task_for_github(task)
idea_card = exporter.format_idea_for_github(idea)
```

### Key Methods

- `load_official_data()`: Load tasks.json and ideas.json
- `format_task_for_github(task)`: Convert task to GitHub card format
- `format_idea_for_github(idea)`: Convert idea to GitHub card format
- `_run_gh_command(command)`: Execute GitHub CLI commands
- `_load_mapping()` / `_save_mapping()`: Manage ID mappings

## Security Considerations

### Authentication
- Uses GitHub CLI authentication (secure token storage)
- Supports personal access tokens via environment variables
- No credentials stored in configuration files

### Data Privacy
- Only exports non-sensitive project metadata
- Respects gitignore patterns for sensitive files
- Local mapping file should be git-ignored if contains sensitive IDs

### Permissions
- Requires repository access for target projects
- Organization projects may require additional permissions
- Read/write access needed for card creation and updates

## Performance

### Optimization Features
- **Incremental Export**: Only exports changed items using ID mapping
- **Batch Operations**: Groups API calls for efficiency
- **Caching**: Local mapping reduces redundant API calls
- **Dry-run Mode**: Preview changes without API calls

### Limits
- GitHub API rate limits apply (5000 requests/hour)
- Large datasets may require multiple export sessions
- Network latency affects export speed

## Future Enhancements

### Planned Features
- **Bidirectional Sync**: Import GitHub changes back to local data
- **Real-time Updates**: Webhook-based synchronization
- **Advanced Filtering**: Export subsets based on criteria
- **Multi-project Support**: Export to multiple GitHub Projects
- **Template System**: Customizable card templates

### Integration Opportunities
- **GitHub Actions**: Automated sync workflows
- **VS Code Extension**: GUI for export operations
- **Slack/Teams**: Export notifications
- **Analytics Dashboard**: Export metrics and insights

## Troubleshooting

### Verification Steps

1. **Check GitHub CLI**:
   ```bash
   gh --version
   gh auth status
   ```

2. **Verify Data Files**:
   ```bash
   ls -la data/tasks.json data/ideas.json
   python -c "import json; print(len(json.load(open('data/tasks.json'))['tasks']))"
   ```

3. **Test Export**:
   ```bash
   python scripts/export_to_github_projects.py --dry-run
   ```

### Support Resources

- **GitHub CLI Documentation**: https://cli.github.com/manual/
- **GitHub Projects API**: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **LLMStruct Issues**: Report bugs via GitHub Issues
- **Configuration Help**: See `docs/llmstruct_config.md`

---

*For more information about LLMStruct's project management features, see the main documentation and [integration guide](integration.md).*