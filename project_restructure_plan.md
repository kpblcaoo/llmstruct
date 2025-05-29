# Project Restructure Plan: From "Mad Scientist" to Professional

## Target Structure

```bash
llmstruct/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── security-audit.yml
│   └── ISSUE_TEMPLATE/
├── src/
│   └── llmstruct/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── commands/
│       │   └── config.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── context.py
│       │   └── cache.py
│       ├── parsers/
│       ├── generators/
│       ├── validators/
│       └── integrations/
│           ├── copilot.py
│           ├── vscode.py
│           └── cursor.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── conftest.py
├── docs/
│   ├── api/
│   ├── user-guide/
│   ├── development/
│   └── deployment/
├── config/
│   ├── llmstruct.toml.example
│   ├── dev.toml
│   └── prod.toml
├── scripts/
│   ├── setup.sh
│   ├── test.sh
│   ├── build.sh
│   └── deploy.sh
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── kubernetes/
│   └── helm/
├── examples/
│   ├── basic/
│   ├── advanced/
│   └── integrations/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   ├── test.txt
│   └── prod.txt
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
└── docker-compose.yml
```

## Migration Script

```bash
#!/bin/bash
# migrate_structure.sh

set -e

echo "🚀 Starting llmstruct restructure..."

# 1. Create new structure
mkdir -p {config,scripts,deployment/{docker,kubernetes},examples/{basic,advanced},requirements,tests/{unit,integration,fixtures}}

# 2. Move CLI components
mkdir -p src/llmstruct/cli/commands
mv src/llmstruct/cli.py src/llmstruct/cli/main.py
mv src/llmstruct/cli_*.py src/llmstruct/cli/

# 3. Create core module
mkdir -p src/llmstruct/core
mv src/llmstruct/context_orchestrator.py src/llmstruct/core/orchestrator.py
mv src/llmstruct/cache.py src/llmstruct/core/

# 4. Organize integrations
mkdir -p src/llmstruct/integrations
mv src/llmstruct/copilot.py src/llmstruct/integrations/
mv src/llmstruct/ai_*.py src/llmstruct/integrations/

# 5. Clean up root
mkdir -p temp/migrate_cleanup
mv test_*.py temp/migrate_cleanup/
mv *_test.json temp/migrate_cleanup/
mv *.txt temp/migrate_cleanup/
mv META_*.md temp/migrate_cleanup/

# 6. Move docs properly
mv docs/* docs/user-guide/ 2>/dev/null || true

# 7. Setup config
cp llmstruct.toml config/llmstruct.toml.example

echo "✅ Structure migration complete!"
``` 