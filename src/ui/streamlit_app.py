import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from src.processors.pitch_deck_processor import PitchDeckProcessor
from src.processors.additional_doc_processor import AdditionalDocProcessor
from src.utils.output_manager import OutputManager

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Startup Document Processing Pipeline",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Startup Document Processing Pipeline")
    st.markdown("Upload and process startup pitch decks and additional documents using AI-powered extraction.")
    
    # Initialize session state
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    if 'company_name' not in st.session_state:
        st.session_state.company_name = None
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pitch_deck_section()
    
    with col2:
        additional_docs_section()
    
    # Display results below
    display_results()

def pitch_deck_section():
    """Pitch deck upload and processing section"""
    st.header("🎯 Pitch Deck Upload")
    st.markdown("Upload your startup pitch deck (PDF or PowerPoint) for AI-powered analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a pitch deck file",
        type=['pdf', 'ppt', 'pptx'],
        help="Upload your startup pitch deck in PDF or PowerPoint format",
        key="pitch_deck_uploader"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
            "File type": uploaded_file.type
        }
        
        st.write("**File Details:**")
        for key, value in file_details.items():
            st.write(f"- **{key}:** {value}")
        
        # Process button
        if st.button("🚀 Process Pitch Deck", type="primary", key="process_pitch_deck"):
            process_pitch_deck(uploaded_file)

def additional_docs_section():
    """Additional documents upload section"""
    st.header("📄 Additional Documents")
    st.markdown("Upload additional documents like call transcripts, founder updates, emails, etc.")
    
    uploaded_files = st.file_uploader(
        "Choose additional document files",
        type=['pdf', 'doc', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload call transcripts, founder updates, emails, and other documents",
        key="additional_docs_uploader"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size / (1024*1024):.2f} MB)")
        
        # Check if we have a company name from pitch deck processing
        company_name = get_company_name_from_session()
        if not company_name:
            st.warning("⚠️ Please process a pitch deck first to determine the company name, or the documents will be saved under a fallback name.")
        
        # Process button
        if st.button("📝 Process Additional Documents", type="primary", key="process_additional_docs"):
            process_additional_docs(uploaded_files)

def process_pitch_deck(uploaded_file):
    """Process uploaded pitch deck"""
    with st.spinner("🔄 Processing pitch deck... This may take a few minutes."):
        try:
            # Save uploaded file temporarily
            temp_path = save_temp_file(uploaded_file)
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Converting file to images...")
            progress_bar.progress(25)
            
            # Process using PitchDeckProcessor
            processor = PitchDeckProcessor()
            
            status_text.text("Extracting metadata and table of contents...")
            progress_bar.progress(50)
            
            result = processor.process(temp_path, "outputs")
            
            status_text.text("Performing topic-based extraction...")
            progress_bar.progress(75)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            progress_bar.progress(100)
            status_text.text("Processing complete!")
            
            # Update session state
            if result['status'] == 'success':
                st.session_state.processing_status['pitch_deck'] = result
                st.session_state.company_name = result.get('company_name')
                
                st.success(f"✅ Pitch deck processed successfully!")
                st.info(f"**Company:** {result['company_name']}")
                st.info(f"**Output Directory:** {result['output_dir']}")
                
                # Display metadata if available
                if result.get('metadata'):
                    with st.expander("📊 Extracted Company Information"):
                        metadata = result['metadata']
                        if metadata.get('sector'):
                            st.write(f"**Sector:** {metadata['sector']}")
                        if metadata.get('sub_sector'):
                            st.write(f"**Sub-sector:** {metadata['sub_sector']}")
                        if metadata.get('website'):
                            st.write(f"**Website:** {metadata['website']}")
            else:
                st.error(f"❌ Error processing pitch deck: {result.get('error', 'Unknown error')}")
                st.session_state.processing_status['pitch_deck'] = result
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.session_state.processing_status['pitch_deck'] = {
                'status': 'failed',
                'error': str(e)
            }

