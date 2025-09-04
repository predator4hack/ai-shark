# VC Document Analyzer

AI-powered pitch deck analysis tool for venture capital professionals.

## Overview

The VC Document Analyzer is a Streamlit-based web application that processes pitch deck documents using Google's Gemini multimodal LLM. It extracts structured information from slides and generates comprehensive analysis reports to streamline the VC investment screening process.

## Features

-   **Multi-format Support**: Process PDF, PowerPoint (PPTX), and image files
-   **AI-Powered Analysis**: Extract headings, descriptions, chart data, and interpretations
-   **Structured Output**: Generate organized Markdown reports
-   **User-Friendly Interface**: Simple web-based file upload and processing
-   **Error Handling**: Graceful handling of processing errors with clear feedback

## Project Structure

```
├── src/                    # Main application source code
│   ├── models/            # Data models and structures
│   ├── processors/        # Document processing components
│   ├── analyzers/         # AI analysis components
│   ├── output/            # Output management components
│   ├── ui/                # Streamlit UI components
│   └── main.py            # Main application entry point
├── config/                # Configuration files
│   └── settings.py        # Application settings
├── tests/                 # Test suite
├── outputs/               # Generated analysis files
├── temp/                  # Temporary file storage
├── logs/                  # Application logs
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── streamlit_app.py       # Streamlit entry point
```

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository and navigate to the project directory
cd your-project-directory

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env file and add your Google API key
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Google API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Add the API key to your `.env` file

### 4. Run the Application

```bash
# Start the Streamlit application
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## Usage

1. **Upload Document**: Use the file upload interface to select your pitch deck (PDF, PPTX, or images)
2. **Processing**: The application will process each slide and extract information using AI
3. **Review Results**: View the structured analysis results in the web interface
4. **Download Output**: Save the complete analysis as a Markdown file

## Requirements Covered

This setup addresses the following requirements from the specification:

-   **Requirement 1.1**: File upload interface for pitch deck documents
-   **Requirement 1.2**: Support for PDF, PowerPoint (PPTX), and image formats
-   **Configuration**: Environment setup for API keys and application settings
-   **Project Structure**: Organized codebase for scalable development

## Development

### Installing Additional Dependencies

```bash
# Add new dependencies to pyproject.toml, then:
pip install -e .
```

### Running Tests

```bash
# Run the test suite (when implemented)
pytest tests/
```

### Code Structure

The application follows a modular architecture:

-   **Models**: Data structures for slides, analysis results, and processing outcomes
-   **Processors**: Document parsing and slide extraction logic
-   **Analyzers**: AI integration and analysis logic
-   **Output**: File generation and formatting
-   **UI**: Streamlit interface components

## Next Steps

With the project structure and dependencies set up, you can now proceed to implement:

1. Core data models (Task 2)
2. Document processor component (Task 3)
3. Gemini API integration (Task 4)
4. Output management system (Task 5)
5. Streamlit user interface (Task 6)

## Troubleshooting

### Common Issues

1. **API Key Not Working**: Ensure your Google API key is valid and has access to Gemini Pro Vision
2. **Import Errors**: Make sure all dependencies are installed and the virtual environment is activated
3. **File Upload Issues**: Check file size limits and supported formats

### Support

For issues and questions, refer to the project documentation or check the application logs in the `logs/` directory.
