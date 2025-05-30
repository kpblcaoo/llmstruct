# 📋 ПЛАН ПРОРАБОТКИ: Система листинга промптов для ЛЛМ

**Статус**: 🤔 Проработка  
**Приоритет**: Высокий  
**Цель**: Создать централизованную систему управления промптами для ЛЛМ  
**Дата создания**: 2025-05-29  

---

## 🎯 КОНТЕКСТ

**Текущая ситуация:**
- Есть `src/llmstruct/templates/llm_prompt_template.txt` (базовый шаблон)
- Система `Context Tags` уже работает: `[code]`, `[debug]`, `[discuss]`, etc.
- `CopilotContextManager` и `SmartContextOrchestrator` уже интегрированы
- Нужна централизованная система управления промптами

**Почему важно:**
- Консистентность работы с разными ЛЛМ (Grok, Claude, локальные)
- Разделение boss/team промптов для приватности
- Оптимизация token budget через smart context injection
- Масштабирование для команды (momai + будущие участники)

---

## 🤔 КЛЮЧЕВЫЕ ВОПРОСЫ ДЛЯ РЕШЕНИЯ

### **1. АРХИТЕКТУРА И СТРУКТУРА**

**1.1 Организация промптов:**
- [ ] Иерархическая структура: базовые → специализированные → пользовательские?
- [ ] Модульная система: header + context_injection + task + output_format?  
- [ ] Версионирование: как отслеживать изменения промптов?
- [ ] Наследование: базовый промпт + overrides?

**1.2 Категоризация:**
- [ ] По типу задач: code, debug, docs, review, plan, refactor?
- [ ] По контексту: struct.json, init.json, minimal, full?
- [ ] По ЛЛМ: universal vs model-specific (Grok vs Claude)?
- [ ] По доступу: public vs boss-only vs personal?

### **2. ХРАНЕНИЕ И УПРАВЛЕНИЕ**

**2.1 Формат и локация:**
- [ ] JSON templates vs текстовые файлы vs database?
- [ ] Структура папок: `templates/[category]/[model]/[prompt].json`?
- [ ] Интеграция с `.personal/` для boss промптов?
- [ ] Синхронизация: git vs отдельная система?

**2.2 Источники контента:**
- [ ] Кто создает: только kpblcaoo vs команда vs AI-генерация?
- [ ] Процесс review: как утверждать новые промпты?
- [ ] Community prompts: можно ли брать из внешних источников?
- [ ] Backup и восстановление промптов?

### **3. ДИНАМИЧЕСКАЯ СБОРКА**

**3.1 Context injection механизм:**
- [ ] Автоматическое определение контекста по типу задачи?
- [ ] Smart filtering: как выбирать релевантные части struct.json?
- [ ] Token budget management: как балансировать полноту vs размер?
- [ ] Переменные: `{{USER_QUESTION}}`, `{{PROJECT_CONTEXT}}`, `{{CURRENT_FILE}}`?

**3.2 Адаптация под ЛЛМ:**
- [ ] Автоопределение модели и адаптация промпта?
- [ ] Fallback стратегии для разных моделей?
- [ ] Специфичные форматирования (Grok предпочтения vs Claude)?
- [ ] Оптимизация длины для context windows?

### **4. ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС**

**4.1 CLI команды:**
- [ ] `llmstruct prompts list [--category code] [--access public]`?
- [ ] `llmstruct prompts create --name review_code --template advanced`?
- [ ] `llmstruct prompts test --prompt my_prompt --input sample_code`?
- [ ] `llmstruct prompts optimize --prompt my_prompt --metrics quality`?

**4.2 Workflow интеграция:**
- [ ] Интеграция с VS Code: auto-suggest промптов?
- [ ] Курсор integration: как подключить к Cursor AI?
- [ ] GitHub workflow: промпты для PR review, issue analysis?
- [ ] Session management: как сохранять контекст между промптами?

### **5. ДОСТУП И БЕЗОПАСНОСТЬ**

**5.1 Разделение уровней доступа:**
- [ ] Boss prompts (`.personal/prompts/`): только kpblcaoo?
- [ ] Team prompts (`templates/team/`): команда видит?
- [ ] Public prompts (`templates/public/`): опен-сорс?
- [ ] Personal overrides: как каждый участник может кастомизировать?

