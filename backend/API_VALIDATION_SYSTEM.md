# API Validation System Documentation

## Overview

This comprehensive API validation system provides robust connectivity testing, rate limiting, retry logic, and monitoring for all external APIs used in the Brand Audit application. **Critically, this system ensures NO FAKE OR FALLBACK DATA is ever returned**, maintaining complete data authenticity.

## Key Features

### 1. Real-Time API Connectivity Testing
- **Lightweight Health Checks**: Each API has specialized health checkers that perform minimal requests to verify connectivity
- **Response Time Monitoring**: Tracks API response times and performance metrics
- **Status Classification**: APIs are classified as Healthy, Degraded, Rate Limited, or Unavailable

### 2. Advanced Rate Limiting
- **Multi-Level Rate Limiting**: Both hourly and daily rate limits are tracked and enforced
- **Automatic Rate Limit Detection**: Detects 429 responses and respects rate limit headers
- **Proactive Rate Limit Management**: Prevents requests when limits are exceeded

### 3. Intelligent Retry Logic
- **Exponential Backoff**: Implements exponential backoff with jitter for failed requests
- **Circuit Breaker Pattern**: Temporarily stops requests to failing APIs to prevent cascading failures
- **Selective Retry**: Different error types (auth, rate limit, timeout) are handled appropriately

### 4. Comprehensive Monitoring
- **Structured Logging**: All API interactions are logged with structured data
- **Performance Metrics**: Tracks success rates, response times, and failure patterns
- **Alert System**: Automatically detects and alerts on performance degradation
- **Historical Data**: Maintains request history and health status over time

### 5. No Fake Data Policy
- **Authentic Data Only**: All mock/fake data methods have been removed
- **Graceful Failures**: Services fail with clear error messages when APIs are unavailable
- **Data Integrity**: Ensures all brand audit data comes from real, verified sources

## API Configurations

### OpenRouter (LLM Service)
- **Base URL**: `https://openrouter.ai/api/v1`
- **Health Check**: `/models` endpoint
- **Rate Limits**: 50 requests/minute, 1000 requests/day
- **Timeout**: 10 seconds

### NewsAPI
- **Base URL**: `https://newsapi.org/v2`
- **Health Check**: `/sources` endpoint
- **Rate Limits**: 100 requests/hour, 1000 requests/day
- **Timeout**: 15 seconds

### BrandFetch
- **Base URL**: `https://api.brandfetch.io/v2`
- **Health Check**: `/search/apple.com` endpoint
- **Rate Limits**: 100 requests/hour, 500 requests/day
- **Timeout**: 20 seconds

## Enhanced Health Endpoints

### `/api/health`
Returns comprehensive system health with real API connectivity status:
```json
{
  "status": "healthy|degraded|critical",
  "service": "AI Brand Audit Tool API",
  "system_health": {
    "overall_status": "healthy",
    "healthy_apis": 3,
    "total_apis": 3,
    "api_health": {
      "openrouter": {
        "status": "healthy",
        "response_time_ms": 245.3,
        "api_key_configured": true
      }
    }
  }
}
```

### `/api/health/detailed`
Provides detailed monitoring data including:
- API configurations and rate limit usage
- Performance metrics and response times
- Alert status and failure patterns
- Historical health data

## Service Integration

### LLM Service (`llm_service.py`)
- **Integration**: Uses `api_validator.execute_with_retry()` for all LLM calls
- **Fallback**: No fake data - fails with clear error messages
- **Validation**: Checks API availability before making requests

### News Service (`news_service.py`)
- **Integration**: Validates NewsAPI connectivity before searches
- **Fallback**: No mock articles - returns empty results with error messages
- **Rate Limiting**: Respects NewsAPI rate limits automatically

### Brand Data Service (`brand_data_service.py`)
- **Integration**: Validates BrandFetch API before asset requests
- **Fallback**: No placeholder images - fails gracefully without fake data
- **Error Handling**: Clear error messages when APIs are unavailable

## Monitoring and Logging

### Log Files
- **API Monitoring**: `logs/api_monitoring.log` - Structured API interaction logs
- **Application Logs**: Standard Flask application logs

### Metrics Tracked
- Total requests and success/failure counts
- Average response times and performance trends
- 24-hour request/failure statistics
- Uptime percentages and downtime tracking
- Rate limit usage and violations

### Alert Conditions
- Response times exceeding 5 seconds
- Failure rates above 50%
- Extended downtime (>10 minutes)
- Rate limit violations

## Usage Examples

### Basic Health Check
```python
from src.services.api_validation_service import api_validator

# Check specific API
health = api_validator.validate_api_connectivity('openrouter')
print(f"Status: {health.status.value}")

# Get system overview
summary = api_validator.get_system_health_summary()
print(f"Overall: {summary['overall_status']}")
```

### Service Integration
```python
from src.services.llm_service import llm_service

try:
    result = llm_service.analyze_brand_sentiment(text, brand)
    if result['success']:
        # Process real analysis data
        analysis = result['analysis']
    else:
        # Handle API unavailability
        print(f"Analysis unavailable: {result['error']}")
except Exception as e:
    # API completely unavailable
    print(f"Service error: {e}")
```

### Monitoring Data
```python
# Get detailed metrics
monitoring_data = api_validator.get_monitoring_data()
for api_name, metrics in monitoring_data.items():
    print(f"{api_name}: {metrics['metrics']['uptime_percentage']:.1f}% uptime")
```

## Testing

Run the validation system test suite:
```bash
cd backend
python test_api_validation.py
```

This will test:
- API health checks for all configured services
- System health summary generation
- Service integration with validation
- Monitoring data collection

## Benefits

1. **Data Authenticity**: Guarantees all data comes from real APIs
2. **Reliability**: Intelligent retry and circuit breaker patterns
3. **Performance**: Optimized rate limiting and caching
4. **Monitoring**: Comprehensive visibility into API health
5. **Maintainability**: Clear error messages and structured logging
6. **Scalability**: Configurable rate limits and timeouts

## Important Notes

- **No Fake Data**: This system completely eliminates fake/mock data responses
- **Graceful Degradation**: Services fail clearly when APIs are unavailable
- **Real-Time Monitoring**: Health status is continuously updated
- **Production Ready**: Designed for production deployment with proper error handling

This validation system ensures your brand audit application maintains the highest standards of data authenticity while providing robust API management and monitoring capabilities.
