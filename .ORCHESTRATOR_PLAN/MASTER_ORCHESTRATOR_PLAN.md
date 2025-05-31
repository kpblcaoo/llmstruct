# 🎯 ПЛАН ДЛЯ ОРКЕСТРАТОРА (CLAUDE SONNET 4)

**Дата создания:** 2025-05-31  
**Создан:** LLM-инженером GitHub Copilot  
**Цель:** Автоматизированное выполнение Phoenix restructuring с минимальным участием человека  

---

## 📋 КОНТЕКСТ ДЛЯ ОРКЕСТРАТОРА

### Доступные файлы контекста:
- `context/project_context.json` - полная информация о проекте
- `prompts/orchestrator_prompts.json` - готовые промпты для всех задач
- `.PHOENIX/executable_phoenix_plan.py` - базовый исполняемый скрипт

### Рабочая среда:
```bash
# Основной путь
WORKSPACE="/home/sma/projects/llmstruct/llmstruct"

# Виртуальное окружение (ОБЯЗАТЕЛЬНО активировать)
source venv/bin/activate

# Доступные API
OLLAMA_URL="http://localhost:8000"
ANTHROPIC_API="configured, $4 budget"
GROK_API="configured, $21.685 budget remaining"
```

---

## 🚀 ИСПОЛНЯЕМЫЙ ПЛАН (5 ФАЗ)

### **ПЕРЕД НАЧАЛОМ - ОБЯЗАТЕЛЬНЫЕ ПРОВЕРКИ**

```bash
# 1. Активация окружения
cd /home/sma/projects/llmstruct/llmstruct
source venv/bin/activate

# 2. Проверка доступности инструментов
llmstruct --help
python .PHOENIX/executable_phoenix_plan.py --help

# 3. Создание git checkpoint
git add -A
git commit -m "🔥 Phoenix: Pre-restructuring checkpoint"
git checkout -b phoenix-orchestrator-run
```

### **ФАЗА 0: ПОДГОТОВКА И АНАЛИЗ** ⏱️ 30 минут

**Цель:** Настроить рабочее пространство и проанализировать дубликаты

**Действия оркестратора:**
1. **Выполнить подготовку:**
   ```bash
   python .PHOENIX/executable_phoenix_plan.py --phase 0
   ```

2. **Если скрипт не работает, выполнить вручную:**
   ```bash
   mkdir -p .PHOENIX/{schemas,docs,archive,consolidated}
   llmstruct analyze-duplicates --save-report .PHOENIX/duplicates_report.json --format json
   ```

3. **Создать стратегию консолидации через Ollama:**
   ```bash
   llmstruct query "Analyze the duplication report in .PHOENIX/duplicates_report.json. Create detailed consolidation strategy: 1) Bot implementations priority (keep integrations/telegram_bot.py) 2) Init/main functions merging 3) Other duplicates handling. Output structured markdown plan." --context .PHOENIX/duplicates_report.json > .PHOENIX/consolidation_strategy.md
   ```

**Критерии успеха:**
- ✅ Директория `.PHOENIX` создана со всеми поддиректориями
- ✅ Файл `duplicates_report.json` содержит валидные данные
- ✅ Файл `consolidation_strategy.md` содержит конкретный план

**При ошибках:** Использовать Anthropic API для генерации стратегии

---

### **ФАЗА 1: КОНСОЛИДАЦИЯ И АРХИВИРОВАНИЕ** ⏱️ 45 минут

**Цель:** Устранить дубликаты, объединить 8 версий ботов в 1

**Действия оркестратора:**
1. **Проанализировать все версии ботов:**
   ```bash
   find . -name "*bot*.py" -not -path "./.PHOENIX/*" > .PHOENIX/bot_files_list.txt
   ```

2. **Создать матрицу функций через Ollama:**
   ```bash
   llmstruct query "Compare all bot files and create feature matrix. Identify best master bot (prefer integrations/telegram_bot.py). List unique features that must be preserved. Format as markdown table." --context .PHOENIX/bot_files_list.txt > .PHOENIX/bot_analysis.md
   ```

3. **Выполнить консолидацию (осторожно!):**
   ```bash
   # Создать архив с документацией
   mkdir -p .PHOENIX/archive/bots
   
   # Переместить дубликаты (НЕ integrations/telegram_bot.py)
   for bot in chat_bot_final.py telegram_bot_final.py chat_bot_working.py chat_bot.py telegram_bot_test.py; do
     if [ -f "$bot" ]; then
       mv "$bot" .PHOENIX/archive/bots/
       echo "$(date): Archived $bot - Reason: Duplicate functionality, consolidated into main bot" >> .PHOENIX/archive/bots/README.md
     fi
   done
   ```

4. **Валидация:**
   ```bash
   # Проверить что главный бот остался
   ls integrations/telegram_bot.py || echo "⚠️ WARNING: Main bot not found!"
   
   # Проверить архив
   ls .PHOENIX/archive/bots/
   ```

