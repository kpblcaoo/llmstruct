# 🦙 LLMStruct Ollama Chat Bot

Продвинутый Telegram бот для общения с Олламой + fallback на Грок/Антропик, с памятью, кешем и доступом к файлам проекта.

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
# Установка зависимостей
pip install httpx

# Настройка переменных окружения
export TELEGRAM_BOT_TOKEN="7576808324:AAG_lyXEt-AEfGCSJ5VoOx1oUEniyjcmHBI"
export GROK_API_KEY="your_grok_key"          # Опционально
export ANTHROPIC_API_KEY="your_claude_key"   # Опционально
```

### 2. Запуск бота

```bash
# Простой запуск
python start_ollama_bot.py

# Или напрямую
python ollama_chat_bot.py
```

## 🏗️ Архитектура

### Компоненты системы:

1. **`OllamaChatBot`** - Основной класс бота
2. **`ModelManager`** - Управление LLM провайдерами
3. **`FileManager`** - Доступ к файлам проекта через CLI
4. **`MemoryManager`** - Память и контекст разговоров
5. **`CursorReporter`** - Отправка отчетов из Cursor

### Fallback система:

```
🦙 Ollama (primary) → 🚀 Grok → 🤖 Claude
```

## 📱 Команды бота

### Основные команды:
- `/start` - Приветствие и справка
- `/help` - Подробная справка
- `/memory` - Статистика сессии
- `/models` - Доступные модели

### Доступ к файлам:
- `/file src/llmstruct/cli.py` - Читать файл
- `/ls src/llmstruct` - Список директории  
- `/ls` - Корневая директория

### CLI команды:
- `/cli status` - Статус проекта
- `/cli metrics` - Метрики системы
- `/cli ai_status` - Статус AI системы
- `/cli workflow` - Статус workflow
- `/cli search context` - Поиск возможностей

### Обычные сообщения:
Любое сообщение без команды отправляется в AI для общения.

## 🧠 Система памяти

### Возможности:
- ✅ Контекст разговора (до 10 последних сообщений)
- ✅ Автосохранение каждые 5 сообщений
- ✅ Ограничение длины сессии (50 сообщений → 40)
- ✅ Персистентное хранение в JSON
- ✅ Отслеживание используемых моделей

### Файлы хранения:
```
data/ollama_chat/
├── sessions.json           # Сессии пользователей
└── global_context.json     # Глобальный контекст
```

## 🤖 Интеграция моделей

### Ollama (основная):
```python
# URL: http://localhost:11434
# Модель по умолчанию: llama3.2:3b
# Timeout: 60 секунд
```

### Grok (fallback):
```python
# API: https://api.x.ai/v1/chat/completions
# Модель: grok-beta
# Требует: GROK_API_KEY
```

### Claude (fallback):
```python
# API: https://api.anthropic.com/v1/messages  
# Модель: claude-3-haiku-20240307
# Требует: ANTHROPIC_API_KEY
```

## 📁 Доступ к файлам

### Безопасность:
- ✅ Только чтение файлов внутри проекта
- ✅ Проверка путей на выход за пределы проекта
- ✅ Ограничение размера вывода (100 строк / 50 элементов)

### CLI команды:
```python
safe_commands = {
    "status": ["python", "-m", "llmstruct.cli", "parse", "--help"],
    "query": ["python", "-m", "llmstruct.cli", "query", "--help"],
    "context": ["python", "-m", "llmstruct.cli", "context", "--help"],
    "metrics": ["python", "-m", "llmstruct.cli", "metrics", "status"],
    "ai_status": ["python", "-c", "from auto_init_ai_system import get_ai_status; print(get_ai_status())"],
    "workflow": ["python", "-c", "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"],
    "search": ["python", "-c", "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('{}'))"]
}
```

## 📋 Отправка отчетов из Cursor

### Использование CursorReporter:

```python
from cursor_reporter import report_started, report_completed, report_failed

# Простые функции
report_started("Implementing new feature", "Started work on user authentication")
report_completed("Bug fix", "Fixed memory leak in background task")
report_failed("API integration", "Connection timeout errors")

# Асинхронные версии
import asyncio
from cursor_reporter import report_task_progress

async def my_task():
    await report_task_progress("Data processing", "Processed 50% of records")
```

### Форматы отчетов:

```
🚀 Cursor Task Report

