# IntelligentAnalyzer Setup Guide

## Overview
The IntelligentAnalyzer is a comprehensive Python module that analyzes prompts using Gemini LLM with advanced web scraping and Google search integration capabilities.

## Features
- **Gemini LLM Integration**: Uses Google's Gemini API for intelligent analysis
- **Google Search**: Automated Google search with customizable result limits
- **Advanced Web Scraping**: 
  - Basic scraping with requests + BeautifulSoup
  - JavaScript rendering with Selenium
  - Parallel processing for multiple URLs
- **Comprehensive Error Handling**: Robust error handling and logging
- **Multiple Export Formats**: JSON, Markdown, and plain text exports
- **Context Management**: Automatic resource cleanup

## Installation

### 1. Install Dependencies
The required dependencies are already added to `pyproject.toml`. Install them using:

```bash
pip install -e .
```

Or install individual packages:
```bash
pip install google-generativeai selenium googlesearch-python beautifulsoup4 lxml fake-useragent requests
```

### 2. Chrome WebDriver Setup
For Selenium functionality, you need Chrome WebDriver:

**Option A: Using ChromeDriver Manager (Recommended)**
```bash
pip install webdriver-manager
```

**Option B: Manual Installation**
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Add to your PATH or place in project directory

### 3. Environment Variables
Create a `.env` file in your project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Getting Gemini API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and add to your `.env` file

## Usage Examples

### Basic Usage
```python
from src.intelligent_analyzer import IntelligentAnalyzer

# Initialize analyzer
analyzer = IntelligentAnalyzer()

# Analyze a prompt
result = analyzer.analyze_prompt(
    "What are the latest AI developments?",
    enable_search=True,
    enable_scraping=True
)

print(f"Confidence: {result.confidence_score}")
print(result.gemini_response)

# Cleanup
analyzer.cleanup()
```

### Using as Context Manager
```python
with IntelligentAnalyzer() as analyzer:
    result = analyzer.analyze_prompt("Your prompt here")
    # Automatic cleanup when exiting context
```

### Custom Configuration
```python
analyzer = IntelligentAnalyzer(
    max_search_results=10,
    timeout=45,
    enable_javascript=True,
    log_level=logging.DEBUG
)
```

### Advanced Scraping
```python
# Use Selenium for JavaScript-heavy sites
result = analyzer.analyze_prompt(
    "Modern web frameworks comparison",
    enable_search=True,
    enable_scraping=True,
    use_selenium=True
)
```

### Export Results
```python
# Export to different formats
json_export = analyzer.export_result(result, 'json')
markdown_export = analyzer.export_result(result, 'markdown')
text_export = analyzer.export_result(result, 'txt')
```

## Configuration Options

### IntelligentAnalyzer Parameters
- `gemini_api_key`: Google Gemini API key (optional if set in env)
- `max_search_results`: Maximum search results to process (default: 10)
- `timeout`: Request timeout in seconds (default: 30)
- `enable_javascript`: Enable JavaScript rendering capability (default: True)
- `log_level`: Logging level (default: logging.INFO)

### analyze_prompt Parameters
- `prompt`: User prompt to analyze (required)
- `enable_search`: Perform Google search (default: True)
- `enable_scraping`: Scrape web content (default: True)
- `use_selenium`: Use Selenium for scraping (auto-detect if None)

## Return Objects

### AnalysisResult
- `query`: Original user prompt
- `gemini_response`: Gemini's analysis
- `search_results`: List of SearchResult objects
- `web_content`: List of scraped content dictionaries
- `confidence_score`: Analysis confidence (0.0-1.0)
- `timestamp`: Analysis timestamp
- `metadata`: Additional processing information

### SearchResult
- `title`: Page title
- `url`: Page URL
- `snippet`: Search result snippet
- `content`: Scraped content (if available)
- `metadata`: Additional metadata

## Error Handling

The module includes comprehensive error handling:
- Network timeouts and connection errors
- Invalid URLs and scraping failures
- API rate limits and authentication errors
- Selenium WebDriver issues
- Graceful degradation when services fail

## Logging

Logs are written to:
- Console (configurable level)
- File: `intelligent_analyzer.log`

Log levels:
- DEBUG: Detailed debugging information
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error messages

## Performance Considerations

### Optimization Tips
1. **Parallel Processing**: Multiple URLs scraped concurrently
2. **Smart Selenium Usage**: Auto-detection of JavaScript requirements
3. **Request Caching**: Session reuse for better performance
4. **Content Limiting**: Automatic content truncation to manage memory

### Resource Management
- Use context managers for automatic cleanup
- Call `cleanup()` method explicitly when not using context managers
- Monitor memory usage for large-scale scraping operations

## Troubleshooting

### Common Issues

**1. ChromeDriver Not Found**
```
Error: ChromeDriver not found in PATH
```
Solution: Install webdriver-manager or add ChromeDriver to PATH

**2. Gemini API Key Error**
```
Error: Gemini API key is required
```
Solution: Set GEMINI_API_KEY environment variable

**3. Rate Limiting**
```
Error: Too many requests
```
Solution: Increase delays between requests or reduce max_search_results

**4. Timeout Errors**
```
Error: Request timeout
```
Solution: Increase timeout parameter or check network connection

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
analyzer = IntelligentAnalyzer(log_level=logging.DEBUG)
```

## Best Practices

1. **Use Context Managers**: Always use `with` statement for automatic cleanup
2. **Handle Exceptions**: Wrap calls in try-except blocks for production use
3. **Rate Limiting**: Be respectful of API and website rate limits
4. **Content Validation**: Validate scraped content before processing
5. **Resource Monitoring**: Monitor memory and CPU usage for large operations

## Examples

See `examples/analyzer_example.py` for comprehensive usage examples including:
- Basic analysis
- Advanced scraping with Selenium
- Custom search operations
- Context manager usage
- Result export formats

## Security Considerations

- Store API keys securely using environment variables
- Validate URLs before scraping to prevent SSRF attacks
- Use appropriate user agents and respect robots.txt
- Implement rate limiting to avoid being blocked
- Sanitize and validate all user inputs

## License and Support

This module is part of the ai-shark project. For issues or questions:
1. Check the troubleshooting section above
2. Review example usage in `examples/`
3. Enable debug logging for detailed error information