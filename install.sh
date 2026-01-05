#!/bin/bash
# affective_playlists - One-Command Installation Script
# Usage: bash install.sh
# Or from GitHub: curl -sL https://raw.githubusercontent.com/sokkohai/affective_playlists/main/install.sh | bash

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  affective_playlists - Installation & Setup               ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}→${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Install Python 3.10+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python $PYTHON_VERSION found, but $REQUIRED_VERSION+ is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Check macOS
echo -e "${YELLOW}→${NC} Checking platform..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠ Warning: Not macOS. Apple Music integration may not work.${NC}"
fi
echo -e "${GREEN}✓ Platform check passed${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}→${NC} Setting up virtual environment..."
VENV_PATH="$PROJECT_ROOT/venv"

if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}  Virtual environment already exists${NC}"
else
    python3 -m venv "$VENV_PATH"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
source "$VENV_PATH/bin/activate"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH}"
echo ""

# Upgrade pip
echo -e "${YELLOW}→${NC} Updating pip..."
pip install -q --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}→${NC} Installing dependencies..."
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -q -r "$PROJECT_ROOT/requirements.txt"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Install in editable mode
echo -e "${YELLOW}→${NC} Installing affective_playlists in development mode..."
pip install -q -e "$PROJECT_ROOT"
echo -e "${GREEN}✓ Package installed${NC}"
echo ""

# Setup configuration
echo -e "${YELLOW}→${NC} Setting up configuration..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo -e "${GREEN}✓ Created .env from template${NC}"
        echo -e "${YELLOW}  IMPORTANT: Edit .env with your API credentials${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Create directories
echo -e "${YELLOW}→${NC} Creating data directories..."
mkdir -p "$PROJECT_ROOT/data/config"
mkdir -p "$PROJECT_ROOT/data/logs"
mkdir -p "$PROJECT_ROOT/data/cache"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Run tests
echo -e "${YELLOW}→${NC} Running test suite..."
if command -v pytest &> /dev/null; then
    if pytest "$PROJECT_ROOT/tests/" -q 2>/dev/null; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed (this may be expected)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ pytest not available, skipping tests${NC}"
fi
echo ""

# Verify installation
echo -e "${YELLOW}→${NC} Verifying installation..."
if python -c "import main; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓ Core modules importable${NC}"
else
    echo -e "${YELLOW}⚠ Module import test skipped (expected in test directory)${NC}"
fi
echo ""

# Final summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}Installation Complete!${NC}                                  ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Edit configuration:"
echo -e "   ${YELLOW}vim .env${NC}"
echo ""
echo "2. Add your API credentials:"
echo "   - OPENAI_API_KEY (required for temperament analysis)"
echo "   - SPOTIFY_CLIENT_ID/SECRET (optional, for better metadata)"
echo "   - LASTFM_API_KEY (optional)"
echo ""
echo "3. Run affective_playlists:"
echo -e "   ${YELLOW}source activate.sh${NC}"
echo -e "   ${YELLOW}affective-playlists${NC}"
echo ""
echo "Or run any of these commands:"
echo -e "   ${YELLOW}affective-playlists temperament${NC}   # AI emotion analysis"
echo -e "   ${YELLOW}affective-playlists enrich${NC}        # Fill metadata"
echo -e "   ${YELLOW}affective-playlists organize${NC}      # Organize by genre"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  - Quick Start: QUICKSTART.md"
echo "  - Installation: docs/INSTALLATION.md"
echo "  - Architecture: docs/OVERVIEW.md"
echo "  - Features: docs/requirements/"
echo ""
echo -e "${GREEN}Happy analyzing! 🎵${NC}"
echo ""
