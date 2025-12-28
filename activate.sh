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
echo "  python main.py              # Interactive menu"
echo "  python main.py --list       # List all subrepos"
echo "  python main.py 4tempers     # Run 4tempers"
echo "  python main.py metad_enr    # Run metadata enrichment"
echo "  python main.py plsort       # Run playlist organizer"
echo ""
