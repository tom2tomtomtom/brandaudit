import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
from threading import Thread, Event
import threading
import queue
from .api_validation_service import APIStatus, APIHealthInfo
from .structured_logger import StructuredLogger, correlation_context


@dataclass
class APIMetrics:
    """Data class for API metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    last_24h_requests: int = 0
    last_24h_failures: int = 0
    uptime_percentage: float = 100.0
    last_downtime: Optional[datetime] = None
    downtime_duration_minutes: float = 0.0


@dataclass
class RealTimeMetric:
    """Real-time metric data point"""
    timestamp: datetime
    api_name: str
    metric_type: str  # 'request', 'response_time', 'error', 'health_check'
    value: float
    success: bool
    additional_data: Dict[str, Any] = field(default_factory=dict)


class RealTimeMetricsCollector:
    """Collects and manages real-time metrics"""

    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.metrics_lock = threading.Lock()
        self.subscribers: List[queue.Queue] = []
        self.subscribers_lock = threading.Lock()

    def add_metric(self, metric: RealTimeMetric):
        """Add a new metric and notify subscribers"""
        with self.metrics_lock:
            self.metrics.append(metric)

        # Notify all subscribers
        with self.subscribers_lock:
            dead_subscribers = []
            for subscriber_queue in self.subscribers:
                try:
                    subscriber_queue.put_nowait(metric)
                except queue.Full:
                    # Remove full queues (dead subscribers)
                    dead_subscribers.append(subscriber_queue)

            # Clean up dead subscribers
            for dead_sub in dead_subscribers:
                self.subscribers.remove(dead_sub)

    def subscribe(self) -> queue.Queue:
        """Subscribe to real-time metrics updates"""
        subscriber_queue = queue.Queue(maxsize=100)
        with self.subscribers_lock:
            self.subscribers.append(subscriber_queue)
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: queue.Queue):
        """Unsubscribe from real-time metrics updates"""
        with self.subscribers_lock:
            if subscriber_queue in self.subscribers:
                self.subscribers.remove(subscriber_queue)

    def get_recent_metrics(self, api_name: Optional[str] = None,
                          metric_type: Optional[str] = None,
                          since: Optional[datetime] = None) -> List[RealTimeMetric]:
        """Get recent metrics with optional filtering"""
        with self.metrics_lock:
            filtered_metrics = []
            for metric in self.metrics:
                if api_name and metric.api_name != api_name:
                    continue
                if metric_type and metric.metric_type != metric_type:
                    continue
                if since and metric.timestamp < since:
                    continue
                filtered_metrics.append(metric)
            return filtered_metrics

    def get_metrics_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get summary of metrics for the specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = self.get_recent_metrics(since=cutoff_time)

        summary = {
            'window_minutes': window_minutes,
            'total_metrics': len(recent_metrics),
            'by_api': defaultdict(lambda: {'requests': 0, 'errors': 0, 'avg_response_time': 0}),
            'by_type': defaultdict(int)
        }

        response_times = defaultdict(list)

        for metric in recent_metrics:
            summary['by_type'][metric.metric_type] += 1
            api_stats = summary['by_api'][metric.api_name]

            if metric.metric_type == 'request':
                api_stats['requests'] += 1
                if not metric.success:
                    api_stats['errors'] += 1
            elif metric.metric_type == 'response_time':
                response_times[metric.api_name].append(metric.value)

        # Calculate average response times
        for api_name, times in response_times.items():
            if times:
                summary['by_api'][api_name]['avg_response_time'] = sum(times) / len(times)

        return dict(summary)


class APIMonitoringService:
    """Comprehensive API monitoring and logging service"""
    
    def __init__(self, log_file_path: str = "logs/api_monitoring.log"):
        self.log_file_path = log_file_path
        self.setup_logging()
        
        # Metrics tracking
        self.api_metrics: Dict[str, APIMetrics] = defaultdict(APIMetrics)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Health status history
        self.health_history: Dict[str, List[Dict]] = defaultdict(list)
        self.max_history_entries = 1000
        
        # Alert thresholds
        self.alert_thresholds = {
            'response_time_ms': 5000,  # 5 seconds
            'failure_rate_threshold': 0.5,  # 50% failure rate
            'consecutive_failures': 5,
            'downtime_minutes': 10
        }

        # Real-time metrics collector
        self.real_time_collector = RealTimeMetricsCollector()

        # Enhanced alerting
        self.alert_callbacks: List[callable] = []
        self.alert_history: deque = deque(maxlen=1000)
    
    def setup_logging(self):
        """Setup structured logging for API monitoring"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('api_monitoring')
        self.logger.setLevel(logging.INFO)
        self.structured_logger = StructuredLogger('api_monitoring')
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler for structured logs
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_api_request(self, api_name: str, operation: str, success: bool,
                       response_time_ms: Optional[float] = None, error_message: Optional[str] = None):
        """Log an API request with enhanced structured data"""
        timestamp = datetime.utcnow()

        # Create structured log entry
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'api_name': api_name,
            'operation': operation,
            'success': success,
            'response_time_ms': response_time_ms,
            'error_message': error_message
        }

        # Add to request history
        self.request_history[api_name].append(log_entry)

        # Update metrics
        self.update_metrics(api_name, success, response_time_ms)

        # Use structured logging
        self.structured_logger.api_request(
            api_name=api_name,
            operation=operation,
            success=success,
            response_time_ms=response_time_ms,
            error_message=error_message,
            event_type='api_request',
            metrics_updated=True
        )

        # Add to real-time metrics
        self.real_time_collector.add_metric(RealTimeMetric(
            timestamp=timestamp,
            api_name=api_name,
            metric_type='request',
            value=1.0,
            success=success,
            additional_data={
                'operation': operation,
                'response_time_ms': response_time_ms,
                'error_message': error_message
            }
        ))

        # Add response time metric if available
        if response_time_ms is not None:
            self.real_time_collector.add_metric(RealTimeMetric(
                timestamp=timestamp,
                api_name=api_name,
                metric_type='response_time',
                value=response_time_ms,
                success=success,
                additional_data={'operation': operation}
            ))

        # Check for alerts
        self.check_alerts(api_name)
    
    def log_health_check(self, api_name: str, health_info: APIHealthInfo):
        """Log API health check results"""
        timestamp = datetime.utcnow()
        
        # Create structured health entry
        health_entry = {
            'timestamp': timestamp.isoformat(),
            'api_name': api_name,
            'status': health_info.status.value,
            'response_time_ms': health_info.response_time_ms,
            'error_message': health_info.error_message,
            'consecutive_failures': health_info.consecutive_failures,
            'last_success': health_info.last_success.isoformat() if health_info.last_success else None
        }
        
        # Add to health history
        self.health_history[api_name].append(health_entry)
        
        # Trim history if too long
        if len(self.health_history[api_name]) > self.max_history_entries:
            self.health_history[api_name] = self.health_history[api_name][-self.max_history_entries:]
        
        # Log health status change
        log_message = f"HEALTH_CHECK | {json.dumps(health_entry, default=str)}"
        
        if health_info.status == APIStatus.HEALTHY:
            self.logger.info(log_message)
        elif health_info.status in [APIStatus.DEGRADED, APIStatus.RATE_LIMITED]:
            self.logger.warning(log_message)
        else:
            self.logger.error(log_message)
        
        # Track downtime
        self.track_downtime(api_name, health_info.status)
    
    def update_metrics(self, api_name: str, success: bool, response_time_ms: Optional[float]):
        """Update API metrics"""
        metrics = self.api_metrics[api_name]
        
        # Update request counts
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update response times
        if response_time_ms is not None:
            self.response_times[api_name].append(response_time_ms)
            if self.response_times[api_name]:
                metrics.avg_response_time_ms = sum(self.response_times[api_name]) / len(self.response_times[api_name])
        
        # Calculate 24h metrics
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_requests = [
            req for req in self.request_history[api_name] 
            if datetime.fromisoformat(req['timestamp']) > cutoff_time
        ]
        
        metrics.last_24h_requests = len(recent_requests)
        metrics.last_24h_failures = sum(1 for req in recent_requests if not req['success'])
        
        # Calculate uptime percentage
        if metrics.total_requests > 0:
            metrics.uptime_percentage = (metrics.successful_requests / metrics.total_requests) * 100
    
    def track_downtime(self, api_name: str, status: APIStatus):
        """Track API downtime periods"""
        metrics = self.api_metrics[api_name]
        now = datetime.utcnow()
        
        if status == APIStatus.UNAVAILABLE:
            if metrics.last_downtime is None:
                metrics.last_downtime = now
                self.logger.error(f"DOWNTIME_START | API {api_name} went down at {now.isoformat()}")
        else:
            if metrics.last_downtime is not None:
                downtime_duration = (now - metrics.last_downtime).total_seconds() / 60
                metrics.downtime_duration_minutes += downtime_duration
                
                self.logger.info(f"DOWNTIME_END | API {api_name} recovered after {downtime_duration:.1f} minutes")
                metrics.last_downtime = None
    
    def check_alerts(self, api_name: str):
        """Check if any alert thresholds are exceeded"""
        metrics = self.api_metrics[api_name]
        
        # Check response time alert
        if (self.response_times[api_name] and
            metrics.avg_response_time_ms > self.alert_thresholds['response_time_ms']):
            self._trigger_alert(
                alert_type='high_response_time',
                api_name=api_name,
                message=f"High response time: {metrics.avg_response_time_ms:.1f}ms",
                severity='warning'
            )

        # Check failure rate alert
        if metrics.total_requests >= 10:  # Only check after sufficient requests
            failure_rate = metrics.failed_requests / metrics.total_requests
            if failure_rate > self.alert_thresholds['failure_rate_threshold']:
                self._trigger_alert(
                    alert_type='high_failure_rate',
                    api_name=api_name,
                    message=f"High failure rate: {failure_rate:.1%}",
                    severity='error'
                )

        # Check downtime alert
        if (metrics.last_downtime and
            (datetime.utcnow() - metrics.last_downtime).total_seconds() / 60 > self.alert_thresholds['downtime_minutes']):
            downtime_minutes = (datetime.utcnow() - metrics.last_downtime).total_seconds() / 60
            self._trigger_alert(
                alert_type='extended_downtime',
                api_name=api_name,
                message=f"Extended downtime: {downtime_minutes:.1f} minutes",
                severity='error'
            )
    
    def get_api_metrics(self, api_name: str) -> Dict[str, Any]:
        """Get comprehensive metrics for an API"""
        metrics = self.api_metrics[api_name]
        
        return {
            'api_name': api_name,
            'metrics': asdict(metrics),
            'recent_response_times': list(self.response_times[api_name])[-10:],  # Last 10 response times
            'health_status_summary': self.get_health_summary(api_name),
            'alerts_active': self.get_active_alerts(api_name)
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all APIs"""
        return {
            api_name: self.get_api_metrics(api_name) 
            for api_name in self.api_metrics.keys()
        }
    
    def get_health_summary(self, api_name: str) -> Dict[str, Any]:
        """Get health status summary for an API"""
        if api_name not in self.health_history:
            return {'status': 'unknown', 'checks_performed': 0}
        
        recent_checks = self.health_history[api_name][-10:]  # Last 10 checks
        if not recent_checks:
            return {'status': 'unknown', 'checks_performed': 0}
        
        latest_status = recent_checks[-1]['status']
        status_counts = defaultdict(int)
        
        for check in recent_checks:
            status_counts[check['status']] += 1
        
        return {
            'current_status': latest_status,
            'checks_performed': len(recent_checks),
            'status_distribution': dict(status_counts),
            'last_check_time': recent_checks[-1]['timestamp']
        }
    
    def get_active_alerts(self, api_name: str) -> List[str]:
        """Get list of active alerts for an API"""
        alerts = []
        metrics = self.api_metrics[api_name]
        
        # Check various alert conditions
        if (self.response_times[api_name] and 
            metrics.avg_response_time_ms > self.alert_thresholds['response_time_ms']):
            alerts.append(f"High response time: {metrics.avg_response_time_ms:.1f}ms")
        
        if metrics.total_requests >= 10:
            failure_rate = metrics.failed_requests / metrics.total_requests
            if failure_rate > self.alert_thresholds['failure_rate_threshold']:
                alerts.append(f"High failure rate: {failure_rate:.1%}")
        
        if (metrics.last_downtime and 
            (datetime.utcnow() - metrics.last_downtime).total_seconds() / 60 > self.alert_thresholds['downtime_minutes']):
            downtime_minutes = (datetime.utcnow() - metrics.last_downtime).total_seconds() / 60
            alerts.append(f"Extended downtime: {downtime_minutes:.1f} minutes")
        
        return alerts

    def subscribe_to_real_time_metrics(self) -> queue.Queue:
        """Subscribe to real-time metrics updates"""
        return self.real_time_collector.subscribe()

    def unsubscribe_from_real_time_metrics(self, subscriber_queue: queue.Queue):
        """Unsubscribe from real-time metrics updates"""
        self.real_time_collector.unsubscribe(subscriber_queue)

    def get_real_time_metrics_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get real-time metrics summary"""
        return self.real_time_collector.get_metrics_summary(window_minutes)

    def get_recent_metrics(self, api_name: Optional[str] = None,
                          metric_type: Optional[str] = None,
                          minutes_back: int = 5) -> List[Dict[str, Any]]:
        """Get recent metrics in serializable format"""
        since = datetime.utcnow() - timedelta(minutes=minutes_back)
        metrics = self.real_time_collector.get_recent_metrics(api_name, metric_type, since)

        return [
            {
                'timestamp': metric.timestamp.isoformat(),
                'api_name': metric.api_name,
                'metric_type': metric.metric_type,
                'value': metric.value,
                'success': metric.success,
                'additional_data': metric.additional_data
            }
            for metric in metrics
        ]

    def add_alert_callback(self, callback: callable):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: callable):
        """Remove alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    def _trigger_alert(self, alert_type: str, api_name: str, message: str, severity: str = 'warning'):
        """Trigger an alert and notify callbacks"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'api_name': api_name,
            'message': message,
            'severity': severity
        }

        # Add to alert history
        self.alert_history.append(alert)

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.structured_logger.error(
                    f"Alert callback failed: {e}",
                    alert_type=alert_type,
                    api_name=api_name,
                    callback_error=str(e)
                )

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return list(self.alert_history)[-limit:]

    def get_live_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive live dashboard data"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'real_time_summary': self.get_real_time_metrics_summary(5),
            'api_metrics': self.get_all_metrics(),
            'recent_alerts': self.get_alert_history(10),
            'system_status': self._get_system_status_summary()
        }

    def _get_system_status_summary(self) -> Dict[str, Any]:
        """Get system status summary for dashboard"""
        all_metrics = self.get_all_metrics()

        total_apis = len(all_metrics)
        healthy_apis = 0
        degraded_apis = 0

        for api_name, data in all_metrics.items():
            health_summary = data.get('health_status_summary', {})
            current_status = health_summary.get('current_status', 'unknown')

            if current_status == 'healthy':
                healthy_apis += 1
            elif current_status in ['degraded', 'rate_limited']:
                degraded_apis += 1

        overall_health = 'healthy'
        if healthy_apis == 0:
            overall_health = 'critical'
        elif degraded_apis > 0:
            overall_health = 'degraded'

        return {
            'overall_health': overall_health,
            'total_apis': total_apis,
            'healthy_apis': healthy_apis,
            'degraded_apis': degraded_apis,
            'critical_apis': total_apis - healthy_apis - degraded_apis
        }


# Global instance
api_monitor = APIMonitoringService()
