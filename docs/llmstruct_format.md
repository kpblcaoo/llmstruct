# llmstruct JSON Format Specification

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

The llmstruct JSON format is a universal, extensible structure for representing codebases, designed for automation and LLM integration.

## 2. Goals



## 3. JSON Structure

The format consists of three top-level fields: `metadata`, `toc`, and `modules`.

### 3.1. `metadata`

- **Type**: Object
- **Required Fields**:
  - `project_name`: String, project name (e.g., "llmstruct").
  - `description`: String, brief description.
  - `version`: String, ISO 8601 timestamp (e.g., "2025-05-18T23:00:27.888546Z").
  - `authors`: Array of objects (name, github, email).
  - `instructions`: Array of strings, LLM usage instructions.
  - `goals`: Array of strings, project goals.
  - `stats`: Object (modules_count, functions_count, classes_count, call_edges_count).
  - `folder_structure`: Array of objects (path, type).

**Example**:
```json
{
  "metadata": {
    "project_name": "llmstruct",
    "description": "Utility for generating structured JSON for codebases",
    "version": "2025-05-18T23:00:27.888546Z",
    "authors": [{"name": "Mikhail Stepanov", "github": "kpblcaoo", "email": "kpblcaoo@gmail.com"}],
    "instructions": ["Follow best practices", "Preserve functionality"],
    "goals": [],
    "stats": {
      "modules_count": 14,
      "functions_count": 27,
      "classes_count": 3,
      "call_edges_count": 90
    },
    "folder_structure": [
      {"path": "src/", "type": "directory"},
      {"path": "src/llmstruct/cli.py", "type": "file"}
    ]
  }
}
```
