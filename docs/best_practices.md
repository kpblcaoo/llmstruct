# llmstruct Best Practices

Best practices for using `llmstruct` to ensure clean code and reliable `struct.json` output.

## Code Style
- **Format Code**: Use `flake8` for Python, `eslint` for JS.
  ```bash
  flake8 src/
  ```
- **Avoid Dynamic Imports**: They confuse parsers (TSK-006).
- **Small Functions**: Max 50 lines for LLM context (G5).

## Project Structure
- Keep `src/` clean: Avoid nested folders >3 levels.
- Use `llmstruct.toml` for custom instructions (TSK-024).

## Testing
- Add tests for idempotence:
  ```bash
  pytest src/tests/test_parser.py
  ```
- Check `struct.json` errors after parsing.

## Tips
- Run `llmstruct parse` before commits to catch issues.
- Use Telegram `/fix` for quick LLM suggestions (TSK-023).

See [integration.md](#integration.md) for CI/CD setup.