# Multi-stage build for optimized AI Brand Audit Tool (Combined Frontend + Backend)

# Frontend build stage
FROM node:20-alpine as frontend-builder

# Set environment variables
ENV NODE_ENV=production \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

# Install pnpm
RUN corepack enable

WORKDIR /app

# Copy frontend package files for better caching
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies with cache mount
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# Copy frontend source and build
COPY frontend/ ./
RUN pnpm build

# Python dependencies stage
FROM python:3.11-slim as python-deps

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements-minimal.txt ./
RUN pip install --user -r requirements-minimal.txt

# Final production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    PORT=8000 \
    PATH=/root/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    procps \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for backend
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy Python dependencies from python-deps stage
COPY --from=python-deps /root/.local /root/.local

# Copy backend application code
COPY backend/ ./

# Copy frontend build from frontend-builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create necessary directories with proper permissions
RUN mkdir -p logs uploads instance /var/log/supervisor && \
    chown -R appuser:appuser /app

# Remove default nginx configuration
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

# Create optimized nginx configuration
RUN echo 'server { \
    listen 80 default_server; \
    server_name _; \
    client_max_body_size 16M; \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Static assets with long cache \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        root /usr/share/nginx/html; \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # Frontend SPA routing \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
        expires 1h; \
        add_header Cache-Control "public, must-revalidate"; \
    } \
    \
    # API proxy with optimized settings \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_redirect off; \
        proxy_buffering off; \
        proxy_read_timeout 300s; \
        proxy_connect_timeout 60s; \
        proxy_send_timeout 300s; \
    } \
    \
    # WebSocket support for real-time updates \
    location /socket.io/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Create supervisor configuration for managing both services
RUN echo '[supervisord] \
nodaemon=true \
user=root \
logfile=/var/log/supervisor/supervisord.log \
pidfile=/var/run/supervisord.pid \
\
[program:backend] \
command=/root/.local/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --worker-class sync --timeout 300 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 --preload --log-level info --access-logfile - --error-logfile - app:app \
directory=/app \
user=appuser \
autostart=true \
autorestart=true \
stderr_logfile=/var/log/supervisor/backend.err.log \
stdout_logfile=/var/log/supervisor/backend.out.log \
environment=PYTHONPATH="/app",FLASK_ENV="production",PORT="8000" \
\
[program:nginx] \
command=/usr/sbin/nginx -g "daemon off;" \
autostart=true \
autorestart=true \
stderr_logfile=/var/log/supervisor/nginx.err.log \
stdout_logfile=/var/log/supervisor/nginx.out.log' > /etc/supervisor/conf.d/supervisord.conf

# Create startup script with proper initialization
RUN echo '#!/bin/bash \
set -e \
\
echo "🚀 Starting AI Brand Audit Tool (Production Mode)" \
echo "📍 Environment: ${FLASK_ENV:-production}" \
echo "📍 Port: ${PORT:-8000}" \
\
# Validate Python application \
echo "📍 Validating Python application..." \
cd /app \
python -c "import app; print('\''✅ Application imports successfully'\'')" \
\
# Test nginx configuration \
echo "📍 Testing nginx configuration..." \
nginx -t \
echo "✅ Nginx configuration is valid" \
\
# Initialize database if needed \
echo "📍 Initializing database..." \
python -c "from src.extensions import db; from app import app; app.app_context().push(); db.create_all(); print('\''✅ Database initialized'\'')" || echo "⚠️ Database initialization skipped" \
\
# Start supervisor to manage both services \
echo "📍 Starting services with supervisor..." \
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /start.sh && chmod +x /start.sh

# Validate application can start
RUN cd /app && python -c "import app; print('✅ Application validation successful')"

# Add comprehensive health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/api/health && curl -f http://localhost/health || exit 1

# Expose port
EXPOSE 80

# Use the startup script
CMD ["/start.sh"]