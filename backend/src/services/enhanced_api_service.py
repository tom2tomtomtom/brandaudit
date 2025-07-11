"""
Enhanced API Service Wrapper

This service wraps all external API calls with comprehensive error handling,
retry logic, fallback strategies, and monitoring. It integrates with the
error management service to provide robust API interactions.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
import logging

from src.services.error_management_service import (
    error_manager, 
    ErrorContext, 
    ErrorCategory,
    RecoveryStrategy
)
from src.services.api_validation_service import api_validator
from src.utils.logging_config import get_logger


class EnhancedAPIService:
    """Enhanced API service with comprehensive error handling"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.circuit_breakers: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, List] = {}
        
    def with_error_handling(self, 
                           api_name: str, 
                           operation_name: str,
                           fallback_key: Optional[str] = None,
                           max_retries: int = 3,
                           timeout: int = 30):
        """
        Decorator for API operations with comprehensive error handling
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_error_handling(
                    func, api_name, operation_name, fallback_key, 
                    max_retries, timeout, *args, **kwargs
                )
            return wrapper
        return decorator
    
    def _execute_with_error_handling(self,
                                   operation_func: Callable,
                                   api_name: str,
                                   operation_name: str,
                                   fallback_key: Optional[str],
                                   max_retries: int,
                                   timeout: int,
                                   *args, **kwargs) -> Dict[str, Any]:
        """Execute API operation with comprehensive error handling"""
        
        # Generate correlation ID for tracking
        correlation_id = f"{api_name}_{operation_name}_{int(time.time())}"
        
        # Create error context
        context = ErrorContext(
            api_name=api_name,
            operation=operation_name,
            correlation_id=correlation_id,
            user_id=kwargs.get('user_id'),
            analysis_id=kwargs.get('analysis_id'),
            request_data=self._sanitize_request_data(kwargs)
        )
        
        # Check circuit breaker
        if self._is_circuit_open(api_name):
            return self._handle_circuit_breaker_open(api_name, context)
        
        # Record start time for performance metrics
        start_time = time.time()
        
        try:
            # Execute the operation with timeout
            result = self._execute_with_timeout(operation_func, timeout, *args, **kwargs)
            
            # Record success metrics
            self._record_performance_metrics(api_name, operation_name, time.time() - start_time, True)
            self._reset_circuit_breaker(api_name)
            
            return result
            
        except Exception as error:
            # Record failure metrics
            self._record_performance_metrics(api_name, operation_name, time.time() - start_time, False)
            
            # Handle the error through error management service
            error_info = error_manager.handle_error(error, context, operation_name)
            
            # Update circuit breaker
            self._update_circuit_breaker(api_name, error_info)
            
            # Execute recovery strategy
            return self._execute_recovery_strategy(
                error_info, operation_func, fallback_key, *args, **kwargs
            )
    
    def _execute_with_timeout(self, operation_func: Callable, timeout: int, *args, **kwargs):
        """Execute operation with timeout"""
        try:
            # For async operations, we'd use asyncio.wait_for
            # For now, assume synchronous operations
            return operation_func(*args, **kwargs)
        except Exception as e:
            if "timeout" in str(e).lower():
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            raise e
    
    def _execute_recovery_strategy(self,
                                 error_info,
                                 operation_func: Callable,
                                 fallback_key: Optional[str],
                                 *args, **kwargs) -> Dict[str, Any]:
        """Execute the appropriate recovery strategy"""
        
        try:
            if error_info.recovery_strategy == RecoveryStrategy.RETRY:
                if error_info.retry_count < error_info.max_retries:
                    return error_manager._handle_retry_recovery(
                        error_info, operation_func, *args, **kwargs
                    )
                else:
                    # Max retries exceeded, try fallback if available
                    if fallback_key and error_info.fallback_available:
                        return error_manager._handle_fallback_recovery(
                            error_info, fallback_key, *args, **kwargs
                        )
            
            elif error_info.recovery_strategy == RecoveryStrategy.FALLBACK and fallback_key:
                return error_manager._handle_fallback_recovery(
                    error_info, fallback_key, *args, **kwargs
                )
            
            elif error_info.recovery_strategy == RecoveryStrategy.DEGRADE:
                return error_manager._handle_degrade_recovery(error_info, *args, **kwargs)
            
            elif error_info.recovery_strategy == RecoveryStrategy.USER_ACTION:
                return error_manager._handle_user_action_recovery(error_info, *args, **kwargs)
            
            else:
                return error_manager._handle_fail_recovery(error_info, *args, **kwargs)
                
        except Exception as recovery_error:
            # Recovery failed, return structured error response
            return {
                "success": False,
                "error": error_info.user_message,
                "error_id": error_info.error_id,
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "user_actions": error_info.user_actions,
                "technical_details": str(recovery_error) if self.logger.level <= logging.DEBUG else None
            }
    
    def _is_circuit_open(self, api_name: str) -> bool:
        """Check if circuit breaker is open for an API"""
        if api_name not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[api_name]
        if breaker['state'] != 'open':
            return False
        
        # Check if enough time has passed to try again
        if datetime.utcnow() > breaker['next_attempt']:
            breaker['state'] = 'half_open'
            return False
        
        return True
    
    def _handle_circuit_breaker_open(self, api_name: str, context: ErrorContext) -> Dict[str, Any]:
        """Handle circuit breaker open state"""
        breaker = self.circuit_breakers[api_name]
        wait_time = (breaker['next_attempt'] - datetime.utcnow()).total_seconds()
        
        return {
            "success": False,
            "error": f"Service temporarily unavailable. Please try again in {int(wait_time)} seconds.",
            "circuit_breaker_open": True,
            "api_name": api_name,
            "retry_after": int(wait_time)
        }
    
    def _update_circuit_breaker(self, api_name: str, error_info):
        """Update circuit breaker state based on error"""
        if api_name not in self.circuit_breakers:
            self.circuit_breakers[api_name] = {
                'failure_count': 0,
                'state': 'closed',
                'next_attempt': None
            }
        
        breaker = self.circuit_breakers[api_name]
        
        if error_info.severity.value in ['high', 'critical']:
            breaker['failure_count'] += 1
            
            # Open circuit breaker after 5 failures
            if breaker['failure_count'] >= 5:
                breaker['state'] = 'open'
                breaker['next_attempt'] = datetime.utcnow() + timedelta(minutes=5)
                self.logger.warning(f"Circuit breaker opened for {api_name}")
    
    def _reset_circuit_breaker(self, api_name: str):
        """Reset circuit breaker on successful operation"""
        if api_name in self.circuit_breakers:
            self.circuit_breakers[api_name] = {
                'failure_count': 0,
                'state': 'closed',
                'next_attempt': None
            }
    
    def _record_performance_metrics(self, api_name: str, operation: str, duration: float, success: bool):
        """Record performance metrics for monitoring"""
        metric_key = f"{api_name}_{operation}"
        
        if metric_key not in self.performance_metrics:
            self.performance_metrics[metric_key] = []
        
        # Keep only last 100 metrics per operation
        metrics = self.performance_metrics[metric_key]
        if len(metrics) >= 100:
            metrics.pop(0)
        
        metrics.append({
            'timestamp': datetime.utcnow(),
            'duration': duration,
            'success': success
        })
    
    def _sanitize_request_data(self, data: Dict) -> Dict:
        """Sanitize request data for logging (remove sensitive info)"""
        sensitive_keys = ['password', 'token', 'key', 'secret', 'auth']
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = str(value)[:100]  # Truncate long values
        
        return sanitized
    
    def get_performance_summary(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        if api_name:
            # Filter metrics for specific API
            relevant_metrics = {k: v for k, v in self.performance_metrics.items() if k.startswith(api_name)}
        else:
            relevant_metrics = self.performance_metrics
        
        summary = {}
        for metric_key, metrics in relevant_metrics.items():
            if not metrics:
                continue
            
            recent_metrics = [m for m in metrics if m['timestamp'] > datetime.utcnow() - timedelta(hours=1)]
            
            if recent_metrics:
                durations = [m['duration'] for m in recent_metrics]
                success_rate = sum(1 for m in recent_metrics if m['success']) / len(recent_metrics)
                
                summary[metric_key] = {
                    'avg_duration': sum(durations) / len(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'success_rate': success_rate,
                    'total_requests': len(recent_metrics)
                }
        
        return summary
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            api_name: {
                'state': breaker['state'],
                'failure_count': breaker['failure_count'],
                'next_attempt': breaker['next_attempt'].isoformat() if breaker['next_attempt'] else None
            }
            for api_name, breaker in self.circuit_breakers.items()
        }


# Global instance
enhanced_api_service = EnhancedAPIService()
