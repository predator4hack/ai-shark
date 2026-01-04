from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .routers import documents, jobs, files, analysis

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
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(documents.router)
app.include_router(jobs.router)
app.include_router(files.router)
app.include_router(analysis.router)


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
            "run_analysis": "/api/v1/analysis/run-agents"
        }
    }


# Serve React static files (production only)
# In production, frontend/dist will exist from build
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Catch-all route for React Router (SPA)
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}, 404

        # Serve index.html for all other routes (React Router handles routing)
        return FileResponse(str(frontend_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
