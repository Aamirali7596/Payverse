#!/bin/bash
# Setup git hooks for PayVerse project

echo "Setting up pre-commit hook..."

if [ ! -d ".git/hooks" ]; then
    echo "Error: Not a git repository"
    exit 1
fi

cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✓ Pre-commit hook installed!"
echo ""
echo "The Security Guardian agent will scan your code before each commit."
echo "To bypass: git commit --no-verify"
