# 🔌 Continue Integration

Полная интеграция LLMStruct с VS Code Continue extension для AI-powered разработки.

## 📁 Содержимое папки

### 🔧 Конфигурация
- **`.continue/config.json`** - настройки Continue для подключения к LLMStruct API
- **`CONTINUE_INTEGRATION.md`** - подробная документация по установке и использованию

### 🧪 Тестирование  
- **`test_continue_api.py`** - скрипт для проверки работы Continue API endpoints

### 🔗 Связанные файлы (в основном проекте)
- **`src/llmstruct/api/routes/continue_adapter.py`** - API адаптер для Continue requests
- **`src/llmstruct/api/app.py`** - регистрация Continue routes в FastAPI

## 🚀 Быстрый старт

### 1. Установка Continue в VS Code
```bash
code --install-extension Continue.continue
```

### 2. Копирование конфигурации
```bash
# Из корня проекта:
cp -r integrations/continue/.continue ./
```

### 3. Запуск API и тестирование
```bash
# Запуск API:
source venv/bin/activate && python test_api.py &

# Тест Continue API:
python integrations/continue/test_continue_api.py
```

### 4. Использование в VS Code
- **Ctrl+Shift+I** - чат сбоку (полноценный диалог с AI)
- **Ctrl+I** - inline генерация кода
- **Ctrl+L** - анализ выделенного кода
- **Ctrl+K** - быстрое редактирование

## ✨ Особенности

- **Использует ваши модели** - Claude через Anthropic API
- **Контекст проекта** - знает структуру LLMStruct
- **Специальные команды** - `/fastapi-endpoint`, `/analyze-structure`, etc.
- **Русский язык** - полная поддержка
- **Real-time чат** - прямо в редакторе

## 📊 Архитектура

```
VS Code Continue → Continue Adapter → LLM Service → Anthropic Claude
                     ↓
                  Continue API
                 (OpenAI-compatible)
```

## 🔧 Логи и отладка

```bash
# Логи API:
tail -f api_system.log | grep Continue

# Проверка статуса:
curl -H "X-API-Key: dev-key" http://localhost:8000/api/continue/v1/models
```

---

**🎯 Результат:** AI-powered IDE с пониманием LLMStruct проекта! 