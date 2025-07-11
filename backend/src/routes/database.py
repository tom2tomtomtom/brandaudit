"""
Database Monitoring Routes
Provides endpoints for database connection pool monitoring and optimization
"""

from flask import Blueprint, jsonify, request
from src.services.database_pool_service import db_pool_service
import logging

# Create database monitoring blueprint
db_bp = Blueprint('database', __name__, url_prefix='/api/database')
logger = logging.getLogger(__name__)


@db_bp.route('/status', methods=['GET'])
def database_status():
    """
    Get comprehensive database status including connection pool metrics
    """
    try:
        status = db_pool_service.get_pool_status()
        
        # Determine HTTP status code based on database health
        if status['health_status'] == 'critical':
            status_code = 503
        elif status['health_status'] in ['warning', 'degraded']:
            status_code = 200  # Still operational but with warnings
        else:
            status_code = 200
        
        return jsonify(status), status_code
        
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return jsonify({
            "health_status": "error",
            "error": "Database status check failed",
            "message": str(e)
        }), 503


@db_bp.route('/metrics', methods=['GET'])
def database_metrics():
    """
    Get detailed database connection pool metrics
    """
    try:
        metrics = db_pool_service.get_pool_metrics()
        
        return jsonify({
            "metrics": {
                "pool_size": metrics.pool_size,
                "checked_in": metrics.checked_in,
                "checked_out": metrics.checked_out,
                "overflow": metrics.overflow,
                "invalid": metrics.invalid,
                "total_connections": metrics.total_connections,
                "active_connections": metrics.active_connections,
                "idle_connections": metrics.idle_connections,
                "failed_connections": metrics.failed_connections,
                "connection_errors": metrics.connection_errors,
                "average_checkout_time": metrics.average_checkout_time,
                "peak_connections": metrics.peak_connections,
                "pool_timeouts": metrics.pool_timeouts
            },
            "timestamp": metrics.__dict__.get('timestamp', 'N/A')
        }), 200
        
    except Exception as e:
        logger.error(f"Database metrics failed: {e}")
        return jsonify({
            "error": "Database metrics system failure",
            "message": str(e)
        }), 503


@db_bp.route('/test', methods=['GET'])
def test_connection():
    """
    Test database connection and return performance metrics
    """
    try:
        test_result = db_pool_service.test_connection()
        
        status_code = 200 if test_result['status'] == 'success' else 503
        
        return jsonify(test_result), status_code
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return jsonify({
            "status": "failed",
            "error": "Connection test system failure",
            "message": str(e)
        }), 503


@db_bp.route('/optimize', methods=['POST'])
def optimize_pool():
    """
    Get optimization recommendations for database connection pool
    """
    try:
        optimization_report = db_pool_service.optimize_pool()
        
        return jsonify(optimization_report), 200
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return jsonify({
            "error": "Database optimization system failure",
            "message": str(e)
        }), 503


@db_bp.route('/history', methods=['GET'])
def metrics_history():
    """
    Get historical database metrics
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # Cap at 200 entries
        
        # Get metrics history
        history = db_pool_service.metrics_history[-limit:] if db_pool_service.metrics_history else []
        
        # Format history for JSON response
        formatted_history = []
        for metrics in history:
            formatted_history.append({
                "pool_size": metrics.pool_size,
                "active_connections": metrics.active_connections,
                "idle_connections": metrics.idle_connections,
                "overflow": metrics.overflow,
                "invalid": metrics.invalid,
                "connection_errors": metrics.connection_errors,
                "average_checkout_time": metrics.average_checkout_time,
                "peak_connections": metrics.peak_connections
            })
        
        return jsonify({
            "history": formatted_history,
            "total_entries": len(db_pool_service.metrics_history),
            "returned_entries": len(formatted_history)
        }), 200
        
    except Exception as e:
        logger.error(f"Database metrics history failed: {e}")
        return jsonify({
            "error": "Database metrics history system failure",
            "message": str(e)
        }), 503


@db_bp.route('/reset-metrics', methods=['POST'])
def reset_metrics():
    """
    Reset database metrics counters (admin endpoint)
    """
    try:
        # Check if this is an admin request (you might want to add authentication)
        admin_key = request.headers.get('X-Admin-Key')
        if not admin_key:
            return jsonify({
                "error": "Admin key required",
                "message": "X-Admin-Key header is required for this operation"
            }), 401
        
        # Reset metrics
        db_pool_service.reset_metrics()
        
        return jsonify({
            "status": "success",
            "message": "Database metrics reset successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Database metrics reset failed: {e}")
        return jsonify({
            "error": "Database metrics reset failed",
            "message": str(e)
        }), 503


@db_bp.route('/configuration', methods=['GET'])
def get_configuration():
    """
    Get current database pool configuration
    """
    try:
        config = db_pool_service.pool_config
        
        # Remove sensitive information
        safe_config = config.copy()
        if 'connect_args' in safe_config:
            connect_args = safe_config['connect_args'].copy()
            # Remove passwords or sensitive data
            for key in list(connect_args.keys()):
                if 'password' in key.lower() or 'secret' in key.lower():
                    connect_args[key] = '***REDACTED***'
            safe_config['connect_args'] = connect_args
        
        return jsonify({
            "configuration": safe_config,
            "environment": db_pool_service._get_pool_config.__doc__ or "production"
        }), 200
        
    except Exception as e:
        logger.error(f"Database configuration retrieval failed: {e}")
        return jsonify({
            "error": "Database configuration retrieval failed",
            "message": str(e)
        }), 503


@db_bp.route('/health-summary', methods=['GET'])
def health_summary():
    """
    Get a summary of database health for dashboards
    """
    try:
        status = db_pool_service.get_pool_status()
        test_result = db_pool_service.test_connection()
        
        summary = {
            "overall_health": status['health_status'],
            "connection_test": test_result['status'],
            "response_time_ms": test_result.get('duration_ms', 0),
            "pool_utilization_percent": status['pool_utilization_percent'],
            "active_connections": status['metrics']['active_connections'],
            "total_connections": status['metrics']['total_connections'],
            "connection_errors": status['metrics']['connection_errors'],
            "recommendations_count": len(status['recommendations']),
            "has_issues": len(status['recommendations']) > 0 or status['health_status'] != 'healthy'
        }
        
        # Determine overall status code
        if summary['overall_health'] == 'critical' or summary['connection_test'] != 'success':
            status_code = 503
        elif summary['has_issues']:
            status_code = 200  # Operational with warnings
        else:
            status_code = 200
        
        return jsonify(summary), status_code
        
    except Exception as e:
        logger.error(f"Database health summary failed: {e}")
        return jsonify({
            "overall_health": "error",
            "connection_test": "failed",
            "error": str(e),
            "has_issues": True
        }), 503


# Error handlers for the database blueprint
@db_bp.errorhandler(404)
def database_not_found(error):
    """Handle 404 errors in database endpoints"""
    return jsonify({
        "error": "Database endpoint not found",
        "available_endpoints": [
            "/api/database/status",
            "/api/database/metrics",
            "/api/database/test",
            "/api/database/optimize",
            "/api/database/history",
            "/api/database/configuration",
            "/api/database/health-summary"
        ]
    }), 404


@db_bp.errorhandler(500)
def database_internal_error(error):
    """Handle 500 errors in database endpoints"""
    logger.error(f"Internal error in database endpoint: {error}")
    return jsonify({
        "error": "Internal database monitoring error",
        "message": "Database monitoring system encountered an error"
    }), 500


# Add CORS headers for database endpoints
@db_bp.after_request
def after_request(response):
    """Add CORS headers to database monitoring responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Admin-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response
