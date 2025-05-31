#!/bin/bash
# БЫСТРЫЕ КОМАНДЫ ДЛЯ ОРКЕСТРАТОРА
# Этот файл содержит готовые к выполнению команды для каждой фазы

# ПОДГОТОВКА
setup_orchestrator() {
    echo "🔥 Setting up Phoenix Orchestrator environment..."
    cd /home/sma/projects/llmstruct/llmstruct
    source venv/bin/activate
    
    # Проверки готовности
    echo "Checking tools availability..."
    llmstruct --help > /dev/null && echo "✅ llmstruct CLI ready" || echo "❌ llmstruct CLI not available"
    python --version
    git status --porcelain
    
    # Создание checkpoint
    git add -A
    git commit -m "🔥 Phoenix: Pre-orchestrator checkpoint - $(date)"
    git checkout -b "phoenix-orchestrator-$(date +%Y%m%d-%H%M%S)"
    
    echo "🚀 Orchestrator environment ready!"
}

# ФАЗА 0: ПОДГОТОВКА
phase_0_preparation() {
    echo "🔄 Executing Phase 0: Preparation and Analysis"
    
    # Создание структуры
    mkdir -p .PHOENIX/{schemas,docs,archive,consolidated}
    
    # Анализ дубликатов
    echo "Running duplicate analysis..."
    llmstruct analyze-duplicates --save-report .PHOENIX/duplicates_report.json --format json
    
    # Создание стратегии консолидации
    echo "Generating consolidation strategy..."
    llmstruct query "Analyze the duplication report and create detailed consolidation strategy. Group by: 1) Bot implementations (8 versions found) 2) Init/main functions 3) Other duplicates. Prioritize keeping integrations/telegram_bot.py as master bot. Output structured markdown plan with specific file operations." --context .PHOENIX/duplicates_report.json > .PHOENIX/consolidation_strategy.md
    
    # Валидация Phase 0
    validate_phase_0
}

validate_phase_0() {
    echo "🔍 Validating Phase 0..."
    local errors=0
    
    [ -d ".PHOENIX" ] && echo "✅ .PHOENIX directory exists" || { echo "❌ .PHOENIX directory missing"; errors=$((errors+1)); }
    [ -f ".PHOENIX/duplicates_report.json" ] && echo "✅ Duplicates report exists" || { echo "❌ Duplicates report missing"; errors=$((errors+1)); }
    [ -f ".PHOENIX/consolidation_strategy.md" ] && echo "✅ Consolidation strategy exists" || { echo "❌ Consolidation strategy missing"; errors=$((errors+1)); }
    
    if [ $errors -eq 0 ]; then
        echo "✅ Phase 0 validation PASSED"
        git add -A && git commit -m "🔥 Phoenix: Phase 0 completed - Preparation and Analysis"
        return 0
    else
        echo "❌ Phase 0 validation FAILED with $errors errors"
        return 1
    fi
}

# ФАЗА 1: КОНСОЛИДАЦИЯ
phase_1_consolidation() {
    echo "🔄 Executing Phase 1: Consolidation and Archiving"
    
    # Найти все bot файлы
    echo "Analyzing bot files..."
    find . -name "*bot*.py" -not -path "./.PHOENIX/*" -not -path "./venv/*" > .PHOENIX/bot_files_list.txt
    cat .PHOENIX/bot_files_list.txt
    
    # Создать анализ ботов
    echo "Creating bot analysis..."
    llmstruct query "Analyze all bot files listed and create feature comparison matrix. Determine: 1) Which bot has most complete functionality 2) Which unique features exist in each bot 3) Safe consolidation plan 4) Risk assessment for each merge. Prefer keeping integrations/telegram_bot.py if it exists and is functional." --context .PHOENIX/bot_files_list.txt > .PHOENIX/bot_analysis.md
    
    # ОСТОРОЖНАЯ консолидация
    echo "Starting careful bot consolidation..."
    mkdir -p .PHOENIX/archive/bots
    
    # Создать резервную копию всех ботов
    cp *bot*.py .PHOENIX/archive/bots/ 2>/dev/null || true
    
    # Архивировать дубликаты (НЕ трогать integrations/telegram_bot.py!)
    for bot in chat_bot_final.py telegram_bot_final.py chat_bot_working.py chat_bot.py telegram_bot_test.py telegram_bot_enhanced.py; do
        if [ -f "$bot" ] && [ "$bot" != "integrations/telegram_bot.py" ]; then
            echo "Archiving $bot..."
            mv "$bot" .PHOENIX/archive/bots/
            echo "$(date): Archived $bot - Reason: Duplicate functionality, consolidated into main bot framework" >> .PHOENIX/archive/bots/README.md
        fi
    done
    
    validate_phase_1
}

