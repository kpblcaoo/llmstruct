# AI-DOGFOODING FINAL IMPLEMENTATION PLAN

**Дата**: 2025-05-28  
**Статус**: УТВЕРЖДЕН К РЕАЛИЗАЦИИ  
**Основание**: Завершенное планирование с ответами на все критические вопросы

---

## 🎯 УТВЕРЖДЕННАЯ АРХИТЕКТУРА

### **CORE DECISIONS:**

✅ **A: STRICT AI-BRANCH SAFETY**
- AI **блокируется** если не в ai-ветке
- Создание веток **вручную** 
- **Одна ветка на сессию/эпик/issue**
- AI **знает** в какой ветке работает

✅ **B: WHITELIST ОПЕРАЦИЙ**
- Только операции из whitelist разрешены без ai-ветки
- Все остальные блокируются с требованием ai-ветки

✅ **C: RISK-BASED МЕТОДОЛОГИЯ**
- Быстро делаем безопасные части
- Медленно и осторожно опасные

✅ **D: SAFETY-FIRST ПОДХОД**
- Начинаем с AI Branch Safety Manager
- Добавляем базовые проверки
- Только потом функциональность

---

## 🏗️ ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

### **1. AI BRANCH SAFETY MANAGER**

```python
class AIBranchSafetyManager:
    """Строгий контроль AI операций через ветки"""
    
    def __init__(self):
        self.session_branch = None  # Текущая ai-ветка сессии
        self.whitelist_operations = {
            "read_file", "list_dir", "codebase_search", 
            "grep_search", "file_search"
        }
        self.blocked_operations = {
            "edit_file", "delete_file", "run_terminal_cmd"
        }
    
    def verify_ai_session_branch(self) -> bool:
        """Проверить что AI в правильной ai-ветке"""
        current_branch = self.get_current_git_branch()
        
        # Проверка формата ai-ветки
        if not current_branch.startswith(('ai/', 'dogfood/', 'ai-experiment/')):
            return False
            
        # Проверка что это ветка текущей сессии
        if self.session_branch and current_branch != self.session_branch:
            return False
            
        return True
    
    def set_session_branch(self, branch_name: str):
        """Установить ветку для текущей AI сессии"""
        if not branch_name.startswith(('ai/', 'dogfood/', 'ai-experiment/')):
            raise ValueError(f"Invalid AI branch format: {branch_name}")
        self.session_branch = branch_name
    
    def check_operation_permission(self, operation: str) -> Tuple[bool, str]:
        """Проверить разрешена ли операция"""
        
        # Операции из whitelist всегда разрешены
        if operation in self.whitelist_operations:
            return True, "Whitelisted operation"
        
        # Опасные операции требуют ai-ветку
        if operation in self.blocked_operations:
            if self.verify_ai_session_branch():
                return True, f"Dangerous operation allowed in AI branch: {self.session_branch}"
            else:
                return False, f"Operation '{operation}' requires AI branch! Current: {self.get_current_git_branch()}"
        
        # Неизвестные операции по умолчанию блокируются
        return False, f"Unknown operation '{operation}' - not in whitelist"
```

### **2. AI SESSION MANAGER**

```python
class AISessionManager:
    """Управление AI сессиями с привязкой к веткам"""
    
    def start_dogfooding_session(self, issue_id: str, description: str):
        """Начать сессию AI-dogfooding"""
        
        # Предложить создание ai-ветки
        branch_name = f"ai/{issue_id}-{self.safe_description(description)}"
        
        print(f"🚨 AI-DOGFOODING REQUIRES AI BRANCH!")
        print(f"Suggested branch: {branch_name}")
        print(f"Create branch manually:")
        print(f"  git checkout -b {branch_name}")
        print(f"Then restart dogfooding session.")
        
        return False  # Блокируем до создания ветки
    
    def verify_session_integrity(self):
        """Проверить целостность AI сессии"""
        safety = AIBranchSafetyManager()
        
        if not safety.verify_ai_session_branch():
            raise AISessionError(
                "AI session integrity violation! "
                f"Expected AI branch, found: {safety.get_current_git_branch()}"
            )
```

### **3. ENHANCED DOGFOOD COMMAND**

```python
def dogfood_command(args):
    """Безопасная команда AI-dogfooding"""
    
    session_manager = AISessionManager()
    safety_manager = AIBranchSafetyManager()
    
    # Проверка AI-ветки ПЕРЕД началом
    if not safety_manager.verify_ai_session_branch():
        print("❌ AI-DOGFOODING BLOCKED!")
        print("Current branch:", safety_manager.get_current_git_branch())
        print("Required: AI branch (ai/*, dogfood/*, ai-experiment/*)")
        print("\nCreate AI branch first:")
        print(f"  git checkout -b ai/{args.task_id or 'dogfood'}-{datetime.now().strftime('%Y%m%d')}")
        return False
    
    # Установка ветки сессии
    current_branch = safety_manager.get_current_git_branch()
    safety_manager.set_session_branch(current_branch)
    
    print(f"✅ AI-DOGFOODING ACTIVE in branch: {current_branch}")
    
    # Запуск с safety middleware
    enhanced_middleware = SafetyEnhancedMiddleware(safety_manager)
    return enhanced_middleware.run_dogfooding(args)
```

---

## 🛡️ SAFETY WHITELIST