**5.2 Фильтрация и безопасность:**
- [ ] Автоочистка sensitive данных из промптов?
- [ ] Логирование использования промптов для аудита?
- [ ] Валидация промптов перед применением?
- [ ] Экранирование от prompt injection атак?

### **6. ОПТИМИЗАЦИЯ И МЕТРИКИ**

**6.1 Качество промптов:**
- [ ] Как измерять эффективность промпта (качество ответов)?
- [ ] A/B тестирование промптов на реальных задачах?
- [ ] Автооптимизация на основе feedback?
- [ ] Система рейтингов от пользователей?

**6.2 Performance:**
- [ ] Кэширование собранных промптов?
- [ ] Lazy loading для больших промптов?
- [ ] Compression для экономии bandwidth?
- [ ] Metrics: время сборки, размер, hit rate?

### **7. ИНТЕГРАЦИЯ С ЭКОСИСТЕМОЙ**

**7.1 Существующие компоненты:**
- [ ] Связь с `Context Tags System`: автовыбор промпта по тегам?
- [ ] Интеграция с `CopilotContextManager`: token budget awareness?
- [ ] Связь с `epic_roadmap_manager`: промпты для epic analysis?
- [ ] Использование `github_sync_manager`: промпты для GitHub API?

**7.2 AI-assisted development:**
- [ ] Промпты для обработки 926 items в processing pipeline?
- [ ] Integration с AI self-awareness системой?
- [ ] Промпты для автогенерации GitHub Issues/Epics?
- [ ] Связь с business planning (boss CLI)?

---

## 🎯 ПРЕДВАРИТЕЛЬНЫЕ РЕШЕНИЯ

### **ПРИОРИТЕТ 1 (Критично - решить сейчас):**

1. **Базовая архитектура:**
   ```
   templates/
   ├── core/           # Базовые промпты (универсальные)
   ├── team/           # Командные промпты (публичные)
   └── .personal/prompts/  # Boss промпты (приватные)
   ```

2. **CLI интерфейс:** 
   - `llmstruct prompts list`
   - `llmstruct prompts use <name> --context <file>`

3. **Интеграция с Context Tags:**
   - Автовыбор промпта по тегам `[code]` → code_analysis_prompt

### **ПРИОРИТЕТ 2 (Важно - решить вскоре):**

1. **Dynamic context injection** с переменными
2. **Multi-LLM support** с fallback стратегиями  
3. **Security filtering** для boss/team разделения

### **ПРИОРИТЕТ 3 (Перспективно - можно отложить):**

1. **AI-оптимизация** промптов
2. **Advanced UI** для управления
3. **Community sharing** промптов

---

## 📋 ПЛАН ДЕЙСТВИЙ

### **Фаза 1: MVP (1-2 дня)**
- [ ] Создать базовую структуру папок
- [ ] Реализовать `llmstruct prompts list/use`
- [ ] Интегрировать с Context Tags
- [ ] Тестирование на 2-3 базовых промптах

### **Фаза 2: Core Features (3-5 дней)**
- [ ] Dynamic context injection
- [ ] Boss/team разделение доступа
- [ ] Multi-LLM адаптация
- [ ] CLI расширение

### **Фаза 3: Advanced (1-2 недели)**
- [ ] Оптимизация и метрики
- [ ] Интеграция с AI ecosystem
- [ ] Performance improvements
- [ ] Documentation

---

## 🤝 УЧАСТИЕ КОМАНДЫ

**kpblcaoo (Михаил):**
- Архитектурные решения
- Boss промпты и security
- Интеграция с существующей системой

**momai:**
- Team промпты для DevOps задач
- CLI интерфейс тестирование
- Performance optimization

**Будущие участники:**
- Prompt contributions
- Quality feedback
- Use case testing

---

**📌 СТАТУС: Готов к детальному планированию первой фазы**

**СЛЕДУЮЩИЙ ШАГ:** Выбрать конкретные решения из вопросов выше и создать техническое ТЗ для MVP. 