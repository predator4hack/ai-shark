# Migration Plan: Streamlit to React UI - AI-Shark VC Document Analyzer

## Project Understanding Summary

The AI-Shark application is a **multi-phase VC document analysis pipeline** built entirely in Streamlit that:

1. **Phase 1:** Uploads and processes pitch decks (PDF/PPT) → extracts metadata, ToC, structured content
2. **Phase 2:** Processes additional documents (transcripts, emails, updates)
3. **Phase 3:** Runs multi-agent AI analysis (business, market, tech, risk agents)
4. **Phase 4:** Simulates founder responses to investment questionnaires
5. **Phase 5:** Generates weighted final investment memo (MD + PDF)

**Current Architecture:**

-   **Monolithic Streamlit application** (no separate backend API)
-   All business logic in Python processors and AI agents
-   File-based state management (outputs directory structure)
-   Google Gemini LLM integration via LangChain
-   No authentication/user management
-   No existing React/Node.js setup

**Key Technical Insights:**

-   1163-line single Streamlit file (`streamlit_app.py`)
-   5 core processors (PitchDeck, AdditionalDoc, Analysis, RefDoc, QA, FinalMemo)
-   Dynamic agent discovery system (auto-discovers AI agents)
-   Session state for workflow progression
-   Docker-ready with Cloud Run deployment config

---

## Clarifying Questions

Before implementing the React migration, I need clarity on the following aspects:

### 1. Architecture Strategy

**Q1.1:** Which integration approach do you prefer?

-   **Option A - Streamlit Custom Components (Incremental):**

    -   Keep Streamlit as the main orchestration layer
    -   Build React components as Streamlit custom components
    -   Gradual migration with no breaking changes
    -   React used only for interactive features (charts, document viewers, chat)
    -   Both UIs coexist within same Streamlit app

-   **Option B - Dual Frontend Architecture (Parallel):**

    -   Keep Streamlit running on port 8080
    -   Build standalone React app on different port (e.g., 3000)
    -   Create FastAPI backend layer (port 8000) to expose processors as REST APIs
    -   Both UIs fully functional independently
    -   URL-based routing: `/streamlit` vs `/react`

-   **Option C - Full SPA with Backend API:**
    -   Completely separate React frontend (SPA)
    -   Build complete FastAPI backend exposing all functionality
    -   Streamlit deprecated once React is ready
    -   Most complex but cleanest separation

Answer: Lets go with Option C

**Q1.2:** Do you want real-time progress updates during long-running operations?

-   If yes, should we use WebSockets or Server-Sent Events (SSE)?
-   Current Streamlit uses progress bars - React equivalent would need streaming

No need of streaming.
Use polling instead of WebSockets/SSE
React frontend periodically checks job status via REST API
Show progress indicator (spinner/indeterminate progress bar)

**Q1.3:** Should the React UI be accessible at a different URL path or completely separate deployment?

Go with same domain, different paths.
For example. Production URLs:
https://yourdomain.com/ → React UI (default)
https://yourdomain.com/api/ → FastAPI backend
https://yourdomain.com/streamlit/ → Streamlit UI (legacy)

---

### 2. Backend API Requirements

**Q2.1:** If we need to create a FastAPI backend layer, should it:

-   Wrap existing processors as-is (minimal refactoring)?
-   Refactor processors to be more REST-friendly?
-   Add database for session persistence (currently file-based)?

Answer: - Refactor the processors to be more REST-friendly.

-   Keep it file based for now. We will be deploying the application on GCP cloud run and would use GCS for storage

**Q2.2:** Authentication & Multi-User Support:

-   Is this a single-user application or multi-user?
-   Do we need user accounts, authentication, and per-user data isolation?
-   Should company data be private to users or shared?

Answer: - Keep it single-user application

-   No user accounts/authentication
-   single user application

**Q2.3:** File Storage:

-   Keep local filesystem storage (`outputs/` directory)?
-   Migrate to cloud storage (S3, GCS)?
-   Hybrid approach (local for dev, cloud for production)?

answer: Hybrid appraoch, local for dev, GCS for production

---

### 3. UI/UX Design Approach

**Q3.1:** Design System & Styling:

-   Do you have preferred component library? (Material-UI, Ant Design, Chakra UI, shadcn/ui, custom)
-   Design inspiration/reference apps?
-   Color scheme / brand guidelines?

Answer: I don't have a preference, however the UI should look premium.

**Q3.2:** UI Flow - Should React maintain the same sequential phase-based flow?

-   **Same Sequential Flow:** Keep 5-phase waterfall (Phase 1 → 2 → 3 → 4 → 5)
-   **Dashboard Approach:** Show all phases upfront, enable any phase when prerequisites met
-   **Wizard/Stepper:** Multi-step wizard with progress indicator

Answer: Same Sequential flow

**Q3.3:** Key Features to Prioritize in React:

-   Interactive document viewer (PDF/pitch deck viewer)?
-   Real-time collaboration features?
-   Advanced data visualization for analysis results?
-   Chat interface with AI agents?
-   Drag-and-drop file uploads?

Ans:

-   Premium look and interactive document viewer
-   Drag and drop file uploads

---

### 4. State Management & Data Flow

**Q4.1:** React State Management:

-   Simple (React Context + useState/useReducer)?
-   Redux Toolkit?
-   Zustand or Jotai?
-   TanStack Query (React Query) for server state?

Ans: User redux toolkit

**Q4.2:** Session Persistence:

-   Browser localStorage/sessionStorage?
-   Backend session management with cookies?
-   JWT tokens for stateless auth?

