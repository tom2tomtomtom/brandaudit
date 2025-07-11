"""
Comprehensive Health Check Service
Provides detailed health monitoring, readiness checks, and system status reporting
"""

import os
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from flask import current_app
from sqlalchemy import text
from src.extensions import db


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class HealthService:
    """Comprehensive health monitoring service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.utcnow()
        self.check_history: List[HealthCheck] = []
        self.max_history = 100
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status including all subsystems"""
        start_time = time.time()
        
        # Run all health checks
        checks = [
            self._check_application_health(),
            self._check_database_health(),
            self._check_api_keys_health(),
            self._check_system_resources(),
            self._check_disk_space(),
            self._check_external_dependencies(),
        ]
        
        # Determine overall status
        overall_status = self._determine_overall_status(checks)
        
        # Calculate total check duration
        total_duration = (time.time() - start_time) * 1000
        
        # Build comprehensive response
        health_report = {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "environment": os.environ.get("FLASK_ENV", "production"),
            "total_check_duration_ms": round(total_duration, 2),
            "checks": {check.name: self._format_check_result(check) for check in checks},
            "system_info": self._get_system_info(),
        }
        
        # Store in history
        self._store_health_check(overall_status, total_duration)
        
        return health_report
    
    def get_readiness_check(self) -> Dict[str, Any]:
        """Get readiness check for Kubernetes/container orchestration"""
        checks = [
            self._check_application_health(),
            self._check_database_health(),
            self._check_api_keys_health(),
        ]
        
        overall_status = self._determine_overall_status(checks)
        is_ready = overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        
        return {
            "ready": is_ready,
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {check.name: check.status.value for check in checks}
        }
    
    def get_liveness_check(self) -> Dict[str, Any]:
        """Get liveness check for basic application health"""
        check = self._check_application_health()
        is_alive = check.status != HealthStatus.UNHEALTHY
        
        return {
            "alive": is_alive,
            "status": check.status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    def _check_application_health(self) -> HealthCheck:
        """Check basic application health"""
        start_time = time.time()
        
        try:
            # Basic application checks
            if not current_app:
                return HealthCheck(
                    name="application",
                    status=HealthStatus.UNHEALTHY,
                    message="Flask application not available",
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.utcnow()
                )
            
            return HealthCheck(
                name="application",
                status=HealthStatus.HEALTHY,
                message="Application is running normally",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={
                    "flask_env": os.environ.get("FLASK_ENV", "production"),
                    "debug_mode": current_app.debug,
                    "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="application",
                status=HealthStatus.UNHEALTHY,
                message=f"Application health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )
    
    def _check_database_health(self) -> HealthCheck:
        """Check database connectivity and performance with enhanced monitoring"""
        start_time = time.time()

        try:
            # Import database pool service
            from src.services.database_pool_service import db_pool_service

            # Test database connection
            connection_test = db_pool_service.test_connection()

            if connection_test["status"] != "success":
                return HealthCheck(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Database connection failed: {connection_test.get('error', 'Unknown error')}",
                    duration_ms=connection_test.get("duration_ms", 0),
                    timestamp=datetime.utcnow()
                )

            # Get comprehensive pool metrics
            pool_status = db_pool_service.get_pool_status()
            duration = connection_test["duration_ms"]

            # Determine status based on pool health and performance
            if pool_status["health_status"] == "critical":
                status = HealthStatus.UNHEALTHY
                message = f"Database pool critical (utilization: {pool_status['pool_utilization_percent']}%)"
            elif pool_status["health_status"] == "warning" or duration > 1000:
                status = HealthStatus.DEGRADED
                message = f"Database performance degraded ({duration:.0f}ms, utilization: {pool_status['pool_utilization_percent']}%)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database healthy ({duration:.0f}ms, utilization: {pool_status['pool_utilization_percent']}%)"

            return HealthCheck(
                name="database",
                status=status,
                message=message,
                duration_ms=duration,
                timestamp=datetime.utcnow(),
                details={
                    "connection_pool": pool_status["metrics"],
                    "pool_health": pool_status["health_status"],
                    "pool_utilization_percent": pool_status["pool_utilization_percent"],
                    "recommendations": pool_status["recommendations"],
                    "database_url": str(db.engine.url).split('@')[-1] if db.engine else "not_configured"
                }
            )

        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )
    
    def _check_api_keys_health(self) -> HealthCheck:
        """Check API key configuration"""
        start_time = time.time()
        
        try:
            required_keys = {
                "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
                "NEWS_API_KEY": os.environ.get("NEWS_API_KEY"),
                "BRANDFETCH_API_KEY": os.environ.get("BRANDFETCH_API_KEY"),
            }
            
            optional_keys = {
                "OPENCORPORATES_API_KEY": os.environ.get("OPENCORPORATES_API_KEY"),
            }
            
            missing_required = [key for key, value in required_keys.items() if not value]
            missing_optional = [key for key, value in optional_keys.items() if not value]
            
            if missing_required:
                status = HealthStatus.UNHEALTHY
                message = f"Missing required API keys: {', '.join(missing_required)}"
            elif missing_optional:
                status = HealthStatus.DEGRADED
                message = f"Missing optional API keys: {', '.join(missing_optional)}"
            else:
                status = HealthStatus.HEALTHY
                message = "All API keys configured"
            
            return HealthCheck(
                name="api_keys",
                status=status,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={
                    "required_keys_configured": len(required_keys) - len(missing_required),
                    "optional_keys_configured": len(optional_keys) - len(missing_optional),
                    "total_keys_configured": len(required_keys) + len(optional_keys) - len(missing_required) - len(missing_optional)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="api_keys",
                status=HealthStatus.UNHEALTHY,
                message=f"API key check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )
    
    def _check_system_resources(self) -> HealthCheck:
        """Check system resource usage"""
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Determine status based on resource usage
            if cpu_percent > 90 or memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"High resource usage (CPU: {cpu_percent}%, Memory: {memory.percent}%)"
            elif cpu_percent > 70 or memory.percent > 70:
                status = HealthStatus.DEGRADED
                message = f"Moderate resource usage (CPU: {cpu_percent}%, Memory: {memory.percent}%)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Resource usage normal (CPU: {cpu_percent}%, Memory: {memory.percent}%)"
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "memory_total_gb": round(memory.total / (1024**3), 2)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.DEGRADED,
                message=f"Resource check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )
    
    def _check_disk_space(self) -> HealthCheck:
        """Check available disk space"""
        start_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage('/')
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            if percent_used > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk space: {percent_used:.1f}% used"
            elif percent_used > 85:
                status = HealthStatus.DEGRADED
                message = f"Low disk space: {percent_used:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space adequate: {percent_used:.1f}% used"
            
            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={
                    "percent_used": round(percent_used, 1),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "total_gb": round(disk_usage.total / (1024**3), 2)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.DEGRADED,
                message=f"Disk space check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )

    def _check_external_dependencies(self) -> HealthCheck:
        """Check external service dependencies"""
        start_time = time.time()

        try:
            import requests

            # Test external services with timeout
            services = {
                "openrouter": "https://openrouter.ai/api/v1/models",
                "news_api": "https://newsapi.org/v2/everything?q=test&pageSize=1",
                "brandfetch": "https://api.brandfetch.io/v2/brands/apple.com"
            }

            service_status = {}

            for service_name, url in services.items():
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code < 500:
                        service_status[service_name] = "available"
                    else:
                        service_status[service_name] = "degraded"
                except requests.RequestException:
                    service_status[service_name] = "unavailable"

            if all(status == "available" for status in service_status.values()):
                status = HealthStatus.HEALTHY
                message = "All external services available"
            elif any(status == "available" for status in service_status.values()):
                status = HealthStatus.DEGRADED
                message = "Some external services unavailable"
            else:
                status = HealthStatus.UNHEALTHY
                message = "External services unavailable"

            return HealthCheck(
                name="external_dependencies",
                status=status,
                message=message,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={"services": service_status}
            )

        except Exception as e:
            return HealthCheck(
                name="external_dependencies",
                status=HealthStatus.DEGRADED,
                message=f"External dependency check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow()
            )

    def _determine_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall health status from individual checks"""
        if any(check.status == HealthStatus.UNHEALTHY for check in checks):
            return HealthStatus.UNHEALTHY
        elif any(check.status == HealthStatus.DEGRADED for check in checks):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def _format_check_result(self, check: HealthCheck) -> Dict[str, Any]:
        """Format health check result for API response"""
        result = {
            "status": check.status.value,
            "message": check.message,
            "duration_ms": round(check.duration_ms, 2),
            "timestamp": check.timestamp.isoformat()
        }

        if check.details:
            result["details"] = check.details

        return result

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                "platform": os.name,
                "python_version": os.sys.version.split()[0],
                "process_id": os.getpid(),
                "working_directory": os.getcwd(),
                "environment_variables_count": len(os.environ),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
        except Exception:
            return {"error": "Unable to retrieve system information"}

    def _store_health_check(self, status: HealthStatus, duration: float):
        """Store health check in history"""
        check = HealthCheck(
            name="overall",
            status=status,
            message=f"Overall health check completed",
            duration_ms=duration,
            timestamp=datetime.utcnow()
        )

        self.check_history.append(check)

        # Maintain history size
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history:]

    def get_health_history(self) -> List[Dict[str, Any]]:
        """Get health check history"""
        return [self._format_check_result(check) for check in self.check_history]

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics and statistics"""
        if not self.check_history:
            return {"error": "No health check history available"}

        recent_checks = self.check_history[-10:]  # Last 10 checks

        status_counts = {}
        total_duration = 0

        for check in recent_checks:
            status_counts[check.status.value] = status_counts.get(check.status.value, 0) + 1
            total_duration += check.duration_ms

        return {
            "total_checks": len(self.check_history),
            "recent_checks": len(recent_checks),
            "average_duration_ms": round(total_duration / len(recent_checks), 2) if recent_checks else 0,
            "status_distribution": status_counts,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "last_check": self.check_history[-1].timestamp.isoformat() if self.check_history else None
        }


# Global health service instance
health_service = HealthService()
