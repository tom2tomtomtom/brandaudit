"""
Graceful Shutdown Service
Handles application shutdown gracefully for zero-downtime deployments
"""

import os
import signal
import threading
import time
import logging
from typing import List, Callable, Dict, Any
from datetime import datetime
from flask import current_app
from src.extensions import db


class ShutdownService:
    """Handles graceful application shutdown"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self.shutdown_timeout = 30  # seconds
        self.active_requests = 0
        self.shutdown_start_time = None
        
        # Register signal handlers
        self._register_signal_handlers()
    
    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        # Handle SIGTERM (Docker/Kubernetes shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        
        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        
        # Handle SIGUSR1 for graceful restart
        signal.signal(signal.SIGUSR1, self._handle_restart_signal)
        
        self.logger.info("Shutdown signal handlers registered")
    
    def _handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
        
        # Start shutdown in a separate thread to avoid blocking signal handler
        shutdown_thread = threading.Thread(target=self._perform_graceful_shutdown)
        shutdown_thread.daemon = True
        shutdown_thread.start()
    
    def _handle_restart_signal(self, signum, frame):
        """Handle restart signals"""
        self.logger.info("Received SIGUSR1 signal, preparing for graceful restart...")
        # For restart, we perform the same shutdown but with different logging
        self._perform_graceful_shutdown(restart=True)
    
    def _perform_graceful_shutdown(self, restart=False):
        """Perform graceful shutdown sequence"""
        if self.is_shutting_down:
            self.logger.warning("Shutdown already in progress, ignoring duplicate signal")
            return
        
        self.is_shutting_down = True
        self.shutdown_start_time = datetime.utcnow()
        
        action = "restart" if restart else "shutdown"
        self.logger.info(f"Starting graceful {action} sequence...")
        
        try:
            # Step 1: Stop accepting new requests
            self._stop_accepting_requests()
            
            # Step 2: Wait for active requests to complete
            self._wait_for_active_requests()
            
            # Step 3: Run custom shutdown handlers
            self._run_shutdown_handlers()
            
            # Step 4: Close database connections
            self._close_database_connections()
            
            # Step 5: Final cleanup
            self._final_cleanup()
            
            shutdown_duration = (datetime.utcnow() - self.shutdown_start_time).total_seconds()
            self.logger.info(f"Graceful {action} completed in {shutdown_duration:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Error during graceful {action}: {e}")
        finally:
            if not restart:
                # Exit the application
                os._exit(0)
    
    def _stop_accepting_requests(self):
        """Stop accepting new requests"""
        self.logger.info("Stopping acceptance of new requests...")
        # This would typically involve stopping the web server from accepting new connections
        # For Flask with Gunicorn, this is handled by the process manager
        time.sleep(1)  # Brief pause to ensure no new requests are accepted
    
    def _wait_for_active_requests(self):
        """Wait for active requests to complete"""
        self.logger.info(f"Waiting for {self.active_requests} active requests to complete...")
        
        wait_start = time.time()
        while self.active_requests > 0 and (time.time() - wait_start) < self.shutdown_timeout:
            self.logger.debug(f"Still waiting for {self.active_requests} active requests...")
            time.sleep(0.5)
        
        if self.active_requests > 0:
            self.logger.warning(f"Shutdown timeout reached, {self.active_requests} requests still active")
        else:
            self.logger.info("All active requests completed")
    
    def _run_shutdown_handlers(self):
        """Run custom shutdown handlers"""
        self.logger.info(f"Running {len(self.shutdown_handlers)} shutdown handlers...")
        
        for i, handler in enumerate(self.shutdown_handlers):
            try:
                self.logger.debug(f"Running shutdown handler {i+1}/{len(self.shutdown_handlers)}")
                handler()
            except Exception as e:
                self.logger.error(f"Error in shutdown handler {i+1}: {e}")
    
    def _close_database_connections(self):
        """Close database connections"""
        self.logger.info("Closing database connections...")
        
        try:
            if db and db.engine:
                # Close all connections in the pool
                db.engine.dispose()
                self.logger.info("Database connections closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing database connections: {e}")
    
    def _final_cleanup(self):
        """Perform final cleanup tasks"""
        self.logger.info("Performing final cleanup...")
        
        try:
            # Clear any temporary files
            temp_dirs = ['uploads/temp', 'logs/temp']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Flush logs
            for handler in logging.getLogger().handlers:
                handler.flush()
            
            self.logger.info("Final cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during final cleanup: {e}")
    
    def register_shutdown_handler(self, handler: Callable):
        """Register a custom shutdown handler"""
        if callable(handler):
            self.shutdown_handlers.append(handler)
            self.logger.debug(f"Registered shutdown handler: {handler.__name__}")
        else:
            raise ValueError("Shutdown handler must be callable")
    
    def increment_active_requests(self):
        """Increment active request counter"""
        if not self.is_shutting_down:
            self.active_requests += 1
    
    def decrement_active_requests(self):
        """Decrement active request counter"""
        if self.active_requests > 0:
            self.active_requests -= 1
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy (not shutting down)"""
        return not self.is_shutting_down
    
    def get_shutdown_status(self) -> Dict[str, Any]:
        """Get current shutdown status"""
        if not self.is_shutting_down:
            return {
                "shutting_down": False,
                "active_requests": self.active_requests,
                "registered_handlers": len(self.shutdown_handlers)
            }
        
        shutdown_duration = 0
        if self.shutdown_start_time:
            shutdown_duration = (datetime.utcnow() - self.shutdown_start_time).total_seconds()
        
        return {
            "shutting_down": True,
            "shutdown_start_time": self.shutdown_start_time.isoformat() if self.shutdown_start_time else None,
            "shutdown_duration_seconds": shutdown_duration,
            "active_requests": self.active_requests,
            "registered_handlers": len(self.shutdown_handlers),
            "timeout_seconds": self.shutdown_timeout
        }


