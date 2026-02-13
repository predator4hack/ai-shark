# Project Structure

AI-Shark has been refactored into separate frontend and backend directories for independent deployment.

## Directory Layout

```text
ai-shark/
├── backend/                    # Backend API (Deploy to Google Cloud Run)
│   ├── src/                   # Python source code
│   │   ├── api/              # FastAPI routes
│   │   ├── agents/           # AI agents
│   │   ├── processors/       # Document processors
│   │   ├── models/           # Data models
│   │   └── utils/            # Utilities
│   ├── config/               # Configuration files
│   ├── tests/                # Backend tests
│   ├── outputs/              # Local output directory
│   ├── Dockerfile            # Production build
│   ├── Dockerfile.dev        # Development build
│   ├── .env.example          # Backend environment template
│   ├── pyproject.toml        # Python dependencies
│   ├── requirements.txt      # Pip requirements
│   └── README.md             # Backend documentation
│
├── frontend/                   # Frontend UI (Deploy to Vercel)
│   ├── src/                  # React source code
│   │   ├── components/       # React components
│   │   ├── features/         # Feature modules
│   │   ├── store/            # Redux store
│   │   └── ...
│   ├── public/               # Static assets
│   ├── Dockerfile            # Frontend production build
│   ├── .env.example          # Frontend environment template
│   ├── package.json          # NPM dependencies
│   └── vite.config.ts        # Vite configuration
│
├── docker-compose.yml          # Local development orchestration
├── .env.example               # Reference guide (points to backend/frontend)
├── README.md                  # Main project documentation
├── DEPLOYMENT.md              # Deployment instructions
├── STRUCTURE.md               # This file
└── specs/                     # Project specifications

```

## Configuration Files

### Backend Configuration

**File**: `backend/.env.example` → `backend/.env`

Contains:
- LLM API keys (Google Gemini, Groq)
- Storage configuration (GCS or local)
- API settings (host, port, CORS)
- Feature flags (mock mode, etc.)

**Setup**:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Configuration

**File**: `frontend/.env.example` → `frontend/.env`

Contains:
- API endpoint URL (`VITE_API_URL`)

**Setup**:
```bash
cd frontend
cp .env.example .env
# Development: Leave as /api (uses proxy)
# Production: Set to https://your-backend-url.run.app/api
```

### Root .env.example

The root `.env.example` is a **reference file** that documents the overall configuration structure and points developers to the correct locations. It doesn't need to be copied.

## Development Setup

### 1. Using Docker Compose (Recommended)

```bash
# Setup environment files
cd backend && cp .env.example .env && cd ..
cd frontend && cp .env.example .env && cd ..

# Edit backend/.env with your API keys
nano backend/.env

# Start all services
docker-compose up
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Manual Setup

**Backend**:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
pip install -e .
uvicorn src.api.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Deployment

### Backend → Google Cloud Run

```bash
cd backend

gcloud run deploy ai-shark-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars USE_GCS=true,GCS_BUCKET_NAME=ai-shark-outputs \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

### Frontend → Vercel

```bash
cd frontend

# Set backend URL in production env
echo "VITE_API_URL=https://your-backend-url.run.app/api" > .env.production

# Deploy
vercel --prod
```

## Key Benefits of This Structure

1. **Separate Deployments**: Frontend (Vercel) and backend (Cloud Run) deploy independently
2. **Clear Boundaries**: Each service has its own configuration, dependencies, and documentation
3. **Scalability**: Backend and frontend can scale independently
4. **Cost Optimization**: Vercel provides free frontend hosting, Cloud Run scales to zero
5. **Developer Experience**: Clear separation makes it easy to work on frontend or backend independently

## Migration from Old Structure

The old structure had everything in the root directory. We've moved:

- `src/` → `backend/src/`
- `config/` → `backend/config/`
- `tests/` → `backend/tests/`
- `pyproject.toml` → `backend/pyproject.toml`
- `requirements.txt` → `backend/requirements.txt`
- `Dockerfile` → `backend/Dockerfile`
- `frontend/` → (already separate, no changes needed)

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | `AIza...` |
| `GROQ_API_KEY` | Groq API key | `gsk_...` |
| `USE_GCS` | Use Google Cloud Storage | `false` (local), `true` (prod) |
| `GCS_BUCKET_NAME` | GCS bucket name | `ai-shark-outputs` |
| `API_PORT` | Backend port | `8000` |
| `USE_MOCK_LLM` | Mock mode for testing | `false` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API endpoint | `/api` (dev), `https://...run.app/api` (prod) |

## Docker Compose Services

- **api**: Backend service (port 8000)
- **frontend**: Frontend service (port 3000)

Both services are networked together in development.

## Questions?

- General setup: See [README.md](README.md)
- Deployment: See [DEPLOYMENT.md](DEPLOYMENT.md)
- Backend specific: See [backend/README.md](backend/README.md)
