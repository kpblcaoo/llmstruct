# 🤖 AI DOCUMENTATION

**Назначение**: Структурированная документация для AI помощника  
**Формат**: Максимально эффективный и однозначный для понимания  
**Обновляется**: При каждом значимом изменении архитектуры

---

## 📋 СИСТЕМА ПЛАНИРОВАНИЯ И ЗАДАЧ

### **🔒 УРОВНИ ДОСТУПА:**

#### **1. ЛИЧНОЕ (Михаил) - НЕ для GitHub**
- **Расположение**: `.personal/`
- **Содержимое**: Личные заметки, идеи, черновики
- **Доступ**: Только Михаил
- **Формат**: Markdown, удобно для быстрых записей

#### **2. РУКОВОДИТЕЛЬСКОЕ - НЕ для GitHub**  
- **Расположение**: `docs/management/`
- **Содержимое**: Бизнес-планы, стратегии, управленческие решения
- **Доступ**: Михаил + будущий модуль руководителя
- **Формат**: JSON + Markdown для структурированности

#### **3. КОМАНДНОЕ - ДЛЯ GitHub**
- **Расположение**: `processing_results/github_*`
- **Содержимое**: Issues, Epics, Discussions для команды
- **Доступ**: Публичный через GitHub
- **Формат**: JSON → GitHub sync

---

## 🎯 СВЯЗКА ПЛАНИРОВАНИЯ

### **PIPELINE ПЛАНОВ:**
```
1. DISCOVERY:
   926 items → processing_results/github_epics_*.json (найденные эпики)

2. ROADMAP PLANNING:
   epics_roadmap.json (планы сессий по эпикам)

3. ACTIVE WORK:
   data/sessions/ai_sessions.json (текущие сессии)

4. EXECUTION:
   GitHub Issues/Epics (команда выполняет)
```

### **КЛЮЧЕВЫЕ ФАЙЛЫ:**

**📊 Планирование:**
- `epics_roadmap.json` - Master план сессий по эпикам
- `processing_results/github_epics_*.json` - Найденные эпики 
- `data/sessions/ai_sessions.json` - Активные сессии

**🔒 Личное/Руководительское:**
- `.personal/current_action_plans.md` - Личные планы
- `docs/management/business_roadmap.json` - Бизнес планы
- `docs/management/team_strategy.md` - Управленческие решения

**🚀 Командное (→ GitHub):**
- `processing_results/github_issues_*.json` - Issues для команды
- `processing_results/github_epics_*.json` - Epics для архитектуры
- `processing_results/github_discussions_*.json` - Обсуждения

---

## 🔄 WORKFLOW УПРАВЛЕНИЯ

### **Михаил (Руководитель):**
1. Создаёт планы в `.personal/` и `docs/management/`
2. Принимает окончательные решения
3. Переносит ТОЛЬКО командные задачи в `processing_results/`
4. Синхронизирует с GitHub через sync manager

### **AI Помощник:**
1. Читает ВСЕ уровни для полного контекста
2. Предлагает идеи на основе всей информации  
3. Создаёт ТОЛЬКО в соответствующих папках
4. НЕ копирует личное/руководительское в командное

### **Команда:**
1. Видит ТОЛЬКО GitHub Issues/Epics/Discussions
2. Работает над назначенными задачами
3. Не имеет доступа к личным/бизнес планам

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
llmstruct/
├── .personal/                     # 🔒 ЛИЧНОЕ
│   ├── current_action_plans.md    
│   ├── personal_ideas.json
│   └── team_collaboration_plan.md
│
├── docs/
│   ├── ai/                        # 🤖 AI ДОКУМЕНТАЦИЯ
│   │   ├── README.md             # Этот файл
│   │   ├── system_overview.md    # Обзор системы
│   │   └── workflow_guide.md     # Гайд по workflow
│   │
│   └── management/               # 🔒 РУКОВОДИТЕЛЬСКОЕ  
│       ├── business_roadmap.json
│       ├── team_strategy.md
│       └── revenue_plans.md
│
├── processing_results/           # 🚀 КОМАНДНОЕ → GITHUB
│   ├── github_issues_*.json
│   ├── github_epics_*.json
│   └── github_discussions_*.json
│
├── data/sessions/               # 🔄 АКТИВНАЯ РАБОТА
│   ├── ai_sessions.json
│   ├── current_session.json
│   └── epics_roadmap.json       # ← НОВЫЙ КЛЮЧЕВОЙ ФАЙЛ
│
└── scripts/                     # 🛠️ АВТОМАТИЗАЦИЯ
    ├── github_sync_manager_enhanced.py
    └── epic_roadmap_manager.py  # ← НОВЫЙ СКРИПТ
```

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО

### **ПРАВИЛА БЕЗОПАСНОСТИ:**
1. **НЕ СМЕШИВАТЬ** личное и командное
2. **НЕ ПУБЛИКОВАТЬ** бизнес-планы на GitHub  
3. **ПРИОРИТЕТ** за окончательными решениями Михаила
4. **ТОЛЬКО командные задачи** → GitHub sync

### **ДЛЯ AI ПОМОЩНИКА:**
- Читай ВСЕ для контекста
- Создавай ТОЛЬКО в нужной папке
- Спрашивай при неуверенности в уровне доступа
- Помни: `.personal/` и `docs/management/` = НЕ для команды

---

**🎯 ГОТОВ К СОЗДАНИЮ EPICS_ROADMAP И СИСТЕМЫ УПРАВЛЕНИЯ!** 