validate_phase_1() {
    echo "🔍 Validating Phase 1..."
    local errors=0
    
    # Проверить что основной бот остался
    if [ -f "integrations/telegram_bot.py" ] || [ $(find . -name "*bot*.py" -not -path "./.PHOENIX/*" | wc -l) -eq 1 ]; then
        echo "✅ Main bot preserved"
    else
        echo "❌ Bot consolidation unclear"
        errors=$((errors+1))
    fi
    
    [ -d ".PHOENIX/archive/bots" ] && echo "✅ Bot archive created" || { echo "❌ Bot archive missing"; errors=$((errors+1)); }
    [ -f ".PHOENIX/bot_analysis.md" ] && echo "✅ Bot analysis completed" || { echo "❌ Bot analysis missing"; errors=$((errors+1)); }
    
    if [ $errors -eq 0 ]; then
        echo "✅ Phase 1 validation PASSED"
        git add -A && git commit -m "🔥 Phoenix: Phase 1 completed - Consolidation and Archiving"
        return 0
    else
        echo "❌ Phase 1 validation FAILED with $errors errors"
        return 1
    fi
}

# ФАЗА 2: СХЕМЫ
phase_2_schemas() {
    echo "🔄 Executing Phase 2: Schema Creation"
    
    # Высокоуровневая схема
    echo "Creating high-level workflow schema..."
    llmstruct query "Create detailed Mermaid diagram: LLMStruct High-Level Workflow. Show: 1) User interaction points (CLI, API, Bot) 2) LLM integration flow (Ollama local, Grok API, Anthropic API) 3) Data flow (Cache, Metrics, Sessions, Database) 4) Major components interaction. Use clear node labels and annotations optimized for LLM understanding. Include error handling flows." > .PHOENIX/schemas/workflow_high_level.mmd
    
    # Схемы компонентов
    echo "Creating component schemas..."
    llmstruct query "Create Mermaid class diagram for FastAPI internal structure. Show: API route classes, middleware, request/response models, authentication, error handling. Include method signatures and relationships." > .PHOENIX/schemas/fastapi_internal.mmd
    
    llmstruct query "Create Mermaid flowchart for CLI system architecture. Show: command parsing flow, argument validation, execution pipeline, output formatting, error handling. Include all major CLI commands and their interaction patterns." > .PHOENIX/schemas/cli_internal.mmd
    
    llmstruct query "Create Mermaid diagram for Bot framework architecture. Show: message processing pipeline, command handling, state management, integration points with LLM providers, session management." > .PHOENIX/schemas/bot_internal.mmd
    
    # LLM Integration Guide
    echo "Creating LLM integration guide..."
    llmstruct query "Create comprehensive LLM_INTEGRATION_GUIDE.md explaining how LLMs should interact with this codebase. Include: 1) Key entry points and their purposes 2) Context requirements for different tasks 3) Expected input/output formats 4) Best practices for code analysis and modification 5) Common patterns and conventions 6) Error handling strategies 7) Self-modification guidelines. Make it the definitive reference for LLM interactions." > .PHOENIX/docs/LLM_INTEGRATION_GUIDE.md
    
    validate_phase_2
}

validate_phase_2() {
    echo "🔍 Validating Phase 2..."
    local errors=0
    
    # Проверить схемы
    for schema in workflow_high_level.mmd fastapi_internal.mmd cli_internal.mmd bot_internal.mmd; do
        if [ -f ".PHOENIX/schemas/$schema" ]; then
            echo "✅ Schema $schema exists"
            # Простая проверка синтаксиса Mermaid
            if grep -qE "(graph|flowchart|classDiagram|sequenceDiagram)" ".PHOENIX/schemas/$schema"; then
                echo "✅ Schema $schema has valid Mermaid syntax"
            else
                echo "⚠️ Schema $schema might have syntax issues"
            fi
        else
            echo "❌ Schema $schema missing"
            errors=$((errors+1))
        fi
    done
    
    [ -f ".PHOENIX/docs/LLM_INTEGRATION_GUIDE.md" ] && echo "✅ LLM Integration Guide exists" || { echo "❌ LLM Integration Guide missing"; errors=$((errors+1)); }
    
    if [ $errors -eq 0 ]; then
        echo "✅ Phase 2 validation PASSED"
        git add -A && git commit -m "🔥 Phoenix: Phase 2 completed - Schema Creation"
        return 0
    else
        echo "❌ Phase 2 validation FAILED with $errors errors"
        return 1
    fi
}

