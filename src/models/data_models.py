"""
Core data models for the VC Document Analyzer application.

This module contains the dataclasses that represent the main data structures
used throughout the application for processing pitch deck documents.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path


@dataclass
class SlideImage:
    """Represents an extracted slide image from a document.
    
    Attributes:
        slide_number: The sequential number of the slide (1-indexed)
        image_data: Raw image data as bytes
        image_format: Image format ('PNG', 'JPEG', etc.)
        original_size: Tuple of (width, height) in pixels
    """
    slide_number: int
    image_data: bytes
    image_format: str
    original_size: Tuple[int, int]


@dataclass
class SlideAnalysis:
    """Stores AI analysis results for a single slide.
    
    Attributes:
        slide_number: The sequential number of the slide (1-indexed)
        heading: Main title or heading extracted from the slide
        image_descriptions: List of descriptions for images/visual elements
        chart_table_data: List of textual descriptions of charts/tables
        interpretation: AI interpretation of what the slide conveys
        confidence_score: Confidence level of the analysis (0.0-1.0)
        processing_time: Time taken to process this slide in seconds
        errors: List of any errors encountered during processing
    """
    slide_number: int
    heading: str
    image_descriptions: List[str]
    chart_table_data: List[str]
    interpretation: str
    confidence_score: float = 0.0
    processing_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None provided."""
        if self.errors is None:
            self.errors = []


@dataclass
class ProcessingResult:
    """Overall processing outcome for a complete document.
    
    Attributes:
        document_name: Original name of the processed document
        total_slides: Total number of slides in the document
        successful_slides: Number of slides processed successfully
        failed_slides: List of slide numbers that failed processing
        processing_time: Total time taken for complete processing
        output_file_path: Path to the generated output file
        slide_analyses: List of all slide analysis results
    """
    document_name: str
    total_slides: int
    successful_slides: int
    failed_slides: List[int]
    processing_time: float
    output_file_path: str
    slide_analyses: List[SlideAnalysis]
    
    def __post_init__(self):
        """Initialize empty lists if None provided."""
        if self.failed_slides is None:
            self.failed_slides = []
        if self.slide_analyses is None:
            self.slide_analyses = []
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_slides == 0:
            return 0.0
        return (self.successful_slides / self.total_slides) * 100.0
    
    @property
    def has_failures(self) -> bool:
        """Check if any slides failed processing."""
        return len(self.failed_slides) > 0