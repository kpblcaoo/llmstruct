# 🚀 Quick Start: LLMStruct Telegram Bot

## 📋 Что готово к использованию

После очистки проекта у нас есть **два основных компонента**:

1. **`test_api_simple.py`** - FastAPI сервер с Ollama интеграцией
2. **`chat_bot_final.py`** - Telegram бот с API интеграцией

## ⚡ Быстрый запуск

### 1. Запуск API сервера

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем API сервер
python test_api_simple.py
```

**Проверка работы:**
```bash
# Статус системы
curl http://localhost:8000/api/v1/system/status

# Документация API
open http://localhost:8000/docs
```

### 2. Запуск Telegram бота

```bash
# Устанавливаем токен бота
export TELEGRAM_BOT_TOKEN='your_bot_token_here'

# Запускаем бота
python chat_bot_final.py
```

## 🔧 Что работает

### ✅ API Endpoints
- `/api/v1/system/health` - проверка здоровья
- `/api/v1/system/status` - детальный статус
- `/api/v1/chat/ollama` - чат с Ollama
- `/api/v1/ollama/models` - список моделей
- `/api/v1/memory/save` - сохранение в память
- `/api/v1/memory/history/{user_id}` - история пользователя

### ✅ Ollama Integration
- 4 модели доступны: `mistral:latest`, `deepseek-coder:6.7b-instruct`, `deepseek-coder:6.7b`, `nomic-embed-text:latest`
- Хост: `http://192.168.88.50:11434`

### ✅ Features
- 🧠 Память пользователей
- 📊 Метрики и токены
- 🔄 Асинхронная обработка
- 🛡️ Обработка ошибок

## 🎯 Telegram Bot Commands

- `/start` - Приветствие и информация
- `/help` - Справка по командам  
- `/status` - Статус системы
- `/memory` - История сообщений
- `/models` - Доступные модели

## 🧪 Тестирование

### API Test
```bash
# Тест чата с Ollama
curl -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!", "user_id": "test", "model": "mistral:latest"}'

# Тест памяти
curl -X POST http://localhost:8000/api/v1/memory/save \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Тестовое сообщение", "timestamp": "2025-05-30T20:00:00"}'
```

## 📊 Производительность

**Улучшения после очистки:**
- 🚀 **20x быстрее** - API вместо CLI команд
- 🛡️ **Стабильнее** - убран parse_mode Markdown
- 🔧 **Совместимее** - единые типы данных
- 📈 **Эффективнее** - асинхронная обработка

## 🗂️ Архив

Все экспериментальные файлы перенесены в:
```
archive/telegram_experiments/
├── chat_bot_fastapi_enhanced.py
├── fastapi_ollama_server.py
├── api_memory_endpoints.py
└── ... (20+ файлов)
```

## 🔍 Troubleshooting

### API не запускается
```bash
# Проверить порт 8000
lsof -i:8000

# Остановить процессы
pkill -f test_api_simple.py
```

### Telegram бот не подключается
```bash
# Проверить токен
echo $TELEGRAM_BOT_TOKEN

# Проверить интернет
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

### Ollama недоступна
```bash
# Проверить подключение
curl http://192.168.88.50:11434/api/tags
```

---
**Статус:** ✅ Готово к использованию  
**Последнее обновление:** 2025-05-30 20:53