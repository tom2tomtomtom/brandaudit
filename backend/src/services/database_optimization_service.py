"""
Database Optimization Service for Brand Audit App
Implements query optimization, connection pooling, and efficient data patterns
"""

import logging
import time
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from flask import current_app

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report


class DatabaseOptimizationService:
    """
    Service for database performance optimization and monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.query_stats = {
            'total_queries': 0,
            'slow_queries': 0,
            'average_query_time': 0,
            'query_times': []
        }
        
        # Set up query monitoring
        self._setup_query_monitoring()
    
    def _setup_query_monitoring(self):
        """Set up SQLAlchemy event listeners for query monitoring"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            self.query_stats['total_queries'] += 1
            self.query_stats['query_times'].append(total_time)
            
            # Keep only last 1000 query times for average calculation
            if len(self.query_stats['query_times']) > 1000:
                self.query_stats['query_times'] = self.query_stats['query_times'][-1000:]
            
            self.query_stats['average_query_time'] = sum(self.query_stats['query_times']) / len(self.query_stats['query_times'])
            
            # Log slow queries (>1 second)
            if total_time > 1.0:
                self.query_stats['slow_queries'] += 1
                self.logger.warning(f"Slow query detected ({total_time:.2f}s): {statement[:200]}...")
    
    def optimize_database_connection(self, app):
        """Configure database connection pool for optimal performance"""
        
        # Connection pool settings
        pool_settings = {
            'poolclass': QueuePool,
            'pool_size': 10,          # Number of connections to maintain
            'max_overflow': 20,       # Additional connections when pool is full
            'pool_timeout': 30,       # Timeout when getting connection from pool
            'pool_recycle': 3600,     # Recycle connections after 1 hour
            'pool_pre_ping': True,    # Validate connections before use
        }
        
        # Update database URI with pool settings
        if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            # PostgreSQL specific optimizations
            pool_settings.update({
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'brand_audit_app'
                }
            })
        
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = pool_settings
        self.logger.info("Database connection pool optimized")
    
    def get_optimized_analyses(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user analyses with optimized query"""
        
        try:
            # Use optimized query with proper indexing
            query = db.session.query(Analysis).filter(
                Analysis.user_id == user_id
            ).order_by(
                Analysis.created_at.desc()
            ).limit(limit).offset(offset)
            
            # Use options to optimize loading
            from sqlalchemy.orm import joinedload
            query = query.options(joinedload(Analysis.user))
            
            analyses = query.all()
            
            return [
                {
                    'id': analysis.id,
                    'brand_name': analysis.brand_name,
                    'status': analysis.status,
                    'progress': analysis.progress,
                    'created_at': analysis.created_at.isoformat(),
                    'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
                    'processing_time': analysis.processing_time_seconds,
                    'concurrent_processing': analysis.concurrent_processing_used
                }
                for analysis in analyses
            ]
            
        except Exception as e:
            self.logger.error(f"Optimized analyses query failed: {str(e)}")
            return []
    
    def get_analysis_with_cache_check(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis with intelligent caching"""
        
        try:
            # Use select_related equivalent for SQLAlchemy
            from sqlalchemy.orm import joinedload
            
            analysis = db.session.query(Analysis).options(
                joinedload(Analysis.user)
            ).filter(Analysis.id == analysis_id).first()
            
            if not analysis:
                return None
            
            return {
                'id': analysis.id,
                'brand_name': analysis.brand_name,
                'status': analysis.status,
                'progress': analysis.progress,
                'results': analysis.results,
                'error_message': analysis.error_message,
                'status_message': analysis.status_message,
                'created_at': analysis.created_at.isoformat(),
                'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
                'performance_metrics': {
                    'processing_time_seconds': analysis.processing_time_seconds,
                    'concurrent_processing_used': analysis.concurrent_processing_used,
                    'cache_hit_rate': analysis.cache_hit_rate
                }
            }
            
        except Exception as e:
            self.logger.error(f"Analysis retrieval failed: {str(e)}")
            return None
    
    def bulk_update_analysis_progress(self, updates: List[Dict]) -> bool:
        """Efficiently update multiple analysis records"""
        
        try:
            # Use bulk update for better performance
            for update in updates:
                db.session.query(Analysis).filter(
                    Analysis.id == update['analysis_id']
                ).update({
                    'progress': update.get('progress'),
                    'status': update.get('status'),
                    'status_message': update.get('status_message')
                })
            
            db.session.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Bulk update failed: {str(e)}")
            db.session.rollback()
            return False
    
    def cleanup_old_analyses(self, days_old: int = 30) -> int:
        """Clean up old completed analyses to maintain performance"""
        
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old completed analyses
            deleted_count = db.session.query(Analysis).filter(
                Analysis.status == 'completed',
                Analysis.completed_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old analyses")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            db.session.rollback()
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        
        try:
            # Get table sizes
            table_stats = {}
            
            if 'postgresql' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                # PostgreSQL specific queries
                result = db.session.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation
                    FROM pg_stats 
                    WHERE schemaname = 'public'
                    ORDER BY tablename, attname;
                """))
                
                for row in result:
                    table_name = row[1]
                    if table_name not in table_stats:
                        table_stats[table_name] = {'columns': []}
                    table_stats[table_name]['columns'].append({
                        'name': row[2],
                        'distinct_values': row[3],
                        'correlation': row[4]
                    })
            
            return {
                'query_stats': self.query_stats,
                'table_stats': table_stats,
                'connection_pool_info': self._get_pool_info()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {str(e)}")
            return {'error': str(e)}
    
    def _get_pool_info(self) -> Dict[str, Any]:
        """Get connection pool information"""
        
        try:
            engine = db.engine
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
            
        except Exception as e:
            self.logger.warning(f"Could not get pool info: {str(e)}")
            return {}
    
    @contextmanager
    def optimized_session(self):
        """Context manager for optimized database sessions"""
        
        session = db.session
        try:
            # Configure session for optimal performance
            session.execute(text("SET statement_timeout = '30s'"))  # PostgreSQL
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def create_missing_indexes(self):
        """Create missing database indexes for performance"""
        
        indexes_to_create = [
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_id_status ON analyses(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at_desc ON analyses(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_analyses_brand_name ON analyses(brand_name)",
            "CREATE INDEX IF NOT EXISTS idx_brands_name_lower ON brands(LOWER(name))",
            "CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_reports_analysis_id ON reports(analysis_id)"
        ]
        
        created_count = 0
        for index_sql in indexes_to_create:
            try:
                db.session.execute(text(index_sql))
                created_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to create index: {str(e)}")
        
        try:
            db.session.commit()
            self.logger.info(f"Created {created_count} database indexes")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to commit indexes: {str(e)}")


# Global instance
db_optimizer = DatabaseOptimizationService()