class RequestTracker:
    """Middleware to track active requests for graceful shutdown"""
    
    def __init__(self, shutdown_service: ShutdownService):
        self.shutdown_service = shutdown_service
    
    def __call__(self, environ, start_response):
        """WSGI middleware to track requests"""
        # Check if we're shutting down
        if self.shutdown_service.is_shutting_down:
            # Return 503 Service Unavailable for new requests during shutdown
            status = '503 Service Unavailable'
            headers = [
                ('Content-Type', 'application/json'),
                ('Retry-After', '30')
            ]
            start_response(status, headers)
            return [b'{"error": "Service is shutting down", "retry_after": 30}']
        
        # Track this request
        self.shutdown_service.increment_active_requests()
        
        try:
            # Process the request
            return self.app(environ, start_response)
        finally:
            # Decrement counter when request completes
            self.shutdown_service.decrement_active_requests()


# Global shutdown service instance
shutdown_service = ShutdownService()


def init_graceful_shutdown(app):
    """Initialize graceful shutdown for Flask application"""
    
    # Register database cleanup handler
    def cleanup_database():
        """Clean up database connections"""
        try:
            if db and db.engine:
                db.engine.dispose()
        except Exception as e:
            app.logger.error(f"Error cleaning up database: {e}")
    
    shutdown_service.register_shutdown_handler(cleanup_database)
    
    # Register application cleanup handler
    def cleanup_application():
        """Clean up application resources"""
        try:
            # Clear caches
            if hasattr(app, 'cache'):
                app.cache.clear()
            
            # Close any open files
            app.logger.info("Application cleanup completed")
            
        except Exception as e:
            app.logger.error(f"Error cleaning up application: {e}")
    
    shutdown_service.register_shutdown_handler(cleanup_application)
    
    # Add request tracking middleware
    app.wsgi_app = RequestTracker(shutdown_service)
    
    app.logger.info("Graceful shutdown initialized")
    
    return shutdown_service


def get_shutdown_service() -> ShutdownService:
    """Get the global shutdown service instance"""
    return shutdown_service