### **РАЗРЕШЕННЫЕ БЕЗ AI-ВЕТКИ:**
```python
SAFE_OPERATIONS = {
    # Read-only операции
    "read_file": "Чтение файлов",
    "list_dir": "Просмотр директорий", 
    "codebase_search": "Семантический поиск",
    "grep_search": "Текстовый поиск",
    "file_search": "Поиск файлов",
    
    # Анализ и метрики
    "analyze_codebase": "Анализ кода",
    "get_metrics": "Получение метрик",
    "check_status": "Проверка статуса"
}
```

### **ТРЕБУЮЩИЕ AI-ВЕТКУ:**
```python
DANGEROUS_OPERATIONS = {
    # Изменение файлов
    "edit_file": "Редактирование файлов",
    "delete_file": "Удаление файлов",
    "create_file": "Создание файлов",
    
    # Выполнение команд
    "run_terminal_cmd": "Выполнение команд",
    "git_operations": "Git операции",
    
    # Изменение конфигурации
    "update_config": "Изменение конфигов",
    "modify_dependencies": "Изменение зависимостей"
}
```

---

## 📋 ЭПИКИ И ЗАДАЧИ

### **EPIC 1: AI BRANCH SAFETY SYSTEM**
**Описание**: Система строгого контроля AI операций через ветки

**Issues:**
- [ ] **ISSUE-001**: Создать AIBranchSafetyManager класс
- [ ] **ISSUE-002**: Реализовать проверку ai-веток
- [ ] **ISSUE-003**: Создать whitelist безопасных операций  
- [ ] **ISSUE-004**: Добавить блокировку опасных операций
- [ ] **ISSUE-005**: Интегрировать с AI middleware
- [ ] **ISSUE-006**: Написать тесты для safety manager

### **EPIC 2: AI SESSION MANAGEMENT**
**Описание**: Управление AI сессиями с привязкой к веткам

**Issues:**
- [ ] **ISSUE-007**: Создать AISessionManager класс
- [ ] **ISSUE-008**: Реализовать привязку сессия-ветка
- [ ] **ISSUE-009**: Добавить проверку целостности сессии
- [ ] **ISSUE-010**: Создать команды управления сессиями

### **EPIC 3: ENHANCED DOGFOOD COMMAND**
**Описание**: Безопасная команда AI-dogfooding с проверками

**Issues:**
- [ ] **ISSUE-011**: Реализовать базовую dogfood команду (TSK-095)
- [ ] **ISSUE-012**: Интегрировать safety проверки
- [ ] **ISSUE-013**: Добавить session management
- [ ] **ISSUE-014**: Создать enhanced middleware wrapper
- [ ] **ISSUE-015**: Добавить logging и метрики

### **EPIC 4: RISK-BASED DEVELOPMENT WORKFLOW**
**Описание**: Методология быстрой разработки безопасных частей

**Issues:**
- [ ] **ISSUE-016**: Создать risk assessment framework
- [ ] **ISSUE-017**: Реализовать быстрые итерации для safe операций
- [ ] **ISSUE-018**: Добавить controlled rollout для dangerous операций
- [ ] **ISSUE-019**: Создать automated testing для safety критической функциональности

---

## ⚡ РИСК-ОРИЕНТИРОВАННАЯ МЕТОДОЛОГИЯ

### **БЕЗОПАСНЫЕ ЧАСТИ (быстро):**
- ✅ Read-only анализ кода
- ✅ Метрики и статистика  
- ✅ Поиск и навигация
- ✅ Генерация отчетов

### **ОПАСНЫЕ ЧАСТИ (медленно):**
- 🚨 Изменение файлов
- 🚨 Выполнение команд
- 🚨 Git операции
- 🚨 Изменение конфигурации

### **ПОЭТАПНОЕ ВНЕДРЕНИЕ:**
```bash
Week 1: Safety Manager + Read-only догфудинг
Week 2: Whitelist операций + базовые проверки  
Week 3: AI-ветки + session management
Week 4: Полная integration + testing
```

---

## 🎯 КРИТЕРИИ ГОТОВНОСТИ

### **EPIC 1 ГОТОВ КОГДА:**
- [ ] AI блокируется без ai-ветки на 100%
- [ ] Whitelist операций работает корректно
- [ ] Все тесты проходят
- [ ] Документация написана

### **EPIC 2 ГОТОВ КОГДА:**
- [ ] Сессии привязываются к веткам
- [ ] Нарушения целостности детектируются  
- [ ] Session recovery работает

### **EPIC 3 ГОТОВ КОГДА:**
- [ ] `dogfood` команда работает безопасно
- [ ] Интеграция с safety system
- [ ] Метрики собираются

### **EPIC 4 ГОТОВ КОГДА:**
- [ ] Risk assessment автоматизирован
- [ ] Быстрые итерации для safe частей
- [ ] Controlled rollout для dangerous частей

---

## 📊 SUCCESS METRICS

```python
success_criteria = {
    "safety_compliance": 1.0,      # 100% соблюдение ai-ветки для опасных операций
    "false_positive_rate": 0.05,   # <5% ложных блокировок safe операций  
    "session_integrity": 1.0,      # 100% целостность AI сессий
    "development_velocity": 1.5     # 50% ускорение разработки safe частей
}
```

---

**🚀 ПЛАН ГОТОВ К ВНЕСЕНИЮ В ЭПИКИ И ISSUES!**

**СЛЕДУЮЩИЙ ШАГ:** Создать эпики в системе управления проектами и начать реализацию с EPIC 1: AI BRANCH SAFETY SYSTEM. 