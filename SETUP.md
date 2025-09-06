# VC Document Analyzer Setup Guide

This guide will help you set up and configure the VC Document Analyzer application.

## Prerequisites

-   Python 3.8 or higher
-   Google Cloud account with Gemini API access
-   Git (for cloning the repository)

## Installation

1. **Clone the repository** (if applicable):

    ```bash
    git clone <repository-url>
    cd vc-document-analyzer
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### 1. Google Gemini API Setup

1. **Get a Google API Key**:

    - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    - Sign in with your Google account
    - Create a new API key
    - Copy the API key for the next step

2. **Configure Environment Variables**:
    - Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    - Edit the `.env` file and add your API key:
        ```
        GOOGLE_API_KEY=your_actual_api_key_here
        ```

### 2. Application Configuration

The application uses the following configuration options (all optional with sensible defaults):

| Variable                | Default                 | Description                                   |
| ----------------------- | ----------------------- | --------------------------------------------- |
| `GOOGLE_API_KEY`        | _required_              | Your Google Gemini API key                    |
| `GEMINI_MODEL`          | `gemini-1.5-pro`        | Gemini model to use (supports multimodal)     |
| `GEMINI_TEMPERATURE`    | `0.1`                   | Temperature for AI responses (0.0-1.0)        |
| `GEMINI_MAX_TOKENS`     | `4096`                  | Maximum tokens in AI responses                |
| `GEMINI_RETRY_ATTEMPTS` | `3`                     | Number of retry attempts for failed API calls |
| `GEMINI_RETRY_DELAY`    | `1.0`                   | Delay between retry attempts (seconds)        |
| `MAX_FILE_SIZE_MB`      | `10`                    | Maximum upload file size in MB                |
| `SUPPORTED_FORMATS`     | `pdf,pptx,png,jpg,jpeg` | Supported file formats                        |
| `OUTPUT_DIR`            | `outputs`               | Directory for saving analysis results         |
| `TEMP_DIR`              | `temp`                  | Directory for temporary files                 |
| `LOG_LEVEL`             | `INFO`                  | Logging level (DEBUG, INFO, WARNING, ERROR)   |
| `LOG_FILE`              | `logs/app.log`          | Log file path                                 |

### 3. Directory Structure

The application will automatically create the following directories:

-   `outputs/` - Analysis results
-   `temp/` - Temporary files during processing
-   `logs/` - Application logs

## Running the Application

### 1. Validate Setup

Run the startup validation to ensure everything is configured correctly:

```bash
python -m config.startup_validation
```

This will check:

-   ✓ Configuration validity
-   ✓ Required dependencies
-   ✓ Directory permissions
-   ✓ API connection

### 2. Start the Application

```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

### 3. Alternative: Direct Python Execution

```bash
python src/main.py
```

## Troubleshooting

### Common Issues

1. **API Key Issues**:

    - Error: "Google API Key not configured"
    - Solution: Ensure `GOOGLE_API_KEY` is set in your `.env` file

2. **API Connection Failed**:

    - Error: "Gemini API connection failed"
    - Solutions:
        - Check your internet connection
        - Verify your API key is valid
        - Ensure you have Gemini API access enabled

3. **File Upload Issues**:

    - Error: "File too large" or "Unsupported format"
    - Solutions:
        - Check file size (default limit: 10MB)
        - Ensure file format is supported (PDF, PPTX, PNG, JPG, JPEG)

4. **Permission Errors**:
    - Error: Directory not writable
    - Solution: Ensure the application has write permissions for `outputs/`, `temp/`, and `logs/` directories

### Debug Mode

For detailed debugging, set the log level to DEBUG in your `.env` file:

```
LOG_LEVEL=DEBUG
```

Check the log file at `logs/app.log` for detailed error information.

### API Rate Limits

If you encounter rate limiting:

-   The application automatically retries failed requests
-   Increase `GEMINI_RETRY_DELAY` for longer delays between requests
-   Consider upgrading your Google Cloud plan for higher rate limits

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/
```

## Support

For issues and questions:

1. Check the application logs in `logs/app.log`
2. Run the startup validation script
3. Verify your API key and internet connection
4. Check the troubleshooting section above

## Security Notes

-   Never commit your `.env` file or API keys to version control
-   Keep your API keys secure and rotate them regularly
-   The application automatically cleans up temporary files
-   No uploaded documents are permanently stored by default
