# Document Loader Error Handling Documentation

## Overview

The Document Loader and Parser system (Task 3) implements comprehensive error handling to ensure robust operation when processing startup documents. This document describes the error handling strategies, common error scenarios, and recovery mechanisms.

## Error Handling Philosophy

The system follows these principles:

1. **Fail Fast**: Detect and report errors as early as possible
2. **Graceful Degradation**: Continue processing when partial failures occur
3. **Clear Messaging**: Provide descriptive error messages for debugging
4. **Recovery**: Attempt to continue processing other files when one fails
5. **Logging**: Comprehensive logging for debugging and monitoring

## Error Types and Handling

### 1. File System Errors

#### File Not Found
- **Error**: `DocumentLoaderError("File does not exist: {path}")`
- **Cause**: Specified file or directory doesn't exist
- **Handling**: Immediate failure with clear error message
- **Recovery**: None - caller must provide valid path

#### Permission Errors
- **Error**: `DocumentLoaderError("File is not readable: {path}")`
- **Cause**: Insufficient permissions to read file
- **Handling**: Immediate failure with permission error
- **Recovery**: None - requires permission fix

#### File Size Errors
- **Error**: `DocumentLoaderError("File too large: {size}MB > {limit}MB")`
- **Cause**: File exceeds configured size limit
- **Handling**: Rejection with size information
- **Recovery**: Increase size limit or process smaller files

### 2. Encoding and Content Errors

#### Encoding Detection Failure
- **Error**: `DocumentLoaderError("Could not decode file with any supported encoding")`
- **Cause**: File uses unsupported character encoding
- **Handling**: Try multiple encodings before failing
- **Recovery**: Add more encoding options to config

```python
# Example encoding fallback
supported_encodings = ['utf-8', 'latin-1', 'cp1252']
for encoding in supported_encodings:
    try:
        content = file.read(encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

#### Markdown Parsing Errors
- **Error**: `DocumentLoaderError("Markdown parsing failed: {error}")`
- **Cause**: Malformed markdown or internal parser error
- **Handling**: Log error and optionally continue with raw text
- **Recovery**: Fall back to plain text processing

### 3. Validation Errors

#### Invalid Document Structure
- **Error**: Pydantic validation errors from model creation
- **Cause**: Generated content doesn't match expected schema
- **Handling**: Log validation error and skip invalid parts
- **Recovery**: Use default values or simplified structure

#### Metadata Extraction Errors
- **Error**: Various metadata-related exceptions
- **Cause**: File system inconsistencies or corrupted metadata
- **Handling**: Use default metadata values
- **Recovery**: Continue with minimal metadata

### 4. Processing Errors

#### Content Processing Failures
- **Error**: Various processing exceptions during analysis
- **Cause**: Unexpected content structure or processing logic bugs
- **Handling**: Log error and continue with available data
- **Recovery**: Use partial results

#### Memory and Performance Issues
- **Error**: Memory exhaustion or timeout errors
- **Cause**: Very large files or inefficient processing
- **Handling**: Implement chunking and pagination
- **Recovery**: Process in smaller segments

## Error Handling Strategies

### 1. Directory Loading Strategy

When loading multiple files from a directory:

```python
documents = []
for filename in target_files:
    try:
        document = self.load_file(file_path)
        documents.append(document)
        logger.info(f"Successfully loaded: {filename}")
    except Exception as e:
        logger.error(f"Failed to load {filename}: {str(e)}")
        # Continue with other files (graceful degradation)
```

**Benefits:**
- Processes all valid files even if some fail
- Provides detailed logging for each file
- Returns partial results rather than complete failure

### 2. Parsing Strategy

When parsing markdown content:

```python
try:
    # Primary parsing attempt
    html_content = self.md.convert(content)
    sections = self._extract_sections(content)
    # ... other extractions
except Exception as e:
    logger.error(f"Failed to parse markdown: {str(e)}")
    raise DocumentLoaderError(f"Markdown parsing failed: {str(e)}")
```

**Benefits:**
- Clear error attribution
- Preserves original error context
- Enables debugging and fixes

### 3. Chunking Strategy

When chunking large documents:

```python
def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
    try:
        # Attempt smart chunking
        if len(text) <= self.config.chunk_size:
            return self._create_single_chunk(text, metadata)

        return self._create_multiple_chunks(text, metadata)
    except Exception as e:
        logger.warning(f"Chunking failed, using fallback: {str(e)}")
        # Fallback to simple splitting
        return self._simple_chunk_fallback(text, metadata)
