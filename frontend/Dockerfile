# Multi-stage build for optimized production frontend
FROM node:20-alpine as base

# Set environment variables for Node.js
ENV NODE_ENV=production \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

# Install pnpm globally
RUN corepack enable

# Dependencies stage
FROM base as dependencies

WORKDIR /app

# Copy package files for dependency caching
COPY package.json pnpm-lock.yaml ./

# Install dependencies with frozen lockfile
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile --prod=false

# Build stage
FROM dependencies as builder

# Copy source code
COPY . .

# Build the application
RUN pnpm build

# Production stage with optimized nginx
FROM nginx:1.25-alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx configuration
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create optimized nginx configuration for SPA with security headers
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
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
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
        add_header X-Content-Type-Options "nosniff" always; \
    } \
    \
    # HTML files with short cache \
    location ~* \.html$ { \
        expires 1h; \
        add_header Cache-Control "public, must-revalidate"; \
        add_header X-Content-Type-Options "nosniff" always; \
    } \
    \
    # SPA routing \
    location / { \
        try_files $uri $uri/ /index.html; \
        expires 1h; \
        add_header Cache-Control "public, must-revalidate"; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Create nginx.conf with optimized settings
RUN echo 'user nginx; \
worker_processes auto; \
error_log /var/log/nginx/error.log notice; \
pid /var/run/nginx.pid; \
\
events { \
    worker_connections 1024; \
    use epoll; \
    multi_accept on; \
} \
\
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    \
    log_format main "$remote_addr - $remote_user [$time_local] \"$request\" " \
                    "$status $body_bytes_sent \"$http_referer\" " \
                    "\"$http_user_agent\" \"$http_x_forwarded_for\""; \
    \
    access_log /var/log/nginx/access.log main; \
    \
    sendfile on; \
    tcp_nopush on; \
    tcp_nodelay on; \
    keepalive_timeout 65; \
    types_hash_max_size 2048; \
    client_max_body_size 16M; \
    \
    include /etc/nginx/conf.d/*.conf; \
}' > /etc/nginx/nginx.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80

# Use nginx with optimized configuration
CMD ["nginx", "-g", "daemon off;"]