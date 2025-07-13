"""
Comprehensive Database System Integration for Brand Audit Tool
Integrates all database components: initialization, validation, health checks, and migrations
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.extensions import db
from src.database.init_db import DatabaseInitializer
from src.database.model_relationship_tests import ModelRelationshipTester
from src.database.crud_validation_tests import CRUDValidationTester
from src.database.sample_data_generator import SampleDataGenerator
from src.database.health_check_system import DatabaseHealthChecker, create_health_check_blueprint
from src.database.migration_system import EnhancedMigrationSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveDatabaseSystem:
    """Comprehensive database system that integrates all components"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_app()
        
        # Initialize all subsystems
        self.initializer = DatabaseInitializer(self.app)
        self.relationship_tester = ModelRelationshipTester(self.app)
        self.crud_tester = CRUDValidationTester(self.app)
        self.data_generator = SampleDataGenerator(self.app)
        self.health_checker = DatabaseHealthChecker(self.app)
        self.migration_system = EnhancedMigrationSystem(self.app)
        
        self.system_status = {}
    
    def create_app(self) -> Flask:
        """Create Flask app for the comprehensive system"""
        app = Flask(__name__)
        
        # Database configuration
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "app.db")}'
        
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {'check_same_thread': False} if 'sqlite' in database_url else {}
            },
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key')
        })
        
        db.init_app(app)
        return app
    
    def setup_production_database(self, 
                                 create_backup: bool = True,
                                 generate_sample_data: bool = False,
                                 run_full_validation: bool = True) -> Dict[str, Any]:
        """Complete production database setup"""
        logger.info("🚀 Starting comprehensive production database setup...")
        
        setup_results = {
            'success': True,
            'components': {},
            'errors': [],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat(),
            'recommendations': []
        }
        
        try:
            # Step 1: Run comprehensive migration
            logger.info("Step 1: Database Migration")
            migration_results = self.migration_system.run_comprehensive_migration(
                create_backup=create_backup,
                message="Production setup migration"
            )
            setup_results['components']['migration'] = migration_results
            
            if not migration_results['success']:
                setup_results['success'] = False
                setup_results['errors'].extend(migration_results['errors'])
                logger.error("   ❌ Migration failed - stopping setup")
                return setup_results
            
            logger.info("   ✅ Migration completed successfully")
            
            # Step 2: Run full validation if requested
            if run_full_validation:
                logger.info("Step 2: Full System Validation")
                
                # Model relationship tests
                relationship_results = self.relationship_tester.run_comprehensive_tests()
                setup_results['components']['relationship_tests'] = relationship_results
                
                if not relationship_results['success']:
                    setup_results['warnings'].append("Model relationship tests failed")
                    logger.warning("   ⚠️ Model relationship tests failed")
                else:
                    logger.info("   ✅ Model relationship tests passed")
                
                # CRUD validation tests
                crud_results = self.crud_tester.run_comprehensive_crud_tests()
                setup_results['components']['crud_tests'] = crud_results
                
                if not crud_results['success']:
                    setup_results['warnings'].append("CRUD validation tests failed")
                    logger.warning("   ⚠️ CRUD validation tests failed")
                else:
                    logger.info("   ✅ CRUD validation tests passed")
            
            # Step 3: Generate sample data if requested
            if generate_sample_data:
                logger.info("Step 3: Sample Data Generation")
                data_results = self.data_generator.generate_comprehensive_sample_data()
                setup_results['components']['sample_data'] = data_results
                
                if not data_results['success']:
                    setup_results['warnings'].append("Sample data generation failed")
                    logger.warning("   ⚠️ Sample data generation failed")
                else:
                    logger.info("   ✅ Sample data generated successfully")
            
            # Step 4: Health check
            logger.info("Step 4: System Health Check")
            health_results = self.health_checker.run_comprehensive_health_check()
            setup_results['components']['health_check'] = health_results
            
            if health_results['overall_status'] == 'unhealthy':
                setup_results['warnings'].append("System health check shows issues")
                logger.warning("   ⚠️ System health check shows issues")
            else:
                logger.info("   ✅ System health check passed")
            
            # Add recommendations
            setup_results['recommendations'].extend(health_results.get('recommendations', []))
            
            # Store system status
            self.system_status = setup_results
            
        except Exception as e:
            setup_results['success'] = False
            setup_results['errors'].append(f"Production setup failed: {e}")
            logger.error(f"❌ Production setup failed: {e}")
        
        return setup_results
    
    def run_maintenance_tasks(self) -> Dict[str, Any]:
        """Run routine maintenance tasks"""
        logger.info("🔧 Running database maintenance tasks...")
        
        maintenance_results = {
            'success': True,
            'tasks_completed': [],
            'tasks_failed': [],
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Health check
            health_results = self.health_checker.run_comprehensive_health_check()
            if health_results['overall_status'] != 'unhealthy':
                maintenance_results['tasks_completed'].append('health_check')
                logger.info("   ✅ Health check completed")
            else:
                maintenance_results['tasks_failed'].append('health_check')
                maintenance_results['errors'].append("Health check failed")
                logger.error("   ❌ Health check failed")
            
            # Data consistency check
            consistency_check = self.health_checker.check_data_consistency()
            if consistency_check['status'] != 'unhealthy':
                maintenance_results['tasks_completed'].append('consistency_check')
                logger.info("   ✅ Data consistency check completed")
            else:
                maintenance_results['tasks_failed'].append('consistency_check')
                maintenance_results['errors'].append("Data consistency issues found")
                logger.warning("   ⚠️ Data consistency issues found")
            
            # Performance check
            performance_check = self.health_checker.check_performance_metrics()
            if performance_check['status'] in ['excellent', 'good', 'acceptable']:
                maintenance_results['tasks_completed'].append('performance_check')
                logger.info("   ✅ Performance check completed")
            else:
                maintenance_results['tasks_failed'].append('performance_check')
                maintenance_results['errors'].append("Performance issues detected")
                logger.warning("   ⚠️ Performance issues detected")
            
            # Backup creation
            backup_result = self.migration_system.create_backup()
            if backup_result['success']:
                maintenance_results['tasks_completed'].append('backup_creation')
                logger.info("   ✅ Backup created")
            else:
                maintenance_results['tasks_failed'].append('backup_creation')
                maintenance_results['errors'].append(f"Backup failed: {backup_result['error']}")
                logger.error("   ❌ Backup creation failed")
            
            if maintenance_results['tasks_failed']:
                maintenance_results['success'] = False
        
        except Exception as e:
            maintenance_results['success'] = False
            maintenance_results['errors'].append(f"Maintenance tasks failed: {e}")
            logger.error(f"❌ Maintenance tasks failed: {e}")
        
        return maintenance_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.system_status:
            # Run a quick health check if no status available
            health_results = self.health_checker.run_comprehensive_health_check()
            return {
                'status': health_results['overall_status'],
                'timestamp': health_results['timestamp'],
                'quick_check': True,
                'details': health_results
            }
        
        return {
            'status': 'healthy' if self.system_status['success'] else 'issues',
            'timestamp': self.system_status['timestamp'],
            'quick_check': False,
            'details': self.system_status
        }
    
    def register_health_endpoints(self) -> None:
        """Register health check endpoints with the Flask app"""
        health_bp = create_health_check_blueprint(self.app)
        self.app.register_blueprint(health_bp)
        logger.info("✅ Health check endpoints registered")


def setup_production_database_cli():
    """CLI function for production database setup"""
    print("🚀 Brand Audit Tool - Comprehensive Database Setup")
    print("=" * 60)
    
    system = ComprehensiveDatabaseSystem()
    
    # Run production setup
    results = system.setup_production_database(
        create_backup=True,
        generate_sample_data=False,  # Don't generate sample data in production
        run_full_validation=True
    )
    
    # Print results
    print(f"\n📊 Setup Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")
    print(f"   Components: {len(results['components'])}")
    
    if results['errors']:
        print(f"   Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"     - {error}")
    
    if results['warnings']:
        print(f"   Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"     - {warning}")
    
    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
    
    print("\n" + "=" * 60)
    if results['success']:
        print("🎉 Production database setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start the Flask application")
        print("   2. Test all endpoints")
        print("   3. Monitor system health at /api/health")
        print("   4. Set up regular maintenance tasks")
    else:
        print("❌ Production database setup failed!")
        print("   Please review the errors above and try again.")
    
    return results['success']


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Database System for Brand Audit Tool')
    parser.add_argument('--maintenance', action='store_true', help='Run maintenance tasks instead of setup')
    parser.add_argument('--sample-data', action='store_true', help='Generate sample data during setup')
    
    args = parser.parse_args()
    
    if args.maintenance:
        system = ComprehensiveDatabaseSystem()
        results = system.run_maintenance_tasks()
        success = results['success']
        print(f"Maintenance {'completed' if success else 'failed'}")
    else:
        success = setup_production_database_cli()
    
    sys.exit(0 if success else 1)
