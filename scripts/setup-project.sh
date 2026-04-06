#!/bin/bash
# Payverse Project Setup Script
# Run this after cloning the repository for the first time

set -e  # Exit on error

echo "=========================================="
echo "🎉 Welcome to Payverse Development Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    exit 1
fi

# 1. Install git hooks
echo "📦 Step 1/6: Installing Git hooks..."
./scripts/setup-hooks.sh
echo -e "${GREEN}✓ Git hooks installed${NC}"
echo ""

# 2. Set up Python virtual environment
echo "🐍 Step 2/6: Setting up Python virtual environment..."
if [ -d "backend/venv" ] || [ -d "backend/.venv" ]; then
    echo "  Virtual environment already exists, skipping..."
else
    cd backend
    python3 -m venv venv
    echo "  Virtual environment created at backend/venv"
    cd ..
fi
echo -e "${GREEN}✓ Python virtual environment ready${NC}"
echo ""

# 3. Install dependencies
echo "📚 Step 3/6: Installing Python dependencies..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
cd ..
echo ""

# 4. Set up pre-commit framework (optional but recommended)
echo "🔍 Step 4/6: Setting up pre-commit framework..."
cd backend
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✓ pre-commit hooks installed${NC}"
else
    echo "  pre-commit not found, skipping..."
fi
cd ..
echo ""

# 5. Configure git (if not already)
echo "⚙️  Step 5/6: Checking Git configuration..."
CURRENT_NAME=$(git config user.name)
CURRENT_EMAIL=$(git config user.email)

if [ -z "$CURRENT_NAME" ] || [ -z "$CURRENT_EMAIL" ]; then
    echo "  Git user not configured. Please run:"
    echo "  git config --global user.name 'Your Name'"
    echo "  git config --global user.email 'your.email@example.com'"
else
    echo "  Git user: $CURRENT_NAME <$CURRENT_EMAIL>"
    echo -e "${GREEN}✓ Git configuration OK${NC}"
fi
echo ""

# 6. Create environment file
echo "🔐 Step 6/6: Environment configuration..."
if [ -f "backend/.env" ]; then
    echo "  .env file already exists, skipping..."
else
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ .env file created from example${NC}"
    echo "  ⚠️  IMPORTANT: Edit backend/.env and add your actual secret values!"
    echo "  Never commit the .env file!"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review .env file and update with your configuration"
echo "2. Read CONTRIBUTING.md for Git workflow guidelines"
echo "3. Create your first feature branch:"
echo "   git checkout -b feature/your-feature"
echo ""
echo "Happy coding! 🚀"
echo ""
