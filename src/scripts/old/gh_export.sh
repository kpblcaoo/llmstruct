#!/bin/bash
# GitHub Projects Export Helper Script
# Provides convenient commands for exporting llmstruct data to GitHub Projects

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPORT_SCRIPT="$PROJECT_ROOT/scripts/export_to_github_projects.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}GitHub Projects Export Helper${NC}"
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  check                    - Check GitHub CLI authentication"
    echo "  list-projects           - List available GitHub Projects" 
    echo "  preview <project_id>    - Preview what would be exported (dry-run)"
    echo "  export <project_id>     - Export all data to GitHub Project"
    echo "  export-tasks <project_id> - Export only tasks"
    echo "  export-ideas <project_id> - Export only ideas"
    echo "  filter-preview <project_id> --status proposed,in_progress - Preview with filters"
    echo ""
    echo "Options:"
    echo "  --owner <owner>         - Repository owner"
    echo "  --repo <repo>          - Repository name"
    echo "  --status <statuses>    - Filter by status (comma-separated)"
    echo "  --priority <priorities> - Filter by priority (comma-separated)"
    echo ""
    echo "Examples:"
    echo "  $0 check"
    echo "  $0 preview 1"
    echo "  $0 export 1 --owner kpblcaoo --repo llmstruct"
    echo "  $0 export-tasks 1 --status proposed,in_progress"
}

check_gh_cli() {
    echo -e "${BLUE}🔍 Checking GitHub CLI...${NC}"
    
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) not found. Please install it first.${NC}"
        echo "Installation: https://cli.github.com/"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI not authenticated. Please run 'gh auth login'${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
    gh auth status
}

list_projects() {
    echo -e "${BLUE}📋 Listing GitHub Projects...${NC}"
    
    local owner_flag=""
    local repo_flag=""
    
    # Parse additional arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --owner)
                owner_flag="--owner $2"
                shift 2
                ;;
            --repo)
                repo_flag="--repo $2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    gh projects list $owner_flag $repo_flag --format json | jq -r '.[] | "\(.number): \(.title) (\(.visibility))"' 2>/dev/null || {
        gh projects list $owner_flag $repo_flag
    }
}

run_export() {
    local command="$1"
    local project_id="$2"
    shift 2
    
    if [[ -z "$project_id" ]]; then
        echo -e "${RED}❌ Project ID is required${NC}"
        print_usage
        exit 1
    fi
    
    local args=()
    local dry_run_flag=""
    
    case "$command" in
        "preview"|"filter-preview")
            dry_run_flag="--dry-run"
            ;;
        "export"|"export-tasks"|"export-ideas")
            dry_run_flag="--execute"
            ;;
    esac
    
    case "$command" in
        "export-tasks"|"filter-preview")
            args+=("--tasks-only")
            ;;
        "export-ideas")
            args+=("--ideas-only")
            ;;
    esac
    
    # Parse additional arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --owner)
                args+=("--owner" "$2")
                shift 2
                ;;
            --repo)
                args+=("--repo" "$2")
                shift 2
                ;;
            --status)
                IFS=',' read -ra statuses <<< "$2"
                args+=("--status" "${statuses[@]}")
                shift 2
                ;;
            --priority)
                IFS=',' read -ra priorities <<< "$2"
                args+=("--priority" "${priorities[@]}")
                shift 2
                ;;
            *)
                echo -e "${YELLOW}⚠️  Unknown option: $1${NC}"
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}🚀 Running export command...${NC}"
    echo "Command: python $EXPORT_SCRIPT $project_id $dry_run_flag ${args[*]}"
    echo ""
    
    cd "$PROJECT_ROOT"
    python "$EXPORT_SCRIPT" "$project_id" $dry_run_flag "${args[@]}"
}

# Main command processing
case "${1:-}" in
    "check")
        check_gh_cli
        ;;
    "list-projects")
        shift
        check_gh_cli
        list_projects "$@"
        ;;
    "preview")
        shift
        check_gh_cli
        run_export "preview" "$@"
        ;;
    "filter-preview")
        shift
        check_gh_cli
        run_export "filter-preview" "$@"
        ;;
    "export")
        shift
        check_gh_cli
        run_export "export" "$@"
        ;;
    "export-tasks")
        shift
        check_gh_cli
        run_export "export-tasks" "$@"
        ;;
    "export-ideas")
        shift
        check_gh_cli
        run_export "export-ideas" "$@"
        ;;
    "")
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        print_usage
        exit 1
        ;;
esac
