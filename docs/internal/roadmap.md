# llmstruct Roadmap

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. v0.2.0 (6–8 weeks, Alpha)

- **Goals**: Standalone parser, basic LLM, demo (TSK-017).
- **Tasks**:
  - TSK-006, TSK-007: Enhance `parser.py`.
  - TSK-011: `task_parser.py` for Issues.
  - TSK-014: API fallback.
  - TSK-016: Stabilize Qwen-1.5B.
  - TSK-024: Instructions in `struct.json`, idempotence.

## 2. v0.3.0 (3–6 months, Beta)

- **Goals**: CI/CD, UI, scalability.
- **Tasks**:
  - TSK-012: CI/CD module.
  - TSK-015: MLflow, Grafana.
  - TSK-021: Flask UI.
  - TSK-023: Telegram bot with `/fix`, `/errors`.

## 3. Actions

- Focus on TSK-006, TSK-011, TSK-024 (@kpblcaoo).
- Plan TSK-012, TSK-015 (@momai).
- Onboard @ivan-ib (TSK-019).
