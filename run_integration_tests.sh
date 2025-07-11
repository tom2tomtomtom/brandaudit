#!/bin/bash

# Comprehensive Integration Test Runner for Brand Audit Application
# This script runs all integration tests and generates comprehensive reports

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
LOG_DIR="logs"
REPORT_DIR="test-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SESSION_ID="integration_test_${TIMESTAMP}"

# Default values
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_E2E=true
PARALLEL=false
VERBOSE=false
CLEANUP=true
START_SERVICES=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            RUN_E2E=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            RUN_E2E=false
            shift
            ;;
        --e2e-only)
            RUN_BACKEND=false
            RUN_FRONTEND=false
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        --no-services)
            START_SERVICES=false
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --e2e-only        Run only end-to-end tests"
            echo "  --parallel        Run tests in parallel"
            echo "  --verbose         Enable verbose output"
            echo "  --no-cleanup      Don't cleanup after tests"
            echo "  --no-services     Don't start/stop services"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Create directories
create_directories() {
    log_step "Creating test directories..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$REPORT_DIR"
    mkdir -p "$LOG_DIR/test_artifacts/$SESSION_ID"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    log_step "Installing dependencies..."
    
    # Backend dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        log_info "Installing backend dependencies..."
        cd "$BACKEND_DIR"
        pip install -r requirements.txt > /dev/null 2>&1 || {
            log_warning "Failed to install some backend dependencies"
        }
        cd ..
    fi
    
    # Frontend dependencies
    if [ -f "$FRONTEND_DIR/package.json" ]; then
        log_info "Installing frontend dependencies..."
        cd "$FRONTEND_DIR"
        npm install > /dev/null 2>&1 || {
            log_warning "Failed to install some frontend dependencies"
        }
        cd ..
    fi
    
    log_success "Dependencies installed"
}

# Start services
start_services() {
    if [ "$START_SERVICES" = false ]; then
        log_info "Skipping service startup (--no-services flag)"
        return
    fi
    
    log_step "Starting services..."
    
    # Start backend
    log_info "Starting backend server..."
    cd "$BACKEND_DIR"
    python app.py > "../$LOG_DIR/backend_server.log" 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Check if backend is running
    if ! curl -s http://localhost:8081/api/health > /dev/null; then
        log_warning "Backend server may not be running properly"
    else
        log_success "Backend server started (PID: $BACKEND_PID)"
    fi
    
    # Start frontend
    log_info "Starting frontend server..."
    cd "$FRONTEND_DIR"
    npm run dev > "../$LOG_DIR/frontend_server.log" 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    # Check if frontend is running
    if ! curl -s http://localhost:5175 > /dev/null; then
        log_warning "Frontend server may not be running properly"
    else
        log_success "Frontend server started (PID: $FRONTEND_PID)"
    fi
}

# Stop services
stop_services() {
    if [ "$START_SERVICES" = false ]; then
        return
    fi
    
    log_step "Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "Frontend server stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "python app.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
}

# Run backend tests
run_backend_tests() {
    log_step "Running backend integration tests..."
    
    cd "$BACKEND_DIR"
    
    # Run pytest with coverage
    if python -m pytest tests/ -v --tb=short --junitxml="../$REPORT_DIR/backend_results.xml" > "../$LOG_DIR/backend_tests.log" 2>&1; then
        log_success "Backend tests passed"
        BACKEND_SUCCESS=true
    else
        log_error "Backend tests failed"
        BACKEND_SUCCESS=false
        if [ "$VERBOSE" = true ]; then
            cat "../$LOG_DIR/backend_tests.log"
        fi
    fi
    
    cd ..
}

# Run frontend tests
run_frontend_tests() {
    log_step "Running frontend integration tests..."
    
    cd "$FRONTEND_DIR"
    
    # Run Vitest
    if npm run test:integration > "../$LOG_DIR/frontend_tests.log" 2>&1; then
        log_success "Frontend tests passed"
        FRONTEND_SUCCESS=true
    else
        log_error "Frontend tests failed"
        FRONTEND_SUCCESS=false
        if [ "$VERBOSE" = true ]; then
            cat "../$LOG_DIR/frontend_tests.log"
        fi
    fi
    
    cd ..
}

# Run E2E tests
run_e2e_tests() {
    log_step "Running end-to-end tests..."
    
    cd "$FRONTEND_DIR"
    
    # Run Playwright tests
    if npm run test:e2e:integration > "../$LOG_DIR/e2e_tests.log" 2>&1; then
        log_success "End-to-end tests passed"
        E2E_SUCCESS=true
    else
        log_error "End-to-end tests failed"
        E2E_SUCCESS=false
        if [ "$VERBOSE" = true ]; then
            cat "../$LOG_DIR/e2e_tests.log"
        fi
    fi
    
    cd ..
}

