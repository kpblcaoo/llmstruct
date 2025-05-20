# Технические идеи llmstruct

Технические идеи для `llmstruct` v0.2.0–v0.3.0, фокус на `struct.json`, LLM (Qwen в разработке, чат-бот как промежуточный, API Anthropic/Grok) и парсинг кода. Цели: G1 (универсальный JSON), G5 (оптимизация LLM). Команда: @kpblcaoo, @momai, @ivan-ib. Тренды (май 2025): Локальные LLM (Qwen, ~5–15k просмотров на Habr), MLOps (MLflow, Grafana), UX в dev tools.

## Основные цели
- **Упрощение контекста**: Минимизировать контекст LLM через `struct.json` (`context: {summary: "проект делает X", files: ["src/main.py"]}`). Кэшировать контекст в `parser.py` для экономии токенов (G5).
- **Идемпотентность**: Парсеры (TSK-006, TSK-012) дают одинаковый `struct.json` для одного кода. Добавить тесты (TSK-012).
- **Удобство**: UX уровня “дружище, сделай код крутым” в v0.3.0 (TSK-021, голосовой ввод через Grok API, Telegram `/fix`).
- **Автоматизация CI/CD**: Автоматизация парсинга PR и создания задач в CI/CD пайплайнах (TSK-012, GitHub Actions, GitLab).

## Парсинг кода
- **Автономный парсер (TSK-006, TSK-007)**: Улучшить `parser.py` для Python/JS, генерировать `struct.json` для малых проектов (~10 файлов, TSK-016). Логировать ошибки (`errors: [{file: "app.js", line: 42, reason: "неверный синтаксис"}]`).
  - Зачем: Демо для Habr (TSK-017), pet-проекты (“pip install llmstruct, llmstruct parse”).
  - Как: Логирование ошибок в `parser.py`, `cli.py` (`llmstruct parse --input src/`). Усилия: ~5–7ч.
  - Эффект: Удобство для v0.2.0, G1, G5.
- **Модуль CI/CD (TSK-012)**: Модуль `llmstruct` для CI/CD GitHub/GitLab, парсинг PR, обновление `struct.json`, интеграция с DevOps-инструментами (Grafana, MLflow, TSK-015). Ошибки в Issues.
  - Зачем: Стабильность для больших проектов (~100+ файлов, TSK-016). Контролируемый парсинг.
  - Как: Пакет PyPI, Action (`.github/workflows/parse.yml`), создание Issues (`gh issue create`). Доки: `integration.md`, `best_practices.md` (TSK-010). Усилия: ~15–20ч.
  - Эффект: Масштабирование в v0.3.0, G5.
- **Инструкции для LLM (TSK-024)**: Переработать инструкции в `struct.json`. Разделить на базовые (парсинг, G1, G5) и пользовательские (в `llmstruct.toml`). Базовые — идемпотентные.
  - Зачем: По идее @kpblcaoo, улучшает контекст, экономию токенов, качество кода. Один `struct.json`, инкрементальный парсинг через `parser.py`.
  - Как: Обновить схему `struct.json`, тесты (`src/tests/test_parser.py`). Усилия: ~8–12ч.
  - Эффект: Основа G5, конкурентно с Aider.

## Автоматизация
- **Парсер задач (TSK-011)**: `task_parser.py` для парсинга `[tasks]` из `llmstruct.toml` в Issues, `struct.json`. Поддержка LLM (чат-бот, Qwen-1.5B, Anthropic/Grok). Экономия ~1–2ч/нед.
  - Пример: `struct.json: tasks: [{id: "TSK-011", status: "open", assignee: "@kpblcaoo"}]`.
  - Эффект: Основа G1, G4, догфудинг.
- **Action для чат-бота (TSK-011)**: GitHub Action для парсинга вывода чат-бота в `struct.json`.
  - Как: `.github/workflows/chatbot.yml`. Усилия: ~3–5ч.
  - Эффект: Связка с чат-ботом, G5.

## Интерфейс
- **Мини-UI (TSK-021)**: Flask-приложение для просмотра/редактирования задач, метрик в `struct.json`. Замена GitHub Projects в v0.3.0.
  - Зачем: Упрощение для комьюнити (TSK-017). CLI-фокус Aider показывает спрос на UI.
  - Как: `src/llmstruct/ui.py`, `templates/`, эндпоинты `/tasks`, `/update_task`. Деплой через @momai (Nginx, TSK-014). Усилия: ~10–15ч.
  - Эффект: Удобство с 6/10 до 8/10, G5.

## База данных
- **SQLite-бэкенд (TSK-022)**: Локальная SQLite для `struct.json` (задачи, метрики).
  - Зачем: Ограничения API (Anthropic, 2025). Усиливает G1, G5.
  - Как: `src/llmstruct/db.py`, `schema.sql`. Синхронизация: `task_parser.py` → SQLite → `struct.json`. Усилия: ~5–8ч.
  - Эффект: Надёжное хранение, поддержка UI.

## API
- **Резервный API (TSK-014)**: Anthropic, Grok, HuggingFace в `api.py` (`/generate_diff`, `/analyze_task`).
  - Зачем: Ограничения VRAM 3060Ti (~7GB для Qwen-7B). Grok free tier (~100 запросов/день).
  - Как: Тест сложных сценариев (TSK-016). Аудит от @ivan-ib. Усилия: ~15–20ч.
  - Эффект: Масштабируемость, G5.
- **Интеграция Continue (TSK-014)**: Поддержка Continue для диффов через LLM.
  - Как: `.continue/config.json`, тест с Qwen-1.5B. Усилия: ~5–8ч.
  - Эффект: Привлечение IDE-юзеров, G5.

## Оптимизация LLM
- **Оптимизация Qwen (TSK-016)**: Стабилизировать Qwen-1.5B для простых сценариев (v0.2.0). Цель — Qwen-7B или VPS (v0.3.0).
  - Зачем: Посты о Qwen на X (~1–5k лайков) показывают спрос.
  - Как: Оптимизировать индексацию (TSK-003–TSK-005), тест через `cli.py` (`--spec`). Усилия: ~35–45ч.
  - Эффект: G5.
- **Метрики MLOps (TSK-015)**: `monitor.py` для метрик LLM (токены, VRAM, CPU/RAM) в `struct.json` (`metrics: {tokens: 500, vram: 3.2GB}`).
  - Зачем: Тренд MLOps (MLflow, Grafana) для dev tools.
  - Как: MLflow для логов, дашборды Grafana (@momai), скрипты (@ivan-ib). Усилия: ~12–18ч.
  - Эффект: Прозрачность (G4), G5.

## Рекомендации
- **v0.2.0**: TSK-006, TSK-011, TSK-016, TSK-024. Автономный парсер, чат-бот/API.
- **v0.3.0**: TSK-012 (CI/CD), TSK-021 (UI), TSK-022 (SQLite), MLflow.
- **Действия**:
  - Обновить `parser.py` с логами ошибок, кэшем контекста (TSK-006, @kpblcaoo).
  - Добавить Action для парсинга, Issues (TSK-012, @momai).
  - Переработать инструкции `struct.json`, тесты (TSK-024, @kpblcaoo).
  - Тестировать MLflow (TSK-015, @momai, @ivan-ib).