"""
Comprehensive logging and debugging infrastructure for brand audit application
"""
import logging
import logging.handlers
import json
import time
import traceback
import functools
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'analysis_id'):
            log_entry['analysis_id'] = record.analysis_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'brand_name'):
            log_entry['brand_name'] = record.brand_name
        if hasattr(record, 'service_name'):
            log_entry['service_name'] = record.service_name
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'api_endpoint'):
            log_entry['api_endpoint'] = record.api_endpoint
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry)


class IntegrationTestLogger:
    """Logger specifically for integration testing"""
    
    def __init__(self, name: str = 'integration_test'):
        self.logger = logging.getLogger(name)
        self.test_session_id = None
        self.test_results = []
        
    def start_test_session(self, session_id: str):
        """Start a new test session"""
        self.test_session_id = session_id
        self.test_results = []
        self.logger.info(
            "Test session started",
            extra={'test_session_id': session_id, 'event_type': 'test_session_start'}
        )
    
    def log_test_start(self, test_name: str, test_type: str = 'integration'):
        """Log test start"""
        self.logger.info(
            f"Test started: {test_name}",
            extra={
                'test_session_id': self.test_session_id,
                'test_name': test_name,
                'test_type': test_type,
                'event_type': 'test_start'
            }
        )
    
    def log_test_result(self, test_name: str, success: bool, duration: float, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        self.test_results.append(result)
        
        self.logger.info(
            f"Test {'passed' if success else 'failed'}: {test_name}",
            extra={
                'test_session_id': self.test_session_id,
                'test_name': test_name,
                'test_success': success,
                'test_duration': duration,
                'event_type': 'test_result',
                **result
            }
        )
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, duration: float, 
                     request_data: Dict = None, response_data: Dict = None):
        """Log API call details"""
        self.logger.info(
            f"API call: {method} {endpoint} -> {status_code}",
            extra={
                'test_session_id': self.test_session_id,
                'api_endpoint': endpoint,
                'http_method': method,
                'status_code': status_code,
                'duration': duration,
                'request_size': len(json.dumps(request_data)) if request_data else 0,
                'response_size': len(json.dumps(response_data)) if response_data else 0,
                'event_type': 'api_call'
            }
        )
    
    def log_websocket_event(self, event_type: str, data: Dict = None):
        """Log WebSocket events"""
        self.logger.info(
            f"WebSocket event: {event_type}",
            extra={
                'test_session_id': self.test_session_id,
                'websocket_event': event_type,
                'event_data': data,
                'event_type': 'websocket'
            }
        )
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test session summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result['duration'] for result in self.test_results)
        
        return {
            'test_session_id': self.test_session_id,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_duration': total_duration,
            'average_duration': total_duration / total_tests if total_tests > 0 else 0,
            'test_results': self.test_results
        }


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def time_function(self, func_name: str = None):
        """Decorator to time function execution"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                function_name = func_name or f"{func.__module__}.{func.__name__}"
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    self.logger.info(
                        f"Function completed: {function_name}",
                        extra={
                            'function_name': function_name,
                            'duration': duration,
                            'success': True,
                            'event_type': 'performance'
                        }
                    )
                    
                    # Store metrics
                    if function_name not in self.metrics:
                        self.metrics[function_name] = []
                    self.metrics[function_name].append(duration)
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    self.logger.error(
                        f"Function failed: {function_name}",
                        extra={
                            'function_name': function_name,
                            'duration': duration,
                            'success': False,
                            'error_type': type(e).__name__,
                            'error_message': str(e),
                            'event_type': 'performance'
                        },
                        exc_info=True
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        summary = {}
        
        for func_name, durations in self.metrics.items():
            summary[func_name] = {
                'call_count': len(durations),
                'total_duration': sum(durations),
                'average_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations)
            }
        
        return summary


def setup_logging(log_level: str = 'INFO', log_dir: str = 'logs') -> Dict[str, logging.Logger]:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    structured_formatter = StructuredFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / 'application.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(structured_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    
    # Separate handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / 'errors.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setFormatter(structured_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Integration test handler
    test_handler = logging.handlers.RotatingFileHandler(
        log_path / 'integration_tests.log',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    test_handler.setFormatter(structured_formatter)
    test_handler.setLevel(logging.DEBUG)
    
    # Create specialized loggers
    loggers = {
        'app': logging.getLogger('brand_audit.app'),
        'api': logging.getLogger('brand_audit.api'),
        'services': logging.getLogger('brand_audit.services'),
        'websocket': logging.getLogger('brand_audit.websocket'),
        'database': logging.getLogger('brand_audit.database'),
        'integration_test': logging.getLogger('brand_audit.integration_test')
    }
    
    # Add test handler to integration test logger
    loggers['integration_test'].addHandler(test_handler)
    
    return loggers


def create_analysis_logger(analysis_id: str, brand_name: str) -> logging.Logger:
    """Create a logger for a specific analysis"""
    logger = logging.getLogger(f'brand_audit.analysis.{analysis_id}')
    
    # Create analysis-specific log file
    log_path = Path('logs') / 'analyses'
    log_path.mkdir(exist_ok=True)
    
    handler = logging.FileHandler(log_path / f'{analysis_id}.log')
    formatter = StructuredFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # Add analysis context to all log records
    class AnalysisFilter(logging.Filter):
        def filter(self, record):
            record.analysis_id = analysis_id
            record.brand_name = brand_name
            return True
    
    logger.addFilter(AnalysisFilter())
    
    return logger


# Debugging utilities
class DebugContext:
    """Context manager for debugging specific operations"""
    
    def __init__(self, operation_name: str, logger: logging.Logger, **context):
        self.operation_name = operation_name
        self.logger = logger
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(
            f"Starting operation: {self.operation_name}",
            extra={**self.context, 'event_type': 'debug_start'}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.debug(
                f"Operation completed: {self.operation_name}",
                extra={
                    **self.context,
                    'duration': duration,
                    'success': True,
                    'event_type': 'debug_end'
                }
            )
        else:
            self.logger.error(
                f"Operation failed: {self.operation_name}",
                extra={
                    **self.context,
                    'duration': duration,
                    'success': False,
                    'error_type': exc_type.__name__,
                    'error_message': str(exc_val),
                    'event_type': 'debug_error'
                },
                exc_info=True
            )


def log_api_request(logger: logging.Logger):
    """Decorator to log API requests and responses"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, g
            
            start_time = time.time()
            
            # Log request
            logger.info(
                f"API request: {request.method} {request.path}",
                extra={
                    'api_endpoint': request.path,
                    'http_method': request.method,
                    'user_agent': request.headers.get('User-Agent'),
                    'remote_addr': request.remote_addr,
                    'event_type': 'api_request'
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful response
                status_code = getattr(result, 'status_code', 200)
                logger.info(
                    f"API response: {request.method} {request.path} -> {status_code}",
                    extra={
                        'api_endpoint': request.path,
                        'http_method': request.method,
                        'status_code': status_code,
                        'duration': duration,
                        'success': True,
                        'event_type': 'api_response'
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error response
                logger.error(
                    f"API error: {request.method} {request.path}",
                    extra={
                        'api_endpoint': request.path,
                        'http_method': request.method,
                        'duration': duration,
                        'success': False,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'event_type': 'api_error'
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator
