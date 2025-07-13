"""
Database Health Check System for Brand Audit Tool
Comprehensive monitoring and health checking for database operations and performance
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask, jsonify, Blueprint
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Comprehensive database health checking system"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.health_status = {}
        self.performance_metrics = {}
        
    def check_database_connection(self) -> Dict[str, Any]:
        """Check basic database connectivity"""
        start_time = time.time()
        
        try:
            with self.app.app_context():
                # Test basic connection
                db.session.execute(text("SELECT 1"))
                
                # Test transaction capability
                db.session.begin()
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': 'Database connection and transactions working normally'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'response_time_ms': (time.time() - start_time) * 1000,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': 'Database connection failed'
            }
    
    def check_table_integrity(self) -> Dict[str, Any]:
        """Check table structure and integrity"""
        try:
            with self.app.app_context():
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                expected_tables = {'users', 'brands', 'analyses', 'reports', 'uploaded_files'}
                missing_tables = expected_tables - set(tables)
                extra_tables = set(tables) - expected_tables
                
                table_details = {}
                for table in expected_tables:
                    if table in tables:
                        columns = inspector.get_columns(table)
                        indexes = inspector.get_indexes(table)
                        foreign_keys = inspector.get_foreign_keys(table)
                        
                        table_details[table] = {
                            'exists': True,
                            'column_count': len(columns),
                            'index_count': len(indexes),
                            'foreign_key_count': len(foreign_keys)
                        }
                    else:
                        table_details[table] = {'exists': False}
                
                status = 'healthy' if not missing_tables else 'unhealthy'
                
                return {
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'table_count': len(tables),
                    'expected_tables': len(expected_tables),
                    'missing_tables': list(missing_tables),
                    'extra_tables': list(extra_tables),
                    'table_details': table_details,
                    'details': f'Found {len(tables)} tables, expected {len(expected_tables)}'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': 'Table integrity check failed'
            }
    
    def check_data_consistency(self) -> Dict[str, Any]:
        """Check data consistency and relationships"""
        try:
            with self.app.app_context():
                issues = []
                
                # Check for orphaned analyses (analyses without valid brands)
                orphaned_analyses = db.session.query(Analysis).filter(
                    ~Analysis.brand_id.in_(db.session.query(Brand.id))
                ).count()
                
                if orphaned_analyses > 0:
                    issues.append(f"{orphaned_analyses} analyses with invalid brand references")
                
                # Check for orphaned reports (reports without valid analyses)
                orphaned_reports = db.session.query(Report).filter(
                    ~Report.analysis_id.in_(db.session.query(Analysis.id))
                ).count()
                
                if orphaned_reports > 0:
                    issues.append(f"{orphaned_reports} reports with invalid analysis references")
                
                # Check for orphaned uploaded files (files without valid users or analyses)
                orphaned_files_user = db.session.query(UploadedFile).filter(
                    ~UploadedFile.user_id.in_(db.session.query(User.id))
                ).count()
                
                orphaned_files_analysis = db.session.query(UploadedFile).filter(
                    UploadedFile.analysis_id.isnot(None),
                    ~UploadedFile.analysis_id.in_(db.session.query(Analysis.id))
                ).count()
                
                if orphaned_files_user > 0:
                    issues.append(f"{orphaned_files_user} uploaded files with invalid user references")
                
                if orphaned_files_analysis > 0:
                    issues.append(f"{orphaned_files_analysis} uploaded files with invalid analysis references")
                
                # Check for analyses with completed status but no results
                incomplete_completed = Analysis.query.filter(
                    Analysis.status == 'completed',
                    Analysis.results.is_(None)
                ).count()
                
                if incomplete_completed > 0:
                    issues.append(f"{incomplete_completed} completed analyses without results")
                
                status = 'healthy' if not issues else 'warning'
                
                return {
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'issues_found': len(issues),
                    'issues': issues,
                    'checks_performed': [
                        'orphaned_analyses',
                        'orphaned_reports', 
                        'orphaned_files',
                        'incomplete_completed_analyses'
                    ],
                    'details': f'Data consistency check completed with {len(issues)} issues'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': 'Data consistency check failed'
            }
    
    def check_performance_metrics(self) -> Dict[str, Any]:
        """Check database performance metrics"""
        try:
            with self.app.app_context():
                metrics = {}
                
                # Query response times
                start_time = time.time()
                user_count = User.query.count()
                metrics['user_count_query_time'] = (time.time() - start_time) * 1000
                
                start_time = time.time()
                brand_count = Brand.query.count()
                metrics['brand_count_query_time'] = (time.time() - start_time) * 1000
                
                start_time = time.time()
                analysis_count = Analysis.query.count()
                metrics['analysis_count_query_time'] = (time.time() - start_time) * 1000
                
                # Complex query performance
                start_time = time.time()
                recent_analyses = Analysis.query.order_by(Analysis.created_at.desc()).limit(10).all()
                metrics['recent_analyses_query_time'] = (time.time() - start_time) * 1000
                
                # Join query performance
                start_time = time.time()
                analyses_with_brands = db.session.query(Analysis, Brand).join(Brand).limit(10).all()
                metrics['join_query_time'] = (time.time() - start_time) * 1000
                
                # Calculate average response time
                avg_response_time = sum(metrics.values()) / len(metrics)
                
                # Determine performance status
                if avg_response_time < 100:  # Less than 100ms average
                    status = 'excellent'
                elif avg_response_time < 500:  # Less than 500ms average
                    status = 'good'
                elif avg_response_time < 1000:  # Less than 1s average
                    status = 'acceptable'
                else:
                    status = 'poor'
                
                return {
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'average_response_time_ms': round(avg_response_time, 2),
                    'metrics': {k: round(v, 2) for k, v in metrics.items()},
                    'record_counts': {
                        'users': user_count,
                        'brands': brand_count,
                        'analyses': analysis_count,
                        'reports': Report.query.count(),
                        'uploaded_files': UploadedFile.query.count()
                    },
                    'details': f'Performance check completed with {status} results'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': 'Performance metrics check failed'
            }
    
    def check_storage_usage(self) -> Dict[str, Any]:
        """Check database storage usage and growth"""
        try:
            with self.app.app_context():
                # Get database file size (for SQLite)
                db_path = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
                
                storage_info = {
                    'database_type': 'sqlite' if 'sqlite' in db_path else 'other',
                    'database_path': db_path.replace('sqlite:///', '') if 'sqlite' in db_path else 'N/A'
                }
                
                if 'sqlite' in db_path:
                    db_file_path = db_path.replace('sqlite:///', '')
                    if os.path.exists(db_file_path):
                        file_size = os.path.getsize(db_file_path)
                        storage_info.update({
                            'database_size_bytes': file_size,
                            'database_size_mb': round(file_size / (1024 * 1024), 2),
                            'file_exists': True
                        })
                    else:
                        storage_info.update({
                            'database_size_bytes': 0,
                            'database_size_mb': 0,
                            'file_exists': False
                        })
                
                # Estimate record sizes
                record_counts = {
                    'users': User.query.count(),
                    'brands': Brand.query.count(),
                    'analyses': Analysis.query.count(),
                    'reports': Report.query.count(),
                    'uploaded_files': UploadedFile.query.count()
                }
                
                total_records = sum(record_counts.values())
                
                return {
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'storage_info': storage_info,
                    'record_counts': record_counts,
                    'total_records': total_records,
                    'estimated_avg_record_size': round(storage_info.get('database_size_bytes', 0) / max(total_records, 1), 2),
                    'details': f'Storage usage check completed for {total_records} total records'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': 'Storage usage check failed'
            }

    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        logger.info("🏥 Running comprehensive database health check...")

        start_time = time.time()

        # Run all health checks
        connection_check = self.check_database_connection()
        table_check = self.check_table_integrity()
        consistency_check = self.check_data_consistency()
        performance_check = self.check_performance_metrics()
        storage_check = self.check_storage_usage()

        total_time = (time.time() - start_time) * 1000

        # Determine overall health status
        checks = [connection_check, table_check, consistency_check, performance_check, storage_check]
        unhealthy_checks = [c for c in checks if c['status'] == 'unhealthy']
        warning_checks = [c for c in checks if c['status'] == 'warning']

        if unhealthy_checks:
            overall_status = 'unhealthy'
        elif warning_checks:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'

        # Compile comprehensive report
        health_report = {
            'overall_status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'total_check_time_ms': round(total_time, 2),
            'checks': {
                'connection': connection_check,
                'table_integrity': table_check,
                'data_consistency': consistency_check,
                'performance': performance_check,
                'storage': storage_check
            },
            'summary': {
                'total_checks': len(checks),
                'healthy_checks': len([c for c in checks if c['status'] == 'healthy']),
                'warning_checks': len(warning_checks),
                'unhealthy_checks': len(unhealthy_checks)
            },
            'recommendations': self._generate_recommendations(checks)
        }

        # Store for monitoring
        self.health_status = health_report

        logger.info(f"✅ Health check completed: {overall_status}")
        return health_report

    def _generate_recommendations(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []

        for check in checks:
            if check['status'] == 'unhealthy':
                if 'connection' in str(check.get('details', '')):
                    recommendations.append("Check database connection settings and network connectivity")
                elif 'table' in str(check.get('details', '')):
                    recommendations.append("Run database migration to ensure all tables exist")
                elif 'consistency' in str(check.get('details', '')):
                    recommendations.append("Run data cleanup to fix orphaned records")
                elif 'performance' in str(check.get('details', '')):
                    recommendations.append("Consider database optimization or indexing")
                elif 'storage' in str(check.get('details', '')):
                    recommendations.append("Check database file permissions and disk space")

            elif check['status'] == 'warning':
                if 'consistency' in str(check.get('details', '')):
                    recommendations.append("Schedule data cleanup to maintain consistency")
                elif 'performance' in str(check.get('details', '')):
                    recommendations.append("Monitor database performance and consider optimization")

        # Add general recommendations
        if not recommendations:
            recommendations.append("Database is healthy - continue regular monitoring")

        return recommendations

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a quick health summary"""
        if not self.health_status:
            return {'status': 'unknown', 'message': 'No health check performed yet'}

        return {
            'status': self.health_status['overall_status'],
            'timestamp': self.health_status['timestamp'],
            'total_checks': self.health_status['summary']['total_checks'],
            'healthy_checks': self.health_status['summary']['healthy_checks'],
            'issues': self.health_status['summary']['warning_checks'] + self.health_status['summary']['unhealthy_checks']
        }


