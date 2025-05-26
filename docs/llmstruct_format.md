# JSON Format Specification for llmstruct

**Status**: Draft  
**Version**: 0.2.1  
**Last Updated**: 2025-01-27  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

The llmstruct JSON format is a universal, extensible structure for representing codebases, designed for automation and integration with Large Language Models (LLMs).

## 2. Goals

- Provide a standardized format for codebase representation
- Enable efficient LLM analysis and code generation
- Support modular architecture and dependency tracking
- Facilitate automated documentation and analysis tools

## 3. JSON Structure

The format consists of three top-level fields: `metadata`, `toc`, and `modules`.

### 3.1. `metadata`

- **Type**: Object
- **Required fields**:
  - `project_name`: String, project name (e.g., "llmstruct")
  - `description`: String, brief project description
  - `version`: String, ISO 8601 timestamp (e.g., "2025-01-27T12:00:00.000000Z")
  - `authors`: Array of objects (name, github, email)
  - `instructions`: Array of strings, instructions for LLM
  - `goals`: Array of strings, project goals
  - `stats`: Object (modules_count, functions_count, classes_count, call_edges_count)
  - `folder_structure`: Array of objects (path, type)

**Example**:
```json
{
  "metadata": {
    "project_name": "llmstruct",
    "description": "Utility for generating structured JSON for codebases",
    "version": "2025-01-27T12:00:00.000000Z",
    "authors": [
      {
        "name": "Mikhail Stepanov",
        "github": "kpblcaoo", 
        "email": "kpblcaoo@gmail.com"
      }
    ],
    "instructions": [
      "Follow best practices",
      "Maintain functionality"
    ],
    "goals": [
      "Automated codebase analysis",
      "LLM integration support"
    ],
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

### 3.2. `toc` (Table of Contents)

- **Type**: Array of objects
- **Purpose**: Provides a hierarchical overview of the codebase structure
- **Fields per entry**:
  - `path`: String, file or directory path
  - `type`: String, either "file" or "directory"
  - `description`: String (optional), brief description

**Example**:
```json
{
  "toc": [
    {
      "path": "src/llmstruct/",
      "type": "directory",
      "description": "Main package directory"
    },
    {
      "path": "src/llmstruct/cli.py",
      "type": "file",
      "description": "Command-line interface module"
    }
  ]
}
```

### 3.3. `modules`

- **Type**: Array of objects
- **Purpose**: Contains detailed information about each code module
- **Fields per module**:
  - `path`: String, module file path
  - `content`: String, full source code content
  - `functions`: Array of function objects
  - `classes`: Array of class objects
  - `dependencies`: Array of strings, imported modules

**Function object structure**:
- `name`: String, function name
- `signature`: String, function signature
- `description`: String, function description
- `calls`: Array of strings, functions called by this function

**Class object structure**:
- `name`: String, class name
- `methods`: Array of method objects (same structure as functions)
- `description`: String, class description

**Example**:
```json
{
  "modules": [
    {
      "path": "src/llmstruct/utils.py",
      "content": "def helper_function():\n    pass",
      "functions": [
        {
          "name": "helper_function",
          "signature": "helper_function()",
          "description": "A utility helper function",
          "calls": []
        }
      ],
      "classes": [],
      "dependencies": []
    }
  ]
}
```

## 4. Version History

- **0.2.1**: Current format with enhanced metadata and modular structure
- **0.1.0**: Initial format specification

## 5. Usage Guidelines

1. All timestamps should use ISO 8601 format
2. File paths should use forward slashes for consistency
3. Dependencies should list only direct imports
4. Function calls should reference functions by their qualified names
5. Content should preserve original formatting and comments