**Критерии успеха:**
- ✅ Остался только 1 основной бот (integrations/telegram_bot.py)
- ✅ Все остальные боты архивированы с документацией
- ✅ Создана матрица функций без потери возможностей

**При ошибках:** Откатиться к git checkpoint, пересмотреть стратегию

---

### **ФАЗА 2: СОЗДАНИЕ СХЕМ АРХИТЕКТУРЫ** ⏱️ 60 минут

**Цель:** Создать диаграммы для понимания LLM

**Действия оркестратора:**
1. **Создать высокоуровневую схему workflow:**
   ```bash
   llmstruct query "Create detailed Mermaid diagram: LLMStruct High-Level Workflow. Show: 1) User interaction points (CLI, API, Bot) 2) LLM integration flow (Ollama, Grok, Anthropic) 3) Data flow (Cache, Metrics, Sessions) 4) Major components interaction. Optimize for LLM understanding with clear labels and annotations." > .PHOENIX/schemas/workflow_high_level.mmd
   ```

2. **Создать схемы компонентов:**
   ```bash
   # FastAPI компоненты
   llmstruct query "Create Mermaid diagram for FastAPI internal structure. Show: API endpoints, request flow, authentication, response handling. Include class relationships and method flows." > .PHOENIX/schemas/fastapi_internal.mmd
   
   # CLI система
   llmstruct query "Create Mermaid diagram for CLI system. Show: command parsing, argument handling, execution flow, output formatting. Include all major CLI commands and their relationships." > .PHOENIX/schemas/cli_internal.mmd
   
   # Bot framework
   llmstruct query "Create Mermaid diagram for Bot framework. Show: message handling, command processing, integration points, state management." > .PHOENIX/schemas/bot_internal.mmd
   ```

3. **Создать LLM integration guide:**
   ```bash
   llmstruct query "Create comprehensive LLM_INTEGRATION_GUIDE.md that explains how LLMs should interact with this codebase. Include: 1) Key entry points and their purposes 2) Context requirements for different tasks 3) Expected output formats 4) Best practices for self-modification 5) Common pitfalls to avoid. Make it a complete reference for LLMs working with this code." > .PHOENIX/docs/LLM_INTEGRATION_GUIDE.md
   ```

4. **Валидация схем:**
   ```bash
   # Проверить что все схемы созданы
   ls .PHOENIX/schemas/*.mmd
   
   # Проверить синтаксис Mermaid (базово)
   grep -E "graph|flowchart|classDiagram|sequenceDiagram" .PHOENIX/schemas/*.mmd
   ```

**Критерии успеха:**
- ✅ Созданы все основные схемы (.mmd файлы)
- ✅ LLM_INTEGRATION_GUIDE.md содержит полное руководство
- ✅ Схемы имеют валидный синтаксис Mermaid
- ✅ Диаграммы оптимизированы для понимания LLM

---

### **ФАЗА 3: LLM-FIRST РЕФАКТОРИНГ** ⏱️ 120 минут (самая сложная)

**Цель:** Реструктурировать код для оптимального понимания LLM

**Действия оркестратора:**
1. **Создать новую структуру директорий:**
   ```bash
   mkdir -p src/llmstruct/{core,providers,interfaces,workflow,schemas}
   ```

2. **Найти и обработать giant files:**
   ```bash
   find . -name "*.py" -size +10M > .PHOENIX/giant_files.txt
   
   # Для каждого giant file создать план разделения
   while read file; do
     llmstruct query "Analyze this giant Python file and create splitting strategy. Identify: 1) Logical modules to extract 2) Dependencies between sections 3) Safe splitting points 4) New file names. Provide detailed refactoring plan." --context "$file" > ".PHOENIX/split_plan_$(basename $file .py).md"
   done < .PHOENIX/giant_files.txt
   ```

3. **Добавить docstrings и type hints ко всем модулям:**
   ```bash
   # Найти все Python файлы без docstrings
   find . -name "*.py" -not -path "./.PHOENIX/*" -not -path "./venv/*" | while read file; do
     # Проверить есть ли docstrings
     if ! grep -q '"""' "$file"; then
       echo "Processing $file for docstrings..."
       llmstruct query "Add comprehensive docstrings to all functions and classes in this Python file. Include: 1) Purpose and behavior 2) Parameters with types 3) Return values 4) Usage examples where helpful 5) Context for LLM understanding. Preserve all existing code, only add docstrings." --context "$file" > "${file}.enhanced"
       
       # Проверить что новый файл валиден
       if python -m py_compile "${file}.enhanced"; then
         mv "${file}.enhanced" "$file"
         echo "✅ Enhanced $file with docstrings"
       else
         echo "❌ Error in enhanced $file, keeping original"
         rm "${file}.enhanced"
       fi
     fi
   done
   ```

