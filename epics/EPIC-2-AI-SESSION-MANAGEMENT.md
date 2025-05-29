# EPIC 2: AI SESSION MANAGEMENT

**Статус**: 🆕 NEW  
**Приоритет**: 🔥 HIGH  
**Оценка**: 2 weeks  
**Связь**: EPIC 1 (AI Branch Safety System)

## 🎯 ОПИСАНИЕ

Управление AI сессиями с привязкой к веткам. Каждая сессия/эпик/issue имеет одну ветку, AI знает в какой ветке работает.

## ✅ КРИТЕРИИ ГОТОВНОСТИ

- [ ] Сессии привязываются к веткам
- [ ] Нарушения целостности детектируются  
- [ ] Session recovery работает
- [ ] AI знает контекст текущей сессии

## 📋 ISSUES

### **ISSUE-007: Создать AISessionManager класс**
- **Приоритет**: 🔥 HIGH
- **Оценка**: 2 дня
- **Описание**: Базовый класс для управления AI сессиями
- **Acceptance Criteria**:
  - [ ] Класс `AISessionManager` создан
  - [ ] Методы `start_dogfooding_session()` и `end_session()`
  - [ ] Session state persistence
  - [ ] Session ID generation и tracking

### **ISSUE-008: Реализовать привязку сессия-ветка**
- **Приоритет**: 🔥 HIGH  
- **Оценка**: 3 дня
- **Описание**: One-to-one mapping между AI сессиями и git ветками
- **Acceptance Criteria**:
  - [ ] Session создается только в ai-ветке
  - [ ] Branch name generation из issue/task ID
  - [ ] Проверка уникальности сессии в ветке
  - [ ] Session metadata в git notes/refs

### **ISSUE-009: Добавить проверку целостности сессии**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 2 дня  
- **Описание**: Детекция и recovery от нарушений session integrity
- **Acceptance Criteria**:
  - [ ] `verify_session_integrity()` метод
  - [ ] Детекция branch switching
  - [ ] Recovery mechanisms
  - [ ] Session corruption detection

### **ISSUE-010: Создать команды управления сессиями**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 2 дня
- **Описание**: CLI команды для управления AI сессиями
- **Acceptance Criteria**:
  - [ ] `session start <issue_id>` команда
  - [ ] `session status` и `session list`
  - [ ] `session switch <session_id>` 
  - [ ] `session end` с cleanup

## 🏗️ ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

```python
# core/ai_safety/session_manager.py
class AISessionManager:
    def __init__(self):
        self.current_session = None
        self.session_storage = SessionStorage()
        self.safety_manager = AIBranchSafetyManager()
    
    def start_dogfooding_session(self, issue_id: str, description: str) -> bool
    def end_session(self, session_id: str) -> bool
    def verify_session_integrity(self) -> bool
    def get_session_context(self) -> SessionContext
    def switch_session(self, session_id: str) -> bool
```

## 📊 МЕТРИКИ

- **Session Integrity**: 100% детекция нарушений
- **Session Recovery**: >95% успешных recovery
- **Context Accuracy**: AI знает правильный контекст в 100% случаев
- **Session Overhead**: <2% impact на производительность

## 🔗 ЗАВИСИМОСТИ

- EPIC 1: AI Branch Safety System (ISSUE-001, ISSUE-002)
- Git repository с поддержкой git notes
- Session storage mechanism (файлы/база данных)

## 📝 ЗАМЕТКИ

- Session persistence должна пережить restart
- Graceful handling git operations (merge, rebase, etc.)
- Session metadata не должна конфликтовать с git workflow 