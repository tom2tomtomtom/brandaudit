#!/bin/bash
set -e

# Debug: Print environment info
echo "=== Docker Container Environment Debug ==="
echo "PORT environment variable: ${PORT:-'NOT SET'}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-'NOT SET'}"
echo "Container hostname: $(hostname)"
echo "Container IP: $(hostname -i 2>/dev/null || echo 'N/A')"
echo "All environment variables with PORT:"
env | grep -i port || echo "No PORT variables found"
echo "============================================"

# Set PORT with Railway's default if not set
export PORT=${PORT:-8080}
echo "Using PORT: $PORT"

# Validate that the port is available
echo "Checking if port $PORT is available..."
if netstat -tuln | grep -q ":$PORT "; then
    echo "⚠️  Port $PORT is already in use!"
    netstat -tuln | grep ":$PORT"
else
    echo "✅ Port $PORT is available"
fi

# Start the application with better configuration
echo "Starting gunicorn on 0.0.0.0:$PORT"
echo "Worker class: sync"
echo "Workers: 1"
echo "Timeout: 120s"
echo "Keep alive: 2s"

exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
