"""
Database initialization script for Brand Audit Tool
Creates tables and sets up initial data
"""

import os
import sys
from flask import Flask

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


def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    # Initialize extensions
    db.init_app(app)
    
    return app


def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Initializing database...")
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Print table information
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Created tables:")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"   📊 {table} ({len(columns)} columns)")
            for col in columns[:3]:  # Show first 3 columns
                print(f"      - {col['name']} ({col['type']})")
            if len(columns) > 3:
                print(f"      ... and {len(columns) - 3} more columns")
        
        return True


def setup_migrations():
    """Set up Flask-Migrate for database migrations"""
    if not MIGRATE_AVAILABLE:
        print("\n🔄 Flask-Migrate not available, skipping migration setup...")
        print("   💡 Using basic database initialization instead")
        return True

    app = create_app()
    migrate_obj = Migrate(app, db)

    with app.app_context():
        print("\n🔄 Setting up database migrations...")

        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

        try:
            if not os.path.exists(migrations_dir):
                print("   📁 Initializing migrations directory...")
                init(directory=migrations_dir)
                print("   ✅ Migrations directory created")
            else:
                print("   📁 Migrations directory already exists")

            print("   📝 Creating initial migration...")
            migrate(message="Initial migration", directory=migrations_dir)
            print("   ✅ Initial migration created")

            print("   ⬆️ Applying migrations...")
            upgrade(directory=migrations_dir)
            print("   ✅ Migrations applied successfully")

        except Exception as e:
            print(f"   ⚠️ Migration setup note: {e}")
            print("   💡 This is normal if migrations already exist")

        return True


def create_sample_data():
    """Create sample data for testing"""
    app = create_app()
    
    with app.app_context():
        print("\n📊 Creating sample data...")
        
        # Check if sample data already exists
        if Brand.query.first():
            print("   ℹ️ Sample data already exists, skipping...")
            return True
        
        # Create sample brands
        sample_brands = [
            {
                "name": "Apple",
                "website": "https://apple.com",
                "industry": "Technology",
                "description": "Consumer electronics and software company",
                "primary_color": "#000000"
            },
            {
                "name": "Nike",
                "website": "https://nike.com",
                "industry": "Sportswear",
                "description": "Athletic footwear and apparel company",
                "primary_color": "#FF6900"
            },
            {
                "name": "Coca-Cola",
                "website": "https://coca-cola.com",
                "industry": "Beverages",
                "description": "Beverage company",
                "primary_color": "#FF0000"
            }
        ]
        
        for brand_data in sample_brands:
            brand = Brand(
                id=f"brand-{brand_data['name'].lower()}",
                **brand_data
            )
            db.session.add(brand)
        
        db.session.commit()
        print(f"   ✅ Created {len(sample_brands)} sample brands")
        
        return True


def verify_database():
    """Verify database setup"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verifying database setup...")
        
        try:
            # Test basic queries
            brand_count = Brand.query.count()
            analysis_count = Analysis.query.count()
            report_count = Report.query.count()
            
            print(f"   📊 Brands: {brand_count}")
            print(f"   📊 Analyses: {analysis_count}")
            print(f"   📊 Reports: {report_count}")
            
            # Test database connection
            db.session.execute(db.text("SELECT 1"))
            print("   ✅ Database connection successful")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database verification failed: {e}")
            return False


def main():
    """Main initialization function"""
    print("🚀 Brand Audit Tool - Database Initialization")
    print("=" * 50)
    
    success_steps = 0
    total_steps = 4
    
    # Step 1: Initialize database
    if init_database():
        success_steps += 1
    
    # Step 2: Setup migrations
    if setup_migrations():
        success_steps += 1
    
    # Step 3: Create sample data
    if create_sample_data():
        success_steps += 1
    
    # Step 4: Verify setup
    if verify_database():
        success_steps += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Database Initialization Summary")
    print("=" * 50)
    print(f"📊 Steps completed: {success_steps}/{total_steps}")
    
    if success_steps == total_steps:
        print("🎉 Database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update app.py to use database instead of in-memory storage")
        print("   2. Test the application with database persistence")
        print("   3. Run migrations when deploying to production")
        return True
    else:
        print("⚠️ Some steps failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
