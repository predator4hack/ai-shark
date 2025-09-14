"""
Document Loader Demo - Task 3 Completion
Demonstrates all document loading and parsing functionality
"""

import logging
from pathlib import Path
from src.utils.document_loader import (
    DirectoryLoader, MarkdownParser, DocumentChunker,
    load_startup_documents, load_as_langchain_documents
)
from task_config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def demo_markdown_parser():
    """Demonstrate markdown parsing capabilities"""
    print("\n=== Markdown Parser Demo ===")

    parser = MarkdownParser()

    sample_markdown = """# Startup Analysis Demo

## Executive Summary
This is a revolutionary fintech startup that aims to disrupt the traditional banking sector.

## Market Opportunity
The global fintech market is valued at $127 billion and growing at 25% CAGR.

| Year | Market Size | Growth Rate |
|------|-------------|-------------|
| 2023 | $127B       | 25%         |
| 2024 | $159B       | 25%         |
| 2025 | $199B       | 25%         |

## Product Features
- AI-powered personal finance management
- Automated savings and investment
- Real-time spending insights

For more information, visit [our website](https://example.com) or check out https://docs.example.com.

## Contact
Email us at info@startup.com for partnerships.
"""

    parsed = parser.parse_content(sample_markdown, "demo.md")

    print(f"✓ Parsed content:")
    print(f"  - Sections: {len(parsed.sections)}")
    print(f"  - Headers: {parsed.headers}")
    print(f"  - Word count: {parsed.word_count}")
    print(f"  - Tables found: {len(parsed.tables)}")
    print(f"  - Links found: {len(parsed.links)}")

    if parsed.tables:
        print(f"  - Table columns: {parsed.tables[0]['headers']}")

    print(f"  - Links: {parsed.links}")


def demo_document_chunker():
    """Demonstrate document chunking functionality"""
    print("\n=== Document Chunker Demo ===")

    chunker = DocumentChunker()

    # Create a longer text for chunking
    long_text = """This is a demonstration of document chunking functionality. """ * 100

    chunks = chunker.chunk_text(long_text, metadata={"source": "demo.md", "type": "test"})

    print(f"✓ Chunked long text:")
    print(f"  - Original length: {len(long_text)} characters")
    print(f"  - Number of chunks: {len(chunks)}")
    print(f"  - Average chunk size: {sum(len(c['text']) for c in chunks) // len(chunks)} characters")

    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"  - Chunk {i}: {len(chunk['text'])} chars, metadata keys: {list(chunk['metadata'].keys())}")


def demo_directory_loader():
    """Demonstrate directory loading functionality"""
    print("\n=== Directory Loader Demo ===")

    loader = DirectoryLoader()

    # Load documents from results directory
    try:
        documents = loader.load_documents(Config.RESULTS_DIR)

        print(f"✓ Loaded {len(documents)} documents from {Config.RESULTS_DIR}")

        for doc in documents:
            print(f"  - Title: {doc.title}")
            print(f"    Type: {doc.document_type}")
            print(f"    Words: {doc.content.word_count}")
            print(f"    Size: {doc.metadata.size} bytes")
            print(f"    Tags: {doc.tags}")
            print(f"    Sections: {len(doc.content.sections)}")

            if doc.content.tables:
                print(f"    Tables: {len(doc.content.tables)}")

            if doc.content.links:
                print(f"    Links: {len(doc.content.links)}")

            print()

    except Exception as e:
        print(f"❌ Error loading documents: {e}")


def demo_langchain_integration():
    """Demonstrate LangChain document integration"""
    print("\n=== LangChain Integration Demo ===")

    try:
        # Load as LangChain documents
        langchain_docs = load_as_langchain_documents()

        print(f"✓ Created {len(langchain_docs)} LangChain document chunks")

        # Show sample chunks
        for i, doc in enumerate(langchain_docs[:3]):
            print(f"  - Chunk {i+1}:")
            print(f"    Content length: {len(doc.page_content)} characters")
            print(f"    Metadata keys: {list(doc.metadata.keys())}")
            print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Title: {doc.metadata.get('title', 'Unknown')}")
            print(f"    Chunk index: {doc.metadata.get('chunk_index', 'Unknown')}")
            print(f"    Preview: {doc.page_content[:100]}...")
            print()

    except Exception as e:
        print(f"❌ Error creating LangChain documents: {e}")


def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print("\n=== Error Handling Demo ===")

    loader = DirectoryLoader()

    # Test loading non-existent directory
    try:
        loader.load_documents("/nonexistent/directory")
        print("❌ Should have raised an error for non-existent directory")
    except Exception as e:
        print(f"✓ Correctly handled non-existent directory: {type(e).__name__}")

    # Test loading non-existent file
    try:
        loader.load_file("/nonexistent/file.md")
        print("❌ Should have raised an error for non-existent file")
    except Exception as e:
        print(f"✓ Correctly handled non-existent file: {type(e).__name__}")

    # Test graceful degradation with empty directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        documents = loader.load_documents(temp_dir)
        print(f"✓ Gracefully handled empty directory: {len(documents)} documents loaded")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n=== Convenience Functions Demo ===")

    # Test convenience function for loading startup documents
    try:
        documents = load_startup_documents()
        print(f"✓ load_startup_documents(): {len(documents)} documents")
    except Exception as e:
        print(f"❌ Error with convenience function: {e}")

    # Test convenience function for LangChain documents
    try:
        langchain_docs = load_as_langchain_documents()
        print(f"✓ load_as_langchain_documents(): {len(langchain_docs)} chunks")
    except Exception as e:
        print(f"❌ Error with LangChain convenience function: {e}")


def main():
    """Run all demos"""
    print("🚀 Document Loader and Parser Demo - Task 3")
    print("=" * 50)

    demo_markdown_parser()
    demo_document_chunker()
    demo_directory_loader()
    demo_langchain_integration()
    demo_error_handling()
    demo_convenience_functions()

    print("\n🎉 Task 3 Completion Demo Finished!")
    print("\nFeatures Demonstrated:")
    print("✓ Markdown parsing with sections, headers, tables, and links")
    print("✓ Document chunking for large files")
    print("✓ Directory loading with file validation")
    print("✓ LangChain Document integration")
    print("✓ Comprehensive error handling")
    print("✓ Graceful degradation for partial failures")
    print("✓ Metadata extraction and document typing")
    print("✓ Tag extraction and content analysis")
    print("✓ Convenience functions for easy usage")


if __name__ == "__main__":
    main()