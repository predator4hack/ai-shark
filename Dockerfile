# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
# Install uv
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir uv
RUN /opt/venv/bin/uv sync --frozen

# Stage 2: Final image
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

# Expose the port Streamlit will listen on
EXPOSE 8080

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_ui.py", "--server.port", "8080", "--server.address", "0.0.0.0"]