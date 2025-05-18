# Руководство по интеграции llmstruct

Интегрируй `llmstruct` в проект для разработки с JSON и LLM. Поддерживает CLI, CI/CD, кастомные воркфлоу.

## Использование CLI
Для pet-проектов:
```bash
pip install llmstruct
llmstruct parse --input src/ --output struct.json
```
- Генерирует `struct.json` с задачами, контекстом, ошибками.
- Смотри [examples/struct.json](#examples/struct.json).

## Настройка CI/CD
Для GitHub/GitLab:
1. Добавь `llmstruct` в репо:
   ```bash
   pip install llmstruct
   ```
2. Создай `.github/workflows/parse.yml`:
   ```yaml
   name: Парсинг кода
   on: [push, pull_request]
   jobs:
     parse:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - run: llmstruct parse --input src/ --output struct.json
         - name: Сообщить об ошибках
           run: |
             if grep -q '"errors"' struct.json; then
               echo "Обнаружены ошибки парсинга!"
               gh issue create --title "Ошибка парсинга" --body "$(cat struct.json | jq '.errors')"
               exit 1
             fi
   ```
3. Проверяй Issues для ошибок парсинга.

## Конфигурация
- Редактируй `llmstruct.toml` для пользовательских инструкций LLM (см. [examples/struct.json](#examples/struct.json)).
- Следуй [best_practices.md](#best_practices.md) для чистого кода.

## Продвинутое
- Используй Telegram-бот (`/tasks`, `/fix`) для обновлений в реальном времени (TSK-023).
- Разверни UI для управления задачами (TSK-021, v0.3.0).

Смотри [onboarding.md](#onboarding.md), чтобы начать контрибьютить!