Ans: browser localStorage/sessionStorage

**Q4.3:** Company/Project Selection:

-   Should users be able to work on multiple companies simultaneously?
-   Switch between companies via dropdown/sidebar?
-   Workspace/project management needed?

Ans: Nope, only one company at a time. No workspace management as of now

---

### 5. Feature Parity & Migration Strategy

**Q5.1:** Phase 1 Implementation Scope:

-   Build only Phase 1 (Pitch Deck) in React first?
-   Build all 5 phases in parallel?
-   Build minimal viable React UI (phases 1, 3, 5 only)?

Answer: Build phase 1 and then iterate

**Q5.2:** Streamlit Deprecation Timeline:

-   How long should both UIs coexist?
-   Feature flag to toggle between UIs?
-   Hard cutover date or gradual sunset?

Answer: I'll tell you when to depricate, no timeline as of now

**Q5.3:** Missing Features in Current Streamlit:

-   Are there features you want in React that Streamlit doesn't have?
-   Features to remove/simplify in React version?

Answer: no additional features for now, will inform later

---

### 6. Development & Deployment

**Q6.1:** Development Environment:

-   Develop React locally with mock backend first?
-   Develop against live Streamlit backend wrapped in API?
-   Docker Compose setup with all services?

Answer:

-   develop against live backend
-   docker compose setup with all services

**Q6.2:** Build Tooling:

-   Vite (recommended for speed)?
-   Create React App (CRA)?
-   Next.js (if you want SSR/SSG)?

Answer: Vite

**Q6.3:** TypeScript:

-   Use TypeScript for React (recommended)?
-   Or plain JavaScript?

Answer: Use TypeScript

**Q6.4:** Deployment Strategy:

-   Deploy React as static build (Vercel, Netlify, S3 + CloudFront)?
-   Deploy alongside backend (same Docker container)?
-   Separate deployments (React on Vercel, API on Cloud Run)?

Answer: Deploy as single Cloud Run service with FastAPI serving React static build (multi-stage Docker build)

---

### 7. Testing & Quality

**Q7.1:** Testing Requirements:

-   Unit tests (Jest/Vitest)?
-   Integration tests (React Testing Library)?
-   E2E tests (Playwright, Cypress)?
-   Test coverage targets?

Answer: Integratino tests

**Q7.2:** Performance Requirements:

-   File upload size limits (currently 200-500MB)?
-   Acceptable processing time for pitch deck?
-   Concurrent user targets?

Answer: 100MB file size limits

---

### 8. Agent Weight Configuration

**Q8.1:** In Phase 5 (Final Memo), users configure agent weights (must sum to 100%).

Should the React UI:

-   Keep numeric inputs with validation (like Streamlit)?
-   Use sliders that auto-adjust others when one changes?
-   Use a visual pie chart with draggable segments?
-   Preset weight templates (e.g., "Balanced", "Market-Focused", "Tech-Focused")?

Answer:

-   UI sliders (manual adjustment) + preset weight templates Templates

---

### 9. File Downloads & Exports

**Q9.1:** The app generates multiple files (MD, DOCX, PDF). Should React:

-   Inline document preview before download?
-   Download multiple files as ZIP?
-   Preview in modal/sidebar?
-   Send files via email?

ANswer: All the files should not be downloaded at once. Please follow how it goes in the current implementation in streamlit

**Q9.2:** Export Formats:

-   Keep current formats (MD, DOCX, PDF)?
-   Add new formats (JSON, CSV for data)?
-   DOCX generation currently optional - make it required in React?

Answer: Keep the current formats

---

DETAILED IMPLEMENTATION PLAN: Streamlit to React Migration - AI-Shark
Executive Summary

Goal: Migrate AI-Shark VC document analyzer from Streamlit to React with FastAPI backend Architecture: Full SPA with FastAPI backend + GCS storage, deployed as single Cloud Run service Scope: Phase 1 (Pitch Deck Processing) first, then iterate to remaining phases Timeline Estimate: 2-3 weeks for Phase 1 complete implementation
Finalized Architecture Decisions

✅ Confirmed Decisions
Frontend: React 18 + TypeScript + Vite + Material-UI
Backend: FastAPI (Python 3.11) exposing REST APIs
State Management: Redux Toolkit + localStorage
Storage: GCS (production) / Local filesystem (development)
Deployment: Single Cloud Run service (FastAPI serves React static build)
Progress Updates: Polling-based (every 2-3 seconds)
File Uploads: 100MB limit, drag-and-drop support
Testing: Integration tests (React Testing Library)
Build Priority: Backend → Frontend → Integration
Phase 1: Pitch Deck Processing - Detailed Implementation
Milestone 1: Backend API Foundation (Week 1)
Task 1.1: Project Restructuring & Dependencies
Create New Files:

/src/api/
├── **init**.py
├── main.py # FastAPI app entry point
├── config.py # Configuration management
├── dependencies.py # Shared dependencies
├── routers/
│ ├── **init**.py
│ ├── documents.py # Document upload/processing endpoints
│ ├── jobs.py # Job status polling endpoints
│ └── files.py # File download endpoints
├── schemas/
│ ├── **init**.py
│ ├── document.py # Request/response models
│ ├── job.py # Job status models
│ └── common.py # Shared schemas
├── services/
│ ├── **init**.py
│ ├── storage_manager.py # GCS/Local storage abstraction
│ └── job_manager.py # Job tracking and status
└── utils/
├── **init**.py
└── errors.py # Custom exceptions

Update pyproject.toml:

