# AI Brand Audit Tool - Production Deployment Guide

This guide covers production deployment options for the AI Brand Audit Tool with optimized configurations for performance, security, and scalability.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for self-hosting)
```bash
# 1. Clone and setup
git clone <repository-url>
cd brand-audit-app

# 2. Configure environment
cp .env.template .env
# Edit .env with your configuration

# 3. Deploy
chmod +x deploy.sh
./deploy.sh docker production
```

### Option 2: Railway (Recommended for cloud deployment)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Deploy
./deploy.sh railway production
```

## 📋 Prerequisites

### System Requirements
- **Docker**: 20.10+ with Docker Compose v2
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: 10GB+ available space
- **Network**: Ports 80, 443, 5432, 6379 available

### Required Environment Variables
```bash
# Security (Generate secure random values)
SECRET_KEY=your-secret-key-here-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-here-minimum-32-characters

# API Keys (Required for full functionality)
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
NEWS_API_KEY=your-news-api-key-here
BRANDFETCH_API_KEY=your-brandfetch-api-key-here
OPENCORPORATES_API_KEY=your-opencorporates-api-key-here

# Database (Auto-configured for Docker Compose)
DATABASE_URL=postgresql://user:password@postgres:5432/brandaudit

# CORS (Update with your domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🐳 Docker Compose Deployment

### Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │    Frontend     │    │    Backend      │
│  Load Balancer  │────│   (React/Vue)   │────│   (Flask API)   │
│   & SSL Term    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │              ┌─────────────────┐            │
         └──────────────│   PostgreSQL    │────────────┘
                        │    Database     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │      Redis      │
                        │  Cache & Queue  │
                        └─────────────────┘
```

### Production Configuration Files

#### docker-compose.yml
- Base configuration with all services
- PostgreSQL 15 with optimized settings
- Redis for caching and background tasks
- Multi-stage Docker builds for optimization

#### docker-compose.prod.yml
- Production overrides with scaling
- Resource limits and reservations
- Enhanced logging configuration
- SSL/TLS termination ready

#### docker-compose.override.yml
- Development overrides (auto-loaded)
- Hot reloading for development
- Exposed database ports for debugging

### Deployment Commands

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale backend services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=2

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Health check
curl http://localhost/api/health

# Stop deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Monitoring and Maintenance

#### Health Endpoints
- `/api/health` - Comprehensive health check
- `/api/health/ready` - Kubernetes readiness probe
- `/api/health/live` - Kubernetes liveness probe
- `/api/database/status` - Database connection pool status

#### Log Management
```bash
# View application logs
docker-compose logs -f backend

# View nginx access logs
docker-compose logs -f nginx

# View database logs
docker-compose logs -f postgres
```

#### Backup Strategy
```bash
# Database backup
docker-compose exec postgres pg_dump -U brandaudit_user brandaudit > backup.sql

# Volume backup
docker run --rm -v brand-audit-app_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## 🚂 Railway Deployment

### Setup Process

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   railway init
   railway link [project-id]
   ```

3. **Configure Environment Variables**
   ```bash
   # Set required variables
   railway variables set SECRET_KEY="your-secret-key"
   railway variables set JWT_SECRET_KEY="your-jwt-secret-key"
   railway variables set OPENROUTER_API_KEY="your-openrouter-key"
   railway variables set NEWS_API_KEY="your-news-key"
   railway variables set BRANDFETCH_API_KEY="your-brandfetch-key"
   
   # Set optional variables
   railway variables set ALLOWED_ORIGINS="https://your-domain.com"
   railway variables set LOG_LEVEL="INFO"
   ```

4. **Add PostgreSQL Service**
   ```bash
   railway add postgresql
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### Railway Configuration

The `railway.prod.json` file includes:
- Multi-stage Docker build optimization
- Health check configuration
- Environment-specific variables
- PostgreSQL plugin integration
- Zero-downtime deployment settings

### Monitoring Railway Deployment

```bash
# View deployment status
railway status

# View logs
railway logs

# View metrics
railway metrics

# Connect to database
railway connect postgresql
```

## 🔧 Performance Optimization

### Database Optimization
- Connection pooling with configurable limits
- Query optimization and indexing
- Automated health monitoring
- Connection leak detection

### Caching Strategy
- Redis for session storage
- API response caching
- Static asset caching with CDN-ready headers
- Database query result caching

### Static File Optimization
- Nginx with gzip compression
- Long-term caching for assets
- CDN-ready cache headers
- Optimized image serving

### Application Performance
- Multi-worker Gunicorn configuration
- Async task processing with Celery
- Request rate limiting
- Memory usage optimization

## 🔒 Security Features

### Application Security
- JWT token authentication
- CORS configuration
- Input validation and sanitization
- SQL injection prevention
- XSS protection headers

### Infrastructure Security
- Non-root container users
- Secret management
- Network isolation
- SSL/TLS termination
- Security headers (CSP, HSTS, etc.)

### Monitoring and Alerting
- Health check endpoints
- Error tracking and logging
- Performance metrics
- Security event monitoring

## 📊 Monitoring and Observability

### Built-in Monitoring
- Application health checks
- Database connection monitoring
- API performance metrics
- Error rate tracking

### Optional Monitoring Stack
Enable with `--profile monitoring`:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **AlertManager**: Alert routing

```bash
# Enable monitoring
docker-compose --profile monitoring up -d

# Access Grafana
open http://localhost:3001
```

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Check environment variables
docker-compose config

# Validate Docker image
docker run --rm -it brand-audit-app_backend:latest /bin/bash
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection pool
curl http://localhost/api/database/status

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check application metrics
curl http://localhost/api/health/metrics

# Scale services
docker-compose up -d --scale backend=2
```

### Health Check Failures
```bash
# Check health endpoint
curl -v http://localhost/api/health

# Check individual services
curl http://localhost/api/health/ready
curl http://localhost/api/database/health-summary
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway up --environment production
```

### Automated Testing
```bash
# Run full test suite
./deploy.sh docker production false

# Run only integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Multiple backend replicas
- Load balancing with Nginx
- Database read replicas
- Redis clustering

### Vertical Scaling
- Resource limit adjustments
- Memory optimization
- CPU allocation tuning
- Storage performance optimization

### Auto-scaling (Kubernetes)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: brand-audit-backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: brand-audit-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🆘 Support and Maintenance

### Regular Maintenance Tasks
- Database backups and cleanup
- Log rotation and archival
- Security updates
- Performance monitoring
- Capacity planning

### Emergency Procedures
- Rollback procedures
- Database recovery
- Service restoration
- Incident response

For additional support, please refer to the project documentation or create an issue in the repository.
