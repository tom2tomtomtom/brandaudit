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


@dataclass
class APIValidationResult:
    """Result of API validation"""
    api_name: str
    is_valid: bool
    health_info: APIHealthInfo
    error_details: Optional[str] = None
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)


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
