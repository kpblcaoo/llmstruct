# 🔄 Session Management Guide

Полное руководство по работе с сессиями в llmstruct с интеграцией в Cursor.

## 🎯 Концепция сессий

**Сессия** = одна ветка + контекст + метаданные + журнал работ  
**Epic Session** = сессия в рамках эпика с планируемыми задачами  
**Workflow Context** = текущий режим работы + активная сессия + workspace mode

## 📋 Структура системы сессий

### **Основные файлы:**
- `data/sessions/current_session.json` - текущая активная сессия
- `data/sessions/ai_sessions.json` - журнал всех AI-сессий
- `data/sessions/worklog.json` - ход работ по текущей сессии
- `data/sessions/epics_roadmap.json` - эпики с запланированными сессиями

### **Типы сессий:**
1. **Regular Sessions** - обычные рабочие сессии
2. **Epic Sessions** - сессии в рамках эпиков (из roadmap)
3. **Ad-hoc Sessions** - быстрые сессии для фиксов

## 🚀 Quick Start

### **1. Посмотреть доступные сессии:**
```bash
# Все сессии (включая epic sessions)
python -c "from auto_init_ai_system import get_available_sessions; print(get_available_sessions())"

# Только epic sessions с статусами
python -c "from auto_init_ai_system import get_epic_sessions_status; print(get_epic_sessions_status())"

# Через session CLI
python scripts/session_cli.py list
```

### **2. Текущая сессия:**
```bash
# Детали текущей сессии
python scripts/session_cli.py current

# Workflow статус с сессией
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"
```

### **3. Переключение между сессиями:**
```bash
# Переключиться на существующую сессию
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-001'))"

# Через session CLI
python scripts/session_cli.py switch SES-001

# Автодетект по ветке
python scripts/session_cli.py switch
```

## 🎯 Работа с Epic Sessions

### **Создание epic session:**
```bash
# Автогенерация session ID
python -c "from auto_init_ai_system import create_epic_session; print(create_epic_session('epic_1_ai_branch_safety'))"

# С конкретным session ID  
python -c "from auto_init_ai_system import create_epic_session; print(create_epic_session('epic_1_ai_branch_safety', 'SES-E1-001'))"

# Через epic manager
python scripts/epic_roadmap_manager.py start --epic-id epic_1_ai_branch_safety --session-id SES-E1-001
```

### **Мониторинг epic sessions:**
```bash
# Статус всех эпиков и их сессий
python scripts/epic_roadmap_manager.py overview

# Детали конкретного эпика
python scripts/epic_roadmap_manager.py epic --epic-id epic_2_session_management

# Статус epic sessions в кратком формате
python -c "from auto_init_ai_system import get_epic_sessions_status; print(get_epic_sessions_status())"
```

## 📝 Логирование событий

### **Ручное логирование:**
```bash
# Добавить событие в worklog
python scripts/session_cli.py log "Started implementing AIBranchSafetyManager"

# Логирование через VS Code Task: 📝 Log Session Event
```

### **Автоматическое логирование:**
- Переключение сессий автоматически логируется
- Создание epic sessions логируется  
- Изменения workspace mode логируются

### **Просмотр журнала:**
```bash
# Последние 10 записей
python scripts/session_cli.py worklog

# Последние 20 записей  
python scripts/session_cli.py worklog 20
```

## 🎭 Интеграция с Workspace

### **Синхронизация режимов:**
```bash
# Переключить workspace mode и залогировать
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[code][debug]'))"

# Режим автоматически адаптируется к типу сессии:
# - Epic sessions → соответствующий режим ([code], [debug], etc.)
# - Regular sessions → [discuss] по умолчанию
```

### **Контекстная осведомленность:**
```bash
# AI знает:
# ✅ Текущую сессию: SES-001
# ✅ Активный эпик: epic_1_ai_branch_safety
# ✅ Workspace mode: [code][debug]  
# ✅ Ветку: feature/json-script-abstraction
# ✅ Журнал работ: последние действия
```

