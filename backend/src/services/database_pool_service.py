"""
Database Connection Pool Service
Provides production-ready database connection pooling, monitoring, and optimization
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import DisconnectionError, OperationalError
from flask import current_app
from src.extensions import db


@dataclass
class ConnectionPoolMetrics:
    """Connection pool metrics for monitoring"""
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    total_connections: int
    active_connections: int
    idle_connections: int
    failed_connections: int
    connection_errors: int
    average_checkout_time: float
    peak_connections: int
    pool_timeouts: int


class DatabasePoolService:
    """Enhanced database connection pool management service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[ConnectionPoolMetrics] = []
        self.connection_errors = 0
        self.pool_timeouts = 0
        self.peak_connections = 0
        self.checkout_times: List[float] = []
        self.max_history = 100
        self._lock = threading.Lock()
        
        # Pool configuration based on environment
        self.pool_config = self._get_pool_config()
        
    def _get_pool_config(self) -> Dict[str, Any]:
        """Get optimized pool configuration based on environment"""
        env = os.environ.get('FLASK_ENV', 'production')
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        
        if database_url.startswith('sqlite'):
            # SQLite configuration
            return {
                'poolclass': StaticPool,
                'pool_size': 1,
                'max_overflow': 0,
                'pool_timeout': 20,
                'pool_recycle': -1,
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 20
                }
            }
        else:
            # PostgreSQL/MySQL configuration
            if env == 'production':
                return {
                    'poolclass': QueuePool,
                    'pool_size': 10,
                    'max_overflow': 20,
                    'pool_timeout': 30,
                    'pool_recycle': 3600,  # 1 hour
                    'pool_pre_ping': True,
                    'connect_args': {
                        'connect_timeout': 10,
                        'application_name': 'brand_audit_tool'
                    }
                }
            else:
                return {
                    'poolclass': QueuePool,
                    'pool_size': 5,
                    'max_overflow': 10,
                    'pool_timeout': 20,
                    'pool_recycle': 1800,  # 30 minutes
                    'pool_pre_ping': True,
                    'connect_args': {
                        'connect_timeout': 10,
                        'application_name': 'brand_audit_tool_dev'
                    }
                }
    
    def configure_engine(self, app) -> Engine:
        """Configure database engine with optimized connection pooling"""
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        
        if not database_url:
            raise ValueError("SQLALCHEMY_DATABASE_URI not configured")
        
        # Create engine with pool configuration
        engine = create_engine(
            database_url,
            echo=app.config.get('SQLALCHEMY_ECHO', False),
            **self.pool_config
        )
        
        # Register event listeners for monitoring
        self._register_event_listeners(engine)
        
        self.logger.info(f"Database engine configured with pool: {self.pool_config}")
        
        return engine
    
    def _register_event_listeners(self, engine: Engine):
        """Register SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Handle new database connections"""
            self.logger.debug("New database connection established")
            
            # Set connection-specific settings
            if hasattr(dbapi_connection, 'execute'):
                try:
                    # For PostgreSQL
                    if 'postgresql' in str(engine.url):
                        dbapi_connection.execute("SET statement_timeout = '300s'")
                        dbapi_connection.execute("SET idle_in_transaction_session_timeout = '600s'")
                    # For MySQL
                    elif 'mysql' in str(engine.url):
                        dbapi_connection.execute("SET SESSION wait_timeout = 300")
                        dbapi_connection.execute("SET SESSION interactive_timeout = 300")
                except Exception as e:
                    self.logger.warning(f"Failed to set connection parameters: {e}")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle connection checkout from pool"""
            connection_record.checkout_time = time.time()
            
            # Update peak connections
            current_connections = self._get_current_connection_count(engine)
            if current_connections > self.peak_connections:
                self.peak_connections = current_connections
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """Handle connection checkin to pool"""
            if hasattr(connection_record, 'checkout_time'):
                checkout_duration = time.time() - connection_record.checkout_time
                with self._lock:
                    self.checkout_times.append(checkout_duration)
                    # Keep only recent checkout times
                    if len(self.checkout_times) > 1000:
                        self.checkout_times = self.checkout_times[-500:]
        
        @event.listens_for(engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            """Handle connection invalidation"""
            self.logger.warning(f"Database connection invalidated: {exception}")
            with self._lock:
                self.connection_errors += 1
        
        # Pool events
        @event.listens_for(engine.pool, "connect")
        def on_pool_connect(dbapi_connection, connection_record):
            """Handle pool connection events"""
            self.logger.debug("Connection added to pool")
        
        @event.listens_for(engine.pool, "checkout")
        def on_pool_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle pool checkout events"""
            pass  # Already handled in engine checkout
        
        @event.listens_for(engine.pool, "checkin")
        def on_pool_checkin(dbapi_connection, connection_record):
            """Handle pool checkin events"""
            pass  # Already handled in engine checkin
    
    def _get_current_connection_count(self, engine: Engine) -> int:
        """Get current number of active connections"""
        try:
            pool = engine.pool
            return pool.checkedout()
        except Exception:
            return 0
    
    def get_pool_metrics(self, engine: Optional[Engine] = None) -> ConnectionPoolMetrics:
        """Get comprehensive connection pool metrics"""
        if engine is None:
            engine = db.engine
        
        if not engine or not hasattr(engine, 'pool'):
            return ConnectionPoolMetrics(
                pool_size=0, checked_in=0, checked_out=0, overflow=0,
                invalid=0, total_connections=0, active_connections=0,
                idle_connections=0, failed_connections=self.connection_errors,
                connection_errors=self.connection_errors, average_checkout_time=0.0,
                peak_connections=self.peak_connections, pool_timeouts=self.pool_timeouts
            )
        
        pool = engine.pool
        
        # Calculate average checkout time
        avg_checkout_time = 0.0
        if self.checkout_times:
            avg_checkout_time = sum(self.checkout_times) / len(self.checkout_times)
        
        metrics = ConnectionPoolMetrics(
            pool_size=pool.size(),
            checked_in=pool.checkedin(),
            checked_out=pool.checkedout(),
            overflow=pool.overflow(),
            invalid=pool.invalid(),
            total_connections=pool.size() + pool.overflow(),
            active_connections=pool.checkedout(),
            idle_connections=pool.checkedin(),
            failed_connections=self.connection_errors,
            connection_errors=self.connection_errors,
            average_checkout_time=round(avg_checkout_time, 4),
            peak_connections=self.peak_connections,
            pool_timeouts=self.pool_timeouts
        )
        
        # Store in history
        with self._lock:
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
        
        return metrics
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get detailed pool status for monitoring"""
        metrics = self.get_pool_metrics()
        
        # Calculate pool utilization
        pool_utilization = 0.0
        if metrics.pool_size > 0:
            pool_utilization = (metrics.checked_out / metrics.pool_size) * 100
        
        # Determine health status
        health_status = "healthy"
        if pool_utilization > 90:
            health_status = "critical"
        elif pool_utilization > 70:
            health_status = "warning"
        elif metrics.connection_errors > 10:
            health_status = "degraded"
        
        return {
            "health_status": health_status,
            "pool_utilization_percent": round(pool_utilization, 2),
            "metrics": {
                "pool_size": metrics.pool_size,
                "active_connections": metrics.active_connections,
                "idle_connections": metrics.idle_connections,
                "overflow_connections": metrics.overflow,
                "invalid_connections": metrics.invalid,
                "total_connections": metrics.total_connections,
                "peak_connections": metrics.peak_connections,
                "failed_connections": metrics.failed_connections,
                "connection_errors": metrics.connection_errors,
                "pool_timeouts": metrics.pool_timeouts,
                "average_checkout_time_seconds": metrics.average_checkout_time
            },
            "configuration": self.pool_config,
            "recommendations": self._get_recommendations(metrics, pool_utilization)
        }
    
    def _get_recommendations(self, metrics: ConnectionPoolMetrics, utilization: float) -> List[str]:
        """Get optimization recommendations based on metrics"""
        recommendations = []
        
        if utilization > 80:
            recommendations.append("Consider increasing pool_size or max_overflow")
        
        if metrics.connection_errors > 5:
            recommendations.append("High connection error rate - check database connectivity")
        
        if metrics.average_checkout_time > 1.0:
            recommendations.append("High average checkout time - consider query optimization")
        
        if metrics.pool_timeouts > 0:
            recommendations.append("Pool timeouts detected - consider increasing pool_timeout")
        
        if metrics.invalid > 0:
            recommendations.append("Invalid connections detected - check pool_recycle setting")
        
        return recommendations
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper error handling"""
        connection = None
        start_time = time.time()
        
        try:
            connection = db.engine.connect()
            yield connection
        except (DisconnectionError, OperationalError) as e:
            self.logger.error(f"Database connection error: {e}")
            with self._lock:
                self.connection_errors += 1
            raise
        except Exception as e:
            self.logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")
            
            # Record checkout time
            checkout_time = time.time() - start_time
            with self._lock:
                self.checkout_times.append(checkout_time)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                # Simple query to test connection
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            duration = (time.time() - start_time) * 1000
            
            return {
                "status": "success",
                "duration_ms": round(duration, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            return {
                "status": "failed",
                "error": str(e),
                "duration_ms": round(duration, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def optimize_pool(self) -> Dict[str, Any]:
        """Optimize pool configuration based on current metrics"""
        metrics = self.get_pool_metrics()
        current_config = self.pool_config.copy()
        
        optimizations = []
        
        # Analyze utilization patterns
        if len(self.metrics_history) >= 10:
            recent_metrics = self.metrics_history[-10:]
            avg_utilization = sum(m.checked_out / max(m.pool_size, 1) for m in recent_metrics) / len(recent_metrics)
            
            if avg_utilization > 0.8:
                # High utilization - increase pool size
                new_pool_size = min(current_config.get('pool_size', 5) + 2, 20)
                optimizations.append(f"Increase pool_size to {new_pool_size}")
                
            elif avg_utilization < 0.3:
                # Low utilization - decrease pool size
                new_pool_size = max(current_config.get('pool_size', 5) - 1, 2)
                optimizations.append(f"Decrease pool_size to {new_pool_size}")
        
        # Check error rates
        if metrics.connection_errors > 5:
            optimizations.append("Increase pool_recycle time due to connection errors")
        
        # Check checkout times
        if metrics.average_checkout_time > 2.0:
            optimizations.append("Consider increasing pool_timeout due to slow checkouts")
        
        return {
            "current_metrics": metrics.__dict__,
            "current_config": current_config,
            "optimizations": optimizations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset_metrics(self):
        """Reset metrics counters"""
        with self._lock:
            self.connection_errors = 0
            self.pool_timeouts = 0
            self.peak_connections = 0
            self.checkout_times.clear()
            self.metrics_history.clear()
        
        self.logger.info("Database pool metrics reset")


# Global database pool service instance
db_pool_service = DatabasePoolService()
