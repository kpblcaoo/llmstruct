# Дорожная карта llmstruct

План разработки `llmstruct` (v0.2.0, v0.3.0). Фокус: `struct.json`, Qwen, GPL-3.0. Команда: @kpblcaoo, @momai, @ivan-ib.

## v0.2.0 (6–8 недель, Альфа)
- **Цели**: Автономный парсер, базовый LLM, демо для Habr (TSK-017).
- **Задачи**:
  - TSK-006, TSK-007: Улучшить `parser.py`, логи ошибок, кэш контекста.
  - TSK-011: `task_parser.py` для Issues, `struct.json`.
  - TSK-014: Резервный API (Anthropic, Grok).
  - TSK-016: Стабилизировать Qwen-1.5B для простых проектов.
  - TSK-024: Базовые/пользовательские инструкции в `struct.json`, идемпотентность.
- **Результаты**:
  - CLI: `llmstruct parse --input src/`.
  - Пост на Habr: “llmstruct альфа!” (TSK-017).
  - ~5–20 контрибьюторов.

## v0.3.0 (3–6 месяцев, Бета)
- **Цели**: CI/CD, UI, масштабируемость, ~50 контрибьюторов.
- **Задачи**:
  - TSK-012: Модуль CI/CD, GitHub Action (@momai).
  - TSK-015: MLflow, Grafana для метрик (@momai, @ivan-ib).
  - TSK-021: Flask UI для `struct.json`.
  - TSK-022: SQLite-бэкенд.
  - TSK-023: Telegram-бот с `/fix`, `/errors`.
- **Результаты**:
  - Пакет PyPI: `pip install llmstruct`.
  - UI: Деплой через Nginx (TSK-014).
  - Видео: “llmstruct против Cursor” (TSK-017).

## Действия
- Фокус на TSK-006, TSK-011, TSK-024 для v0.2.0 (@kpblcaoo).
- Планировать TSK-012, TSK-015 (@momai).
- Онбординг @ivan-ib (TSK-019, @kpblcaoo).