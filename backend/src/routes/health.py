"""
Health Check Routes
Provides comprehensive health monitoring endpoints for production deployments
"""

from flask import Blueprint, jsonify, request
from src.services.health_service import health_service
from src.services.shutdown_service import get_shutdown_service
import logging

# Create health blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint
    Returns detailed health status of all system components
    """
    try:
        health_report = health_service.get_comprehensive_health()
        
        # Determine HTTP status code based on health
        if health_report['status'] == 'healthy':
            status_code = 200
        elif health_report['status'] == 'degraded':
            status_code = 200  # Still operational but with warnings
        else:
            status_code = 503  # Service unavailable
        
        return jsonify(health_report), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": "Health check system failure",
            "message": str(e)
        }), 503


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes readiness probe endpoint
    Returns whether the service is ready to accept traffic
    """
    try:
        readiness_report = health_service.get_readiness_check()
        
        status_code = 200 if readiness_report['ready'] else 503
        
        return jsonify(readiness_report), status_code
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "ready": False,
            "status": "unhealthy",
            "error": str(e)
        }), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes liveness probe endpoint
    Returns whether the service is alive and should not be restarted
    """
    try:
        liveness_report = health_service.get_liveness_check()
        
        status_code = 200 if liveness_report['alive'] else 503
        
        return jsonify(liveness_report), status_code
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return jsonify({
            "alive": False,
            "status": "unhealthy",
            "error": str(e)
        }), 503


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with full system information
    Includes metrics, history, and comprehensive diagnostics
    """
    try:
        # Get comprehensive health report
        health_report = health_service.get_comprehensive_health()
        
        # Add additional details
        health_report['metrics'] = health_service.get_health_metrics()
        health_report['history'] = health_service.get_health_history()[-5:]  # Last 5 checks
        
        # Add shutdown service status
        shutdown_service = get_shutdown_service()
        health_report['shutdown_status'] = shutdown_service.get_shutdown_status()
        
        # Determine status code
        if health_report['status'] == 'healthy':
            status_code = 200
        elif health_report['status'] == 'degraded':
            status_code = 200
        else:
            status_code = 503
        
        return jsonify(health_report), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": "Detailed health check system failure",
            "message": str(e)
        }), 503


@health_bp.route('/health/metrics', methods=['GET'])
def health_metrics():
    """
    Health metrics endpoint for monitoring systems
    Returns performance metrics and statistics
    """
    try:
        metrics = health_service.get_health_metrics()
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Health metrics failed: {e}")
        return jsonify({
            "error": "Health metrics system failure",
            "message": str(e)
        }), 503


