"""
Document Loader and Parser for Multi-Agent Startup Analysis System
Task 3: Document Loader and Parser

Implements document loading, markdown parsing, and LangChain Document integration
with comprehensive error handling and validation.
"""

import os
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

import markdown
from markdown.extensions import toc, tables, fenced_code
from langchain_core.documents import Document as LangChainDocument

from src.models.document_models import DocumentMetadata, ParsedContent, StartupDocument
from task_config import Config


logger = logging.getLogger(__name__)


@dataclass
class LoaderConfig:
    """Configuration for document loading"""
    max_file_size_mb: int = 50
    chunk_size: int = 4000
    chunk_overlap: int = 200
    supported_encodings: List[str] = None

    def __post_init__(self):
        if self.supported_encodings is None:
            self.supported_encodings = ['utf-8', 'latin-1', 'cp1252']


class DocumentLoaderError(Exception):
    """Custom exception for document loading errors"""
    pass


class MarkdownParser:
    """Markdown parser with advanced features and error handling"""

    def __init__(self, config: Optional[LoaderConfig] = None):
        self.config = config or LoaderConfig()
        self._setup_markdown()

    def _setup_markdown(self):
        """Setup markdown parser with extensions"""
        self.md = markdown.Markdown(
            extensions=[
                'toc',
                'tables',
                'fenced_code',
                'attr_list',
                'def_list',
                'footnotes',
                'md_in_html'
            ],
            extension_configs={
                'toc': {
                    'permalink': True,
                    'baselevel': 1
                }
            }
        )

    def parse_content(self, content: str, file_path: str) -> ParsedContent:
        """
        Parse markdown content into structured format

        Args:
            content: Raw markdown content
            file_path: Path to source file for context

        Returns:
            ParsedContent: Structured content object

        Raises:
            DocumentLoaderError: If parsing fails
        """
        try:
            # Convert markdown to HTML for processing
            html_content = self.md.convert(content)

            # Extract sections
            sections = self._extract_sections(content)

            # Extract headers
            headers = self._extract_headers(content)

            # Extract tables
            tables = self._extract_tables(content)

            # Extract links
            links = self._extract_links(content)

            # Calculate metrics
            word_count = len(content.split())
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])

            return ParsedContent(
                sections=sections,
                raw_text=content,
                word_count=word_count,
                paragraph_count=paragraph_count,
                headers=headers,
                tables=tables,
                links=links
            )

        except Exception as e:
            logger.error(f"Failed to parse markdown content from {file_path}: {str(e)}")
            raise DocumentLoaderError(f"Markdown parsing failed: {str(e)}")

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content"""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Check for headers
            if line.startswith('#'):
                # Save previous section if exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line.strip('#').strip()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _extract_headers(self, content: str) -> List[str]:
        """Extract all headers from markdown content"""
        headers = []
        for line in content.split('\n'):
            if line.startswith('#'):
                header = line.strip('#').strip()
                if header:
                    headers.append(header)
        return headers

    def _extract_tables(self, content: str) -> List[Dict[str, any]]:
        """Extract tables from markdown content"""
        tables = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for table pattern (pipe-separated)
            if '|' in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # Check if next line is separator (contains dashes)
                if '|' in next_line and '-' in next_line:
                    table_data = self._parse_table(lines, i)
                    if table_data:
                        tables.append(table_data)
                        i += table_data.get('rows_processed', 2)
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

        return tables

    def _parse_table(self, lines: List[str], start_idx: int) -> Optional[Dict[str, any]]:
        """Parse a single table starting at given index"""
        try:
            # Header row
            header_line = lines[start_idx].strip()
            if not header_line.startswith('|') or not header_line.endswith('|'):
                return None

            headers = [h.strip() for h in header_line.split('|')[1:-1]]

            # Separator row (skip)
            sep_idx = start_idx + 1
            if sep_idx >= len(lines):
                return None

            # Data rows
            rows = []
            row_idx = sep_idx + 1

            while row_idx < len(lines):
                line = lines[row_idx].strip()
                if not line or not line.startswith('|'):
                    break

                if line.endswith('|'):
                    row_data = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row_data) == len(headers):
                        row_dict = dict(zip(headers, row_data))
                        rows.append(row_dict)

                row_idx += 1

            return {
                'headers': headers,
                'rows': rows,
                'rows_processed': row_idx - start_idx
            }

        except Exception as e:
            logger.warning(f"Failed to parse table at line {start_idx}: {str(e)}")
            return None

    def _extract_links(self, content: str) -> List[str]:
        """Extract links from markdown content"""
        # Pattern for markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        # Pattern for direct URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'

        links = []

        # Extract markdown links
        for match in re.finditer(link_pattern, content):
            url = match.group(2)
            if url not in links:
                links.append(url)

        # Extract direct URLs
        for match in re.finditer(url_pattern, content):
            url = match.group(0)
            if url not in links:
                links.append(url)

        return links


class DocumentChunker:
    """Handles document chunking for large files"""

    def __init__(self, config: Optional[LoaderConfig] = None):
        self.config = config or LoaderConfig()

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict[str, any]]:
        """
        Chunk text into smaller pieces for processing

        Args:
            text: Text to chunk
            metadata: Optional metadata to include with chunks

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if len(text) <= self.config.chunk_size:
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                'chunk_index': 0,
                'total_chunks': 1,
                'start_char': 0,
                'end_char': len(text)
            })
            return [{
                'text': text,
                'metadata': chunk_metadata,
                'chunk_index': 0
            }]

        chunks = []
        chunk_index = 0
        start = 0

        while start < len(text):
            end = start + self.config.chunk_size

            # Try to find a good break point (sentence or paragraph end)
            if end < len(text):
                # Look for sentence end within overlap distance
                for i in range(end, max(start, end - self.config.chunk_overlap), -1):
                    if text[i:i+1] in '.!?\n':
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata.update({
                    'chunk_index': chunk_index,
                    'start_char': start,
                    'end_char': end
                })

                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata,
                    'chunk_index': chunk_index
                })

                chunk_index += 1

            # Move start position with overlap
            start = max(start + 1, end - self.config.chunk_overlap)

        # Update total chunks info
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)

        return chunks


