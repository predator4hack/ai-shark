from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers import documents, jobs, files, analysis, cache

# Create FastAPI app
app = FastAPI(
    title="AI-Shark API",
    description="VC Document Analysis API",
    version="1.0.0"
)

# CORS configuration
# Get frontend URL from environment (for production deployment)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Build allowed origins list
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite default port
    frontend_url,  # Production frontend from environment variable
]

# Remove duplicates
allowed_origins = list(set(allowed_origins))

# Debug log for CORS configuration
print(f"🔐 CORS Configuration:")
print(f"   FRONTEND_URL env var: {os.getenv('FRONTEND_URL', 'NOT SET')}")
print(f"   Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(documents.router)
app.include_router(jobs.router)
app.include_router(files.router)
app.include_router(analysis.router)
app.include_router(cache.router)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-shark-api"}


# Root endpoint
@app.get("/api")
async def api_root():
    return {
        "message": "AI-Shark API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "pitch_deck_upload": "/api/v1/documents/pitch-deck",
            "job_status": "/api/v1/jobs/{job_id}/status",
            "file_download": "/api/v1/files/download/{company_name}/{file_path}",
            "discover_agents": "/api/v1/analysis/discover-agents",
            "run_analysis": "/api/v1/analysis/run-agents",
            "cache_status": "/api/v1/cache/status",
            "invalidate_cache": "/api/v1/cache/invalidate"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
