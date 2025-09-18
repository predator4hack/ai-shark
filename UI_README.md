# Startup Document Processing UI

A Streamlit-based web interface for processing startup pitch decks and additional documents using AI-powered content extraction.

## Features

### 🎯 Pitch Deck Processing
- **Supported Formats**: PDF, PowerPoint (.ppt, .pptx)
- **AI Analysis**: 
  - Extracts company metadata (name, sector, sub-sector, website)
  - Generates table of contents
  - Performs topic-by-topic content extraction
  - Saves structured markdown output

### 📄 Additional Document Processing  
- **Supported Formats**: PDF, Word documents (.doc, .docx), Text files (.txt)
- **Content Types**: Call transcripts, founder updates, emails, reports
- **AI Processing**: Structures and cleans content using LLM
- **Output**: Readable markdown format

## Installation

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   GEMINI_EMBEDDING_MODEL=models/embedding-001
   ```

## Usage

### Starting the Application

```bash
streamlit run streamlit_ui.py
```

This will open the web interface in your default browser (usually at `http://localhost:8501`).

### Using the Interface

1. **Upload Pitch Deck**:
   - Click "Choose a pitch deck file" 
   - Select a PDF or PowerPoint file
   - Click "🚀 Process Pitch Deck"
   - Wait for AI processing to complete

2. **Upload Additional Documents**:
   - Click "Choose additional document files"
   - Select multiple files (PDFs, Word docs, text files)
   - Click "📝 Process Additional Documents"
   - Monitor processing progress

3. **View Results**:
   - Processing results appear in the "📋 Processing Results" section
   - File paths and success/failure status are displayed
   - Access generated files in the `outputs/<company-name>/` directory

### Output Structure

```
outputs/
└── <company-name>/
    ├── metadata.json              # Company metadata from pitch deck
    ├── pitch_deck.md             # Processed pitch deck content
    ├── table_of_contents.json    # Extracted table of contents
    └── additional_docs/
        ├── document1.md          # Processed additional documents
        ├── document2.md
        └── ...
```

## Processing Pipeline Details

### Pitch Deck Processing

1. **File Conversion**: 
   - PDF: Direct image extraction using PyMuPDF
   - PowerPoint: Converted to PDF first, then to images

2. **Stage 1 - Metadata Extraction**:
   - Uses Gemini AI to analyze all pages
   - Extracts: startup name, sector, sub-sector, website, table of contents
   - Custom prompt designed specifically for comprehensive metadata extraction
   - Returns structured JSON with company information and content mapping

3. **Stage 2 - Topic Analysis**:
   - Processes each topic based on extracted table of contents
   - Extracts detailed content for specific page ranges
   - Uses targeted prompts for topic-specific analysis
   - Handles missing or invalid page references gracefully

4. **Output Generation**:
   - Converts structured data to markdown with proper formatting
   - Saves metadata as separate JSON file
   - Creates human-readable reports with company header and structured content
   - Includes table of contents overview in markdown output

### Additional Document Processing

1. **Text Extraction**:
   - PDF: Uses PyMuPDF for text extraction
   - Word: Uses python-docx for content extraction
   - Text: Direct file reading with encoding detection

2. **Content Structuring**:
   - Uses Gemini AI to clean and organize content
   - Identifies document types (transcripts, emails, etc.)
   - Maintains important details while improving readability

3. **Markdown Conversion**:
   - Adds document headers and metadata
   - Formats content for readability
   - Preserves original structure where appropriate

## Error Handling

- **File Upload Errors**: Validates file types and sizes
- **Processing Errors**: Displays user-friendly error messages
- **API Errors**: Retries with exponential backoff
- **Partial Failures**: Continues processing other files if one fails

## Features

### User Interface
- **Drag & Drop**: Easy file upload interface
- **Progress Tracking**: Real-time processing status
- **Multi-file Support**: Process multiple additional documents
- **Results Display**: Clear success/failure indicators
- **File Management**: Shows created files and locations

### AI Processing
- **Robust Analysis**: Uses Google's Gemini AI models
- **Retry Logic**: Handles API failures gracefully
- **Content Awareness**: Adapts processing based on document type
- **Quality Output**: Structured, readable markdown format

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**:
   - Ensure `.env` file exists with valid API key
   - Check that the key has proper permissions

2. **"Module not found" errors**:
   - Run `uv sync` to install all dependencies
   - Ensure you're in the correct directory

3. **Processing fails for PowerPoint files**:
   - Install LibreOffice for better PPT conversion
   - Or use PDF format for more reliable processing

4. **Large file processing is slow**:
   - Large files take longer to process
   - Consider splitting very large documents
   - Check your Gemini API quotas

### Performance Tips

- **Optimize File Sizes**: Compress large PDFs before upload
- **Batch Processing**: Process multiple additional documents together
- **Monitor Progress**: Use the progress indicators to track processing
- **Check Outputs**: Verify files are created in the outputs directory

## Development

### Architecture

The application follows a modular design:

- **`src/processors/`**: Document processing logic
  - `BaseProcessor`: Abstract base class for processors  
  - `PitchDeckProcessor`: Handles pitch deck analysis
  - `AdditionalDocProcessor`: Processes additional documents
  - `FileConverter`: Handles file format conversions

- **`src/ui/`**: Streamlit user interface
  - `streamlit_app.py`: Main UI application

- **`src/utils/`**: Utility modules
  - `OutputManager`: Handles file saving and directory management

### Extending the Application

1. **Add New File Types**:
   - Extend `BaseProcessor` for new document types
   - Add file type validation in UI
   - Update supported extensions lists

2. **Enhance Processing**:
   - Modify prompt templates in existing pipeline
   - Add new analysis stages
   - Implement additional output formats

3. **UI Improvements**:
   - Add new Streamlit components
   - Enhance progress tracking
   - Add file preview capabilities

## License

This project is part of the AI Shark startup analysis platform.