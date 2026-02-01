FROM python:3.11-slim
WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements_core.txt requirements.txt ./

# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ -f requirements_core.txt ]; then pip install --no-cache-dir -r requirements_core.txt || true; fi

# Copy source code (after requirements for better caching)
COPY backend/ ./backend/
COPY python-tools/ ./python-tools/
COPY providers/ ./providers/
COPY services/ ./services/
COPY security/ ./security/
COPY orchestration/ ./orchestration/
COPY config/ ./config/
COPY intelligence/ ./intelligence/
COPY main.py audit_log.py email_service.py ./

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app:/app/python-tools

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
