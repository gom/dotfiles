#!/usr/bin/env bash

# Hook Name: check_git_status
# Event: pre-command

echo "🔄 Running Pre-Command Hook: Checking Git Status..."
git status -s