🔵 Priority: Normal
📋 Task: Implementing new feature  
📊 Status: Started
🕐 Time: 2025-05-30 18:00:00

Started work on user authentication

*Sent from Cursor IDE*
```

## 🔧 Диагностика

### Проверка системы:
```bash
python start_ollama_bot.py
```

Выводит:
- ✅/❌ Зависимости Python
- ✅/❌ Ollama доступность + модели
- ✅/⚠️ API ключи (Grok, Claude)
- ✅ Создание директорий

### Логи:
```
logs/ollama_chat_bot.log  # Основные логи бота
```

### Структура логов:
```
2025-05-30 18:00:00 - INFO - 🤖 OllamaChatBot initialized
2025-05-30 18:00:01 - INFO - 📚 Loaded 3 chat sessions  
2025-05-30 18:00:02 - INFO - 🚀 LLMStruct Ollama Chat Bot starting...
2025-05-30 18:00:05 - INFO - 💬 Message from Михаил: Привет...
2025-05-30 18:00:06 - INFO - 🦙 Trying Ollama for user Михаил
2025-05-30 18:00:08 - INFO - ✅ Report sent: Task completed - completed
```

## 🛠️ Установка Ollama

### Linux/macOS:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.2:3b
```

### Windows:
1. Скачать с https://ollama.ai/
2. Установить 
3. `ollama serve`
4. `ollama pull llama3.2:3b`

### Проверка:
```bash
curl http://localhost:11434/api/tags
```

## 🔀 Примеры использования

### 1. Обычный чат:
```
Пользователь: Привет! Как дела?
Бот: 🦙 Ollama: Привет! У меня всё отлично, спасибо! Готов помочь...
```

### 2. Чтение файлов:
```
Пользователь: /file src/llmstruct/cli.py
Бот: 📄 src/llmstruct/cli.py
```python
#!/usr/bin/env python3
...
```

### 3. CLI команды:
```
Пользователь: /cli ai_status
Бот: ✅ ai_status
```
🧠 AI System Status: Active
📊 Modules: 272 analyzed
...
```

### 4. Fallback в действии:
```
Логи:
INFO - 🦙 Trying Ollama for user Михаил
ERROR - Ollama request failed: Connection refused  
INFO - 🚀 Ollama failed, trying Grok
INFO - 🚀 Grok: Success!

Пользователь: Привет!
Бот: 🚀 Grok: Привет! Как дела? Чем могу помочь?
```

## 📊 Метрики и мониторинг

### Отслеживаемые данные:
- 📱 Количество сообщений в сессии
- 🤖 Использованные модели
- ⏰ Время последней активности  
- 📈 Общее количество сессий
- 🔄 Частота автосохранений

### Команда статистики:
```
/memory

🧠 Memory Statistics

Session: ollama_-4938821563_123456789
• Messages: 15
• Started: 2025-05-30 17:30:00
• Last activity: 2025-05-30 18:15:00  
• Preferred model: ollama

Global:
• Total sessions: 3
```

## ⚠️ Troubleshooting

### Проблема: Ollama не отвечает
```bash
# Проверить статус
curl http://localhost:11434/api/tags

# Перезапустить
pkill ollama
ollama serve &
```

### Проблема: Все модели недоступны  
```
❌ All AI providers are currently unavailable
Please try again later.
```

**Решение:**
1. Проверить Ollama: `ollama serve`
2. Проверить API ключи: `echo $GROK_API_KEY`
3. Проверить интернет соединение

### Проблема: Доступ к файлам
```
❌ Access denied: path outside project
```

**Решение:**
- Использовать относительные пути от корня проекта
- Пример: `/file src/llmstruct/cli.py` вместо `/file /home/user/...`

## 🎯 Roadmap

### Ближайшие улучшения:
- [ ] Поддержка изображений в сообщениях
- [ ] Интеграция с календарем задач
- [ ] Расширенная система плагинов
- [ ] Веб-интерфейс для управления
- [ ] Поддержка голосовых сообщений

### Интеграции:
- [ ] GitHub API для работы с репозиториями
- [ ] Jira/Trello для управления задачами  
- [ ] Notion API для документации
- [ ] Docker интеграция для запуска команд

## 📄 Лицензия

MIT License - используйте как хотите!

---

**Создано для проекта LLMStruct** 🚀 