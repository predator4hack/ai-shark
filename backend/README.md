# Aviato Backend

FastAPI backend for Aviato VC Document Analyzer - deployed on Google Cloud Run.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
# or using uv
uv sync
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run development server:
```bash
uvicorn src.api.main:app --reload
```

## Deployment

This backend is configured for deployment on Google Cloud Run.

### Build and Deploy

```bash
# Build the Docker image
docker build -t aviato-backend .

# Deploy to Cloud Run
gcloud run deploy aviato-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Project Structure

```
backend/
├── src/              # Application source code
│   ├── api/         # FastAPI routes and endpoints
│   ├── agents/      # AI agents
│   ├── processors/  # Document processors
│   ├── models/      # Data models
│   └── utils/       # Utility functions
├── config/          # Configuration files
├── tests/           # Test files
└── outputs/         # Output directory for processed files
```

## Environment Variables

See [.env.example](.env.example) for required environment variables.
