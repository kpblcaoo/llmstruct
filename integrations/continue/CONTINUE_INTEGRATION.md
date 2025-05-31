# 🔌 Continue Integration Guide

## Что такое Continue?

[Continue](https://continue.dev/) - это VS Code расширение, которое превращает ваш редактор в AI-powered IDE. Наша LLMStruct интеграция дает вам доступ к контекстно-осведомленному AI прямо в редакторе!

## ✨ Возможности

### 🎯 Основные функции:
- **Inline Chat** - AI помощник прямо в коде
- **Code Generation** - генерация с пониманием проекта
- **Code Explanation** - умные объяснения
- **Refactoring** - предложения по улучшению
- **Custom Commands** - специальные команды для LLMStruct

### 🧠 LLMStruct-специфичные команды:
- `/analyze-structure` - анализ архитектуры кода
- `/add-context` - добавление контекстной интеграции  
- `/fastapi-endpoint` - создание FastAPI эндпоинтов
- `/websocket-handler` - WebSocket обработчики

## 🚀 Быстрый старт

### 1. Установка Continue
```bash
# В VS Code Command Palette (Ctrl+Shift+P):
ext install Continue.continue
```

### 2. Запуск LLMStruct API
```bash
source venv/bin/activate
python test_api.py &
```

### 3. Использование
- **Ctrl+I** - Inline chat
- **Ctrl+Shift+I** - Sidebar chat
- **Ctrl+L** - Выделить код и спросить
- **Ctrl+K** - Quick command

## ⚙️ Конфигурация

Файл `.continue/config.json` уже настроен для работы с LLMStruct API:

```json
{
  "models": [
    {
      "title": "LLMStruct Claude",
      "provider": "openai", 
      "apiBase": "http://localhost:8000/api/continue",
      "apiKey": "dev-key"
    }
  ]
}
```

## 📖 Примеры использования

### Анализ кода:
1. Выделите код в редакторе
2. Нажмите **Ctrl+L**
3. Напишите: `/analyze-structure`

### Создание API endpoint:
1. Выделите функцию
2. **Ctrl+I**
3. Команда: `/fastapi-endpoint`

### Добавление контекста:
1. Выделите класс/функцию
2. **Ctrl+L** 
3. Команда: `/add-context`

## 🔧 Режимы работы

### Inline Chat (Ctrl+I)
- Генерация кода на месте
- Быстрые правки и улучшения
- Объяснения выделенного кода

### Sidebar Chat (Ctrl+Shift+I)  
- Полноценный диалог с AI
- Планирование архитектуры
- Подробные объяснения

### Quick Edit (Ctrl+K)
- Быстрое редактирование
- Рефакторинг
- Оптимизация

## 🎭 Специальные команды

| Команда | Описание | Пример |
|---------|----------|--------|
| `/analyze-structure` | Анализ архитектуры | Проверка модульности |
| `/add-context` | Интеграция контекста | SmartContextOrchestrator |
| `/fastapi-endpoint` | API эндпоинт | С auth + logging |
| `/websocket-handler` | WebSocket | Real-time обработка |

## 🐛 Решение проблем

### API не отвечает:
```bash
# Проверьте, что API запущен:
curl http://localhost:8000/api/v1/system/health

# Перезапустите API:
source venv/bin/activate && python test_api.py
```

### Continue не подключается:
1. Проверьте `.continue/config.json`
2. Убедитесь что `apiBase` правильный
3. Проверьте API key в конфиге

### Нет ответов от AI:
1. Проверьте логи: `tail -f api_system.log`
2. Убедитесь что ANTHROPIC_API_KEY в .env
3. Проверьте интернет соединение

## 📊 Мониторинг

### Логи API:
```bash
tail -f api_system.log | grep Continue
```

### Проверка эндпоинтов:
```bash
# Модели:
curl -H "X-API-Key: dev-key" http://localhost:8000/api/continue/v1/models

# Тест чата:
curl -X POST -H "Content-Type: application/json" -H "X-API-Key: dev-key" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"model":"claude-3-haiku"}' \
  http://localhost:8000/api/continue/v1/chat/completions
```

## 🚀 Продвинутые функции

### Embeddings (в разработке):
- Семантический поиск в коде
- Контекстные предложения
- Интеллектуальный autocomplete

### Custom Context Providers:
- Интеграция с `struct.json`
- Анализ зависимостей
- Метрики кода

### Team Features:
- Shared configurations
- Code style enforcement  
- Collaborative AI sessions

## 📚 Ресурсы

- [Continue Documentation](https://continue.dev/docs)
- [LLMStruct API Docs](http://localhost:8000/docs)
- [GitHub Issues](https://github.com/kpblcaoo/llmstruct/issues)

---

**🎉 Готово!** Теперь у вас есть AI-powered IDE с пониманием LLMStruct проекта! 