# Contributing to llmstruct

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

Contributions are welcome to llmstruct! This guide outlines how to contribute code, documentation, and translations.

## 2. Code Contribution

- **Style**: Follow PEP 8, use type hints, and verify with `mypy`.
- **Structure**: Add parsers to `src/llmstruct/parsers/` and validators to `src/llmstruct/validators/`.
- **Testing**: Add tests to `tests/`. Run `pytest tests/ && mypy src/`.

## 3. Documentation Contribution

- **Format**: Update `docs/llmstruct_format.md` for JSON changes.
- **Localization**: Add translations to `docs/<lang>/` (e.g., `docs/ru/`).
- **Other**: Update `docs/project_structure.md` for structural changes.

## 4. Pull Request Process

- Push to a feature branch and open a PR to `main`.
- Include a clear description, motivation, and testing details.
- Ensure tests pass and get one approval.

## 5. Code of Conduct

- Be respectful and inclusive.
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).
- Report issues to kpblcaoo@gmail.com or GitHub Issues.
