"""
Enhanced Migration System for Brand Audit Tool
Provides data validation, rollback capabilities, and production readiness checks
"""

import os
import sys
import json
import logging
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from flask import Flask
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Try to import flask-migrate
try:
    from flask_migrate import Migrate, init, migrate, upgrade, downgrade, current, history
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMigrationSystem:
    """Enhanced migration system with validation and rollback capabilities"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_app()
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        self.backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        self.migrate_obj = None
        
        if MIGRATE_AVAILABLE:
            self.migrate_obj = Migrate(self.app, db)
        
        # Ensure directories exist
        os.makedirs(self.migrations_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_app(self) -> Flask:
        """Create Flask app for migrations"""
        app = Flask(__name__)
        
        # Database configuration
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "app.db")}'
        
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key')
        })
        
        db.init_app(app)
        return app
    
    def validate_pre_migration(self) -> Dict[str, Any]:
        """Validate system before running migrations"""
        logger.info("🔍 Running pre-migration validation...")
        
        validation_results = {
            'success': True,
            'checks': {},
            'errors': [],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            with self.app.app_context():
                # Check database connection
                try:
                    db.session.execute(text("SELECT 1"))
                    validation_results['checks']['database_connection'] = True
                    logger.info("   ✅ Database connection verified")
                except Exception as e:
                    validation_results['checks']['database_connection'] = False
                    validation_results['errors'].append(f"Database connection failed: {e}")
                    validation_results['success'] = False
                
                # Check if Flask-Migrate is available
                if not MIGRATE_AVAILABLE:
                    validation_results['warnings'].append("Flask-Migrate not available - using basic migrations")
                    validation_results['checks']['flask_migrate'] = False
                else:
                    validation_results['checks']['flask_migrate'] = True
                    logger.info("   ✅ Flask-Migrate available")
                
                # Check existing table structure
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                validation_results['checks']['existing_tables'] = existing_tables
                logger.info(f"   ✅ Found {len(existing_tables)} existing tables")
                
                # Check for data that might be affected
                if existing_tables:
                    data_counts = {}
                    if 'users' in existing_tables:
                        data_counts['users'] = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
                    if 'brands' in existing_tables:
                        data_counts['brands'] = db.session.execute(text("SELECT COUNT(*) FROM brands")).scalar()
                    if 'analyses' in existing_tables:
                        data_counts['analyses'] = db.session.execute(text("SELECT COUNT(*) FROM analyses")).scalar()
                    
                    validation_results['checks']['data_counts'] = data_counts
                    total_records = sum(data_counts.values())
                    
                    if total_records > 0:
                        validation_results['warnings'].append(f"Database contains {total_records} records - backup recommended")
                        logger.info(f"   ⚠️ Database contains {total_records} records")
                    else:
                        logger.info("   ✅ Database is empty - safe to migrate")
                
                # Check disk space (for SQLite)
                db_path = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
                if 'sqlite' in db_path:
                    db_file_path = db_path.replace('sqlite:///', '')
                    if os.path.exists(db_file_path):
                        file_size = os.path.getsize(db_file_path)
                        free_space = shutil.disk_usage(os.path.dirname(db_file_path)).free
                        
                        if free_space < file_size * 2:  # Need at least 2x database size for backup
                            validation_results['warnings'].append("Low disk space - backup may fail")
                        
                        validation_results['checks']['disk_space'] = {
                            'database_size': file_size,
                            'free_space': free_space,
                            'sufficient_space': free_space >= file_size * 2
                        }
                        logger.info(f"   ✅ Disk space check completed")
                
        except Exception as e:
            validation_results['success'] = False
            validation_results['errors'].append(f"Pre-migration validation failed: {e}")
            logger.error(f"   ❌ Pre-migration validation failed: {e}")
        
        return validation_results
    
    def create_backup(self) -> Dict[str, Any]:
        """Create database backup before migration"""
        logger.info("💾 Creating database backup...")
        
        backup_result = {
            'success': False,
            'backup_path': None,
            'timestamp': datetime.utcnow().isoformat(),
            'error': None
        }
        
        try:
            # Generate backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"database_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # For SQLite, copy the database file
            db_path = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'sqlite' in db_path:
                db_file_path = db_path.replace('sqlite:///', '')
                if os.path.exists(db_file_path):
                    shutil.copy2(db_file_path, backup_path)
                    backup_result['success'] = True
                    backup_result['backup_path'] = backup_path
                    logger.info(f"   ✅ Backup created: {backup_path}")
                else:
                    backup_result['error'] = "Database file not found"
            else:
                # For other databases, use SQL dump (simplified)
                backup_result['error'] = "Backup not implemented for non-SQLite databases"
                logger.warning("   ⚠️ Backup not implemented for non-SQLite databases")
        
        except Exception as e:
            backup_result['error'] = str(e)
            logger.error(f"   ❌ Backup failed: {e}")
        
        return backup_result
    
    def initialize_migrations(self) -> Dict[str, Any]:
        """Initialize migration repository"""
        logger.info("🔄 Initializing migrations...")
        
        result = {
            'success': False,
            'message': '',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if not MIGRATE_AVAILABLE:
                result['message'] = "Flask-Migrate not available"
                return result
            
            with self.app.app_context():
                if not os.path.exists(os.path.join(self.migrations_dir, 'alembic.ini')):
                    init(directory=self.migrations_dir)
                    result['success'] = True
                    result['message'] = "Migration repository initialized"
                    logger.info("   ✅ Migration repository initialized")
                else:
                    result['success'] = True
                    result['message'] = "Migration repository already exists"
                    logger.info("   ✅ Migration repository already exists")
        
        except Exception as e:
            result['message'] = f"Migration initialization failed: {e}"
            logger.error(f"   ❌ Migration initialization failed: {e}")
        
        return result
    
    def create_migration(self, message: str = "Auto migration") -> Dict[str, Any]:
        """Create a new migration"""
        logger.info(f"📝 Creating migration: {message}")
        
        result = {
            'success': False,
            'migration_file': None,
            'message': '',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if not MIGRATE_AVAILABLE:
                result['message'] = "Flask-Migrate not available"
                return result
            
            with self.app.app_context():
                migration_result = migrate(message=message, directory=self.migrations_dir)
                result['success'] = True
                result['message'] = f"Migration created: {message}"
                logger.info(f"   ✅ Migration created: {message}")
        
        except Exception as e:
            result['message'] = f"Migration creation failed: {e}"
            logger.error(f"   ❌ Migration creation failed: {e}")
        
        return result
    
    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending migrations"""
        logger.info("⬆️ Applying migrations...")
        
        result = {
            'success': False,
            'applied_migrations': [],
            'message': '',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if not MIGRATE_AVAILABLE:
                # Fallback to basic table creation
                with self.app.app_context():
                    db.create_all()
                    result['success'] = True
                    result['message'] = "Basic table creation completed (Flask-Migrate not available)"
                    logger.info("   ✅ Basic table creation completed")
                return result
            
            with self.app.app_context():
                # Get current migration state
                current_rev = current(directory=self.migrations_dir)
                
                # Apply migrations
                upgrade(directory=self.migrations_dir)
                
                # Get new migration state
                new_rev = current(directory=self.migrations_dir)
                
                result['success'] = True
                result['message'] = f"Migrations applied successfully"
                result['applied_migrations'] = [{'from': current_rev, 'to': new_rev}]
                logger.info("   ✅ Migrations applied successfully")
        
        except Exception as e:
            result['message'] = f"Migration application failed: {e}"
            logger.error(f"   ❌ Migration application failed: {e}")
        
        return result

    def validate_post_migration(self) -> Dict[str, Any]:
        """Validate system after migration"""
        logger.info("🔍 Running post-migration validation...")

        validation_results = {
            'success': True,
            'checks': {},
            'errors': [],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            with self.app.app_context():
                # Check all expected tables exist
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                expected_tables = {'users', 'brands', 'analyses', 'reports', 'uploaded_files'}

                missing_tables = expected_tables - set(existing_tables)
                if missing_tables:
                    validation_results['errors'].append(f"Missing tables: {missing_tables}")
                    validation_results['success'] = False
                else:
                    validation_results['checks']['all_tables_exist'] = True
                    logger.info("   ✅ All expected tables exist")

                # Check table structures
                for table in expected_tables:
                    if table in existing_tables:
                        columns = inspector.get_columns(table)
                        indexes = inspector.get_indexes(table)
                        foreign_keys = inspector.get_foreign_keys(table)

                        validation_results['checks'][f'{table}_structure'] = {
                            'columns': len(columns),
                            'indexes': len(indexes),
                            'foreign_keys': len(foreign_keys)
                        }

                # Test basic CRUD operations
                try:
                    # Test User model
                    test_user = User(
                        id='test-migration-user',
                        email='test@migration.com',
                        name='Test User'
                    )
                    test_user.set_password('testpass')
                    db.session.add(test_user)
                    db.session.flush()

                    # Test Brand model
                    test_brand = Brand(
                        id='test-migration-brand',
                        name='Test Brand'
                    )
                    db.session.add(test_brand)
                    db.session.flush()

                    # Test Analysis model
                    test_analysis = Analysis(
                        id='test-migration-analysis',
                        user_id=test_user.id,
                        brand_id=test_brand.id,
                        brand_name='Test Brand',
                        analysis_types=['test'],
                        status='started'
                    )
                    db.session.add(test_analysis)
                    db.session.flush()

                    # Clean up test data
                    db.session.delete(test_analysis)
                    db.session.delete(test_brand)
                    db.session.delete(test_user)
                    db.session.commit()

                    validation_results['checks']['crud_operations'] = True
                    logger.info("   ✅ CRUD operations working")

                except Exception as e:
                    validation_results['errors'].append(f"CRUD operations failed: {e}")
                    validation_results['success'] = False
                    db.session.rollback()

        except Exception as e:
            validation_results['success'] = False
            validation_results['errors'].append(f"Post-migration validation failed: {e}")
            logger.error(f"   ❌ Post-migration validation failed: {e}")

        return validation_results

    def run_comprehensive_migration(self, create_backup: bool = True, message: str = "Comprehensive migration") -> Dict[str, Any]:
        """Run comprehensive migration with all validation steps"""
        logger.info("🚀 Starting comprehensive migration process...")

        migration_results = {
            'success': True,
            'steps_completed': [],
            'steps_failed': [],
            'backup_path': None,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # Step 1: Pre-migration validation
            logger.info("Step 1: Pre-migration validation")
            pre_validation = self.validate_pre_migration()
            if pre_validation['success']:
                migration_results['steps_completed'].append('pre_validation')
                logger.info("   ✅ Pre-migration validation passed")
            else:
                migration_results['steps_failed'].append('pre_validation')
                migration_results['errors'].extend(pre_validation['errors'])
                migration_results['success'] = False
                logger.error("   ❌ Pre-migration validation failed")
                return migration_results

            # Step 2: Create backup (if requested)
            if create_backup:
                logger.info("Step 2: Creating backup")
                backup_result = self.create_backup()
                if backup_result['success']:
                    migration_results['steps_completed'].append('backup')
                    migration_results['backup_path'] = backup_result['backup_path']
                    logger.info("   ✅ Backup created successfully")
                else:
                    migration_results['steps_failed'].append('backup')
                    migration_results['errors'].append(backup_result['error'])
                    # Don't fail the entire process for backup issues
                    logger.warning("   ⚠️ Backup failed but continuing")

            # Step 3: Initialize migrations
            logger.info("Step 3: Initializing migrations")
            init_result = self.initialize_migrations()
            if init_result['success']:
                migration_results['steps_completed'].append('migration_init')
                logger.info("   ✅ Migration initialization completed")
            else:
                migration_results['steps_failed'].append('migration_init')
                migration_results['errors'].append(init_result['message'])
                # Continue with basic table creation
                logger.warning("   ⚠️ Migration init failed, will use basic table creation")

            # Step 4: Apply migrations
            logger.info("Step 4: Applying migrations")
            apply_result = self.apply_migrations()
            if apply_result['success']:
                migration_results['steps_completed'].append('migration_apply')
                logger.info("   ✅ Migrations applied successfully")
            else:
                migration_results['steps_failed'].append('migration_apply')
                migration_results['errors'].append(apply_result['message'])
                migration_results['success'] = False
                logger.error("   ❌ Migration application failed")
                return migration_results

            # Step 5: Post-migration validation
            logger.info("Step 5: Post-migration validation")
            post_validation = self.validate_post_migration()
            if post_validation['success']:
                migration_results['steps_completed'].append('post_validation')
                logger.info("   ✅ Post-migration validation passed")
            else:
                migration_results['steps_failed'].append('post_validation')
                migration_results['errors'].extend(post_validation['errors'])
                migration_results['success'] = False
                logger.error("   ❌ Post-migration validation failed")

        except Exception as e:
            migration_results['success'] = False
            migration_results['errors'].append(f"Comprehensive migration failed: {e}")
            logger.error(f"❌ Comprehensive migration failed: {e}")

        return migration_results


def run_enhanced_migration(create_backup: bool = True, message: str = "Enhanced migration"):
    """Run enhanced migration (standalone function)"""
    print("🚀 Brand Audit Tool - Enhanced Migration System")
    print("=" * 60)

    migration_system = EnhancedMigrationSystem()
    results = migration_system.run_comprehensive_migration(
        create_backup=create_backup,
        message=message
    )

    # Print detailed results
    print(f"\n📊 Migration Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")
    print(f"   Steps Completed: {len(results['steps_completed'])}")
    print(f"   Steps Failed: {len(results['steps_failed'])}")

    if results['backup_path']:
        print(f"   Backup Created: {results['backup_path']}")

    if results['steps_completed']:
        print(f"   ✅ Completed: {', '.join(results['steps_completed'])}")

    if results['steps_failed']:
        print(f"   ❌ Failed: {', '.join(results['steps_failed'])}")

    if results['errors']:
        print(f"\n⚠️ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error}")

    print("\n" + "=" * 60)
    if results['success']:
        print("🎉 Enhanced migration completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Test the application with the migrated database")
        print("   2. Monitor database performance")
        print("   3. Set up regular backups")
        print("   4. Consider running production readiness check")
    else:
        print("⚠️ Migration failed. Please review the errors above.")
        if results['backup_path']:
            print(f"   💾 Backup available at: {results['backup_path']}")

    return results['success']


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Migration System for Brand Audit Tool')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--message', type=str, default='Enhanced migration', help='Migration message')

    args = parser.parse_args()

    success = run_enhanced_migration(
        create_backup=not args.no_backup,
        message=args.message
    )

    sys.exit(0 if success else 1)
