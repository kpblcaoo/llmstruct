# 🧠 Cursor AI Workflow Integration Package

## 📋 Что это такое?

Полная интеграция AI-системы самоанализа с Cursor IDE для проекта `llmstruct`. Включает:

- **AI Self-Awareness**: Система знает о своих 272 модулях, 1857 функциях, 183 классах
- **Workflow Management**: Контекстные теги `[code]`, `[debug]`, `[discuss]`, `[meta]`, `[test]`, `[docs]`
- **Session Management**: 13 доступных сессий с эпиками и переключением контекста
- **VS Code Integration**: 17 задач в Command Palette для управления AI системой
- **Smart Context**: Автоматическое определение текущей сессии, эпика, режима workspace

## 🚀 Быстрая установка

### 1. Скопировать файлы в проект

```bash
# Из папки cursor_workflow_integration скопировать:
cp files/auto_init_ai_system.py /path/to/your/project/
cp files/.cursorrules /path/to/your/project/
cp -r .vscode/ /path/to/your/project/
```

### 2. Автоматическая установка (рекомендуется)

```bash
# Запустить установочный скрипт
python scripts/install_ai_integration.py
```

### 3. Проверить установку

```bash
# Проверить что AI система работает
python -c "from auto_init_ai_system import get_ai_status; print(get_ai_status())"

# Проверить workflow статус
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"
```

## 🎮 Как использовать

### В Cursor IDE

1. **Открыть Command Palette**: `Ctrl+Shift+P` (Linux/Windows) или `Cmd+Shift+P` (Mac)

2. **Доступные команды**:
   - `🧠 Initialize AI System` - автозапуск системы
   - `🔍 AI Status Check` - полный статус
   - `🔎 Search AI Capabilities` - поиск функций
   - `🎭 Workflow Status` - статус сессий и эпиков
   - `⚙️ Switch Workspace Mode` - переключение режимов
   - `🔄 Switch to Session` - переключение сессий
   - `🚀 Create Epic Session` - создание новых сессий

### В терминале

```bash
# Статус AI системы
python -c "from auto_init_ai_system import get_ai_status; print(get_ai_status())"

# Поиск возможностей
python -c "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('context'))"

# Переключить режим workspace
python -c "from auto_init_ai_system import switch_workspace_mode; switch_workspace_mode('[code][debug]')"

# Управление сессиями
python -c "from auto_init_ai_system import get_available_sessions; print(get_available_sessions())"
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-001'))"

# Управление эпиками
python scripts/epic_roadmap_manager.py overview
python scripts/session_cli.py current
```

## 🎯 Workflow режимы

### Базовые теги:
- `[discuss]` - Планирование, обсуждение, без изменений файлов
- `[meta]` - Работа над механизмами LLM взаимодействия
- `[code]` - Чистая реализация/программирование  
- `[debug]` - Отладка, исправление проблем
- `[docs]` - Фокус на документации
- `[test]` - Тестирование, валидация

### Умные комбинации:
- `[code][debug]` - Реализация + отладка
- `[discuss][meta]` - Планирование LLM улучшений
- `[docs][meta]` - Документирование AI паттернов

## 📊 Session Management

### Доступные сессии:
- **SES-001**: General Development Session
- **Epic Sessions**: 12 специализированных сессий по 4 эпикам:
  - Epic 1: AI Branch Safety (3 сессии)
  - Epic 2: Context Orchestration (3 сессии)  
  - Epic 3: Advanced Prompting (3 сессии)
  - Epic 4: Production Deployment (3 сессии)

### Переключение сессий:
```bash
# Список всех сессий
python -c "from auto_init_ai_system import get_available_sessions; print(get_available_sessions())"

# Переключиться на сессию
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-001'))"

# Создать новую эпик-сессию
python -c "from auto_init_ai_system import create_epic_session; print(create_epic_session('epic_1_ai_branch_safety'))"
```

## 🔧 Требования

### Обязательные компоненты:
- Python 3.8+
- Виртуальное окружение в `./venv/`
- Модули проекта:
  - `src/llmstruct/ai_self_awareness.py`
  - `src/llmstruct/workspace.py`
  - `scripts/session_cli.py`
  - `scripts/epic_roadmap_manager.py`

### Структура данных:
- `struct.json` - анализ модулей проекта
- `data/sessions/` - управление сессиями
- `ai_system.log` - логирование AI операций

## 📁 Структура пакета

```
cursor_workflow_integration/
├── README.md                    # Эта инструкция
├── files/                       # Основные файлы
│   ├── auto_init_ai_system.py  # Главный модуль интеграции
│   └── .cursorrules            # Конфигурация Cursor
├── .vscode/                     # VS Code конфигурация
│   ├── tasks.json              # 17 AI задач
│   └── settings.json           # Настройки (опционально)
├── scripts/                     # Установочные скрипты
│   └── install_ai_integration.py
└── docs/                        # Документация
    ├── CURSOR_AI_EXAMPLES.md
    ├── SESSION_MANAGEMENT_GUIDE.md
    ├── WORKFLOW_CURSOR_INTEGRATION_REPORT.md
    └── SESSION_INTEGRATION_REPORT.md
```

## 🎯 Примеры использования

### Начало работы с новой задачей:
1. `Ctrl+Shift+P` → `🎭 Workflow Status` - проверить текущий контекст
2. `Ctrl+Shift+P` → `⚙️ Switch Workspace Mode` → выбрать `[code][debug]`
3. `Ctrl+Shift+P` → `🔄 Switch to Session` → выбрать подходящую сессию
4. Начать работу с полным контекстом AI системы

### Поиск функций в проекте:
1. `Ctrl+Shift+P` → `🔎 Search AI Capabilities`
2. Ввести поисковый запрос (например, "context")
3. Получить список из 272 модулей с релевантными результатами

### Отладка проблем:
1. Переключиться в режим `[debug]`
2. Использовать AI знания о 1857 функциях для анализа
3. Логировать все действия в `ai_system.log`

## 🔍 Troubleshooting

### Проблема: AI система не инициализируется
```bash
# Проверить виртуальное окружение
source ./venv/bin/activate

# Проверить наличие модулей
python -c "import sys; print(sys.path)"
python -c "from llmstruct.ai_self_awareness import SystemCapabilityDiscovery"
```

### Проблема: VS Code задачи не видны
1. Убедиться что `.vscode/tasks.json` скопирован
2. Перезапустить Cursor/VS Code
3. Проверить `Ctrl+Shift+P` → "Tasks: Run Task"

### Проблема: Сессии не переключаются
```bash
# Проверить структуру данных
ls -la data/sessions/
python scripts/session_cli.py current
```

## 📞 Поддержка

Все файлы протестированы и готовы к использованию. При проблемах:

1. Проверить логи в `ai_system.log`
2. Запустить диагностику: `python -c "from auto_init_ai_system import get_ai_status; print(get_ai_status())"`
3. Изучить документацию в папке `docs/`

## 🎉 Результат

После установки вы получите:
- **Умный AI ассистент** который знает о всех возможностях проекта
- **Контекстное переключение** между режимами работы
- **Управление сессиями** для фокусированной работы
- **17 команд в Cursor** для быстрого доступа к AI функциям
- **Автоматическое логирование** всех AI операций

**Добро пожаловать в AI-enhanced development environment!** 🚀 