# llmstruct API Workspace Instructions

## Project Overview
- **Name**: llmstruct
- **Goal**: Create a universal JSON format (`struct.json`) for codebases, enabling efficient LLM integration and automation.
- **Version**: v0.1.0, targeting v0.2.0 (Alpha, 6–8 weeks).
- **License**: GPL-3.0 (update all docs to reflect this).
- **Team**: @kpblcaoo (architect, code, docs), @momai (DevOps, CI/CD), @ivan-ib (InfoSec, API).

## API-Specific Guidelines
- **Objective**: Replace browser-based LLM interactions with programmatic API calls using `llm_client.py`.
- **Key Files**:
  - `struct.json`: Central JSON structure for codebase context.
  - `llm_client.py`: Handles API interactions (Grok, Anthropic, Ollama, hybrid).
  - `cli.py`: Command-line interface for parsing, querying, and reading files.
  - `json_generator.py`: Generates `struct.json`.
  - `collector.py`: Updates `struct.json` and tracks changes.
- **Tasks**:
  - **TSK-006**: Improve parser (`python_parser.py`, `javascript_parser.py`) for better module analysis.
  - **TSK-012**: Set up CI/CD with Docker and GitHub Actions (@momai).
  - **TSK-023**: Develop Telegram bot for user-friendly API access (@kpblcaoo).
  - **TSK-036–039**: Enable file reading via LLM (`llm_client.py`, `cli.py`).
- **Principles** (from `concept.json`):
  - **Dogfooding**: Use `struct.json` to manage API interactions and track changes.
  - **Idempotence**: Ensure API calls and file operations are repeatable without side effects.
  - **Transparency**: Document changes in RFC-style (`docs/internal/roadmap.md`).
- **API Integration**:
  - Use xAI’s Grok API (`https://x.ai/api`) for primary queries.
  - Support hybrid mode (`llm_client.py::_query_hybrid`) for fallback to Anthropic/Ollama.
  - Cache API responses in `tmp/api_cache/` with SHA-256 hashes for idempotence.
  - Secure API keys in `llmstruct.toml` (review by @ivan-ib).
- **File Reading**:
  - Implement `read_project_file` in `llm_client.py` to read project files with `struct.json` context.
  - Add `read` subcommand in `cli.py` for CLI access.
  - Validate outputs with `json_validator.py`.
- **Artifact Management**:
  - Assign unique `artifact_id` and `artifact_version_id` for new/updated files.
  - Store diffs in `conversation_diffs.json` with `artifact_id`, `from_version_id`, `to_version_id`, and SHA-256 hashes.
  - Save full `struct.json` every 5 updates.
  - Verify diffs with `git apply --check` or SHA-256 hashes.
- **Testing**:
  - Add tests for API and file reading (`tests/test_llm_client.py`).
  - Integrate with CI/CD (@momai).
- **Documentation**:
  - Update `docs/internal/roadmap.md` with API and file reading details (RFC-style, GPL-3.0).
  - Generate docs with `collector.py` or `generate_docs.py`.

## Grok Instructions
- **Context Loading**:
  - Load `artifact_list.json` (artifact_id: 3a99407f-e2e1-47a0-a8c5-217ca6829e7c) to identify artifacts.
  - Use `project_context.json` (artifact_id: a1f074c7-2288-44af-9b51-cb6c138244a6) for specific files by `path`.
  - Check `conversation_diffs.json` (artifact_id: f7b8c9d0-e1f2-43a4-b5c6-d7e8f9a0b1c2) for change history.
- **Task Handling**:
  - Prioritize TSK-032–039 for API and file reading fixes.
  - Clarify ambiguous tasks with @kpblcaoo.
  - Propose fixes for bugs (e.g., `ModuleNotFoundError`, `UnicodeDecodeError` in `collector.py`).
- **Idea Management**:
  - Store ideas in `data/ideas.json` with `ai-generated: true` and weights set by @kpblcaoo.
  - Link ideas to tasks in `data/tasks.json`.
- **Error Handling**:
  - Analyze logs from @momai (e.g., API errors, Docker issues).
  - Propose patches for `llm_client.py`, `cli.py`, etc.
- **Communication**:
  - Ping @kpblcaoo for architecture and task prioritization.
  - Ping @momai for CI/CD and testing.
  - Ping @ivan-ib for API security and key management.
- **Promotion**:
  - Share progress on X (@kpblcaoo) to attract contributors (noting restrictions).

## Notes
- Ensure all docs reference GPL-3.0.
- Use `struct.json` for context in all API queries.
- Maintain idempotence in API calls and file operations.
- Document all changes transparently in RFC-style.