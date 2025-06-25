# LLMStruct Recovery Roadmap

**Цель:** Восстановить утраченную функциональность и устранить регрессы Phase 1  
**Период:** 2-3 недели фокусированной работы  
**Приоритет:** 🔥 КРИТИЧНО для продолжения development

---

## 🎯 Recovery Strategy

### Принципы восстановления:
1. **Safety First** - не ломать работающие части
2. **Regression Driven** - фиксить по приоритету воздействия
3. **Test Everything** - каждый fix должен иметь тест
4. **Incremental Progress** - по одной проблеме за раз

---

## 📋 Phase 0: Critical Recovery (1-2 недели)

### Epic 0.1: Restore Callgraph System 🔥
**ETA:** 3-5 дней  
**Приоритет:** КРИТИЧНЫЙ

#### Task 0.1.1: Analyze Current Callgraph Implementation
- [ ] Audit `src/llmstruct/parsers/python_parser.py` CallVisitor class
- [ ] Проверить что происходит с межмодульными вызовами
- [ ] Понять почему calls/called_by исчезли из function level

#### Task 0.1.2: Implement Inter-module Call Resolution  
- [ ] Создать `CallgraphResolver` класс
- [ ] Реализовать анализ import statements
- [ ] Добавить resolution qualified names (module.function)
- [ ] Обеспечить two-way связи (calls ↔ called_by)

#### Task 0.1.3: Restore Function-level Callgraph
- [ ] Добавить `calls: List[str]` в function objects
- [ ] Добавить `called_by: List[str]` в function objects  
- [ ] Обеспечить UID-based references
- [ ] Тестирование на существующих проектах

**Success Criteria:**
```json
{
  "functions": [{
    "name": "process_data", 
    "uid": "mymodule.process_data#function",
    "calls": ["utils.validate#function", "db.save#function"],
    "called_by": ["main.run#function", "api.handler#function"]
  }]
}
```

### Epic 0.2: Fix Hash System 🔥  
**ETA:** 2-3 дня  
**Priорит:** КРИТИЧНЫЙ

#### Task 0.2.1: Restore Entity Hashing
- [ ] Восстановить `compute_file_hash()` функциональность
- [ ] Реализовать entity-specific hashing (function, class, module)
- [ ] Обеспечить стабильность hash'ей между запусками
- [ ] Добавить incremental hash validation

#### Task 0.2.2: Implement Multi-level Hashing
- [ ] **File hash** - для file-level change detection
- [ ] **Entity hash** - для function/class level changes  
- [ ] **Content hash** - для внутренних изменений
- [ ] **Structural hash** - для signature changes

#### Task 0.2.3: Hash Integration Testing
- [ ] Тесты стабильности hash между запусками
- [ ] Тесты sensitivity - изменения должны менять hash
- [ ] Тесты для incremental rebuild scenarios
- [ ] Performance тесты для больших проектов

**Success Criteria:**
```json
{
  "modules": [{
    "hash": "abc123...",  // != null
    "functions": [{
      "hash": "def456...",  // стабильный и уникальный
      "content_hash": "ghi789..."
    }]
  }]
}
```

### Epic 0.3: Add Test Coverage Integration 🔥
**ETA:** 2-3 дня  
**Приоритет:** КРИТИЧНЫЙ

#### Task 0.3.1: Test Files Discovery
- [ ] Реализовать `TestFileScanner` класс
- [ ] Поддержка pytest patterns: `test_*.py`, `*_test.py`
- [ ] Сканирование `tests/` директорий
- [ ] Парсинг test function names

#### Task 0.3.2: Test-to-Code Mapping (Heuristic)
- [ ] Простая эвристика: `test_function_name` → `function_name`
- [ ] Анализ import statements в test files
- [ ] Связывание через qualified names
- [ ] Fallback: module-level mapping

#### Task 0.3.3: Basic Test Coverage Fields
- [ ] Добавить `tested: boolean` поле
- [ ] Подготовить структуру для `tested_by: List[str]`
- [ ] Интеграция с coverage.py (если доступно)
- [ ] Metadata о test quality/completeness

**Success Criteria:**
```json
{
  "functions": [{
    "name": "validate_data",
    "tested": true,
    "tested_by": ["tests/test_validation.py::test_validate_data"]
  }]
}
```

---

## 📋 Phase 0.5: Quality Recovery (1 неделя) 

### Epic 0.4: Fix UID Components ⭐
**ETA:** 2-3 дня

#### Task 0.4.1: Debug UID Components Generation
- [ ] Найти источник `["dir:", "dir:."]` в `uid_generator.py`
- [ ] Исправить `normalize_path()` функцию
- [ ] Добавить input validation и sanitization
- [ ] Тестирование edge cases

