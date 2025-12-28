#!/bin/bash
# plMetaTemp Setup Script
# Unified setup for 4tempers, metad_enr, and plsort

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         plMetaTemp - Unified Setup Script                   ║${NC}"
echo -e "${BLUE}║  4tempers | metad_enr | plsort                             ║${NC}"
echo -e "${BLUE}╚═════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step headers
print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}➜ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
print_step "Checking Python Installation"
if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment if requested
print_step "Virtual Environment Setup"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
print_step "Upgrading pip"
python3 -m pip install --quiet --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
print_step "Installing Dependencies"
echo -e "${YELLOW}Installing packages from requirements.txt...${NC}"
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""
echo "Installed packages:"
pip list | grep -E "(requests|python-dotenv)" || true

# Setup environment file
print_step "Environment Configuration"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Edit .env with your API keys:${NC}"
    echo "  - OPENAI_API_KEY (required for 4tempers)"
    echo "  - SPOTIFY_CLIENT_ID/SECRET (optional)"
    echo "  - LASTFM_API_KEY (optional)"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
    echo -e "${YELLOW}Review .env for any missing credentials${NC}"
fi

# Create necessary directories
print_step "Creating Directories"
DIRS=("logs" "cache" "data")
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✓ Created $dir/$(NC)"
    else
        echo -e "${GREEN}✓ $dir/ already exists${NC}"
    fi
done

# Check subrepo directories
print_step "Verifying Subproject Directories"
SUBREPOS=("4tempers" "metad_enr" "plsort")
for subrepo in "${SUBREPOS[@]}"; do
    if [ -d "$subrepo" ]; then
        echo -e "${GREEN}✓ $subrepo/$(NC)"
    else
        echo -e "${RED}✗ $subrepo/ not found${NC}"
        exit 1
    fi
done

# Verify shared modules
print_step "Verifying Shared Modules"
SHARED_MODULES=("shared/__init__.py" "shared/apple_music.py" "shared/normalizer.py" "shared/logger.py")
for module in "${SHARED_MODULES[@]}"; do
    if [ -f "$module" ]; then
        echo -e "${GREEN}✓ $module${NC}"
    else
        echo -e "${RED}✗ $module not found${NC}"
        exit 1
    fi
done

# Test imports
print_step "Testing Module Imports"
python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '.')

try:
    from shared import AppleMusicInterface, TextNormalizer, setup_logger
    print("✓ Successfully imported from shared module")
except ImportError as e:
    print(f"✗ Failed to import from shared: {e}")
    sys.exit(1)

try:
    import logging
    logger = setup_logger("test")
    print("✓ Logger setup successful")
except Exception as e:
    print(f"✗ Logger setup failed: {e}")
    sys.exit(1)
PYTHON_TEST

# Test Apple Music Access
print_step "Checking Apple Music Access"
if command_exists osascript; then
    echo -e "${YELLOW}Testing AppleScript access to Music.app...${NC}"
    if osascript -e 'tell application "Music" to return name' >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Apple Music app is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Apple Music app not accessible${NC}"
        echo -e "${YELLOW}  - Ensure Music.app is installed and running${NC}"
        echo -e "${YELLOW}  - Grant AppleScript permissions in System Preferences${NC}"
    fi
else
    echo -e "${RED}✗ osascript not found (macOS required)${NC}"
    exit 1
fi

# Print summary
print_step "Setup Summary"
echo ""
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo ""
echo "Next steps:"
echo ""
echo -e "${YELLOW}1. Edit .env with your credentials:${NC}"
echo "   vim .env"
echo ""
echo -e "${YELLOW}2. Run the main CLI:${NC}"
echo "   python main.py"
echo ""
echo -e "${YELLOW}3. Or run a specific subrepo:${NC}"
echo "   python main.py 4tempers"
echo "   python main.py metad_enr"
echo "   python main.py plsort"
echo ""
echo -e "${YELLOW}4. View the refactoring guide:${NC}"
echo "   cat REFACTORING_GUIDE.md"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
