# 🔧 Continue VS Code Extension Integration

Интеграция LLMStruct с Continue VS Code extension для продвинутой AI-assisted разработки.

## ✨ Возможности

### 🤖 **AI Models**
- **Claude 3 Haiku** через LLMStruct FastAPI
- **Автокомплит** с контекстом проекта
- **Настраиваемые API endpoints** через .env

### 🛠️ **Custom Commands**
- `/analyze-structure` - Анализ архитектуры кода
- `/add-context` - Добавление context orchestration
- `/fastapi-endpoint` - Генерация FastAPI endpoints
- `/websocket-handler` - Создание WebSocket handlers
- `/telegram-command` - Команды для Telegram бота
- `/memory-integration` - Интеграция системы памяти

### 💬 **Slash Commands**
- `/edit` - Редактирование с AI помощью
- `/comment` - Умные комментарии
- `/epic` - Управление эпиками и задачами
- `/memory` - Функции системы памяти

## 🚀 Установка и настройка

### 1. Установите Continue Extension
```bash
# В VS Code
ext install Continue.continue
```

### 2. Настройте конфигурацию
```bash
# Базовая настройка (localhost:8000)
cd integrations/continue
python setup_config.py

# Или с custom настройками
export LLMSTRUCT_API_BASE="https://your-api.com"
export LLMSTRUCT_API_KEY="your-api-key"
python setup_config.py
```

### 3. Создайте .env файл (опционально)
```bash
# В корне проекта
echo "LLMSTRUCT_API_BASE=http://localhost:8000" > .env
echo "LLMSTRUCT_API_KEY=your-secure-key" >> .env
```

## 🔧 Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `LLMSTRUCT_API_BASE` | `http://localhost:8000` | Base URL LLMStruct API |
| `LLMSTRUCT_API_KEY` | `dev-key` | API ключ для аутентификации |

## 📁 Структура файлов

```
integrations/continue/
├── .continue/
│   ├── config.json          # Финальная конфигурация
│   └── config.template.json # Шаблон с переменными
├── setup_config.py          # Скрипт настройки
└── README.md               # Этот файл
```

## 🎯 Использование

### Базовые команды
1. **Ctrl+Shift+P** → "Continue: Start"
2. Выберите код и нажмите **Ctrl+I**
3. Используйте slash commands: `/edit`, `/comment`, etc.

### LLMStruct специфичные команды
```javascript
// Пример: добавление context orchestration
// Выделите код и используйте /add-context

function myFunction() {
    // Код будет дополнен SmartContextOrchestrator patterns
}
```

### Интеграция с эпиками
```python
# Используйте /epic для создания epic-related кода
# Автоматически добавляется интеграция с WorkspaceStateManager
```

## 🔍 Отладка

### Проверка API соединения
```bash
# Тест базового API
curl http://localhost:8000/api/v1/system/health

# Тест Continue endpoint
curl http://localhost:8000/api/continue/models
```

### Логи Continue
- **VS Code**: Developer → Toggle Developer Tools → Console
- Ищите сообщения от Continue extension

### Общие проблемы

1. **API недоступен**
   ```bash
   # Запустите LLMStruct сервер
   source venv/bin/activate
   python test_api.py
   ```

2. **Неверная конфигурация**
   ```bash
   # Пересоздайте конфигурацию
   python integrations/continue/setup_config.py
   ```

3. **Проблемы с аутентификацией**
   ```bash
   # Проверьте API ключ
   echo $LLMSTRUCT_API_KEY
   ```

## 🎮 Advanced Features

### Context Providers
- **File**: Контекст текущего файла
- **Folder**: Контекст папки
- **Codebase**: Полный контекст проекта
- **Terminal**: Интеграция с терминалом

### Tab Autocomplete
Умный автокомплит на основе:
- Контекста проекта
- LLMStruct patterns
- Ваших coding patterns

## 📊 Интеграция с LLMStruct

Continue автоматически использует:
- **SmartContextOrchestrator** для оптимизации контекста
- **Copilot Manager** для VS Code интеграции
- **Workspace State** для session management
- **Epic System** для task-oriented coding

## 🔄 Обновление конфигурации

```bash
# При изменении .env или добавлении новых features
cd integrations/continue
python setup_config.py

# Перезапустите VS Code для применения изменений
```

---

💡 **Tip**: Continue работает лучше всего когда LLMStruct API server запущен локально с полным контекстом проекта! 