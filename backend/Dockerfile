# Multi-stage build for optimized production backend
FROM python:3.11-slim as base

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Dependencies stage
FROM base as dependencies

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements-minimal.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM base as production

WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY backend/ .

# Create necessary directories with proper permissions
RUN mkdir -p logs uploads instance && \
    chown -R appuser:appuser /app

# Make start script executable
RUN chmod +x start.sh

# Set production environment variables
ENV FLASK_ENV=production \
    PYTHONPATH=/app \
    PORT=8080

# Validate application can import successfully
RUN python -c "import app; print('✅ Application imports successfully')"

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Add comprehensive health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/health || exit 1

# Use the start script
CMD ["./start.sh"]