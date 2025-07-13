"""
Robust Database Setup for Brand Audit Tool
Creates a clean, functional, and robust database system
"""

import os
import sys
import logging
from typing import Dict, Any
from datetime import datetime

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Import the main app to use its configuration
from app import app, db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile
from src.services.database_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_and_setup_database() -> Dict[str, Any]:
    """Clean setup of the database with the app's configuration"""
    logger.info("🧹 Starting clean and robust database setup...")
    
    setup_results = {
        'success': True,
        'steps_completed': [],
        'errors': [],
        'warnings': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        with app.app_context():
            # Step 1: Drop all existing tables (clean slate)
            logger.info("Step 1: Cleaning existing database...")
            try:
                db.drop_all()
                setup_results['steps_completed'].append('database_cleaned')
                logger.info("   ✅ Existing database cleaned")
            except Exception as e:
                setup_results['warnings'].append(f"Database cleaning warning: {e}")
                logger.warning(f"   ⚠️ Database cleaning warning: {e}")
            
            # Step 2: Create all tables
            logger.info("Step 2: Creating database tables...")
            db.create_all()
            setup_results['steps_completed'].append('tables_created')
            logger.info("   ✅ Database tables created")
            
            # Step 3: Verify table creation
            logger.info("Step 3: Verifying table structure...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = {'users', 'brands', 'analyses', 'reports', 'uploaded_files'}
            
            if expected_tables.issubset(set(tables)):
                setup_results['steps_completed'].append('tables_verified')
                logger.info(f"   ✅ All {len(expected_tables)} tables verified")
            else:
                missing = expected_tables - set(tables)
                setup_results['errors'].append(f"Missing tables: {missing}")
                setup_results['success'] = False
                logger.error(f"   ❌ Missing tables: {missing}")
                return setup_results
            
            # Step 4: Test basic database operations
            logger.info("Step 4: Testing database operations...")
            try:
                # Test creating a brand
                test_brand = DatabaseService.create_brand(
                    name="Test Brand",
                    website="https://test.com",
                    industry="Technology"
                )
                
                # Test creating an analysis
                test_analysis = DatabaseService.create_analysis(
                    brand_name="Test Brand",
                    analysis_types=["brand_positioning"]
                )
                
                # Test database stats
                stats = DatabaseService.get_database_stats()
                
                # Clean up test data
                db.session.delete(test_analysis)
                db.session.delete(test_brand)
                db.session.commit()
                
                setup_results['steps_completed'].append('operations_tested')
                logger.info("   ✅ Database operations tested successfully")
                
            except Exception as e:
                setup_results['errors'].append(f"Database operations test failed: {e}")
                setup_results['success'] = False
                logger.error(f"   ❌ Database operations test failed: {e}")
                return setup_results
            
            # Step 5: Create sample data
            logger.info("Step 5: Creating sample data...")
            try:
                sample_data_count = create_sample_data()
                setup_results['steps_completed'].append('sample_data_created')
                setup_results['sample_data_count'] = sample_data_count
                logger.info(f"   ✅ Created {sample_data_count} sample records")
                
            except Exception as e:
                setup_results['warnings'].append(f"Sample data creation failed: {e}")
                logger.warning(f"   ⚠️ Sample data creation failed: {e}")
            
            # Step 6: Final verification
            logger.info("Step 6: Final system verification...")
            try:
                final_stats = DatabaseService.get_database_stats()
                setup_results['final_stats'] = final_stats
                setup_results['steps_completed'].append('final_verification')
                logger.info("   ✅ Final verification completed")
                logger.info(f"   📊 Final stats: {final_stats}")
                
            except Exception as e:
                setup_results['warnings'].append(f"Final verification warning: {e}")
                logger.warning(f"   ⚠️ Final verification warning: {e}")
    
    except Exception as e:
        setup_results['success'] = False
        setup_results['errors'].append(f"Database setup failed: {e}")
        logger.error(f"❌ Database setup failed: {e}")
    
    return setup_results


def create_sample_data() -> int:
    """Create robust sample data"""
    sample_brands = [
        {"name": "Apple", "website": "https://apple.com", "industry": "Technology"},
        {"name": "Nike", "website": "https://nike.com", "industry": "Sportswear"},
        {"name": "Coca-Cola", "website": "https://coca-cola.com", "industry": "Beverages"}
    ]
    
    created_count = 0
    
    # Create brands
    for brand_data in sample_brands:
        try:
            brand = DatabaseService.create_brand(**brand_data)
            created_count += 1
            
            # Create an analysis for each brand
            analysis = DatabaseService.create_analysis(
                brand_name=brand.name,
                analysis_types=["brand_positioning", "competitor_analysis"]
            )
            created_count += 1
            
        except Exception as e:
            logger.warning(f"Failed to create sample data for {brand_data['name']}: {e}")
    
    return created_count


def main():
    """Main function for robust database setup"""
    print("🚀 Brand Audit Tool - Robust Database Setup")
    print("=" * 60)
    
    # Run the setup
    results = clean_and_setup_database()
    
    # Print results
    print(f"\n📊 Setup Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")
    print(f"   Steps Completed: {len(results['steps_completed'])}")
    
    if results['steps_completed']:
        print(f"   ✅ Completed: {', '.join(results['steps_completed'])}")
    
    if results.get('sample_data_count'):
        print(f"   📊 Sample Data: {results['sample_data_count']} records created")
    
    if results.get('final_stats'):
        stats = results['final_stats']
        print(f"   📈 Database Stats:")
        print(f"     - Users: {stats.get('total_users', 0)}")
        print(f"     - Brands: {stats.get('total_brands', 0)}")
        print(f"     - Analyses: {stats.get('total_analyses', 0)}")
        print(f"     - Reports: {stats.get('total_reports', 0)}")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"   - {error}")
    
    if results['warnings']:
        print(f"\n⚠️ Warnings:")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    print("\n" + "=" * 60)
    if results['success']:
        print("🎉 Robust database setup completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Start the Flask application: python app.py")
        print("   2. Test the API endpoints")
        print("   3. Check health status at: /api/db/health")
        print("   4. The database is ready for production use!")
    else:
        print("❌ Database setup failed!")
        print("   Please review the errors above and try again.")
    
    return results['success']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