[project]
dependencies = [ # Existing dependencies...
"fastapi>=0.109.0",
"uvicorn[standard]>=0.27.0",
"python-multipart>=0.0.6", # File uploads
"google-cloud-storage>=2.14.0",
"pydantic>=2.5.0",
"pydantic-settings>=2.1.0",
]
Task 1.2: Storage Abstraction Layer
File: /src/api/services/storage_manager.py

"""
Storage abstraction supporting both local filesystem and GCS.
Automatically detects environment and uses appropriate backend.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional
import os

class StorageBackend(ABC):
@abstractmethod
def save_file(self, path: str, content: bytes | BinaryIO) -> str:
"""Save file and return public path/URL"""
pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """Read file content"""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> list[str]:
        """List files with given prefix"""
        pass

    @abstractmethod
    def delete_file(self, path: str) -> None:
        """Delete a file"""
        pass

    @abstractmethod
    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        """Get download URL (signed for GCS, direct for local)"""
        pass

class LocalStorageBackend(StorageBackend):
"""Local filesystem storage for development"""

    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            full_path.write_bytes(content)
        else:
            with open(full_path, 'wb') as f:
                f.write(content.read())

        return str(full_path)

    def read_file(self, path: str) -> bytes:
        return (self.base_dir / path).read_bytes()

    def file_exists(self, path: str) -> bool:
        return (self.base_dir / path).exists()

    def list_files(self, prefix: str) -> list[str]:
        pattern = str(self.base_dir / prefix / "**/*")
        return [str(p.relative_to(self.base_dir)) for p in Path().glob(pattern) if p.is_file()]

    def delete_file(self, path: str) -> None:
        (self.base_dir / path).unlink(missing_ok=True)

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        # For local, return relative path
        return f"/api/v1/files/download/{path}"

class GCSStorageBackend(StorageBackend):
"""Google Cloud Storage backend for production"""

    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.bucket_name = bucket_name

    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        blob = self.bucket.blob(path)

        if isinstance(content, bytes):
            blob.upload_from_string(content)
        else:
            blob.upload_from_file(content, rewind=True)

        return f"gs://{self.bucket_name}/{path}"

    def read_file(self, path: str) -> bytes:
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()

    def file_exists(self, path: str) -> bool:
        return self.bucket.blob(path).exists()

    def list_files(self, prefix: str) -> list[str]:
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, path: str) -> None:
        self.bucket.blob(path).delete()

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        blob = self.bucket.blob(path)
        return blob.generate_signed_url(expiration=expiration)

class StorageManager:
"""
Main storage interface. Auto-detects environment: - Local: USE_GCS=false or missing - GCS: USE_GCS=true
"""

    def __init__(self):
        use_gcs = os.getenv("USE_GCS", "false").lower() == "true"

        if use_gcs:
            bucket_name = os.getenv("GCS_BUCKET_NAME", "ai-shark-outputs")
            self.backend = GCSStorageBackend(bucket_name)
            print(f"✅ Using GCS storage: {bucket_name}")
        else:
            base_dir = os.getenv("OUTPUT_DIR", "outputs")
            self.backend = LocalStorageBackend(base_dir)
            print(f"✅ Using local storage: {base_dir}")

    # Delegate all methods to backend
    def save_file(self, path: str, content: bytes | BinaryIO) -> str:
        return self.backend.save_file(path, content)

    def read_file(self, path: str) -> bytes:
        return self.backend.read_file(path)

    def file_exists(self, path: str) -> bool:
        return self.backend.file_exists(path)

    def list_files(self, prefix: str) -> list[str]:
        return self.backend.list_files(prefix)

    def delete_file(self, path: str) -> None:
        return self.backend.delete_file(path)

    def get_download_url(self, path: str, expiration: int = 3600) -> str:
        return self.backend.get_download_url(path, expiration)

# Global instance

storage = StorageManager()
Key Features:
Single interface for both local and GCS
Auto-detection based on environment variables
Signed URLs for secure downloads
Drop-in replacement for current file operations
Task 1.3: Job Management System
File: /src/api/services/job_manager.py

"""
In-memory job tracking for async processing.
Stores job status, progress messages, and results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
import uuid

class JobStatus(str, Enum):
PENDING = "pending"
PROCESSING = "processing"
COMPLETED = "completed"
FAILED = "failed"

class Job(BaseModel):
job_id: str
status: JobStatus
progress_message: str
result: Optional[Dict[str, Any]] = None
error: Optional[str] = None
created_at: datetime
updated_at: datetime
company_name: Optional[str] = None

class JobManager:
"""
Simple in-memory job store.
For production, consider Redis or database.
"""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}

    def create_job(self, company_name: Optional[str] = None) -> str:
        """Create new job and return job_id"""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job = Job(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress_message="Job created, waiting to start...",
            created_at=now,
            updated_at=now,
            company_name=company_name
        )

        self._jobs[job_id] = job
        return job_id

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress_message: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update job status and progress"""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self._jobs[job_id]
        job.status = status
        job.progress_message = progress_message
        job.updated_at = datetime.utcnow()

        if result:
            job.result = result
        if error:
            job.error = error

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self._jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than max_age_hours"""
        now = datetime.utcnow()
        to_delete = [
            job_id for job_id, job in self._jobs.items()
            if (now - job.created_at).total_seconds() > max_age_hours * 3600
        ]
        for job_id in to_delete:
            del self._jobs[job_id]

# Global instance

job_manager = JobManager()
Task 1.4: Pydantic Schemas
File: /src/api/schemas/document.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class PitchDeckUploadResponse(BaseModel):
job_id: str
message: str = "Pitch deck upload started"

