"""
Unit tests for Document Loader and Parser (Task 3)
Tests document loading, parsing, chunking, and LangChain integration
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open

from src.utils.document_loader import (
    DirectoryLoader, MarkdownParser, DocumentChunker, LoaderConfig,
    DocumentLoaderError, load_startup_documents, load_as_langchain_documents
)
from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent


class TestLoaderConfig:
    """Test LoaderConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = LoaderConfig()
        assert config.max_file_size_mb == 50
        assert config.chunk_size == 4000
        assert config.chunk_overlap == 200
        assert 'utf-8' in config.supported_encodings

    def test_custom_config(self):
        """Test custom configuration"""
        config = LoaderConfig(
            max_file_size_mb=100,
            chunk_size=2000,
            chunk_overlap=100,
            supported_encodings=['utf-8']
        )
        assert config.max_file_size_mb == 100
        assert config.chunk_size == 2000
        assert config.chunk_overlap == 100
        assert config.supported_encodings == ['utf-8']


class TestMarkdownParser:
    """Test MarkdownParser functionality"""

    def test_parser_initialization(self):
        """Test parser initialization"""
        parser = MarkdownParser()
        assert parser.config is not None
        assert parser.md is not None

    def test_basic_content_parsing(self):
        """Test basic markdown content parsing"""
        parser = MarkdownParser()
        content = """# Title

## Section 1
This is content for section 1.

## Section 2
This is content for section 2.

Some additional content here.
"""

        result = parser.parse_content(content, "test.md")

        assert isinstance(result, ParsedContent)
        assert "Title" in result.sections
        assert "Section 1" in result.sections
        assert "Section 2" in result.sections
        assert result.word_count > 0
        assert len(result.headers) >= 3

    def test_section_extraction(self):
        """Test section extraction from markdown"""
        parser = MarkdownParser()
        content = """# Main Title

Content under main title.

## Sub Section

Content under sub section.

### Deep Section

Deep content here.
"""

        sections = parser._extract_sections(content)
        assert "Main Title" in sections
        assert "Sub Section" in sections
        assert "Deep Section" in sections

    def test_header_extraction(self):
        """Test header extraction"""
        parser = MarkdownParser()
        content = """# Header 1
## Header 2
### Header 3
Regular text
"""

        headers = parser._extract_headers(content)
        assert headers == ["Header 1", "Header 2", "Header 3"]

    def test_table_extraction(self):
        """Test table extraction from markdown"""
        parser = MarkdownParser()
        content = """
| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |

Some other content.

| Product | Price |
|---------|-------|
| Apple   | $1.50 |
"""

        tables = parser._extract_tables(content)
        assert len(tables) == 2
        assert tables[0]['headers'] == ['Name', 'Age', 'City']
        assert len(tables[0]['rows']) == 2
        assert tables[1]['headers'] == ['Product', 'Price']

    def test_link_extraction(self):
        """Test link extraction from markdown"""
        parser = MarkdownParser()
        content = """
Check out [Google](https://google.com) and visit https://github.com directly.
Also see [Documentation](https://docs.example.com/guide).
"""

        links = parser._extract_links(content)
        assert "https://google.com" in links
        assert "https://github.com" in links
        assert "https://docs.example.com/guide" in links

    def test_empty_content_parsing(self):
        """Test parsing empty or minimal content"""
        parser = MarkdownParser()

        result = parser.parse_content("", "empty.md")
        assert result.word_count == 0
        assert len(result.sections) == 0

        result = parser.parse_content("   \n\n   ", "whitespace.md")
        assert result.word_count == 0

    def test_parsing_error_handling(self):
        """Test error handling in parsing"""
        parser = MarkdownParser()

        # Mock markdown conversion to raise an exception
        with patch.object(parser.md, 'convert', side_effect=Exception("Parse error")):
            with pytest.raises(DocumentLoaderError):
                parser.parse_content("# Test", "test.md")


