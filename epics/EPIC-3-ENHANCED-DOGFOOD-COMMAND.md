# EPIC 3: ENHANCED DOGFOOD COMMAND

**Статус**: 🆕 NEW  
**Приоритет**: 🔥 HIGH  
**Оценка**: 2 weeks  
**Связь**: EPIC 1 (Safety), EPIC 2 (Sessions), TSK-095

## 🎯 ОПИСАНИЕ

Безопасная команда AI-dogfooding с проверками безопасности и session management. Реализация TSK-095 с enhanced safety features.

## ✅ КРИТЕРИИ ГОТОВНОСТИ

- [ ] `dogfood` команда работает безопасно
- [ ] Интеграция с safety system
- [ ] Метрики собираются
- [ ] Session management интегрирован

## 📋 ISSUES

### **ISSUE-011: Реализовать базовую dogfood команду (TSK-095)**
- **Приоритет**: 🔥 CRITICAL
- **Оценка**: 3 дня
- **Описание**: Базовая команда AI-dogfooding из TSK-095
- **Acceptance Criteria**:
  - [ ] CLI команда `dogfood` создана
  - [ ] Базовый AI workflow запускается
  - [ ] Интеграция с существующим AI bridge
  - [ ] Обработка аргументов и параметров

### **ISSUE-012: Интегрировать safety проверки**
- **Приоритет**: 🔥 HIGH  
- **Оценка**: 2 дня
- **Описание**: Интеграция с AI Branch Safety System
- **Acceptance Criteria**:
  - [ ] Pre-flight safety checks
  - [ ] Блокировка без ai-ветки
  - [ ] Информативные error messages
  - [ ] Safety override для emergency

### **ISSUE-013: Добавить session management**
- **Приоритет**: 🔥 HIGH
- **Оценка**: 2 дня  
- **Описание**: Интеграция с AI Session Management
- **Acceptance Criteria**:
  - [ ] Автоматическое создание/восстановление сессии
  - [ ] Session context в AI operations
  - [ ] Session cleanup при завершении
  - [ ] Multi-session support

### **ISSUE-014: Создать enhanced middleware wrapper**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 3 дня
- **Описание**: Middleware для обертки AI операций с safety
- **Acceptance Criteria**:
  - [ ] `SafetyEnhancedMiddleware` класс
  - [ ] Operation interception и validation
  - [ ] Graceful degradation
  - [ ] Performance monitoring

### **ISSUE-015: Добавить logging и метрики**
- **Приоритет**: 🟡 MEDIUM
- **Оценка**: 1 день
- **Описание**: Comprehensive logging и metrics collection
- **Acceptance Criteria**:
  - [ ] Structured logging всех операций
  - [ ] Safety events tracking
  - [ ] Performance метрики
  - [ ] Dashboard для monitoring

## 🏗️ ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

```python
# core/commands/dogfood_command.py
def dogfood_command(args):
    """Enhanced dogfood command with safety"""
    
    # Safety pre-checks
    safety_manager = AIBranchSafetyManager()
    if not safety_manager.verify_ai_session_branch():
        return safety_block_with_instructions(args)
    
    # Session management
    session_manager = AISessionManager()
    session = session_manager.get_or_create_session(args)
    
    # Enhanced middleware
    middleware = SafetyEnhancedMiddleware(safety_manager, session)
    return middleware.run_dogfooding(args)

# core/middleware/safety_enhanced.py  
class SafetyEnhancedMiddleware:
    def __init__(self, safety_manager, session_manager):
        self.safety = safety_manager
        self.session = session_manager
        self.metrics = MetricsCollector()
    
    def run_dogfooding(self, args) -> DogfoodResult
    def intercept_operation(self, operation: str) -> bool
    def collect_metrics(self, operation: str, result: Any)
```

## 📊 МЕТРИКИ

- **Safety Compliance**: 100% операций проходят safety checks
- **Session Success Rate**: >98% успешных сессий  
- **Command Reliability**: >99% успешных запусков
- **Performance Overhead**: <10% от baseline

## 🔗 ЗАВИСИМОСТИ

- EPIC 1: AI Branch Safety System (все issues)
- EPIC 2: AI Session Management (ISSUE-007, ISSUE-008)
- TSK-095: Base dogfood command requirements
- Существующий AI bridge и middleware

## 📝 ЗАМЕТКИ

- Backward compatibility с существующими AI workflows
- Progressive enhancement - добавляем safety поверх существующего
- Emergency bypass mechanism для критических случаев
- Extensive testing в AI-ветках перед production 