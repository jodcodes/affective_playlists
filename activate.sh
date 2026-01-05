#!/bin/bash
# affective_playlists Environment Activation Script
# Activates virtual environment and installs dependencies if needed

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}affective_playlists - Environment Activation${NC}"
echo ""

# Create venv if needed
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${RED}✗ Failed to activate environment${NC}"
    exit 1
fi

source "$VENV_PATH/bin/activate"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH}"

# Check if dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import requests, dotenv" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
    pip install -q --upgrade pip
    pip install -q -r "$PROJECT_ROOT/requirements.txt"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

echo ""
echo -e "${GREEN}✓ affective_playlists environment ready!${NC}"
echo ""
echo "Available commands:"
echo "  affective-playlists                 # Interactive menu"
echo "  affective-playlists temperament     # AI-based Playlist Temperament Analysis"
echo "  affective-playlists enrich          # Metadata Filling and Enrichment"
echo "  affective-playlists organize        # Playlist Organization by Genre"
echo ""
echo "  python main.py [command]            # Alternative: use python main.py"
echo ""
echo "Options:"
echo "  affective-playlists -v              # Verbose logging"
echo "  affective-playlists --help          # Show help"
echo "  affective-playlists --version       # Show version"
echo ""
