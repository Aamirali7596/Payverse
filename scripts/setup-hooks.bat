@echo off
REM Setup git hooks for PayVerse project

echo Setting up pre-commit hook...

if not exist ".git\hooks" (
    echo Error: Not a git repository
    pause
    exit /b 1
)

copy hooks\pre-commit .git\hooks\pre-commit
if errorlevel 1 (
    echo Failed to copy pre-commit hook
    pause
    exit /b 1
)

echo Success! Pre-commit hook installed.
echo.
echo The Security Guardian agent will scan your code before each commit.
echo To bypass: git commit --no-verify
echo.
pause
