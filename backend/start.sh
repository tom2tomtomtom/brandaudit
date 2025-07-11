#!/bin/bash
set -e

# Graceful shutdown handler
cleanup() {
    echo "🛑 Received shutdown signal, performing graceful shutdown..."

    # Send SIGTERM to gunicorn master process
    if [ ! -z "$GUNICORN_PID" ]; then
        echo "📍 Sending SIGTERM to gunicorn (PID: $GUNICORN_PID)"
        kill -TERM "$GUNICORN_PID" 2>/dev/null || true

        # Wait for graceful shutdown with timeout
        echo "📍 Waiting for graceful shutdown (max 30 seconds)..."
        for i in {1..30}; do
            if ! kill -0 "$GUNICORN_PID" 2>/dev/null; then
                echo "✅ Gunicorn shut down gracefully"
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if kill -0 "$GUNICORN_PID" 2>/dev/null; then
            echo "⚠️ Forcing shutdown of gunicorn"
            kill -KILL "$GUNICORN_PID" 2>/dev/null || true
        fi
    fi

    echo "🏁 Shutdown complete"
    exit 0
}

# Register signal handlers
trap cleanup SIGTERM SIGINT SIGUSR1

# Debug: Print environment info
echo "=== Production Container Environment ==="
echo "PORT environment variable: ${PORT:-'NOT SET'}"
echo "FLASK_ENV: ${FLASK_ENV:-'NOT SET'}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-'NOT SET'}"
echo "Container hostname: $(hostname)"
echo "Container IP: $(hostname -i 2>/dev/null || echo 'N/A')"
echo "Process ID: $$"
echo "========================================"

# Set PORT with Railway's default if not set
export PORT=${PORT:-8080}
echo "📍 Using PORT: $PORT"

# Validate environment
echo "📍 Validating environment configuration..."
python -c "
from src.config.env_validator import get_validation_report
import json
report = get_validation_report()
print('✅ Environment validation completed')
if not report['is_valid']:
    print('⚠️ Environment validation warnings:')
    for error in report['errors']:
        print(f'   • {error}')
"

# Validate that the port is available
echo "📍 Checking if port $PORT is available..."
if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo "⚠️ Port $PORT is already in use!"
    netstat -tuln | grep ":$PORT" || true
else
    echo "✅ Port $PORT is available"
fi

# Test application startup
echo "📍 Testing application startup..."
python -c "
import app
print('✅ Application imports successfully')
try:
    with app.app.test_client() as client:
        response = client.get('/api/health/live')
        if response.status_code == 200:
            print('✅ Health check endpoint working')
        else:
            print(f'⚠️ Health check returned status: {response.status_code}')
except Exception as e:
    print(f'⚠️ Health check test failed: {e}')
"

# Calculate optimal worker count (but cap at 4 for resource efficiency)
WORKERS=${WORKERS:-$(python -c "import os; print(min(4, max(1, (os.cpu_count() or 1) * 2 + 1)))")}

# Start the application with production configuration
echo "🚀 Starting gunicorn with production configuration"
echo "📍 Bind: 0.0.0.0:$PORT"
echo "📍 Workers: $WORKERS"
echo "📍 Worker class: sync"
echo "📍 Timeout: 300s (for long-running brand analysis)"
echo "📍 Keep alive: 2s"
echo "📍 Max requests: 1000 (with jitter)"
echo "📍 Graceful timeout: 30s"

# Start gunicorn in background to capture PID
gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class sync \
    --timeout 300 \
    --graceful-timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --pid /tmp/gunicorn.pid \
    app:app &

# Capture gunicorn PID
GUNICORN_PID=$!
echo "📍 Gunicorn started with PID: $GUNICORN_PID"

# Wait for gunicorn to start
sleep 3

# Verify gunicorn is running
if kill -0 "$GUNICORN_PID" 2>/dev/null; then
    echo "✅ Gunicorn is running successfully"

    # Test health endpoint
    echo "📍 Testing health endpoint..."
    curl -f "http://localhost:$PORT/api/health/live" -m 10 || echo "⚠️ Health endpoint test failed"

else
    echo "❌ Gunicorn failed to start"
    exit 1
fi

# Wait for gunicorn process (this keeps the script running)
echo "📍 Application ready - waiting for shutdown signal..."
wait $GUNICORN_PID
