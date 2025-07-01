FROM python:3.10-slim-buster
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads instance

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8000

# Test app can start
RUN python -c "from src.main import app; print('✅ App imports successfully')"

EXPOSE $PORT

# Use startup script for better debugging
CMD ["python", "start.py"]