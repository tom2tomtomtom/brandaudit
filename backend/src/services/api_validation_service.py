import os
import time
import logging
import requests
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from .api_types import APIStatus, APIHealthInfo, APIValidationResult, SystemHealthMetrics
from .api_health_checkers import OpenRouterHealthChecker, NewsAPIHealthChecker, BrandFetchHealthChecker
from .api_monitoring_service import api_monitor


@dataclass
class RateLimitInfo:
    """Data class for rate limit tracking"""
    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    max_requests: int = 100
    window_duration: timedelta = field(default_factory=lambda: timedelta(hours=1))
    
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        now = datetime.utcnow()
        if now - self.window_start > self.window_duration:
            # Reset window
            self.requests_made = 0
            self.window_start = now
            return False
        return self.requests_made >= self.max_requests


class APIValidationService:
    """Comprehensive API validation and health monitoring service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # API configurations with enhanced rate limiting
        self.api_configs = {
            'openrouter': {
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'timeout': 10,
                'rate_limit': RateLimitInfo(max_requests=50, window_duration=timedelta(minutes=1)),
                'daily_limit': RateLimitInfo(max_requests=1000, window_duration=timedelta(days=1))
            },
            'newsapi': {
                'api_key': os.getenv('NEWS_API_KEY'),
                'base_url': 'https://newsapi.org/v2',
                'timeout': 15,
                'rate_limit': RateLimitInfo(max_requests=100, window_duration=timedelta(hours=1)),
                'daily_limit': RateLimitInfo(max_requests=1000, window_duration=timedelta(days=1))
            },
            'brandfetch': {
                'api_key': os.getenv('BRANDFETCH_API_KEY'),
                'base_url': 'https://api.brandfetch.io/v2',
                'timeout': 20,
                'rate_limit': RateLimitInfo(max_requests=100, window_duration=timedelta(hours=1)),
                'daily_limit': RateLimitInfo(max_requests=500, window_duration=timedelta(days=1))
            }
        }

        # Initialize health checkers
        self.health_checkers = {
            'openrouter': OpenRouterHealthChecker(self.api_configs['openrouter']['api_key']),
            'newsapi': NewsAPIHealthChecker(self.api_configs['newsapi']['api_key']),
            'brandfetch': BrandFetchHealthChecker(self.api_configs['brandfetch']['api_key'])
        }

        # Health status tracking
        self.health_status: Dict[str, APIHealthInfo] = {}
        self.initialize_health_status()

        # Enhanced retry configuration
        self.max_retries = 3
        self.base_retry_delay = 1.0  # seconds
        self.max_retry_delay = 60.0  # seconds
        self.circuit_breaker_threshold = 5  # consecutive failures before circuit breaker
        self.circuit_breaker_timeout = timedelta(minutes=10)  # how long to wait before retry
    
    def initialize_health_status(self):
        """Initialize health status for all APIs"""
        for api_name in self.api_configs.keys():
            self.health_status[api_name] = APIHealthInfo(
                status=APIStatus.UNKNOWN,
                response_time=0.0,
                last_checked=datetime.utcnow()
            )
    
    def get_api_health(self, api_name: str) -> APIHealthInfo:
        """Get current health status for an API"""
        return self.health_status.get(api_name, APIHealthInfo(
            status=APIStatus.UNKNOWN,
            last_check=datetime.utcnow()
        ))
    
    def get_all_api_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all APIs"""
        result = {}
        for api_name, health_info in self.health_status.items():
            result[api_name] = {
                'status': health_info.status.value,
                'last_check': health_info.last_check.isoformat(),
                'response_time_ms': health_info.response_time_ms,
                'error_message': health_info.error_message,
                'consecutive_failures': health_info.consecutive_failures,
                'last_success': health_info.last_success.isoformat() if health_info.last_success else None,
                'api_key_configured': bool(self.api_configs[api_name]['api_key'])
            }
        return result
    
    def validate_api_connectivity(self, api_name: str, force_check: bool = False) -> APIHealthInfo:
        """Validate connectivity for a specific API"""
        if api_name not in self.api_configs:
            raise ValueError(f"Unknown API: {api_name}")
        
        config = self.api_configs[api_name]
        current_health = self.health_status[api_name]
        
        # Check if we need to perform a new health check
        time_since_check = datetime.utcnow() - current_health.last_check
        if not force_check and time_since_check < timedelta(minutes=5):
            # Return cached status if checked recently
            return current_health
        
        # Check if API key is configured
        if not config['api_key']:
            current_health.status = APIStatus.UNAVAILABLE
            current_health.error_message = "API key not configured"
            current_health.last_check = datetime.utcnow()
            return current_health
        
        # Check rate limits (both hourly and daily)
        if config['rate_limit'].is_rate_limited():
            current_health.status = APIStatus.RATE_LIMITED
            current_health.error_message = "Hourly rate limit exceeded"
            current_health.rate_limit_reset = (
                config['rate_limit'].window_start + config['rate_limit'].window_duration
            )
            current_health.last_check = datetime.utcnow()
            return current_health

        if config['daily_limit'].is_rate_limited():
            current_health.status = APIStatus.RATE_LIMITED
            current_health.error_message = "Daily rate limit exceeded"
            current_health.rate_limit_reset = (
                config['daily_limit'].window_start + config['daily_limit'].window_duration
            )
            current_health.last_check = datetime.utcnow()
            return current_health

        # Check circuit breaker
        if (current_health.consecutive_failures >= self.circuit_breaker_threshold and
            current_health.last_check and
            datetime.utcnow() - current_health.last_check < self.circuit_breaker_timeout):
            current_health.status = APIStatus.UNAVAILABLE
            current_health.error_message = f"Circuit breaker open - too many failures"
            current_health.last_check = datetime.utcnow()
            return current_health

        # Use specialized health checker
        if api_name in self.health_checkers:
            health_result = self.health_checkers[api_name].check_health()
            self.health_status[api_name] = health_result

            # Log health check result
            api_monitor.log_health_check(api_name, health_result)

            # Update rate limit counters on successful check
            if health_result.status in [APIStatus.HEALTHY, APIStatus.DEGRADED]:
                config['rate_limit'].requests_made += 1
                config['daily_limit'].requests_made += 1

            return health_result
        else:
            # Fallback to generic test
            return self._test_api_connectivity(api_name, config, current_health)

    def _test_api_connectivity(self, api_name: str, config: Dict, current_health: APIHealthInfo) -> APIHealthInfo:
        """Test actual API connectivity with lightweight request"""
        start_time = time.time()

        try:
            # Prepare headers based on API type
            headers = self._get_api_headers(api_name, config['api_key'])

            # Make test request
            url = f"{config['base_url']}{config['test_endpoint']}"
            response = requests.get(
                url,
                headers=headers,
                timeout=config['timeout'],
                params=self._get_test_params(api_name)
            )

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Update rate limit tracking
            config['rate_limit'].requests_made += 1

            # Analyze response
            if response.status_code == 200:
                current_health.status = APIStatus.HEALTHY
                current_health.response_time_ms = response_time
                current_health.error_message = None
                current_health.consecutive_failures = 0
                current_health.last_success = datetime.utcnow()

                self.logger.info(f"API {api_name} health check passed - {response_time:.1f}ms")

            elif response.status_code == 429:
                current_health.status = APIStatus.RATE_LIMITED
                current_health.error_message = "Rate limit exceeded"
                current_health.consecutive_failures += 1

                # Try to parse rate limit reset time
                reset_header = response.headers.get('X-RateLimit-Reset') or response.headers.get('Retry-After')
                if reset_header:
                    try:
                        reset_time = datetime.utcnow() + timedelta(seconds=int(reset_header))
                        current_health.rate_limit_reset = reset_time
                    except ValueError:
                        pass

                self.logger.warning(f"API {api_name} rate limited - status {response.status_code}")

            elif response.status_code in [401, 403]:
                current_health.status = APIStatus.UNAVAILABLE
                current_health.error_message = f"Authentication failed - status {response.status_code}"
                current_health.consecutive_failures += 1

                self.logger.error(f"API {api_name} authentication failed - status {response.status_code}")

            else:
                current_health.status = APIStatus.DEGRADED
                current_health.error_message = f"HTTP {response.status_code}: {response.text[:100]}"
                current_health.consecutive_failures += 1

                self.logger.warning(f"API {api_name} degraded - status {response.status_code}")

            current_health.response_time_ms = response_time

        except requests.exceptions.Timeout:
            current_health.status = APIStatus.DEGRADED
            current_health.error_message = f"Request timeout after {config['timeout']}s"
            current_health.consecutive_failures += 1
            current_health.response_time_ms = (time.time() - start_time) * 1000

            self.logger.warning(f"API {api_name} timeout after {config['timeout']}s")

        except requests.exceptions.ConnectionError:
            current_health.status = APIStatus.UNAVAILABLE
            current_health.error_message = "Connection error - API unreachable"
            current_health.consecutive_failures += 1

            self.logger.error(f"API {api_name} connection error")

        except Exception as e:
            current_health.status = APIStatus.UNAVAILABLE
            current_health.error_message = f"Unexpected error: {str(e)[:100]}"
            current_health.consecutive_failures += 1

            self.logger.error(f"API {api_name} unexpected error: {e}")

        current_health.last_check = datetime.utcnow()
        return current_health

    def _get_api_headers(self, api_name: str, api_key: str) -> Dict[str, str]:
        """Get appropriate headers for each API"""
        if api_name == 'openrouter':
            return {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://brand-audit-tool.com',
                'X-Title': 'Brand Audit Tool'
            }
        elif api_name == 'newsapi':
            return {
                'X-API-Key': api_key,
                'User-Agent': 'Brand Audit Tool/1.0'
            }
        elif api_name == 'brandfetch':
            return {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        else:
            return {'Authorization': f'Bearer {api_key}'}

    def _get_test_params(self, api_name: str) -> Dict[str, str]:
        """Get test parameters for lightweight requests"""
        if api_name == 'newsapi':
            return {'pageSize': '1', 'language': 'en'}
        elif api_name == 'brandfetch':
            return {'limit': '1'}
        else:
            return {}

    def validate_all_apis(self, force_check: bool = False) -> Dict[str, APIHealthInfo]:
        """Validate connectivity for all configured APIs"""
        results = {}
        for api_name in self.api_configs.keys():
            try:
                results[api_name] = self.validate_api_connectivity(api_name, force_check)
            except Exception as e:
                self.logger.error(f"Failed to validate {api_name}: {e}")
                results[api_name] = APIHealthInfo(
                    status=APIStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    error_message=f"Validation failed: {str(e)}"
                )
        return results

    def execute_with_retry(self, api_name: str, operation_func, *args, **kwargs):
        """Execute an API operation with enhanced retry logic and validation"""
        # First check if API is available
        health = self.validate_api_connectivity(api_name)

        if health.status == APIStatus.UNAVAILABLE:
            # Check if circuit breaker should be reset
            if (health.consecutive_failures >= self.circuit_breaker_threshold and
                health.last_check and
                datetime.utcnow() - health.last_check >= self.circuit_breaker_timeout):
                self.logger.info(f"Attempting to reset circuit breaker for {api_name}")
                health = self.validate_api_connectivity(api_name, force_check=True)
                if health.status == APIStatus.UNAVAILABLE:
                    raise Exception(f"API {api_name} is unavailable: {health.error_message}")
            else:
                raise Exception(f"API {api_name} is unavailable: {health.error_message}")

        if health.status == APIStatus.RATE_LIMITED:
            if health.rate_limit_reset:
                wait_time = (health.rate_limit_reset - datetime.utcnow()).total_seconds()
                if wait_time > 0:
                    raise Exception(f"API {api_name} rate limited. Reset in {wait_time:.0f} seconds")

        # Execute operation with enhanced retry logic
        last_exception = None
        config = self.api_configs[api_name]

        for attempt in range(self.max_retries):
            try:
                # Check rate limits before each attempt
                if config['rate_limit'].is_rate_limited() or config['daily_limit'].is_rate_limited():
                    raise Exception(f"Rate limit exceeded for {api_name}")

                # Update rate limit tracking before request
                config['rate_limit'].requests_made += 1
                config['daily_limit'].requests_made += 1

                # Execute the operation
                start_time = time.time()
                result = operation_func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000

                # Log successful operation
                self.log_api_usage(api_name, operation_func.__name__, True, response_time)

                # Reset consecutive failures on success
                self.health_status[api_name].consecutive_failures = 0
                self.health_status[api_name].last_success = datetime.utcnow()
                self.health_status[api_name].status = APIStatus.HEALTHY

                return result

            except requests.exceptions.Timeout as e:
                last_exception = e
                error_msg = f"Request timeout after {config['timeout']}s"
                self.health_status[api_name].consecutive_failures += 1
                self.logger.warning(f"API {api_name} timeout on attempt {attempt + 1}: {error_msg}")

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                error_msg = "Connection error - API unreachable"
                self.health_status[api_name].consecutive_failures += 1
                self.logger.warning(f"API {api_name} connection error on attempt {attempt + 1}: {error_msg}")

            except Exception as e:
                error_msg = str(e)

                # Check if it's a rate limit error
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    self.health_status[api_name].status = APIStatus.RATE_LIMITED
                    self.logger.warning(f"API {api_name} rate limited: {error_msg}")
                    self.log_api_usage(api_name, operation_func.__name__, False, None, error_msg)
                    raise e  # Don't retry rate limit errors

                # Check if it's an authentication error
                if "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
                    self.health_status[api_name].status = APIStatus.UNAVAILABLE
                    self.logger.error(f"API {api_name} authentication error: {error_msg}")
                    self.log_api_usage(api_name, operation_func.__name__, False, None, error_msg)
                    raise e  # Don't retry auth errors

                last_exception = e
                self.health_status[api_name].consecutive_failures += 1
                self.logger.warning(f"API {api_name} error on attempt {attempt + 1}: {error_msg}")

            # Calculate exponential backoff with jitter
            if attempt < self.max_retries - 1:
                base_delay = self.base_retry_delay * (2 ** attempt)
                jitter = base_delay * 0.1 * (0.5 - time.time() % 1)  # Add some randomness
                delay = min(base_delay + jitter, self.max_retry_delay)
                self.logger.info(f"Retrying {api_name} in {delay:.1f} seconds...")
                time.sleep(delay)

        # All retries failed - log and update status
        final_error_msg = str(last_exception) if last_exception else "Unknown error"
        self.log_api_usage(api_name, operation_func.__name__, False, None, final_error_msg)
        self.health_status[api_name].status = APIStatus.DEGRADED

        # Check if we should open circuit breaker
        if self.health_status[api_name].consecutive_failures >= self.circuit_breaker_threshold:
            self.health_status[api_name].status = APIStatus.UNAVAILABLE
            self.logger.error(f"Circuit breaker opened for {api_name} after {self.circuit_breaker_threshold} failures")

        raise Exception(f"API {api_name} failed after {self.max_retries} attempts: {last_exception}")

    def is_api_available(self, api_name: str) -> bool:
        """Check if an API is currently available for use"""
        health = self.get_api_health(api_name)
        return health.status in [APIStatus.HEALTHY, APIStatus.DEGRADED]

    def get_available_apis(self) -> List[str]:
        """Get list of currently available APIs"""
        available = []
        for api_name in self.api_configs.keys():
            if self.is_api_available(api_name):
                available.append(api_name)
        return available

    def log_api_usage(self, api_name: str, operation: str, success: bool,
                     response_time_ms: Optional[float] = None, error_message: Optional[str] = None):
        """Log API usage for monitoring purposes"""
        # Use the monitoring service for comprehensive logging
        api_monitor.log_api_request(api_name, operation, success, response_time_ms, error_message)

        # Also log to our own logger for immediate feedback
        status = "SUCCESS" if success else "FAILURE"
        log_msg = f"API_USAGE: {api_name} | {operation} | {status}"

        if response_time_ms:
            log_msg += f" | {response_time_ms:.1f}ms"

        if error_message:
            log_msg += f" | Error: {error_message}"

        if success:
            self.logger.info(log_msg)
        else:
            self.logger.warning(log_msg)

    def get_monitoring_data(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive monitoring data for APIs"""
        if api_name:
            return api_monitor.get_api_metrics(api_name)
        else:
            return api_monitor.get_all_metrics()

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        all_health = self.get_all_api_health()
        monitoring_data = self.get_monitoring_data()

        # Calculate overall system status
        api_statuses = [info['status'] for info in all_health.values()]
        healthy_count = sum(1 for status in api_statuses if status == 'healthy')
        total_apis = len(api_statuses)

        if healthy_count == total_apis:
            overall_status = "healthy"
        elif healthy_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "unavailable"

        return {
            'overall_status': overall_status,
            'healthy_apis': healthy_count,
            'total_apis': total_apis,
            'api_health': all_health,
            'monitoring_summary': {
                api_name: {
                    'total_requests': data['metrics']['total_requests'],
                    'success_rate': (data['metrics']['successful_requests'] / max(data['metrics']['total_requests'], 1)) * 100,
                    'avg_response_time': data['metrics']['avg_response_time_ms'],
                    'active_alerts': data['alerts_active']
                }
                for api_name, data in monitoring_data.items()
            },
            'timestamp': datetime.utcnow().isoformat()
        }


# Global instance
api_validator = APIValidationService()
