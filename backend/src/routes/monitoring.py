"""
Monitoring and Error Handling API Routes

Provides endpoints for system health monitoring, error reporting,
and performance metrics access.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging

from src.services.monitoring_service import monitoring_service, AlertLevel
from src.services.error_management_service import error_manager
from src.services.enhanced_retry_service import enhanced_retry_service
from src.services.fallback_service import fallback_service
from src.services.api_validation_service import api_validator

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
logger = logging.getLogger(__name__)


@monitoring_bp.route('/health', methods=['GET'])
def get_system_health():
    """Get overall system health status"""
    try:
        health_status = monitoring_service.get_health_status()
        
        # Add additional health information
        health_status.update({
            'api_status': api_validator.get_system_health_summary(),
            'circuit_breakers': enhanced_retry_service.get_circuit_breaker_status(),
            'error_rate': _calculate_recent_error_rate(),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'data': health_status
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'status': 'unknown'
        }), 500


@monitoring_bp.route('/health/detailed', methods=['GET'])
def get_detailed_health():
    """Get detailed system health information"""
    try:
        hours = request.args.get('hours', 1, type=int)
        
        detailed_health = {
            'system_health': monitoring_service.get_health_status(),
            'performance_metrics': monitoring_service.get_performance_summary(hours=hours),
            'error_statistics': error_manager.get_error_statistics(time_window_hours=hours),
            'api_health': api_validator.get_detailed_health_report(),
            'circuit_breakers': enhanced_retry_service.get_circuit_breaker_status(),
            'retry_statistics': enhanced_retry_service.get_retry_statistics(),
            'fallback_status': fallback_service.get_fallback_quality_report(),
            'alerts': monitoring_service.get_active_alerts(),
            'system_impact': error_manager.get_system_health_impact(),
            'timestamp': datetime.utcnow().isoformat(),
            'time_window_hours': hours
        }
        
        return jsonify({
            'success': True,
            'data': detailed_health
        }), 200
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Detailed health check failed'
        }), 500


@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        hours = request.args.get('hours', 1, type=int)
        metric_type = request.args.get('type', 'all')
        
        metrics = {
            'summary': monitoring_service.get_metrics_summary(hours=hours),
            'performance': monitoring_service.get_performance_summary(hours=hours),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if metric_type == 'performance' or metric_type == 'all':
            metrics['performance_details'] = _get_performance_details(hours)
        
        if metric_type == 'errors' or metric_type == 'all':
            metrics['error_details'] = error_manager.get_error_statistics(time_window_hours=hours)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics'
        }), 500


@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts"""
    try:
        level = request.args.get('level')
        alert_level = None
        
        if level:
            try:
                alert_level = AlertLevel(level.lower())
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid alert level: {level}'
                }), 400
        
        alerts = monitoring_service.get_active_alerts(level=alert_level)
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'total_count': len(alerts),
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Alert retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve alerts'
        }), 500


@monitoring_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve a specific alert"""
    try:
        monitoring_service.resolve_alert(alert_id)
        
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} resolved'
        }), 200
        
    except Exception as e:
        logger.error(f"Alert resolution failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to resolve alert'
        }), 500


@monitoring_bp.route('/circuit-breakers', methods=['GET'])
def get_circuit_breakers():
    """Get circuit breaker status"""
    try:
        status = enhanced_retry_service.get_circuit_breaker_status()
        
        return jsonify({
            'success': True,
            'data': {
                'circuit_breakers': status,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Circuit breaker status retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve circuit breaker status'
        }), 500


@monitoring_bp.route('/circuit-breakers/<operation_name>/reset', methods=['POST'])
def reset_circuit_breaker(operation_name):
    """Reset a specific circuit breaker"""
    try:
        enhanced_retry_service.reset_circuit_breaker(operation_name)
        
        return jsonify({
            'success': True,
            'message': f'Circuit breaker for {operation_name} reset'
        }), 200
        
    except Exception as e:
        logger.error(f"Circuit breaker reset failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to reset circuit breaker'
        }), 500


@monitoring_bp.route('/errors/report', methods=['POST'])
def report_error():
    """Report an error from the frontend"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No error data provided'
            }), 400
        
        # Log the frontend error
        error_data = {
            'error_id': data.get('error_id'),
            'message': data.get('message'),
            'stack': data.get('stack'),
            'component_stack': data.get('component_stack'),
            'user_agent': data.get('user_agent'),
            'url': data.get('url'),
            'timestamp': data.get('timestamp'),
            'user_id': data.get('user_id'),
            'correlation_id': data.get('correlation_id')
        }
        
        logger.error(f"Frontend error reported: {error_data}")
        
        # Create alert for critical frontend errors
        if data.get('severity') == 'critical':
            monitoring_service.create_alert(
                level=AlertLevel.ERROR,
                title="Critical Frontend Error",
                message=f"Critical error in frontend: {data.get('message', 'Unknown error')}",
                service="frontend",
                **error_data
            )
        
        return jsonify({
            'success': True,
            'message': 'Error reported successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error reporting failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to report error'
        }), 500


@monitoring_bp.route('/fallback/status', methods=['GET'])
def get_fallback_status():
    """Get fallback service status and quality report"""
    try:
        status = fallback_service.get_fallback_quality_report()
        
        return jsonify({
            'success': True,
            'data': {
                'fallback_status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Fallback status retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve fallback status'
        }), 500


def _calculate_recent_error_rate():
    """Calculate recent error rate"""
    try:
        stats = error_manager.get_error_statistics(time_window_hours=1)
        total_errors = stats.get('total_errors', 0)
        
        # Estimate total requests (this would be better tracked separately)
        performance_summary = monitoring_service.get_performance_summary(hours=1)
        total_requests = performance_summary.get('total_operations', 1)
        
        error_rate = total_errors / max(total_requests, 1)
        return min(error_rate, 1.0)  # Cap at 100%
        
    except Exception:
        return 0.0


def _get_performance_details(hours):
    """Get detailed performance information"""
    try:
        summary = monitoring_service.get_performance_summary(hours=hours)
        
        # Add additional performance insights
        details = {
            'summary': summary,
            'slow_operations': [],
            'high_error_operations': []
        }
        
        # Identify slow operations
        for operation, metrics in summary.get('operations', {}).items():
            if metrics.get('avg_duration', 0) > 5.0:  # Slower than 5 seconds
                details['slow_operations'].append({
                    'operation': operation,
                    'avg_duration': metrics['avg_duration'],
                    'max_duration': metrics.get('max_duration', 0)
                })
            
            if metrics.get('success_rate', 1.0) < 0.9:  # Less than 90% success rate
                details['high_error_operations'].append({
                    'operation': operation,
                    'success_rate': metrics['success_rate'],
                    'total_requests': metrics.get('total_requests', 0)
                })
        
        return details
        
    except Exception as e:
        logger.error(f"Performance details calculation failed: {str(e)}")
        return {}


# Error handler for monitoring blueprint
@monitoring_bp.errorhandler(Exception)
def handle_monitoring_error(error):
    """Handle errors in monitoring endpoints"""
    logger.error(f"Monitoring endpoint error: {str(error)}")
    
    return jsonify({
        'success': False,
        'error': 'Monitoring service error',
        'message': 'An error occurred while accessing monitoring data'
    }), 500
