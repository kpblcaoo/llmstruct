# llmstruct

A utility for generating structured JSON representations of codebases, designed for integration with Large Language Models (LLMs).

## About the Project

llmstruct is an open-source project for universal codebase introspection, context orchestration, and LLM-driven automation. It supports modular JSON formats, CLI automation, queue-based workflows, and advanced security.

- **4-level context orchestration** (init.json)
- **Smart context selection** for LLMs
- **CLI automation**: queues, cache, batch workflows
- **Security**: git hooks, secret detection, safe write boundaries
- **Extensible**: plugins, new languages, custom workflows

## Installation

```bash
pip install llmstruct
```

## Quickstart

Generate `struct.json` with default settings:
```bash
python -m llmstruct .
```

Run interactive CLI with context orchestration:
```bash
llmstruct interactive . --context data/init.json --mode anthropic
```

Automate documentation via queue:
```bash
llmstruct queue process --file data/cli_queue_enhanced.json
```

## JSON Ecosystem
- `init.json` — master context, orchestration rules
- `struct.json` — codebase structure
- `cli.json` — CLI commands, automation templates
- `cli_queue.json` — command queue for workflows
- `tasks.json` — project/task management
- `*_enhanced.json` — advanced automation & context

## Security
- All writes restricted to `./tmp`
- Pre-commit/commit-msg hooks for secret detection
- See [docs/SECURITY.md](docs/SECURITY.md)

## Documentation
- [LLMstruct JSON Format](docs/llmstruct_format.md)
- [CLI Commands & Automation](docs/cli_commands.md)
- [Security Guide](docs/SECURITY.md)
- [Project Structure](docs/project_structure.md)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
