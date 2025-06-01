#!/usr/bin/env bash
set -e

# Usage: ./scripts/check_code.sh [target_dir]
# Default: src/llmstruct

TARGET_DIR=${1:-src/llmstruct}

echo "🔍 Running flake8 (style/lint checks) on $TARGET_DIR ..."
flake8 "$TARGET_DIR"

echo "🔍 Running mypy (type checks) on $TARGET_DIR ..."
mypy "$TARGET_DIR"

echo "🔍 Running black (format check) on $TARGET_DIR ..."
black --check "$TARGET_DIR"

echo "🔍 Running isort (import order check) on $TARGET_DIR ..."
isort --check-only "$TARGET_DIR"

echo "✅ All checks passed!" 