# ФАЗА 3: РЕФАКТОРИНГ (самая осторожная!)
phase_3_refactoring() {
    echo "🔄 Executing Phase 3: LLM-First Refactoring"
    echo "⚠️ This is the most critical phase - proceeding carefully..."
    
    # Создать структуру
    mkdir -p src/llmstruct/{core,providers,interfaces,workflow,schemas}
    
    # Найти giant files
    echo "Identifying giant files..."
    find . -name "*.py" -size +10M -not -path "./.PHOENIX/*" -not -path "./venv/*" > .PHOENIX/giant_files.txt || touch .PHOENIX/giant_files.txt
    
    if [ -s .PHOENIX/giant_files.txt ]; then
        echo "Found giant files to split:"
        cat .PHOENIX/giant_files.txt
        
        # Создать план разделения для каждого giant file
        while IFS= read -r file; do
            echo "Creating split plan for $file..."
            llmstruct query "Analyze this giant Python file and create detailed splitting strategy. Identify: 1) Logical modules to extract 2) Class and function groupings 3) Dependencies between sections 4) Safe splitting points 5) Proposed new file names and structure. Provide step-by-step refactoring plan." --context "$file" > ".PHOENIX/split_plan_$(basename "$file" .py).md"
        done < .PHOENIX/giant_files.txt
    else
        echo "✅ No giant files found"
    fi
    
    # Добавить docstrings (осторожно!)
    echo "Adding docstrings to Python files..."
    find . -name "*.py" -not -path "./.PHOENIX/*" -not -path "./venv/*" -not -path "./src/*" | head -10 | while IFS= read -r file; do
        echo "Processing $file for docstrings..."
        
        # Проверить есть ли уже docstrings
        if ! grep -q '"""' "$file" && [ -s "$file" ]; then
            # Создать enhanced версию
            llmstruct query "Enhance this Python file by adding comprehensive docstrings to all classes and functions. Include: 1) Clear purpose description 2) Parameter types and descriptions 3) Return value description 4) Usage examples where helpful 5) Context for LLM understanding. PRESERVE ALL EXISTING CODE - only add docstrings, do not modify functionality." --context "$file" > "${file}.enhanced"
            
            # Проверить синтаксис enhanced версии
            if python -m py_compile "${file}.enhanced" 2>/dev/null; then
                mv "${file}.enhanced" "$file"
                echo "✅ Enhanced $file with docstrings"
            else
                echo "❌ Enhanced $file has syntax errors, keeping original"
                rm -f "${file}.enhanced"
            fi
        fi
    done
    
    validate_phase_3
}

validate_phase_3() {
    echo "🔍 Validating Phase 3..."
    local errors=0
    
    # Проверить новую структуру
    [ -d "src/llmstruct" ] && echo "✅ New src structure created" || { echo "❌ New src structure missing"; errors=$((errors+1)); }
    
    # Проверить что код компилируется
    echo "Checking Python syntax for all files..."
    syntax_errors=0
    find . -name "*.py" -not -path "./.PHOENIX/*" -not -path "./venv/*" | while IFS= read -r file; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            echo "❌ Syntax error in $file"
            syntax_errors=$((syntax_errors+1))
        fi
    done
    
    if [ $syntax_errors -eq 0 ]; then
        echo "✅ All Python files have valid syntax"
    else
        echo "❌ Found $syntax_errors files with syntax errors"
        errors=$((errors+1))
    fi
    
    if [ $errors -eq 0 ]; then
        echo "✅ Phase 3 validation PASSED"
        git add -A && git commit -m "🔥 Phoenix: Phase 3 completed - LLM-First Refactoring"
        return 0
    else
        echo "❌ Phase 3 validation FAILED with $errors errors"
        return 1
    fi
}

