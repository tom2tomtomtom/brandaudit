# Comprehensive Service Validation System

This validation system provides thorough testing of all services in the Flask Brand Audit application to ensure everything is operational before deployment.

## Features

### 🔍 Service Import Testing
- Tests all 23+ service imports and initialization
- Validates service class instantiation
- Identifies missing dependencies or import errors

### 🗄️ Database Connectivity
- Tests SQLAlchemy database connection
- Validates model creation (User, Analysis, Brand, Report)
- Checks database service functionality
- Creates and cleans up test database

### 🌐 API Service Validation
- Tests OpenRouter API connectivity
- Validates News API functionality
- Checks Brandfetch API status
- Uses existing API validation service for comprehensive health checks

### 🎭 Playwright & Visual Analysis
- Tests Playwright browser automation
- Validates visual analysis service capabilities
- Checks browser installation and functionality

### 📊 Presentation Generation
- Tests PDF generation capabilities (reportlab)
- Validates PowerPoint generation (python-pptx)
- Checks HTML report generation
- Verifies presentation service functionality

### ⚡ Async Capabilities
- Tests async analysis service
- Validates concurrent processing capabilities

### 🔧 Environment Configuration
- Checks required API keys (OPENROUTER_API_KEY, NEWS_API_KEY, BRANDFETCH_API_KEY)
- Validates optional environment variables
- Reports missing configuration

## Usage

### Quick Start
```bash
# From project root
cd backend
python run_validation.py
```

### Direct Execution
```bash
# From backend directory
python comprehensive_service_validation.py
```

### Programmatic Usage
```python
from comprehensive_service_validation import ServiceValidator

validator = ServiceValidator()
validator.run_all_validations()
report = validator.generate_report()
validator.print_report()
```

## Output

### Console Report
The validation provides a comprehensive console report showing:
- Overall system status (HEALTHY/DEGRADED/UNHEALTHY)
- Individual service test results with execution times
- Detailed error messages and recommendations
- Summary statistics

### JSON Report
A detailed JSON report is automatically saved with:
- Complete validation results
- Service-specific details and capabilities
- Execution metrics
- Actionable recommendations

### Exit Codes
- `0`: All services healthy
- `1`: Critical failures detected (UNHEALTHY)
- `2`: Warnings present but functional (DEGRADED)
- `130`: User interrupted
- `1`: Validation system error

## Validation Categories

### ✅ PASS
Service is fully operational and ready for production use.

### ⚠️ WARNING
Service is functional but has issues that should be addressed:
- Missing optional API keys
- Degraded API performance
- Non-critical configuration issues

### ❌ FAIL
Service has critical issues that must be resolved:
- Import failures
- Missing required dependencies
- Database connectivity issues
- Missing required API keys
- Playwright installation problems

### ⏭️ SKIP
Service validation was skipped (currently unused).

## Common Issues & Solutions

### Import Failures
```bash
# Install missing dependencies
pip install -r requirements.txt

# For Playwright specifically
playwright install
```

### Database Issues
- Check database file permissions
- Verify SQLAlchemy configuration
- Ensure database directory exists

### API Connectivity
- Verify API keys in environment variables
- Check network connectivity
- Review API rate limits and quotas

### Playwright Issues
```bash
# Install browser dependencies
playwright install

# For system-specific issues
playwright install-deps
```

## Integration with CI/CD

The validation script is designed for CI/CD integration:

```yaml
# Example GitHub Actions step
- name: Validate Services
  run: |
    cd backend
    python comprehensive_service_validation.py
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
    BRANDFETCH_API_KEY: ${{ secrets.BRANDFETCH_API_KEY }}
```

## Customization

### Adding New Service Tests
1. Add service to `services_to_test` list in `validate_service_imports()`
2. Create specific validation method if needed
3. Add to `run_all_validations()` method

### Modifying Test Criteria
Edit the validation methods to adjust:
- Timeout values
- Required vs optional services
- Test data and scenarios

## Best Practices

1. **Run Before Deployment**: Always validate services before production deployment
2. **Monitor Regularly**: Use in health check systems for ongoing monitoring
3. **Address Warnings**: Don't ignore warnings - they indicate potential issues
4. **Keep Updated**: Update validation as new services are added

## Troubleshooting

### Permission Issues
```bash
chmod +x comprehensive_service_validation.py
chmod +x run_validation.py
```

### Path Issues
Ensure you're running from the correct directory (backend/) or use the runner script.

### Environment Variables
Create a `.env` file in the backend directory with required API keys:
```
OPENROUTER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
BRANDFETCH_API_KEY=your_key_here
```

## Support

This validation system ensures your Brand Audit application is production-ready with all services operational and properly configured. It maintains the principle of NO FAKE DATA by validating real API connectivity and authentic service functionality.
