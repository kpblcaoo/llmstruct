# LLMStruct

A tool for generating a JSON-based code structure format for automation, tooling, and LLM integration.

## License
MIT License - see [LICENSE](LICENSE) for details.

## Features
- Generates JSON describing project structure (modules, functions, classes, call graphs).
- Supports Python and JavaScript (extensible via plugins).
- Includes JSON schema validation.
- Integrates with LLMs for context-aware code assistance.

## Installation
```bash
pip install llmstruct
```

## Usage
```bash
python -m llmstruct <project_root> -o struct.json --language python
python -m llmstruct.validate struct.json llmstruct_schema.json
```

## JSON Format
See [llmstruct_format.md](docs/llmstruct_format.md) for the full specification.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-plugin`).
3. Commit changes (`git commit -m "Add JavaScript plugin"`).
4. Push to the branch (`git push origin feature/new-plugin`).
5. Open a Pull Request.

## Development
- Run tests: `pytest tests/`.
- Validate JSON: `python -m llmstruct.validate struct.json llmstruct_schema.json`.
- CI/CD: GitHub Actions for linting, testing, and JSON validation.

## Roadmap
- Add plugins for Go, Java, and TypeScript.
- Enhance call graph analysis with cross-module dependencies.
- Integrate with VS Code for real-time JSON updates.