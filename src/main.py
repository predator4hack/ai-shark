"""Main entry point for the VC Document Analyzer Streamlit application."""

import streamlit as st
import tempfile
import time
from pathlib import Path
import sys
import logging
from typing import List, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from config.logging_config import setup_logging
from config.startup_validation import run_startup_validation
from src.models.data_models import SlideImage, SlideAnalysis, ProcessingResult
from src.processors.document_processor import DocumentProcessor, DocumentProcessorError
from src.analyzers.gemini_analyzer import GeminiAnalyzer
from src.output.output_manager import OutputManager
from src.ui.streamlit_interface import StreamlitInterface, ProgressTracker, SidebarManager


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class DocumentProcessingPipeline:
    """Main processing pipeline that integrates all components for document analysis.
    
    This class orchestrates the complete workflow from file upload to final output,
    with comprehensive error handling, progress tracking, and resource cleanup.
    """
    
    def __init__(self, ui: StreamlitInterface):
        """Initialize the processing pipeline.
        
        Args:
            ui: StreamlitInterface instance for user feedback
        """
        self.ui = ui
        self.progress = None
        self.temp_files = []
        self.document_processor = None
        self.gemini_analyzer = None
        self.output_manager = None
        self.start_time = None
        
    def execute(self, uploaded_file) -> None:
        """Execute the complete document processing pipeline.
        
        Args:
            uploaded_file: Streamlit uploaded file object
        """
        self.start_time = time.time()
        temp_file_path = None
        
        try:
            # Initialize progress tracking
            self.progress = ProgressTracker()
            
            # Step 1: Prepare temporary file
            temp_file_path = self._prepare_temporary_file(uploaded_file)
            
            # Step 2: Initialize all processors
            self._initialize_processors()
            
            # Step 3: Validate API connection
            self._validate_api_connection()
            
            # Step 4: Extract slides from document
            slides = self._extract_slides(temp_file_path)
            
            # Step 5: Analyze slides with AI
            analysis_results = self._analyze_slides(slides)
            
            # Step 6: Save results and complete processing
            self._save_and_complete_processing(analysis_results, uploaded_file.name)
            
        except ProcessingError as e:
            # Handle known processing errors
            logger.error(f"Processing failed: {e}")
            self.ui.show_error(str(e))
            self._cleanup_on_error()
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error during processing: {e}", exc_info=True)
            self.ui.show_error(f"An unexpected error occurred: {str(e)}")
            self._cleanup_on_error()
            
        finally:
            # Always cleanup temporary files
            self._cleanup_temporary_files(temp_file_path)
    
    def _prepare_temporary_file(self, uploaded_file) -> str:
        """Prepare temporary file from uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Path to temporary file
            
        Raises:
            ProcessingError: If file preparation fails
        """
        try:
            self.progress.update(10, "📄 Preparing uploaded file...")
            
            # Create temporary file with appropriate suffix
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            
            # Track temporary file for cleanup
            self.temp_files.append(temp_file_path)
            
            logger.info(f"Created temporary file: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            raise ProcessingError(f"Failed to prepare temporary file: {str(e)}")
    
    def _initialize_processors(self) -> None:
        """Initialize all processing components.
        
        Raises:
            ProcessingError: If initialization fails
        """
        try:
            self.progress.update(20, "🔧 Initializing processors...")
            
            self.document_processor = DocumentProcessor()
            self.gemini_analyzer = GeminiAnalyzer()
            self.output_manager = OutputManager()
            
            logger.info("All processors initialized successfully")
            
        except Exception as e:
            raise ProcessingError(f"Failed to initialize processors: {str(e)}")
    
    def _validate_api_connection(self) -> None:
        """Validate API connection before processing.
        
        Raises:
            ProcessingError: If API connection fails
        """
        try:
            self.progress.update(25, "🔗 Testing API connection...")
            
            if not self.gemini_analyzer.test_connection():
                raise ProcessingError(
                    "Failed to connect to Gemini API. Please check your API key and internet connection."
                )
            
            logger.info("API connection validated successfully")
            
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"API connection validation failed: {str(e)}")
    
    def _extract_slides(self, temp_file_path: str) -> List[SlideImage]:
        """Extract slides from the document.
        
        Args:
            temp_file_path: Path to temporary document file
            
        Returns:
            List of extracted slide images
            
        Raises:
            ProcessingError: If slide extraction fails
        """
        try:
            self.progress.update(30, "📊 Extracting slides from document...")
            
            slides = self.document_processor.process_document(temp_file_path)
            
            if not slides:
                raise ProcessingError("No slides could be extracted from the document")
            
            self.ui.show_success(f"Successfully extracted {len(slides)} slides")
            logger.info(f"Extracted {len(slides)} slides from document")
            
            return slides
            
        except DocumentProcessorError as e:
            raise ProcessingError(f"Document processing failed: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Slide extraction failed: {str(e)}")
    
    def _analyze_slides(self, slides: List[SlideImage]) -> List[SlideAnalysis]:
        """Analyze slides with AI processing.
        
        Args:
            slides: List of slide images to analyze
            
        Returns:
            List of slide analysis results
            
        Raises:
            ProcessingError: If critical analysis failures occur
        """
        try:
            self.progress.update(40, "🤖 Analyzing slides with AI...")
            
            analysis_results = []
            total_slides = len(slides)
            successful_analyses = 0
            
            # Create container for slide-by-slide progress
            slide_progress_container = st.container()
            
            for i, slide in enumerate(slides):
                try:
                    # Update progress for current slide
                    slide_progress = 40 + (50 * (i + 1) / total_slides)
                    self.progress.update(
                        int(slide_progress), 
                        f"🔍 Analyzing slide {i + 1} of {total_slides}..."
                    )
                    
                    # Show current slide being processed
                    with slide_progress_container:
                        st.info(f"Processing slide {i + 1}/{total_slides}")
                    
                    # Analyze the slide
                    analysis = self.gemini_analyzer.analyze_slide(slide)
                    analysis_results.append(analysis)
                    
                    # Track successful analyses
                    if not analysis.errors:
                        successful_analyses += 1
                    
                    # Brief delay for progress visibility and API rate limiting
                    time.sleep(2)  # Increased delay to prevent rate limiting
                    
                    logger.debug(f"Completed analysis for slide {i + 1}")
                    
                except Exception as e:
                    # Create error analysis for failed slide
                    logger.warning(f"Failed to analyze slide {i + 1}: {e}")
                    
                    error_analysis = SlideAnalysis(
                        slide_number=slide.slide_number,
                        heading="",
                        image_descriptions=[],
                        chart_table_data=[],
                        interpretation="",
                        errors=[f"Analysis failed: {str(e)}"]
                    )
                    analysis_results.append(error_analysis)
            
            # Clear slide progress display
            slide_progress_container.empty()
            
            # Check if we have any successful analyses
            if successful_analyses == 0:
                # Check if failures are due to rate limiting
                rate_limit_errors = sum(1 for result in analysis_results 
                                      if any("rate limit" in error.lower() for error in result.errors))
                
                if rate_limit_errors > 0:
                    # Rate limiting detected - provide fallback results instead of failing
                    logger.warning(f"All analyses failed due to rate limiting. Providing fallback results.")
                    
                    # Try to get retry time from analyzer
                    retry_time = getattr(self.gemini_analyzer, '_rate_limited_until', 0)
                    if retry_time > time.time():
                        wait_minutes = int((retry_time - time.time()) / 60) + 1
                        self.ui.show_warning(
                            f"⚠️ API rate limits exceeded. Providing basic slide information instead of detailed analysis. "
                            f"You can try again in approximately {wait_minutes} minutes for full AI analysis."
                        )
                    else:
                        self.ui.show_warning(
                            "⚠️ API rate limits exceeded. Providing basic slide information instead of detailed analysis. "
                            "Please wait and try again later for full AI analysis."
                        )
                else:
                    raise ProcessingError(
                        "All slide analyses failed. Please check your document quality and API connection."
                    )
            
            # Log analysis summary
            failed_analyses = total_slides - successful_analyses
            logger.info(f"Analysis complete: {successful_analyses} successful, {failed_analyses} failed")
            
            if failed_analyses > 0:
                self.ui.show_warning(
                    f"Analysis completed with {failed_analyses} failed slides out of {total_slides} total."
                )
            
            return analysis_results
            
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"Slide analysis failed: {str(e)}")
    
    def _save_and_complete_processing(self, analysis_results: List[SlideAnalysis], 
                                    original_filename: str) -> None:
        """Save results and complete the processing pipeline.
        
        Args:
            analysis_results: List of slide analysis results
            original_filename: Original filename of the document
            
        Raises:
            ProcessingError: If saving fails
        """
        try:
            self.progress.update(90, "💾 Saving analysis results...")
            
            # Calculate processing statistics
            processing_time = time.time() - self.start_time
            successful_slides = len([r for r in analysis_results if not r.errors])
            
            processing_stats = {
                "total_processing_time": processing_time,
                "slides_processed": len(analysis_results),
                "successful_slides": successful_slides,
                "api_calls_made": len(analysis_results)
            }
            
            # Save analysis results
            output_file_path = self.output_manager.save_analysis(
                analysis_results, 
                original_filename,
                processing_stats
            )
            
            # Complete progress tracking
            self.progress.complete("✅ Analysis complete!")
            
            # Store results in session state for display
            st.session_state.analysis_results = analysis_results
            st.session_state.output_file_path = output_file_path
            st.session_state.processing_complete = True
            
            # Show completion message with statistics
            self.ui.show_success(
                f"Analysis completed successfully! Processed {len(analysis_results)} slides "
                f"({successful_slides} successful) in {processing_time:.1f} seconds."
            )
            
            # Provide user notification about file saving
            self.ui.show_info(f"Results saved to: {Path(output_file_path).name}")
            
            logger.info(f"Processing pipeline completed successfully: {output_file_path}")
            
            # Auto-refresh to show results
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            raise ProcessingError(f"Failed to save results: {str(e)}")
    
    def _cleanup_on_error(self) -> None:
        """Cleanup resources when an error occurs."""
        try:
            if self.progress:
                self.progress.clear()
        except Exception as e:
            logger.warning(f"Failed to clear progress indicators: {e}")
    
    def _cleanup_temporary_files(self, temp_file_path: Optional[str] = None) -> None:
        """Clean up all temporary files created during processing.
        
        Args:
            temp_file_path: Additional temporary file path to clean up
        """
        # Add the main temp file to cleanup list if provided
        if temp_file_path and temp_file_path not in self.temp_files:
            self.temp_files.append(temp_file_path)
        
        # Clean up all tracked temporary files
        for temp_file in self.temp_files:
            try:
                temp_path = Path(temp_file)
                if temp_path.exists():
                    temp_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
        
        # Clean up document processor temporary files if available
        if self.document_processor:
            try:
                self.document_processor.cleanup_temp_files()
            except Exception as e:
                logger.warning(f"Failed to cleanup document processor temp files: {e}")
        
        # Clear the temp files list
        self.temp_files.clear()


