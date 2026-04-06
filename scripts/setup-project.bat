@echo off
REM Payverse Project Setup Script for Windows
REM Run this after cloning the repository for the first time

echo ==========================================
echo Welcome to Payverse Development Setup
echo ==========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo ERROR: Not a git repository
    pause
    exit /b 1
)

REM 1. Install git hooks
echo Step 1/6: Installing Git hooks...
call scripts\setup-hooks.bat
echo Git hooks installed.
echo.

REM 2. Check Python
echo Step 2/6: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
python --version
echo.

REM 3. Create virtual environment
echo Step 3/6: Setting up Python virtual environment...
if exist "backend\venv" (
    echo Virtual environment already exists, skipping...
) else (
    cd backend
    python -m venv venv
    echo Virtual environment created at backend\venv
    cd ..
)
echo.

REM 4. Install dependencies
echo Step 4/6: Installing Python dependencies...
cd backend
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
) else if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
)
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed.
cd ..
echo.

REM 5. Environment file
echo Step 5/6: Environment configuration...
if exist "backend\.env" (
    echo .env file already exists, skipping...
) else (
    copy backend\.env.example backend\.env
    echo .env file created from example
    echo IMPORTANT: Edit backend\.env and add your actual secret values!
    echo Never commit the .env file!
)
echo.

REM 6. Git configuration check
echo Step 6/6: Checking Git configuration...
for /f "tokens=*" %%i in ('git config user.name') do set GIT_NAME=%%i
for /f "tokens=*" %%i in ('git config user.email') do set GIT_EMAIL=%%i

if "%GIT_NAME%"=="" (
    echo Git user.name not configured.
    echo Please run:
    echo   git config --global user.name "Your Name"
    echo   git config --global user.email "your.email@example.com"
) else (
    echo Git user: %GIT_NAME% <%GIT_EMAIL%>
    echo Git configuration OK.
)
echo.

echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Review .env file and update with your configuration
echo 2. Read CONTRIBUTING.md for Git workflow guidelines
echo 3. Create your first feature branch:
echo    git checkout -b feature/your-feature
echo.
echo Happy coding!
echo.
pause