```

**Benefits:**
- Graceful fallback to simpler methods
- Maintains functionality even with errors
- Logs issues for improvement

## Logging and Monitoring

### Log Levels

- **ERROR**: Critical failures that prevent processing
- **WARNING**: Issues that don't prevent processing but indicate problems
- **INFO**: Normal operation status and successful processing
- **DEBUG**: Detailed information for troubleshooting

### Log Messages

```python
# Success logging
logger.info(f"Successfully loaded: {filename}")
logger.info(f"Parsed {len(sections)} sections from {filename}")

# Warning logging
logger.warning(f"File is not markdown: {file_path}")
logger.warning(f"Failed to parse table at line {line_num}: {error}")

# Error logging
logger.error(f"Failed to load {filename}: {str(e)}")
logger.error(f"Could not decode file with any supported encoding: {file_path}")
```

### Error Context

All error messages include:
- File path or identifier
- Specific error description
- Context information (line numbers, section names, etc.)
- Suggested recovery actions when applicable

## Configuration for Error Handling

### LoaderConfig Options

```python
@dataclass
class LoaderConfig:
    max_file_size_mb: int = 50          # File size limit
    chunk_size: int = 4000              # Chunk size for large files
    chunk_overlap: int = 200            # Overlap between chunks
    supported_encodings: List[str] = None  # Encoding fallback list
```

### Customization

```python
# Strict configuration (fail fast)
strict_config = LoaderConfig(
    max_file_size_mb=10,
    supported_encodings=['utf-8']  # Only UTF-8
)

# Permissive configuration (graceful degradation)
permissive_config = LoaderConfig(
    max_file_size_mb=100,
    supported_encodings=['utf-8', 'latin-1', 'cp1252', 'ascii']
)
```

## Error Recovery Patterns

### 1. Retry with Fallback

```python
def load_with_fallback(self, file_path):
    try:
        return self.advanced_load(file_path)
    except ComplexError:
        logger.warning("Advanced loading failed, trying simple method")
        return self.simple_load(file_path)
```

### 2. Partial Processing

```python
def process_sections(self, content):
    results = {}
    for section_name, section_content in content.sections.items():
        try:
            results[section_name] = self.process_section(section_content)
        except Exception as e:
            logger.warning(f"Failed to process section {section_name}: {e}")
            results[section_name] = section_content  # Use raw content
    return results
```

### 3. Default Value Substitution

```python
def extract_metadata(self, file_path):
    try:
        return self._detailed_metadata(file_path)
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {e}")
        return self._minimal_metadata(file_path)
```

## Best Practices

### For Developers

1. **Always log errors** with sufficient context
2. **Use specific exception types** for different error categories
3. **Implement graceful degradation** where possible
4. **Test error scenarios** explicitly
5. **Document error conditions** and recovery strategies

### For Users

1. **Check log files** for detailed error information
2. **Verify file permissions** and accessibility
3. **Ensure files are not corrupted** or too large
4. **Use supported file formats** (markdown)
5. **Configure appropriate limits** for your use case

### Example Usage with Error Handling

```python
import logging
from src.utils.document_loader import load_startup_documents, DocumentLoaderError

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    # Load documents with automatic error handling
    documents = load_startup_documents("/path/to/documents")

    if not documents:
        print("No documents were loaded successfully")
    else:
        print(f"Successfully loaded {len(documents)} documents")

except DocumentLoaderError as e:
    print(f"Document loading failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Troubleshooting Common Issues

### Issue: "File does not exist"
- **Solution**: Check file path spelling and existence
- **Prevention**: Use absolute paths and verify before processing

### Issue: "Could not decode file"
- **Solution**: Check file encoding and add to supported_encodings
- **Prevention**: Ensure files are saved in UTF-8 encoding

### Issue: "File too large"
- **Solution**: Increase max_file_size_mb in config or split file
- **Prevention**: Monitor file sizes and implement preprocessing

### Issue: "Markdown parsing failed"
- **Solution**: Check markdown syntax and format
- **Prevention**: Validate markdown files before processing

### Issue: Memory errors during chunking
- **Solution**: Reduce chunk_size in configuration
- **Prevention**: Monitor memory usage and optimize chunk settings

## Monitoring and Alerts

### Key Metrics to Monitor

- Success rate of file loading
- Average processing time per file
- Error frequency by type
- Memory usage during processing
- File size distribution

### Alert Conditions

- Error rate exceeds 10%
- Individual file processing takes > 30 seconds
- Memory usage exceeds 80%
- Disk space for logs is low

This comprehensive error handling ensures the document loader remains robust and reliable even when processing diverse and potentially problematic input files.