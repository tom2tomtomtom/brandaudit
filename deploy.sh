#!/bin/bash
# Production Deployment Script for AI Brand Audit Tool
# Supports Docker Compose and Railway deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-"docker"}
ENVIRONMENT=${2:-"production"}
SKIP_TESTS=${3:-"false"}

echo -e "${BLUE}🚀 AI Brand Audit Tool - Production Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Deployment Type: ${YELLOW}$DEPLOYMENT_TYPE${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "Skip Tests: ${YELLOW}$SKIP_TESTS${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}📋 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check environment file
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        if [[ ! -f ".env" ]]; then
            echo -e "${YELLOW}⚠️  .env file not found, creating from template...${NC}"
            if [[ -f ".env.template" ]]; then
                cp .env.template .env
                echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
                exit 1
            else
                echo -e "${RED}❌ No .env template found${NC}"
                exit 1
            fi
        fi
    fi
    
    # Check Railway CLI for Railway deployments
    if [[ "$DEPLOYMENT_TYPE" == "railway" ]]; then
        if ! command -v railway &> /dev/null; then
            echo -e "${RED}❌ Railway CLI is not installed${NC}"
            echo -e "${YELLOW}Install with: npm install -g @railway/cli${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        echo -e "${YELLOW}⏭️  Skipping tests as requested${NC}"
        return
    fi
    
    echo -e "${BLUE}🧪 Running tests...${NC}"
    
    # Run test suite
    docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test
    
    # Check test results
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        exit 1
    fi
    
    # Clean up test containers
    docker-compose -f docker-compose.yml -f docker-compose.test.yml down -v
}