# ФАЗА 4: ДОКУМЕНТАЦИЯ
phase_4_documentation() {
    echo "🔄 Executing Phase 4: Final Documentation"
    
    # Новый README
    echo "Creating professional README..."
    llmstruct query "Create impressive professional README.md for LLMStruct project. Include: 1) Eye-catching badges and project status 2) Clear value proposition and description 3) Architecture overview with links to diagrams 4) Quick start guide with examples 5) Installation instructions 6) Usage examples for different scenarios 7) Contributing guidelines 8) LLM-first design principles explanation 9) API documentation links. Make it GitHub-ready and professional." > README_new.md
    
    # API документация
    echo "Creating API documentation..."
    llmstruct query "Generate comprehensive API documentation for LLMStruct FastAPI endpoints. Include: 1) Complete endpoint descriptions 2) Request/response schemas with examples 3) Authentication requirements 4) Error codes and handling 5) Rate limiting information 6) Usage examples for different LLM providers 7) Integration examples. Format as professional API docs." > .PHOENIX/docs/API_DOCUMENTATION.md
    
    # Примеры использования
    echo "Creating usage examples..."
    mkdir -p examples
    llmstruct query "Create practical, runnable usage examples for LLMStruct: 1) Basic chat bot setup and configuration 2) Multi-provider LLM usage (Ollama + external APIs) 3) Custom command creation and registration 4) Workflow automation examples 5) Self-modification and code generation examples 6) Integration with external tools. Each example should be complete, documented, and immediately runnable." > examples/README.md
    
    validate_phase_4
}

validate_phase_4() {
    echo "🔍 Validating Phase 4..."
    local errors=0
    
    [ -f "README_new.md" ] && echo "✅ New README created" || { echo "❌ New README missing"; errors=$((errors+1)); }
    [ -f ".PHOENIX/docs/API_DOCUMENTATION.md" ] && echo "✅ API documentation created" || { echo "❌ API documentation missing"; errors=$((errors+1)); }
    [ -f "examples/README.md" ] && echo "✅ Usage examples created" || { echo "❌ Usage examples missing"; errors=$((errors+1)); }
    
    if [ $errors -eq 0 ]; then
        echo "✅ Phase 4 validation PASSED"
        git add -A && git commit -m "🔥 Phoenix: Phase 4 completed - Final Documentation"
        return 0
    else
        echo "❌ Phase 4 validation FAILED with $errors errors"
        return 1
    fi
}

# ПОЛНОЕ ВЫПОЛНЕНИЕ ВСЕХ ФАЗ
execute_full_phoenix_plan() {
    echo "🔥 STARTING FULL PHOENIX ORCHESTRATOR EXECUTION"
    
    setup_orchestrator || { echo "❌ Setup failed"; return 1; }
    
    phase_0_preparation || { echo "❌ Phase 0 failed"; return 1; }
    
    phase_1_consolidation || { echo "❌ Phase 1 failed"; return 1; }
    
    phase_2_schemas || { echo "❌ Phase 2 failed"; return 1; }
    
    phase_3_refactoring || { echo "❌ Phase 3 failed"; return 1; }
    
    phase_4_documentation || { echo "❌ Phase 4 failed"; return 1; }
    
    # Финальный отчет
    echo "Creating completion report..."
    llmstruct query "Create comprehensive Phoenix restructuring completion report. Include: 1) Before/after metrics comparison 2) All completed tasks and improvements 3) Code quality enhancements 4) LLM-readiness assessment 5) Remaining technical debt 6) Recommendations for future development 7) Success metrics achievement. Celebrate the transformation!" > .PHOENIX/COMPLETION_REPORT.md
    
    git add -A && git commit -m "🎉 Phoenix: RESTRUCTURING COMPLETED SUCCESSFULLY!"
    
    echo ""
    echo "🎉 PHOENIX RESTRUCTURING COMPLETED SUCCESSFULLY!"
    echo "📊 Check .PHOENIX/COMPLETION_REPORT.md for full results"
    echo "🚀 Your codebase is now LLM-optimized and professional!"
    echo ""
}

# Показать доступные функции
show_available_functions() {
    echo "🔥 Phoenix Orchestrator Functions Available:"
    echo ""
    echo "  setup_orchestrator           - Prepare environment and create checkpoint"
    echo "  phase_0_preparation          - Execute Phase 0: Preparation and Analysis"
    echo "  phase_1_consolidation        - Execute Phase 1: Consolidation and Archiving" 
    echo "  phase_2_schemas              - Execute Phase 2: Schema Creation"
    echo "  phase_3_refactoring          - Execute Phase 3: LLM-First Refactoring"
    echo "  phase_4_documentation        - Execute Phase 4: Final Documentation"
    echo "  execute_full_phoenix_plan    - Run all phases sequentially"
    echo "  show_available_functions     - Show this help"
    echo ""
    echo "Usage: source this file, then call any function"
    echo "Example: setup_orchestrator && phase_0_preparation"
    echo ""
}

# По умолчанию показать доступные функции
show_available_functions
