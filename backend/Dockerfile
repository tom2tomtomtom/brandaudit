FROM python:3.10-slim-buster
WORKDIR /app

# Install system dependencies including procps for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p logs uploads instance

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Test minimal app can start
RUN python -c "import app; print('✅ Minimal app imports successfully')"

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Add health check for better container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/health || exit 1

# Use the start script
CMD ["./start.sh"]