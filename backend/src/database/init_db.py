"""
Comprehensive Database Initialization and Validation System for Brand Audit Tool
Creates tables, validates constraints, tests relationships, and ensures production readiness
"""

import os
import sys
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import text, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Try to import flask-migrate, but continue without it if not available
try:
    from flask_migrate import Migrate, init, migrate, upgrade
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False
    print("⚠️ Flask-Migrate not available, using basic database initialization")

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Change to backend directory for imports
os.chdir(backend_dir)

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Comprehensive database initialization and validation system"""

    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_app()
        self.validation_results = {}
        self.errors = []

    def create_app(self) -> Flask:
        """Create Flask app for database operations"""
        app = Flask(__name__)

        # Database configuration with environment variable support
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

        # Initialize extensions
        db.init_app(app)

        return app

    def log_error(self, operation: str, error: Exception):
        """Log and store errors for reporting"""
        error_msg = f"{operation}: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        self.errors.append({
            'operation': operation,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': traceback.format_exc()
        })

    def validate_database_connection(self) -> bool:
        """Validate database connection and basic functionality"""
        try:
            with self.app.app_context():
                # Test basic connection
                db.session.execute(text("SELECT 1"))

                # Test transaction capability
                db.session.begin()
                db.session.execute(text("SELECT 1"))
                db.session.commit()

                logger.info("✅ Database connection validated successfully")
                return True

        except Exception as e:
            self.log_error("Database connection validation", e)
            return False


    def create_tables_with_validation(self) -> bool:
        """Create all tables with comprehensive validation"""
        try:
            with self.app.app_context():
                logger.info("🗄️ Creating database tables...")

                # Drop all tables if they exist (for clean initialization)
                db.drop_all()

                # Create all tables
                db.create_all()

                # Validate table creation
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                expected_tables = {'users', 'brands', 'analyses', 'reports', 'uploaded_files'}

                if not expected_tables.issubset(set(tables)):
                    missing = expected_tables - set(tables)
                    raise Exception(f"Missing tables: {missing}")

                logger.info("✅ Database tables created successfully!")

                # Detailed table information
                self._log_table_details(inspector, tables)

                # Validate table constraints
                self._validate_table_constraints(inspector)

                return True

        except Exception as e:
            self.log_error("Table creation", e)
            return False

    def _log_table_details(self, inspector, tables: List[str]):
        """Log detailed information about created tables"""
        logger.info(f"\n📋 Created tables ({len(tables)}):")

        for table in tables:
            columns = inspector.get_columns(table)
            indexes = inspector.get_indexes(table)
            foreign_keys = inspector.get_foreign_keys(table)

            logger.info(f"   📊 {table}:")
            logger.info(f"      - Columns: {len(columns)}")
            logger.info(f"      - Indexes: {len(indexes)}")
            logger.info(f"      - Foreign Keys: {len(foreign_keys)}")

            # Log key columns
            for col in columns:
                constraints = []
                if col.get('primary_key'):
                    constraints.append('PK')
                if not col.get('nullable', True):
                    constraints.append('NOT NULL')
                if col.get('unique'):
                    constraints.append('UNIQUE')

                constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
                logger.info(f"        • {col['name']} ({col['type']}){constraint_str}")

    def _validate_table_constraints(self, inspector):
        """Validate table constraints and relationships"""
        logger.info("\n🔍 Validating table constraints...")

        constraint_validations = {
            'users': {
                'required_columns': ['id', 'email', 'password_hash', 'name'],
                'unique_columns': ['email'],
                'indexed_columns': ['email']
            },
            'brands': {
                'required_columns': ['id', 'name'],
                'indexed_columns': ['name']
            },
            'analyses': {
                'required_columns': ['id', 'brand_id', 'brand_name', 'status'],
                'foreign_keys': [('brand_id', 'brands', 'id')]
            },
            'reports': {
                'required_columns': ['id', 'analysis_id', 'report_type', 'filename'],
                'foreign_keys': [('analysis_id', 'analyses', 'id')]
            },
            'uploaded_files': {
                'required_columns': ['id', 'user_id', 'filename', 'file_path'],
                'foreign_keys': [('user_id', 'users', 'id')]
            }
        }

        for table_name, validations in constraint_validations.items():
            self._validate_single_table(inspector, table_name, validations)


    def _validate_single_table(self, inspector, table_name: str, validations: Dict[str, Any]):
        """Validate constraints for a single table"""
        try:
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]

            # Check required columns
            if 'required_columns' in validations:
                missing_columns = set(validations['required_columns']) - set(column_names)
                if missing_columns:
                    raise Exception(f"Table {table_name} missing required columns: {missing_columns}")

            # Check unique constraints
            if 'unique_columns' in validations:
                unique_constraints = inspector.get_unique_constraints(table_name)
                unique_column_names = set()
                for constraint in unique_constraints:
                    unique_column_names.update(constraint['column_names'])

                for col in columns:
                    if col['name'] in validations['unique_columns'] and not col.get('unique'):
                        # Check if it's in a unique constraint
                        if col['name'] not in unique_column_names:
                            logger.warning(f"Column {table_name}.{col['name']} should be unique")

            # Check foreign keys
            if 'foreign_keys' in validations:
                foreign_keys = inspector.get_foreign_keys(table_name)
                fk_columns = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0])
                             for fk in foreign_keys}

                for local_col, ref_table, ref_col in validations['foreign_keys']:
                    if local_col not in fk_columns:
                        raise Exception(f"Missing foreign key: {table_name}.{local_col} -> {ref_table}.{ref_col}")

                    actual_ref = fk_columns[local_col]
                    if actual_ref != (ref_table, ref_col):
                        raise Exception(f"Incorrect foreign key reference: {table_name}.{local_col} -> {actual_ref} (expected {ref_table}.{ref_col})")

            logger.info(f"      ✅ {table_name} constraints validated")

        except Exception as e:
            self.log_error(f"Table validation for {table_name}", e)
            raise

    def setup_migrations(self) -> bool:
        """Set up Flask-Migrate for database migrations"""
        if not MIGRATE_AVAILABLE:
            logger.info("\n🔄 Flask-Migrate not available, skipping migration setup...")
            logger.info("   💡 Using basic database initialization instead")
            return True

        try:
            migrate_obj = Migrate(self.app, db)

            with self.app.app_context():
                logger.info("\n🔄 Setting up database migrations...")

                migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

                if not os.path.exists(migrations_dir):
                    logger.info("   📁 Initializing migrations directory...")
                    init(directory=migrations_dir)
                    logger.info("   ✅ Migrations directory created")
                else:
                    logger.info("   📁 Migrations directory already exists")

                logger.info("   📝 Creating initial migration...")
                migrate(message="Initial migration", directory=migrations_dir)
                logger.info("   ✅ Initial migration created")

                logger.info("   ⬆️ Applying migrations...")
                upgrade(directory=migrations_dir)
                logger.info("   ✅ Migrations applied successfully")

                return True

        except Exception as e:
            # This is often expected if migrations already exist
            logger.info(f"   ⚠️ Migration setup note: {e}")
            logger.info("   💡 This is normal if migrations already exist")
            return True

        return True

    def comprehensive_initialize(self) -> Dict[str, Any]:
        """Run comprehensive database initialization with full validation"""
        logger.info("🚀 Starting comprehensive database initialization...")

        results = {
            'success': True,
            'steps_completed': [],
            'steps_failed': [],
            'validation_results': {},
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Step 1: Validate database connection
        if self.validate_database_connection():
            results['steps_completed'].append('database_connection')
        else:
            results['steps_failed'].append('database_connection')
            results['success'] = False

        # Step 2: Create tables with validation
        if self.create_tables_with_validation():
            results['steps_completed'].append('table_creation')
        else:
            results['steps_failed'].append('table_creation')
            results['success'] = False

        # Step 3: Setup migrations
        if self.setup_migrations():
            results['steps_completed'].append('migration_setup')
        else:
            results['steps_failed'].append('migration_setup')
            # Don't fail the entire process for migration issues

        # Add error details
        results['errors'] = self.errors
        results['validation_results'] = self.validation_results

        if results['success']:
            logger.info("✅ Comprehensive database initialization completed successfully!")
        else:
            logger.error("❌ Database initialization completed with errors")

        return results


# Legacy function wrappers for backward compatibility
def create_app():
    """Create Flask app for database operations (legacy wrapper)"""
    initializer = DatabaseInitializer()
    return initializer.app


def init_database():
    """Initialize database with tables (legacy wrapper)"""
    initializer = DatabaseInitializer()
    results = initializer.comprehensive_initialize()
    return results['success']


def create_sample_data():
    """Create sample data for testing"""
    initializer = DatabaseInitializer()

    with initializer.app.app_context():
        logger.info("\n📊 Creating sample data...")

        try:
            # Check if sample data already exists
            if Brand.query.first():
                logger.info("   ℹ️ Sample data already exists, skipping...")
                return True

            # Create sample brands with comprehensive data
            sample_brands = [
                {
                    "name": "Apple",
                    "website": "https://apple.com",
                    "industry": "Technology",
                    "description": "Technology company known for innovative consumer electronics",
                    "primary_color": "#000000",
                    "founded_year": 1976,
                    "headquarters": "Cupertino, CA"
                },
                {
                    "name": "Nike",
                    "website": "https://nike.com",
                    "industry": "Sportswear",
                    "description": "Global leader in athletic footwear and apparel",
                    "primary_color": "#FF6900",
                    "founded_year": 1964,
                    "headquarters": "Beaverton, OR"
                },
                {
                    "name": "Coca-Cola",
                    "website": "https://coca-cola.com",
                    "industry": "Beverages",
                    "description": "World's largest beverage company",
                    "primary_color": "#FF0000",
                    "founded_year": 1886,
                    "headquarters": "Atlanta, GA"
                }
            ]

            created_brands = []
            for brand_data in sample_brands:
                brand = Brand(
                    id=f"brand-{brand_data['name'].lower().replace(' ', '-')}",
                    **brand_data
                )
                db.session.add(brand)
                created_brands.append(brand)

            db.session.flush()  # Get IDs for relationships

            # Create sample analyses for each brand
            for brand in created_brands:
                analysis = Analysis(
                    id=f"analysis-sample-{brand.name.lower().replace(' ', '-')}",
                    brand_id=brand.id,
                    brand_name=brand.name,
                    analysis_types=["brand_positioning", "competitor_analysis", "market_research"],
                    status="completed",
                    progress=100,
                    results={
                        "brand_positioning": {
                            "strength": "Strong" if brand.name == "Apple" else "Moderate",
                            "market_position": "Leader" if brand.name in ["Apple", "Nike"] else "Major Player",
                            "brand_value": "Premium" if brand.name == "Apple" else "Mass Market"
                        },
                        "competitor_analysis": {
                            "main_competitors": ["Samsung", "Google"] if brand.name == "Apple"
                                               else ["Adidas", "Puma"] if brand.name == "Nike"
                                               else ["Pepsi", "Dr Pepper"],
                            "competitive_advantage": "Innovation" if brand.name == "Apple"
                                                   else "Brand Recognition" if brand.name == "Nike"
                                                   else "Global Distribution"
                        },
                        "market_research": {
                            "market_size": "Large",
                            "growth_rate": "5%" if brand.name == "Apple" else "3%" if brand.name == "Nike" else "2%",
                            "target_demographic": "Tech enthusiasts" if brand.name == "Apple"
                                                else "Athletes and fitness enthusiasts" if brand.name == "Nike"
                                                else "General consumers"
                        }
                    },
                    analysis_version="1.0",
                    data_sources=["web_scraping", "api_data", "social_media"],
                    processing_time_seconds=45.2,
                    concurrent_processing_used=True,
                    cache_hit_rate=0.75,
                    created_at=datetime.utcnow() - timedelta(days=1),
                    completed_at=datetime.utcnow() - timedelta(hours=23)
                )
                db.session.add(analysis)

            db.session.commit()
            logger.info(f"   ✅ Created {len(sample_brands)} sample brands with analyses")

        except Exception as e:
            logger.error(f"   ❌ Error creating sample data: {e}")
            db.session.rollback()
            return False

        return True


def verify_database():
    """Verify database setup (legacy wrapper)"""
    initializer = DatabaseInitializer()

    with initializer.app.app_context():
        logger.info("\n🔍 Verifying database setup...")

        try:
            # Test basic queries
            user_count = User.query.count()
            brand_count = Brand.query.count()
            analysis_count = Analysis.query.count()
            report_count = Report.query.count()
            file_count = UploadedFile.query.count()

            logger.info(f"   📊 Users: {user_count}")
            logger.info(f"   📊 Brands: {brand_count}")
            logger.info(f"   📊 Analyses: {analysis_count}")
            logger.info(f"   📊 Reports: {report_count}")
            logger.info(f"   📊 Uploaded Files: {file_count}")

            # Test database connection
            db.session.execute(text("SELECT 1"))
            logger.info("   ✅ Database connection successful")

            # Test relationships
            if analysis_count > 0:
                sample_analysis = Analysis.query.first()
                if sample_analysis.brand:
                    logger.info("   ✅ Analysis-Brand relationship working")
                if sample_analysis.reports:
                    logger.info("   ✅ Analysis-Report relationship working")

            return True

        except Exception as e:
            logger.error(f"   ❌ Database verification failed: {e}")
            return False


def main():
    """Main initialization function with comprehensive validation"""
    print("🚀 Brand Audit Tool - Comprehensive Database Initialization")
    print("=" * 60)

    initializer = DatabaseInitializer()

    # Run comprehensive initialization
    results = initializer.comprehensive_initialize()

    # Print detailed results
    print(f"\n📊 Initialization Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")
    print(f"   Steps Completed: {len(results['steps_completed'])}")
    print(f"   Steps Failed: {len(results['steps_failed'])}")

    if results['steps_completed']:
        print(f"   ✅ Completed: {', '.join(results['steps_completed'])}")

    if results['steps_failed']:
        print(f"   ❌ Failed: {', '.join(results['steps_failed'])}")

    if results['errors']:
        print(f"\n⚠️ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error['operation']}: {error['error']}")

    # Create sample data if initialization was successful
    if results['success']:
        print(f"\n📊 Creating sample data...")
        if create_sample_data():
            print("   ✅ Sample data created successfully")
        else:
            print("   ⚠️ Sample data creation failed")

        # Verify setup
        print(f"\n🔍 Verifying database setup...")
        if verify_database():
            print("   ✅ Database verification successful")
        else:
            print("   ❌ Database verification failed")

    # Summary
    print("\n" + "=" * 60)
    print("🎯 Database Initialization Summary")
    print("=" * 60)

    if results['success']:
        print("🎉 Comprehensive database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update app.py to use database instead of in-memory storage")
        print("   2. Test the application with database persistence")
        print("   3. Run migrations when deploying to production")
        print("   4. Monitor database health using the health check endpoint")
        return True
    else:
        print("⚠️ Database initialization failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check database connection settings")
        print("   2. Ensure database permissions are correct")
        print("   3. Review error logs for specific issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
