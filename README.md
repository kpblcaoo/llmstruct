# llmstruct

A utility for generating structured JSON representations of codebases, designed for integration with Large Language Models (LLMs).

## About the Project

llmstruct is an open-source project developed by an international community, initiated by Mikhail Stepanov. It creates a universal JSON format capturing modules, functions, classes, call graphs, and metadata. The project supports modular parsers (e.g., Python, JavaScript) and is extensible for new languages, aligning with an RFC-style open standard. Contributions from all regions are encouraged to build a global standard.

## Installation

```bash
pip install llmstruct
```

## Usage

Generate `struct.json` with default settings:
```bash
python -m llmstruct .
```

See [Configuration Guide](docs/llmstruct_config.md) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
