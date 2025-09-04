"""
Output management system for the VC Document Analyzer.

This module handles the formatting and saving of slide analysis results
to structured Markdown files with proper metadata and organization.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from ..models.data_models import SlideAnalysis, ProcessingResult


class OutputManager:
    """Manages output file operations and formatting for analysis results."""
    
    def __init__(self, output_directory: str = "outputs"):
        """Initialize the OutputManager.
        
        Args:
            output_directory: Directory where output files will be saved
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_analysis(self, results: List[SlideAnalysis], original_filename: str, 
                     processing_stats: Optional[Dict[str, Any]] = None) -> str:
        """Save slide analysis results to a Markdown file.
        
        Args:
            results: List of SlideAnalysis objects to save
            original_filename: Original name of the processed document
            processing_stats: Optional processing statistics
            
        Returns:
            Path to the saved output file
            
        Raises:
            OSError: If file saving fails
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot save empty results list")
        
        try:
            # Generate output filename
            output_filename = self.generate_filename(original_filename)
            output_path = self.output_directory / output_filename
            
            # Generate markdown content
            markdown_content = self._generate_markdown_content(
                results, original_filename, processing_stats
            )
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Analysis saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")
            raise OSError(f"Failed to save analysis to file: {e}")
    
    def generate_filename(self, original_name: str) -> str:
        """Generate a timestamped filename from the original document name.
        
        Args:
            original_name: Original filename of the document
            
        Returns:
            Sanitized filename with timestamp
        """
        # First sanitize the entire filename, then remove extension
        sanitized_full = self._sanitize_filename(original_name)
        
        # Remove common file extensions
        for ext in ['.pdf', '.pptx', '.ppt', '.png', '.jpg', '.jpeg']:
            if sanitized_full.lower().endswith(ext.lower()):
                sanitized_full = sanitized_full[:-len(ext)]
                break
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        return f"{sanitized_full}_{timestamp}.md"
    
    def format_slide_markdown(self, analysis: SlideAnalysis) -> str:
        """Format a single slide analysis as Markdown.
        
        Args:
            analysis: SlideAnalysis object to format
            
        Returns:
            Formatted Markdown string for the slide
        """
        markdown = f"## Slide {analysis.slide_number}"
        
        if analysis.heading:
            markdown += f": {analysis.heading}"
        
        markdown += "\n\n"
        
        # Add image descriptions
        if analysis.image_descriptions:
            markdown += "### Visual Elements\n\n"
            for i, description in enumerate(analysis.image_descriptions, 1):
                markdown += f"- **Image {i}**: {description}\n"
            markdown += "\n"
        
        # Add chart/table data
        if analysis.chart_table_data:
            markdown += "### Charts and Tables\n\n"
            for i, data in enumerate(analysis.chart_table_data, 1):
                markdown += f"- **Data {i}**: {data}\n"
            markdown += "\n"
        
        # Add interpretation
        if analysis.interpretation:
            markdown += "### Interpretation\n\n"
            markdown += f"{analysis.interpretation}\n\n"
        
        # Add metadata
        markdown += "### Metadata\n\n"
        markdown += f"- **Confidence Score**: {analysis.confidence_score:.2f}\n"
        markdown += f"- **Processing Time**: {analysis.processing_time:.2f}s\n"
        
        if analysis.errors:
            markdown += f"- **Errors**: {len(analysis.errors)} error(s)\n"
            for error in analysis.errors:
                markdown += f"  - {error}\n"
        
        markdown += "\n---\n\n"
        
        return markdown
    
    def create_summary_metadata(self, results: List[SlideAnalysis], 
                              original_filename: str,
                              processing_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate metadata summary for the analysis results.
        
        Args:
            results: List of SlideAnalysis objects
            original_filename: Original document filename
            processing_stats: Optional processing statistics
            
        Returns:
            Dictionary containing summary metadata
        """
        total_slides = len(results)
        successful_slides = len([r for r in results if not r.errors])
        failed_slides = [r.slide_number for r in results if r.errors]
        
        total_processing_time = sum(r.processing_time for r in results)
        avg_confidence = sum(r.confidence_score for r in results) / total_slides if total_slides > 0 else 0.0
        
        metadata = {
            "document_name": original_filename,
            "processing_date": datetime.now().isoformat(),
            "total_slides": total_slides,
            "successful_slides": successful_slides,
            "failed_slides": failed_slides,
            "success_rate": (successful_slides / total_slides * 100) if total_slides > 0 else 0.0,
            "total_processing_time": total_processing_time,
            "average_confidence": avg_confidence,
        }
        
        if processing_stats:
            metadata.update(processing_stats)
        
        return metadata
    
    def _generate_markdown_content(self, results: List[SlideAnalysis], 
                                 original_filename: str,
                                 processing_stats: Optional[Dict[str, Any]] = None) -> str:
        """Generate complete Markdown content for the analysis results.
        
        Args:
            results: List of SlideAnalysis objects
            original_filename: Original document filename
            processing_stats: Optional processing statistics
            
        Returns:
            Complete Markdown content as string
        """
        # Generate metadata
        metadata = self.create_summary_metadata(results, original_filename, processing_stats)
        
        # Start with document header
        content = f"# Pitch Deck Analysis: {original_filename}\n\n"
        
        # Add summary metadata
        content += "## Document Summary\n\n"
        content += f"- **Original Document**: {metadata['document_name']}\n"
        content += f"- **Processing Date**: {metadata['processing_date']}\n"
        content += f"- **Total Slides**: {metadata['total_slides']}\n"
        content += f"- **Successfully Processed**: {metadata['successful_slides']}\n"
        content += f"- **Success Rate**: {metadata['success_rate']:.1f}%\n"
        content += f"- **Total Processing Time**: {metadata['total_processing_time']:.2f}s\n"
        content += f"- **Average Confidence**: {metadata['average_confidence']:.2f}\n"
        
        if metadata['failed_slides']:
            content += f"- **Failed Slides**: {', '.join(map(str, metadata['failed_slides']))}\n"
        
        content += "\n---\n\n"
        
        # Add individual slide analyses
        content += "# Slide-by-Slide Analysis\n\n"
        
        for analysis in sorted(results, key=lambda x: x.slide_number):
            content += self.format_slide_markdown(analysis)
        
        return content
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename to sanitize
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores and whitespace
        sanitized = sanitized.strip('_').strip()
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "document"
        
        # Limit length to reasonable size
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized