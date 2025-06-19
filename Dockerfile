# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/
COPY examples/ ./examples/
COPY main.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash qrlp && \
    chown -R qrlp:qrlp /app
USER qrlp

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/status')" || exit 1

# Default command
CMD ["python", "main.py", "--port", "8080", "--host", "0.0.0.0"] 