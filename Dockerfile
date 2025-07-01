# Multi-stage build for AI Brand Audit Tool
FROM node:20-alpine as frontend-builder
WORKDIR /app

# Copy frontend package files
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy frontend source
COPY frontend/ ./
RUN pnpm build

# Final stage with both frontend and backend
FROM python:3.10-slim

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setup Python backend
WORKDIR /app
COPY backend/requirements-minimal.txt ./
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy backend code
COPY backend/app.py ./

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create nginx config that serves frontend and proxies API to backend
RUN echo 'server { \
    listen 80; \
    server_name _; \
    \
    # Serve frontend static files \
    location / { \
        root /usr/share/nginx/html; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Proxy API requests to Python backend \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_redirect off; \
    } \
}' > /etc/nginx/sites-available/default

# Create startup script that runs both services
RUN echo '#!/bin/bash \
set -e \
echo "🚀 Starting AI Brand Audit Tool (Combined Frontend + Backend)..." \
echo "📍 Starting Python backend on port 8000..." \
python app.py & \
sleep 2 \
echo "📍 Starting Nginx frontend on port 80..." \
nginx -g "daemon off;"' > /start.sh && chmod +x /start.sh

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8000

EXPOSE 80

CMD ["/start.sh"]