# Flask Blueprint for health check endpoints
def create_health_check_blueprint(app: Flask) -> Blueprint:
    """Create Flask blueprint for health check endpoints"""

    health_bp = Blueprint('health', __name__, url_prefix='/api/health')
    health_checker = DatabaseHealthChecker(app)

    @health_bp.route('/', methods=['GET'])
    def health_check():
        """Quick health check endpoint"""
        try:
            summary = health_checker.get_health_summary()
            if summary['status'] == 'unknown':
                # Run a quick check
                connection_check = health_checker.check_database_connection()
                return jsonify({
                    'status': connection_check['status'],
                    'timestamp': connection_check['timestamp'],
                    'message': 'Quick health check completed'
                })

            return jsonify(summary)

        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    @health_bp.route('/comprehensive', methods=['GET'])
    def comprehensive_health_check():
        """Comprehensive health check endpoint"""
        try:
            health_report = health_checker.run_comprehensive_health_check()

            # Return appropriate HTTP status code
            if health_report['overall_status'] == 'healthy':
                status_code = 200
            elif health_report['overall_status'] == 'warning':
                status_code = 200  # Still operational
            else:
                status_code = 503  # Service unavailable

            return jsonify(health_report), status_code

        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'message': 'Health check failed'
            }), 500

    @health_bp.route('/connection', methods=['GET'])
    def connection_check():
        """Database connection check endpoint"""
        try:
            result = health_checker.check_database_connection()
            status_code = 200 if result['status'] == 'healthy' else 503
            return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    @health_bp.route('/performance', methods=['GET'])
    def performance_check():
        """Database performance check endpoint"""
        try:
            result = health_checker.check_performance_metrics()
            return jsonify(result)

        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    @health_bp.route('/storage', methods=['GET'])
    def storage_check():
        """Database storage usage check endpoint"""
        try:
            result = health_checker.check_storage_usage()
            return jsonify(result)

        except Exception as e:
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    return health_bp


