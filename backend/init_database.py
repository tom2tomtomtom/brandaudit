#!/usr/bin/env python3
"""
Simple database initialization script for Brand Audit Tool
Creates tables and sets up initial data
"""

import os
import sys
from flask import Flask

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile


def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "src", "database", "app.db")}'
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
        
        # Create database directory if it doesn't exist
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "database")
        os.makedirs(db_dir, exist_ok=True)
        
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
            Brand(
                id="brand-apple",
                name="Apple",
                website="https://apple.com",
                industry="Technology",
                description="Consumer electronics and software company",
                primary_color="#000000"
            ),
            Brand(
                id="brand-nike",
                name="Nike",
                website="https://nike.com",
                industry="Sportswear",
                description="Athletic footwear and apparel company",
                primary_color="#FF6900"
            ),
            Brand(
                id="brand-coca-cola",
                name="Coca-Cola",
                website="https://coca-cola.com",
                industry="Beverages",
                description="Beverage company",
                primary_color="#FF0000"
            )
        ]
        
        for brand in sample_brands:
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


def test_database_service():
    """Test database service functionality"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Testing database service...")
        
        try:
            from src.services.database_service import DatabaseService
            
            # Test creating analysis
            analysis = DatabaseService.create_analysis(
                brand_name="TestBrand",
                analysis_types=["test"],
                user_id=None
            )
            print(f"   ✅ Created test analysis: {analysis.id}")
            
            # Test retrieving analysis
            retrieved = DatabaseService.get_analysis(analysis.id)
            if retrieved:
                print(f"   ✅ Retrieved analysis: {retrieved.brand_name}")
            else:
                print("   ❌ Failed to retrieve analysis")
                return False
            
            # Test updating status
            success = DatabaseService.update_analysis_status(
                analysis.id, 
                "completed", 
                progress=100
            )
            if success:
                print("   ✅ Updated analysis status")
            else:
                print("   ❌ Failed to update status")
                return False
            
            # Test database stats
            stats = DatabaseService.get_database_stats()
            print(f"   ✅ Database stats: {stats}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database service test failed: {e}")
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
    
    # Step 2: Create sample data
    if create_sample_data():
        success_steps += 1
    
    # Step 3: Verify setup
    if verify_database():
        success_steps += 1
    
    # Step 4: Test database service
    if test_database_service():
        success_steps += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Database Initialization Summary")
    print("=" * 50)
    print(f"📊 Steps completed: {success_steps}/{total_steps}")
    
    if success_steps == total_steps:
        print("🎉 Database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Database is ready for use")
        print("   2. Flask app will use database instead of in-memory storage")
        print("   3. Test the application with database persistence")
        return True
    else:
        print("⚠️ Some steps failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