## 🔧 VS Code Integration

### **Доступные Tasks в Command Palette:**

#### **Основные команды:**
- `🔄 List All Sessions` - список всех сессий
- `🎯 Epic Sessions Status` - статус epic sessions
- `📋 Current Session Details` - детали текущей сессии
- `🔧 Session Management Help` - справка

#### **Переключение и создание:**
- `🔄 Switch to Session` - интерактивное переключение
- `🚀 Create Epic Session` - создание с выбором эпика
- `📝 Log Session Event` - интерактивное логирование

#### **Мониторинг:**
- `📄 Session Worklog` - журнал работ
- `🎭 Workflow Status` - полный статус workflow + сессии

## 💡 Recommended Workflows

### **Workflow 1: Начать работу над эпиком**
```bash
# 1. Посмотреть доступные эпики
python scripts/epic_roadmap_manager.py overview

# 2. Создать сессию для эпика  
python -c "from auto_init_ai_system import create_epic_session; print(create_epic_session('epic_1_ai_branch_safety'))"

# 3. Переключить workspace mode
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[code]'))"

# 4. Начать работу и логировать
python scripts/session_cli.py log "Started Epic 1: AIBranchSafetyManager implementation"
```

### **Workflow 2: Переключиться между задачами**
```bash
# 1. Посмотреть доступные сессии
python -c "from auto_init_ai_system import get_available_sessions; print(get_available_sessions())"

# 2. Переключиться на нужную
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-E2-001'))"

# 3. Контекст автоматически обновляется
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"
```

### **Workflow 3: Завершить сессию**
```bash
# 1. Залогировать результаты
python scripts/session_cli.py log "Completed AIBranchSafetyManager core implementation"

# 2. Переключиться на следующую сессию или main
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-E1-002'))"

# 3. Обновить статус эпика (если нужно)
python scripts/epic_roadmap_manager.py complete --session-id SES-E1-001
```

## 🔍 Поиск и фильтрация

### **Поиск сессий по критериям:**
```bash
# По статусу (в JSON файлах)
grep -r '"status": "active"' data/sessions/

# По эпику  
grep -r '"epic_id": "epic_1"' data/sessions/

# По автору
grep -r '"author": "@kpblcaoo"' data/sessions/
```

## 📊 Диагностика и отладка

### **Проверка целостности:**
```bash
# Валидация сессионных файлов
python validate_sessions.py

# Проверка синхронизации с git ветками
python scripts/session_cli.py switch  # Автодетект по ветке
```

### **Логи системы:**
```bash
# Все действия записываются в ai_system.log
tail -f ai_system.log | grep -i session

# Поиск конкретной сессии в логах
grep "SES-E1-001" ai_system.log
```

## 🎯 Advanced Features

### **Elastic Session Workflow (planned):**
```bash
# Концепция: /go task TSK-XXX → работа в фокусированной сессии → /back с резюме
# Статус: Available via epic_roadmap_manager.py и session_cli.py
```

### **Session Recovery:**
```bash
# Восстановление потерянной сессии по ветке
python scripts/session_cli.py switch  # Автодетект

# Восстановление из worklog
python scripts/session_cli.py worklog | tail -n 20
```

### **Cross-Project Sessions (future):**
```bash
# Планируется: работа с сессиями между проектами
# Через install_ai_integration.py
```

---

## 🎉 Summary

**Реализованная система сессий обеспечивает:**

✅ **Seamless переключение** между задачами и эпиками  
✅ **Automatic context preservation** между сессиями  
✅ **Integration** с workflow system и workspace modes  
✅ **Comprehensive logging** всех действий  
✅ **VS Code integration** с интерактивными commands  
✅ **Epic-based planning** с roadmap integration  

**Результат:** Эффективная работа с множественными задачами без потери контекста. 