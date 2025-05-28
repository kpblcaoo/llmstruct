# EPIC 1: AI BRANCH SAFETY SYSTEM

**Статус**: 🆕 NEW  
**Приоритет**: 🔥 CRITICAL  
**Оценка**: 3 weeks  
**Связь**: AI-Dogfooding Final Plan

## 🎯 ОПИСАНИЕ

Система строгого контроля AI операций через ветки. AI блокируется если не в ai-ветке, создание веток вручную, одна ветка на сессию/эпик/issue.

## ✅ КРИТЕРИИ ГОТОВНОСТИ

- [ ] AI блокируется без ai-ветки на 100%
- [ ] Whitelist операций работает корректно
- [ ] Все тесты проходят
- [ ] Документация написана

## 📋 ISSUES

### **ISSUE-001: Создать AIBranchSafetyManager класс**
- **Приоритет**: 🔥 HIGH
- **Оценка**: 3 дня
- **Описание**: Базовый класс для контроля AI операций
- **Acceptance Criteria**:
  - [ ] Класс `AIBranchSafetyManager` создан
  - [ ] Методы `verify_ai_session_branch()` и `set_session_branch()` работают
  - [ ] Проверка формата ai-веток (ai/, dogfood/, ai-experiment/)
  - [ ] Unit тесты покрывают основной функционал

### **ISSUE-002: Реализовать проверку ai-веток**
- **Приоритет**: 🔥 HIGH  
- **Оценка**: 2 дня
- **Описание**: Проверка что AI находится в правильной ai-ветке
- **Acceptance Criteria**:
  - [ ] `get_current_git_branch()` получает текущую ветку
  - [ ] Валидация формата ai-веток
  - [ ] Проверка соответствия ветки текущей сессии
  - [ ] Обработка edge cases (detached HEAD, etc.)

### **ISSUE-003: Создать whitelist безопасных операций**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 1 день  
- **Описание**: Список операций разрешенных без ai-ветки
- **Acceptance Criteria**:
  - [ ] `SAFE_OPERATIONS` словарь создан
  - [ ] Read-only операции включены (read_file, list_dir, search)
  - [ ] Анализ и метрики включены
  - [ ] Конфигурируемый whitelist

### **ISSUE-004: Добавить блокировку опасных операций**
- **Приоритет**: 🔥 HIGH
- **Оценка**: 2 дня
- **Описание**: Блокировка операций изменения без ai-ветки
- **Acceptance Criteria**:
  - [ ] `DANGEROUS_OPERATIONS` список создан
  - [ ] Блокировка edit_file, delete_file, run_terminal_cmd
  - [ ] Информативные сообщения об ошибках
  - [ ] Возможность override для emergency cases

### **ISSUE-005: Интегрировать с AI middleware**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 3 дня
- **Описание**: Интеграция safety manager с существующим AI middleware
- **Acceptance Criteria**:
  - [ ] Safety checks в AI middleware pipeline
  - [ ] Graceful degradation при ошибках
  - [ ] Логирование всех safety events
  - [ ] Performance не деградирует >5%

### **ISSUE-006: Написать тесты для safety manager**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 2 дня
- **Описание**: Comprehensive test suite для safety functionality
- **Acceptance Criteria**:
  - [ ] Unit тесты для всех методов
  - [ ] Integration тесты с git
  - [ ] Mock тесты для edge cases
  - [ ] Coverage >95%

## 🏗️ ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

```python
# core/ai_safety/branch_manager.py
class AIBranchSafetyManager:
    def __init__(self):
        self.session_branch = None
        self.whitelist_operations = SAFE_OPERATIONS
        self.blocked_operations = DANGEROUS_OPERATIONS
    
    def verify_ai_session_branch(self) -> bool
    def set_session_branch(self, branch_name: str)
    def check_operation_permission(self, operation: str) -> Tuple[bool, str]
    def get_current_git_branch(self) -> str
```

## 📊 МЕТРИКИ

- **Safety Compliance**: 100% блокировка опасных операций без ai-ветки
- **False Positive Rate**: <5% ложных блокировок safe операций
- **Performance Impact**: <5% overhead на AI операции
- **Test Coverage**: >95% для safety критического кода

## 🔗 ЗАВИСИМОСТИ

- Git repository должен быть инициализирован
- Python 3.8+ для typing support
- Существующий AI middleware framework

## 📝 ЗАМЕТКИ

- Начинаем с conservative whitelist, расширяем по мере тестирования
- Emergency override mechanism для критических ситуаций
- Comprehensive logging для audit trail 