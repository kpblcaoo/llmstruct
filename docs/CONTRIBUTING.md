# Contributing to LLMstruct

LLMstruct is an open-source project created by Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com). We welcome contributions to enhance the JSON standard, parsers, and documentation.

## Contribution Guidelines

### 1. Getting Started

- **Issues**: Use GitHub Issues to report bugs, suggest features, or discuss improvements.
- **Fork and Clone**: Fork the repository and clone it locally (`git clone https://github.com/kpblcaoo/llmstruct.git`).
- **Branches**: Create a branch for your changes (`git checkout -b feature/your-feature`).

### 2. Code Contributions

- **Style**:
  - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
  - Use type hints and verify with `mypy`.
  - Write clear, concise docstrings following [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- **Structure**:
  - Place new parsers in `src/llmstruct/parsers/` (e.g., `go_parser.py`).
  - Update `src/llmstruct/parsers/__init__.py` to register new parsers.
  - Add validators in `src/llmstruct/validators/` (e.g., `json_validator.py`).
- **Testing**:
  - Add tests in `tests/` (e.g., `tests/test_python_parser.py`).
  - Run `pytest` and `mypy` before submitting (`pytest tests/ && mypy src/`).
  - Aim for >80% test coverage (check with `pytest --cov=src`).
- **Commits**:
  - Write clear commit messages (e.g., `Add Go parser to src/llmstruct/parsers`).
  - Sign off commits with `Signed-off-by: Your Name <your.email@example.com>`.

### 3. Documentation Contributions

- **Format Specification**:
  - Update `docs/llmstruct_format.md` for changes to the JSON format.
  - Follow RFC-style: clear sections, examples, versioning.
- **Localization**:
  - Add translations to `docs/<lang>/` (e.g., `docs/ru/llmstruct_format.md` for Russian).
  - Ensure consistency with the English version.
- **Other Docs**:
  - Update `docs/project_structure.md` for structural changes.
  - Add usage examples to `examples/` (e.g., `examples/example_go_project.py`).
  - New language translations are welcome! Create a `docs/<lang>/` directory and translate key files (e.g., `README.md`, `llmstruct_format.md`).
### 4. Pull Request Process

1. **Create a PR**:
   - Push your branch (`git push origin feature/your-feature`).
   - Open a Pull Request against the `main` branch.
   - Use the PR template (if available) to describe changes, motivation, and testing.
2. **Review**:
   - Expect feedback within 7 days.
   - Address comments and update the PR as needed.
3. **Approval**:
   - PRs require at least one approval from maintainers (e.g., kpblcaoo).
   - Tests must pass (CI checks for `pytest`, `mypy`).
4. **Merge**:
   - Maintainers will merge approved PRs.
   - Squash commits for a clean history if necessary.

### 5. Code of Conduct

- Be respectful and inclusive.
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).
- Report issues to kpblcaoo@gmail.com or via GitHub Issues.

### 6. Contact

- **Maintainer**: Mikhail Stepanov (@kpblcaoo, kpblcaoo@gmail.com)
- **Issues**: Use GitHub Issues for questions, bugs, or feature requests.
- **Discussions**: Join discussions in GitHub Discussions (if enabled).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.
