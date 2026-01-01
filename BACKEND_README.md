# AI-Shark Backend API

FastAPI backend for the AI-Shark VC Document Analyzer application.

## Architecture

This backend implements a REST API that exposes the pitch deck processing functionality:

- **Storage Abstraction**: Supports both local filesystem (dev) and Google Cloud Storage (production)
- **Job Management**: In-memory job tracking for async processing with status polling
- **Background Processing**: Uses FastAPI BackgroundTasks for long-running operations

## Project Structure

```
src/api/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration management
├── routers/
│   ├── documents.py          # Document upload/processing endpoints
│   ├── jobs.py               # Job status polling endpoints
│   └── files.py              # File download endpoints
├── schemas/
│   ├── document.py           # Request/response models
│   └── common.py             # Shared schemas
└── services/
    ├── storage_manager.py    # GCS/Local storage abstraction
    └── job_manager.py        # Job tracking and status
```

## Installation

1. Install dependencies using uv:

```bash
uv pip install -e .
```

2. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `USE_GCS`: Set to `false` for local development, `true` for production
- `GCS_BUCKET_NAME`: GCS bucket name (only needed if USE_GCS=true)
- `OUTPUT_DIR`: Local output directory (default: `outputs`)

## Running the API

### Development Mode

```bash
python test_api.py
```

Or using uvicorn directly:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Root**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/health
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### 1. Upload Pitch Deck

**POST** `/api/v1/documents/pitch-deck`

Upload and process a pitch deck (PDF/PPT/PPTX).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary file, max 100MB)

**Response:**
```json
{
  "job_id": "uuid-here",
  "message": "Pitch deck uploaded successfully. Processing started."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/pitch-deck" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@pitch_deck.pdf"
```

### 2. Get Job Status

**GET** `/api/v1/jobs/{job_id}/status`

Poll job status (used by frontend every 2-3 seconds).

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "processing",  // pending, processing, completed, failed
  "progress_message": "Converting pitch deck to images...",
  "result": null,  // populated when status is "completed"
  "error": null    // populated when status is "failed"
}
```

When completed, `result` contains:
```json
{
  "success": true,
  "company_name": "Example Corp",
  "files_created": [
    "Example Corp/pitch_deck.md",
    "Example Corp/metadata.json"
  ],
  "metadata": { ... },
  "processing_time": 12.34
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}/status"
```

### 3. Download File

**GET** `/api/v1/files/download/{company_name}/{file_path}`

Download a processed file.

**Behavior:**
- **Local storage**: Streams file directly
- **GCS**: Returns redirect to signed URL (valid for 1 hour)

**Example:**
```bash
curl "http://localhost:8000/api/v1/files/download/Example%20Corp/pitch_deck.md" -O
```

### 4. List Company Files

**GET** `/api/v1/files/{company_name}/list`

List all files for a company.

**Response:**
```json
{
  "company_name": "Example Corp",
  "files": [
    {
      "path": "Example Corp/pitch_deck.md",
      "download_url": "/api/v1/files/download/Example Corp/pitch_deck.md"
    }
  ]
}
```

## Storage Backends

### Local Storage (Development)

Set in `.env`:
```
USE_GCS=false
OUTPUT_DIR=outputs
```

Files are stored in the `outputs/` directory with the following structure:
```
outputs/
└── {company_name}/
    ├── pitch_deck.md
    ├── metadata.json
    └── toc.json
```

### Google Cloud Storage (Production)

Set in `.env`:
```
USE_GCS=true
GCS_BUCKET_NAME=ai-shark-outputs
```

Requirements:
- Google Cloud credentials configured (`gcloud auth application-default login`)
- GCS bucket created and accessible

## Testing

### Manual Testing with curl

1. Start the server:
```bash
python test_api.py
```

2. Upload a pitch deck:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/pitch-deck" \
  -F "file=@sample_deck.pdf"
```

3. Get the `job_id` from response and poll status:
```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}/status"
```

4. Download the result:
```bash
curl "http://localhost:8000/api/v1/files/download/{company_name}/pitch_deck.md" -O
```

### Testing with the Interactive Docs

Visit http://localhost:8000/docs and use the Swagger UI to test endpoints interactively.

## CORS Configuration

The API is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite default port)

To add more origins, edit [src/api/main.py](src/api/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://yourdomain.com",  # Add production domain
    ],
    ...
)
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid file type or validation error
- `404 Not Found`: Job or file not found
- `413 Payload Too Large`: File exceeds 100MB limit
- `500 Internal Server Error`: Processing error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Job Lifecycle

1. **Upload**: Client uploads file → API creates job → Returns `job_id`
2. **Processing**: Background task processes file, updates job status
3. **Polling**: Client polls `/jobs/{job_id}/status` every 2-3 seconds
4. **Completion**: Status changes to `completed` or `failed`
5. **Download**: Client downloads files using URLs from result

## Performance Considerations

- **File Size Limit**: 100MB (configurable via `MAX_FILE_SIZE_MB`)
- **Job Cleanup**: Jobs older than 24 hours are automatically cleaned up
- **Concurrent Processing**: Uses FastAPI's background tasks (one task per upload)
- **Memory Usage**: In-memory job storage (consider Redis for production scale)

## Production Deployment

See [Dockerfile](Dockerfile) for multi-stage build that:
1. Builds React frontend
2. Serves both API and static files from single FastAPI app

Deploy to Google Cloud Run:
```bash
gcloud run deploy ai-shark \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars USE_GCS=true,GCS_BUCKET_NAME=ai-shark-outputs \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600
```

## Troubleshooting

### ImportError: No module named 'google.cloud'

Install GCS dependencies:
```bash
uv pip install google-cloud-storage
```

### Storage backend not detected

Check your `.env` file has:
```
USE_GCS=false  # or true for GCS
OUTPUT_DIR=outputs
```

### CORS errors in browser

Add your frontend URL to `allow_origins` in [src/api/main.py](src/api/main.py).

### Background task not starting

Check server logs for errors. Ensure dependencies are installed and environment variables are set.

## Next Steps

After implementing the backend (Task 1), proceed to:
- **Task 2**: React Frontend Setup
- **Task 3**: Integration & Testing
- **Task 4**: Deployment to Cloud Run

See [specs/react_migration_plan.md](specs/react_migration_plan.md) for the complete implementation plan.
