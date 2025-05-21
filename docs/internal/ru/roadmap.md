# Дорожная карта llmstruct

**Статус**: Черновик  
**Версия**: 0.1.0  
**Последнее обновление**: 2025-05-18T23:00:27.888546Z  
**Автор**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. v0.2.0 (6–8 недель, Альфа)

- **Цели**: Автономный парсер, базовый LLM, демо (TSK-017).
- **Задачи**:
  - TSK-006, TSK-007: Улучшить `parser.py`.
  - TSK-011: `task_parser.py` для Issues.
  - TSK-014: Резервный API.
  - TSK-016: Стабилизировать Qwen-1.5B.
  - TSK-024: Инструкции в `struct.json`, идемпотентность.

## 2. v0.3.0 (3–6 месяцев, Бета)

- **Цели**: CI/CD, UI, масштабируемость.
- **Задачи**:
  - TSK-012: Модуль CI/CD.
  - TSK-015: MLflow, Grafana.
  - TSK-021: Flask UI.
  - TSK-023: Telegram-бот с `/fix`, `/errors`.

## 3. Действия

- Фокус на TSK-006, TSK-011, TSK-024 (@kpblcaoo).
- Планировать TSK-012, TSK-015 (@momai).
- Онбординг @ivan-ib (TSK-019).