class JobStatusResponse(BaseModel):
job_id: str
status: str # pending, processing, completed, failed
progress_message: str
result: Optional[Dict] = None
error: Optional[str] = None

class PitchDeckResult(BaseModel):
success: bool
company_name: str
output_dir: str
files_created: List[str]
metadata: Dict
processing_time: float

class FileDownloadResponse(BaseModel):
filename: str
download_url: str
expires_in: int = 3600 # seconds
Task 1.5: FastAPI Routes - Documents
File: /src/api/routers/documents.py

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from ..schemas.document import PitchDeckUploadResponse, PitchDeckResult
from ..services.job_manager import job_manager, JobStatus
from ..services.storage_manager import storage
from src.processors.pitch_deck_processor import PitchDeckProcessor

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

def process_pitch_deck_background(job_id: str, temp_file_path: str):
"""
Background task to process pitch deck.
Updates job status throughout processing.
"""
try: # Update: Starting processing
job_manager.update_status(
job_id,
JobStatus.PROCESSING,
"Starting pitch deck processing..."
)

        # Initialize processor
        processor = PitchDeckProcessor(use_real_llm=True)

        # Update: Converting to images
        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Converting pitch deck to images..."
        )

        # Process pitch deck (existing logic)
        result = processor.process(
            file_path=temp_file_path,
            output_dir=None  # Will use storage_manager instead
        )

        # Save files to storage
        company_name = result.get("company_name", "unknown")

        job_manager.update_status(
            job_id,
            JobStatus.PROCESSING,
            "Saving processed files..."
        )

        # Save pitch_deck.md to storage
        pitch_deck_content = result.get("pitch_deck_md", "")
        storage.save_file(
            f"{company_name}/pitch_deck.md",
            pitch_deck_content.encode('utf-8')
        )

        # Save metadata.json
        import json
        metadata = result.get("metadata", {})
        storage.save_file(
            f"{company_name}/metadata.json",
            json.dumps(metadata, indent=2).encode('utf-8')
        )

        # Update: Complete
        job_manager.update_status(
            job_id,
            JobStatus.COMPLETED,
            "Pitch deck processing completed!",
            result={
                "success": True,
                "company_name": company_name,
                "files_created": [
                    f"{company_name}/pitch_deck.md",
                    f"{company_name}/metadata.json"
                ],
                "metadata": metadata
            }
        )

    except Exception as e:
        job_manager.update_status(
            job_id,
            JobStatus.FAILED,
            f"Processing failed: {str(e)}",
            error=str(e)
        )

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.post("/pitch-deck", response_model=PitchDeckUploadResponse)
async def upload_pitch_deck(
file: UploadFile = File(...),
background_tasks: BackgroundTasks = BackgroundTasks()
):
"""
Upload and process pitch deck (PDF/PPT/PPTX).
Returns job_id for status tracking.

    File size limit: 100MB
    """

    # Validate file type
    allowed_extensions = [".pdf", ".ppt", ".pptx"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Validate file size (100MB limit)
    MAX_SIZE = 100 * 1024 * 1024  # 100MB in bytes
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: 100MB"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    # Create job
    job_id = job_manager.create_job()

    # Start background processing
    background_tasks.add_task(process_pitch_deck_background, job_id, temp_path)

    return PitchDeckUploadResponse(
        job_id=job_id,
        message="Pitch deck uploaded successfully. Processing started."
    )

File: /src/api/routers/jobs.py

from fastapi import APIRouter, HTTPException

from ..schemas.document import JobStatusResponse
from ..services.job_manager import job_manager

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
"""
Get current status of a processing job.
Used for polling from React frontend.
"""
job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress_message=job.progress_message,
        result=job.result,
        error=job.error
    )

File: /src/api/routers/files.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
import io

from ..services.storage_manager import storage
from ..schemas.document import FileDownloadResponse

router = APIRouter(prefix="/api/v1/files", tags=["files"])

@router.get("/download/{company_name}/{file_path:path}")
async def download_file(company_name: str, file_path: str):
"""
Download a processed file.
For GCS: Returns redirect to signed URL
For Local: Streams file directly
"""
full_path = f"{company_name}/{file_path}"

    if not storage.file_exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    # For GCS, redirect to signed URL
    if hasattr(storage.backend, 'bucket_name'):
        signed_url = storage.get_download_url(full_path)
        return RedirectResponse(url=signed_url)

    # For local, stream file
    content = storage.read_file(full_path)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_path.split('/')[-1]}"}
    )

@router.get("/{company_name}/list")
async def list_company_files(company_name: str):
"""List all files for a company"""
files = storage.list_files(company_name)

    return {
        "company_name": company_name,
        "files": [
            {
                "path": f,
                "download_url": f"/api/v1/files/download/{f}"
            }
            for f in files
        ]
    }

Task 1.6: FastAPI Main Application
File: /src/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .routers import documents, jobs, files

# Create FastAPI app

app = FastAPI(
title="AI-Shark API",
description="VC Document Analysis API",
version="1.0.0"
)

# CORS configuration for React development

app.add_middleware(
CORSMiddleware,
allow_origins=[
"http://localhost:3000", # React dev server
"http://localhost:5173", # Vite default port
],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Include API routers

app.include_router(documents.router)
app.include_router(jobs.router)
app.include_router(files.router)

# Health check

@app.get("/health")
async def health_check():
return {"status": "healthy", "service": "ai-shark-api"}

# Serve React static files (production only)

# In production, frontend/dist will exist from build

frontend_dist = Path("frontend/dist")
if frontend_dist.exists(): # Mount static assets
app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Catch-all route for React Router (SPA)
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}, 404

        # Serve index.html for all other routes (React Router handles routing)
        return FileResponse(str(frontend_dist / "index.html"))

