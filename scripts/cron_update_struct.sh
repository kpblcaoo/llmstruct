#!/bin/bash
# Cron script for periodic struct.json updates
# Add to crontab: */30 * * * * /path/to/this/script.sh

PROJECT_DIR="/home/kpblc/projects/github/llmstruct"
SCRIPT_PATH="$PROJECT_DIR/scripts/auto_update_struct.py"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Check if update is needed
if python3 "$SCRIPT_PATH" --check-only --quiet; then
    echo "$(date): struct.json is up to date"
else
    echo "$(date): Updating struct.json"
    python3 "$SCRIPT_PATH" --quiet
fi
