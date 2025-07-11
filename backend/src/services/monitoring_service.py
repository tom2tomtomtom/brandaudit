"""
Comprehensive Monitoring Service

This service provides structured logging, performance metrics collection,
health monitoring, and alerting capabilities for the brand audit application.
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
import logging
import uuid
from contextlib import contextmanager

from src.utils.logging_config import get_logger


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance metric tracking"""
    operation: str
    duration: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check result"""
    service: str
    status: str
    response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class Alert:
    """Alert information"""
    id: str
    level: AlertLevel
    title: str
    message: str
    service: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MonitoringService:
    """Comprehensive monitoring service"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics: deque = deque(maxlen=5000)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        
        # Monitoring configuration
        self.metric_retention_hours = 24
        self.performance_thresholds = {
            'response_time_warning': 5.0,  # seconds
            'response_time_critical': 10.0,
            'error_rate_warning': 0.1,  # 10%
            'error_rate_critical': 0.25  # 25%
        }
        
        # Start background cleanup thread
        self._start_cleanup_thread()
    
    @contextmanager
    def track_performance(self, operation: str, correlation_id: Optional[str] = None, **kwargs):
        """Context manager for tracking operation performance"""
        start_time = time.time()
        success = True
        error = None
        
        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            metric = PerformanceMetric(
                operation=operation,
                duration=duration,
                success=success,
                correlation_id=correlation_id,
                additional_data={**kwargs, 'error': error} if error else kwargs
            )
            
            self.record_performance_metric(metric)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, **tags):
        """Record a metric"""
        metric = MetricData(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags
        )
        
        self.metrics[name].append(metric)
        
        # Check for alert conditions
        self._check_metric_alerts(metric)
    
    def record_performance_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        self.performance_metrics.append(metric)
        
        # Record as regular metrics too
        self.record_metric(
            f"operation_duration_{metric.operation}",
            metric.duration,
            MetricType.TIMER,
            success=str(metric.success)
        )
        
        # Check performance thresholds
        self._check_performance_alerts(metric)
    
    def record_health_check(self, service: str, status: str, response_time: float, **details):
        """Record a health check result"""
        health_check = HealthCheck(
            service=service,
            status=status,
            response_time=response_time,
            details=details
        )
        
        self.health_checks[service] = health_check
        
        # Record as metrics
        self.record_metric(
            f"health_check_response_time_{service}",
            response_time,
            MetricType.GAUGE,
            status=status
        )
        
        # Check for health alerts
        self._check_health_alerts(health_check)
    
    def create_alert(self, level: AlertLevel, title: str, message: str, service: str, **metadata):
        """Create an alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            level=level,
            title=title,
            message=message,
            service=service,
            metadata=metadata
        )
        
        self.alerts[alert.id] = alert
        
        # Log the alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[level]
        
        self.logger.log(log_level, f"ALERT [{level.value.upper()}] {title}: {message}", 
                       extra={'alert_id': alert.id, 'service': service, **metadata})
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {str(e)}")
        
        return alert.id
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.utcnow()
            self.logger.info(f"Alert resolved: {alert_id}")
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler"""
        self.alert_handlers.append(handler)
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        summary = {}
        
        for metric_name, metric_data in self.metrics.items():
            recent_metrics = [m for m in metric_data if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                continue
            
            values = [m.value for m in recent_metrics]
            
            summary[metric_name] = {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1] if values else 0,
                'metric_type': recent_metrics[-1].metric_type.value
            }
        
        return summary
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [m for m in self.performance_metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {'total_operations': 0}
        
        # Group by operation
        operations = defaultdict(list)
        for metric in recent_metrics:
            operations[metric.operation].append(metric)
        
        summary = {
            'total_operations': len(recent_metrics),
            'time_period_hours': hours,
            'operations': {}
        }
        
        for operation, metrics in operations.items():
            durations = [m.duration for m in metrics]
            successes = sum(1 for m in metrics if m.success)
            
            summary['operations'][operation] = {
                'total_requests': len(metrics),
                'success_rate': successes / len(metrics),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'p95_duration': self._percentile(durations, 95),
                'p99_duration': self._percentile(durations, 99)
            }
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.health_checks:
            return {'status': 'unknown', 'services': {}}
        
        services = {}
        overall_healthy = True
        
        for service, health_check in self.health_checks.items():
            is_healthy = health_check.status == 'healthy'
            is_recent = (datetime.utcnow() - health_check.timestamp).total_seconds() < 300  # 5 minutes
            
            services[service] = {
                'status': health_check.status,
                'response_time': health_check.response_time,
                'last_check': health_check.timestamp.isoformat(),
                'is_recent': is_recent,
                'details': health_check.details
            }
            
            if not is_healthy or not is_recent:
                overall_healthy = False
        
        return {
            'status': 'healthy' if overall_healthy else 'degraded',
            'services': services,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        alerts = [alert for alert in self.alerts.values() if not alert.resolved]
        
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        return [asdict(alert) for alert in sorted(alerts, key=lambda x: x.timestamp, reverse=True)]
    
    def _check_metric_alerts(self, metric: MetricData):
        """Check if metric triggers any alerts"""
        # Example: Check for high error rates
        if 'error_rate' in metric.name and metric.value > self.performance_thresholds['error_rate_warning']:
            level = AlertLevel.CRITICAL if metric.value > self.performance_thresholds['error_rate_critical'] else AlertLevel.WARNING
            
            self.create_alert(
                level=level,
                title=f"High Error Rate: {metric.name}",
                message=f"Error rate is {metric.value:.2%}, threshold: {self.performance_thresholds['error_rate_warning']:.2%}",
                service=metric.tags.get('service', 'unknown'),
                metric_name=metric.name,
                metric_value=metric.value
            )
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check if performance metric triggers alerts"""
        if metric.duration > self.performance_thresholds['response_time_warning']:
            level = AlertLevel.CRITICAL if metric.duration > self.performance_thresholds['response_time_critical'] else AlertLevel.WARNING
            
            self.create_alert(
                level=level,
                title=f"Slow Response Time: {metric.operation}",
                message=f"Operation took {metric.duration:.2f}s, threshold: {self.performance_thresholds['response_time_warning']:.2f}s",
                service=metric.operation,
                duration=metric.duration,
                correlation_id=metric.correlation_id
            )
    
    def _check_health_alerts(self, health_check: HealthCheck):
        """Check if health check triggers alerts"""
        if health_check.status != 'healthy':
            self.create_alert(
                level=AlertLevel.ERROR,
                title=f"Service Health Issue: {health_check.service}",
                message=f"Service {health_check.service} is {health_check.status}",
                service=health_check.service,
                response_time=health_check.response_time,
                error_message=health_check.error_message
            )
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up old data"""
        def cleanup():
            while True:
                try:
                    cutoff_time = datetime.utcnow() - timedelta(hours=self.metric_retention_hours)
                    
                    # Clean up old metrics
                    for metric_name, metric_data in self.metrics.items():
                        while metric_data and metric_data[0].timestamp < cutoff_time:
                            metric_data.popleft()
                    
                    # Clean up old performance metrics
                    while (self.performance_metrics and 
                           self.performance_metrics[0].timestamp < cutoff_time):
                        self.performance_metrics.popleft()
                    
                    # Clean up resolved alerts older than 7 days
                    alert_cutoff = datetime.utcnow() - timedelta(days=7)
                    alerts_to_remove = [
                        alert_id for alert_id, alert in self.alerts.items()
                        if alert.resolved and alert.resolved_at and alert.resolved_at < alert_cutoff
                    ]
                    
                    for alert_id in alerts_to_remove:
                        del self.alerts[alert_id]
                    
                    time.sleep(3600)  # Run cleanup every hour
                    
                except Exception as e:
                    self.logger.error(f"Cleanup thread error: {str(e)}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()


# Global instance
monitoring_service = MonitoringService()
