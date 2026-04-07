#!/bin/bash
# Setup git hooks for TaxionLab project

echo "Setting up pre-commit and pre-push hooks..."

if [ ! -d ".git/hooks" ]; then
    echo "Error: Not a git repository"
    exit 1
fi

# Install pre-commit hook
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "✓ Pre-commit hook installed!"

# Install pre-push hook
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
echo "✓ Pre-push hook installed!"

echo ""
echo "Git hooks are now active!"
echo ""
echo "Pre-commit: Runs the Security Guardian agent to scan code before each commit."
echo "Pre-push: Runs comprehensive checks (formatting, type-checking, tests) before pushing to protected branches."
echo ""
echo "To bypass hooks temporarily (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "To run hooks on all files manually:"
echo "  pre-commit run --all-files"