class TestDocumentChunker:
    """Test DocumentChunker functionality"""

    def test_chunker_initialization(self):
        """Test chunker initialization"""
        chunker = DocumentChunker()
        assert chunker.config is not None

    def test_small_text_chunking(self):
        """Test chunking of small text (no chunking needed)"""
        chunker = DocumentChunker()
        text = "This is a small text that doesn't need chunking."

        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
        assert chunks[0]['chunk_index'] == 0
        assert chunks[0]['metadata']['total_chunks'] == 1

    def test_large_text_chunking(self):
        """Test chunking of large text"""
        chunker = DocumentChunker(LoaderConfig(chunk_size=100, chunk_overlap=20))
        text = "This is a sentence. " * 50  # Create long text

        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1

        # Check metadata
        for i, chunk in enumerate(chunks):
            assert chunk['chunk_index'] == i
            assert chunk['metadata']['total_chunks'] == len(chunks)
            assert 'start_char' in chunk['metadata']
            assert 'end_char' in chunk['metadata']

    def test_chunk_overlap(self):
        """Test chunk overlap functionality"""
        chunker = DocumentChunker(LoaderConfig(chunk_size=50, chunk_overlap=10))
        text = "Word " * 30  # Create text longer than chunk size

        chunks = chunker.chunk_text(text)
        assert len(chunks) >= 2

        # Verify overlap exists between chunks
        if len(chunks) > 1:
            first_chunk_end = chunks[0]['metadata']['end_char']
            second_chunk_start = chunks[1]['metadata']['start_char']
            assert first_chunk_end > second_chunk_start

    def test_chunk_with_metadata(self):
        """Test chunking with custom metadata"""
        chunker = DocumentChunker()
        text = "Short text"
        metadata = {"source": "test.md", "title": "Test Document"}

        chunks = chunker.chunk_text(text, metadata)
        assert chunks[0]['metadata']['source'] == "test.md"
        assert chunks[0]['metadata']['title'] == "Test Document"


