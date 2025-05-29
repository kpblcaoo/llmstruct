#!/bin/bash

# 🚀 FULL PROJECT ROLLOUT SCRIPT
# Полный автоматизированный выкат проекта на GitHub

set -e

echo "🚀 Starting AI-Dogfooding Project Rollout..."
echo "=================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[$1/6]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_step 1 "Checking dependencies..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
    fi
    
    # Проверка Git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
    fi
    
    # Проверка GitHub token (автоматически через setup скрипт)
    if [ ! -f "scripts/setup_github_token.sh" ]; then
        print_error "setup_github_token.sh not found!"
    fi
    
    # Автоматическая настройка GitHub токена
    print_info "Setting up GitHub token..."
    ./scripts/setup_github_token.sh
    if [ $? -ne 0 ]; then
        print_error "GitHub token setup failed!"
    fi
    
    # Загрузка .env для проверки
    if [ -f ".env" ]; then
        source .env
    fi
    
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN is still not available after setup!"
    fi
    
    # Проверка requests library
    if ! python3 -c "import requests" 2>/dev/null; then
        print_warning "Installing requests library..."
        pip install requests
    fi
    
    print_success "All dependencies are ready"
}

# Валидация данных
validate_data() {
    print_step 2 "Validating epic data..."
    
    if [ ! -f "epics/epics_data.json" ]; then
        print_error "epics/epics_data.json not found!"
    fi
    
    if [ ! -f "scripts/validate_epics.py" ]; then
        print_error "scripts/validate_epics.py not found!"
    fi
    
    python3 scripts/validate_epics.py
    if [ $? -ne 0 ]; then
        print_error "Epic validation failed!"
    fi
    
    print_success "Epic data is valid"
}

# Создание GitHub Issues
create_github_issues() {
    print_step 3 "Creating GitHub issues..."
    
    if [ ! -f "scripts/create_github_issues.py" ]; then
        print_error "scripts/create_github_issues.py not found!"
    fi
    
    # Исправление bug в скрипте (owner/repo в URL)
    python3 scripts/create_github_issues.py
    if [ $? -ne 0 ]; then
        print_error "Failed to create GitHub issues!"
    fi
    
    print_success "GitHub issues created successfully"
}

# Создание AI-ветки
create_ai_branch() {
    print_step 4 "Creating AI development branch..."
    
    # Проверка что мы не в ai-ветке
    current_branch=$(git branch --show-current)
    if [[ $current_branch == ai/* ]]; then
        print_warning "Already in AI branch: $current_branch"
        return
    fi
    
    # Создание новой ai-ветки
    branch_name="ai/dogfood-implementation-$(date +%Y%m%d-%H%M)"
    git checkout -b $branch_name
    
    print_success "Created AI branch: $branch_name"
}

# Коммит новых файлов
commit_project_files() {
    print_step 5 "Committing project files..."
    
    # Добавление всех созданных файлов
    git add epics/
    git add .github/
    git add docs/
    git add scripts/
    
    # Проверка есть ли что коммитить
    if git diff --cached --quiet; then
        print_warning "No new files to commit"
        return
    fi
    
    # Коммит
    git commit -m "🚀 AI-Dogfooding Project Setup

✅ Created complete epic structure:
- 4 EPICs with 19 detailed tasks
- GitHub issue templates
- Automation scripts
- Documentation

🎯 Ready for AI-powered development!

[AI-Dogfooding] [Project-Setup] [Epic-Structure]"
    
    print_success "Project files committed"
}

# Финальная информация
show_next_steps() {
    print_step 6 "Project rollout complete!"
    
    echo ""
    echo "🎉 AI-DOGFOODING PROJECT READY!"
    echo "================================"
    echo ""
    echo "📋 WHAT WAS CREATED:"
    echo "  ✅ 4 EPICs with 19 detailed tasks"
    echo "  ✅ GitHub issue templates"
    echo "  ✅ Automation scripts"
    echo "  ✅ Complete documentation"
    echo "  ✅ AI development branch"
    echo ""
    echo "🚀 NEXT STEPS:"
    echo "  1. Check GitHub issues: https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/issues"
    echo "  2. Start first epic: python dogfood.py --epic 1 --task 1"
    echo "  3. Monitor progress: cat epics/README.md"
    echo ""
    echo "🎯 CURRENT BRANCH: $(git branch --show-current)"
    echo "🔗 PROJECT STATUS: https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/projects"
    echo ""
    print_success "Ready for AI-augmented development!"
}

# Основной процесс
main() {
    check_dependencies
    validate_data
    create_github_issues
    create_ai_branch
    commit_project_files
    show_next_steps
}

# Обработка ошибок
trap 'echo -e "${RED}❌ Script failed at line $LINENO${NC}"' ERR

# Запуск
main "$@" 