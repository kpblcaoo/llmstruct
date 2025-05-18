# llmstruct Roadmap

Development plan for `llmstruct` (v0.2.0, v0.3.0). Focus: `struct.json`, Qwen, GPL-3.0. Team: @kpblcaoo, @momai, @ivan-ib.

## v0.2.0 (6–8 weeks, Alpha)
- **Goals**: Standalone parser, basic LLM, demo for Habr (TSK-017).
- **Tasks**:
  - TSK-006, TSK-007: Enhance `parser.py`, error logs, context cache.
  - TSK-011: `task_parser.py` for Issues, `struct.json`.
  - TSK-014: API fallback (Anthropic, Grok).
  - TSK-016: Stabilize Qwen-1.5B for simple projects.
  - TSK-024: Base/custom instructions in `struct.json`, idempotence.
- **Deliverables**:
  - CLI: `llmstruct parse --input src/`.
  - Habr post: “llmstruct alpha!” (TSK-017).
  - ~5–20 contributors.

## v0.3.0 (3–6 months, Beta)
- **Goals**: CI/CD, UI, scalability, ~50 contributors.
- **Tasks**:
  - TSK-012: CI/CD module, GitHub Action (@momai).
  - TSK-015: MLflow, Grafana for metrics (@momai, @ivan-ib).
  - TSK-021: Flask UI for `struct.json`.
  - TSK-022: SQLite backend.
  - TSK-023: Telegram bot with `/fix`, `/errors`.
- **Deliverables**:
  - PyPI package: `pip install llmstruct`.
  - UI: Deployed via Nginx (TSK-014).
  - Video: “llmstruct vs Cursor” (TSK-017).

## Actions
- Focus on TSK-006, TSK-011, TSK-024 for v0.2.0 (@kpblcaoo).
- Plan TSK-012, TSK-015 (@momai).
- Onboard @ivan-ib (TSK-019, @kpblcaoo).