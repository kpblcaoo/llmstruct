# LLMStruct CLI — Документация

## Оглавление
- [Введение](#введение)
- [Быстрый старт](#быстрый-старт)
- [Архитектура CLI](#архитектура-cli)
- [Основные команды](#основные-команды)
- [Модульная структура](#модульная-структура)
- [Примеры использования](#примеры-использования)
- [Best Practices](#best-practices)
- [FAQ](#faq)

---

## Введение

CLI (`src/llmstruct/cli.py`) — основной интерфейс для работы с системой LLMStruct из командной строки. Он реализован как thin router: вся логика вынесена в модули (`src/llmstruct/modules/cli/`). Это обеспечивает чистоту, расширяемость и простоту поддержки.

---

## Быстрый старт

```bash
# Запуск CLI (пример)
python -m llmstruct.cli parse .
python -m llmstruct.cli query --prompt "Что делает этот проект?"
```

- Все команды CLI поддерживают `--help` для справки.
- Для большинства задач рекомендуется использовать модульные команды (см. ниже).

---

## Архитектура CLI

- **cli.py** — только роутер: парсит аргументы, вызывает функции из modules/cli.
- **modules/cli/** — вся бизнес-логика CLI-команд (parse, query, audit, copilot и др.).
- **ARCHIVE/** — устаревшие файлы, не используемые в новой архитектуре.

**Преимущества:**
- Легко расширять и тестировать отдельные команды.
- Нет дублирования логики.
- Быстрая поддержка новых фич.

---

## Основные команды

| Команда                | Описание                                      |
|------------------------|-----------------------------------------------|
| `parse`                | Парсинг кода и генерация struct.json          |
| `query`                | Запрос к LLM с контекстом                     |
| `context`              | Генерация context.json                        |
| `dogfood`              | Анализ dogfooding (заглушка/разработка)       |
| `review`               | LLM review кода (заглушка/разработка)         |
| `copilot`              | Интеграция Copilot и управление контекстом    |
| `audit`                | Аудит структуры проекта                       |
| `analyze-duplicates`   | Анализ дублирования функций                   |

**Пример справки:**
```bash
python -m llmstruct.cli --help
python -m llmstruct.cli parse --help
```

---

## Модульная структура

- Все команды реализованы в отдельных файлах в `modules/cli/`:
  - `parse.py`, `query.py`, `audit.py`, `copilot.py`, ...
- Для расширения CLI — добавь новый модуль и зарегистрируй его в `cli.py`.
- Старые файлы CLI перенесены в `ARCHIVE/` и не используются.

---

## Примеры использования

### Генерация структуры кода
```bash
python -m llmstruct.cli parse . -o struct.json --language python
```

### Запрос к LLM
```bash
python -m llmstruct.cli query --prompt "Опиши архитектуру проекта" --context struct.json
```

### Аудит проекта
```bash
python -m llmstruct.cli audit . --include-duplicates
```

### Copilot-интеграция
```bash
python -m llmstruct.cli copilot . status
python -m llmstruct.cli copilot . suggest --query "Как улучшить архитектуру?"
```

### Фильтрация файлов и директорий

- Включить только Python-файлы:
  ```bash
  python -m llmstruct.cli parse . --include '*.py'
  ```
- Исключить архив и тесты:
  ```bash
  python -m llmstruct.cli parse . --exclude-dir .ARCHIVE/,tests/
  ```
- Исключить все markdown-файлы и директорию docs:
  ```bash
  python -m llmstruct.cli parse . --exclude '*.md' --exclude-dir docs/
  ```
- Включить только src/llmstruct и scripts:
  ```bash
  python -m llmstruct.cli parse . --include-dir src/llmstruct/,scripts/
  ```
- Можно комбинировать:
  ```bash
  python -m llmstruct.cli parse . --include '*.py,*.md' --exclude-dir .ARCHIVE/ --exclude 'test_*'
  ```

> Аргументы можно указывать несколько раз или через запятую. Директории фильтруются независимо от паттернов файлов.

---

## Best Practices
- Используй только модульные команды — не редактируй cli.py напрямую.
- Для новых CLI-фич — создай модуль в `modules/cli/`.
- Архивируй устаревшие файлы в `ARCHIVE/`.
- Для сложных сценариев — используй workflow и context orchestrator.
- Проверяй справку команд через `--help`.

---

## FAQ

**Q:** Как добавить новую CLI-команду?
**A:** Создай модуль в `modules/cli/`, зарегистрируй в `cli.py` через импорт и добавь в парсер аргументов.

**Q:** Где искать старые реализации?
**A:** В папке `ARCHIVE/`.

**Q:** Как узнать, какие команды доступны?
**A:** `python -m llmstruct.cli --help`

---

> Документация актуальна для архитектуры 2024+. Для legacy-CLI см. ARCHIVE/ 