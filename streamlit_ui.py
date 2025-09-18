#!/usr/bin/env python3
"""
Main entry point for the Streamlit UI application.
Run this file to start the document processing pipeline interface.

Usage:
    streamlit run streamlit_ui.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main Streamlit app
from ui.streamlit_app import main, add_sidebar

if __name__ == "__main__":
    # Ensure the outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Add sidebar
    add_sidebar()
    
    # Run main application
    main()