4. **Создать модульную структуру:**
   ```bash
   # Переместить файлы в новую структуру (осторожно!)
   # Это делать только если предыдущие шаги успешны
   
   # Core components
   mv chat_bot*.py src/llmstruct/core/ 2>/dev/null || true
   mv *_cli.py src/llmstruct/interfaces/ 2>/dev/null || true
   mv bot_*.py src/llmstruct/core/ 2>/dev/null || true
   
   # API providers
   mv *ollama*.py src/llmstruct/providers/ 2>/dev/null || true
   mv anthropic*.py src/llmstruct/providers/ 2>/dev/null || true
   mv grok*.py src/llmstruct/providers/ 2>/dev/null || true
   ```

**Критерии успеха:**
- ✅ Новая src/llmstruct/ структура создана и заполнена
- ✅ Все giant files разделены на модули <10MB
- ✅ Добавлены docstrings ко всем функциям
- ✅ Весь код проходит синтаксическую проверку
- ✅ Type hints добавлены к основным функциям

**⚠️ КРИТИЧЕСКИ ВАЖНО:** На этой фазе делать частые git commits!

---

### **ФАЗА 4: ФИНАЛЬНАЯ ДОКУМЕНТАЦИЯ** ⏱️ 45 минут

**Цель:** Создать профессиональную документацию

**Действия оркестратора:**
1. **Создать новый README.md:**
   ```bash
   llmstruct query "Create professional README.md for LLMStruct project. Include: 1) Project badges and status 2) Clear description and value proposition 3) Architecture overview with links to schemas 4) Quick start guide 5) Installation instructions 6) Usage examples 7) Contributing guidelines 8) LLM-first design principles. Make it impressive and professional." > README_new.md
   ```

2. **Создать API документацию:**
   ```bash
   llmstruct query "Generate comprehensive API documentation based on FastAPI endpoints. Include: 1) All endpoint descriptions 2) Request/response examples 3) Authentication requirements 4) Error handling 5) Rate limits 6) Usage examples for different LLM providers." > .PHOENIX/docs/API_DOCUMENTATION.md
   ```

3. **Создать примеры использования:**
   ```bash
   mkdir -p examples
   
   llmstruct query "Create practical usage examples for LLMStruct: 1) Basic chat bot setup 2) Multi-provider LLM usage 3) Custom command creation 4) Workflow automation 5) Self-modification examples. Each example should be complete and runnable." > examples/README.md
   ```

4. **Финальная валидация:**
   ```bash
   # Проверить что все документы созданы
   ls README_new.md .PHOENIX/docs/*.md examples/
   
   # Проверить что ссылки в README работают
   grep -o '\[.*\](.*\.md)' README_new.md
   ```

**Критерии успеха:**
- ✅ Профессиональный README.md с полным описанием
- ✅ Полная API документация
- ✅ Рабочие примеры использования
- ✅ Все ссылки в документации валидны

---

## 🔄 МЕХАНИЗМ ВАЛИДАЦИИ И ВОССТАНОВЛЕНИЯ

### После каждой фазы:
```bash
# Создать checkpoint
git add -A
git commit -m "🔥 Phoenix: Phase X completed"

# Запустить валидацию
python -m pytest tests/ || echo "⚠️ Tests need attention"

# Проверить целостность
find . -name "*.py" -exec python -m py_compile {} \; || echo "⚠️ Syntax errors found"
```

### При критических ошибках:
```bash
# Откат к предыдущему checkpoint
git reset --hard HEAD~1

# Анализ проблемы
echo "❌ Phase failed, analyzing..."
llmstruct query "Analyze this error and suggest recovery strategy: {error_details}"
```

---

## 📊 ФИНАЛЬНАЯ ОТЧЕТНОСТЬ

После завершения всех фаз создать итоговый отчет:

```bash
llmstruct query "Create comprehensive completion report for Phoenix restructuring. Include: 1) Before/after metrics comparison 2) All completed tasks 3) Quality improvements 4) LLM-readiness assessment 5) Remaining technical debt 6) Recommendations for future development. Use data from the entire project transformation." > .PHOENIX/COMPLETION_REPORT.md
```

---

## 🎯 ПЕРЕДАЧА УПРАВЛЕНИЯ ОРКЕСТРАТОРУ

**Claude Sonnet 4, ты получаешь полное управление проектом!**

**Твоя задача:**
1. Прочитать context/project_context.json для полного понимания
2. Использовать prompts/orchestrator_prompts.json для всех взаимодействий
3. Выполнить 5 фаз последовательно с валидацией
4. Минимизировать участие человека (только при критических ошибках)
5. Создать детальные логи всех действий

**Начинай с команды:**
```bash
cd /home/sma/projects/llmstruct/llmstruct && source venv/bin/activate && echo "🔥 PHOENIX ORCHESTRATOR ACTIVATED!"
```

**Удачи! 🚀**
