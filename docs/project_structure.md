# LLMStruct Project Structure

This document describes the directory structure of the LLMStruct project, following Python best practices for modularity, scalability, and maintainability.

## Directory Layout

```
llmstruct/
├── src/
│   └── llmstruct/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py          # Entry point for `python -m llmstruct`
│       ├── cli.py               # CLI entry point (main function)
│       ├── self_run.py          # Logic for attaching JSON to LLM requests
│       ├── generators/
│       │   ├── __init__.py
│       │   └── json_generator.py # JSON generation logic
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── python_parser.py  # Python parsing logic
│       │   └── javascript_parser.py # JavaScript parsing logic
│       ├── validators/
│       │   ├── __init__.py
│       │   └── json_validator.py # JSON schema validation
│       └── templates/
│           ├── __init__.py
│           └── llm_prompt_template.txt # LLM prompt template
├── tests/
│   ├── __init__.py
│   ├── test_python_parser.py    # Tests for Python parser
│   ├── test_javascript_parser.py # Tests for JavaScript parser
│   └── test_json_validator.py   # Tests for JSON validation
├── docs/
│   ├── llmstruct_format.md      # JSON format specification
│   ├── project_structure.md     # This file
│   └── llmstruct_decision_checklist.md # Decision checklist
├── schemas/
│   ├── llmstruct_schema.json    # JSON schema for struct.json
│   └── sample_struct.json       # Sample JSON output
├── examples/
│   ├── python_project/          # Example Python project
│   └── js_project/             # Example JavaScript project
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD configuration
├── .gitignore                  # Git ignore patterns
├── LICENSE                     # MIT license
├── README.md                   # Project overview and setup
├── pyproject.toml              # Project metadata and dependencies
└── setup.py                    # Setup script (optional)
```

## Description

- **src/llmstruct/**: Core package containing all source code.
  - `__main__.py`: Enables `python -m llmstruct` execution.
  - `cli.py`: Handles command-line interface and orchestration.
  - `self_run.py`: Manages JSON attachment for LLM requests.
  - `generators/`: Modules for generating output formats (currently JSON).
  - `parsers/`: Language-specific parsers (Python, JavaScript, extensible).
  - `validators/`: Tools for validating JSON against the schema.
  - `templates/`: Stores prompt templates for LLM integration.
- **tests/**: Unit and integration tests using `pytest`.
- **docs/**: Documentation, including JSON format spec and decision checklist.
- **schemas/**: JSON schema and sample outputs for reference.
- **examples/**: Sample projects to demonstrate usage.
- **.github/workflows/**: CI/CD pipelines for linting, testing, and JSON validation.
- **Root Files**:
  - `.gitignore`: Excludes build artifacts, virtualenvs, etc.
  - `LICENSE`: MIT license.
  - `README.md`: Project overview, installation, and quickstart.
  - `pyproject.toml`: Defines dependencies, scripts, and metadata (PEP 621).
  - `setup.py`: Optional for legacy compatibility.

## Notes

- The `refactored_structure.py` artifact is a conceptual outline, not a real file. Its contents map to `cli.py`, `self_run.py`, `python_parser.py`, `javascript_parser.py`, and `json_generator.py`.
- The `json_validator.py` file was previously named `validate_json.py` in some contexts; the structure uses the more descriptive name.
- The `llm_prompt_template.txt` is placed in `templates/` for clarity and extensibility.
- The `usage.md` file was removed from `docs/` as it was not generated, avoiding confusion.

## Maintaining This File

- Update `project_structure.md` whenever the directory layout changes.
- Use this file as a reference for contributors to understand the project’s organization.
- Consider generating a visual diagram (e.g., using `mermaid`) for inclusion in the README or docs.