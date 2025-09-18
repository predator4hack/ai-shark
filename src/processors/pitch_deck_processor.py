import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image

from src.processors.base_processor import BaseProcessor
from src.processors.file_converter import FileConverter
from src.utils.output_manager import OutputManager
from src.utils.llm_manager import llm_manager

class PitchDeckProcessor(BaseProcessor):
    """Processes pitch deck files (PDF and PPT)"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.ppt', '.pptx']
    
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
            
            print(f"Successfully extracted {len(images)} pages/slides")
            
            # Stage 1: Extract metadata including startup info and table of contents
            print("Stage 1: Extracting startup metadata and table of contents...")
            metadata = self._extract_metadata(images)
            
            if not metadata:
                raise ValueError("Could not extract metadata from the document")
            print(metadata)
            # Extract company name and create output directory
            company_name = metadata.get('startup_name')
            if not company_name:
                company_name = OutputManager.generate_fallback_name()
                print(f"No company name found, using fallback: {company_name}")
            
            company_dir = OutputManager.create_company_dir(company_name, output_dir)
            
            # Get output file paths
            output_paths = OutputManager.get_output_paths(company_dir, 'pitch_deck')
            
            # Save metadata
            OutputManager.save_json(metadata, output_paths['metadata'])
            
            # Stage 2: Topic-based extraction (if table of contents exists)
            extracted_data = {}
            if metadata.get('table_of_contents'):
                print("Stage 2: Performing topic-based extraction...")
                extracted_data = self._extract_topics(images, metadata['table_of_contents'])
            else:
                print("No table of contents found, skipping topic-based extraction")
            
            # Convert to markdown and save
            markdown_content = self._convert_to_markdown(extracted_data, metadata)
            OutputManager.save_file(markdown_content, output_paths['markdown'])
            
            # Save table of contents separately if available
            if metadata.get('table_of_contents'):
                OutputManager.save_json(metadata['table_of_contents'], output_paths['toc'])
            
            created_files = [output_paths['metadata'], output_paths['markdown']]
            if metadata.get('table_of_contents'):
                created_files.append(output_paths['toc'])
            
            return {
                'status': 'success',
                'company_name': company_name,
                'output_dir': company_dir,
                'files_created': created_files,
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
        """Process PDF pitch deck using LLM manager"""
        return llm_manager.pdf_to_images(pdf_path)
    
    def _process_ppt(self, ppt_path: str) -> List[Image.Image]:
        """Process PPT by converting to images"""
        # Try PDF conversion first
        pdf_path = FileConverter.ppt_to_pdf(ppt_path)
        if pdf_path and os.path.exists(pdf_path):
            try:
                images = llm_manager.pdf_to_images(pdf_path)
                os.unlink(pdf_path)  # Clean up temporary PDF
                return images
            except Exception as e:
                print(f"Error processing converted PDF: {e}")
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
        
        # Fallback: direct PPT to images
        return FileConverter.ppt_to_images(ppt_path)
    
    def _extract_metadata(self, images: List[Image.Image]) -> Optional[Dict[str, Any]]:
        """
        Stage 1: Extract startup_name, sector, sub-sector, website, and table of contents
        """
        return llm_manager.extract_metadata(images)
    
    def _extract_topics(self, images: List[Image.Image], toc: Dict[str, List[int]]) -> Dict[str, Any]:
        """Stage 2: Topic-based content extraction"""
        if not toc or not isinstance(toc, dict):
            print("Invalid table of contents format")
            return {}
        
        extracted_data = {}
        
        for topic, page_nums in toc.items():
            if not isinstance(page_nums, list) or not page_nums:
                print(f"Skipping topic '{topic}' - invalid page numbers: {page_nums}")
                continue
                
            print(f"Extracting topic: '{topic}' from pages {page_nums}")
            
            # Get images for specific pages (adjusting for 0-based index)
            topic_images = []
            for page_num in page_nums:
                if isinstance(page_num, int) and 0 < page_num <= len(images):
                    topic_images.append(images[page_num - 1])
                else:
                    print(f"Warning: Page number {page_num} out of range for topic '{topic}'")
            
            if topic_images:
                try:
                    topic_data = llm_manager.extract_topic_data(topic, topic_images)
                    extracted_data[topic] = topic_data
                    print(f"Successfully extracted data for topic '{topic}'")
                except Exception as e:
                    print(f"Error extracting data for topic '{topic}': {e}")
                    extracted_data[topic] = f"Error extracting data: {e}"
            else:
                print(f"No valid images found for topic '{topic}'")
        
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
        
        # Add table of contents if available
        if metadata.get('table_of_contents'):
            markdown_content.append("## Table of Contents")
            markdown_content.append("")
            for topic, pages in metadata['table_of_contents'].items():
                if isinstance(pages, list):
                    page_str = ", ".join(map(str, pages))
                    markdown_content.append(f"- **{topic.replace('_', ' ').title()}:** Pages {page_str}")
                else:
                    markdown_content.append(f"- **{topic.replace('_', ' ').title()}:** {pages}")
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
        else:
            markdown_content.append("## Analysis")
            markdown_content.append("")
            markdown_content.append("*Topic-based analysis was not performed due to missing table of contents.*")
            markdown_content.append("")
        
        return "\n".join(markdown_content)