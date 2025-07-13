#!/usr/bin/env python3
"""
Test suite for existing database functionality
Tests DatabaseService and existing data models
"""
import os
import sys
import pytest
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from src.extensions import db
from src.services.database_service import DatabaseService
from src.models.user_model import User, Brand, Analysis, Report

class TestExistingDatabaseService:
    """Test suite for existing DatabaseService functionality"""
    
    @pytest.fixture
    def app_context(self):
        """Create app context with test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_create_analysis_exists(self, app_context):
        """Test existing create_analysis method"""
        analysis = DatabaseService.create_analysis(
            brand_name="Apple Inc",
            analysis_types=["brand_positioning", "competitive_analysis"]
        )
        
        assert analysis is not None
        assert analysis.brand_name == "Apple Inc"
        assert analysis.analysis_types == ["brand_positioning", "competitive_analysis"]
        assert analysis.status == "started"
        assert analysis.progress == 0
        assert analysis.id.startswith("analysis-")
        
        # Should create associated brand
        brand = Brand.query.filter_by(name="Apple Inc").first()
        assert brand is not None
        assert brand.name == "Apple Inc"
        
    def test_get_analysis_exists(self, app_context):
        """Test existing get_analysis method"""
        # Create analysis first
        created_analysis = DatabaseService.create_analysis("Tesla", ["visual_analysis"])
        analysis_id = created_analysis.id
        
        # Retrieve analysis
        retrieved_analysis = DatabaseService.get_analysis(analysis_id)
        
        assert retrieved_analysis is not None
        assert retrieved_analysis.id == analysis_id
        assert retrieved_analysis.brand_name == "Tesla"
        assert retrieved_analysis.analysis_types == ["visual_analysis"]
        
    def test_get_analysis_not_found(self, app_context):
        """Test get_analysis with non-existent ID"""
        result = DatabaseService.get_analysis("nonexistent-id")
        assert result is None
        
    def test_update_analysis_status_exists(self, app_context):
        """Test existing update_analysis_status method"""
        # Create analysis
        analysis = DatabaseService.create_analysis("Nike", ["brand_health"])
        analysis_id = analysis.id
        
        # Update status
        success = DatabaseService.update_analysis_status(
            analysis_id, 
            "processing", 
            error_message=None, 
            progress=50
        )
        
        assert success is True
        
        # Verify update
        updated_analysis = DatabaseService.get_analysis(analysis_id)
        assert updated_analysis.status == "processing"
        assert updated_analysis.progress == 50
        
    def test_update_analysis_results_exists(self, app_context):
        """Test existing update_analysis_results method"""
        # Create analysis
        analysis = DatabaseService.create_analysis("Microsoft", ["competitive_analysis"])
        analysis_id = analysis.id
        
        # Update results
        test_results = {
            "brand_health_score": 85,
            "visual_analysis": {"consistency_score": 90},
            "competitive_intelligence": {"market_position": "strong"}
        }
        
        success = DatabaseService.update_analysis_results(analysis_id, test_results)
        assert success is True
        
        # Verify results
        updated_analysis = DatabaseService.get_analysis(analysis_id)
        assert updated_analysis.results == test_results
        
    def test_get_recent_analyses_exists(self, app_context):
        """Test existing get_recent_analyses method"""
        # Create multiple analyses
        DatabaseService.create_analysis("Brand1", ["analysis1"])
        DatabaseService.create_analysis("Brand2", ["analysis2"])
        DatabaseService.create_analysis("Brand3", ["analysis3"])
        
        # Get recent analyses
        recent_analyses = DatabaseService.get_recent_analyses(limit=2)
        
        assert len(recent_analyses) == 2
        assert all(isinstance(analysis, Analysis) for analysis in recent_analyses)
        
        # Should be ordered by created_at desc
        assert recent_analyses[0].created_at >= recent_analyses[1].created_at
        
    def test_create_brand_exists(self, app_context):
        """Test existing create_brand method"""
        brand = DatabaseService.create_brand(
            name="Google",
            website="https://google.com",
            industry="Technology"
        )
        
        assert brand is not None
        assert brand.name == "Google"
        assert brand.website == "https://google.com"
        assert brand.industry == "Technology"
        assert brand.id is not None
        
    def test_get_brand_exists(self, app_context):
        """Test existing get_brand method"""
        # Create brand first
        created_brand = DatabaseService.create_brand("Amazon", website="https://amazon.com")
        brand_id = created_brand.id
        
        # Retrieve brand
        retrieved_brand = DatabaseService.get_brand(brand_id)
        
        assert retrieved_brand is not None
        assert retrieved_brand.id == brand_id
        assert retrieved_brand.name == "Amazon"
        assert retrieved_brand.website == "https://amazon.com"
        
    def test_search_brands_exists(self, app_context):
        """Test existing search_brands method"""
        # Create test brands
        DatabaseService.create_brand("Apple Inc")
        DatabaseService.create_brand("Apple Music")
        DatabaseService.create_brand("Microsoft")
        
        # Search for brands
        results = DatabaseService.search_brands("Apple", limit=5)
        
        assert len(results) == 2
        assert all("Apple" in brand.name for brand in results)
        
    def test_get_database_stats_exists(self, app_context):
        """Test existing get_database_stats method"""
        # Create test data
        DatabaseService.create_analysis("TestBrand1", ["test"])
        DatabaseService.create_analysis("TestBrand2", ["test"])
        
        # Get stats
        stats = DatabaseService.get_database_stats()
        
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'total_brands' in stats
        assert 'total_reports' in stats
        assert 'total_users' in stats
        assert 'completed_analyses' in stats
        assert 'failed_analyses' in stats
        
        assert stats['total_analyses'] >= 2
        assert stats['total_brands'] >= 2
        
    def test_get_popular_brands_exists(self, app_context):
        """Test existing get_popular_brands method"""
        # Create multiple analyses for same brand
        DatabaseService.create_analysis("Popular Brand", ["test1"])
        DatabaseService.create_analysis("Popular Brand", ["test2"])
        DatabaseService.create_analysis("Less Popular", ["test3"])
        
        # Get popular brands
        popular = DatabaseService.get_popular_brands(limit=5)
        
        assert isinstance(popular, list)
        assert len(popular) >= 2
        
        # Should have required fields
        for brand_info in popular:
            assert 'brand_id' in brand_info
            assert 'brand_name' in brand_info
            assert 'analysis_count' in brand_info
            
        # Most popular should be first
        assert popular[0]['brand_name'] == "Popular Brand"
        assert popular[0]['analysis_count'] == 2

class TestExistingDataModels:
    """Test suite for existing data models"""
    
    @pytest.fixture
    def app_context(self):
        """Create app context with test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_analysis_model_exists(self, app_context):
        """Test existing Analysis model functionality"""
        # Create brand first
        brand = Brand(
            id="test-brand-id",
            name="Test Brand",
            created_at=datetime.utcnow()
        )
        db.session.add(brand)
        db.session.flush()
        
        # Create analysis
        analysis = Analysis(
            id="test-analysis-id",
            brand_id=brand.id,
            brand_name="Test Brand",
            analysis_types=["test_analysis"],
            status="started",
            created_at=datetime.utcnow()
        )
        db.session.add(analysis)
        db.session.commit()
        
        # Test model methods
        assert analysis.to_dict() is not None
        assert analysis.to_dict()['brand_name'] == "Test Brand"
        
        # Test status update
        analysis.update_status("completed", progress=100)
        assert analysis.status == "completed"
        assert analysis.progress == 100
        
        # Test results update
        test_results = {"score": 85}
        analysis.update_results(test_results)
        assert analysis.results == test_results
        
    def test_brand_model_exists(self, app_context):
        """Test existing Brand model functionality"""
        brand = Brand(
            id="test-brand-id",
            name="Test Brand",
            website="https://test.com",
            industry="Technology",
            created_at=datetime.utcnow()
        )
        db.session.add(brand)
        db.session.commit()
        
        # Test model attributes
        assert brand.name == "Test Brand"
        assert brand.website == "https://test.com"
        assert brand.industry == "Technology"
        assert brand.created_at is not None
        
    def test_user_model_exists(self, app_context):
        """Test existing User model functionality"""
        user = User(
            id="test-user-id",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        
        # Test model attributes
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.is_active is True  # Default value
        
    def test_report_model_exists(self, app_context):
        """Test existing Report model functionality"""
        # Create dependencies
        brand = Brand(id="brand-id", name="Test Brand", created_at=datetime.utcnow())
        analysis = Analysis(
            id="analysis-id", 
            brand_id="brand-id", 
            brand_name="Test Brand",
            created_at=datetime.utcnow()
        )
        db.session.add_all([brand, analysis])
        db.session.flush()
        
        # Create report
        report = Report(
            id="report-id",
            analysis_id="analysis-id",
            report_type="pdf",
            filename="test_report.pdf",
            file_path="/path/to/report.pdf",
            title="Test Report",
            created_at=datetime.utcnow()
        )
        db.session.add(report)
        db.session.commit()
        
        # Test model attributes
        assert report.report_type == "pdf"
        assert report.filename == "test_report.pdf"
        assert report.title == "Test Report"
        assert report.status == "generated"  # Default value
