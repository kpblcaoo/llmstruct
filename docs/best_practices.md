# llmstruct Best Practices

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

This document outlines best practices for contributing to llmstruct, ensuring consistency, quality, and collaboration. It aligns with the project's goals (TSK-008, TSK-017).

## 2. Code Contribution

- **Style**: Follow PEP 8 for Python, use type hints, and verify with `mypy`.
- **Structure**: Add parsers to `src/llmstruct/parsers/` (e.g., `go_parser.py`).
- **Testing**: Add tests to `tests/` (e.g., `test_python_parser.py`). Aim for >80% coverage (`pytest --cov=src`).

## 3. Documentation Contribution

- **Format**: Update `docs/llmstruct_format.md` for JSON changes (TSK-008).
- **Localization**: Add translations to `docs/<lang>/` (e.g., `docs/ru/llmstruct_format.md`).
- **Other**: Update `docs/project_structure.md` for structural changes.

## 4. Pull Requests

- Create PRs to `main` with clear descriptions (TSK-011).
- Ensure tests pass (`pytest`, `mypy`) and get one approval (e.g., @kpblcaoo).
