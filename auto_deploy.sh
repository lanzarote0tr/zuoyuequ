#!/bin/bash

# --- Configuration ---
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BRANCH="main"
CHECK_INTERVAL=10   # in seconds
LOG_FILE="/tmp/auto_deploy_last_run.log" # Temp file to capture output reliably

# Fix git safety
git config --global --add safe.directory "$PROJECT_DIR"

# Ensure we have a proper terminal type for Docker output
export TERM=xterm-256color

cd "$PROJECT_DIR" || { echo "ERROR: Directory not found: $PROJECT_DIR"; exit 1; }

echo "Starting Auto-Deploy (Single 'Up' Mode)..."
echo "Watching branch: $BRANCH"
echo "Project Dir: $PROJECT_DIR"


while true; do
    git pull origin $BRANCH
    sleep $CHECK_INTERVAL
done