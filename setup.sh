#!/bin/bash
# MetaWipe - Linux/macOS Setup Script
# Filename: setup.sh
# This script helps you install all dependencies on Linux/macOS

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   PERFECT METADATA CLEANER - AUTO SETUP & EXECUTION      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
else
    echo -e "${RED}Unsupported OS. This script works on Linux and macOS.${NC}"
    exit 1
fi

echo -e "${CYAN}Detected OS: $OS${NC}"
echo ""

# Step 1: Install system dependencies
echo -e "${YELLOW}[1/4] Installing system dependencies...${NC}"
if [ "$OS" == "linux" ]; then
    if command -v apt-get &> /dev/null; then
        echo "Using apt-get..."
        sudo apt-get update -qq
        sudo apt-get install -y libimage-exiftool-perl ffmpeg python3-pip
    elif command -v yum &> /dev/null; then
        echo "Using yum..."
        sudo yum install -y perl-Image-ExifTool ffmpeg python3-pip
    else
        echo -e "${RED}Package manager not supported. Install manually:${NC}"
        echo "  - exiftool (libimage-exiftool-perl)"
        echo "  - ffmpeg"
        exit 1
    fi
elif [ "$OS" == "mac" ]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}Homebrew not found. Install from https://brew.sh${NC}"
        exit 1
    fi
    echo "Using Homebrew..."
    brew install exiftool ffmpeg python3
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

# Step 2: Install Python packages
echo -e "${YELLOW}[2/4] Installing Python packages...${NC}"
pip3 install --upgrade pip --quiet
pip3 install pillow pypdf python-docx mutagen openpyxl --quiet
echo -e "${GREEN}✓ Python packages installed${NC}"
echo ""

# Step 3: Verify installations
echo -e "${YELLOW}[3/4] Verifying installations...${NC}"

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 - NOT FOUND"
        return 1
    fi
}

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 - NOT FOUND"
        return 1
    fi
}

all_ok=true
check_command exiftool || all_ok=false
check_command ffmpeg || all_ok=false
check_command python3 || all_ok=false
check_python_package PIL || all_ok=false
check_python_package pypdf || all_ok=false
check_python_package docx || all_ok=false
check_python_package mutagen || all_ok=false
check_python_package openpyxl || all_ok=false

if [ "$all_ok" = false ]; then
    echo ""
    echo -e "${RED}Some dependencies are missing. Please install them manually.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies verified${NC}"
echo ""

# Step 4: Run the cleaner
echo -e "${YELLOW}[4/4] Ready to clean metadata...${NC}"
echo ""

# Ask for target directory
read -p "Enter directory to clean (default: current directory): " TARGET_DIR
TARGET_DIR=${TARGET_DIR:-.}

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Directory not found: $TARGET_DIR${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Target directory: $TARGET_DIR${NC}"
echo ""

# Show options
echo -e "${YELLOW}Choose cleaning mode:${NC}"
echo "  1) MAXIMUM (backup + re-encode videos + normalize timestamps) [RECOMMENDED]"
echo "  2) BALANCED (backup + copy videos + normalize timestamps)"
echo "  3) QUICK (backup + copy videos)"
echo "  4) DRY RUN (preview only, no changes)"
echo "  5) CUSTOM (choose your own options)"
echo ""
read -p "Enter choice [1-5] (default: 1): " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        echo -e "${GREEN}Using MAXIMUM mode (slowest, most thorough)${NC}"
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\" --backup --reencode-videos --normalize-time --verbose"
        ;;
    2)
        echo -e "${GREEN}Using BALANCED mode (fast, very effective)${NC}"
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\" --backup --normalize-time --verbose"
        ;;
    3)
        echo -e "${GREEN}Using QUICK mode (fastest)${NC}"
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\" --backup --verbose"
        ;;
    4)
        echo -e "${GREEN}Using DRY RUN mode (preview only)${NC}"
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\" --dry-run"
        ;;
    5)
        echo ""
        read -p "Create backups? (y/n, default: y): " BACKUP
        read -p "Re-encode videos? (y/n, default: n): " REENCODE
        read -p "Normalize timestamps? (y/n, default: y): " NORMALIZE
        read -p "Verbose output? (y/n, default: y): " VERBOSE
        
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\""
        [[ "${BACKUP:-y}" == "y" ]] && CMD="$CMD --backup"
        [[ "${REENCODE:-n}" == "y" ]] && CMD="$CMD --reencode-videos"
        [[ "${NORMALIZE:-y}" == "y" ]] && CMD="$CMD --normalize-time"
        [[ "${VERBOSE:-y}" == "y" ]] && CMD="$CMD --verbose"
        
        echo -e "${GREEN}Using CUSTOM mode${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice. Using MAXIMUM mode.${NC}"
        CMD="python3 clean_metadata.py --path \"$TARGET_DIR\" --backup --reencode-videos --normalize-time --verbose"
        ;;
esac

echo ""
echo -e "${CYAN}Command to execute:${NC}"
echo "$CMD"
echo ""
read -p "Press ENTER to start cleaning or Ctrl+C to cancel..."
echo ""

# Execute the command
eval $CMD

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✓ METADATA CLEANING COMPLETED!                 ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Your files are now clean of metadata and digital footprints!${NC}"
    echo -e "Backup location: ${YELLOW}~/.metadata_cleaner/backups/${NC}"
    echo -e "Log location: ${YELLOW}~/.metadata_cleaner/logs/${NC}"
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           ✗ CLEANING FAILED OR INCOMPLETE                ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Check the log files for details: ~/.metadata_cleaner/logs/${NC}"
fi

exit $EXIT_CODE