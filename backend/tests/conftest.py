"""
Comprehensive test configuration for brand audit integration tests
"""
import pytest
import os
import tempfile
import json
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from flask import Flask
from flask_socketio import SocketIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import application components
from src.main import create_app
from src.extensions import db
from src.models.user_model import User, Analysis, Brand
from src.services.websocket_service import WebSocketService
from src.services.database_service import DatabaseService


@pytest.fixture(scope="session")
def test_config():
    """Test configuration with isolated database"""
    return {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'CACHE_TYPE': 'simple',
        'RATELIMIT_ENABLED': False,
        # Test API keys
        'OPENROUTER_API_KEY': 'test-openrouter-key',
        'NEWS_API_KEY': 'test-news-key',
        'BRANDFETCH_API_KEY': 'test-brandfetch-key',
        'OPENCORPORATES_API_KEY': 'test-opencorporates-key'
    }


@pytest.fixture(scope="session")
def app(test_config):
    """Create application for testing"""
    app = create_app()
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    """SocketIO test client"""
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio.test_client(app)


@pytest.fixture
def db_session(app):
    """Database session for testing"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use this connection
        session = sessionmaker(bind=connection)()
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email='test@example.com',
        username='testuser',
        is_active=True,
        is_verified=True
    )
    user.set_password('testpassword')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_brand(db_session):
    """Create test brand"""
    brand = Brand(
        name='Test Brand',
        website='https://testbrand.com',
        industry='Technology',
        description='A test brand for integration testing'
    )
    db_session.add(brand)
    db_session.commit()
    return brand


@pytest.fixture
def test_analysis(db_session, test_user, test_brand):
    """Create test analysis"""
    analysis = Analysis(
        id='test-analysis-id',
        user_id=test_user.id,
        brand_id=test_brand.id,
        brand_name=test_brand.name,
        analysis_types=['comprehensive'],
        status='started',
        progress=0
    )
    db_session.add(analysis)
    db_session.commit()
    return analysis


@pytest.fixture
def mock_api_services():
    """Mock external API services"""
    with patch('src.services.llm_service.LLMService') as mock_llm, \
         patch('src.services.news_service.NewsService') as mock_news, \
         patch('src.services.visual_analysis_service.VisualAnalysisService') as mock_visual, \
         patch('src.services.campaign_analysis_service.CampaignAnalysisService') as mock_campaign:
        
        # Configure mock responses
        mock_llm.return_value.analyze_brand_sentiment.return_value = {
            'analysis': 'Mock LLM analysis',
            'sentiment_score': 0.8,
            'key_insights': ['Insight 1', 'Insight 2']
        }
        
        mock_news.return_value.get_recent_news.return_value = {
            'articles': [
                {'title': 'Test Article', 'url': 'https://test.com', 'sentiment': 'positive'}
            ]
        }
        
        mock_visual.return_value.analyze_brand_visuals.return_value = {
            'colors': ['#FF0000', '#00FF00'],
            'fonts': ['Arial', 'Helvetica'],
            'logo_analysis': {'quality': 'high'}
        }
        
        mock_campaign.return_value.analyze_brand_campaigns.return_value = {
            'campaigns': [
                {'name': 'Test Campaign', 'platform': 'social', 'performance': 'good'}
            ]
        }
        
        yield {
            'llm': mock_llm,
            'news': mock_news,
            'visual': mock_visual,
            'campaign': mock_campaign
        }


@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing"""
    return {
        'analysis_id': 'test-analysis-id',
        'brand_name': 'Test Brand',
        'status': 'completed',
        'progress': 100,
        'llm_insights': {
            'analysis': 'Comprehensive brand analysis...',
            'sentiment_score': 0.85,
            'key_findings': ['Strong brand recognition', 'Positive market sentiment']
        },
        'news_analysis': {
            'articles_count': 25,
            'sentiment_distribution': {'positive': 60, 'neutral': 30, 'negative': 10},
            'recent_articles': []
        },
        'visual_analysis': {
            'primary_colors': ['#1E3A8A', '#FFFFFF'],
            'secondary_colors': ['#64748B', '#F1F5F9'],
            'fonts': ['Inter', 'Roboto'],
            'logo_quality_score': 0.9
        },
        'competitive_analysis': {
            'competitors': ['Competitor A', 'Competitor B'],
            'market_position': 'leader',
            'competitive_advantages': ['Innovation', 'Brand loyalty']
        }
    }


@pytest.fixture
def websocket_service(app):
    """WebSocket service for testing"""
    socketio = SocketIO(app, cors_allowed_origins="*")
    return WebSocketService(socketio)


