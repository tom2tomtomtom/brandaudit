"""
Real-time monitoring endpoints with WebSocket support
"""
from flask import Blueprint, jsonify, request
from flask_socketio import emit, join_room, leave_room
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from src.services.api_monitoring_service import api_monitor
from src.services.api_validation_service import api_validator
from src.services.structured_logger import StructuredLogger

# Create blueprint
realtime_bp = Blueprint('realtime', __name__)
logger = StructuredLogger(__name__)

# Global WebSocket connections tracking
websocket_connections = {}
monitoring_threads = {}


@realtime_bp.route('/metrics/live', methods=['GET'])
def get_live_metrics():
    """Get current live metrics snapshot"""
    try:
        window_minutes = request.args.get('window', 5, type=int)
        api_name = request.args.get('api_name')
        
        # Get real-time metrics summary
        metrics_summary = api_monitor.get_real_time_metrics_summary(window_minutes)
        
        # Get recent metrics
        recent_metrics = api_monitor.get_recent_metrics(
            api_name=api_name,
            minutes_back=window_minutes
        )
        
        # Get API health status
        api_health = api_validator.get_system_health_summary()
        
        # Get circuit breaker status
        circuit_breaker_status = api_validator.get_circuit_breaker_status()
        
        return jsonify({
            'success': True,
            'data': {
                'timestamp': datetime.utcnow().isoformat(),
                'window_minutes': window_minutes,
                'metrics_summary': metrics_summary,
                'recent_metrics': recent_metrics[-50:],  # Last 50 metrics
                'api_health': api_health,
                'circuit_breakers': circuit_breaker_status,
                'alert_history': api_monitor.get_alert_history(10)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get live metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve live metrics',
            'message': str(e)
        }), 500


@realtime_bp.route('/metrics/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        dashboard_data = api_monitor.get_live_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard data',
            'message': str(e)
        }), 500


@realtime_bp.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    """Get historical metrics data"""
    try:
        api_name = request.args.get('api_name')
        metric_type = request.args.get('metric_type')
        hours_back = request.args.get('hours', 1, type=int)
        
        # Get historical metrics
        historical_metrics = api_monitor.get_recent_metrics(
            api_name=api_name,
            metric_type=metric_type,
            minutes_back=hours_back * 60
        )
        
        return jsonify({
            'success': True,
            'data': {
                'api_name': api_name,
                'metric_type': metric_type,
                'hours_back': hours_back,
                'metrics': historical_metrics
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics history',
            'message': str(e)
        }), 500


def init_websocket_handlers(socketio):
    """Initialize WebSocket handlers for real-time monitoring"""
    
    @socketio.on('connect', namespace='/monitoring')
    def handle_connect():
        """Handle WebSocket connection"""
        logger.info("WebSocket client connected to monitoring namespace")
        emit('connected', {'message': 'Connected to real-time monitoring'})
    
    @socketio.on('disconnect', namespace='/monitoring')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        client_id = request.sid
        logger.info(f"WebSocket client disconnected: {client_id}")
        
        # Clean up monitoring thread if exists
        if client_id in monitoring_threads:
            monitoring_threads[client_id].stop()
            del monitoring_threads[client_id]
    
    @socketio.on('subscribe_metrics', namespace='/monitoring')
    def handle_subscribe_metrics(data):
        """Handle subscription to real-time metrics"""
        client_id = request.sid
        api_name = data.get('api_name')
        update_interval = data.get('interval', 5)  # seconds
        
        logger.info(f"Client {client_id} subscribing to metrics", 
                   api_name=api_name, update_interval=update_interval)
        
        # Start monitoring thread for this client
        if client_id not in monitoring_threads:
            thread = MetricsStreamingThread(
                client_id=client_id,
                socketio=socketio,
                api_name=api_name,
                update_interval=update_interval
            )
            monitoring_threads[client_id] = thread
            thread.start()
        
        emit('subscription_confirmed', {
            'api_name': api_name,
            'update_interval': update_interval
        })
    
    @socketio.on('unsubscribe_metrics', namespace='/monitoring')
    def handle_unsubscribe_metrics():
        """Handle unsubscription from real-time metrics"""
        client_id = request.sid
        
        if client_id in monitoring_threads:
            monitoring_threads[client_id].stop()
            del monitoring_threads[client_id]
        
        emit('unsubscription_confirmed', {'message': 'Unsubscribed from metrics'})


class MetricsStreamingThread(threading.Thread):
    """Thread for streaming real-time metrics to WebSocket clients"""
    
    def __init__(self, client_id: str, socketio, api_name: Optional[str] = None, 
                 update_interval: int = 5):
        super().__init__(daemon=True)
        self.client_id = client_id
        self.socketio = socketio
        self.api_name = api_name
        self.update_interval = update_interval
        self.stop_event = threading.Event()
        self.logger = StructuredLogger(f"{__name__}.MetricsStreamingThread")
    
    def run(self):
        """Run the metrics streaming loop"""
        self.logger.info(f"Starting metrics streaming for client {self.client_id}")
        
        while not self.stop_event.is_set():
            try:
                # Get current metrics
                metrics_data = self._get_current_metrics()
                
                # Emit to specific client
                self.socketio.emit(
                    'metrics_update',
                    metrics_data,
                    namespace='/monitoring',
                    room=self.client_id
                )
                
                # Wait for next update
                self.stop_event.wait(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in metrics streaming: {e}", 
                                client_id=self.client_id)
                break
        
        self.logger.info(f"Stopped metrics streaming for client {self.client_id}")
    
    def stop(self):
        """Stop the streaming thread"""
        self.stop_event.set()
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics for streaming"""
        try:
            # Get real-time metrics summary
            metrics_summary = api_monitor.get_real_time_metrics_summary(1)  # 1 minute window
            
            # Get recent metrics
            recent_metrics = api_monitor.get_recent_metrics(
                api_name=self.api_name,
                minutes_back=1
            )
            
            # Get API health
            api_health = api_validator.get_system_health_summary()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'client_id': self.client_id,
                'api_name': self.api_name,
                'metrics_summary': metrics_summary,
                'recent_metrics': recent_metrics[-10:],  # Last 10 metrics
                'api_health': api_health,
                'update_interval': self.update_interval
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get current metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }


# Alert callback for WebSocket notifications
def websocket_alert_callback(alert: Dict[str, Any]):
    """Callback to send alerts via WebSocket"""
    try:
        from src.extensions import socketio
        socketio.emit('alert', alert, namespace='/monitoring')
    except Exception as e:
        logger.error(f"Failed to send WebSocket alert: {e}")


# Register alert callback
api_monitor.add_alert_callback(websocket_alert_callback)