@health_bp.route('/health/history', methods=['GET'])
def health_history():
    """
    Health check history endpoint
    Returns historical health check data
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # Cap at 100 entries
        
        history = health_service.get_health_history()
        
        # Return most recent entries up to limit
        recent_history = history[-limit:] if history else []
        
        return jsonify({
            "history": recent_history,
            "total_entries": len(history),
            "returned_entries": len(recent_history)
        }), 200
        
    except Exception as e:
        logger.error(f"Health history failed: {e}")
        return jsonify({
            "error": "Health history system failure",
            "message": str(e)
        }), 503


@health_bp.route('/health/status', methods=['GET'])
def simple_status():
    """
    Simple status endpoint for basic monitoring
    Returns minimal status information
    """
    try:
        liveness = health_service.get_liveness_check()

        return jsonify({
            "status": "ok" if liveness['alive'] else "error",
            "timestamp": liveness['timestamp'],
            "uptime_seconds": liveness['uptime_seconds']
        }), 200 if liveness['alive'] else 503

    except Exception as e:
        logger.error(f"Simple status check failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 503


@health_bp.route('/health/dashboard', methods=['GET'])
def enhanced_dashboard():
    """
    Enhanced dashboard endpoint with comprehensive system monitoring
    Aggregates API health, monitoring metrics, circuit breaker status, and real-time performance data
    """
    try:
        from src.services.api_validation_service import api_validator
        from src.services.api_monitoring_service import api_monitor
        from src.services.monitoring_service import monitoring_service
        from datetime import datetime, timedelta

        # Get comprehensive health report
        health_report = health_service.get_comprehensive_health()

        # Get API validation and monitoring data
        api_health = api_validator.get_system_health_summary()
        api_monitoring_data = api_monitor.get_all_metrics()

        # Get system monitoring metrics
        system_metrics = monitoring_service.get_health_status()

        # Calculate system-wide statistics
        now = datetime.utcnow()
        dashboard_data = {
            "timestamp": now.isoformat(),
            "overall_status": health_report["status"],
            "uptime_seconds": health_report["uptime_seconds"],

            # System Health Summary
            "system_health": {
                "application": health_report["checks"]["application"]["status"],
                "database": health_report["checks"]["database"]["status"],
                "api_keys": health_report["checks"]["api_keys"]["status"],
                "system_resources": health_report["checks"]["system_resources"]["status"],
                "disk_space": health_report["checks"]["disk_space"]["status"],
                "external_dependencies": health_report["checks"]["external_dependencies"]["status"]
            },

            # API Health Dashboard
            "api_dashboard": {
                "overall_status": api_health["overall_status"],
                "healthy_apis": api_health["healthy_apis"],
                "total_apis": api_health["total_apis"],
                "api_details": api_health["api_health"],
                "monitoring_summary": api_health["monitoring_summary"]
            },

            # Real-time Performance Metrics
            "performance_metrics": {
                "response_times": _get_recent_response_times(api_monitoring_data),
                "success_rates": _calculate_success_rates(api_monitoring_data),
                "request_volumes": _get_request_volumes(api_monitoring_data),
                "error_rates": _calculate_error_rates(api_monitoring_data)
            },

            # Circuit Breaker Status
            "circuit_breakers": _get_circuit_breaker_status(api_health["api_health"]),

            # System Resource Utilization
            "resource_utilization": {
                "cpu_percent": health_report["system_info"]["cpu_percent"],
                "memory_percent": health_report["system_info"]["memory_percent"],
                "disk_usage": health_report["system_info"]["disk_usage"]
            },

            # Active Alerts and Issues
            "alerts": _get_active_alerts(api_monitoring_data, health_report),

            # Historical Trends (last 24 hours)
            "trends": _get_historical_trends(api_monitoring_data),

            # Quick Actions and Recommendations
            "recommendations": _generate_recommendations(health_report, api_health, api_monitoring_data)
        }

        # Determine HTTP status code
        if dashboard_data["overall_status"] == "healthy":
            status_code = 200
        elif dashboard_data["overall_status"] == "degraded":
            status_code = 200  # Still operational
        else:
            status_code = 503  # Service unavailable

        return jsonify(dashboard_data), status_code

    except Exception as e:
        logger.error(f"Enhanced dashboard failed: {e}")
        return jsonify({
            "status": "error",
            "error": "Dashboard generation failed",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


def _get_recent_response_times(api_monitoring_data: dict) -> dict:
    """Extract recent response times for all APIs"""
    response_times = {}
    for api_name, data in api_monitoring_data.items():
        recent_times = data.get('recent_response_times', [])
        if recent_times:
            response_times[api_name] = {
                "current_avg": sum(recent_times) / len(recent_times),
                "min": min(recent_times),
                "max": max(recent_times),
                "recent_values": recent_times[-5:]  # Last 5 values
            }
        else:
            response_times[api_name] = {
                "current_avg": 0,
                "min": 0,
                "max": 0,
                "recent_values": []
            }
    return response_times


def _calculate_success_rates(api_monitoring_data: dict) -> dict:
    """Calculate success rates for all APIs"""
    success_rates = {}
    for api_name, data in api_monitoring_data.items():
        metrics = data.get('metrics', {})
        total_requests = metrics.get('total_requests', 0)
        successful_requests = metrics.get('successful_requests', 0)

        if total_requests > 0:
            success_rate = (successful_requests / total_requests) * 100
        else:
            success_rate = 100.0  # No requests = 100% success rate

        success_rates[api_name] = {
            "percentage": round(success_rate, 2),
            "successful_requests": successful_requests,
            "total_requests": total_requests,
            "last_24h_requests": metrics.get('last_24h_requests', 0),
            "last_24h_failures": metrics.get('last_24h_failures', 0)
        }
    return success_rates


def _get_request_volumes(api_monitoring_data: dict) -> dict:
    """Get request volume statistics"""
    volumes = {}
    for api_name, data in api_monitoring_data.items():
        metrics = data.get('metrics', {})
        volumes[api_name] = {
            "total_requests": metrics.get('total_requests', 0),
            "last_24h_requests": metrics.get('last_24h_requests', 0),
            "requests_per_hour": metrics.get('last_24h_requests', 0) / 24,
            "uptime_percentage": metrics.get('uptime_percentage', 100.0)
        }
    return volumes


def _calculate_error_rates(api_monitoring_data: dict) -> dict:
    """Calculate error rates for all APIs"""
    error_rates = {}
    for api_name, data in api_monitoring_data.items():
        metrics = data.get('metrics', {})
        total_requests = metrics.get('total_requests', 0)
        failed_requests = metrics.get('failed_requests', 0)

        if total_requests > 0:
            error_rate = (failed_requests / total_requests) * 100
        else:
            error_rate = 0.0

        error_rates[api_name] = {
            "percentage": round(error_rate, 2),
            "failed_requests": failed_requests,
            "total_requests": total_requests,
            "last_24h_failures": metrics.get('last_24h_failures', 0)
        }
    return error_rates


def _get_circuit_breaker_status(api_health_data: dict) -> dict:
    """Get circuit breaker status for all APIs"""
    circuit_breakers = {}
    for api_name, health_info in api_health_data.items():
        consecutive_failures = health_info.get('consecutive_failures', 0)
        status = health_info.get('status', 'unknown')

        # Determine circuit breaker state based on failures and status
        if consecutive_failures >= 5:  # Circuit breaker threshold
            cb_state = "open"
        elif consecutive_failures >= 3:
            cb_state = "half_open"
        else:
            cb_state = "closed"

        circuit_breakers[api_name] = {
            "state": cb_state,
            "consecutive_failures": consecutive_failures,
            "api_status": status,
            "last_success": health_info.get('last_success'),
            "error_message": health_info.get('error_message')
        }
    return circuit_breakers


def _get_active_alerts(api_monitoring_data: dict, health_report: dict) -> list:
    """Get all active alerts and issues"""
    alerts = []

    # Check API monitoring alerts
    for api_name, data in api_monitoring_data.items():
        active_alerts = data.get('alerts_active', [])
        for alert in active_alerts:
            alerts.append({
                "type": "api_monitoring",
                "severity": "warning" if "High response time" in alert else "error",
                "api_name": api_name,
                "message": alert,
                "timestamp": datetime.utcnow().isoformat()
            })

    # Check system health alerts
    for check_name, check_data in health_report.get("checks", {}).items():
        if check_data["status"] in ["degraded", "unhealthy"]:
            severity = "error" if check_data["status"] == "unhealthy" else "warning"
            alerts.append({
                "type": "system_health",
                "severity": severity,
                "component": check_name,
                "message": check_data["message"],
                "timestamp": check_data["timestamp"]
            })

    # Check resource utilization alerts
    system_info = health_report.get("system_info", {})
    if system_info.get("cpu_percent", 0) > 80:
        alerts.append({
            "type": "resource_utilization",
            "severity": "warning",
            "component": "cpu",
            "message": f"High CPU usage: {system_info['cpu_percent']:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        })

    if system_info.get("memory_percent", 0) > 85:
        alerts.append({
            "type": "resource_utilization",
            "severity": "error" if system_info["memory_percent"] > 95 else "warning",
            "component": "memory",
            "message": f"High memory usage: {system_info['memory_percent']:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        })

    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)


def _get_historical_trends(api_monitoring_data: dict) -> dict:
    """Get historical trends for the last 24 hours"""
    trends = {}

    for api_name, data in api_monitoring_data.items():
        metrics = data.get('metrics', {})

        # Calculate trend indicators
        total_requests = metrics.get('total_requests', 0)
        last_24h_requests = metrics.get('last_24h_requests', 0)
        last_24h_failures = metrics.get('last_24h_failures', 0)

        # Simple trend calculation (would be more sophisticated with time-series data)
        if total_requests > 0:
            overall_success_rate = ((total_requests - metrics.get('failed_requests', 0)) / total_requests) * 100
        else:
            overall_success_rate = 100.0

        if last_24h_requests > 0:
            recent_success_rate = ((last_24h_requests - last_24h_failures) / last_24h_requests) * 100
        else:
            recent_success_rate = 100.0

        trends[api_name] = {
            "request_volume_trend": "stable",  # Would calculate from time-series data
            "success_rate_trend": "improving" if recent_success_rate > overall_success_rate else "stable",
            "response_time_trend": "stable",  # Would calculate from time-series data
            "overall_success_rate": round(overall_success_rate, 2),
            "recent_success_rate": round(recent_success_rate, 2),
            "avg_response_time": metrics.get('avg_response_time_ms', 0)
        }

    return trends


def _generate_recommendations(health_report: dict, api_health: dict, api_monitoring_data: dict) -> list:
    """Generate actionable recommendations based on current system state"""
    recommendations = []

    # Check overall system health
    if health_report["status"] == "unhealthy":
        recommendations.append({
            "priority": "high",
            "category": "system_health",
            "title": "Critical System Issues Detected",
            "description": "Multiple system components are unhealthy. Immediate attention required.",
            "action": "Review system health checks and address critical issues"
        })

    # Check API health
    unhealthy_apis = [name for name, info in api_health["api_health"].items()
                     if info["status"] in ["unavailable", "rate_limited"]]

    if unhealthy_apis:
        recommendations.append({
            "priority": "high",
            "category": "api_health",
            "title": f"API Issues: {', '.join(unhealthy_apis)}",
            "description": f"{len(unhealthy_apis)} API(s) are experiencing issues",
            "action": "Check API keys, rate limits, and network connectivity"
        })

    # Check performance issues
    slow_apis = []
    for api_name, data in api_monitoring_data.items():
        avg_response_time = data.get('metrics', {}).get('avg_response_time_ms', 0)
        if avg_response_time > 5000:  # 5 seconds
            slow_apis.append(api_name)

    if slow_apis:
        recommendations.append({
            "priority": "medium",
            "category": "performance",
            "title": f"Slow API Response Times: {', '.join(slow_apis)}",
            "description": "Some APIs are responding slowly, which may impact user experience",
            "action": "Investigate API performance and consider implementing caching"
        })

    # Check resource utilization
    system_info = health_report.get("system_info", {})
    if system_info.get("memory_percent", 0) > 80:
        recommendations.append({
            "priority": "medium",
            "category": "resources",
            "title": "High Memory Usage",
            "description": f"Memory usage is at {system_info['memory_percent']:.1f}%",
            "action": "Monitor memory usage and consider scaling or optimization"
        })

    # Check disk space
    if system_info.get("disk_usage", {}).get("percent", 0) > 85:
        recommendations.append({
            "priority": "high",
            "category": "resources",
            "title": "Low Disk Space",
            "description": f"Disk usage is at {system_info['disk_usage']['percent']:.1f}%",
            "action": "Free up disk space or expand storage capacity"
        })

    return recommendations


@health_bp.route('/shutdown/status', methods=['GET'])
def shutdown_status():
    """
    Shutdown status endpoint
    Returns current shutdown state and active request count
    """
    try:
        shutdown_service = get_shutdown_service()
        status = shutdown_service.get_shutdown_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Shutdown status check failed: {e}")
        return jsonify({
            "error": "Shutdown status system failure",
            "message": str(e)
        }), 503


# Error handlers for the health blueprint
@health_bp.errorhandler(404)
def health_not_found(error):
    """Handle 404 errors in health endpoints"""
    return jsonify({
        "error": "Health endpoint not found",
        "available_endpoints": [
            "/api/health",
            "/api/health/ready",
            "/api/health/live",
            "/api/health/detailed",
            "/api/health/metrics",
            "/api/health/history",
            "/api/health/status",
            "/api/shutdown/status"
        ]
    }), 404


@health_bp.errorhandler(500)
def health_internal_error(error):
    """Handle 500 errors in health endpoints"""
    logger.error(f"Internal error in health endpoint: {error}")
    return jsonify({
        "error": "Internal health system error",
        "message": "Health monitoring system encountered an error"
    }), 500


# Add CORS headers for health endpoints
@health_bp.after_request
def after_request(response):
    """Add CORS headers to health check responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response
