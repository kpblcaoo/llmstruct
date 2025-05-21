# llmstruct Integration Guide

Integrate `llmstruct` into your project for JSON-driven development with LLMs. Supports CLI, CI/CD, and custom workflows.

## CLI Usage
For pet projects:
```bash
pip install llmstruct
llmstruct parse --input src/ --output struct.json
```
- Generates `struct.json` with tasks, context, errors.
- See [examples/struct.json](#examples/struct.json).

## CI/CD Setup
For GitHub/GitLab:
1. Add `llmstruct` to your repo:
   ```bash
   pip install llmstruct
   ```
2. Create `.github/workflows/parse.yml`:
   ```yaml
   name: Parse Code
   on: [push, pull_request]
   jobs:
     parse:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - run: llmstruct parse --input src/ --output struct.json
         - name: Report Errors
           run: |
             if grep -q '"errors"' struct.json; then
               echo "Parse errors found!"
               gh issue create --title "Parse Error" --body "$(cat struct.json | jq '.errors')"
               exit 1
             fi
   ```
3. Check Issues for parse errors.

## Configuration
- Edit `llmstruct.toml` for custom LLM instructions (see [examples/struct.json](#examples/struct.json)).
- Follow [best_practices.md](#best_practices.md) for clean code.

## Advanced
- Use Telegram bot (`/tasks`, `/fix`) for real-time updates (TSK-023).
- Deploy UI for task management (TSK-021, v0.3.0).
- Integrate with DevOps tools: Grafana for metrics (TSK-015), MLflow for LLM logging.

See [onboarding.md](#onboarding.md) to start contributing!