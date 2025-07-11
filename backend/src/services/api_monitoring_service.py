import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from .api_validation_service import APIStatus, APIHealthInfo


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
    
    def setup_logging(self):
        """Setup structured logging for API monitoring"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('api_monitoring')
        self.logger.setLevel(logging.INFO)
        
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
        """Log an API request with structured data"""
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
        
        # Log to file
        log_message = f"API_REQUEST | {json.dumps(log_entry, default=str)}"
        if success:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
        
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
            self.logger.warning(
                f"ALERT | High response time for {api_name}: {metrics.avg_response_time_ms:.1f}ms"
            )
        
        # Check failure rate alert
        if metrics.total_requests >= 10:  # Only check after sufficient requests
            failure_rate = metrics.failed_requests / metrics.total_requests
            if failure_rate > self.alert_thresholds['failure_rate_threshold']:
                self.logger.error(
                    f"ALERT | High failure rate for {api_name}: {failure_rate:.1%}"
                )
        
        # Check downtime alert
        if (metrics.last_downtime and 
            (datetime.utcnow() - metrics.last_downtime).total_seconds() / 60 > self.alert_thresholds['downtime_minutes']):
            self.logger.error(
                f"ALERT | Extended downtime for {api_name}: {(datetime.utcnow() - metrics.last_downtime).total_seconds() / 60:.1f} minutes"
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


# Global instance
api_monitor = APIMonitoringService()
