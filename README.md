# llmstruct

A utility for generating structured JSON representations of codebases, designed for integration with Large Language Models (LLMs).

---

## 🧑‍💻 Developer Entry Point

- **Quickstart:** See [QUICK_START.md](QUICK_START.md) for setup and usage.
- **CLI Reference:** All commands and automation patterns are described in [data/cli.json](data/cli.json).
- **Modular CLI Architecture:** See [docs/cli_modular_architecture.md](docs/cli_modular_architecture.md) for how to extend and integrate.
- **Task & Idea Management:** All project tasks and ideas are tracked in [data/tasks.json](data/tasks.json) and [data/ideas.json](data/ideas.json). Cross-references are maintained in [docs.json](docs.json).
- **Audit & Recovery:** Use the CLI audit system to recover lost tasks/ideas and maintain data integrity:
  ```bash
  llmstruct audit scan      # Scan for recoverable entries
  llmstruct audit status    # Show placeholder statistics
  llmstruct audit recover   # Restore lost tasks/ideas from sources
  ```
- **API Layer (Planned):** Future releases will provide a REST/GraphQL API for all CLI and automation features (see TSK-139, IDEA-140).

---

## About the Project

llmstruct is an open-source project for universal codebase introspection, context orchestration, and LLM-driven automation. It supports modular JSON formats, CLI automation, queue-based workflows, and advanced security.

- **4-level context orchestration** (init.json)
- **Smart context selection** for LLMs
- **CLI automation**: queues, cache, batch workflows
- **Security**: git hooks, secret detection, safe write boundaries, secure struct.json generation
- **Extensible**: plugins, new languages, custom workflows

### 🔒 Security Features

- **Automatic gitignore integration**: Respects `.gitignore` patterns
- **Comprehensive exclude patterns**: Blocks sensitive files, secrets, personal data
- **49% size reduction**: From 403KB to 207KB by excluding unnecessary files
- **CI/CD safe**: Secure for automated deployment in public repositories
- **Configuration-driven**: All patterns defined in `llmstruct.toml`

See [docs/struct_security.md](docs/struct_security.md) for complete security documentation.

### 🐹 Go Language Support

llmstruct includes advanced Go language support with full AST analysis through Docker:

**Features:**
- **Full AST parsing** using `golang.org/x/tools/go/packages`
- **128+ functions** and **36+ structs** extraction from real projects
- **Type analysis**: Parameters, return values, receivers, embedded fields
- **Documentation extraction**: Comments and docstrings
- **Package dependency mapping**: Import analysis and module relationships
- **Docker containerized**: No local Go installation required

**Usage:**
```bash
# Build the Go analyzer Docker image
cd llmstruct
docker build -f docker/parser_go/Dockerfile -t go-analyzer-improved .

# Analyze a Go project
docker run --rm \
  -v /path/to/go/project:/workspace:ro \
  -v /path/to/output:/output \
  go-analyzer-improved /workspace --output /output/result.json
```

```bash
# example
docker run --rm \
  --name go-analyzer-container \
  -v /home/user/go-project:/workspace:ro \
  -v /home/user/llmstruct/docker/parser_go:/output \
  go-analyzer-improved /workspace --output /output/go_analysis_result.json

```

**Architecture:**
- `src/llmstruct/parsers/go_analyzer.py` - Python orchestrator and llmstruct format converter
- `src/llmstruct/parsers/analyzer.go` - Go AST analyzer using go/packages
- `docker/parser_go/Dockerfile` - Multi-stage Docker build with Go 1.24+

The Go analyzer automatically handles version compatibility, dependency resolution, and converts raw AST data into llmstruct's standardized JSON format.

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
- [Struct.json Security Configuration](docs/struct_security.md)
- [Project Structure](docs/project_structure.md)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
