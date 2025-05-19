# Руководство по началу работы с llmstruct

Начни использовать `llmstruct`, open-source инструмент для разработки с JSON и LLM. Лицензия GPL-3.0.

## Быстрый старт
1. **Установка**:
   ```bash
      cd llmstruct/
      pip install -e .
   ```
2. **Парсинг кода**:
   ```bash
   llmstruct parse --input src/ --output struct.json
   ```
3. **Изучение**:
   - Смотри `struct.json` для задач, контекста, метрик.
   - Проверяй ошибки: `errors: [{file: "app.js", line: 42, reason: "неверный синтаксис"}]`.
4. **Контрибьют**:
   - Присоединяйся к Issues на GitHub: [github.com/kpblcaoo/llmstruct](#).
   - Пробуй Telegram-бот: `/join`, `/tasks`, `/fix`.

## Следующие шаги
- Читай [integration.md](#integration.md) для настройки CI/CD.
- Следуй [best_practices.md](#best_practices.md) для чистого кода.
- Смотри [examples/struct.json](#examples/struct.json) для базовых/пользовательских инструкций.

Добро пожаловать в комьюнити `llmstruct`! Давай сделаем разработку умнее.