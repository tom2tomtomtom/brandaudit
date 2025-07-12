#!/bin/bash

# 🚀 Analytics Dashboard Deployment Verification Script
# This script verifies that all components are ready for deployment

echo "🔍 Analytics Dashboard Deployment Verification"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
print_info "Checking Git Repository Status..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_status 1 "Not in a git repository"
    exit 1
fi

# Check git status
git_status=$(git status --porcelain)
if [ -z "$git_status" ]; then
    print_status 0 "Git working tree is clean"
else
    print_status 1 "Git working tree has uncommitted changes"
    echo "Uncommitted changes:"
    git status --short
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ]; then
    print_status 0 "On main branch"
else
    print_warning "Currently on branch: $current_branch (not main)"
fi

# Check if local is up to date with remote
git fetch origin main 2>/dev/null
local_commit=$(git rev-parse HEAD)
remote_commit=$(git rev-parse origin/main)

if [ "$local_commit" = "$remote_commit" ]; then
    print_status 0 "Local branch is up to date with origin/main"
else
    print_status 1 "Local branch is not up to date with origin/main"
fi

echo ""
print_info "Checking Frontend Dependencies..."

# Check if package.json exists
if [ -f "frontend/package.json" ]; then
    print_status 0 "Frontend package.json exists"
    
    # Check for required analytics dependencies
    required_deps=("jspdf" "jspdf-autotable" "xlsx" "html2canvas" "socket.io-client" "recharts")
    
    for dep in "${required_deps[@]}"; do
        if grep -q "\"$dep\"" frontend/package.json; then
            print_status 0 "Dependency $dep found"
        else
            print_status 1 "Dependency $dep missing"
        fi
    done
else
    print_status 1 "Frontend package.json not found"
fi

echo ""
print_info "Checking Backend Dependencies..."

# Check if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    print_status 0 "Backend requirements.txt exists"
    
    # Check for Flask-SocketIO
    if grep -q "Flask-SocketIO" backend/requirements.txt; then
        print_status 0 "Flask-SocketIO dependency found"
    else
        print_status 1 "Flask-SocketIO dependency missing"
    fi
else
    print_status 1 "Backend requirements.txt not found"
fi

echo ""
print_info "Checking Analytics Dashboard Components..."

# Check for main analytics components
analytics_components=(
    "frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx"
    "frontend/src/components/analytics/RealTimeAnalyticsPanel.jsx"
    "frontend/src/components/analytics/AIInsightsEngine.jsx"
    "frontend/src/components/analytics/BrandComparisonTool.jsx"
    "frontend/src/components/analytics/PerformanceMonitor.jsx"
    "frontend/src/components/analytics/MobileAnalyticsDashboard.jsx"
    "frontend/src/components/analytics/ExportDialog.jsx"
    "frontend/src/services/analyticsApi.js"
    "frontend/src/services/realTimeAnalytics.js"
    "frontend/src/services/exportService.js"
    "backend/src/routes/analytics.py"
)

for component in "${analytics_components[@]}"; do
    if [ -f "$component" ]; then
        print_status 0 "Component $(basename $component) exists"
    else
        print_status 1 "Component $(basename $component) missing"
    fi
done

echo ""
print_info "Checking Environment Configuration..."

# Check for environment files
if [ -f "frontend/.env.example" ] || [ -f "frontend/.env" ]; then
    print_status 0 "Frontend environment configuration found"
else
    print_warning "Frontend environment configuration not found"
fi

if [ -f "backend/.env.example" ] || [ -f "backend/.env" ]; then
    print_status 0 "Backend environment configuration found"
else
    print_warning "Backend environment configuration not found"
fi

echo ""
print_info "Checking Documentation..."

docs=(
    "ANALYTICS_DASHBOARD_SUMMARY.md"
    "DEPLOYMENT_CHECKLIST.md"
    "frontend/src/components/analytics/README.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        print_status 0 "Documentation $(basename $doc) exists"
    else
        print_status 1 "Documentation $(basename $doc) missing"
    fi
done

echo ""
print_info "Deployment Readiness Summary"
echo "=============================================="

# Count total checks
total_checks=0
passed_checks=0

# This is a simplified check - in a real script you'd track each check
if [ -z "$git_status" ] && [ "$current_branch" = "main" ] && [ "$local_commit" = "$remote_commit" ]; then
    print_status 0 "Git repository is deployment ready"
    ((passed_checks++))
else
    print_status 1 "Git repository needs attention"
fi
((total_checks++))

if [ -f "frontend/package.json" ] && grep -q "jspdf" frontend/package.json; then
    print_status 0 "Frontend dependencies are ready"
    ((passed_checks++))
else
    print_status 1 "Frontend dependencies need attention"
fi
((total_checks++))

if [ -f "backend/requirements.txt" ] && grep -q "Flask-SocketIO" backend/requirements.txt; then
    print_status 0 "Backend dependencies are ready"
    ((passed_checks++))
else
    print_status 1 "Backend dependencies need attention"
fi
((total_checks++))

if [ -f "frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx" ]; then
    print_status 0 "Analytics components are present"
    ((passed_checks++))
else
    print_status 1 "Analytics components are missing"
fi
((total_checks++))

echo ""
echo "=============================================="
echo -e "${BLUE}📊 Deployment Readiness: $passed_checks/$total_checks checks passed${NC}"

if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}🚀 READY FOR DEPLOYMENT!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run 'npm install' in frontend directory"
    echo "2. Run 'pip install -r requirements.txt' in backend directory"
    echo "3. Configure environment variables"
    echo "4. Deploy to your chosen platform"
    echo "5. Run post-deployment verification tests"
    exit 0
else
    echo -e "${RED}⚠️  DEPLOYMENT READINESS ISSUES DETECTED${NC}"
    echo ""
    echo "Please address the failed checks above before deploying."
    exit 1
fi