if **name** == "**main**":
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
Task 1.7: Configuration Management
File: /src/api/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings): # API Settings
api_host: str = "0.0.0.0"
api_port: int = 8000

    # Storage Settings
    use_gcs: bool = False
    gcs_bucket_name: str = "ai-shark-outputs"
    output_dir: str = "outputs"

    # LLM Settings (inherited from existing config)
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    # File Upload Limits
    max_file_size_mb: int = 100

    # Job Management
    job_cleanup_hours: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
return Settings()

settings = get_settings()

Milestone 2: React Frontend Setup (Week 1-2)
Task 2.1: Initialize React Project
Commands:

# Navigate to project root

cd /home/chandan/myspace/ai-shark

# Create frontend directory

npm create vite@latest frontend -- --template react-ts

cd frontend

# Install dependencies

npm install

# Install Material-UI

npm install @mui/material @mui/icons-material @emotion/react @emotion/styled

# Install Redux Toolkit

npm install @reduxjs/toolkit react-redux

# Install React Router

npm install react-router-dom

# Install file upload library

npm install react-dropzone

# Install API client

npm install axios

# Install development dependencies

npm install -D @types/node
Task 2.2: Project Structure
Create Directory Structure:

frontend/
├── public/
│ └── vite.svg
├── src/
│ ├── main.tsx # App entry point
│ ├── App.tsx # Root component
│ ├── vite-env.d.ts
│ ├── assets/ # Images, fonts
│ ├── components/ # Reusable components
│ │ ├── FileUpload/
│ │ │ ├── DragDropZone.tsx
│ │ │ └── UploadProgress.tsx
│ │ ├── Layout/
│ │ │ ├── Header.tsx
│ │ │ ├── Sidebar.tsx
│ │ │ └── MainLayout.tsx
│ │ └── common/
│ │ ├── LoadingSpinner.tsx
│ │ └── ErrorAlert.tsx
│ ├── pages/ # Page components
│ │ ├── PitchDeckPage.tsx
│ │ ├── ResultsPage.tsx
│ │ └── NotFoundPage.tsx
│ ├── store/ # Redux store
│ │ ├── index.ts
│ │ ├── hooks.ts # Typed hooks
│ │ └── slices/
│ │ ├── pitchDeckSlice.ts
│ │ └── uiSlice.ts
│ ├── api/ # API client
│ │ ├── client.ts # Axios instance
│ │ └── endpoints/
│ │ ├── documents.ts
│ │ └── jobs.ts
│ ├── types/ # TypeScript types
│ │ ├── api.ts
│ │ └── models.ts
│ └── utils/ # Utilities
│ ├── constants.ts
│ └── formatters.ts
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
Task 2.3: Vite Configuration
File: frontend/vite.config.ts

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
plugins: [react()],
resolve: {
alias: {
'@': path.resolve(\_\_dirname, './src'),
},
},
server: {
port: 3000,
proxy: {
// Proxy API requests to FastAPI during development
'/api': {
target: 'http://localhost:8000',
changeOrigin: true,
},
},
},
build: {
outDir: 'dist',
sourcemap: true,
},
})
Task 2.4: Redux Store Setup
File: frontend/src/store/index.ts

import { configureStore } from '@reduxjs/toolkit'
import pitchDeckReducer from './slices/pitchDeckSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
reducer: {
pitchDeck: pitchDeckReducer,
ui: uiReducer,
},
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
File: frontend/src/store/hooks.ts

import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from './index'

// Typed versions of useDispatch and useSelector
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
File: frontend/src/store/slices/pitchDeckSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface PitchDeckState {
jobId: string | null
status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed'
progressMessage: string
companyName: string | null
files: string[]
metadata: Record<string, any> | null
error: string | null
}

const initialState: PitchDeckState = {
jobId: null,
status: 'idle',
progressMessage: '',
companyName: null,
files: [],
metadata: null,
error: null,
}

const pitchDeckSlice = createSlice({
name: 'pitchDeck',
initialState,
reducers: {
setJobId: (state, action: PayloadAction<string>) => {
state.jobId = action.payload
state.status = 'processing'
},
updateStatus: (state, action: PayloadAction<{
status: PitchDeckState['status']
progressMessage: string
}>) => {
state.status = action.payload.status
state.progressMessage = action.payload.progressMessage
},
setResult: (state, action: PayloadAction<{
companyName: string
files: string[]
metadata: Record<string, any>
}>) => {
state.status = 'completed'
state.companyName = action.payload.companyName
state.files = action.payload.files
state.metadata = action.payload.metadata
},
setError: (state, action: PayloadAction<string>) => {
state.status = 'failed'
state.error = action.payload
},
reset: (state) => {
return initialState
},
},
})

