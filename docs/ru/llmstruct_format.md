# Спецификация формата JSON для llmstruct

**Статус**: Черновик  
**Версия**: 0.1.0  
**Последнее обновление**: 2025-05-18T23:00:27.888546Z  
**Автор**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Введение

Формат JSON llmstruct — это универсальная, расширяемая структура для представления кодовых баз, разработанная для автоматизации и интеграции с LLM.

## 2. Цели



## 3. Структура JSON

Формат состоит из трех полей верхнего уровня: `metadata`, `toc` и `modules`.

### 3.1. `metadata`

- **Тип**: Объект
- **Обязательные поля**:
  - `project_name`: Строка, название проекта (например, "llmstruct").
  - `description`: Строка, краткое описание.
  - `version`: Строка, метка времени ISO 8601 (например, "2025-05-18T23:00:27.888546Z").
  - `authors`: Массив объектов (имя, github, email).
  - `instructions`: Массив строк, инструкции для LLM.
  - `goals`: Массив строк, цели проекта.
  - `stats`: Объект (modules_count, functions_count, classes_count, call_edges_count).
  - `folder_structure`: Массив объектов (path, type).

**Пример**:
```json
{
  "metadata": {
    "project_name": "llmstruct",
    "description": "Утилита для генерации структурированного JSON для кодовых баз",
    "version": "2025-05-18T23:00:27.888546Z",
    "authors": [{"name": "Mikhail Stepanov", "github": "kpblcaoo", "email": "kpblcaoo@gmail.com"}],
    "instructions": ["Следовать лучшим практикам", "Сохранять функциональность"],
    "goals": [],
    "stats": {
      "modules_count": 14,
      "functions_count": 27,
      "classes_count": 3,
      "call_edges_count": 90
    },
    "folder_structure": [
      {"path": "src/", "type": "directory"},
      {"path": "src/llmstruct/cli.py", "type": "file"}
    ]
  }
}
```
