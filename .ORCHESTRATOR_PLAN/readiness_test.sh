#!/bin/bash
# ТЕСТОВЫЕ КОМАНДЫ ДЛЯ ПРОВЕРКИ ГОТОВНОСТИ ОРКЕСТРАТОРА

echo "🔥 PHOENIX ORCHESTRATOR READINESS TEST"
echo "======================================"

# Переход в рабочую директорию
cd /home/sma/projects/llmstruct/llmstruct

# Активация виртуального окружения
echo "1. Activating virtual environment..."
source venv/bin/activate || { echo "❌ Failed to activate venv"; exit 1; }
echo "✅ Virtual environment activated"

# Проверка CLI
echo ""
echo "2. Testing llmstruct CLI..."
if llmstruct --help > /dev/null 2>&1; then
    echo "✅ llmstruct CLI is working"
else
    echo "❌ llmstruct CLI not working"
    exit 1
fi

# Тест простого query
echo ""
echo "3. Testing basic query functionality..."
if llmstruct query "Hello, test message" > /dev/null 2>&1; then
    echo "✅ Basic query works"
else
    echo "⚠️ Basic query failed - might need context or different approach"
fi

# Проверка git
echo ""
echo "4. Checking git status..."
git status --porcelain > /dev/null && echo "✅ Git repository ready" || { echo "❌ Git issues detected"; exit 1; }

# Проверка Python
echo ""
echo "5. Checking Python environment..."
python --version
echo "✅ Python ready"

# Проверка структуры проекта
echo ""
echo "6. Checking project structure..."
echo "Total Python files: $(find . -name "*.py" -not -path "./venv/*" | wc -l)"
echo "Bot files found: $(find . -name "*bot*.py" -not -path "./venv/*" | wc -l)"
echo "Current directory: $(pwd)"

# Проверка доступного места
echo ""
echo "7. Checking disk space..."
df -h . | tail -1 | awk '{print "Available space: " $4}'

# Проверка памяти
echo ""
echo "8. Checking system resources..."
free -h | grep "Mem:" | awk '{print "Available RAM: " $7}'

echo ""
echo "🎯 READINESS TEST COMPLETED"
echo ""
echo "If all checks passed, you can proceed with:"
echo "source .ORCHESTRATOR_PLAN/quick_commands.sh"
echo "execute_full_phoenix_plan"
echo ""
echo "Or run phases individually:"
echo "setup_orchestrator"
echo "phase_0_preparation"
echo "# ... and so on"
