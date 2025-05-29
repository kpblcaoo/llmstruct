# 🔄 AI WORKFLOW GUIDE

**Для AI помощника**: Пошаговые инструкции работы с системой планирования

---

## 📚 ОСНОВНЫЕ ПРИНЦИПЫ

### **🔒 БЕЗОПАСНОСТЬ ДАННЫХ:**
1. **НЕ КОПИРОВАТЬ** из `.personal/` в `processing_results/`
2. **НЕ КОПИРОВАТЬ** из `docs/management/` в `processing_results/`
3. **ТОЛЬКО КОМАНДНЫЕ ЗАДАЧИ** попадают в GitHub sync
4. **СПРАШИВАТЬ** Михаила при неуверенности

### **📖 ЧТЕНИЕ КОНТЕКСТА:**
1. **ЧИТАТЬ ВСЁ** для полного понимания
2. **АНАЛИЗИРОВАТЬ** связи между личным и командным
3. **ПРЕДЛАГАТЬ** на основе всей информации
4. **СОЗДАВАТЬ** только в правильных папках

---

## 🎯 WORKFLOW ШАГИ

### **ШАГ 1: ПОНИМАНИЕ ЗАДАЧИ**

**Источники информации:**
```bash
# Личные планы Михаила
.personal/current_action_plans.md
.personal/team_collaboration_plan.md

# Руководительские планы  
docs/management/business_roadmap.json
docs/management/team_strategy.md

# Командные задачи
processing_results/github_*.json
data/sessions/epics_roadmap.json
```

**Вопросы для анализа:**
- Это личная задача или командная?
- Требует ли это GitHub sync?
- Какой уровень доступа нужен?

### **ШАГ 2: ВЫБОР ДЕЙСТВИЯ**

**Сценарии:**

#### **A) ЛИЧНАЯ/РУКОВОДИТЕЛЬСКАЯ ЗАДАЧА:**
```bash
# Создавать в:
.personal/           # Личные заметки
docs/management/     # Бизнес планы
```

#### **B) КОМАНДНАЯ ЗАДАЧА:**
```bash  
# Создавать в:
processing_results/github_issues_*.json     # Issues
processing_results/github_epics_*.json      # Epics  
processing_results/github_discussions_*.json # Discussions

# Затем синхронизировать:
python scripts/github_sync_manager_enhanced.py --live
```

#### **C) PLANNING & ROADMAP:**
```bash
# Работать с:
data/sessions/epics_roadmap.json           # Master план
data/sessions/current_session.json         # Активная сессия

# Управление:
python scripts/epic_roadmap_manager.py overview
python scripts/epic_roadmap_manager.py epic --epic-id epic_1
```

### **ШАГ 3: ВЫПОЛНЕНИЕ**

**Команды для AI помощника:**

#### **📊 Анализ состояния:**
```bash
# Посмотреть roadmap
python scripts/epic_roadmap_manager.py overview

# Детали эпика
python scripts/epic_roadmap_manager.py epic --epic-id epic_1

# Статус GitHub sync
python scripts/github_sync_manager_enhanced.py --categories github_issues
```

#### **🚀 Создание задач:**
```bash
# НЕ СОЗДАВАТЬ напрямую в GitHub!
# ТОЛЬКО через processing_results/*.json

# Затем синхронизировать:
python scripts/github_sync_manager_enhanced.py --live --categories github_issues
```

#### **📝 Обновление планов:**
```bash
# Обновить roadmap
# Редактировать data/sessions/epics_roadmap.json

# Начать сессию
python scripts/epic_roadmap_manager.py start --epic-id epic_1 --session-id SES-E1-001

# Завершить сессию  
python scripts/epic_roadmap_manager.py complete --session-id SES-E1-001
```

---

## 🚫 ЧАСТЫЕ ОШИБКИ

### **НЕЛЬЗЯ:**
1. ❌ Создавать Issues напрямую в GitHub
2. ❌ Копировать бизнес-планы в командные задачи
3. ❌ Публиковать личные заметки Михаила
4. ❌ Работать без чтения полного контекста
5. ❌ Игнорировать систему уровней доступа

### **ПРАВИЛЬНО:**
1. ✅ Читать ВСЕ файлы для контекста
2. ✅ Создавать в processing_results/*.json
3. ✅ Синхронизировать через github_sync_manager
4. ✅ Спрашивать при неуверенности
5. ✅ Следовать workflow шагам

---

## 🔧 ПРИМЕРЫ КОМАНД

### **Анализ текущего состояния:**
```bash
# Обзор всех эпиков
python scripts/epic_roadmap_manager.py overview

# Статус конкретного эпика
python scripts/epic_roadmap_manager.py epic --epic-id epic_1

# Проверка GitHub sync
python scripts/github_sync_manager_enhanced.py --categories github_issues --dry-run
```

### **Начало работы над эпиком:**
```bash
# 1. Выбрать эпик и сессию
python scripts/epic_roadmap_manager.py epic --epic-id epic_1

# 2. Начать сессию
python scripts/epic_roadmap_manager.py start --epic-id epic_1 --session-id SES-E1-001

# 3. Создать ветку (для человека)
# git checkout -b ai/epic-1-session-001-safety-manager

# 4. Работать над задачами
```

### **Синхронизация с GitHub:**
```bash
# Сухой прогон
python scripts/github_sync_manager_enhanced.py --dry-run

# Реальная синхронизация
python scripts/github_sync_manager_enhanced.py --live --categories github_issues

# Синхронизация эпиков
python scripts/github_sync_manager_enhanced.py --live --categories github_epics
```

---

## 📋 ЧЕКЛИСТ ДЛЯ AI

### **Перед каждым ответом:**
- [ ] Прочитал ли я все релевантные файлы?
- [ ] Понимаю ли я уровень доступа задачи?
- [ ] Создаю ли я в правильной папке?
- [ ] Не копирую ли личное в командное?

### **При создании задач:**
- [ ] Это командная задача?
- [ ] Создаю в processing_results/?
- [ ] Планирую GitHub sync?
- [ ] Учитываю связь с эпиками?

### **При работе с планами:**
- [ ] Обновляю epics_roadmap.json?
- [ ] Слежу за зависимостями эпиков?
- [ ] Проверяю current_session.json?
- [ ] Архивирую завершённые сессии?

---

## 🎯 ЦЕЛЬ СИСТЕМЫ

**Обеспечить:**
1. **Безопасность** личных и бизнес данных
2. **Эффективность** командной работы
3. **Прозрачность** планирования и выполнения
4. **Масштабируемость** для будущего модуля руководителя

**Результат:**
- Команда видит только свои задачи
- Михаил контролирует стратегию
- AI помогает на всех уровнях
- Планы выполняются структурированно

---

**🤖 ЗАПОМНИ: Читай всё, создавай правильно, синхронизируй безопасно!** 