#!/usr/bin/env python3
"""
Environment Template Generator
Generates .env template files with proper documentation and validation
"""

import os
import sys
from src.config.env_validator import generate_env_template, get_validation_report


def main():
    """Generate environment template and validation report"""
    print("🔧 AI Brand Audit Tool - Environment Configuration Generator")
    print("=" * 60)
    
    # Generate template
    template_content = generate_env_template()
    
    # Write template file
    template_path = ".env.template"
    with open(template_path, "w") as f:
        f.write(template_content)
    
    print(f"✅ Environment template generated: {template_path}")
    
    # Generate validation report
    report = get_validation_report()
    
    print("\n📊 Current Environment Status:")
    print("-" * 40)
    
    if report["is_valid"]:
        print("✅ Environment configuration is valid")
    else:
        print("❌ Environment configuration has issues:")
        for error in report["errors"]:
            print(f"   • {error}")
    
    if report["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in report["warnings"]:
            print(f"   • {warning}")
    
    print("\n📋 Configuration Variables:")
    print("-" * 40)
    
    for var in report["configured_vars"]:
        status = "✅" if var["configured"] else "❌"
        required = "REQUIRED" if var["required"] else "OPTIONAL"
        sensitive = " (SENSITIVE)" if var["sensitive"] else ""
        
        print(f"{status} {var['name']} [{required}]{sensitive}")
        print(f"   {var['description']}")
        print()
    
    # Generate Docker environment file
    docker_env_content = generate_docker_env_template()
    docker_env_path = ".env.docker"
    with open(docker_env_path, "w") as f:
        f.write(docker_env_content)
    
    print(f"🐳 Docker environment template generated: {docker_env_path}")
    
    # Generate Railway environment instructions
    railway_instructions = generate_railway_instructions()
    railway_path = "RAILWAY_DEPLOYMENT.md"
    with open(railway_path, "w") as f:
        f.write(railway_instructions)
    
    print(f"🚂 Railway deployment instructions generated: {railway_path}")
    
    print("\n🎯 Next Steps:")
    print("1. Copy .env.template to .env and fill in your values")
    print("2. For Docker: Use .env.docker as reference")
    print("3. For Railway: Follow instructions in RAILWAY_DEPLOYMENT.md")
    print("4. Run validation: python -c 'from src.config.env_validator import get_validation_report; print(get_validation_report())'")


def generate_docker_env_template():
    """Generate Docker-specific environment template"""
    return """# Docker Environment Configuration for AI Brand Audit Tool
# This file is used for docker-compose deployments

# Security (Generate secure random values)
SECRET_KEY=your-secret-key-here-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-here-minimum-32-characters

# Database (Use PostgreSQL for production)
DATABASE_URL=postgresql://user:password@db:5432/brandaudit

# API Keys (Required for full functionality)
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
NEWS_API_KEY=your-news-api-key-here
BRANDFETCH_API_KEY=your-brandfetch-api-key-here
OPENCORPORATES_API_KEY=your-opencorporates-api-key-here

# Application Settings
FLASK_ENV=production
PORT=8080
DEBUG=false

# CORS (Add your frontend domains)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Upload
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=16777216

# Rate Limiting (Use Redis for production)
RATE_LIMIT_STORAGE_URL=redis://redis:6379/0
DEFAULT_RATE_LIMIT=200 per day, 50 per hour

# Logging
LOG_LEVEL=INFO

# Background Tasks (Redis required)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Docker-specific settings
POSTGRES_DB=brandaudit
POSTGRES_USER=brandaudit_user
POSTGRES_PASSWORD=secure_password_here
REDIS_URL=redis://redis:6379/0
"""


def generate_railway_instructions():
    """Generate Railway deployment instructions"""
    return """# Railway Deployment Guide for AI Brand Audit Tool

## Prerequisites
1. Railway account (https://railway.app)
2. Railway CLI installed
3. API keys for external services

## Environment Variables Setup

### Required Variables
Set these in your Railway project dashboard or via CLI:

```bash
# Security
railway variables set SECRET_KEY="your-secret-key-here-minimum-32-characters"
railway variables set JWT_SECRET_KEY="your-jwt-secret-key-here-minimum-32-characters"

# API Keys
railway variables set OPENROUTER_API_KEY="sk-or-your-openrouter-api-key-here"
railway variables set NEWS_API_KEY="your-news-api-key-here"
railway variables set BRANDFETCH_API_KEY="your-brandfetch-api-key-here"
railway variables set OPENCORPORATES_API_KEY="your-opencorporates-api-key-here"

# Application
railway variables set FLASK_ENV="production"
railway variables set DEBUG="false"
railway variables set LOG_LEVEL="INFO"

# CORS (Update with your actual domain)
railway variables set ALLOWED_ORIGINS="https://your-frontend-domain.com"
```

### Optional Variables (with defaults)
```bash
railway variables set UPLOAD_FOLDER="uploads"
railway variables set MAX_FILE_SIZE="16777216"
railway variables set RATE_LIMIT_STORAGE_URL="memory://"
railway variables set DEFAULT_RATE_LIMIT="200 per day, 50 per hour"
```

## Database Setup

### Option 1: Railway PostgreSQL (Recommended)
```bash
# Add PostgreSQL service
railway add postgresql

# The DATABASE_URL will be automatically set
```

### Option 2: External Database
```bash
railway variables set DATABASE_URL="postgresql://user:password@host:port/database"
```

## Deployment Steps

1. **Initialize Railway project:**
   ```bash
   railway login
   railway init
   ```

2. **Set environment variables:**
   ```bash
   # Use the commands above or set via dashboard
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Monitor deployment:**
   ```bash
   railway logs
   ```

## Health Check Configuration

Railway will automatically use the health check endpoint defined in `railway.json`:
- Path: `/api/health`
- Timeout: 300 seconds
- Restart policy: ON_FAILURE

## Scaling Configuration

For production workloads, consider:
- Upgrading to Railway Pro for better resources
- Using multiple replicas for high availability
- Setting up monitoring and alerting

## Troubleshooting

### Common Issues:

1. **Build failures:**
   - Check that all required files are committed
   - Verify Dockerfile syntax
   - Check build logs: `railway logs --build`

2. **Runtime errors:**
   - Verify all environment variables are set
   - Check application logs: `railway logs`
   - Test health endpoint: `curl https://your-app.railway.app/api/health`

3. **Database connection issues:**
   - Verify DATABASE_URL is set correctly
   - Check database service status
   - Ensure database migrations are run

### Useful Commands:
```bash
# View all variables
railway variables

# View logs
railway logs --tail

# Connect to shell
railway shell

# View service status
railway status
```

## Security Considerations

1. **Never commit sensitive data:**
   - Use Railway's environment variables
   - Keep API keys secure
   - Rotate keys regularly

2. **HTTPS enforcement:**
   - Railway provides HTTPS by default
   - Update CORS origins to use HTTPS

3. **Database security:**
   - Use strong passwords
   - Enable connection encryption
   - Regular backups

## Performance Optimization

1. **Resource allocation:**
   - Monitor CPU and memory usage
   - Scale vertically if needed

2. **Database optimization:**
   - Use connection pooling
   - Monitor query performance
   - Regular maintenance

3. **Caching:**
   - Consider Redis for caching
   - Implement application-level caching

For more information, visit: https://docs.railway.app
"""


if __name__ == "__main__":
    main()
