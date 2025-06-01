# llmstruct Technical Ideas

Technical ideas for `llmstruct` v0.2.0–v0.3.0, focusing on `struct.json`, LLM (Qwen in dev, chatbot interim, Anthropic/Grok APIs), and code parsing. Goals: G1 (universal JSON), G5 (LLM optimization). Team: @kpblcaoo, @momai, @ivan-ib. Trends (May 2025): Local LLMs (Qwen, ~5–15k views on Habr), MLOps (MLflow, Grafana), UX focus in dev tools.

## Core Goals
- **Context Simplification**: Minimize LLM context via `struct.json` (`context: {summary: "проект делает X", files: ["src/main.py"]}`). Cache context in `parser.py` to reduce token usage (G5).
- **Idempotence**: Ensure parsers (TSK-006, TSK-012) produce consistent `struct.json` for same code. Add tests (TSK-012).
- **Ease of Use**: Target UX like “дружище, сделай код хорошо” in v0.3.0 (TSK-021, voice input via Grok API, Telegram `/fix`).
- **CI/CD Automation**: Automate PR parsing and task creation in CI/CD pipelines (TSK-012, GitHub Actions, GitLab).

## Code Parsing
- **Standalone Parser (TSK-006, TSK-007)**: Enhance `parser.py` for Python/JS, generate `struct.json` for simple projects (~10 files, TSK-016). Log errors (`errors: [{file: "app.js", line: 42, reason: "invalid syntax"}]`).
  - Why: Demo for Habr (TSK-017), pet projects (“pip install llmstruct, llmstruct parse”).
  - How: Error logging in `parser.py`, `cli.py` (`llmstruct parse --input src/`). Effort: ~5–7h.
  - Impact: Usability for v0.2.0, G1, G5.
- **CI/CD Module (TSK-012)**: Module `llmstruct` for GitHub/GitLab CI/CD, parsing PRs, updating `struct.json`, and integrating with DevOps tools (Grafana, MLflow, TSK-015). Report errors via Issues.
  - Why: Stable for large projects (~100+ files, TSK-016). Controlled parsing.
  - How: PyPI package, Action (`.github/workflows/parse.yml`), Issue creation (`gh issue create`). Docs: `integration.md`, `best_practices.md` (TSK-010). Effort: ~15–20h.
  - Impact: Scales to v0.3.0, G5.
- **LLM Instructions (TSK-024)**: Rework `struct.json` instructions for LLM. Split into base (parsing, G1, G5) and custom (user-defined, in `llmstruct.toml`). Ensure base instructions are idempotent.
  - Why: Per @kpblcaoo, improves context, token efficiency, code quality. Single `struct.json`, incremental parsing via `parser.py`.
  - How: Update `struct.json` schema, add tests (`src/tests/test_parser.py`). Effort: ~8–12h.
  - Impact: Core for G5, competitive vs Aider.

## Automation
- **Task Parser (TSK-011)**: `task_parser.py` to parse `[tasks]` from `llmstruct.toml` to Issues, `struct.json`. Support LLM (chatbot, Qwen-1.5B, Anthropic/Grok). Saves ~1–2h/week.
  - Example: `struct.json: tasks: [{id: "TSK-011", status: "open", assignee: "@kpblcaoo"}]`.
  - Impact: Core for G1, G4, dogfooding.
- **Chatbot Action (TSK-011)**: GitHub Action to parse chatbot output to `struct.json`.
  - How: `.github/workflows/chatbot.yml`. Effort: ~3–5h.
  - Impact: Bridges chatbot, G5.

## CI/CD Automation
- **struct.json Auto-Generation in CI/CD (NEW)**: Include struct.json generation as part of CI/CD pipeline to improve process efficiency without reducing its transparency.
  - Why: Automatically updated struct.json provides current project context for developers and LLMs, enables immediate context awareness in CI checks, reduces manual maintenance overhead
  - How: Add struct.json generation step in GitHub Actions after lint/test phases, commit updated struct.json back to repo if changed, use in subsequent CI steps for context-aware operations
  - Impact: Improves developer experience, enables context-aware CI/CD workflows, maintains project documentation automatically
  - Effort: ~3-5h (GitHub Action workflow, auto-commit logic)

## User Interface
- **Mini-UI (TSK-021)**: Flask app for `struct.json` to view/edit tasks, metrics. Replaces GitHub Projects in v0.3.0.
  - Why: Simplifies for community (TSK-017). Aider’s CLI focus shows UI demand.
  - How: `src/llmstruct/ui.py`, `templates/`, endpoints `/tasks`, `/update_task`. Deploy via @momai (Nginx, TSK-014). Effort: ~10–15h.
  - Impact: Usability from 6/10 to 8/10, G5.

## Database
- **SQLite Backend (TSK-022)**: Local SQLite DB for `struct.json` (tasks, metrics).
  - Why: API limits (Anthropic restricted, 2025). Enhances G1, G5.
  - How: `src/llmstruct/db.py`, `schema.sql`. Sync: `task_parser.py` → SQLite → `struct.json`. Effort: ~5–8h.
  - Impact: Robust storage, supports UI.

## API Enhancements
- **Cloud API Fallback (TSK-014)**: Anthropic, Grok, HuggingFace in `api.py` (`/generate_diff`, `/analyze_task`).
  - Why: 3060Ti VRAM limits (~7GB for Qwen-7B). Grok free tier (~100 req/day).
  - How: Test complex scenarios (TSK-016). Audit by @ivan-ib. Effort: ~15–20h.
  - Impact: Scalability, G5.
- **Continue Integration (TSK-014)**: Support Continue for LLM-driven diffs.
  - How: `.continue/config.json`, test with Qwen-1.5B. Effort: ~5–8h.
  - Impact: Attracts IDE users, G5.

## LLM Optimization
- **Qwen Optimization (TSK-016)**: Stabilize Qwen-1.5B for simple scenarios (v0.2.0). Target Qwen-7B or VPS (v0.3.0).
  - Why: Qwen posts on X (~1–5k likes) show demand.
  - How: Optimize indexing (TSK-003–TSK-005), test with `cli.py` (`--spec`). Effort: ~35–45h.
  - Impact: G5.
- **MLOps Metrics (TSK-015)**: `monitor.py` for LLM metrics (tokens, VRAM, CPU/RAM) in `struct.json` (`metrics: {tokens: 500, vram: 3.2GB}`).
  - Why: MLOps trend (MLflow, Grafana) for dev tools.
  - How: MLflow for logging, Grafana dashboards (@momai), scripts (@ivan-ib). Effort: ~12–18h.
  - Impact: Transparency (G4), G5.

## Recommendations
- **v0.2.0**: TSK-006, TSK-011, TSK-016, TSK-024. Standalone parser, chatbot/API.
- **v0.3.0**: TSK-012 (CI/CD), TSK-021 (UI), TSK-022 (SQLite), MLflow.
- **Actions**:
  - Update `parser.py` with error logs, context cache (TSK-006, @kpblcaoo).
  - Add Action for parsing, Issues (TSK-012, @momai).
  - Rework `struct.json` instructions, tests (TSK-024, @kpblcaoo).
  - Test MLflow (TSK-015, @momai, @ivan-ib).