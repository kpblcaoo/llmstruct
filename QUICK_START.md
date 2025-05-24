# 🚀 LLMStruct: Быстрый старт

**LLMStruct v0.4.1** - универсальный JSON-формат для кодовых баз с интеграцией LLM и автоматической валидацией данных.

## 📦 Установка

### Разработка
```bash
# Клонирование и установка в режиме разработки
git clone https://github.com/kpblcaoo/llmstruct.git
cd llmstruct
pip install -e .

# Проверка установки
llmstruct --help
```

### Продакшн
```bash
pip install llmstruct
```

## 🛠️ Режимы использования

### 1. CLI Режим (для разработчиков)

#### Основные команды
```bash
# Парсинг проекта в struct.json
llmstruct parse . -o struct.json

# Интерактивный режим с LLM
llmstruct interactive . --context struct.json

# Запросы к LLM с контекстом
llmstruct query --prompt "Объясни архитектуру" --context struct.json

# Copilot интеграция
llmstruct copilot . init
llmstruct copilot . status
```

#### Интерактивный CLI
```bash
llmstruct interactive .
```
**Доступные команды в интерактивном режиме:**
- `/view <path>` - просмотр файлов/папок
- `/write <file> <content>` - запись в файл  
- `/auto-update` - обновление struct.json
- `/queue run` - обработка очереди команд
- `/cache stats` - статистика кэша
- `/copilot status` - статус Copilot
- `/help` - список всех команд

### 2. GitHub Copilot Pro Режим

#### Настройка Copilot интеграции
```bash
# Инициализация Copilot контекста
llmstruct copilot . init --force

# Загрузка слоёв контекста
llmstruct copilot . load --layer core
llmstruct copilot . load --layer data

# Проверка статуса
llmstruct copilot . status
```

#### Экспорт контекста для Copilot
```bash
# JSON формат
llmstruct copilot . export --format json --output copilot_context.json

# Экспорт конкретных слоёв
llmstruct copilot . export --layers core,data,insights --output context_filtered.json
```

#### Валидация изменений
```bash
# Валидация файла
llmstruct copilot . validate --file-path src/main.py --change-type edit

# Предложения по улучшению
llmstruct copilot . suggest --query "Оптимизация производительности"
```

## ⚡ Быстрые команды

### Автоматизация
```bash
# Автообновление struct.json при изменениях
llmstruct parse . --use-cache

# Обработка очереди команд
echo '{"commands": [{"action": "parse", "args": ["."]}]}' > data/cli_queue.json
llmstruct interactive . 
# Затем: /queue run
```

### Мониторинг
```bash
# Статус системы
llmstruct interactive . 
# Затем: /status

# Структура проекта
llmstruct interactive .
# Затем: /struct status
```

## 🔧 Конфигурация

Создайте `llmstruct.toml` в корне проекта:
```toml
[cache]
enabled = true
directory = ".llmstruct_cache"
ttl = 3600

[copilot]
enabled = true
context_layers = ["core", "data", "insights"]
auto_refresh = true

[auto_update]
enabled = true
watch_patterns = ["src/**/*.py", "*.json"]
```

## 📊 Примеры использования

### Анализ проекта
```bash
# Полный анализ с генерацией отчёта
llmstruct dogfood --input src/ --output analysis_report.json

# Ревью кода через LLM
llmstruct review --input src/ --mode hybrid --output review_report.json
```

### Copilot работа
```bash
# 1. Инициализация
llmstruct copilot . init

# 2. Интерактивная работа
llmstruct interactive .
# /copilot status
# /view src/main.py  
# /copilot test

# 3. Экспорт для внешних инструментов
llmstruct copilot . export --format json --output copilot_full_context.json
```

## 🎯 Ключевые возможности

- **📁 Автоматический парсинг**: Генерация struct.json из любой кодовой базы
- **🤖 LLM интеграция**: Поддержка Grok, Anthropic, Ollama, гибридный режим
- **💾 Кэширование**: Умное кэширование для ускорения повторных операций
- **🔍 Copilot Pro**: Полная интеграция с GitHub Copilot Pro
- **⚡ CLI автоматизация**: Очереди команд, автообновления, мониторинг
- **🛡️ Валидация данных**: Автоматическая проверка целостности и дубликатов (68.4% эффективность)

## 🚨 Решение проблем

### Частые проблемы
```bash
# Очистка кэша
llmstruct interactive .
# /cache clear

# Пересоздание struct.json
llmstruct parse . --force

# Проверка конфигурации Copilot
llmstruct copilot . status
```

### Логи и отладка
```bash
# Включение подробных логов
export LLMSTRUCT_LOG_LEVEL=DEBUG
llmstruct interactive .
```

---
**💡 Совет**: Начните с `llmstruct interactive .` для изучения всех возможностей системы в интерактивном режиме.
