# UI & Pre-Processing documents

**Objective** - Create a simple streamlit UI for the project. The UI should be miniaml with following features:

1. Users should be able to upload the stratup pitch deck
2. Users can upload any additional documents about the startup
3. Create a document processing pipeline using LLMs, extracting the content of all the files and save them in the /outputs/<company-name>/ in markdown format for each of the uploaded file

**Implementation Details**:

1. There should be an button to upload or drag and drop to upload the pitch deck in pdf or power point presentation only
2. There should be an additional button to upload any other additional document related to the startup
3. Analyse the exsisting data_extraction_pipeline.py and see how it's extracting the contents of the given pitch deck. Similar to this extraction pipeline, you have to create a processing pipeline that would process the pitch deck and additional data uploaded from the UI
4. Process the files(Processing details are mentioned below) and store them in the dir /outputs/<company-name>/

## Processing files:

1. Pitch Deck Processing:
   In csae of PDF:

    1. Convert PDF to a list of images
    2. Stage 1: Generate JSON output consisting fields [startup_name, sector, sub-sector, website, table_of_contents], save this JSON file in /outputs/<company-name>/ (<company-name> is present in the JSON file created in the step)
    3. Stage 2: Targeted, topic-by-topic extraction utilizing table_of_contents from previous step
    4. Convert to Markdown and save

    (The steps mentioned above are similar as the pipeline mentioned in data_extraction_pipeline.py)

    In case of PPTs:

    - Come up with the best way to extract the information.

2. Additional Data Processing:

    Since these documents can have any content, the way of extraction can be a bit different from the above pipeline.

    PDF/Docs:

    - Come up with a data extraction pipeline for these type of documents. The documents can contain call transcripts, founder updates, and emails.

For each document, create a separate file in /outputs/<company-name>/

Try to keep the modules reusable. Use the existing/update directory structure to create the modules

Example about sector and sub sector(not an exhaustive list):

```
Technology: Fintech, BioTech, Ed-Tech, AI etc.

Healthcare: Includes pharmaceuticals, medical devices, and health services.

Financial Services: Covers banking, insurance, and investment.

Consumer Goods: Includes retail, food and beverage, and personal care.

Industrials: Manufacturing, construction, and engineering.

Energy: Traditional and renewable energy sources.
```

Clarifying questions

1. PowerPoint Processing: For PPT files, would you prefer to:

    - Convert PPT to PDF first and then use the existing PDF pipeline?

2. Company Name Extraction: The pipeline needs to extract the company
   name from the first stage to create the output directory
   /outputs/<company-name>/. Should we:

    - Use the startup_name field from the JSON output in Stage 1
    - Handle cases where company name extraction fails (fallback naming)

3. Additional Documents Processing: For additional documents
   (PDFs/docs containing call transcripts, founder updates, emails),
   should we:
   Use a simpler extraction approach (just convert to text and then
   to markdown)

4. File Naming Convention: For the output files in
   /outputs/<company-name>/, what naming convention would you prefer?

    - pitch_deck.md, for pitch deck files
    - Or use original filenames

5. Error Handling: How should the UI handle processing failures?

-   Show error messages in the UI?

6. Dependencies: I noticed the requirements.txt has some merge
   conflicts. Should I clean that up, or do you have a preferred set of
   dependencies?

I cleaned it up. However you can update it if you want to add packages

---

# Implementation Plan

## Overview
This plan outlines the step-by-step implementation of a Streamlit UI with document processing capabilities for startup pitch decks and additional documents. The implementation will reuse existing patterns from `data_extraction_pipeline.py` and maintain modular, reusable code structure.

## Phase 1: Project Structure Setup

### 1.1 Create Core Module Structure
```
src/
├── ui/
│   ├── __init__.py
│   ├── streamlit_app.py          # Main UI application
│   └── components/
│       ├── __init__.py
│       ├── file_uploader.py      # File upload components
│       └── progress_tracker.py   # Processing progress display
├── processors/
│   ├── __init__.py
│   ├── base_processor.py         # Abstract base processor
│   ├── pitch_deck_processor.py   # Pitch deck processing logic
│   ├── additional_doc_processor.py # Additional document processing
│   └── file_converter.py         # PPT to PDF conversion utilities
└── utils/
    ├── file_utils.py             # File handling utilities
    └── output_manager.py         # Output directory management
```

### 1.2 Update Dependencies
- Add any missing packages for PPT processing if needed
- Ensure all existing dependencies are compatible

## Phase 2: Core Processing Modules

### 2.1 Base Processor (src/processors/base_processor.py)
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path

