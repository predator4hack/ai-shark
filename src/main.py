"""Main entry point for the VC Document Analyzer Streamlit application."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from config.settings import settings


def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(
        page_title=settings.APP_NAME,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 VC Document Analyzer")
    st.markdown("AI-powered pitch deck analysis for venture capital professionals")
    
    # Placeholder for the main application
    st.info("🚧 Application setup complete! Ready for implementation of core features.")
    
    # Display configuration status
    with st.expander("Configuration Status"):
        st.write("**API Configuration:**")
        api_configured = bool(settings.GOOGLE_API_KEY)
        st.write(f"- Google API Key: {'✅ Configured' if api_configured else '❌ Not configured'}")
        
        st.write("**Application Settings:**")
        st.write(f"- Max file size: {settings.MAX_FILE_SIZE_MB} MB")
        st.write(f"- Supported formats: {', '.join(settings.SUPPORTED_FORMATS)}")
        st.write(f"- Output directory: {settings.OUTPUT_DIR}")


if __name__ == "__main__":
    main()