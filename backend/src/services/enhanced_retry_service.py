"""
Enhanced Retry Service with Circuit Breaker

This service provides sophisticated retry logic with circuit breaker patterns,
intelligent backoff strategies, and failure detection for robust API interactions.
"""

import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging
from functools import wraps

from src.utils.logging_config import get_logger


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0
    timeout: Optional[float] = None
    retryable_exceptions: List[type] = field(default_factory=list)
    non_retryable_exceptions: List[type] = field(default_factory=list)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # successes needed to close from half-open
    timeout: float = 30.0


@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None


class EnhancedRetryService:
    """Enhanced retry service with circuit breaker and intelligent backoff"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.retry_stats: Dict[str, Dict] = {}
        
        # Default configurations
        self.default_retry_config = RetryConfig()
        self.default_circuit_config = CircuitBreakerConfig()
    
    def with_retry_and_circuit_breaker(self,
                                     operation_name: str,
                                     retry_config: Optional[RetryConfig] = None,
                                     circuit_config: Optional[CircuitBreakerConfig] = None):
        """
        Decorator for operations with retry logic and circuit breaker
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_retry(
                    func, operation_name, retry_config, circuit_config, *args, **kwargs
                )
            return wrapper
        return decorator
    
    def execute_with_retry(self,
                          operation_func: Callable,
                          operation_name: str,
                          retry_config: Optional[RetryConfig] = None,
                          circuit_config: Optional[CircuitBreakerConfig] = None,
                          *args, **kwargs) -> Any:
        """Execute operation with retry logic and circuit breaker"""
        
        retry_config = retry_config or self.default_retry_config
        circuit_config = circuit_config or self.default_circuit_config
        
        # Initialize circuit breaker if not exists
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreakerState()
        
        circuit_breaker = self.circuit_breakers[operation_name]
        
        # Check circuit breaker state
        if not self._can_execute(circuit_breaker, circuit_config):
            raise Exception(f"Circuit breaker is OPEN for {operation_name}. Service unavailable.")
        
        # Initialize retry statistics
        if operation_name not in self.retry_stats:
            self.retry_stats[operation_name] = {
                'total_attempts': 0,
                'total_successes': 0,
                'total_failures': 0,
                'avg_attempts_per_success': 0.0
            }
        
        last_exception = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                self.retry_stats[operation_name]['total_attempts'] += 1
                
                # Execute the operation
                start_time = time.time()
                result = self._execute_with_timeout(operation_func, retry_config.timeout, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Success - update circuit breaker and stats
                self._record_success(circuit_breaker, circuit_config, operation_name)
                self.retry_stats[operation_name]['total_successes'] += 1
                
                self.logger.info(f"Operation {operation_name} succeeded on attempt {attempt + 1} "
                               f"in {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                last_exception = e
                self.retry_stats[operation_name]['total_failures'] += 1
                
                # Check if this exception should be retried
                if not self._should_retry(e, retry_config):
                    self.logger.info(f"Non-retryable exception for {operation_name}: {str(e)}")
                    self._record_failure(circuit_breaker, circuit_config, operation_name)
                    raise e
                
                # Record failure
                self._record_failure(circuit_breaker, circuit_config, operation_name)
                
                # Check if we should continue retrying
                if attempt == retry_config.max_attempts - 1:
                    self.logger.error(f"Operation {operation_name} failed after {retry_config.max_attempts} attempts")
                    break
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, retry_config)
                
                self.logger.warning(f"Operation {operation_name} failed on attempt {attempt + 1}: {str(e)}. "
                                  f"Retrying in {delay:.2f}s")
                
                time.sleep(delay)
        
        # All retries exhausted
        raise Exception(f"Operation {operation_name} failed after {retry_config.max_attempts} attempts. "
                       f"Last error: {str(last_exception)}")
    
    def _can_execute(self, circuit_breaker: CircuitBreakerState, config: CircuitBreakerConfig) -> bool:
        """Check if operation can be executed based on circuit breaker state"""
        
        if circuit_breaker.state == CircuitBreakerState.CLOSED:
            return True
        
        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            # Check if enough time has passed to try again
            if (circuit_breaker.next_attempt_time and 
                datetime.utcnow() >= circuit_breaker.next_attempt_time):
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                circuit_breaker.success_count = 0
                return True
            return False
        
        return False
    
    def _record_success(self, circuit_breaker: CircuitBreakerState, config: CircuitBreakerConfig, operation_name: str):
        """Record successful operation"""
        
        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            circuit_breaker.success_count += 1
            
            if circuit_breaker.success_count >= config.success_threshold:
                circuit_breaker.state = CircuitBreakerState.CLOSED
                circuit_breaker.failure_count = 0
                circuit_breaker.success_count = 0
                self.logger.info(f"Circuit breaker CLOSED for {operation_name}")
        
        elif circuit_breaker.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            circuit_breaker.failure_count = 0
    
    def _record_failure(self, circuit_breaker: CircuitBreakerState, config: CircuitBreakerConfig, operation_name: str):
        """Record failed operation"""
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = datetime.utcnow()
        
        if (circuit_breaker.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN] and
            circuit_breaker.failure_count >= config.failure_threshold):
            
            circuit_breaker.state = CircuitBreakerState.OPEN
            circuit_breaker.next_attempt_time = datetime.utcnow() + timedelta(seconds=config.recovery_timeout)
            
            self.logger.warning(f"Circuit breaker OPENED for {operation_name} after {config.failure_threshold} failures")
    
    def _should_retry(self, exception: Exception, config: RetryConfig) -> bool:
        """Determine if an exception should trigger a retry"""
        
        # Check non-retryable exceptions first
        if config.non_retryable_exceptions:
            for exc_type in config.non_retryable_exceptions:
                if isinstance(exception, exc_type):
                    return False
        
        # Check retryable exceptions
        if config.retryable_exceptions:
            for exc_type in config.retryable_exceptions:
                if isinstance(exception, exc_type):
                    return True
            return False  # If retryable list is specified, only retry those
        
        # Default retry logic based on exception type and message
        exception_str = str(exception).lower()
        
        # Don't retry authentication errors
        if any(term in exception_str for term in ['401', '403', 'unauthorized', 'forbidden']):
            return False
        
        # Don't retry client errors (4xx except 429)
        if any(term in exception_str for term in ['400', '404', '422']):
            return False
        
        # Retry server errors, timeouts, and network issues
        if any(term in exception_str for term in ['500', '502', '503', '504', 'timeout', 'connection', 'network']):
            return True
        
        # Retry rate limit errors with delay
        if any(term in exception_str for term in ['429', 'rate limit']):
            return True
        
        return True  # Default to retry
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for next retry attempt"""
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = config.base_delay * self._fibonacci(attempt + 1)
        
        else:
            delay = config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def _execute_with_timeout(self, operation_func: Callable, timeout: Optional[float], *args, **kwargs):
        """Execute operation with optional timeout"""
        if timeout is None:
            return operation_func(*args, **kwargs)
        
        # For synchronous operations, we can't easily implement timeout
        # In a real implementation, you might use threading or process pools
        return operation_func(*args, **kwargs)
    
    def get_circuit_breaker_status(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker status"""
        if operation_name:
            if operation_name in self.circuit_breakers:
                cb = self.circuit_breakers[operation_name]
                return {
                    operation_name: {
                        'state': cb.state.value,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'last_failure_time': cb.last_failure_time.isoformat() if cb.last_failure_time else None,
                        'next_attempt_time': cb.next_attempt_time.isoformat() if cb.next_attempt_time else None
                    }
                }
            return {operation_name: 'not_initialized'}
        
        return {
            name: {
                'state': cb.state.value,
                'failure_count': cb.failure_count,
                'success_count': cb.success_count,
                'last_failure_time': cb.last_failure_time.isoformat() if cb.last_failure_time else None,
                'next_attempt_time': cb.next_attempt_time.isoformat() if cb.next_attempt_time else None
            }
            for name, cb in self.circuit_breakers.items()
        }
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry statistics for monitoring"""
        stats = {}
        for operation_name, data in self.retry_stats.items():
            if data['total_successes'] > 0:
                avg_attempts = data['total_attempts'] / data['total_successes']
            else:
                avg_attempts = 0.0
            
            stats[operation_name] = {
                **data,
                'avg_attempts_per_success': avg_attempts,
                'success_rate': data['total_successes'] / max(data['total_attempts'], 1)
            }
        
        return stats
    
    def reset_circuit_breaker(self, operation_name: str):
        """Manually reset a circuit breaker"""
        if operation_name in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreakerState()
            self.logger.info(f"Circuit breaker manually reset for {operation_name}")


# Global instance
enhanced_retry_service = EnhancedRetryService()
