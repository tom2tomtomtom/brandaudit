"""
Model Relationship Testing System for Brand Audit Tool
Validates SQLAlchemy model relationships, foreign keys, and cascading operations
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelRelationshipTester:
    """Comprehensive testing system for model relationships"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_test_app()
        self.test_results = {}
        self.errors = []
        self.test_data = {}
        
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
    
    def setup_test_data(self) -> bool:
        """Create test data for relationship testing"""
        try:
            with self.app.app_context():
                # Create all tables
                db.create_all()
                
                # Create test user
                test_user = User(
                    id=str(uuid.uuid4()),
                    email="test@example.com",
                    name="Test User",
                    company="Test Company",
                    role="user"
                )
                test_user.set_password("testpassword")
                db.session.add(test_user)
                
                # Create test brand
                test_brand = Brand(
                    id=str(uuid.uuid4()),
                    name="Test Brand",
                    website="https://testbrand.com",
                    industry="Technology",
                    description="Test brand for relationship testing"
                )
                db.session.add(test_brand)
                
                db.session.flush()  # Get IDs
                
                # Create test analysis
                test_analysis = Analysis(
                    id=f"analysis-test-{int(datetime.utcnow().timestamp())}",
                    user_id=test_user.id,
                    brand_id=test_brand.id,
                    brand_name=test_brand.name,
                    analysis_types=["brand_positioning"],
                    status="completed",
                    results={"test": "data"}
                )
                db.session.add(test_analysis)
                
                # Create test report
                test_report = Report(
                    id=str(uuid.uuid4()),
                    analysis_id=test_analysis.id,
                    user_id=test_user.id,
                    report_type="pdf",
                    filename="test_report.pdf",
                    file_path="/tmp/test_report.pdf",
                    title="Test Report"
                )
                db.session.add(test_report)
                
                # Create test uploaded file
                test_file = UploadedFile(
                    id=str(uuid.uuid4()),
                    user_id=test_user.id,
                    analysis_id=test_analysis.id,
                    filename="test_file.jpg",
                    original_filename="original_test.jpg",
                    file_path="/tmp/test_file.jpg",
                    file_size=1024,
                    mime_type="image/jpeg",
                    file_type="logo"
                )
                db.session.add(test_file)
                
                db.session.commit()
                
                # Store test data references
                self.test_data = {
                    'user': test_user,
                    'brand': test_brand,
                    'analysis': test_analysis,
                    'report': test_report,
                    'uploaded_file': test_file
                }
                
                logger.info("✅ Test data created successfully")
                return True
                
        except Exception as e:
            self.log_error("Test data setup", e)
            return False
    
    def test_user_relationships(self) -> bool:
        """Test User model relationships"""
        try:
            with self.app.app_context():
                user = self.test_data['user']
                
                # Test user -> analyses relationship
                analyses = user.analyses
                assert len(analyses) > 0, "User should have analyses"
                assert analyses[0].user_id == user.id, "Analysis should reference correct user"
                
                # Test user -> reports relationship
                reports = user.reports
                assert len(reports) > 0, "User should have reports"
                assert reports[0].user_id == user.id, "Report should reference correct user"
                
                logger.info("✅ User relationships validated")
                return True
                
        except Exception as e:
            self.log_error("User relationships test", e)
            return False
    
    def test_brand_relationships(self) -> bool:
        """Test Brand model relationships"""
        try:
            with self.app.app_context():
                brand = self.test_data['brand']
                
                # Test brand -> analyses relationship
                analyses = brand.analyses
                assert len(analyses) > 0, "Brand should have analyses"
                assert analyses[0].brand_id == brand.id, "Analysis should reference correct brand"
                
                logger.info("✅ Brand relationships validated")
                return True
                
        except Exception as e:
            self.log_error("Brand relationships test", e)
            return False
    
    def test_analysis_relationships(self) -> bool:
        """Test Analysis model relationships"""
        try:
            with self.app.app_context():
                analysis = self.test_data['analysis']
                
                # Test analysis -> user relationship (backref)
                user = analysis.user
                assert user is not None, "Analysis should have a user"
                assert user.id == analysis.user_id, "Analysis should reference correct user"
                
                # Test analysis -> brand relationship (backref)
                brand = analysis.brand
                assert brand is not None, "Analysis should have a brand"
                assert brand.id == analysis.brand_id, "Analysis should reference correct brand"
                
                # Test analysis -> reports relationship
                reports = analysis.reports
                assert len(reports) > 0, "Analysis should have reports"
                assert reports[0].analysis_id == analysis.id, "Report should reference correct analysis"
                
                logger.info("✅ Analysis relationships validated")
                return True
                
        except Exception as e:
            self.log_error("Analysis relationships test", e)
            return False
    
    def test_report_relationships(self) -> bool:
        """Test Report model relationships"""
        try:
            with self.app.app_context():
                report = self.test_data['report']
                
                # Test report -> analysis relationship (backref)
                analysis = report.analysis
                assert analysis is not None, "Report should have an analysis"
                assert analysis.id == report.analysis_id, "Report should reference correct analysis"
                
                # Test report -> user relationship (backref)
                user = report.user
                assert user is not None, "Report should have a user"
                assert user.id == report.user_id, "Report should reference correct user"
                
                logger.info("✅ Report relationships validated")
                return True
                
        except Exception as e:
            self.log_error("Report relationships test", e)
            return False
    
    def test_uploaded_file_relationships(self) -> bool:
        """Test UploadedFile model relationships"""
        try:
            with self.app.app_context():
                uploaded_file = self.test_data['uploaded_file']
                
                # Test uploaded_file -> user relationship (implicit via foreign key)
                user = User.query.get(uploaded_file.user_id)
                assert user is not None, "UploadedFile should reference valid user"
                
                # Test uploaded_file -> analysis relationship (implicit via foreign key)
                analysis = Analysis.query.get(uploaded_file.analysis_id)
                assert analysis is not None, "UploadedFile should reference valid analysis"
                
                logger.info("✅ UploadedFile relationships validated")
                return True
                
        except Exception as e:
            self.log_error("UploadedFile relationships test", e)
            return False

    def test_cascade_operations(self) -> bool:
        """Test cascade delete operations"""
        try:
            with self.app.app_context():
                # Create additional test data for cascade testing
                cascade_user = User(
                    id=str(uuid.uuid4()),
                    email="cascade@example.com",
                    name="Cascade Test User"
                )
                cascade_user.set_password("testpassword")
                db.session.add(cascade_user)

                cascade_brand = Brand(
                    id=str(uuid.uuid4()),
                    name="Cascade Test Brand",
                    website="https://cascadetest.com"
                )
                db.session.add(cascade_brand)

                db.session.flush()

                cascade_analysis = Analysis(
                    id=f"analysis-cascade-{int(datetime.utcnow().timestamp())}",
                    user_id=cascade_user.id,
                    brand_id=cascade_brand.id,
                    brand_name=cascade_brand.name,
                    analysis_types=["test"],
                    status="completed"
                )
                db.session.add(cascade_analysis)

                cascade_report = Report(
                    id=str(uuid.uuid4()),
                    analysis_id=cascade_analysis.id,
                    user_id=cascade_user.id,
                    report_type="pdf",
                    filename="cascade_test.pdf",
                    file_path="/tmp/cascade_test.pdf",
                    title="Cascade Test Report"
                )
                db.session.add(cascade_report)

                db.session.commit()

                # Test cascade delete: User -> Analyses -> Reports
                initial_analysis_count = Analysis.query.count()
                initial_report_count = Report.query.count()

                db.session.delete(cascade_user)
                db.session.commit()

                # Verify cascaded deletions
                final_analysis_count = Analysis.query.count()
                final_report_count = Report.query.count()

                assert final_analysis_count < initial_analysis_count, "User deletion should cascade to analyses"
                assert final_report_count < initial_report_count, "User deletion should cascade to reports"

                # Verify specific records are deleted
                deleted_analysis = Analysis.query.get(cascade_analysis.id)
                deleted_report = Report.query.get(cascade_report.id)

                assert deleted_analysis is None, "Analysis should be deleted with user"
                assert deleted_report is None, "Report should be deleted with user"

                logger.info("✅ Cascade operations validated")
                return True

        except Exception as e:
            self.log_error("Cascade operations test", e)
            return False

    def test_foreign_key_constraints(self) -> bool:
        """Test foreign key constraint enforcement"""
        try:
            with self.app.app_context():
                # Test invalid user_id in Analysis
                try:
                    invalid_analysis = Analysis(
                        id=f"analysis-invalid-{int(datetime.utcnow().timestamp())}",
                        user_id="non-existent-user-id",
                        brand_id=self.test_data['brand'].id,
                        brand_name="Test Brand",
                        analysis_types=["test"],
                        status="started"
                    )
                    db.session.add(invalid_analysis)
                    db.session.commit()

                    # If we reach here, constraint wasn't enforced
                    assert False, "Foreign key constraint should prevent invalid user_id"

                except IntegrityError:
                    # This is expected - foreign key constraint working
                    db.session.rollback()
                    logger.info("   ✅ User foreign key constraint enforced")

                # Test invalid brand_id in Analysis
                try:
                    invalid_analysis = Analysis(
                        id=f"analysis-invalid-brand-{int(datetime.utcnow().timestamp())}",
                        user_id=self.test_data['user'].id,
                        brand_id="non-existent-brand-id",
                        brand_name="Test Brand",
                        analysis_types=["test"],
                        status="started"
                    )
                    db.session.add(invalid_analysis)
                    db.session.commit()

                    assert False, "Foreign key constraint should prevent invalid brand_id"

                except IntegrityError:
                    db.session.rollback()
                    logger.info("   ✅ Brand foreign key constraint enforced")

                # Test invalid analysis_id in Report
                try:
                    invalid_report = Report(
                        id=str(uuid.uuid4()),
                        analysis_id="non-existent-analysis-id",
                        user_id=self.test_data['user'].id,
                        report_type="pdf",
                        filename="invalid_test.pdf",
                        file_path="/tmp/invalid_test.pdf",
                        title="Invalid Test Report"
                    )
                    db.session.add(invalid_report)
                    db.session.commit()

                    assert False, "Foreign key constraint should prevent invalid analysis_id"

                except IntegrityError:
                    db.session.rollback()
                    logger.info("   ✅ Analysis foreign key constraint enforced")

                logger.info("✅ Foreign key constraints validated")
                return True

        except Exception as e:
            self.log_error("Foreign key constraints test", e)
            return False

    def test_unique_constraints(self) -> bool:
        """Test unique constraint enforcement"""
        try:
            with self.app.app_context():
                # Test unique email constraint on User
                try:
                    duplicate_user = User(
                        id=str(uuid.uuid4()),
                        email=self.test_data['user'].email,  # Duplicate email
                        name="Duplicate User"
                    )
                    duplicate_user.set_password("testpassword")
                    db.session.add(duplicate_user)
                    db.session.commit()

                    assert False, "Unique constraint should prevent duplicate email"

                except IntegrityError:
                    db.session.rollback()
                    logger.info("   ✅ User email unique constraint enforced")

                logger.info("✅ Unique constraints validated")
                return True

        except Exception as e:
            self.log_error("Unique constraints test", e)
            return False

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all relationship tests"""
        logger.info("🧪 Starting comprehensive model relationship tests...")

        results = {
            'success': True,
            'tests_passed': [],
            'tests_failed': [],
            'total_tests': 0,
            'passed_tests': 0,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Setup test data
        if not self.setup_test_data():
            results['success'] = False
            results['tests_failed'].append('test_data_setup')
            results['errors'] = self.errors
            return results

        # Define all tests
        tests = [
            ('User Relationships', self.test_user_relationships),
            ('Brand Relationships', self.test_brand_relationships),
            ('Analysis Relationships', self.test_analysis_relationships),
            ('Report Relationships', self.test_report_relationships),
            ('UploadedFile Relationships', self.test_uploaded_file_relationships),
            ('Cascade Operations', self.test_cascade_operations),
            ('Foreign Key Constraints', self.test_foreign_key_constraints),
            ('Unique Constraints', self.test_unique_constraints)
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
            logger.info("✅ All model relationship tests passed!")
        else:
            logger.error(f"❌ {len(results['tests_failed'])} tests failed")

        return results


def run_model_relationship_tests():
    """Run model relationship tests (standalone function)"""
    print("🧪 Brand Audit Tool - Model Relationship Tests")
    print("=" * 50)

    tester = ModelRelationshipTester()
    results = tester.run_comprehensive_tests()

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
        print("🎉 All model relationship tests completed successfully!")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")

    return results['success']


if __name__ == "__main__":
    success = run_model_relationship_tests()
    sys.exit(0 if success else 1)
