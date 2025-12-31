#!/bin/bash
# Debug Launcher Script for AI-Shark Application
# This script helps you launch different components in debug mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI-Shark Application Debug Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please create a virtual environment first:${NC}"
    echo -e "  python3 -m venv .venv"
    echo -e "  source .venv/bin/activate"
    echo -e "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Some features may not work without environment variables.${NC}"
    echo ""
fi

# Menu for selecting what to debug
echo -e "${BLUE}Select what you want to debug:${NC}"
echo "1) Streamlit Application (Main UI)"
echo "2) Pitch Deck Processor"
echo "3) Analysis Pipeline"
echo "4) Run Tests"
echo "5) Start Remote Debug Server (attach from VSCode)"
echo "6) Exit"
echo ""
read -p "Enter your choice [1-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting Streamlit in debug mode...${NC}"
        echo -e "${YELLOW}Set breakpoints in VSCode and use 'Debug Streamlit App' configuration${NC}"
        echo -e "${YELLOW}Or run with debugpy for remote debugging:${NC}"
        python -m debugpy --listen 5678 --wait-for-client -m streamlit run src/ui/streamlit_app.py --server.port=8501
        ;;
    2)
        echo -e "${GREEN}Starting Pitch Deck Processor in debug mode...${NC}"
        echo -e "${YELLOW}Set breakpoints in VSCode and use 'Debug Pitch Deck Processor' configuration${NC}"
        python -m debugpy --listen 5678 --wait-for-client src/processors/pitch_deck_processor.py
        ;;
    3)
        echo -e "${GREEN}Starting Analysis Pipeline in debug mode...${NC}"
        read -p "Enter company directory path (e.g., outputs/company_name): " company_dir
        if [ -z "$company_dir" ]; then
            echo -e "${RED}Error: Company directory path is required${NC}"
            exit 1
        fi
        python -m debugpy --listen 5678 --wait-for-client -c "
from src.processors.analysis_pipeline import AnalysisPipeline
pipeline = AnalysisPipeline(company_dir='$company_dir', use_real_llm=True)
results = pipeline.run_pipeline()
print('Results:', results)
"
        ;;
    4)
        echo -e "${GREEN}Running tests in debug mode...${NC}"
        echo -e "${YELLOW}Use 'Debug Tests' configuration in VSCode or attach to port 5678${NC}"
        python -m debugpy --listen 5678 --wait-for-client -m pytest tests/ -v -s
        ;;
    5)
        echo -e "${GREEN}Starting remote debug server...${NC}"
        echo -e "${YELLOW}Connect from VSCode using 'Attach to Running Process' configuration${NC}"
        echo -e "${YELLOW}Server will wait for debugger on localhost:5678${NC}"
        python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m streamlit run src/ui/streamlit_app.py
        ;;
    6)
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac
