# LLMstruct

A utility for generating structured JSON representations of codebases, designed for integration with Large Language Models (LLMs).

## About the Project

LLMstruct is an open-source project developed by an international community, initiated by Mikhail Stepanov. It creates a universal JSON format capturing modules, functions, classes, call graphs, and metadata. The project supports modular parsers (e.g., Python, JavaScript) and is extensible for new languages, aligning with an RFC-style open standard. Contributions from all regions are encouraged to build a global standard.

## Installation

```bash
pip install llmstruct
```

## Usage

Generate `struct.json` with default settings:
```bash
python -m llmstruct .
```

Specify custom project goals via CLI:
```bash
python -m llmstruct . --goals "Create universal JSON format" "Support LLM integration"
```

Use `llmstruct.toml` for configuration:
```bash
cat <<EOF > llmstruct.toml
[goals]
goals = ["Create universal JSON format", "Support LLM integration"]

[cli]
language = "python"
include_patterns = ["*.py"]
exclude_patterns = ["tests/*"]
EOF
python -m llmstruct .
```

See [Configuration Guide](docs/llmstruct_config.md) for details.

## Localization

LLMstruct welcomes contributions in all languages. English is the primary language for collaboration, with translations available in [Russian](docs/ru/README.md) and other languages under `docs/<lang>/`. Help us translate to your language!

## Author

- **Mikhail Stepanov** ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code, documentation, and pull requests. For Russian documentation, see [docs/ru/README.md](docs/ru/README.md) and [docs/ru/CONTRIBUTING.md](docs/ru/CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.