# LLMstruct Configuration

**Document Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T12:35:00Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## Overview

LLMstruct supports configuration via a `llmstruct.toml` file in the project root. This file defines project goals and CLI settings, providing flexibility for users. Command-line arguments override settings in `llmstruct.toml`.

## Configuration File

Create a `llmstruct.toml` file in your project root. The file uses TOML format and includes two main sections: `[goals]` and `[cli]`.

### Example `llmstruct.toml`

```toml
[goals]
goals = [
    "Create universal JSON format for codebase structure",
    "Support LLM integration for enhanced automation"
]

[cli]
language = "python"
include_patterns = ["*.py"]
exclude_patterns = ["tests/*", "venv/*"]
include_ranges = true
include_hashes = false
```

### Sections

- `[goals]`:
  - `goals`: List of project goals (strings). Used in `struct.json` under `metadata.goals`.
- `[cli]`:
  - `language`: Programming language (`python`, `javascript`). Default: `python`.
  - `include_patterns`: List of file patterns to include (e.g., `["*.py"]`).
  - `exclude_patterns`: List of file patterns to exclude (e.g., `["tests/*"]`).
  - `include_ranges`: Boolean, include line ranges for functions/classes. Default: `false`.
  - `include_hashes`: Boolean, include file hashes. Default: `false`.

## Usage

1. Create `llmstruct.toml` in your project root.
2. Run LLMstruct:
   ```bash
   python -m llmstruct .
   ```
   This uses settings from `llmstruct.toml`.
3. Override settings via CLI:
   ```bash
   python -m llmstruct . --goals "Custom goal" --language javascript
   ```
   CLI arguments take precedence over `llmstruct.toml`.

## Notes

- If no goals are specified (via `--goals` or `llmstruct.toml`), LLMstruct logs a warning and sets `metadata.goals` to an empty list.
- Ensure `toml` is installed (`pip install toml`) for configuration parsing.
- Invalid `llmstruct.toml` files trigger an error log but do not halt execution.

## References

- [LLMstruct JSON Format Specification](llmstruct_format.md)
- [Project Structure](project_structure.md)