export const { setJobId, updateStatus, setResult, setError, reset } = pitchDeckSlice.actions
export default pitchDeckSlice.reducer
Task 2.5: API Client
File: frontend/src/api/client.ts

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const apiClient = axios.create({
baseURL: API_BASE_URL,
headers: {
'Content-Type': 'application/json',
},
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
(response) => response,
(error) => {
console.error('API Error:', error.response?.data || error.message)
return Promise.reject(error)
}
)
File: frontend/src/api/endpoints/documents.ts

import { apiClient } from '../client'

export interface UploadPitchDeckResponse {
job_id: string
message: string
}

export interface JobStatusResponse {
job_id: string
status: 'pending' | 'processing' | 'completed' | 'failed'
progress_message: string
result?: {
success: boolean
company_name: string
files_created: string[]
metadata: Record<string, any>
}
error?: string
}

export const documentsApi = {
uploadPitchDeck: async (file: File): Promise<UploadPitchDeckResponse> => {
const formData = new FormData()
formData.append('file', file)

    const response = await apiClient.post<UploadPitchDeckResponse>(
      '/v1/documents/pitch-deck',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data

},

getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
const response = await apiClient.get<JobStatusResponse>(
`/v1/jobs/${jobId}/status`
)
return response.data
},

downloadFile: (companyName: string, filePath: string): string => {
return `${apiClient.defaults.baseURL}/v1/files/download/${companyName}/${filePath}`
},
}
Task 2.6: Drag-and-Drop File Upload Component
File: frontend/src/components/FileUpload/DragDropZone.tsx

import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Box, Typography, Paper } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

interface DragDropZoneProps {
onFileSelect: (file: File) => void
acceptedFileTypes?: string[]
maxSizeMB?: number
disabled?: boolean
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
onFileSelect,
acceptedFileTypes = ['.pdf', '.ppt', '.pptx'],
maxSizeMB = 100,
disabled = false,
}) => {
const onDrop = useCallback((acceptedFiles: File[]) => {
if (acceptedFiles.length > 0) {
onFileSelect(acceptedFiles[0])
}
}, [onFileSelect])

const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
onDrop,
accept: {
'application/pdf': ['.pdf'],
'application/vnd.ms-powerpoint': ['.ppt'],
'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
},
maxSize: maxSizeMB _ 1024 _ 1024,
multiple: false,
disabled,
})

return (
<Paper
{...getRootProps()}
elevation={3}
sx={{
        p: 4,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'grey.300',
        bgcolor: isDragActive ? 'action.hover' : 'background.paper',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: disabled ? 'grey.300' : 'primary.main',
          bgcolor: disabled ? 'background.paper' : 'action.hover',
        },
      }} >
<input {...getInputProps()} />

      <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

      <Typography variant="h6" gutterBottom>
        {isDragActive ? 'Drop the file here' : 'Drag & drop your pitch deck'}
      </Typography>

      <Typography variant="body2" color="text.secondary">
        or click to browse
      </Typography>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Supported formats: {acceptedFileTypes.join(', ')} (Max {maxSizeMB}MB)
      </Typography>

      {fileRejections.length > 0 && (
        <Typography color="error" variant="body2" sx={{ mt: 2 }}>
          {fileRejections[0].errors[0].message}
        </Typography>
      )}
    </Paper>

)
}
Task 2.7: Pitch Deck Upload Page
File: frontend/src/pages/PitchDeckPage.tsx

import React, { useState, useEffect } from 'react'
import {
Container,
Typography,
Box,
Card,
CardContent,
LinearProgress,
Alert,
Button,
List,
ListItem,
ListItemText,
ListItemIcon,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import DownloadIcon from '@mui/icons-material/Download'

import { DragDropZone } from '../components/FileUpload/DragDropZone'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setJobId, updateStatus, setResult, setError } from '../store/slices/pitchDeckSlice'
import { documentsApi } from '../api/endpoints/documents'