def run_health_check_cli():
    """Run health check from command line"""
    print("🏥 Brand Audit Tool - Database Health Check")
    print("=" * 50)

    # Create a minimal Flask app for testing
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    checker = DatabaseHealthChecker(app)
    health_report = checker.run_comprehensive_health_check()

    # Print results
    print(f"\n🎯 Overall Status: {health_report['overall_status'].upper()}")
    print(f"⏱️ Total Check Time: {health_report['total_check_time_ms']}ms")

    print(f"\n📊 Check Summary:")
    summary = health_report['summary']
    print(f"   ✅ Healthy: {summary['healthy_checks']}/{summary['total_checks']}")
    print(f"   ⚠️ Warnings: {summary['warning_checks']}")
    print(f"   ❌ Unhealthy: {summary['unhealthy_checks']}")

    print(f"\n🔍 Individual Checks:")
    for check_name, check_result in health_report['checks'].items():
        status_icon = "✅" if check_result['status'] == 'healthy' else "⚠️" if check_result['status'] == 'warning' else "❌"
        print(f"   {status_icon} {check_name.replace('_', ' ').title()}: {check_result['status']}")
        if 'error' in check_result:
            print(f"      Error: {check_result['error']}")

    if health_report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in health_report['recommendations']:
            print(f"   • {rec}")

    print("\n" + "=" * 50)
    if health_report['overall_status'] == 'healthy':
        print("🎉 Database is healthy!")
    elif health_report['overall_status'] == 'warning':
        print("⚠️ Database has some issues but is operational")
    else:
        print("❌ Database has critical issues that need attention")

    return health_report['overall_status'] == 'healthy'


if __name__ == "__main__":
    success = run_health_check_cli()
    sys.exit(0 if success else 1)