class BaseProcessor(ABC):
    """Abstract base class for document processors"""
    
    @abstractmethod
    def process(self, file_path: str, output_dir: str) -> Dict[str, Any]:
        """Process document and return metadata"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        pass
```

### 2.2 File Converter (src/processors/file_converter.py)
```python
from pptx import Presentation
import fitz  # PyMuPDF
from pathlib import Path

class FileConverter:
    """Handles file format conversions"""
    
    @staticmethod
    def ppt_to_pdf(ppt_path: str, output_path: str) -> str:
        """Convert PPT to PDF using python-pptx and reportlab/other PDF library"""
        # Implementation for PPT to PDF conversion
        
    @staticmethod
    def extract_ppt_images(ppt_path: str) -> List[Image]:
        """Extract images directly from PPT slides"""
        # Alternative approach: direct image extraction from PPT
```

### 2.3 Pitch Deck Processor (src/processors/pitch_deck_processor.py)
```python
class PitchDeckProcessor(BaseProcessor):
    """Processes pitch deck files (PDF and PPT)"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.ppt', '.pptx']
        
    def process(self, file_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Main processing logic:
        1. Handle file type (PDF direct, PPT -> PDF conversion)
        2. Convert to images
        3. Stage 1: Extract metadata and ToC
        4. Stage 2: Topic-based extraction
        5. Save outputs
        """
        
    def _process_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Process PDF pitch deck using existing pipeline logic"""
        
    def _process_ppt(self, ppt_path: str, output_dir: str) -> Dict[str, Any]:
        """Process PPT by converting to PDF first"""
        
    def _extract_metadata(self, images: List[Image]) -> Dict[str, Any]:
        """Stage 1: Extract startup_name, sector, sub-sector, website, ToC"""
        
    def _extract_topics(self, images: List[Image], toc: Dict) -> Dict[str, Any]:
        """Stage 2: Topic-based content extraction"""
        
    def _save_outputs(self, data: Dict, metadata: Dict, output_dir: str, company_name: str):
        """Save JSON metadata and markdown content"""
```

### 2.4 Additional Document Processor (src/processors/additional_doc_processor.py)
```python
class AdditionalDocProcessor(BaseProcessor):
    """Processes additional documents (transcripts, emails, updates)"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
        
    def process(self, file_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Simplified processing:
        1. Extract text content
        2. Structure content using LLM
        3. Convert to markdown
        4. Save with original filename
        """
        
    def _extract_text(self, file_path: str) -> str:
        """Extract raw text based on file type"""
        
    def _structure_content(self, text: str, filename: str) -> str:
        """Use LLM to structure and clean up content"""
        
    def _text_to_markdown(self, structured_text: str) -> str:
        """Convert structured text to markdown format"""
```

### 2.5 Output Manager (src/utils/output_manager.py)
```python
class OutputManager:
    """Manages output directory structure and file saving"""
    
    @staticmethod
    def create_company_dir(company_name: str) -> str:
        """Create /outputs/<company-name>/ directory"""
        
    @staticmethod
    def sanitize_company_name(name: str) -> str:
        """Sanitize company name for directory creation"""
        
    @staticmethod
    def generate_fallback_name() -> str:
        """Generate fallback name when company extraction fails"""
        
    @staticmethod
    def save_file(content: str, filepath: str, mode: str = 'w'):
        """Save content to file with error handling"""
```

## Phase 3: Streamlit UI Implementation

### 3.1 Main Application (src/ui/streamlit_app.py)
```python
import streamlit as st
from src.processors.pitch_deck_processor import PitchDeckProcessor
from src.processors.additional_doc_processor import AdditionalDocProcessor
from src.utils.output_manager import OutputManager

def main():
    """Main Streamlit application"""
    st.title("Startup Document Processing Pipeline")
    
    # Session state initialization
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    
    # Pitch deck upload section
    pitch_deck_section()
    
    # Additional documents upload section  
    additional_docs_section()
    
    # Processing results display
    display_results()

def pitch_deck_section():
    """Pitch deck upload and processing section"""
    st.header("Pitch Deck Upload")
    
    uploaded_file = st.file_uploader(
        "Upload Pitch Deck",
        type=['pdf', 'ppt', 'pptx'],
        help="Upload your startup pitch deck (PDF or PowerPoint)"
    )
    
    if uploaded_file and st.button("Process Pitch Deck"):
        process_pitch_deck(uploaded_file)

def additional_docs_section():
    """Additional documents upload section"""
    st.header("Additional Documents")
    
    uploaded_files = st.file_uploader(
        "Upload Additional Documents",
        type=['pdf', 'doc', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload call transcripts, founder updates, emails, etc."
    )
    
    if uploaded_files and st.button("Process Additional Documents"):
        process_additional_docs(uploaded_files)

def process_pitch_deck(uploaded_file):
    """Process uploaded pitch deck"""
    with st.spinner("Processing pitch deck..."):
        try:
            # Save uploaded file temporarily
            temp_path = save_temp_file(uploaded_file)
            
            # Process using PitchDeckProcessor
            processor = PitchDeckProcessor()
            result = processor.process(temp_path, "outputs")
            
            # Update session state
            st.session_state.processing_status['pitch_deck'] = {
                'status': 'completed',
                'company_name': result.get('company_name'),
                'output_dir': result.get('output_dir'),
                'files_created': result.get('files_created', [])
            }
            
            st.success(f"Pitch deck processed successfully! Company: {result['company_name']}")
            
        except Exception as e:
            st.error(f"Error processing pitch deck: {str(e)}")
            st.session_state.processing_status['pitch_deck'] = {
                'status': 'failed',
                'error': str(e)
            }

def process_additional_docs(uploaded_files):
    """Process uploaded additional documents"""
    # Get company name from pitch deck processing or use fallback
    company_name = get_company_name_from_session()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        
        try:
            temp_path = save_temp_file(uploaded_file)
            processor = AdditionalDocProcessor()
            result = processor.process(temp_path, f"outputs/{company_name}")
            results.append(result)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            results.append({'status': 'failed', 'filename': uploaded_file.name, 'error': str(e)})
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    st.session_state.processing_status['additional_docs'] = results
    status_text.text("Processing completed!")

def display_results():
    """Display processing results and output file links"""
    if st.session_state.processing_status:
        st.header("Processing Results")
        
        # Display pitch deck results
        if 'pitch_deck' in st.session_state.processing_status:
            display_pitch_deck_results()
        
        # Display additional docs results
        if 'additional_docs' in st.session_state.processing_status:
            display_additional_docs_results()

# Additional utility functions...
```

### 3.2 File Upload Components (src/ui/components/file_uploader.py)
```python
class FileUploadHandler:
    """Handles file upload operations and validation"""
    
    @staticmethod
    def validate_pitch_deck_file(file) -> bool:
        """Validate pitch deck file type and size"""
        
    @staticmethod
    def validate_additional_doc_file(file) -> bool:
        """Validate additional document file"""
        
    @staticmethod
    def save_uploaded_file(uploaded_file, directory: str) -> str:
        """Save uploaded file to temporary location"""
```

### 3.3 Progress Tracker (src/ui/components/progress_tracker.py)
```python
class ProgressTracker:
    """Manages processing progress display"""
    
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        
    def update_progress(self, message: str):
        """Update progress with message"""
        
    def complete(self):
        """Mark processing as complete"""
```

## Phase 4: Integration and Testing

### 4.1 Error Handling Strategy
```python
class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_processing_error(error: Exception, context: str) -> Dict[str, Any]:
        """Handle and log processing errors"""
        
    @staticmethod
    def display_user_friendly_error(error: Exception, st_container):
        """Display user-friendly error messages in Streamlit"""
```

### 4.2 Configuration Management
```python
# config/ui_config.py
UI_CONFIG = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_pitch_deck_formats': ['.pdf', '.ppt', '.pptx'],
    'supported_additional_formats': ['.pdf', '.doc', '.docx', '.txt'],
    'output_base_dir': 'outputs',
    'temp_dir': 'temp_uploads'
}
```

## Phase 5: File Structure and Organization

### 5.1 Output Directory Structure
```
outputs/
└── <company-name>/
    ├── metadata.json           # Company metadata from Stage 1
    ├── pitch_deck.md          # Processed pitch deck content
    └── additional_docs/
        ├── document_1.md      # First additional document
        ├── document_2.md      # Second additional document
        └── ...
```

### 5.2 File Naming Conventions
- **Pitch Deck**: Always saved as `pitch_deck.md`
- **Metadata**: Always saved as `metadata.json`
- **Additional Docs**: Use original filename with `.md` extension
- **Company Directory**: Sanitized company name from metadata

## Phase 6: Implementation Sequence

### Step 1: Core Infrastructure
1. Create directory structure
2. Implement BaseProcessor abstract class
3. Implement OutputManager utility
4. Implement FileConverter for PPT handling

### Step 2: Processing Logic
1. Implement PitchDeckProcessor (reusing existing pipeline logic)
2. Implement AdditionalDocProcessor
3. Add error handling and logging
4. Test processing modules independently

### Step 3: UI Development
1. Create basic Streamlit app structure
2. Implement file upload components
3. Integrate processing modules
4. Add progress tracking and error display
5. Implement results display

### Step 4: Integration Testing
1. Test end-to-end workflow
2. Test error scenarios
3. Test with various file types
4. Validate output structure

### Step 5: Final Polish
1. Add loading indicators
2. Improve error messages
3. Add file download capabilities
4. Documentation and cleanup

## Key Design Decisions

1. **PPT Processing**: Convert PPT to PDF first, then use existing PDF pipeline
2. **Company Name**: Use `startup_name` from Stage 1 JSON, fallback to timestamp-based naming
3. **Additional Docs**: Simple text extraction + LLM structuring approach
4. **File Naming**: Fixed names for pitch deck, original names for additional docs
5. **Error Handling**: Display errors in UI, continue processing other files
6. **Modularity**: Separate processors for different document types, reusable components

## Success Criteria

1. ✅ Users can upload pitch decks (PDF/PPT) via drag-and-drop interface
2. ✅ Users can upload multiple additional documents
3. ✅ Processing pipeline extracts company metadata and creates appropriate directory structure
4. ✅ All outputs saved in `/outputs/<company-name>/` with proper naming
5. ✅ Error handling displays helpful messages without crashing
6. ✅ Code follows existing project patterns and remains modular/reusable
7. ✅ Processing progress visible to users
8. ✅ Results displayed with links to generated files

This plan provides sufficient detail for any agent to resume and complete the implementation while maintaining consistency with existing code patterns and requirements.
