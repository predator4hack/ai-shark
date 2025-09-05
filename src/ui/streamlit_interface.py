"""
Streamlit user interface components for the VC Document Analyzer.

This module contains reusable UI components and interface logic
for the Streamlit application.
"""

import streamlit as st
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from src.models.data_models import SlideImage, SlideAnalysis, ProcessingResult
from src.processors.document_processor import DocumentProcessor, DocumentProcessorError
from src.analyzers.gemini_analyzer import GeminiAnalyzer
from src.output.output_manager import OutputManager
from config.settings import settings


logger = logging.getLogger(__name__)


class StreamlitInterface:
    """Main interface class for the Streamlit application."""
    
    def __init__(self):
        """Initialize the Streamlit interface."""
        self.document_processor = None
        self.gemini_analyzer = None
        self.output_manager = None
    
    def render_file_upload_widget(self) -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
        """Render the file upload widget with validation.
        
        Returns:
            Uploaded file object or None if no file uploaded
        """
        uploaded_file = st.file_uploader(
            "Choose a pitch deck file",
            type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
            help=f"Supported formats: PDF, PPTX, PNG, JPG, JPEG. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded_file is not None:
            # Validate and display file information
            if self._validate_uploaded_file(uploaded_file):
                self._display_file_info(uploaded_file)
                return uploaded_file
        
        return None
    
    def _validate_uploaded_file(self, uploaded_file) -> bool:
        """Validate the uploaded file size and format.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            True if file is valid, False otherwise
        """
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            st.error(f"❌ File too large! Maximum size is {settings.MAX_FILE_SIZE_MB}MB. Your file is {file_size_mb:.1f}MB.")
            return False
        
        return True
    
    def _display_file_info(self, uploaded_file):
        """Display information about the uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
        """
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{file_size_mb:.1f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type)
    
    def show_progress(self, current: int, total: int, message: str) -> None:
        """Display progress indicator with message.
        
        Args:
            current: Current progress value
            total: Total progress value
            message: Progress message to display
        """
        progress_percentage = int((current / total) * 100) if total > 0 else 0
        
        # Use session state to maintain progress bar and status text
        if 'progress_bar' not in st.session_state:
            st.session_state.progress_bar = st.progress(0)
            st.session_state.status_text = st.empty()
        
        st.session_state.progress_bar.progress(progress_percentage)
        st.session_state.status_text.text(message)
    
    def display_results(self, analysis_results: List[SlideAnalysis], output_file_path: str) -> None:
        """Display the analysis results in a structured format.
        
        Args:
            analysis_results: List of slide analysis results
            output_file_path: Path to the saved output file
        """
        if not analysis_results:
            st.warning("No analysis results to display.")
            return
        
        # Display summary metrics
        self._display_summary_metrics(analysis_results)
        
        # Display download button
        self._display_download_button(output_file_path)
        
        # Display individual slide results
        self._display_slide_results(analysis_results)
    
    def _display_summary_metrics(self, results: List[SlideAnalysis]) -> None:
        """Display summary metrics for the analysis results.
        
        Args:
            results: List of slide analysis results
        """
        successful_slides = len([r for r in results if not r.errors])
        failed_slides = len(results) - successful_slides
        avg_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Slides", len(results))
        with col2:
            st.metric("Successful", successful_slides)
        with col3:
            st.metric("Failed", failed_slides, delta=None if failed_slides == 0 else f"-{failed_slides}")
        with col4:
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
    
    def _display_download_button(self, output_file_path: str) -> None:
        """Display download button for the output file.
        
        Args:
            output_file_path: Path to the output file
        """
        if output_file_path and Path(output_file_path).exists():
            with open(output_file_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Full Analysis (Markdown)",
                    data=f.read(),
                    file_name=Path(output_file_path).name,
                    mime="text/markdown",
                    use_container_width=True
                )
    
    def _display_slide_results(self, results: List[SlideAnalysis]) -> None:
        """Display individual slide analysis results.
        
        Args:
            results: List of slide analysis results
        """
        st.subheader("Slide-by-Slide Analysis")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            show_errors_only = st.checkbox("Show only slides with errors")
        with col2:
            show_metadata = st.checkbox("Show processing metadata", value=False)
        
        # Filter results
        display_results = results
        if show_errors_only:
            display_results = [r for r in results if r.errors]
        
        if not display_results:
            st.info("No slides match the current filter criteria.")
            return
        
        # Display slides
        for analysis in display_results:
            self._display_single_slide(analysis, show_metadata)
    
    def _display_single_slide(self, analysis: SlideAnalysis, show_metadata: bool = False) -> None:
        """Display a single slide analysis result.
        
        Args:
            analysis: Slide analysis result
            show_metadata: Whether to show processing metadata
        """
        slide_title = f"Slide {analysis.slide_number}"
        if analysis.heading:
            slide_title += f": {analysis.heading}"
        
        with st.expander(slide_title, expanded=bool(analysis.errors)):
            # Show errors prominently if any
            if analysis.errors:
                st.error("⚠️ Processing Errors:")
                for error in analysis.errors:
                    st.write(f"• {error}")
                st.divider()
            
            # Slide content
            if analysis.heading:
                st.subheader(analysis.heading)
            
            if analysis.image_descriptions:
                st.write("**Visual Elements:**")
                for i, desc in enumerate(analysis.image_descriptions, 1):
                    st.write(f"{i}. {desc}")
            
            if analysis.chart_table_data:
                st.write("**Charts and Tables:**")
                for i, data in enumerate(analysis.chart_table_data, 1):
                    st.write(f"{i}. {data}")
            
            if analysis.interpretation:
                st.write("**Interpretation:**")
                st.write(analysis.interpretation)
            
            # Metadata (optional)
            if show_metadata:
                st.write("**Processing Metadata:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Confidence: {analysis.confidence_score:.2f}")
                with col2:
                    st.write(f"Processing Time: {analysis.processing_time:.2f}s")
    
    def show_error(self, error_message: str) -> None:
        """Display an error message to the user.
        
        Args:
            error_message: Error message to display
        """
        st.error(f"❌ {error_message}")
    
    def show_success(self, message: str) -> None:
        """Display a success message to the user.
        
        Args:
            message: Success message to display
        """
        st.success(f"✅ {message}")
    
    def show_info(self, message: str) -> None:
        """Display an info message to the user.
        
        Args:
            message: Info message to display
        """
        st.info(f"ℹ️ {message}")
    
    def show_warning(self, message: str) -> None:
        """Display a warning message to the user.
        
        Args:
            message: Warning message to display
        """
        st.warning(f"⚠️ {message}")


class ProgressTracker:
    """Helper class for tracking and displaying progress during processing."""
    
    def __init__(self):
        """Initialize the progress tracker."""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.current_step = 0
        self.total_steps = 100
    
    def update(self, step: int, message: str) -> None:
        """Update progress with step and message.
        
        Args:
            step: Current step (0-100)
            message: Status message
        """
        self.current_step = step
        self.progress_bar.progress(step)
        self.status_text.text(message)
    
    def increment(self, increment: int, message: str) -> None:
        """Increment progress by a certain amount.
        
        Args:
            increment: Amount to increment
            message: Status message
        """
        self.current_step = min(100, self.current_step + increment)
        self.update(self.current_step, message)
    
    def complete(self, message: str = "Complete!") -> None:
        """Mark progress as complete.
        
        Args:
            message: Completion message
        """
        self.update(100, message)
    
    def clear(self) -> None:
        """Clear the progress indicators."""
        self.progress_bar.empty()
        self.status_text.empty()


class SidebarManager:
    """Manages the sidebar content and configuration display."""
    
    @staticmethod
    def render_sidebar() -> None:
        """Render the complete sidebar with all sections."""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Status section
            SidebarManager._render_api_status()
            st.divider()
            
            # Application Settings section
            SidebarManager._render_app_settings()
            st.divider()
            
            # Help and Information section
            SidebarManager._render_help_section()
            
            # Footer
            st.divider()
            st.caption("VC Document Analyzer v1.0")
            st.caption("Powered by Google Gemini AI")
    
    @staticmethod
    def _render_api_status() -> None:
        """Render the API status section."""
        st.subheader("API Status")
        api_configured = bool(settings.GOOGLE_API_KEY)
        
        if api_configured:
            st.success("✅ Google API Key configured")
            
            # Test API connection
            if st.button("🔗 Test API Connection"):
                with st.spinner("Testing connection..."):
                    try:
                        analyzer = GeminiAnalyzer()
                        if analyzer.test_connection():
                            st.success("✅ API connection successful")
                        else:
                            st.error("❌ API connection failed")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        else:
            st.error("❌ Google API Key not configured")
            st.info("💡 Set the GOOGLE_API_KEY environment variable")
    
    @staticmethod
    def _render_app_settings() -> None:
        """Render the application settings section."""
        st.subheader("Application Settings")
        st.write(f"**Max File Size:** {settings.MAX_FILE_SIZE_MB} MB")
        st.write(f"**Supported Formats:** {', '.join(settings.SUPPORTED_FORMATS)}")
        st.write(f"**Output Directory:** {settings.OUTPUT_DIR}")
    
    @staticmethod
    def _render_help_section() -> None:
        """Render the help and information section."""
        st.subheader("📚 Help & Information")
        
        with st.expander("Supported File Formats"):
            st.write("""
            - **PDF**: Multi-page pitch decks
            - **PPTX**: PowerPoint presentations  
            - **PNG/JPG**: Individual slide images
            """)
        
        with st.expander("How It Works"):
            st.write("""
            1. **Upload** your pitch deck file
            2. **Extract** slides as images
            3. **Analyze** each slide with AI
            4. **Generate** structured analysis
            5. **Download** results as Markdown
            """)
        
        with st.expander("Tips for Best Results"):
            st.write("""
            - Use high-quality, clear images
            - Ensure text is readable
            - Keep file size under 10MB
            - PDF and PPTX work best for multi-slide decks
            """)