class ProcessingError(Exception):
    """Custom exception for processing pipeline errors."""
    pass


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
    
    # Run startup validation (but don't block UI for minor issues)
    # Cache validation results to avoid running on every Streamlit rerun
    if 'startup_validation_done' not in st.session_state:
        try:
            validation_passed = run_startup_validation()
            st.session_state.startup_validation_done = True
            st.session_state.startup_validation_passed = validation_passed
            
            if not validation_passed:
                st.warning("⚠️ Some startup validations failed. Check the logs for details.")
        except Exception as e:
            st.error(f"⚠️ Startup validation error: {e}")
            logger.error(f"Startup validation failed: {e}")
            st.session_state.startup_validation_done = True
            st.session_state.startup_validation_passed = False
    elif not st.session_state.get('startup_validation_passed', False):
        st.warning("⚠️ Some startup validations failed. Check the logs for details.")
    
    # Check critical API configuration
    if not settings.GOOGLE_API_KEY:
        st.error("⚠️ Google API Key not configured. Please set the GOOGLE_API_KEY environment variable.")
        st.info("💡 You can get an API key from the Google AI Studio: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize UI components
    ui = StreamlitInterface()
    
    # Main application interface
    render_main_interface(ui)
    
    # Sidebar with configuration and help
    SidebarManager.render_sidebar()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'output_file_path' not in st.session_state:
        st.session_state.output_file_path = None


def render_main_interface(ui: StreamlitInterface):
    """Render the main application interface.
    
    Args:
        ui: StreamlitInterface instance
    """
    # Show results if processing is complete
    if st.session_state.processing_complete and st.session_state.analysis_results:
        render_results_section(ui)
        
        # Reset button
        if st.button("🔄 Analyze Another Document", use_container_width=True):
            reset_session_state()
            st.rerun()
    else:
        # File upload section
        render_file_upload_section(ui)


def render_file_upload_section(ui: StreamlitInterface):
    """Render the file upload interface and processing controls.
    
    Args:
        ui: StreamlitInterface instance
    """
    st.header("📁 Upload Pitch Deck")
    
    # File upload widget
    uploaded_file = ui.render_file_upload_widget()
    
    if uploaded_file is not None:
        # Process button
        if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
            process_document(uploaded_file, ui)


def process_document(uploaded_file, ui: StreamlitInterface):
    """Process the uploaded document through the complete analysis pipeline.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        ui: StreamlitInterface instance
    """
    # Initialize the main processing pipeline
    pipeline = DocumentProcessingPipeline(ui)
    
    # Execute the complete processing workflow
    pipeline.execute(uploaded_file)


def render_results_section(ui: StreamlitInterface):
    """Render the analysis results display section.
    
    Args:
        ui: StreamlitInterface instance
    """
    st.header("📊 Analysis Results")
    
    results = st.session_state.analysis_results
    output_file_path = st.session_state.output_file_path
    
    if not results:
        ui.show_warning("No analysis results to display.")
        return
    
    # Display results using UI component
    ui.display_results(results, output_file_path)


def reset_session_state():
    """Reset session state to allow processing another document."""
    st.session_state.processing_complete = False
    st.session_state.analysis_results = None
    st.session_state.output_file_path = None


if __name__ == "__main__":
    main()