def process_additional_docs(uploaded_files):
    """Process uploaded additional documents"""
    # Get company name from pitch deck processing or use fallback
    company_name = get_company_name_from_session()
    if not company_name:
        company_name = OutputManager.generate_fallback_name()
        st.info(f"Using fallback company name: {company_name}")
    
    # Create company directory
    company_dir = OutputManager.create_company_dir(company_name)
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    processor = AdditionalDocProcessor()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
        
        try:
            # Save file temporarily
            temp_path = save_temp_file(uploaded_file)
            
            # Process the document
            result = processor.process(temp_path, company_dir)
            results.append(result)
            
            # Clean up temp file
            os.unlink(temp_path)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            results.append({
                'status': 'failed', 
                'filename': uploaded_file.name, 
                'error': str(e)
            })
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Update session state
    st.session_state.processing_status['additional_docs'] = results
    
    # Display results
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    if successful:
        st.success(f"✅ Successfully processed {len(successful)} document(s)")
    
    if failed:
        st.error(f"❌ Failed to process {len(failed)} document(s)")
        with st.expander("View errors"):
            for result in failed:
                st.write(f"**{result['filename']}:** {result.get('error', 'Unknown error')}")
    
    status_text.text("All documents processed!")

def display_results():
    """Display processing results and output file links"""
    if st.session_state.processing_status:
        st.header("📋 Processing Results")
        
        # Display pitch deck results
        if 'pitch_deck' in st.session_state.processing_status:
            display_pitch_deck_results()
        
        # Display additional docs results
        if 'additional_docs' in st.session_state.processing_status:
            display_additional_docs_results()

def display_pitch_deck_results():
    """Display pitch deck processing results"""
    result = st.session_state.processing_status['pitch_deck']
    
    with st.expander("🎯 Pitch Deck Results", expanded=True):
        if result['status'] == 'success':
            st.success("Pitch deck processed successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company:** {result['company_name']}")
                st.write(f"**Output Directory:** {result['output_dir']}")
            
            with col2:
                if result.get('files_created'):
                    st.write("**Files Created:**")
                    for file_path in result['files_created']:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            st.write(f"- ✅ {filename}")
                        else:
                            filename = os.path.basename(file_path)
                            st.write(f"- ❌ {filename} (not found)")
            
            # Provide download links if possible
            if result.get('output_dir') and os.path.exists(result['output_dir']):
                st.write("**📁 Access your files at:**")
                st.code(result['output_dir'])
                
        else:
            st.error(f"Processing failed: {result.get('error', 'Unknown error')}")

def display_additional_docs_results():
    """Display additional documents processing results"""
    results = st.session_state.processing_status['additional_docs']
    
    with st.expander("📄 Additional Documents Results", expanded=True):
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] != 'success']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**✅ Successfully Processed:**")
            for result in successful:
                st.write(f"- {result['filename']}")
        
        with col2:
            if failed:
                st.write("**❌ Failed to Process:**")
                for result in failed:
                    st.write(f"- {result['filename']}")

def save_temp_file(uploaded_file) -> str:
    """Save uploaded file to temporary location"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def get_company_name_from_session() -> str:
    """Get company name from session state"""
    if st.session_state.company_name:
        return st.session_state.company_name
    
    # Try to get from pitch deck results
    if 'pitch_deck' in st.session_state.processing_status:
        result = st.session_state.processing_status['pitch_deck']
        if result.get('status') == 'success' and result.get('company_name'):
            return result['company_name']
    
    return None

# Add sidebar with information
def add_sidebar():
    """Add sidebar with application information"""
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application processes startup documents using AI:
        
        **Pitch Deck Processing:**
        - Extracts company metadata
        - Generates table of contents
        - Performs topic-based analysis
        - Saves structured markdown output
        
        **Additional Documents:**
        - Processes transcripts, emails, updates
        - Structures content using AI
        - Converts to readable markdown format
        
        **Supported Formats:**
        - PDF files
        - PowerPoint (.ppt, .pptx)
        - Word documents (.doc, .docx)
        - Text files (.txt)
        """)
        
        st.header("🔧 Settings")
        if st.button("🗑️ Clear All Results"):
            st.session_state.processing_status = {}
            st.session_state.company_name = None
            st.rerun()

if __name__ == "__main__":
    add_sidebar()
    main()