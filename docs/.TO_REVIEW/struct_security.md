# Struct.json Security Configuration

## Overview

The `struct.json` generation system now includes comprehensive security measures to prevent exposure of sensitive data, personal files, and temporary workspaces.

## Security Features

### 1. Gitignore Integration
- **Automatic**: Uses `.gitignore` patterns by default (`use_gitignore = true`)
- **Comprehensive**: All patterns from `.gitignore` are automatically excluded
- **CI/CD Safe**: Works seamlessly in automated environments

### 2. Enhanced Exclude Patterns

The system uses a multi-layered approach with patterns defined in `llmstruct.toml`:

```toml
[parsing]
exclude_patterns = [
    # Python/build artifacts
    "**/__pycache__/**", 
    "**/.*", 
    "build/**",
    
    # Personal/temporary workspaces
    "temp_workfiles/**", 
    "sorting_workspace/**",
    "ideas_sorting/**",
    
    # Backup and temporary files
    "**/*.bak",
    "**/*.swp", 
    "**/*~",
    "**/*.backup",
    "*_backup.*",
    
    # Secrets and credentials
    "secrets/**",
    "secret_*",
    "*_secret*",
    "private_*",
    "*api_key*",
    "*_token*",
    "*.key",
    "*.pem",
    "*.env",
    "*.env.*",
    
    # Personal configurations
    "**/*_personal.json",
    "**/personal_*.json",
    "**/session_*.json",
    "**/local_config.*",
    
    # Archive and logs
    "workflow_archive/**",
    "**/*.log"
]
```

### 3. Directory Exclusions

```toml
exclude_dirs = [
    "venv", "__pycache__", ".git", ".pytest_cache", 
    "build", "dist", "tmp", "bak", "sorting_workspace", 
    "temp_workfiles", "workflow_archive", "htmlcov", "logs"
]
```

## Implementation Details

### CLI Configuration Priority

The system reads configuration with the following priority:
1. Command-line arguments (`--include`, `--exclude`)
2. `[parsing]` section in `llmstruct.toml`
3. `[cli]` section in `llmstruct.toml` (legacy compatibility)
4. Built-in defaults

### CI/CD Integration

The CI/CD workflow automatically uses secure patterns:

```yaml
- name: Generate struct.json
  run: python -m llmstruct parse . -o struct.json
```

This command:
- ✅ Reads `llmstruct.toml` configuration
- ✅ Applies all exclude patterns
- ✅ Uses `.gitignore` patterns
- ✅ Excludes personal/sensitive directories
- ✅ Safe for public repositories

## Security Benefits

### Before Security Implementation
- **Size**: ~403KB (16,112 lines)
- **Risk**: Included temp files, backups, personal data
- **CI/CD**: Potential secret exposure

### After Security Implementation
- **Size**: ~207KB (8,260 lines) - **49% reduction**
- **Risk**: Only public source code and documentation
- **CI/CD**: Safe for automated deployment

## Validation

To validate that security patterns are working:

```bash
# Generate secure struct.json
python -m llmstruct parse . -o struct_secure.json

# Check for sensitive patterns (should return minimal results)
grep -i "temp_workfiles\|backup\|secret\|personal\|\.env" struct_secure.json

# Compare sizes
wc -l struct*.json
```

## Best Practices

1. **Keep llmstruct.toml Updated**: Add new exclude patterns as needed
2. **Regular Audits**: Periodically review generated struct.json for sensitive data
3. **Environment-Specific Configs**: Use different patterns for dev/prod environments
4. **Monitor CI/CD**: Check CI logs for security warnings

## Related Files

- `llmstruct.toml` - Main configuration
- `.gitignore` - Automatic pattern source
- `src/llmstruct/cli.py` - CLI implementation
- `src/llmstruct/cli_config.py` - Configuration handling
- `src/llmstruct/generators/json_generator.py` - Core generation logic

## Cross-References

- **Tasks**: TSK-098 (Audit System), TSK-141 (Index Restoration)
- **Ideas**: Security patterns, CI/CD automation
- **Documentation**: `docs/cli_modular_architecture.md`, `QUICK_START.md`
