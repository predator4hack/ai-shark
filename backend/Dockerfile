# Production Backend-only Dockerfile - Aviato VC Document Analyzer
# Stage 1: Python Dependencies Builder
FROM python:3.11-slim AS python-builder

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables for UV
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
WORKDIR /app
COPY pyproject.toml ./

# Generate lockfile and install dependencies using UV
RUN uv lock && uv sync --no-dev

# =============================================================================
# Stage 2: Production Runtime
FROM python:3.11-slim AS production

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libfontconfig1 \
    libxrender1 \
    libxext6 \
    libx11-6 \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from python-builder stage
COPY --from=python-builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code (backend only)
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser task_config.py ./
COPY --chown=appuser:appuser pyproject.toml ./

# Create outputs directory for file processing
RUN mkdir -p /app/outputs && chown appuser:appuser /app/outputs

# Ensure appuser has proper home directory permissions
RUN chown -R appuser:appuser /home/appuser

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Health check for FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run FastAPI backend only
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