export const PitchDeckPage: React.FC = () => {
const dispatch = useAppDispatch()
const pitchDeck = useAppSelector((state) => state.pitchDeck)
const [polling, setPolling] = useState(false)

// Handle file upload
const handleFileSelect = async (file: File) => {
try {
dispatch(updateStatus({ status: 'uploading', progressMessage: 'Uploading file...' }))

      const response = await documentsApi.uploadPitchDeck(file)
      dispatch(setJobId(response.job_id))
      setPolling(true)
    } catch (error: any) {
      dispatch(setError(error.response?.data?.detail || 'Upload failed'))
    }

}

// Poll job status
useEffect(() => {
if (!polling || !pitchDeck.jobId) return

    const pollInterval = setInterval(async () => {
      try {
        const status = await documentsApi.getJobStatus(pitchDeck.jobId!)

        dispatch(updateStatus({
          status: status.status as any,
          progressMessage: status.progress_message,
        }))

        if (status.status === 'completed' && status.result) {
          dispatch(setResult({
            companyName: status.result.company_name,
            files: status.result.files_created,
            metadata: status.result.metadata,
          }))
          setPolling(false)
        } else if (status.status === 'failed') {
          dispatch(setError(status.error || 'Processing failed'))
          setPolling(false)
        }
      } catch (error: any) {
        console.error('Polling error:', error)
        dispatch(setError('Failed to fetch job status'))
        setPolling(false)
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)

}, [polling, pitchDeck.jobId, dispatch])

return (
<Container maxWidth="lg" sx={{ py: 4 }}>
<Typography variant="h3" component="h1" gutterBottom>
Phase 1: Pitch Deck Analysis
</Typography>

      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your pitch deck (PDF or PowerPoint) to extract company metadata,
        table of contents, and structured analysis.
      </Typography>

      {/* Upload Zone */}
      {pitchDeck.status === 'idle' && (
        <Box sx={{ my: 4 }}>
          <DragDropZone onFileSelect={handleFileSelect} />
        </Box>
      )}

      {/* Processing Status */}
      {(pitchDeck.status === 'uploading' || pitchDeck.status === 'processing') && (
        <Card sx={{ my: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing...
            </Typography>
            <LinearProgress sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary">
              {pitchDeck.progressMessage}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {pitchDeck.status === 'failed' && (
        <Alert severity="error" sx={{ my: 4 }}>
          {pitchDeck.error}
        </Alert>
      )}

      {/* Results */}
      {pitchDeck.status === 'completed' && pitchDeck.companyName && (
        <Card sx={{ my: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              ✓ Processing Complete
            </Typography>

            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
              Company: {pitchDeck.companyName}
            </Typography>

            {pitchDeck.metadata && (
              <Box sx={{ my: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Sector: {pitchDeck.metadata.sector || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Website: {pitchDeck.metadata.website || 'N/A'}
                </Typography>
              </Box>
            )}

            <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
              Generated Files:
            </Typography>

            <List>
              {pitchDeck.files.map((file) => (
                <ListItem key={file}>
                  <ListItemIcon>
                    <DescriptionIcon />
                  </ListItemIcon>
                  <ListItemText primary={file.split('/').pop()} />
                  <Button
                    startIcon={<DownloadIcon />}
                    href={documentsApi.downloadFile(pitchDeck.companyName!, file.split('/').pop()!)}
                    target="_blank"
                  >
                    Download
                  </Button>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Container>

)
}
Task 2.8: Main App & Router
File: frontend/src/App.tsx

import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { Provider } from 'react-redux'

import { store } from './store'
import { PitchDeckPage } from './pages/PitchDeckPage'
import { NotFoundPage } from './pages/NotFoundPage'

// Premium dark theme
const theme = createTheme({
palette: {
mode: 'light',
primary: {
main: '#1976d2',
},
secondary: {
main: '#dc004e',
},
},
typography: {
fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
},
})

function App() {
return (
<Provider store={store}>
<ThemeProvider theme={theme}>
<CssBaseline />
<BrowserRouter>
<Routes>
<Route path="/" element={<PitchDeckPage />} />
<Route path="\*" element={<NotFoundPage />} />
</Routes>
</BrowserRouter>
</ThemeProvider>
</Provider>
)
}

export default App
Milestone 3: Integration & Testing (Week 2)
Task 3.1: Docker Compose for Development
File: docker-compose.dev.yml

version: '3.8'

services:
api:
build:
context: .
dockerfile: Dockerfile.dev
ports: - "8000:8000"
volumes: - ./src:/app/src - ./outputs:/app/outputs
environment: - USE_GCS=false - OUTPUT_DIR=/app/outputs - GOOGLE_API_KEY=${GOOGLE_API_KEY}
command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

frontend:
build:
context: ./frontend
dockerfile: Dockerfile.dev
ports: - "3000:3000"
volumes: - ./frontend/src:/app/src - ./frontend/public:/app/public
environment: - VITE_API_URL=http://localhost:8000/api
command: npm run dev -- --host 0.0.0.0

streamlit:
build:
context: .
dockerfile: Dockerfile
ports: - "8501:8501"
volumes: - ./src:/app/src - ./outputs:/app/outputs
environment: - GOOGLE_API_KEY=${GOOGLE_API_KEY}
command: streamlit run streamlit_ui.py --server.port=8501
File: Dockerfile.dev (API)

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install -e .

COPY src/ ./src/

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
File: frontend/Dockerfile.dev

FROM node:18-alpine

WORKDIR /app

COPY package\*.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
Task 3.2: Production Dockerfile (Multi-stage)
File: Dockerfile

# Stage 1: Build React Frontend

FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package\*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Output: /app/frontend/dist

# Stage 2: Python API

FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy source code

COPY src/ ./src/
COPY streamlit_ui.py ./

# Copy React build from stage 1

COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port

EXPOSE 8080

# Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
 CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run FastAPI (serves both API and React)

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
Task 3.3: Environment Variables
File: .env.example

# LLM Configuration

GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Storage Configuration

USE_GCS=false # Set to true for production
GCS_BUCKET_NAME=ai-shark-outputs
OUTPUT_DIR=outputs

# API Configuration

API_PORT=8000

# File Upload

MAX_FILE_SIZE_MB=100
Task 3.4: Testing Strategy
Integration Tests - Backend File: tests/api/test_pitch_deck_upload.py

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_upload_pitch_deck():
"""Test pitch deck upload endpoint"""
with open("tests/fixtures/sample_deck.pdf", "rb") as f:
response = client.post(
"/api/v1/documents/pitch-deck",
files={"file": ("sample_deck.pdf", f, "application/pdf")}
)

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["message"] == "Pitch deck uploaded successfully. Processing started."

def test_job_status():
"""Test job status polling""" # First upload a file to get job_id
with open("tests/fixtures/sample_deck.pdf", "rb") as f:
upload_response = client.post(
"/api/v1/documents/pitch-deck",
files={"file": ("sample_deck.pdf", f, "application/pdf")}
)

    job_id = upload_response.json()["job_id"]

    # Poll status
    response = client.get(f"/api/v1/jobs/{job_id}/status")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "progress_message" in data

def test_invalid_file_type():
"""Test rejection of invalid file types"""
with open("tests/fixtures/invalid.txt", "rb") as f:
response = client.post(
"/api/v1/documents/pitch-deck",
files={"file": ("invalid.txt", f, "text/plain")}
)

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

Integration Tests - Frontend File: frontend/src/tests/PitchDeckPage.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { store } from '../store'
import { PitchDeckPage } from '../pages/PitchDeckPage'

const renderWithProviders = (component: React.ReactElement) => {
return render(
<Provider store={store}>
<BrowserRouter>
{component}
</BrowserRouter>
</Provider>
)
}

test('renders pitch deck upload page', () => {
renderWithProviders(<PitchDeckPage />)
expect(screen.getByText(/Phase 1: Pitch Deck Analysis/i)).toBeInTheDocument()
})

test('handles file upload', async () => {
renderWithProviders(<PitchDeckPage />)

const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
const input = screen.getByLabelText(/drag & drop/i)

fireEvent.change(input, { target: { files: [file] } })

await waitFor(() => {
expect(screen.getByText(/Processing/i)).toBeInTheDocument()
})
})
Milestone 4: Deployment to Cloud Run (Week 3)
Task 4.1: GCS Bucket Setup
Commands:

# Create GCS bucket

gcloud storage buckets create gs://ai-shark-outputs \
 --location=us-central1 \
 --uniform-bucket-level-access

# Set lifecycle policy (optional - auto-delete old files)

cat > lifecycle.json <<EOF
{
"lifecycle": {
"rule": [
{
"action": {"type": "Delete"},
"condition": {"age": 90}
}
]
}
}
EOF

gcloud storage buckets update gs://ai-shark-outputs --lifecycle-file=lifecycle.json
Task 4.2: Cloud Run Deployment
File: .gcloudignore

.git
.gitignore
node_modules
frontend/node_modules
outputs/
\*.pyc
**pycache**
.env
.venv
tests/
Deploy Commands:

# Build and deploy

gcloud run deploy ai-shark \
 --source . \
 --region us-central1 \
 --platform managed \
 --allow-unauthenticated \
 --set-env-vars USE_GCS=true,GCS_BUCKET_NAME=ai-shark-outputs \
 --set-secrets GOOGLE_API_KEY=google-api-key:latest \
 --memory 2Gi \
 --cpu 2 \
 --timeout 600 \
 --max-instances 10 \
 --min-instances 0

# Get deployed URL

gcloud run services describe ai-shark --region us-central1 --format='value(status.url)'
Task 4.3: CI/CD with GitHub Actions (Optional)
File: .github/workflows/deploy.yml

name: Deploy to Cloud Run

on:
push:
branches: [main]

jobs:
deploy:
runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ai-shark \
            --source . \
            --region us-central1 \
            --platform managed \
            --allow-unauthenticated \
            --set-env-vars USE_GCS=true,GCS_BUCKET_NAME=ai-shark-outputs \
            --set-secrets GOOGLE_API_KEY=google-api-key:latest

Critical Files Summary
Files to Create (Backend):
/src/api/main.py - FastAPI app
/src/api/config.py - Settings
/src/api/services/storage_manager.py - GCS/Local abstraction
/src/api/services/job_manager.py - Job tracking
/src/api/routers/documents.py - Upload endpoints
/src/api/routers/jobs.py - Status endpoints
/src/api/routers/files.py - Download endpoints
/src/api/schemas/document.py - Pydantic models
Files to Create (Frontend):
/frontend/src/App.tsx - Root component
/frontend/src/pages/PitchDeckPage.tsx - Main page
/frontend/src/store/slices/pitchDeckSlice.ts - Redux slice
/frontend/src/api/endpoints/documents.ts - API client
/frontend/src/components/FileUpload/DragDropZone.tsx - Upload component
/frontend/vite.config.ts - Vite config
Files to Modify:
/pyproject.toml - Add FastAPI dependencies
/Dockerfile - Multi-stage build
/docker-compose.yml - Add services
/src/processors/pitch_deck_processor.py - Integrate with StorageManager
Testing Checklist
Backend Tests:
Pitch deck upload (valid file)
File type validation (reject invalid)
File size validation (reject > 100MB)
Job status polling
File download (local)
File download (GCS signed URL)
Error handling (missing file, invalid job_id)
Frontend Tests:
Drag and drop file upload
Upload progress indicator
Status polling (2-second interval)
Result display (company name, files)
File download links
Error messages display
Responsive design (mobile/tablet/desktop)
Integration Tests:
End-to-end: Upload → Process → Display results
Multiple file formats (PDF, PPT, PPTX)
Large file handling (50-100MB)
Network error recovery
Browser localStorage persistence
Deployment Tests:
Docker build succeeds
Docker Compose starts all services
Cloud Run deployment succeeds
GCS file upload/download
HTTPS/SSL working
Environment variables loaded correctly
Next Steps After Phase 1
Once Phase 1 is complete and tested, the implementation will continue with:
Phase 2: Additional Documents Upload (similar pattern to Phase 1)
Phase 3: Multi-Agent Analysis (more complex - parallel agent execution)
Phase 4: Founder Simulation (two paths: reference docs vs direct Q&A)
Phase 5: Final Memo with weight configuration sliders
Each phase will follow the same pattern:
Backend: Add routes + update processors to use StorageManager
Frontend: Create page component + Redux slice
Integration: Add to main navigation flow
Handoff Notes for New Agent
If a new agent continues this work, they should:
Start with Backend First: Implement all Task 1.x items before frontend
Test Each Component: Don't move to next task until current one is tested
Follow Naming Conventions: Use same patterns established in examples
Preserve Existing Code: Don't modify /src/processors/ logic, only wrap it
Check Environment: Ensure .env file has GOOGLE_API_KEY before testing
Use Type Hints: Python uses type hints, TypeScript uses interfaces
Material-UI Components: Stick to MUI for consistent premium look
Redux Pattern: All state changes via dispatched actions, no direct mutation
Storage Abstraction: Always use storage.save_file(), never direct file writes
Polling Interval: Keep at 2-3 seconds to balance responsiveness and API load
Key Architecture Principles:
Backend processes are async (background tasks)
Frontend polls for status (no WebSockets)
Storage is abstracted (works locally and on GCS)
No authentication (single-user app)
Single deployment (FastAPI serves React)
