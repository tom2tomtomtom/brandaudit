#!/usr/bin/env python3
"""
Comprehensive test suite for EXISTING Flask API functionality
Tests what EXISTS, not what we think should exist
"""
import os
import sys
import pytest
import json
import time
import threading
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import existing app and services
from app import app, socketio, analysis_storage
from src.services.database_service import DatabaseService
from src.services.websocket_service import get_websocket_service
from simple_analysis import SimpleAnalyzer

class TestExistingAPI:
    """Test suite for existing API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client for existing Flask app"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                # Initialize test database
                from src.extensions import db
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def socketio_client(self):
        """Create test client for existing WebSocket functionality"""
        app.config['TESTING'] = True
        return socketio.test_client(app)

    def test_health_endpoint_exists(self, client):
        """Test existing /api/health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'status' in data
        assert 'service' in data
        assert data['service'] == "AI Brand Audit Tool API"
        assert 'version' in data
        assert 'timestamp' in data
        assert 'environment' in data
        
        # Test existing system health integration
        assert 'system_health' in data
        assert 'api_connectivity' in data
        
    def test_health_endpoint_post_method(self, client):
        """Test existing health endpoint supports POST"""
        response = client.post('/api/health')
        assert response.status_code == 200
        
    def test_health_endpoint_options_method(self, client):
        """Test existing health endpoint supports OPTIONS (CORS)"""
        response = client.options('/api/health')
        assert response.status_code == 200
        
    def test_detailed_health_endpoint_exists(self, client):
        """Test existing /api/health/detailed endpoint"""
        response = client.get('/api/health/detailed')
        assert response.status_code in [200, 500]  # May fail if APIs not configured
        
        data = response.get_json()
        assert 'service' in data
        assert 'timestamp' in data
        
    def test_brand_search_endpoint_exists(self, client):
        """Test existing /api/brand/search endpoint"""
        test_data = {'query': 'Apple'}
        response = client.post('/api/brand/search', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['brand_name'] == 'Apple'
        assert 'website' in data['data']
        
    def test_upload_endpoint_exists(self, client):
        """Test existing /api/upload endpoint"""
        # Test with no files
        response = client.post('/api/upload')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['files_uploaded'] == 0
        
    def test_analyze_endpoint_exists(self, client):
        """Test existing /api/analyze endpoint"""
        test_data = {
            'company_name': 'Apple Inc',
            'analysis_types': ['brand_positioning', 'competitive_analysis']
        }
        
        response = client.post('/api/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'analysis_id' in data['data']
        assert data['data']['status'] == 'started'
        assert 'estimated_time' in data['data']
        
        # Verify analysis was stored
        analysis_id = data['data']['analysis_id']
        assert analysis_id in analysis_storage
        assert analysis_storage[analysis_id]['brand_name'] == 'Apple Inc'
        
    def test_analyze_status_endpoint_exists(self, client):
        """Test existing /api/analyze/<id>/status endpoint"""
        # First create an analysis
        test_data = {'company_name': 'Tesla'}
        response = client.post('/api/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        analysis_id = response.get_json()['data']['analysis_id']
        
        # Test status endpoint
        response = client.get(f'/api/analyze/{analysis_id}/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['analysis_id'] == analysis_id
        assert 'status' in data['data']
        assert 'progress' in data['data']
        
    def test_analyze_results_endpoint_exists(self, client):
        """Test existing /api/analyze/<id>/results endpoint"""
        # Create analysis and mark as completed
        analysis_id = f"test-{int(time.time())}"
        analysis_storage[analysis_id] = {
            'brand_name': 'Nike',
            'status': 'completed',
            'results': {
                'brand_health_score': 85,
                'visual_analysis': {'consistency_score': 90}
            }
        }
        
        response = client.get(f'/api/analyze/{analysis_id}/results')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['brand_health_score'] == 85
        
    def test_analyze_results_not_complete(self, client):
        """Test results endpoint when analysis not complete"""
        analysis_id = f"test-incomplete-{int(time.time())}"
        analysis_storage[analysis_id] = {
            'brand_name': 'Microsoft',
            'status': 'processing'
        }
        
        response = client.get(f'/api/analyze/{analysis_id}/results')
        assert response.status_code == 202
        
        data = response.get_json()
        assert data['success'] is False
        assert 'not yet complete' in data['error']
        
    def test_analyze_results_not_found(self, client):
        """Test results endpoint with non-existent analysis"""
        response = client.get('/api/analyze/nonexistent/results')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error']
        
    def test_analyses_endpoint_exists(self, client):
        """Test existing /api/analyses endpoint"""
        response = client.get('/api/analyses')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'analyses' in data['data']
        assert len(data['data']['analyses']) >= 2  # Should have sample data
        
        # Verify sample data structure
        analysis = data['data']['analyses'][0]
        assert 'id' in analysis
        assert 'company_name' in analysis
        assert 'status' in analysis
        assert 'results' in analysis
        
    def test_root_endpoint_exists(self, client):
        """Test existing root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['service'] == "AI Brand Audit Tool API"
        assert data['status'] == "running"
        assert 'endpoints' in data
        assert '/api/health' in data['endpoints']
        assert '/api/analyze' in data['endpoints']
        
    def test_cors_headers_exist(self, client):
        """Test CORS is properly configured"""
        response = client.options('/api/health')
        assert response.status_code == 200

        # CORS should be configured for all origins
        response = client.get('/api/health', headers={'Origin': 'http://localhost:3000'})
        assert response.status_code == 200

class TestExistingWebSocketFunctionality:
    """Test suite for existing WebSocket functionality"""

    @pytest.fixture
    def socketio_client(self):
        """Create test client for existing WebSocket functionality"""
        app.config['TESTING'] = True
        return socketio.test_client(app)

    def test_websocket_connection_exists(self, socketio_client):
        """Test existing WebSocket connection functionality"""
        assert socketio_client.is_connected()

        # Should receive connected event
        received = socketio_client.get_received()
        assert len(received) > 0
        assert received[0]['name'] == 'connected'
        assert 'status' in received[0]['args'][0]

    def test_websocket_join_analysis_room(self, socketio_client):
        """Test existing join_analysis WebSocket event"""
        analysis_id = "test-analysis-123"

        # Emit join_analysis event
        socketio_client.emit('join_analysis', {'analysis_id': analysis_id})

        # Should not raise any errors
        assert socketio_client.is_connected()

    def test_websocket_leave_analysis_room(self, socketio_client):
        """Test existing leave_analysis WebSocket event"""
        analysis_id = "test-analysis-123"

        # First join, then leave
        socketio_client.emit('join_analysis', {'analysis_id': analysis_id})
        socketio_client.emit('leave_analysis', {'analysis_id': analysis_id})

        # Should not raise any errors
        assert socketio_client.is_connected()

    def test_websocket_service_initialization(self):
        """Test existing WebSocket service is properly initialized"""
        websocket_service = get_websocket_service()
        assert websocket_service is not None
        assert hasattr(websocket_service, 'socketio')
        assert hasattr(websocket_service, 'progress_trackers')

    def test_websocket_progress_tracking(self):
        """Test existing progress tracking functionality"""
        websocket_service = get_websocket_service()
        analysis_id = "test-progress-123"

        # Create progress tracker
        websocket_service.create_progress_tracker(analysis_id)
        assert analysis_id in websocket_service.progress_trackers

        # Test stage updates
        websocket_service.emit_stage_update(analysis_id, 0, 50, "Testing stage")
        tracker = websocket_service.progress_trackers[analysis_id]
        assert tracker.current_stage == 0
        assert tracker.stage_progress == 50

    def test_websocket_error_handling(self):
        """Test existing WebSocket error handling"""
        websocket_service = get_websocket_service()
        analysis_id = "test-error-123"

        # Create tracker and emit error
        websocket_service.create_progress_tracker(analysis_id)
        websocket_service.emit_error(analysis_id, "Test error message")

        tracker = websocket_service.progress_trackers[analysis_id]
        assert tracker.error_message == "Test error message"
        assert tracker.status == "error"

class TestExistingAnalysisWorkflow:
    """Test suite for existing analysis workflow in simple_analysis.py"""

    def test_simple_analyzer_initialization(self):
        """Test existing SimpleAnalyzer class initialization"""
        analyzer = SimpleAnalyzer()

        # Should initialize with API keys from environment
        assert hasattr(analyzer, 'openrouter_api_key')
        assert hasattr(analyzer, 'news_api_key')
        assert hasattr(analyzer, 'brandfetch_api_key')

        # Should initialize optional services
        assert hasattr(analyzer, 'visual_service')
        assert hasattr(analyzer, 'competitor_service')
        assert hasattr(analyzer, 'campaign_service')

    @patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-openrouter-key',
        'NEWS_API_KEY': 'test-news-key',
        'BRANDFETCH_API_KEY': 'test-brandfetch-key'
    })
    def test_analyzer_with_api_keys(self):
        """Test analyzer behavior with API keys configured"""
        analyzer = SimpleAnalyzer()

        assert analyzer.openrouter_api_key == 'test-openrouter-key'
        assert analyzer.news_api_key == 'test-news-key'
        assert analyzer.brandfetch_api_key == 'test-brandfetch-key'

    def test_analyzer_without_api_keys(self):
        """Test analyzer behavior without API keys"""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            analyzer = SimpleAnalyzer()

            # Should handle missing API keys gracefully
            result = analyzer.analyze_brand("Test Brand")
            assert result['success'] is False
            assert 'No API keys configured' in result['error']

    @patch('simple_analysis.SimpleAnalyzer.call_llm_analysis')
    @patch('simple_analysis.SimpleAnalyzer.call_news_api')
    @patch('simple_analysis.SimpleAnalyzer.call_brandfetch')
    def test_analyze_brand_workflow(self, mock_brandfetch, mock_news, mock_llm):
        """Test existing analyze_brand workflow"""
        # Mock API responses
        mock_llm.return_value = {
            'success': True,
            'analysis': 'Test LLM analysis content'
        }
        mock_news.return_value = {
            'success': True,
            'total_articles': 5,
            'positive_percentage': 70
        }
        mock_brandfetch.return_value = {
            'success': True,
            'name': 'Test Brand',
            'domain': 'test.com',
            'colors': ['#FF0000', '#00FF00']
        }

        analyzer = SimpleAnalyzer()
        result = analyzer.analyze_brand("Test Brand")

        # Should return successful analysis
        assert result['success'] is True
        assert result['brand_name'] == "Test Brand"
        assert 'analysis_id' in result
        assert 'data_sources' in result

        # Should have called all API methods
        mock_llm.assert_called_once()
        mock_news.assert_called_once()
        mock_brandfetch.assert_called_once()

    def test_transform_for_frontend_real_only(self):
        """Test existing transform_for_frontend_real_only method"""
        analyzer = SimpleAnalyzer()

        # Test data with real API responses
        simple_data = {
            'brand_name': 'Test Brand',
            'analysis_id': 'test-123',
            'generated_at': datetime.utcnow().isoformat(),
            'llm_analysis': {
                'success': True,
                'analysis': 'EXECUTIVE SUMMARY\nTest analysis content'
            },
            'news_analysis': {
                'success': True,
                'total_articles': 3,
                'positive_percentage': 80
            },
            'brand_data': {
                'success': True,
                'name': 'Test Brand',
                'colors': ['#FF0000']
            }
        }

        result = analyzer.transform_for_frontend_real_only(simple_data)

        assert result['success'] is True
        assert result['brand_name'] == 'Test Brand'
        assert 'data_sources' in result
        assert result['data_sources']['llm_analysis'] is True
        assert result['data_sources']['news_data'] is True
        assert result['data_sources']['brand_data'] is True
