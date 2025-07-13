"""
Structured logging utility with correlation IDs and performance metrics
"""
import logging
import json
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
import threading

# Thread-local storage for correlation ID
_local = threading.local()


class StructuredLogger:
    """Enhanced logger with structured logging, correlation IDs, and performance metrics"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _get_correlation_id(self) -> str:
        """Get or generate correlation ID for current thread"""
        if not hasattr(_local, 'correlation_id'):
            _local.correlation_id = str(uuid.uuid4())[:8]
        return _local.correlation_id
    
    def _format_structured_message(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> str:
        """Format message with structured data"""
        structured_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'correlation_id': self._get_correlation_id(),
            'logger': self.name,
            'message': message
        }
        
        if extra_data:
            structured_data.update(extra_data)
        
        return json.dumps(structured_data, default=str)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        structured_msg = self._format_structured_message(message, kwargs)
        self.logger.info(structured_msg)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        structured_msg = self._format_structured_message(message, kwargs)
        self.logger.warning(structured_msg)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        structured_msg = self._format_structured_message(message, kwargs)
        self.logger.error(structured_msg)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        structured_msg = self._format_structured_message(message, kwargs)
        self.logger.debug(structured_msg)
    
    def api_request(self, api_name: str, operation: str, success: bool, 
                   response_time_ms: Optional[float] = None, error_message: Optional[str] = None,
                   **extra_data):
        """Log API request with standardized format"""
        log_data = {
            'event_type': 'api_request',
            'api_name': api_name,
            'operation': operation,
            'success': success,
            'response_time_ms': response_time_ms,
            'error_message': error_message
        }
        log_data.update(extra_data)
        
        if success:
            self.info(f"API request successful: {api_name}.{operation}", **log_data)
        else:
            self.error(f"API request failed: {api_name}.{operation}", **log_data)
    
    def performance_metric(self, operation: str, duration_ms: float, success: bool, **extra_data):
        """Log performance metric"""
        log_data = {
            'event_type': 'performance_metric',
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success
        }
        log_data.update(extra_data)
        
        self.info(f"Performance metric: {operation}", **log_data)
    
    def circuit_breaker_event(self, api_name: str, event: str, state: str, **extra_data):
        """Log circuit breaker events"""
        log_data = {
            'event_type': 'circuit_breaker',
            'api_name': api_name,
            'event': event,
            'state': state
        }
        log_data.update(extra_data)
        
        self.info(f"Circuit breaker {event}: {api_name} -> {state}", **log_data)
    
    def health_check(self, component: str, status: str, response_time_ms: float, **extra_data):
        """Log health check results"""
        log_data = {
            'event_type': 'health_check',
            'component': component,
            'status': status,
            'response_time_ms': response_time_ms
        }
        log_data.update(extra_data)
        
        if status == 'healthy':
            self.info(f"Health check passed: {component}", **log_data)
        else:
            self.warning(f"Health check failed: {component}", **log_data)


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current thread"""
    _local.correlation_id = correlation_id


def get_correlation_id() -> str:
    """Get correlation ID for current thread"""
    if not hasattr(_local, 'correlation_id'):
        _local.correlation_id = str(uuid.uuid4())[:8]
    return _local.correlation_id


@contextmanager
def correlation_context(correlation_id: Optional[str] = None):
    """Context manager for correlation ID"""
    old_id = getattr(_local, 'correlation_id', None)
    _local.correlation_id = correlation_id or str(uuid.uuid4())[:8]
    try:
        yield _local.correlation_id
    finally:
        if old_id:
            _local.correlation_id = old_id
        else:
            delattr(_local, 'correlation_id')


def performance_logger(operation_name: Optional[str] = None):
    """Decorator to log performance metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = StructuredLogger(func.__module__)
            
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.performance_metric(
                    operation=op_name,
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_msg
                )
        
        return wrapper
    return decorator


def api_logger(api_name: str, operation: str):
    """Decorator to log API operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = StructuredLogger(func.__module__)
            
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                response_time_ms = (time.time() - start_time) * 1000
                logger.api_request(
                    api_name=api_name,
                    operation=operation,
                    success=success,
                    response_time_ms=response_time_ms,
                    error_message=error_msg
                )
        
        return wrapper
    return decorator


# Global logger instances for common use
api_validation_logger = StructuredLogger('api_validation')
monitoring_logger = StructuredLogger('monitoring')
health_logger = StructuredLogger('health')
circuit_breaker_logger = StructuredLogger('circuit_breaker')