class TestDirectoryLoader:
    """Test DirectoryLoader functionality"""

    def test_loader_initialization(self):
        """Test loader initialization"""
        loader = DirectoryLoader()
        assert loader.config is not None
        assert loader.parser is not None
        assert loader.chunker is not None

    def test_file_validation(self):
        """Test file validation methods"""
        loader = DirectoryLoader()

        # Test non-existent file
        with pytest.raises(DocumentLoaderError):
            loader._validate_file(Path("nonexistent.md"))

    def test_metadata_extraction(self):
        """Test metadata extraction from file"""
        loader = DirectoryLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nContent here.")
            temp_path = Path(f.name)

        try:
            metadata = loader._extract_metadata(temp_path)

            assert isinstance(metadata, DocumentMetadata)
            assert metadata.file_path == str(temp_path.absolute())
            assert metadata.size > 0
            assert metadata.file_extension == '.md'
            assert isinstance(metadata.last_modified, datetime)
        finally:
            temp_path.unlink()

    def test_content_reading(self):
        """Test file content reading with encoding detection"""
        loader = DirectoryLoader()
        content = "# Test Document\n\nThis is test content."

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            read_content = loader._read_file_content(temp_path)
            assert read_content == content
        finally:
            temp_path.unlink()

    def test_document_type_determination(self):
        """Test document type determination"""
        loader = DirectoryLoader()

        # Test filename-based detection
        content = ParsedContent(sections={}, raw_text="test content", word_count=2)

        assert loader._determine_document_type(Path("analysis_results.md"), content) == "market_analysis"
        assert loader._determine_document_type(Path("public_data.md"), content) == "business_plan"
        assert loader._determine_document_type(Path("pitch_deck.md"), content) == "pitch_deck"

    def test_title_extraction(self):
        """Test title extraction from content"""
        loader = DirectoryLoader()

        # Test header-based title
        content = ParsedContent(
            sections={},
            raw_text="# Main Title\n\nContent here.",
            word_count=4,
            headers=["Main Title", "Section 1"]
        )
        assert loader._extract_title(content) == "Main Title"

        # Test content without headers
        content = ParsedContent(
            sections={"title": "Document Title"},
            raw_text="Document Title\n\nContent here.",
            word_count=4,
            headers=[]
        )
        assert loader._extract_title(content) == "Document Title"

    def test_tag_extraction(self):
        """Test tag extraction from filename and content"""
        loader = DirectoryLoader()

        content = ParsedContent(
            sections={},
            raw_text="This is about artificial intelligence and machine learning in fintech.",
            word_count=11,
            headers=[]
        )

        tags = loader._extract_tags(Path("analysis_results.md"), content)
        assert "analysis" in tags
        assert "ai" in tags
        assert "fintech" in tags

    @patch('builtins.open', new_callable=mock_open, read_data="# Test Doc\n\nContent here.")
    @patch('os.access', return_value=True)
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    @patch('pathlib.Path.stat')
    def test_load_file_success(self, mock_stat, mock_is_file, mock_exists, mock_access, mock_file):
        """Test successful file loading"""
        # Mock file stats
        mock_stat.return_value.st_size = 1000
        mock_stat.return_value.st_mtime = 1609459200  # 2021-01-01
        mock_stat.return_value.st_ctime = 1609459200

        loader = DirectoryLoader()

        document = loader.load_file(Path("test.md"))

        assert isinstance(document, StartupDocument)
        assert document.title == "Test Doc"
        assert document.metadata.size == 1000

    def test_langchain_document_creation(self):
        """Test LangChain document creation"""
        loader = DirectoryLoader()

        # Create a sample startup document
        metadata = DocumentMetadata(
            file_path="/test/sample.md",
            size=500,
            last_modified=datetime.now(),
            file_extension=".md"
        )

        content = ParsedContent(
            sections={"intro": "Introduction"},
            raw_text="Introduction content here.",
            word_count=4
        )

        startup_doc = StartupDocument(
            content=content,
            metadata=metadata,
            document_type="pitch_deck",
            title="Sample Document"
        )

        langchain_docs = loader.create_langchain_documents([startup_doc])

        assert len(langchain_docs) >= 1
        assert all(hasattr(doc, 'page_content') for doc in langchain_docs)
        assert all(hasattr(doc, 'metadata') for doc in langchain_docs)
        assert langchain_docs[0].metadata['title'] == "Sample Document"


class TestDirectoryLoading:
    """Test directory loading functionality"""

    def test_load_nonexistent_directory(self):
        """Test loading from non-existent directory"""
        loader = DirectoryLoader()

        with pytest.raises(DocumentLoaderError):
            loader.load_documents("/nonexistent/directory")

    def test_load_empty_directory(self):
        """Test loading from empty directory"""
        loader = DirectoryLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            documents = loader.load_documents(temp_dir)
            assert documents == []

    def test_load_directory_with_files(self):
        """Test loading directory with actual markdown files"""
        loader = DirectoryLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "analysis_results.md").write_text("# Analysis Results\n\nContent here.")
            (temp_path / "public_data.md").write_text("# Public Data\n\nMore content.")
            (temp_path / "other.md").write_text("# Other Document\n\nOther content.")

            documents = loader.load_documents(temp_dir)

            assert len(documents) == 3
            assert all(isinstance(doc, StartupDocument) for doc in documents)

            # Check that target files are included
            titles = [doc.title for doc in documents]
            assert "Analysis Results" in titles
            assert "Public Data" in titles


