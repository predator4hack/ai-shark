#!/usr/bin/env python3
"""
Quick test script to verify the FastAPI backend is working
"""

import uvicorn
from src.api.main import app

if __name__ == "__main__":
    print("🚀 Starting AI-Shark FastAPI server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📍 API Root: http://localhost:8000/api")
    print("📍 Health Check: http://localhost:8000/health")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
