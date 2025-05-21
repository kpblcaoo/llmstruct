# Конфигурация LLMstruct

**Статус документа**: Черновик  
**Версия**: 0.1.0  
**Последнее обновление**: 2025-05-18T12:35:00Z  
**Автор**: Михаил Степанов ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## Обзор

LLMstruct поддерживает настройку через файл `llmstruct.toml` в корне проекта. Этот файл определяет цели проекта и настройки CLI, обеспечивая гибкость для пользователей. Аргументы командной строки имеют приоритет над настройками в `llmstruct.toml`.

## Файл конфигурации

Создайте файл `llmstruct.toml` в корне проекта. Файл использует формат TOML и включает две основные секции: `[goals]` и `[cli]`.

### Пример `llmstruct.toml`

```toml
[goals]
goals = [
    "Создать универсальный JSON-формат для структуры кода",
    "Поддержать интеграцию с LLM для улучшенной автоматизации"
]

[cli]
language = "python"
include_patterns = ["*.py"]
exclude_patterns = ["tests/*", "venv/*"]
include_ranges = true
include_hashes = false
```

### Секции

- `[goals]`:
  - `goals`: Список целей проекта (строки). Используется в `struct.json` под `metadata.goals`.
- `[cli]`:
  - `language`: Язык программирования (`python`, `javascript`). По умолчанию: `python`.
  - `include_patterns`: Список шаблонов файлов для включения (например, `["*.py"]`).
  - `exclude_patterns`: Список шаблонов файлов для исключения (например, `["tests/*"]`).
  - `include_ranges`: Булево, включать диапазоны строк для функций/классов. По умолчанию: `false`.
  - `include_hashes`: Булево, включать хэши файлов. По умолчанию: `false`.

## Использование

1. Создайте `llmstruct.toml` в корне проекта.
2. Запустите LLMstruct:
   ```bash
   python -m llmstruct .
   ```
   Это использует настройки из `llmstruct.toml`.
3. Переопределите настройки через CLI:
   ```bash
   python -m llmstruct . --goals "Пользовательская цель" --language javascript
   ```
   Аргументы CLI имеют приоритет над `llmstruct.toml`.

## Примечания

- Если цели не указаны (через `--goals` или `llmstruct.toml`), LLMstruct выводит предупреждение и устанавливает `metadata.goals` в пустой список.
- Убедитесь, что установлен `toml` (`pip install toml`) для парсинга конфигурации.
- Некорректные файлы `llmstruct.toml` вызывают сообщение об ошибке, но не останавливают выполнение.

## Ссылки

- [Спецификация JSON-формата LLMstruct](llmstruct_format.md)
- [Структура проекта](project_structure.md)