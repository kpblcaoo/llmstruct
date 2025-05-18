# LLMstruct JSON Format Specification

**Document Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T00:34:00Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

The LLMstruct JSON format is a universal, extensible structure for representing codebases, designed for automation and integration with Large Language Models (LLMs). It captures modules, functions, classes, call graphs, and metadata, supporting multiple programming languages and enabling modular parsing.

This document specifies the format, adhering to RFC-style principles: clarity, openness, and extensibility. It is intended for developers, LLM integrators, and contributors to the LLMstruct project.

## 2. Goals

- Provide a universal JSON format for code structures (modules, functions, classes, calls, metadata).
- Ensure extensibility for new languages and entity types.
- Support modular, plugin-based parsers.
- Maintain an open, well-documented format.
- Enable LLM integration for automation and context-aware assistance.

## 3. JSON Structure

The LLMstruct JSON format consists of three top-level fields: `metadata`, `toc`, and `modules`.

### 3.1. `metadata`

Contains project-wide information and statistics.

- **Type**: Object
- **Required Fields**:
  - `project_name`: String, name of the project (e.g., "llmstruct").
  - `description`: String, brief project description.
  - `version`: String, ISO 8601 timestamp of generation (e.g., "2025-05-18T00:34:00Z").
  - `authors`: Array of objects, project authors:
    - `name`: String, full name (e.g., "Mikhail Stepanov").
    - `github`: String, GitHub handle (e.g., "kpblcaoo").
    - `email`: String, contact email (e.g., "kpblcaoo@gmail.com").
  - `instructions`: Array of strings, guidelines for LLM usage.
  - `goals`: Array of strings, project objectives.
  - `stats`: Object, summary statistics:
    - `modules_count`: Integer, number of modules.
    - `functions_count`: Integer, number of functions.
    - `classes_count`: Integer, number of classes.
    - `call_edges_count`: Integer, number of call graph edges.
  - `folder_structure`: Array of objects, directory/file structure:
    - `path`: String, relative path (e.g., "src/llmstruct/cli.py").
    - `type`: String, "directory" or "file".
- **Optional Fields**:
  - None currently defined.

**Example**:
```json
{
  "metadata": {
    "project_name": "llmstruct",
    "description": "Utility for generating structured JSON for codebases",
    "version": "2025-05-18T00:34:00Z",
    "authors": [
      {
        "name": "Mikhail Stepanov",
        "github": "kpblcaoo",
        "email": "kpblcaoo@gmail.com"
      }
    ],
    "instructions": ["Follow best practices", "Preserve functionality"],
    "goals": ["Create universal JSON format", "Ensure extensibility"],
    "stats": {
      "modules_count": 16,
      "functions_count": 35,
      "classes_count": 4,
      "call_edges_count": 959
    },
    "folder_structure": [
      {"path": "src/", "type": "directory"},
      {"path": "src/llmstruct/cli.py", "type": "file"}
    ]
  }
}
```

## 4. Extensibility

- **Language Support**: Add parsers in `src/llmstruct/parsers/` (e.g., `go_parser.py`) and register in `src/llmstruct/parsers/__init__.py`.
- **New Fields**: Extend `metadata`, `functions`, or `classes` with optional fields (e.g., `functions[].complexity`).
- **Custom Categories**: Update `infer_category` in parsers to support new categories (e.g., "tests").

## 5. Usage

Generate `struct.json`:
```bash
python -m llmstruct ./ -o struct.json --language python
```

## 6. Future Work

- Define JSON schema (`schemas/llmstruct_schema.json`).
- Add non-code file support (e.g., `README.md` metadata).
- Implement versioning (e.g., `v1.1` for new fields).
- Create contribution guidelines (`CONTRIBUTING.md`).

## 7. Change History

- **0.1.0 (2025-05-18)**: Initial draft, based on `struct.json` output.

## 8. References

- [LLMstruct Project Structure](project_structure.md)
- [Python `ast` Module](https://docs.python.org/3/library/ast.html)
- [Esprima JavaScript Parser](https://esprima.org/)