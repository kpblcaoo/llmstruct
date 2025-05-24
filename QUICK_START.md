# LLMStruct Quick Start

## Installation & Setup

```bash
pip install -e .
```

## Basic Usage

### Generate Project Structure
```bash
python -m llmstruct parse . -o struct.json
```

### Interactive CLI
```bash
python -m llmstruct interactive .
```

### Audit System
```bash
python -m llmstruct interactive .
# In CLI:
/audit scan      # Scan for recoverable data
/audit recover   # Recover missing tasks/ideas  
/audit status    # Show placeholder status
```

## Configuration

Edit `llmstruct.toml` for:
- **Security**: Exclude patterns for sensitive files
- **Parsing**: Include/exclude file patterns
- **Cache**: Performance settings
- **API**: LLM integration

## Documentation

For detailed information, see:
- **CLI Commands**: `data/cli.json` - Complete command reference
- **Security**: `docs/struct_security.md` - Safe CI/CD patterns  
- **Architecture**: `docs/cli_modular_architecture.md` - System design
- **Format**: `docs/llmstruct_format.md` - JSON specification

## Safety Features

- ✅ **Automatic .gitignore integration**
- ✅ **Exclude sensitive patterns** (secrets, personal files, backups)
- ✅ **CI/CD safe** - 49% smaller struct.json output
- ✅ **Audit system** for data recovery

See `docs/struct_security.md` for complete security configuration.