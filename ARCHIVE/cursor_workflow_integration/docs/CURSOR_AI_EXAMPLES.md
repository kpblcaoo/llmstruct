# 🎯 Cursor AI Integration Examples

Примеры использования интегрированной AI workflow системы в Cursor.

## 🚀 Quick Start Commands

### **Базовые команды AI системы:**
```bash
# Полный статус системы включая workflow
python -c "from auto_init_ai_system import get_ai_status; print(get_ai_status())"

# Только workflow статус
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"

# Поиск функций/модулей (с кешированием!)
python -c "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('copilot'))"
```

### **Workspace Mode Management:**
```bash
# Переключить в планирование
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[discuss][meta]'))"

# Переключить в разработку + отладку
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[code][debug]'))"

# Переключить в документацию
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[docs]'))"
```

### **Epic & Session Management:**
```bash
# Обзор всех эпиков
python scripts/epic_roadmap_manager.py overview

# Детали конкретного эпика
python scripts/epic_roadmap_manager.py epic --epic-id epic_1_ai_branch_safety

# Начать сессию
python scripts/epic_roadmap_manager.py start --epic-id epic_1_ai_branch_safety --session-id SES-E1-001
```

## 🎭 Context Tags Examples

### **При планировании и обсуждении:**
- **Контекст:** `[discuss]` или `[discuss][meta]`
- **Пример запроса:** "Покажи общую архитектуру проекта"
- **VS Code Task:** `🎭 Workflow Status`

### **При программировании:**
- **Контекст:** `[code]` или `[code][debug]`  
- **Пример запроса:** "Реализуй функцию для парсинга JSON"
- **VS Code Task:** `⚙️ Switch Workspace Mode` → выбрать `[code]`

### **При отладке:**
- **Контекст:** `[debug]` или `[code][debug]`
- **Пример запроса:** "Найди причину ошибки в функции X"
- **VS Code Task:** `⚙️ Switch Workspace Mode` → выбрать `[code][debug]`

### **При документации:**
- **Контекст:** `[docs]` или `[docs][meta]`
- **Пример запроса:** "Создай документацию для API"
- **VS Code Task:** `⚙️ Switch Workspace Mode` → выбрать `[docs]`

## 🔍 Search Examples

### **Поиск функций:**
```bash
# Поиск функций работы с JSON
python -c "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('json'))"

# Поиск функций контекста
python -c "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('context'))"

# Поиск CLI функций
python -c "from auto_init_ai_system import search_ai_capabilities; print(search_ai_capabilities('cli'))"
```

### **VS Code Tasks с интерактивностью:**
1. Открыть Command Palette (`Ctrl+Shift+P`)
2. Выбрать `🔎 Search AI Capabilities`
3. Ввести поисковый запрос в интерактивном диалоге
4. Получить результаты без блокировки

## 📊 Epic Workflow Examples

### **Начать работу над эпиком:**
```bash
# 1. Посмотреть доступные эпики
python scripts/epic_roadmap_manager.py overview

# 2. Детали эпика
python scripts/epic_roadmap_manager.py epic --epic-id epic_2_session_management

# 3. Начать сессию
python scripts/epic_roadmap_manager.py start --epic-id epic_2 --session-id SES-E2-001

# 4. Переключить режим под задачу
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[code]'))"
```

### **VS Code Tasks для Epic Management:**
1. `📊 Epic Roadmap Overview` - обзор всех эпиков
2. `🎯 Epic Details` - выбрать эпик из списка для детального просмотра
3. `🎭 Workflow Status` - текущий статус workflow

## 🤖 AI Context Awareness

### **Система автоматически понимает:**
- ✅ Текущий workspace mode: `[code]`, `[debug]`, `[discuss]`
- ✅ Активную сессию: `SES-001`
- ✅ Текущую ветку: `feature/json-script-abstraction`
- ✅ Активные эпики: из `epic_roadmap.json`
- ✅ Разрешения и ограничения по режиму

### **Примеры контекстно-осведомленных запросов:**
```
"Покажи статус AI-системы" → 
   Ответ включает workflow статус

"Найди функции для работы с сессиями" → 
   Учитывает текущую сессию SES-001

"Переключи режим на отладку" →
   Использует WorkspaceStateManager автоматически
```

## 🔧 VS Code Integration Examples

### **Доступные Tasks в Command Palette:**
- `🧠 Initialize AI System` - автоинициализация при открытии
- `🔍 AI Status Check` - полный статус системы  
- `🔎 Search AI Capabilities` - интерактивный поиск
- `🎭 Workflow Status` - статус workflow и сессий
- `⚙️ Switch Workspace Mode` - интерактивное переключение режимов
- `📊 Epic Roadmap Overview` - обзор всех эпиков
- `🎯 Epic Details` - детали выбранного эпика

### **Automatic Features:**
- ✅ **Auto-initialization** при открытии проекта
- ✅ **Smart caching** для быстрого поиска
- ✅ **Logging** всех действий в `ai_system.log`
- ✅ **Context preservation** между командами
- ✅ **Interactive inputs** вместо блокирующих prompt()

## 📈 Performance Features

### **Кеширование (Grok optimization):**
- `struct.json` кешируется в `data/ai_self_awareness/search_cache.json`
- Автоматическая проверка времени изменения файлов
- Логирование cache hits/misses

### **Логирование (Grok suggestion):**
- Все действия записываются в `ai_system.log`
- Уровни: INFO, WARNING, ERROR
- Помогает в отладке крупного проекта

## 🎯 Recommended Workflow

### **Начало работы:**
1. Открыть проект в Cursor → автоинициализация AI
2. `🎭 Workflow Status` - посмотреть текущий статус
3. `📊 Epic Roadmap Overview` - выбрать задачу
4. `⚙️ Switch Workspace Mode` - установить подходящий режим
5. Работать с контекстно-осведомленным AI

### **Во время разработки:**
- Использовать `🔎 Search AI Capabilities` для поиска функций
- Переключать режимы по мере необходимости
- AI автоматически учитывает текущий контекст

### **Завершение сессии:**
- Проверить логи в `ai_system.log`
- Обновить статус эпика если нужно
- AI сохраняет состояние автоматически

---

## 💡 Tips & Tricks

1. **Логи помогают:** Всегда проверяй `ai_system.log` при проблемах
2. **Кеш ускоряет:** Поиск работает быстрее благодаря кешированию
3. **Контекст важен:** AI работает лучше зная текущий workspace mode
4. **Интерактивность:** VS Code Tasks не блокируют, используй их
5. **Workflow integration:** Система знает о сессиях и эпиках автоматически 