"""
Document Models for Multi-Agent Startup Analysis System
Task 2: Data Models and Document Structure

Pydantic models for handling startup documents and their metadata.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """Metadata for a startup document"""

    file_path: str = Field(..., description="Full path to the document file")
    size: int = Field(..., description="File size in bytes", ge=0)
    last_modified: datetime = Field(..., description="Last modification timestamp")
    creation_time: Optional[datetime] = Field(None, description="File creation timestamp")
    file_extension: str = Field(..., description="File extension (e.g., .md, .pdf)")
    encoding: Optional[str] = Field("utf-8", description="Text encoding if applicable")

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        """Ensure file path is not empty"""
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()

    @field_validator('file_extension')
    @classmethod
    def validate_extension(cls, v):
        """Ensure extension starts with dot"""
        if not v.startswith('.'):
            v = f'.{v}'
        return v.lower()


class ParsedContent(BaseModel):
    """Parsed content from a document"""

    sections: Dict[str, str] = Field(
        default_factory=dict,
        description="Document sections mapped by title"
    )
    raw_text: str = Field(..., description="Complete raw text content")
    word_count: int = Field(..., description="Total word count", ge=0)
    paragraph_count: int = Field(default=0, description="Number of paragraphs", ge=0)
    headers: List[str] = Field(
        default_factory=list,
        description="Extracted headers/titles"
    )
    tables: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted table data"
    )
    links: List[str] = Field(
        default_factory=list,
        description="Extracted URLs/links"
    )

    @field_validator('word_count')
    @classmethod
    def validate_word_count(cls, v, info):
        """Validate word count matches raw text"""
        if info.data and 'raw_text' in info.data and info.data['raw_text']:
            actual_count = len(info.data['raw_text'].split())
            if abs(v - actual_count) > 10:  # Allow small variance
                raise ValueError(f"Word count {v} doesn't match actual count {actual_count}")
        return v

    def get_section_content(self, section_name: str) -> Optional[str]:
        """Get content for a specific section"""
        return self.sections.get(section_name)

    def has_section(self, section_name: str) -> bool:
        """Check if section exists"""
        return section_name in self.sections


class StartupDocument(BaseModel):
    """Main model for a startup document"""

    content: ParsedContent = Field(..., description="Parsed document content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    document_type: str = Field(..., description="Type of document (e.g., 'pitch_deck', 'business_plan')")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    version: str = Field(default="1.0", description="Document version")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    language: str = Field(default="en", description="Document language")
    processed_at: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

    @field_validator('document_type')
    @classmethod
    def validate_document_type(cls, v):
        """Validate document type"""
        allowed_types = {
            'pitch_deck', 'business_plan', 'financial_report',
            'market_analysis', 'technical_spec', 'other'
        }
        if v.lower() not in allowed_types:
            raise ValueError(f"Document type must be one of: {allowed_types}")
        return v.lower()

    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Validate language code"""
        # Simple validation for common language codes
        if len(v) != 2 or not v.isalpha():
            raise ValueError("Language must be a 2-letter language code")
        return v.lower()

    def get_summary(self) -> Dict[str, Any]:
        """Get document summary"""
        return {
            'title': self.title or 'Untitled',
            'type': self.document_type,
            'word_count': self.content.word_count,
            'sections': len(self.content.sections),
            'size_mb': round(self.metadata.size / (1024 * 1024), 2),
            'processed_at': self.processed_at.isoformat()
        }

    def search_content(self, query: str) -> List[str]:
        """Search for content matching query"""
        results = []
        query_lower = query.lower()

        # Search in raw text
        if query_lower in self.content.raw_text.lower():
            results.append(f"Found in main content")

        # Search in sections
        for section_name, section_content in self.content.sections.items():
            if query_lower in section_content.lower():
                results.append(f"Found in section: {section_name}")

        return results


# Example data for testing
def create_sample_document() -> StartupDocument:
    """Create a sample startup document for testing"""
    metadata = DocumentMetadata(
        file_path="/path/to/sample.md",
        size=1024,
        last_modified=datetime.now(),
        file_extension=".md"
    )

    content = ParsedContent(
        sections={
            "Executive Summary": "This is a revolutionary startup...",
            "Market Analysis": "The market size is $10B...",
            "Financial Projections": "We project $1M revenue..."
        },
        raw_text="This is a revolutionary startup in the fintech space",
        word_count=9,
        headers=["Executive Summary", "Market Analysis", "Financial Projections"]
    )

    return StartupDocument(
        content=content,
        metadata=metadata,
        document_type="pitch_deck",
        title="Sample Startup Pitch",
        author="John Doe",
        tags=["fintech", "startup", "series-a"]
    )