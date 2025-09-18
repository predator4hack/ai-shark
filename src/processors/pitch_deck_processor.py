import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image

from src.processors.base_processor import BaseProcessor
from src.processors.file_converter import FileConverter
from src.utils.output_manager import OutputManager

# Import existing functionality from data_extraction_pipeline
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_extraction_pipeline import (
    configure_gemini, 
    generate_table_of_contents, 
    extract_topic_data,
    json_to_markdown,
    retry_with_backoff
)

class PitchDeckProcessor(BaseProcessor):
    """Processes pitch deck files (PDF and PPT)"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.ppt', '.pptx']
        # Configure Gemini API
        try:
            configure_gemini()
        except Exception as e:
            print(f"Warning: Could not configure Gemini API: {e}")
    
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        return self.supported_extensions
    
    def process(self, file_path: str, output_dir: str = "outputs") -> Dict[str, Any]:
        """
        Main processing logic for pitch decks
        
        Args:
            file_path: Path to the pitch deck file
            output_dir: Base output directory
            
        Returns:
            Dictionary containing processing results and metadata
        """
        try:
            print(f"Processing pitch deck: {file_path}")
            file_extension = Path(file_path).suffix.lower()
            
            # Convert to images based on file type
            if file_extension == '.pdf':
                images = self._process_pdf(file_path)
            elif file_extension in ['.ppt', '.pptx']:
                images = self._process_ppt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            if not images:
                raise ValueError("Could not extract images from the file")
            
            # Stage 1: Extract metadata and table of contents
            print("Stage 1: Extracting metadata and table of contents...")
            metadata = self._extract_metadata(images)
            
            if not metadata:
                raise ValueError("Could not extract metadata from the document")
            
            # Extract company name and create output directory
            company_name = metadata.get('startup_name', 'unknown_company')
            company_dir = OutputManager.create_company_dir(company_name, output_dir)
            
            # Get output file paths
            output_paths = OutputManager.get_output_paths(company_dir, 'pitch_deck')
            
            # Save metadata
            OutputManager.save_json(metadata, output_paths['metadata'])
            
            # Stage 2: Topic-based extraction
            print("Stage 2: Performing topic-based extraction...")
            extracted_data = self._extract_topics(images, metadata.get('table_of_contents', {}))
            
            # Convert to markdown and save
            markdown_content = self._convert_to_markdown(extracted_data, metadata)
            OutputManager.save_file(markdown_content, output_paths['markdown'])
            
            # Save table of contents separately
            if 'table_of_contents' in metadata:
                OutputManager.save_json(metadata['table_of_contents'], output_paths['toc'])
            
            return {
                'status': 'success',
                'company_name': company_name,
                'output_dir': company_dir,
                'files_created': [
                    output_paths['metadata'],
                    output_paths['markdown'],
                    output_paths['toc']
                ],
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Error processing pitch deck: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'company_name': None,
                'output_dir': None,
                'files_created': []
            }
    
    def _process_pdf(self, pdf_path: str) -> List[Image.Image]:
        """Process PDF pitch deck using existing pipeline logic"""
        return FileConverter.pdf_to_images(pdf_path)
    
    def _process_ppt(self, ppt_path: str) -> List[Image.Image]:
        """Process PPT by converting to images"""
        # Try PDF conversion first
        pdf_path = FileConverter.ppt_to_pdf(ppt_path)
        if pdf_path and os.path.exists(pdf_path):
            try:
                images = FileConverter.pdf_to_images(pdf_path)
                os.unlink(pdf_path)  # Clean up temporary PDF
                return images
            except Exception as e:
                print(f"Error processing converted PDF: {e}")
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
        
        # Fallback: direct PPT to images
        return FileConverter.ppt_to_images(ppt_path)
    
    def _extract_metadata(self, images: List[Image.Image]) -> Dict[str, Any]:
        """Stage 1: Extract startup_name, sector, sub-sector, website, ToC"""
        try:
            return generate_table_of_contents(images)
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None
    
    def _extract_topics(self, images: List[Image.Image], toc: Dict) -> Dict[str, Any]:
        """Stage 2: Topic-based content extraction"""
        if not toc:
            return {}
        
        extracted_data = {}
        
        for topic, page_nums in toc.items():
            if isinstance(page_nums, list) and page_nums:
                print(f"Extracting topic: '{topic}' from pages {page_nums}")
                
                # Get images for specific pages (adjusting for 0-based index)
                topic_images = []
                for page_num in page_nums:
                    if isinstance(page_num, int) and 0 < page_num <= len(images):
                        topic_images.append(images[page_num - 1])
                
                if topic_images:
                    try:
                        topic_data = extract_topic_data(topic, topic_images)
                        extracted_data[topic] = topic_data
                    except Exception as e:
                        print(f"Error extracting data for topic '{topic}': {e}")
                        extracted_data[topic] = f"Error extracting data: {e}"
        
        return extracted_data
    
    def _convert_to_markdown(self, extracted_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Convert extracted data to markdown format"""
        markdown_content = []
        
        # Add company header
        company_name = metadata.get('startup_name', 'Unknown Company')
        markdown_content.append(f"# {company_name} - Pitch Deck Analysis")
        markdown_content.append("")
        
        # Add metadata section
        markdown_content.append("## Company Information")
        markdown_content.append("")
        
        if metadata.get('sector'):
            markdown_content.append(f"**Sector:** {metadata['sector']}")
        if metadata.get('sub_sector'):
            markdown_content.append(f"**Sub-sector:** {metadata['sub_sector']}")
        if metadata.get('website'):
            markdown_content.append(f"**Website:** {metadata['website']}")
        
        markdown_content.append("")
        
        # Add extracted content
        if extracted_data:
            markdown_content.append("## Detailed Analysis")
            markdown_content.append("")
            
            for topic, content in extracted_data.items():
                markdown_content.append(f"### {topic.replace('_', ' ').title()}")
                markdown_content.append("")
                markdown_content.append(str(content))
                markdown_content.append("")
        
        return "\n".join(markdown_content)