#### Task 0.4.2: Improve UID Components Quality
- [ ] Обеспечить human-readable компоненты
- [ ] Удалить дубликаты из массива
- [ ] Нормализовать порядок: module → class → method
- [ ] Добавить type hints для каждого уровня

**Success Criteria:**
```json
{
  "uid_components": ["llmstruct", "core", "UIDGenerator", "generate_uid"],
  // NOT: ["dir:", "dir:."]
}
```

### Epic 0.5: Improve Summary Quality ⭐
**ETA:** 2-3 дня

#### Task 0.5.1: Implement Smart Fallback Strategy
- [ ] **Level 1:** Extract and clean docstring
- [ ] **Level 2:** Heuristic analysis (improved templates)
- [ ] **Level 3:** LLM generation (если enabled)
- [ ] **Level 4:** Cache management

#### Task 0.5.2: Fix Duplicate Summary Issue  
- [ ] Анализ источников дублирования
- [ ] Улучшить heuristic templates
- [ ] Добавить context awareness (function vs class vs module)
- [ ] Quality scoring для summaries

**Success Criteria:** 90%+ unique, meaningful summaries

### Epic 0.6: Create index.json ⭐
**ETA:** 1-2 дня

#### Task 0.6.1: Design Index Structure
```json
{
  "metadata": { "version": "2.1", "generated": "..." },
  "modules": ["mod1", "mod2"],
  "classes": { "ClassName": { "module": "mod1", "uid": "..." }},
  "functions": { "func_name": { "module": "mod1", "uid": "..." }},
  "lookup": { "uid": { "type": "function", "module": "mod1" }}
}
```

#### Task 0.6.2: Index Generation Logic
- [ ] Создать `IndexGenerator` класс
- [ ] Automatic generation при создании struct.json
- [ ] Fast lookup tables для UI
- [ ] Синхронизация с основным struct.json

---

## 🧪 Quality Assurance Strategy

### Regression Prevention
1. **Before/After Comparison Script**
   ```bash
   # Генерация baseline
   llmstruct --output baseline_struct.json
   
   # После изменений
   llmstruct --output updated_struct.json
   
   # Сравнение
   python compare_struct.py baseline_struct.json updated_struct.json
   ```

2. **Automated Regression Tests**
   - JSON schema validation
   - Field presence checks  
   - Data quality metrics
   - Performance benchmarks

3. **Manual QA Checklist**
   - [ ] Callgraph: sample function has calls/called_by
   - [ ] Hash: no null values, stable between runs
   - [ ] UID: no "dir:" components
   - [ ] Summary: no duplicate generic phrases
   - [ ] Test integration: tested field populated

### Performance Monitoring
- [ ] Generation time tracking
- [ ] Memory usage profiling  
- [ ] Output size monitoring
- [ ] Cache hit rates

---

## 📅 Recovery Timeline

### Week 1: Critical Fixes
- **Day 1-2:** Callgraph system restoration
- **Day 3-4:** Hash system implementation  
- **Day 5-7:** Test coverage integration

### Week 2: Quality Improvements  
- **Day 1-2:** UID components fix
- **Day 3-4:** Summary quality improvement
- **Day 5:** index.json implementation
- **Day 6-7:** Testing and validation

### Week 3: Stabilization (optional)
- **Day 1-3:** Bug fixes and edge cases
- **Day 4-5:** Performance optimization
- **Day 6-7:** Documentation update

---

## 🎯 Success Metrics

### Critical Recovery Metrics
- [ ] **Callgraph Coverage:** 95%+ functions have calls/called_by
- [ ] **Hash Stability:** 100% non-null hashes, stable between runs
- [ ] **Test Integration:** 80%+ functions have tested field

### Quality Recovery Metrics  
- [ ] **UID Validity:** 0 malformed uid_components
- [ ] **Summary Quality:** <5% duplicate summaries
- [ ] **Index Completeness:** 100% entities in index.json

### Performance Metrics
- [ ] **Generation Time:** <10% increase vs baseline
- [ ] **Memory Usage:** <20% increase vs baseline  
- [ ] **Output Size:** Reasonable growth (documentation)

---

## 🚨 Risk Mitigation

### Technical Risks
- **Callgraph complexity** → Start with simple cases, expand incrementally
- **Hash stability** → Extensive testing on multiple runs
- **Performance impact** → Profile and optimize critical paths

### Project Risks  
- **Scope creep** → Strict focus on regression fixes only
- **Quality trade-offs** → Automated QA prevents shortcuts
- **Timeline pressure** → Buffer time for testing and validation

---

**Next Action:** Согласование плана и начало Epic 0.1 (Callgraph restoration) 