# Function to build and validate images
build_images() {
    echo -e "${BLUE}🏗️  Building Docker images...${NC}"
    
    # Build production images
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    
    # Validate images
    echo -e "${BLUE}🔍 Validating built images...${NC}"
    
    # Test backend image
    docker run --rm --name test-backend \
        -e FLASK_ENV=production \
        -e SECRET_KEY=test-key \
        -e JWT_SECRET_KEY=test-jwt-key \
        brand-audit-app_backend:latest \
        python -c "import app; print('✅ Backend image validation passed')" || {
        echo -e "${RED}❌ Backend image validation failed${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ Image build and validation completed${NC}"
}

# Function to deploy with Docker Compose
deploy_docker() {
    echo -e "${BLUE}🐳 Deploying with Docker Compose...${NC}"
    
    # Stop existing containers gracefully
    echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down --timeout 30
    
    # Start new deployment
    echo -e "${BLUE}🚀 Starting new deployment...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    # Wait for services to be healthy
    echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
    sleep 30
    
    # Check health
    check_deployment_health "http://localhost"
}

# Function to deploy with Railway
deploy_railway() {
    echo -e "${BLUE}🚂 Deploying with Railway...${NC}"
    
    # Login check
    if ! railway whoami &> /dev/null; then
        echo -e "${YELLOW}🔐 Please login to Railway...${NC}"
        railway login
    fi
    
    # Deploy
    if [[ "$ENVIRONMENT" == "production" ]]; then
        railway up --environment production
    else
        railway up --environment staging
    fi
    
    # Get deployment URL
    RAILWAY_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
    
    if [[ -n "$RAILWAY_URL" ]]; then
        echo -e "${GREEN}🌐 Deployment URL: $RAILWAY_URL${NC}"
        check_deployment_health "$RAILWAY_URL"
    else
        echo -e "${YELLOW}⚠️  Could not retrieve deployment URL${NC}"
    fi
}

# Function to check deployment health
check_deployment_health() {
    local BASE_URL=$1
    echo -e "${BLUE}🏥 Checking deployment health...${NC}"
    
    # Wait for application to start
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        echo -e "${BLUE}Attempt $attempt/$max_attempts: Checking health endpoint...${NC}"
        
        if curl -f -s "$BASE_URL/api/health/ready" > /dev/null; then
            echo -e "${GREEN}✅ Application is healthy and ready${NC}"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            echo -e "${RED}❌ Health check failed after $max_attempts attempts${NC}"
            echo -e "${YELLOW}🔍 Checking logs...${NC}"
            
            if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
                docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=50 backend
            fi
            
            exit 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Additional health checks
    echo -e "${BLUE}🔍 Running additional health checks...${NC}"
    
    # Check database connectivity
    if curl -f -s "$BASE_URL/api/database/health-summary" > /dev/null; then
        echo -e "${GREEN}✅ Database connectivity check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Database connectivity check failed${NC}"
    fi
    
    # Check API endpoints
    if curl -f -s "$BASE_URL/api/health/metrics" > /dev/null; then
        echo -e "${GREEN}✅ API endpoints check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  API endpoints check failed${NC}"
    fi
}

# Function to run post-deployment tasks
post_deployment() {
    echo -e "${BLUE}📋 Running post-deployment tasks...${NC}"
    
    # Database migrations (if needed)
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        echo -e "${BLUE}🗄️  Running database migrations...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend \
            python -c "
from src.extensions import db
from app import app
with app.app_context():
    db.create_all()
    print('✅ Database migrations completed')
" || echo -e "${YELLOW}⚠️  Database migrations skipped${NC}"
    fi
    
    # Clear caches
    echo -e "${BLUE}🧹 Clearing application caches...${NC}"
    # Add cache clearing logic here if needed
    
    echo -e "${GREEN}✅ Post-deployment tasks completed${NC}"
}

# Function to show deployment summary
show_summary() {
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${GREEN}=================================${NC}"
    echo -e "Deployment Type: ${YELLOW}$DEPLOYMENT_TYPE${NC}"
    echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
    echo -e "Timestamp: ${YELLOW}$(date)${NC}"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        echo -e "Application URL: ${YELLOW}http://localhost${NC}"
        echo -e "Health Check: ${YELLOW}http://localhost/api/health${NC}"
        echo -e "Database Monitor: ${YELLOW}http://localhost/api/database/status${NC}"
        
        echo -e "\n${BLUE}📊 Container Status:${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
        
        echo -e "\n${BLUE}💡 Useful Commands:${NC}"
        echo -e "View logs: ${YELLOW}docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f${NC}"
        echo -e "Scale backend: ${YELLOW}docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=2${NC}"
        echo -e "Stop deployment: ${YELLOW}docker-compose -f docker-compose.yml -f docker-compose.prod.yml down${NC}"
    fi
    
    echo -e "\n${GREEN}🚀 Your AI Brand Audit Tool is now running in production!${NC}"
}

# Main deployment flow
main() {
    check_prerequisites
    
    if [[ "$SKIP_TESTS" != "true" ]]; then
        run_tests
    fi
    
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        build_images
        deploy_docker
    elif [[ "$DEPLOYMENT_TYPE" == "railway" ]]; then
        deploy_railway
    else
        echo -e "${RED}❌ Unknown deployment type: $DEPLOYMENT_TYPE${NC}"
        echo -e "${YELLOW}Supported types: docker, railway${NC}"
        exit 1
    fi
    
    post_deployment
    show_summary
}

# Handle script arguments
case "$1" in
    "docker"|"railway")
        main
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [deployment_type] [environment] [skip_tests]"
        echo ""
        echo "Arguments:"
        echo "  deployment_type: docker|railway (default: docker)"
        echo "  environment: production|staging (default: production)"
        echo "  skip_tests: true|false (default: false)"
        echo ""
        echo "Examples:"
        echo "  $0 docker production false"
        echo "  $0 railway staging true"
        echo "  $0 docker"
        ;;
    *)
        if [[ -n "$1" ]]; then
            echo -e "${RED}❌ Unknown deployment type: $1${NC}"
            echo -e "${YELLOW}Use '$0 help' for usage information${NC}"
            exit 1
        fi
        main
        ;;
esac
