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
