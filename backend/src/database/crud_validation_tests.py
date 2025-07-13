"""
CRUD Operation Validation System for Brand Audit Tool
Comprehensive testing for Create, Read, Update, Delete operations across all models
"""

import os
import sys
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile
from src.services.database_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDValidationTester:
    """Comprehensive CRUD operation validation system"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_test_app()
        self.test_results = {}
        self.errors = []
        self.created_records = {}
        
    def create_test_app(self) -> Flask:
        """Create Flask app for testing"""
        app = Flask(__name__)
        
        # Use in-memory SQLite for testing
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test-secret-key',
            'TESTING': True
        })
        
        db.init_app(app)
        return app
    
    def log_error(self, test_name: str, error: Exception):
        """Log and store test errors"""
        error_msg = f"{test_name}: {str(error)}"
        logger.error(error_msg)
        self.errors.append({
            'test': test_name,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def setup_test_environment(self) -> bool:
        """Setup test environment"""
        try:
            with self.app.app_context():
                db.create_all()
                logger.info("✅ Test environment setup complete")
                return True
        except Exception as e:
            self.log_error("Test environment setup", e)
            return False
    
    def test_user_crud_operations(self) -> bool:
        """Test User model CRUD operations"""
        try:
            with self.app.app_context():
                # CREATE
                user_data = {
                    'id': str(uuid.uuid4()),
                    'email': 'crud_test@example.com',
                    'name': 'CRUD Test User',
                    'company': 'Test Company',
                    'role': 'user'
                }
                
                user = User(**user_data)
                user.set_password('testpassword')
                db.session.add(user)
                db.session.commit()
                
                self.created_records['user'] = user
                logger.info("   ✅ User CREATE operation successful")
                
                # READ
                retrieved_user = User.query.get(user.id)
                assert retrieved_user is not None, "User should be retrievable"
                assert retrieved_user.email == user_data['email'], "Retrieved user should match created user"
                
                # Test query by email
                user_by_email = User.query.filter_by(email=user_data['email']).first()
                assert user_by_email is not None, "User should be findable by email"
                assert user_by_email.id == user.id, "User found by email should match"
                
                logger.info("   ✅ User READ operations successful")
                
                # UPDATE
                new_name = 'Updated CRUD Test User'
                new_company = 'Updated Test Company'
                
                retrieved_user.name = new_name
                retrieved_user.company = new_company
                db.session.commit()
                
                # Verify update
                updated_user = User.query.get(user.id)
                assert updated_user.name == new_name, "User name should be updated"
                assert updated_user.company == new_company, "User company should be updated"
                
                logger.info("   ✅ User UPDATE operation successful")
                
                # Test password operations
                assert user.check_password('testpassword'), "Password should be verifiable"
                user.set_password('newpassword')
                db.session.commit()
                assert user.check_password('newpassword'), "New password should work"
                assert not user.check_password('testpassword'), "Old password should not work"
                
                logger.info("   ✅ User password operations successful")
                
                # Test account locking
                user.increment_failed_login()
                assert user.failed_login_attempts == 1, "Failed login attempts should increment"
                
                user.lock_account(1)  # Lock for 1 minute
                assert user.is_locked(), "User should be locked"
                
                user.unlock_account()
                assert not user.is_locked(), "User should be unlocked"
                assert user.failed_login_attempts == 0, "Failed attempts should be reset"
                
                logger.info("   ✅ User security operations successful")
                
                return True
                
        except Exception as e:
            self.log_error("User CRUD operations", e)
            return False
    
    def test_brand_crud_operations(self) -> bool:
        """Test Brand model CRUD operations"""
        try:
            with self.app.app_context():
                # CREATE
                brand_data = {
                    'id': str(uuid.uuid4()),
                    'name': 'CRUD Test Brand',
                    'website': 'https://crudtest.com',
                    'industry': 'Technology',
                    'description': 'Test brand for CRUD operations',
                    'primary_color': '#FF0000',
                    'founded_year': 2020,
                    'headquarters': 'Test City, TC'
                }
                
                brand = Brand(**brand_data)
                db.session.add(brand)
                db.session.commit()
                
                self.created_records['brand'] = brand
                logger.info("   ✅ Brand CREATE operation successful")
                
                # READ
                retrieved_brand = Brand.query.get(brand.id)
                assert retrieved_brand is not None, "Brand should be retrievable"
                assert retrieved_brand.name == brand_data['name'], "Retrieved brand should match created brand"
                
                # Test query by name
                brand_by_name = Brand.query.filter_by(name=brand_data['name']).first()
                assert brand_by_name is not None, "Brand should be findable by name"
                assert brand_by_name.id == brand.id, "Brand found by name should match"
                
                logger.info("   ✅ Brand READ operations successful")
                
                # UPDATE
                new_description = 'Updated test brand description'
                new_website = 'https://updated-crudtest.com'
                
                retrieved_brand.description = new_description
                retrieved_brand.website = new_website
                db.session.commit()
                
                # Verify update
                updated_brand = Brand.query.get(brand.id)
                assert updated_brand.description == new_description, "Brand description should be updated"
                assert updated_brand.website == new_website, "Brand website should be updated"
                
                logger.info("   ✅ Brand UPDATE operation successful")
                
                return True
                
        except Exception as e:
            self.log_error("Brand CRUD operations", e)
            return False
    
    def test_analysis_crud_operations(self) -> bool:
        """Test Analysis model CRUD operations"""
        try:
            with self.app.app_context():
                # Ensure we have user and brand for foreign keys
                if 'user' not in self.created_records or 'brand' not in self.created_records:
                    raise Exception("User and Brand must be created before Analysis")
                
                user = self.created_records['user']
                brand = self.created_records['brand']
                
                # CREATE using DatabaseService
                analysis = DatabaseService.create_analysis(
                    brand_name=brand.name,
                    analysis_types=['brand_positioning', 'competitor_analysis'],
                    user_id=user.id
                )
                
                self.created_records['analysis'] = analysis
                logger.info("   ✅ Analysis CREATE operation successful")
                
                # READ
                retrieved_analysis = DatabaseService.get_analysis(analysis.id)
                assert retrieved_analysis is not None, "Analysis should be retrievable"
                assert retrieved_analysis.brand_name == brand.name, "Retrieved analysis should match created analysis"
                
                logger.info("   ✅ Analysis READ operations successful")
                
                # UPDATE
                new_status = 'processing'
                new_progress = 50
                error_message = 'Test error message'
                
                success = DatabaseService.update_analysis_status(
                    analysis.id, 
                    new_status, 
                    error_message, 
                    new_progress
                )
                assert success, "Analysis status update should succeed"
                
                # Verify update
                updated_analysis = DatabaseService.get_analysis(analysis.id)
                assert updated_analysis.status == new_status, "Analysis status should be updated"
                assert updated_analysis.progress == new_progress, "Analysis progress should be updated"
                assert updated_analysis.error_message == error_message, "Analysis error message should be updated"
                
                logger.info("   ✅ Analysis UPDATE operation successful")
                
                # Test results update
                test_results = {
                    'brand_positioning': {'strength': 'Strong'},
                    'competitor_analysis': {'competitors': ['Competitor A', 'Competitor B']}
                }
                
                success = DatabaseService.update_analysis_results(analysis.id, test_results)
                assert success, "Analysis results update should succeed"
                
                # Verify results update
                updated_analysis = DatabaseService.get_analysis(analysis.id)
                assert updated_analysis.results == test_results, "Analysis results should be updated"
                
                logger.info("   ✅ Analysis results update successful")
                
                return True
                
        except Exception as e:
            self.log_error("Analysis CRUD operations", e)
            return False

    def test_report_crud_operations(self) -> bool:
        """Test Report model CRUD operations"""
        try:
            with self.app.app_context():
                # Ensure we have analysis for foreign key
                if 'analysis' not in self.created_records:
                    raise Exception("Analysis must be created before Report")

                analysis = self.created_records['analysis']
                user = self.created_records['user']

                # CREATE using DatabaseService
                report = DatabaseService.create_report(
                    analysis_id=analysis.id,
                    report_type='pdf',
                    filename='crud_test_report.pdf',
                    file_path='/tmp/crud_test_report.pdf',
                    title='CRUD Test Report',
                    user_id=user.id,
                    description='Test report for CRUD operations',
                    file_size=1024,
                    pages_count=5
                )

                self.created_records['report'] = report
                logger.info("   ✅ Report CREATE operation successful")

                # READ
                retrieved_report = DatabaseService.get_report(report.id)
                assert retrieved_report is not None, "Report should be retrievable"
                assert retrieved_report.title == 'CRUD Test Report', "Retrieved report should match created report"

                # Test get reports by analysis
                analysis_reports = DatabaseService.get_analysis_reports(analysis.id)
                assert len(analysis_reports) > 0, "Analysis should have reports"
                assert any(r.id == report.id for r in analysis_reports), "Report should be in analysis reports"

                logger.info("   ✅ Report READ operations successful")

                # UPDATE
                new_status = 'completed'
                success = DatabaseService.update_report_status(report.id, new_status)
                assert success, "Report status update should succeed"

                # Verify update
                updated_report = DatabaseService.get_report(report.id)
                assert updated_report.status == new_status, "Report status should be updated"

                logger.info("   ✅ Report UPDATE operation successful")

                # Test download increment
                initial_downloads = updated_report.download_count
                success = DatabaseService.increment_report_download(report.id)
                assert success, "Report download increment should succeed"

                # Verify download increment
                updated_report = DatabaseService.get_report(report.id)
                assert updated_report.download_count == initial_downloads + 1, "Download count should increment"
                assert updated_report.last_downloaded is not None, "Last downloaded should be set"

                logger.info("   ✅ Report download tracking successful")

                return True

        except Exception as e:
            self.log_error("Report CRUD operations", e)
            return False

    def test_uploaded_file_crud_operations(self) -> bool:
        """Test UploadedFile model CRUD operations"""
        try:
            with self.app.app_context():
                # Ensure we have user and analysis for foreign keys
                if 'user' not in self.created_records or 'analysis' not in self.created_records:
                    raise Exception("User and Analysis must be created before UploadedFile")

                user = self.created_records['user']
                analysis = self.created_records['analysis']

                # CREATE
                file_data = {
                    'id': str(uuid.uuid4()),
                    'user_id': user.id,
                    'analysis_id': analysis.id,
                    'filename': 'crud_test_file.jpg',
                    'original_filename': 'original_crud_test.jpg',
                    'file_path': '/tmp/crud_test_file.jpg',
                    'file_size': 2048,
                    'mime_type': 'image/jpeg',
                    'file_type': 'logo'
                }

                uploaded_file = UploadedFile(**file_data)
                db.session.add(uploaded_file)
                db.session.commit()

                self.created_records['uploaded_file'] = uploaded_file
                logger.info("   ✅ UploadedFile CREATE operation successful")

                # READ
                retrieved_file = UploadedFile.query.get(uploaded_file.id)
                assert retrieved_file is not None, "UploadedFile should be retrievable"
                assert retrieved_file.filename == file_data['filename'], "Retrieved file should match created file"

                # Test query by user
                user_files = UploadedFile.query.filter_by(user_id=user.id).all()
                assert len(user_files) > 0, "User should have uploaded files"
                assert any(f.id == uploaded_file.id for f in user_files), "File should be in user files"

                # Test query by analysis
                analysis_files = UploadedFile.query.filter_by(analysis_id=analysis.id).all()
                assert len(analysis_files) > 0, "Analysis should have uploaded files"
                assert any(f.id == uploaded_file.id for f in analysis_files), "File should be in analysis files"

                logger.info("   ✅ UploadedFile READ operations successful")

                # UPDATE (UploadedFile typically doesn't have update operations, but we can test direct updates)
                new_file_type = 'screenshot'
                retrieved_file.file_type = new_file_type
                db.session.commit()

                # Verify update
                updated_file = UploadedFile.query.get(uploaded_file.id)
                assert updated_file.file_type == new_file_type, "File type should be updated"

                logger.info("   ✅ UploadedFile UPDATE operation successful")

                return True

        except Exception as e:
            self.log_error("UploadedFile CRUD operations", e)
            return False

    def test_database_service_operations(self) -> bool:
        """Test DatabaseService utility operations"""
        try:
            with self.app.app_context():
                # Test database statistics
                stats = DatabaseService.get_database_stats()
                assert isinstance(stats, dict), "Stats should be a dictionary"
                assert 'total_analyses' in stats, "Stats should include total_analyses"
                assert 'total_brands' in stats, "Stats should include total_brands"
                assert 'total_reports' in stats, "Stats should include total_reports"
                assert 'total_users' in stats, "Stats should include total_users"

                logger.info("   ✅ Database statistics successful")

                # Test brand search
                if 'brand' in self.created_records:
                    brand = self.created_records['brand']
                    search_results = DatabaseService.search_brands('CRUD')
                    assert len(search_results) > 0, "Brand search should return results"
                    assert any(b.id == brand.id for b in search_results), "Search should find our test brand"

                logger.info("   ✅ Brand search successful")

                # Test popular brands (requires analyses)
                popular_brands = DatabaseService.get_popular_brands(limit=5)
                assert isinstance(popular_brands, list), "Popular brands should be a list"

                logger.info("   ✅ Popular brands query successful")

                # Test user analyses query
                if 'user' in self.created_records:
                    user = self.created_records['user']
                    user_analyses = DatabaseService.get_user_analyses(user.id)
                    assert isinstance(user_analyses, list), "User analyses should be a list"

                logger.info("   ✅ User analyses query successful")

                # Test recent analyses
                recent_analyses = DatabaseService.get_recent_analyses(limit=10)
                assert isinstance(recent_analyses, list), "Recent analyses should be a list"

                logger.info("   ✅ Recent analyses query successful")

                return True

        except Exception as e:
            self.log_error("DatabaseService operations", e)
            return False

    def test_delete_operations(self) -> bool:
        """Test DELETE operations with proper cleanup"""
        try:
            with self.app.app_context():
                # Test cleanup old analyses
                initial_count = Analysis.query.count()

                # Create an old analysis for cleanup testing
                old_analysis = Analysis(
                    id=f"analysis-old-{int(datetime.utcnow().timestamp())}",
                    brand_id=self.created_records['brand'].id,
                    brand_name='Old Test Brand',
                    analysis_types=['test'],
                    status='completed',
                    created_at=datetime.utcnow() - timedelta(days=35)  # 35 days old
                )
                db.session.add(old_analysis)
                db.session.commit()

                # Test cleanup
                cleaned_count = DatabaseService.cleanup_old_analyses(days=30)
                assert cleaned_count > 0, "Should clean up old analyses"

                final_count = Analysis.query.count()
                assert final_count < initial_count + 1, "Old analysis should be cleaned up"

                logger.info("   ✅ Analysis cleanup successful")

                # Test direct DELETE operations
                # Delete uploaded file
                if 'uploaded_file' in self.created_records:
                    file_id = self.created_records['uploaded_file'].id
                    db.session.delete(self.created_records['uploaded_file'])
                    db.session.commit()

                    deleted_file = UploadedFile.query.get(file_id)
                    assert deleted_file is None, "UploadedFile should be deleted"

                    logger.info("   ✅ UploadedFile DELETE successful")

                # Delete report
                if 'report' in self.created_records:
                    report_id = self.created_records['report'].id
                    db.session.delete(self.created_records['report'])
                    db.session.commit()

                    deleted_report = Report.query.get(report_id)
                    assert deleted_report is None, "Report should be deleted"

                    logger.info("   ✅ Report DELETE successful")

                # Delete analysis
                if 'analysis' in self.created_records:
                    analysis_id = self.created_records['analysis'].id
                    db.session.delete(self.created_records['analysis'])
                    db.session.commit()

                    deleted_analysis = Analysis.query.get(analysis_id)
                    assert deleted_analysis is None, "Analysis should be deleted"

                    logger.info("   ✅ Analysis DELETE successful")

                # Delete brand
                if 'brand' in self.created_records:
                    brand_id = self.created_records['brand'].id
                    db.session.delete(self.created_records['brand'])
                    db.session.commit()

                    deleted_brand = Brand.query.get(brand_id)
                    assert deleted_brand is None, "Brand should be deleted"

                    logger.info("   ✅ Brand DELETE successful")

                # Delete user (this should cascade to related records if any remain)
                if 'user' in self.created_records:
                    user_id = self.created_records['user'].id
                    db.session.delete(self.created_records['user'])
                    db.session.commit()

                    deleted_user = User.query.get(user_id)
                    assert deleted_user is None, "User should be deleted"

                    logger.info("   ✅ User DELETE successful")

                return True

        except Exception as e:
            self.log_error("DELETE operations", e)
            return False

    def run_comprehensive_crud_tests(self) -> Dict[str, Any]:
        """Run all CRUD validation tests"""
        logger.info("🧪 Starting comprehensive CRUD validation tests...")

        results = {
            'success': True,
            'tests_passed': [],
            'tests_failed': [],
            'total_tests': 0,
            'passed_tests': 0,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Setup test environment
        if not self.setup_test_environment():
            results['success'] = False
            results['tests_failed'].append('test_environment_setup')
            results['errors'] = self.errors
            return results

        # Define all tests in order (some depend on others)
        tests = [
            ('User CRUD Operations', self.test_user_crud_operations),
            ('Brand CRUD Operations', self.test_brand_crud_operations),
            ('Analysis CRUD Operations', self.test_analysis_crud_operations),
            ('Report CRUD Operations', self.test_report_crud_operations),
            ('UploadedFile CRUD Operations', self.test_uploaded_file_crud_operations),
            ('DatabaseService Operations', self.test_database_service_operations),
            ('DELETE Operations', self.test_delete_operations)
        ]

        results['total_tests'] = len(tests)

        # Run each test
        for test_name, test_func in tests:
            logger.info(f"   Running: {test_name}")

            if test_func():
                results['tests_passed'].append(test_name)
                results['passed_tests'] += 1
            else:
                results['tests_failed'].append(test_name)
                results['success'] = False

        # Add error details
        results['errors'] = self.errors

        # Log summary
        if results['success']:
            logger.info("✅ All CRUD validation tests passed!")
        else:
            logger.error(f"❌ {len(results['tests_failed'])} tests failed")

        return results


def run_crud_validation_tests():
    """Run CRUD validation tests (standalone function)"""
    print("🧪 Brand Audit Tool - CRUD Validation Tests")
    print("=" * 50)

    tester = CRUDValidationTester()
    results = tester.run_comprehensive_crud_tests()

    # Print detailed results
    print(f"\n📊 Test Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")
    print(f"   Tests Passed: {results['passed_tests']}/{results['total_tests']}")

    if results['tests_passed']:
        print(f"   ✅ Passed: {', '.join(results['tests_passed'])}")

    if results['tests_failed']:
        print(f"   ❌ Failed: {', '.join(results['tests_failed'])}")

    if results['errors']:
        print(f"\n⚠️ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error['test']}: {error['error']}")

    print("\n" + "=" * 50)
    if results['success']:
        print("🎉 All CRUD validation tests completed successfully!")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")

    return results['success']


if __name__ == "__main__":
    success = run_crud_validation_tests()
    sys.exit(0 if success else 1)
