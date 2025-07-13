"""
API types and enums for the validation service
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from datetime import datetime


class APIStatus(Enum):
    """API status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerInfo:
    """Circuit breaker state and configuration"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_threshold: int = 5
    recovery_timeout: int = 300  # seconds
    half_open_max_calls: int = 3
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None


@dataclass
class APIHealthInfo:
    """Information about API health status"""
    status: APIStatus
    response_time: float
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    last_checked: datetime = field(default_factory=datetime.utcnow)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    # Enhanced circuit breaker information
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_success: Optional[datetime] = None
    circuit_breaker: CircuitBreakerInfo = field(default_factory=CircuitBreakerInfo)
    response_time_ms: float = 0.0
    last_check: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIValidationResult:
    """Result of API validation with enhanced circuit breaker support"""
    api_name: str
    is_valid: bool
    health_info: APIHealthInfo
    error_details: Optional[str] = None
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    # Enhanced circuit breaker functionality
    circuit_breaker_triggered: bool = False
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    should_retry: bool = True
    retry_after_seconds: Optional[int] = None


@dataclass
class SystemHealthMetrics:
    """System-wide health metrics"""
    overall_status: APIStatus
    api_statuses: Dict[str, APIHealthInfo]
    total_apis: int
    healthy_apis: int
    degraded_apis: int
    unavailable_apis: int
    last_updated: datetime = field(default_factory=datetime.utcnow)
