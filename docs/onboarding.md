# llmstruct Onboarding Guide

Get started with `llmstruct`, the open-source dev tool for JSON-driven development with LLMs. Licensed under GPL-3.0.

## Quick Start
1. **Install**:
   ```bash
   pip install llmstruct
   ```
2. **Parse Code**:
   ```bash
   llmstruct parse --input src/ --output struct.json
   ```
3. **Explore**:
   - See `struct.json` for tasks, context, metrics.
   - Check errors: `errors: [{file: "app.js", line: 42, reason: "invalid syntax"}]`.
4. **Contribute**:
   - Join Issues on GitHub: [github.com/kpblcaoo/llmstruct](#).
   - Try Telegram bot: `/join`, `/tasks`, `/fix`.

## Next Steps
- Read [integration.md](#integration.md) for CI/CD setup.
- Follow [best_practices.md](#best_practices.md) for clean code.
- See [examples/struct.json](#examples/struct.json) for base/custom instructions.

Welcome to the `llmstruct` community! Let’s make development smarter.