@pytest.fixture
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_brand_data(name="Test Brand", website="https://test.com"):
        return {
            'name': name,
            'website': website,
            'industry': 'Technology',
            'description': f'Test brand: {name}'
        }
    
    @staticmethod
    def create_analysis_request(company_name="Test Company"):
        return {
            'company_name': company_name,
            'website': f'https://{company_name.lower().replace(" ", "")}.com',
            'analysis_options': {
                'brandPerception': True,
                'competitiveAnalysis': True,
                'visualAnalysis': True,
                'pressCoverage': True,
                'socialSentiment': False
            }
        }
    
    @staticmethod
    def create_progress_update(analysis_id, progress=50, stage=2):
        return {
            'analysis_id': analysis_id,
            'overall_progress': progress,
            'current_stage': stage,
            'stage_progress': 75,
            'current_step_name': 'Visual Analysis',
            'current_substep': 'Extracting brand colors',
            'status': 'processing',
            'time_remaining': 120,
            'estimated_completion': (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
            'elapsed_time': 180
        }


@pytest.fixture
def test_data_factory():
    """Test data factory"""
    return TestDataFactory


# Utility functions for tests
def assert_valid_analysis_response(response_data):
    """Assert that analysis response has valid structure"""
    assert 'success' in response_data
    assert 'data' in response_data
    if response_data['success']:
        assert 'analysis_id' in response_data['data']
        assert 'estimated_completion' in response_data['data']


def assert_valid_progress_update(progress_data):
    """Assert that progress update has valid structure"""
    required_fields = [
        'analysis_id', 'overall_progress', 'current_stage',
        'status', 'current_step_name'
    ]
    for field in required_fields:
        assert field in progress_data, f"Missing required field: {field}"

    assert 0 <= progress_data['overall_progress'] <= 100
    assert progress_data['status'] in ['starting', 'processing', 'completed', 'error']


def assert_valid_results_structure(results_data):
    """Assert that results have valid structure"""
    assert 'success' in results_data
    if results_data['success']:
        data = results_data['data']
        assert 'analysis_id' in data
        assert 'brand_name' in data
        assert 'status' in data
        # Check for main analysis sections
        expected_sections = ['llm_insights', 'visual_analysis']
        for section in expected_sections:
            if section in data:
                assert isinstance(data[section], dict)


class IntegrationTestHelper:
    """Helper class for integration tests"""

    @staticmethod
    def wait_for_analysis_completion(client, analysis_id, timeout=60):
        """Wait for analysis to complete"""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = client.get(f'/api/analyze/{analysis_id}/status')
            if response.status_code == 200:
                data = response.get_json()
                if data.get('data', {}).get('status') in ['completed', 'error']:
                    return data
            time.sleep(2)

        raise TimeoutError(f"Analysis {analysis_id} did not complete within {timeout} seconds")

    @staticmethod
    def simulate_analysis_progress(websocket_service, analysis_id, stages=None):
        """Simulate analysis progress updates"""
        if not stages:
            stages = [
                {'name': 'LLM Analysis', 'duration': 5},
                {'name': 'News Analysis', 'duration': 3},
                {'name': 'Visual Analysis', 'duration': 4},
                {'name': 'Competitive Analysis', 'duration': 3}
            ]

        total_stages = len(stages)
        for i, stage in enumerate(stages):
            progress = int((i + 1) / total_stages * 100)
            update_data = {
                'analysis_id': analysis_id,
                'overall_progress': progress,
                'current_stage': i,
                'stage_progress': 100,
                'current_step_name': stage['name'],
                'status': 'completed' if i == total_stages - 1 else 'processing'
            }
            websocket_service.emit_progress_update(analysis_id, update_data)

    @staticmethod
    def create_mock_analysis_results(analysis_id, brand_name):
        """Create mock analysis results"""
        return {
            'analysis_id': analysis_id,
            'brand_name': brand_name,
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.utcnow().isoformat(),
            'llm_insights': {
                'analysis': f'Comprehensive analysis of {brand_name}...',
                'sentiment_score': 0.85,
                'key_findings': ['Strong market presence', 'Positive brand perception']
            },
            'visual_analysis': {
                'primary_colors': ['#1E3A8A', '#FFFFFF'],
                'fonts': ['Inter', 'Roboto'],
                'logo_quality_score': 0.9
            },
            'news_analysis': {
                'articles_count': 15,
                'sentiment_distribution': {'positive': 70, 'neutral': 20, 'negative': 10}
            }
        }


@pytest.fixture
def integration_helper():
    """Integration test helper"""
    return IntegrationTestHelper