class DirectoryLoader:
    """Loads and validates documents from directories"""

    def __init__(self, config: Optional[LoaderConfig] = None):
        self.config = config or LoaderConfig()
        self.parser = MarkdownParser(config)
        self.chunker = DocumentChunker(config)

    def load_documents(self, directory_path: Union[str, Path]) -> List[StartupDocument]:
        """
        Load all supported documents from directory

        Args:
            directory_path: Path to directory containing documents

        Returns:
            List of StartupDocument objects

        Raises:
            DocumentLoaderError: If directory access fails
        """
        directory = Path(directory_path)

        if not directory.exists():
            raise DocumentLoaderError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise DocumentLoaderError(f"Path is not a directory: {directory}")

        documents = []

        # Look for specific files mentioned in task
        target_files = ['analysis_results.md', 'public_data.md']

        for filename in target_files:
            file_path = directory / filename

            if file_path.exists():
                try:
                    document = self.load_file(file_path)
                    documents.append(document)
                    logger.info(f"Successfully loaded: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
                    # Continue with other files (graceful degradation)

        # Also load any other .md files
        for file_path in directory.glob("*.md"):
            if file_path.name not in target_files:
                try:
                    document = self.load_file(file_path)
                    documents.append(document)
                    logger.info(f"Successfully loaded additional file: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load {file_path.name}: {str(e)}")

        if not documents:
            logger.warning(f"No documents loaded from {directory}")

        return documents

    def load_file(self, file_path: Union[str, Path]) -> StartupDocument:
        """
        Load a single document file

        Args:
            file_path: Path to the document file

        Returns:
            StartupDocument object

        Raises:
            DocumentLoaderError: If file loading fails
        """
        file_path = Path(file_path)

        # Validate file
        self._validate_file(file_path)

        # Extract metadata
        metadata = self._extract_metadata(file_path)

        # Read content
        content_text = self._read_file_content(file_path)

        # Parse content
        parsed_content = self.parser.parse_content(content_text, str(file_path))

        # Determine document type
        doc_type = self._determine_document_type(file_path, parsed_content)

        # Create document
        document = StartupDocument(
            content=parsed_content,
            metadata=metadata,
            document_type=doc_type,
            title=self._extract_title(parsed_content),
            version="1.0",
            tags=self._extract_tags(file_path, parsed_content),
            processed_at=datetime.now()
        )

        return document

    def _validate_file(self, file_path: Path):
        """Validate file existence, size, and accessibility"""
        if not file_path.exists():
            raise DocumentLoaderError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise DocumentLoaderError(f"Path is not a file: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise DocumentLoaderError(f"File is not readable: {file_path}")

        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.config.max_file_size_mb:
            raise DocumentLoaderError(
                f"File too large: {size_mb:.2f}MB > {self.config.max_file_size_mb}MB"
            )

        # Validate markdown format
        if file_path.suffix.lower() != '.md':
            logger.warning(f"File is not markdown: {file_path}")

    def _extract_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract file metadata"""
        stat = file_path.stat()

        return DocumentMetadata(
            file_path=str(file_path.absolute()),
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            creation_time=datetime.fromtimestamp(stat.st_ctime),
            file_extension=file_path.suffix.lower(),
            encoding='utf-8'  # Will be validated during reading
        )

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection"""
        content = None
        encoding_used = None

        for encoding in self.config.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    encoding_used = encoding
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise DocumentLoaderError(
                f"Could not decode file with any supported encoding: {file_path}"
            )

        logger.debug(f"File {file_path.name} read with encoding: {encoding_used}")
        return content

    def _determine_document_type(self, file_path: Path, content: ParsedContent) -> str:
        """Determine document type based on filename and content"""
        filename = file_path.name.lower()

        # Check filename patterns
        if 'analysis' in filename or 'result' in filename:
            return 'market_analysis'
        elif 'public' in filename or 'data' in filename:
            return 'business_plan'
        elif 'pitch' in filename or 'deck' in filename:
            return 'pitch_deck'
        elif 'financial' in filename or 'finance' in filename:
            return 'financial_report'

        # Check content for clues
        text_lower = content.raw_text.lower()
        if any(word in text_lower for word in ['revenue', 'funding', 'investment']):
            return 'pitch_deck'
        elif any(word in text_lower for word in ['market', 'competition', 'analysis']):
            return 'market_analysis'

        return 'other'

    def _extract_title(self, content: ParsedContent) -> Optional[str]:
        """Extract document title from content"""
        if content.headers:
            # Use first header as title
            return content.headers[0]

        # Look for title in sections
        if 'title' in content.sections:
            return content.sections['title'].strip()

        # Use first line if it looks like a title
        first_lines = content.raw_text.split('\n')[:3]
        for line in first_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line

        return None

    def _extract_tags(self, file_path: Path, content: ParsedContent) -> List[str]:
        """Extract relevant tags from filename and content"""
        tags = []

        # Add filename-based tags
        filename = file_path.name.lower()
        if 'analysis' in filename:
            tags.append('analysis')
        if 'public' in filename:
            tags.append('public-data')
        if 'result' in filename:
            tags.append('results')

        # Add content-based tags
        text_lower = content.raw_text.lower()
        tag_keywords = {
            'ai': ['artificial intelligence', 'machine learning', 'ai', 'ml'],
            'fintech': ['financial', 'payment', 'banking', 'fintech'],
            'data': ['data analytics', 'data', 'analytics'],
            'saas': ['software as a service', 'saas', 'subscription'],
            'marketplace': ['marketplace', 'platform', 'e-commerce']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)

        return list(set(tags))  # Remove duplicates

    def create_langchain_documents(self, documents: List[StartupDocument]) -> List[LangChainDocument]:
        """
        Convert StartupDocument objects to LangChain Document objects

        Args:
            documents: List of StartupDocument objects

        Returns:
            List of LangChain Document objects with chunking applied
        """
        langchain_docs = []

        for doc in documents:
            # Create chunks from the document content
            chunks = self.chunker.chunk_text(
                doc.content.raw_text,
                metadata={
                    'source': doc.metadata.file_path,
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'file_size': doc.metadata.size,
                    'tags': doc.tags,
                    'word_count': doc.content.word_count,
                    'processed_at': doc.processed_at.isoformat()
                }
            )

            # Convert each chunk to LangChain Document
            for chunk in chunks:
                langchain_doc = LangChainDocument(
                    page_content=chunk['text'],
                    metadata=chunk['metadata']
                )
                langchain_docs.append(langchain_doc)

        return langchain_docs


# Convenience functions for easy usage
def load_startup_documents(directory_path: Union[str, Path] = None) -> List[StartupDocument]:
    """
    Convenience function to load startup documents from default or specified directory

    Args:
        directory_path: Optional directory path (defaults to results directory)

    Returns:
        List of StartupDocument objects
    """
    if directory_path is None:
        directory_path = Config.RESULTS_DIR

    loader = DirectoryLoader()
    return loader.load_documents(directory_path)


def load_as_langchain_documents(directory_path: Union[str, Path] = None) -> List[LangChainDocument]:
    """
    Convenience function to load documents directly as LangChain Documents

    Args:
        directory_path: Optional directory path (defaults to results directory)

    Returns:
        List of LangChain Document objects
    """
    documents = load_startup_documents(directory_path)
    loader = DirectoryLoader()
    return loader.create_langchain_documents(documents)