# Generate comprehensive report
generate_report() {
    log_step "Generating comprehensive test report..."
    
    # Use Python test runner to generate detailed report
    cd "$BACKEND_DIR"
    if python tests/test_runner.py --format json > "../$LOG_DIR/test_runner.log" 2>&1; then
        log_success "Detailed report generated"
    else
        log_warning "Failed to generate detailed report"
    fi
    cd ..
    
    # Create summary report
    cat > "$REPORT_DIR/test_summary_$TIMESTAMP.md" << EOF
# Integration Test Report

**Session ID:** $SESSION_ID  
**Timestamp:** $(date)  
**Duration:** $((SECONDS))s

## Test Results Summary

| Test Category | Status | Details |
|---------------|--------|---------|
| Backend Tests | $([ "$BACKEND_SUCCESS" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | Backend API and service integration |
| Frontend Tests | $([ "$FRONTEND_SUCCESS" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | React component integration |
| End-to-End Tests | $([ "$E2E_SUCCESS" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | Complete user journey validation |

## Logs and Artifacts

- Backend Tests: \`$LOG_DIR/backend_tests.log\`
- Frontend Tests: \`$LOG_DIR/frontend_tests.log\`
- E2E Tests: \`$LOG_DIR/e2e_tests.log\`
- Server Logs: \`$LOG_DIR/backend_server.log\`, \`$LOG_DIR/frontend_server.log\`
- Test Artifacts: \`$LOG_DIR/test_artifacts/$SESSION_ID/\`

## Next Steps

$(if [ "$BACKEND_SUCCESS" = false ] || [ "$FRONTEND_SUCCESS" = false ] || [ "$E2E_SUCCESS" = false ]; then
    echo "❌ **Action Required:** Some tests failed. Review the logs above and fix the issues."
else
    echo "✅ **All tests passed!** The application is ready for deployment."
fi)

EOF

    log_success "Test summary report created: $REPORT_DIR/test_summary_$TIMESTAMP.md"
}

# Cleanup function
cleanup() {
    if [ "$CLEANUP" = true ]; then
        log_step "Cleaning up..."
        stop_services
        
        # Archive logs
        tar -czf "$REPORT_DIR/test_logs_$TIMESTAMP.tar.gz" "$LOG_DIR" 2>/dev/null || true
        
        log_success "Cleanup completed"
    fi
}

# Main execution
main() {
    echo -e "${CYAN}🧪 Brand Audit Application - Integration Test Suite${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo ""
    
    log_info "Session ID: $SESSION_ID"
    log_info "Timestamp: $(date)"
    echo ""
    
    # Setup
    create_directories
    check_prerequisites
    install_dependencies
    
    if [ "$START_SERVICES" = true ]; then
        start_services
    fi
    
    # Initialize success flags
    BACKEND_SUCCESS=true
    FRONTEND_SUCCESS=true
    E2E_SUCCESS=true
    
    # Run tests
    if [ "$PARALLEL" = true ]; then
        log_info "Running tests in parallel..."
        
        # Run tests in background
        [ "$RUN_BACKEND" = true ] && run_backend_tests &
        [ "$RUN_FRONTEND" = true ] && run_frontend_tests &
        [ "$RUN_E2E" = true ] && run_e2e_tests &
        
        # Wait for all tests to complete
        wait
    else
        log_info "Running tests sequentially..."
        
        [ "$RUN_BACKEND" = true ] && run_backend_tests
        [ "$RUN_FRONTEND" = true ] && run_frontend_tests
        [ "$RUN_E2E" = true ] && run_e2e_tests
    fi
    
    # Generate report
    generate_report
    
    # Final summary
    echo ""
    echo -e "${CYAN}📊 FINAL RESULTS${NC}"
    echo -e "${CYAN}================${NC}"
    
    if [ "$RUN_BACKEND" = true ]; then
        echo -e "Backend Tests:    $([ "$BACKEND_SUCCESS" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
    fi
    
    if [ "$RUN_FRONTEND" = true ]; then
        echo -e "Frontend Tests:   $([ "$FRONTEND_SUCCESS" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
    fi
    
    if [ "$RUN_E2E" = true ]; then
        echo -e "E2E Tests:        $([ "$E2E_SUCCESS" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
    fi
    
    echo ""
    echo -e "📄 Report: $REPORT_DIR/test_summary_$TIMESTAMP.md"
    echo -e "📁 Logs: $LOG_DIR/"
    echo ""
    
    # Determine exit code
    if [ "$BACKEND_SUCCESS" = true ] && [ "$FRONTEND_SUCCESS" = true ] && [ "$E2E_SUCCESS" = true ]; then
        log_success "All integration tests passed! 🎉"
        EXIT_CODE=0
    else
        log_error "Some integration tests failed! 😞"
        EXIT_CODE=1
    fi
    
    # Cleanup
    cleanup
    
    exit $EXIT_CODE
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