class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch('src.utils.document_loader.DirectoryLoader')
    def test_load_startup_documents(self, mock_loader_class):
        """Test load_startup_documents convenience function"""
        mock_loader = mock_loader_class.return_value
        mock_loader.load_documents.return_value = []

        result = load_startup_documents("/test/path")

        mock_loader_class.assert_called_once()
        mock_loader.load_documents.assert_called_once_with("/test/path")

    @patch('src.utils.document_loader.DirectoryLoader')
    def test_load_as_langchain_documents(self, mock_loader_class):
        """Test load_as_langchain_documents convenience function"""
        mock_loader = mock_loader_class.return_value
        mock_loader.load_documents.return_value = []
        mock_loader.create_langchain_documents.return_value = []

        result = load_as_langchain_documents("/test/path")

        mock_loader_class.assert_called_once()
        mock_loader.load_documents.assert_called_once_with("/test/path")
        mock_loader.create_langchain_documents.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_large_file_rejection(self):
        """Test rejection of files that are too large"""
        config = LoaderConfig(max_file_size_mb=0.001)  # Very small limit
        loader = DirectoryLoader(config)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Large File\n" + "Content " * 1000)  # Write enough to exceed limit
            temp_path = Path(f.name)

        try:
            with pytest.raises(DocumentLoaderError, match="File too large"):
                loader._validate_file(temp_path)
        finally:
            temp_path.unlink()

    def test_encoding_error_handling(self):
        """Test handling of files with encoding issues"""
        loader = DirectoryLoader(LoaderConfig(supported_encodings=['ascii']))  # Limited encoding

        # Create file with unicode content
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as f:
            f.write("# Test\n\nUnicode: café résumé".encode('utf-8'))
            temp_path = Path(f.name)

        try:
            with pytest.raises(DocumentLoaderError, match="Could not decode file"):
                loader._read_file_content(temp_path)
        finally:
            temp_path.unlink()

    def test_graceful_degradation(self):
        """Test graceful degradation when some files fail to load"""
        loader = DirectoryLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create one good file and one problematic file
            (temp_path / "good.md").write_text("# Good Document\n\nContent here.")

            # Create a file that will cause issues (we'll mock the error)
            (temp_path / "bad.md").write_text("# Bad Document\n\nContent here.")

            # Mock the load_file method to raise an error for bad.md
            original_load_file = loader.load_file

            def mock_load_file(file_path):
                if file_path.name == "bad.md":
                    raise Exception("Simulated loading error")
                return original_load_file(file_path)

            loader.load_file = mock_load_file

            # Should still load the good file
            documents = loader.load_documents(temp_dir)
            assert len(documents) == 1
            assert documents[0].title == "Good Document"


class TestRealFileLoading:
    """Test loading with real files from results directory"""

    def test_load_actual_results_files(self):
        """Test loading the actual analysis_results.md and public_data.md files"""
        from task_config import Config

        # Only run if files exist
        results_dir = Config.RESULTS_DIR
        analysis_file = results_dir / "analysis_results.md"
        public_file = results_dir / "public_data.md"

        if not (analysis_file.exists() and public_file.exists()):
            pytest.skip("Real result files not found")

        loader = DirectoryLoader()
        documents = loader.load_documents(results_dir)

        # Should load at least the two target files
        assert len(documents) >= 2

        # Check that we have documents with expected characteristics
        titles = [doc.title for doc in documents if doc.title]
        assert len(titles) > 0

        # Check that content was parsed
        for doc in documents:
            assert doc.content.word_count > 0
            assert len(doc.content.raw_text) > 0

    def test_create_langchain_docs_from_real_files(self):
        """Test creating LangChain documents from real files"""
        from task_config import Config

        results_dir = Config.RESULTS_DIR
        if not (results_dir / "analysis_results.md").exists():
            pytest.skip("Real result files not found")

        langchain_docs = load_as_langchain_documents(results_dir)

        assert len(langchain_docs) > 0

        # Check LangChain document structure
        for doc in langchain_docs:
            assert hasattr(doc, 'page_content')
            assert hasattr(doc, 'metadata')
            assert len(doc.page_content) > 0
            assert 'source' in doc.metadata


if __name__ == "__main__":
    pytest.main([__file__])